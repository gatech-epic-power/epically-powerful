"""
Epically Powerful header. TODO: complete.

TODO:
- Complete header
- Create functionality to ensure that CAN bus is not instantiated if actuators have already done so (also that actuators and these IMUs MUST NOT have overlapping names).
"""


import time
from typing import List, Dict, Set, Optional

import os
import platform
import can
import numpy as np

from epicallypowerful.sensing.open_imu.sae_j1939 import ExtendedID29Bit
from epicallypowerful.sensing.open_imu.range_converter import (
    acceleration_packer,
    angular_packer,
)
from epicallypowerful.toolbox.jetson_performance import _rpi_or_jetson
from epicallypowerful.sensing.imu_abc import IMU
from epicallypowerful.sensing.imu_data import IMUData


# The PGNs of the CAN messages sent by the OpenIMU300RIs
ANGULAR_PGN = 61482
ACCELERATION_PGN = 61485

# PGN -> packer.
# Packer functions are used to convert the raw data from the CAN messages into the correct units.
PACKER_DICT = {
    ACCELERATION_PGN: acceleration_packer,
    ANGULAR_PGN: angular_packer,
}

# def _load_can_drivers() -> None:
#     """Loads and unload the can drivers, then reloads to ensure fresh driver initialization
#     This will load the CAN drivers, but then remove them and load them again...
#     Trust the process. Loading them alone will not reset the can drivers.
#     If they are not reset, the buffer can fill up due to errors and the buffer
#     will not properly reset.
#     """

#     dev_uname = platform.uname()
#     if 'aarch64' in dev_uname.machine.lower() and 'tegra' in dev_uname.release.lower():
#         os.system('sudo modprobe can')
#         os.system('sudo modprobe can_raw')
#         os.system('sudo modprobe mttcan')

#         os.system('sudo /sbin/ip link set can0 down')
#         os.system('sudo rmmod can_raw')
#         os.system('sudo rmmod can')
#         os.system('sudo rmmod mttcan')

#         os.system('sudo modprobe can')
#         os.system('sudo modprobe can_raw')
#         os.system('sudo modprobe mttcan')

#         os.system('sudo /sbin/ip link set can0 down')
#         os.system('sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000')

#     elif 'aarch64' in dev_uname.machine.lower() and ('rpi' in dev_uname.release.lower() or 'raspi' in dev_uname.release.lower() or 'bcm' in dev_uname.release.lower()):
#         os.system('sudo /sbin/ip link set can0 down')
#         os.system('sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000')


def is_jetson() -> bool:
    """
    Check if the device is a Jetson.
    Returns:
        (bool): A flag that determines whether the device is a Jetson.
    """
    return "tegra" in platform.release()


def _load_can_drivers() -> None:
    """
    Load can drivers on the Jetson.

    Raises:
        Exception: If the device is not a Jetson.

    """

    if not is_jetson():
        raise Exception("This is not a Jetson device.")

    os.system("sudo modprobe can")
    os.system("sudo modprobe can_raw")
    os.system("sudo modprobe mttcan")

    os.system("sudo /sbin/ip link set can0 down")
    os.system("sudo rmmod can_raw")
    os.system("sudo rmmod can")
    os.system("sudo rmmod mttcan")

    os.system("sudo modprobe can")
    os.system("sudo modprobe can_raw")
    os.system("sudo modprobe mttcan")

    os.system("sudo /sbin/ip link set can0 down")
    os.system("sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000")


class OpenIMUs(IMU):
    def __init__(
        self,
        imu_ids: List[int],
        load_drivers: bool=True,
        disabled: bool=False,
    ) -> None:
        """

        A listener to capture data from OpenIMU300RI sensors sent over CAN.

        Args:
            imu_ids (list[int]): A list containing all device IDs.
            load_can_drivers (bool): Whether the can drivers should be loaded. Other listeners may have already loaded the drivers.
            disabled (bool): Whether the listener is disabled.
        """

        # can id -> order in which the IMU data is stored in the listener.
        self.listen_data_length=len(imu_ids) * 6 + 1 # TODO: fix hardcoded number of data channels read in (`6`)
        self.disabled = disabled=disabled or not (_rpi_or_jetson() == "jetson")
        self.imu_order: Dict[int, int] = dict()
        self.imu_ids = imu_ids
        self.imu_data: Dict[int, IMUData] = dict()

        for i, imu_id in enumerate(imu_ids):
            self.imu_order[imu_id] = i
            self.imu_data[imu_id] = IMUData()

        if self.disabled:
            print("OpenIMUs instance is disabled.")

        self.load_drivers = load_drivers

        self._set_up_connected_imus()


    def _set_up_connected_imus(self) -> None:
        """Set up driver resources for IMUs.
        """
        if self.load_drivers:
            _load_can_drivers()

        self.bus = can.Bus(interface="socketcan", bitrate=1000000)
        # self._verify_num_imus()


    def _verify_num_imus(self, timeout_sec: int=3) -> None:
        """Verify the number of IMUs that are connected is the amount that we expect.

        Args:
            timeout_sec (int): Maximum time in seconds to wait for the expected number of IMUs to connect.
        """

        if self.disabled:
            return

        imu_id_cache: Set[int] = set()
        start = time.perf_counter()
        while True:
            msg = self.bus.recv(timeout=timeout_sec)

            # TROUBLESHOOTING
            print(f"msg: {msg}")

            if msg:
                parsed_id = ExtendedID29Bit(msg.arbitration_id)
                imu_id_cache.add(parsed_id.source)

            if len(imu_id_cache) == len(self.imu_order):
                return
            if time.perf_counter() > start + timeout_sec:
                raise Exception(
                    f"{len(imu_id_cache)} out of {len(self.imu_order)} IMUs connected. Only the following IMUs are connected: {list(imu_id_cache)}"
                )


    def _unpack_payload(self, payload: bytes, pgn: int) -> List:
        """
        Unpack the payload of a message into the buffer.

        Assumptions:
        - Only linear acceleration and angular velocity measurements are being unpacked.

        Args:
            payload (bytes): The payload of the message.
            pgn (int): The Parameter Group Number (PGN) of the message.

        Returns:
            A list of 3 values representing the (x, y, z) measurements.
        """

        if self.disabled:
            return [0, 0, 0]

        # Select the correct unpacker
        unpacker = PACKER_DICT[pgn].from_unsigned_int

        # Unpack payload into buffer. X Y Z is the order.
        # Each IMU starts at imu_num * 6.
        # offset is used to select the correct 3 cells.
        return [
            unpacker(payload[0] | payload[1] << 8),
            unpacker(payload[2] | payload[3] << 8),
            unpacker(payload[4] | payload[5] << 8),
        ]


    def _get_data_in_loop(self) -> np.ndarray:
        """
        Get data in the loop and update corresponding IMUData object instances.

        .. warning::
            You should only be calling ``get_data()`` to get the data.

        Returns:
            np.ndarray: Returns a 1d numpy array of length ``len(imu_ids) * 6 + 1``.
        """
        data = np.zeros(self.listen_data_length)
        
        if not self.disabled:
            # This set will keep track of what OpenIMU messages we have received so far
            msg_id_cache = set()

            for msg in self.bus:
                parsed_id = ExtendedID29Bit(msg.arbitration_id)

                # We are only interested in linear acceleration and angular velocity messages
                if parsed_id.pgn in [ACCELERATION_PGN, ANGULAR_PGN]:
                    if parsed_id.pgn == ANGULAR_PGN:
                        buffer_offset = 3
                    else:
                        buffer_offset = 0

                    imu_num = self.imu_order[parsed_id.source]
                    start = imu_num * 6 + buffer_offset # TODO: fix hardcoded `6`

                    # 3 axes: X, Y, Z
                    data[start:start + 3] = self._unpack_payload(
                        msg.data, parsed_id.pgn
                    )

                    # Populate corresponding IMUData object instance with most recent data
                    imu_id = self.imu_ids[imu_num]

                    if parsed_id.pgn == ACCELERATION_PGN:
                        self.imu_data[imu_id].acc_x = data[start:start + 1]
                        self.imu_data[imu_id].acc_y = data[start:start + 2]
                        self.imu_data[imu_id].acc_z = data[start:start + 3]
                    elif parsed_id.pgn == ANGULAR_PGN:
                        self.imu_data[imu_id].gyro_x = data[start:start + 1]
                        self.imu_data[imu_id].gyro_y = data[start:start + 2]
                        self.imu_data[imu_id].gyro_z =data[start:start + 3]

                    self.imu_data[imu_id].timestamp = time.perf_counter()
                    

                    msg_id_cache.add(parsed_id.extended_id)

                    # 2 messages per IMU, linear acceleration and angular velocity
                    if len(msg_id_cache) == len(self.imu_order) * 2:
                        break

        data[-1] = time.perf_counter()
        
        return data


    def get_data(self, imu_id: int | list[int]) -> IMUData:
        """Get data from all connected IMUs by parsing CAN bus buffer, then return imu data for specified IMU(s) by ID.

        Args:
            imu_id (int or list[int]): CAN ID of the OpenIMU from which to update the appropriate IMUData dataclass.

        Returns:
            IMUData object instance or list of IMUData object instances populated with most recent OpenIMU data. NOTE: some fields in the dataclass will necessarily remain unpopulated as the OpenIMUs do not provide all the information that other IMUs do.
        """

        # Get data for all IMUs with new messages in CAN bus buffer
        _ = self._get_data_in_loop()

        if isinstance(imu_id, int):
            return self.imu_data[imu_id]
        elif isinstance(imu_id, list):
            return [self.imu_data[idx] for idx in imu_id]

            
    def _close_loop_resources(self):
        """Close resources opened in the OpenIMUs instance.
        """
        if not self.disabled:
            self.bus.shutdown()


if __name__ == "__main__":
    imus = OpenIMUs(imu_ids=[132])

    print("OpenIMUs instance initialized and listening for data...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Get data from the single connected OpenIMU
            data = imus.get_data(132)

            # If you want to see all of the data
            # print(data)

            # If you want to see the data from a specific IMU
            # print(data.imu(location="left"))

            # Print a specific channel of data from the OpenIMU
            print(data.acc_x)

            time.sleep(0.5)

    except KeyboardInterrupt:
        imus._close_loop_resources()
        print("\nStopped OpenIMUs instance.")
