"""
Epically Powerful header. TODO: complete.

Reference info:
- OpenIMU ReadTheDocs page: https://openimu.readthedocs.io/en/latest/index.html
- OpenIMU CAN bus usage and breakdown: https://medium.com/@mikehorton/what-can-a-can-bus-imu-do-to-make-an-autonomous-vehicle-safer-e93f748569f6

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
    gyroscope_packer,
    magnetometer_packer,
)
from epicallypowerful.toolbox.jetson_performance import _rpi_or_jetson
from epicallypowerful.sensing.imu_abc import IMU
from epicallypowerful.sensing.imu_data import IMUData


# Set conversion constants
DEG2RAD = 3.141592653589/180 # [rad/deg]

# Set the PGNs of the CAN messages sent by the OpenIMU300RIs
ACCELEROMETER_PGN = 61485 # Linear acceleration
GYROSCOPE_PGN = 61482 # Angular velocity
MAGNETOMETER_PGN = 65386 # Magnetometer


def _load_can_drivers() -> None:
    """Loads and unload the can drivers, then reloads to ensure fresh driver initialization
    This will load the CAN drivers, but then remove them and load them again...
    Trust the process. Loading them alone will not reset the can drivers.
    If they are not reset, the buffer can fill up due to errors and the buffer
    will not properly reset.
    """

    dev_uname = platform.uname()
    if 'aarch64' in dev_uname.machine.lower() and 'tegra' in dev_uname.release.lower():
        os.system('sudo modprobe can')
        os.system('sudo modprobe can_raw')
        os.system('sudo modprobe mttcan')

        os.system('sudo /sbin/ip link set can0 down')
        os.system('sudo rmmod can_raw')
        os.system('sudo rmmod can')
        os.system('sudo rmmod mttcan')

        os.system('sudo modprobe can')
        os.system('sudo modprobe can_raw')
        os.system('sudo modprobe mttcan')

        os.system('sudo /sbin/ip link set can0 down')
        os.system('sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000')

    elif 'aarch64' in dev_uname.machine.lower() and ('rpi' in dev_uname.release.lower() or 'raspi' in dev_uname.release.lower() or 'bcm' in dev_uname.release.lower()):
        os.system('sudo /sbin/ip link set can0 down')
        os.system('sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000')


class OpenIMUs(IMU):
    def __init__(
        self,
        imu_ids: List[int],
        components: List[str]=['acc', 'gyro'],
        rate: float=100,
        load_drivers: bool=True,
        disabled: bool=False,
        verbose: bool=False,
    ) -> None:
        """

        A listener to capture data from OpenIMU300RI sensors sent over CAN.

        Args:
            imu_ids (list[int]): A list containing all device IDs.
            components (list[str]): A list of the components to use. Default: ['acc', 'gyro'].
            rate (float): rate [Hz] at which to sample from IMUs. NOTE: this does not affect the IMU's internal operating frequency, just the rate at which data are sampled from it.
            load_can_drivers (bool): Whether the can drivers should be loaded. Other processes may have already loaded the drivers (like the actuators).
            disabled (bool): Whether the listener is disabled.
            verbose (bool): Whether to print low-level operating steps to terminal. Default: False.
        """

        # can id -> order in which the IMU data is stored in the listener.
        # self.listen_data_length includes 3 channels each for acc, gyro, mag, and 1 for time
        # self.listen_data_length=len(imu_ids) * 3*len(components) + 1 # TODO: abstract # of components away
        self.listen_data_length=len(imu_ids) * 9 + 1
        self.disabled = disabled=disabled or not (_rpi_or_jetson() == "jetson")
        self.imu_order: Dict[int, int] = dict()
        self.imu_data: Dict[int, IMUData] = dict()

        if not isinstance(imu_ids, list):
            imu_ids = [imu_ids]

        self.imu_ids = imu_ids
        
        # TROUBLESHOOTING: TODO: fix `mag` functionality so we can disable this
        if any([c for c in components if 'mag' in c]):
            print(f"Troubleshooting catch! `mag` functionality is not currently enabled. Defaulting to just `acc` and `gyro` components.")
            components = [c for c in components if not 'mag' in c]

        self.components = components
        self.rate = rate
        self.packer_dict = {}

        # Set message unpacking capabilities based on which components to include
        if 'acc' in self.components:
            self.packer_dict[ACCELEROMETER_PGN] = acceleration_packer
        
        if 'gyro' in self.components:
            self.packer_dict[GYROSCOPE_PGN] = gyroscope_packer
        
        if 'mag' in self.components:
            self.packer_dict[MAGNETOMETER_PGN] = magnetometer_packer

        # Set IMU IDs and order of data unpacking
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
        self._verify_num_imus()


    def _verify_num_imus(self, timeout_sec: int=2) -> None:
        """Verify the number of IMUs that are connected is the amount that we expect. To succeed, we need to get at least one message from each IMU over the CAN bus within the timeout threshold.

        Args:
            timeout_sec (int): Maximum time in seconds to wait for the expected number of IMUs to connect.
        """

        if self.disabled:
            return

        imu_id_cache: Set[int] = set()
        start = time.perf_counter()

        while True:
            msg = self.bus.recv(timeout=timeout_sec)

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
        unpacker = self.packer_dict[pgn].from_unsigned_int

        # Unpack payload into buffer. X Y Z is the order
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
            np.ndarray: Returns a 1D numpy array of length ``len(imu_ids) * (3 * len(components)) + 1``.
        """
        data = np.zeros(self.listen_data_length)
        
        if not self.disabled:
            # This set will keep track of what OpenIMU messages we have received so far
            msg_id_cache = set()
            tmp_msg_id_cache = set()

            for msg in self.bus:
                parsed_id = ExtendedID29Bit(msg.arbitration_id)

                # We are only interested in linear acceleration and angular velocity messages
                if parsed_id.pgn in list(self.packer_dict.keys()):
                    if parsed_id.pgn == ACCELEROMETER_PGN:
                        buffer_offset = 0
                    elif parsed_id.pgn == GYROSCOPE_PGN:
                        buffer_offset = 3
                    elif parsed_id.pgn == MAGNETOMETER_PGN:
                        buffer_offset = 6

                    imu_num = self.imu_order[parsed_id.source]
                    start = imu_num * len(self.packer_dict.keys()) + buffer_offset

                    # 3 axes: X, Y, Z
                    data[start:start + 3] = self._unpack_payload(
                        msg.data, parsed_id.pgn
                    )

                    # Populate corresponding IMUData object instance with most recent data
                    imu_id = self.imu_ids[imu_num]

                    if parsed_id.pgn == ACCELEROMETER_PGN: # [m*s^-2]
                        self.imu_data[imu_id].acc_x = data[start].astype(np.float32)
                        self.imu_data[imu_id].acc_y = data[start + 1].astype(np.float32)
                        self.imu_data[imu_id].acc_z = data[start + 2].astype(np.float32)
                    elif parsed_id.pgn == GYROSCOPE_PGN: # [rad/s]
                        self.imu_data[imu_id].gyro_x = data[start].astype(np.float32) * DEG2RAD
                        self.imu_data[imu_id].gyro_y = data[start + 1].astype(np.float32) * DEG2RAD
                        self.imu_data[imu_id].gyro_z = data[start + 2].astype(np.float32) * DEG2RAD
                    elif parsed_id.pgn == MAGNETOMETER_PGN: # [Gauss] # TODO: confirm these units
                        self.imu_data[imu_id].mag_x = data[start].astype(np.float32)
                        self.imu_data[imu_id].mag_y = data[start + 1].astype(np.float32)
                        self.imu_data[imu_id].mag_z = data[start + 2].astype(np.float32)

                    self.imu_data[imu_id].timestamp = time.perf_counter()

                    msg_id_cache.add(parsed_id.extended_id)

                    # 3 possible messages per IMU: acceleration, angular velocity, and magnetometer data. Break once we've received all three from unpacker
                    if len(msg_id_cache) == len(self.imu_order) * len(self.packer_dict.keys()):
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

        # Get data for all IMUs with new messages in CAN bus buffer. This process will update all IMUData object instances with the most recent data
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
    # OPENIMU_ID = 142
    OPENIMU_ID = 132

    t_prev = time.perf_counter()
    freq_array = np.zeros(100,)

    imus = OpenIMUs(imu_ids=[OPENIMU_ID], components=['acc', 'gyro', 'mag'])

    print("OpenIMUs instance initialized and listening for data...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Get latest frequency reading and update mean frequency
            t = time.perf_counter()
            t_diff = t - t_prev
            freq_array = np.roll(freq_array, -1)
            freq_array[-1] = 1/t_diff
            t_prev = t
            mean_rate = freq_array.mean()

            # Get data from the single connected OpenIMU
            data = imus.get_data(OPENIMU_ID)

            # If you want to see all of the data
            # print(data)
            
            # Print a specific channel of data from the OpenIMU
            print(f"mean_rate: {mean_rate:^5.1f} Hz | acc_x: {data.acc_x:^5.2f}, acc_y: {data.acc_y:^5.2f}, acc_z: {data.acc_z:^5.2f}, gyro_x: {data.gyro_x:^5.2f}, gyro_y: {data.gyro_y:^5.2f}, gyro_z: {data.gyro_z:^5.2f}, mag_x: {data.mag_x:^5.2f}, mag_y: {data.mag_y:^5.2f}, mag_z: {data.mag_z:^5.2f}")

    except KeyboardInterrupt:
        imus._close_loop_resources()
        print("\nStopped OpenIMUs instance.")
