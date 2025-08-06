"""epically-powerful module for managing IMUs.

This module contains the classes and commands for initializing
and reading from Microstrain IMUs using the MSCL package.

"""

import os
import time
from typing import List
import numpy as np
from scipy.spatial.transform import Rotation as R
from epicallypowerful.sensing.imu_data import IMUData

"""Try to import mscl 
(follow instructions from MSCL installation guide: 
https://github.com/LORD-MicroStrain/MSCL/blob/master/HowToUseMSCL.md)

NOTE: the most important thing is that the `_mscl.so` shared object file 
in the `/usr/share/python3-mscl` folder is generated anew each on every new 
machine. THIS VERSION of the file must be imported into the `lib` folder.
"""
# Method of importing mscl suggested by manufacturer
import sys
import platform
if platform.platform().lower().startswith("linux"):
    sys.path.append(f"/usr/local/lib/python{sys.version_info.major}.{sys.version_info.minor}/dist-packages")
    # sys.path.append(f"/usr/share/python{sys.version_info.major}-mscl")

mscl_available = False

try:
    import mscl
    mscl_available = True
except:
    mscl_available = False

# Set constants
TARE_ON_STARTUP = False
IMU_RATE = 1000 # [Hz]
G_CONSTANT = 9.80665 # [m/s^2]
PI = 3.1415265


class MicrostrainImus:
    """Class for receiving data from Microstrain IMUs. Getting data from each IMU is as simple as calling :py:meth:`get_data` with the respective serial identifier as the argument.
    The microstrain IMUs typically need no special configuration or calibration. The serial number used to identify the IMUs is typically found on top of the IMU, and is the last 6 digits following the period.
    
    In order to use this functionality, the low level MSCL drivers need to be installed. Please see the tutorials on installing this, or directly consult the MSCL documentation (https://github.com/LORD-MicroStrain/MSCL).

    Many helper functions are included in the :py:class:`IMUData` class to assist with getting data conveniently. Please see that documentation for all options.
    
    Example:
        .. code-block:: python


            from epicpower.sensing import MicroStrainImus
            
            ### Instantiation
            LEFT_THIGH = '154143'
            LEFT_SHANK = '133930'

            imus = MicrostrainImus([LEFT_THIGH, LEFT_SHANK])

            ### Data
            # Complete Data
            thigh_data = imus.get_data(LEFT_THIGH)
            shank_data = imus.get_data(LEFT_SHANK)

            # Specific Orientation Channels
            thigh_roll = thigh_data.roll
            thigh_pitch = thigh_data.pitch
            thigh_yaw = thigh_data.yaw

            # Helpers for getting multiple relevant channels at once
            thigh_quaternion = thigh_data.quaternion
            thigh_euler = thigh_data.euler


    Args:
        imu_ids (list): dict of body segments and Microstrain serial numbers.
        rate (int): operational rate to set using internal MSCL library.
        tare_on_startup (bool): boolean for whether to automatically tare on startup. Default: False.
        verbose (bool): boolean for whether to print out additional information. Default: False.
        num_retries (int): number of times to retry connecting to an IMU if it fails the first time. Default: 10.
    """

    def __init__(
        self,
        imu_ids: list[str],
        rate: int=IMU_RATE,
        tare_on_startup: bool=TARE_ON_STARTUP,
        timeout: float=0.0002,
        num_retries: int=10,
        verbose: bool=False
    ) -> None:
        if not mscl_available:
            raise ModuleNotFoundError("MSCL not found, please install MSCL to use the MicroStrain IMUs. Please see https://github.com/LORD-MicroStrain/MSCL or the included setup script, ep-install-mscl.")
        
        self.verbose = verbose
        self.timeout = timeout
        self._enable_ports()
        self._imu_ref_rot_matrices = {}

        for i in range(num_retries):
            try:
                self._imu_nodes = self._set_up_connected_imus(
                    imu_ids=imu_ids,
                    rate=rate
                )

                # Set reference rotation matrices to identity or current rotation matrix
                if tare_on_startup:
                    self.tare_imu()
                else:
                    for imu_id in imu_ids:
                        self._imu_ref_rot_matrices[imu_id] = R.from_matrix(np.eye(3))

                break
            except Exception:
                if i == num_retries - 1:
                    print(f"Error initializing IMUs after {num_retries} attempts. Check that the IMUs are connected.")
                else:
                    if verbose:
                        print(f"Retrying initialization...")

    def _enable_ports(self) -> None:
        """Grant access to all ports used by Microstrains."""
        os.system("sudo chmod 777 /dev/ttyACM*")


    def _check_connected_imus(self) -> dict:
        """Check for connected IMUs and return a dictionary of mscl DeviceInfo objects

        Returns:
            connected_devices (dict): Dictionary of mscl DeviceInfo objects
            with serial ports as keys.
        """
        connected_devices = mscl.Devices.listInertialDevices()

        if self.verbose:
            print(f"Connected serial ports: {connected_devices.keys()}")

        return connected_devices


    def _set_up_connected_imus(self, imu_ids: List[str], rate: int) -> dict:
        """Set up connected IMUs and return a dictionary of MSCL Inertial Nodes

        Args:
            imu_ids (list): list of MSCL Inertial Node IMU IDs to set up.
            rate (float): rate at which each MSCL IMU object samples data.

        Returns:

            imus: Dictionary of MSCL Inertial Nodes with serial numbers as
                keys, and nodes and dataclasses as a tuple pair.
        """

        # Create a dictionary of MSCL Inertial Nodes
        devices = self._check_connected_imus()
        imus = {}

        try:
            # Iterate through IMU IDs detected by device
            for serial_port, device_info in devices.items():
                imu_id = device_info.serial().split(".")[1]

                # If IMU ID is in list of IMU IDs from config, include in dict
                if imu_id in imu_ids:
                    node = mscl.InertialNode(mscl.Connection.Serial(serial_port))
                    node_data = IMUData()
                    imus[imu_id] = (node, node_data)

            if self.verbose:
                print(f"Connected IMUs: {imus.keys()}")

        except Exception:
            print("Handling...")
            print("Tip: check that you set all the serial numbers of the IMUs properly!")

            for serial_port in devices.keys():
                tmp_connection = mscl.Connection.Serial(serial_port)
                tmp_connection.disconnect()

        # Set up active data channels for each node
        ahrs_channels = mscl.MipChannels()
        est_filter_channels = mscl.MipChannels()

        # Set data streams to collect
        ahrs_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_SENSOR_ORIENTATION_QUATERNION,
                mscl.SampleRate.Hertz(rate)
            )
        )
        ahrs_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_SENSOR_EULER_ANGLES,
                mscl.SampleRate.Hertz(rate)
            )
        )
        ahrs_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_SENSOR_SCALED_GYRO_VEC,
                mscl.SampleRate.Hertz(rate)
            )
        )
        ahrs_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_SENSOR_SCALED_ACCEL_VEC,
                mscl.SampleRate.Hertz(rate)
            )
        )
        ahrs_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_SENSOR_ORIENTATION_MATRIX,
                mscl.SampleRate.Hertz(rate)
            )
        )
        ahrs_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_SENSOR_SCALED_MAG_VEC,
                mscl.SampleRate.Hertz(rate)
            )
        )
        est_filter_channels.append(
            mscl.MipChannel(
                mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_ORIENT_QUATERNION,
                mscl.SampleRate.Hertz(rate)
            )
        )

        for imu_id, imu_node in imus.items():
            # Check connectivity status
            node_obj = imu_node[0]
            success = node_obj.ping()
    
            if self.verbose:
                print(f"{imu_id} works: {success}")

            # Activate and enable data streaming
            node_obj.setToIdle()
            node_obj.setActiveChannelFields(
                mscl.MipTypes.CLASS_AHRS_IMU,
                ahrs_channels
            )
            # node_obj.setActiveChannelFields(
            #     mscl.MipTypes.CLASS_ESTFILTER,
            #     est_filter_channels
            # ) # FOR ESTIMATION FILTER

            node_obj.enableDataStream(mscl.MipTypes.CLASS_AHRS_IMU)
            # node_obj.enableDataStream(mscl.MipTypes.CLASS_ESTFILTER) # FOR ESTIMATION FILTER

            node_obj.resume()

            # Ensure that sensor is in local frame (not some ref. frame)
            node_obj.setSensorToVehicleRotation_eulerAngles(
                mscl.EulerAngles(0, 0, 0)
            )

            if self.verbose:
                current_settings = node_obj.getComplementaryFilterSettings()
                print(
                    f"Complementary filter settings: {current_settings.upCompensationEnabled}, {current_settings.northCompensationEnabled}, {current_settings.upCompensationTimeInSeconds}, {current_settings.northCompensationTimeInSeconds}"
                )

            # Set complementary filter parameters # TODO: Check this part???? -> probably make the defaults the system defaults
            cf_filter_settings = mscl.ComplementaryFilterData()
            cf_filter_settings.upCompensationEnabled = True
            cf_filter_settings.northCompensationEnabled = False # True
            cf_filter_settings.upCompensationTimeInSeconds = 10
            cf_filter_settings.northCompensationTimeInSeconds = 60
            node_obj.setComplementaryFilterSettings(cf_filter_settings)

            if self.verbose:
                current_settings = node_obj.getComplementaryFilterSettings()
                print(
                    f"Complementary filter settings: {current_settings.upCompensationEnabled}, {current_settings.northCompensationEnabled}, {current_settings.upCompensationTimeInSeconds}, {current_settings.northCompensationTimeInSeconds}"
                )
                print(
                    f"(roll, pitch, yaw) tare settings: {node_obj.getSensorToVehicleRotation_eulerAngles().roll(),node_obj.getSensorToVehicleRotation_eulerAngles().pitch(),node_obj.getSensorToVehicleRotation_eulerAngles().yaw()}"
                )

        return imus


    def get_data(self, imu_id: str, raw=True) -> IMUData:
        """Get orientation, angular velocity and linear acceleration vector 
        from MSCL Inertial Node.

        Args:
            imu_id (str): serial number relating to MSCL Inertial Node
                        containing orientation, ang. velocity and lin.
                        acceleration.
            raw (bool): whether to provide IMU values relative to a zeroed
                        (static) reference frame obtained by calling
                        `self.tare_imus()`. Default: True (providing raw values).

        Returns:
            imu_data: IMUData dataclass object with orientation, angular
                    velocity and linear acceleration.
        """
        # Pre-populate imu_data with values in buffer (in case no new values)
        imu_node = self._imu_nodes[imu_id][0]
        imu_data = self._imu_nodes[imu_id][1]

        # Check through mscl Inertial Node collected packets
        packets = None
        start = time.perf_counter()

        # Reduce dropout when reading in new IMU data
        while not packets:
            packets = imu_node.getDataPackets(0)

            if time.perf_counter() - start > self.timeout:
                break
        
        # If there is new data in packets, use it
        if packets is not None and len(packets) > 0:
            last_packet = packets[-1]
            imu_data.timestamp = time.perf_counter()

            for data_point in last_packet.data():
                data_field = data_point.field()
                data_qualifier = data_point.qualifier()

                # TROUBLESHOOTING: check data qualifiers and channel IDs
                # if self.verbose:
                #     print(f"data_field: {data_field}, data_qualifier: {data_qualifier}, data_point.channelName(): {data_point.channelName()}")

                if (
                    data_field == mscl.MipTypes.CH_FIELD_SENSOR_ORIENTATION_QUATERNION
                ): # ORIENTATION QUATERNION
                    quat_vec = data_point.as_Vector()
                    imu_data.orientw = quat_vec.as_floatAt(0)
                    imu_data.orientx = quat_vec.as_floatAt(1)
                    imu_data.orienty = quat_vec.as_floatAt(2)
                    imu_data.orientz = quat_vec.as_floatAt(3)
                elif (
                    data_field == mscl.MipTypes.CH_FIELD_SENSOR_ORIENTATION_MATRIX
                ): # ORIENTATION MATRIX
                    rot_mat = data_point.as_Matrix()
                    imu_data.m11 = rot_mat.as_floatAt(0, 0)
                    imu_data.m12 = rot_mat.as_floatAt(0, 1)
                    imu_data.m13 = rot_mat.as_floatAt(0, 2)
                    imu_data.m21 = rot_mat.as_floatAt(1, 0)
                    imu_data.m22 = rot_mat.as_floatAt(1, 1)
                    imu_data.m23 = rot_mat.as_floatAt(1, 2)
                    imu_data.m31 = rot_mat.as_floatAt(2, 0)
                    imu_data.m32 = rot_mat.as_floatAt(2, 1)
                    imu_data.m33 = rot_mat.as_floatAt(2, 2)
                elif (
                    data_field == mscl.MipTypes.CH_FIELD_ESTFILTER_ESTIMATED_ORIENT_QUATERNION
                ): # EF QUATERNION
                    ef_quat_vec = data_point.as_Vector()
                    imu_data.ef_orientw = ef_quat_vec.as_Vector().as_floatAt(0)
                    imu_data.ef_orientx = ef_quat_vec.as_Vector().as_floatAt(1)
                    imu_data.ef_orienty = ef_quat_vec.as_Vector().as_floatAt(2)
                    imu_data.ef_orientz = ef_quat_vec.as_Vector().as_floatAt(3)
                elif (
                    data_field == mscl.MipTypes.CH_FIELD_SENSOR_EULER_ANGLES
                ): # EULER ORIENTATION (Computed)
                    if data_qualifier == mscl.MipTypes.CH_ROLL:
                        imu_data.roll = data_point.as_double()
                    elif data_qualifier == mscl.MipTypes.CH_PITCH:
                        imu_data.pitch = data_point.as_double()
                    elif data_qualifier == mscl.MipTypes.CH_YAW:
                        imu_data.yaw = data_point.as_double()
                elif (
                data_field == mscl.MipTypes.CH_FIELD_SENSOR_SCALED_GYRO_VEC
                ): # ANGULAR RATE (SCALED)
                    if data_qualifier == mscl.MipTypes.CH_X:
                        imu_data.gyrox = data_point.as_double()
                    elif data_qualifier == mscl.MipTypes.CH_Y:
                        imu_data.gyroy = data_point.as_double()
                    elif data_qualifier == mscl.MipTypes.CH_Z:
                        imu_data.gyroz = data_point.as_double()
                elif (data_field == mscl.MipTypes.CH_FIELD_SENSOR_SCALED_ACCEL_VEC
                ): # LINEAR ACCELERATION (SCALED)
                    if data_qualifier == mscl.MipTypes.CH_X:
                        imu_data.accx = data_point.as_double() * G_CONSTANT
                    elif data_qualifier == mscl.MipTypes.CH_Y:
                        imu_data.accy = data_point.as_double() * G_CONSTANT
                    elif data_qualifier == mscl.MipTypes.CH_Z:
                        imu_data.accz = data_point.as_double() * G_CONSTANT
                elif (
                data_field == mscl.MipTypes.CH_FIELD_SENSOR_SCALED_MAG_VEC
                ): # MAGNETOMETER (SCALED)
                    if data_qualifier == mscl.MipTypes.CH_X:
                        imu_data.magx = data_point.as_double()
                    if data_qualifier == mscl.MipTypes.CH_Y:
                        imu_data.magy = data_point.as_double()
                    if data_qualifier == mscl.MipTypes.CH_Z:
                        imu_data.magz = data_point.as_double()

        # Convert quaternion and Euler readings to be with respect to static values
        if not raw:
            # Get current rotation matrix and multiply it by inverse of
            # rotation matrix from zeroing for current IMU
            rot_raw = R.from_matrix(imu_data.matrix.T)
            rot_zeroed = self._imu_ref_rot_matrices[imu_id] * rot_raw

            # Convert orientation (quaternions)
            imu_data.orientx, imu_data.orienty, imu_data.orientz, imu_data.orientw = (
                rot_zeroed.as_quat()
            )

            # Convert orientation (Euler angles)
            imu_data.roll, imu_data.pitch, imu_data.yaw = list(
                rot_zeroed.as_euler("xyz", degrees=False)
            )

            ######## NOTE: ROTATION MATRIX NOT CONVERTED ########
            # USING THE `raw=False` OPTION DOES NOT CONVERT
            # THE ROTATION MATRIX. INSTEAD, QUATERNIONS AND
            # EULER ANGLES ARE CONVERTED, WHILE THE RAW AND REF.
            # ROTATION MATRICES ARE RETURNED AS IS. THE ZEROED
            # ROTATION MATRIX CAN STILL BE COMPUTED AFTERWARDS.
            #####################################################

        # Store ref. orientation (rotation matrix)
        converted_elements = []

        for elem in list(self._imu_ref_rot_matrices[imu_id].as_matrix()):
            for el in elem:
                converted_elements.append(el)

        (
            imu_data.ref_m11,
            imu_data.ref_m12,
            imu_data.ref_m13,
            imu_data.ref_m21,
            imu_data.ref_m22,
            imu_data.ref_m23,
            imu_data.ref_m31,
            imu_data.ref_m32,
            imu_data.ref_m33,
        ) = converted_elements

        self._imu_nodes[imu_id] = (imu_node, imu_data)

        return imu_data


    def tare_imu(self, imu_id=None, zeroing_time=0.25) -> None:
        """Manually tare MSCL Inertial Nodes.

        Args:
            imu_id (str): MSCL Inertial Node, or a list, set, tuple or dict of
                        MSCL Inertial Nodes.
            zeroing_time (float): time to get current raw rotation matrix.
        """
        t0 = time.perf_counter()

        while time.perf_counter() - t0 < zeroing_time:
            if imu_id is None:
                for imu_id, imu_node in self._imu_nodes.items():
                    self._imu_ref_rot_matrices[imu_id] = R.from_matrix(
                        self.get_data(imu_id, raw=True).matrix.T
                    ).inv()

            else:
                self._imu_ref_rot_matrices[imu_id] = R.from_matrix(
                    self.get_data(imu_id, raw=True).matrix.T
                ).inv()

        # TROUBLESHOOTING: get current reference rotation matrix
        # if self.verbose:
        #     print(f"static matrix: {self._imu_ref_rot_matrices[imu_id].as_quat()}")

    def __getitem__(self, index: str) -> IMUData:
        return self.get_data(index)


def main(imu_ids: List[str], rate=IMU_RATE, tare_on_startup=False) -> None:
    """Test implementation that constantly streams roll, pitch, yaw from
    each connected IMU.

    Args:
        imu_ids (list): dict of body segments and Microstrain serial numbers.
        use_euler (bool): boolean for whether to use Euler angle convention
                        (True) or Quaternion angle convention (False).
        rate (int): operational rate to set using internal MSCL library.
        tare_on_startup (bool): boolean for whether to automatically tare on
                                startup. Default: True.

    Returns:
        None
    """
    imus = MicrostrainImus(
        imu_ids=imu_ids,
        rate=rate,
        tare_on_startup=tare_on_startup,
        verbose=True
    )
    last_time = time.perf_counter()

    # Continuously stream data
    while True:
        for imu_id in imu_ids:
            current_time = time.perf_counter()
            print(
                f"[{(1/(current_time-last_time)):.4f}]: ID: {imu_id} | roll: {imus.get_data(imu_id, True).roll:.2f},\t pitch: {imus.get_data(imu_id, True).pitch:.2f},\t yaw: {imus.get_data(imu_id, True).yaw:.2f}"
            )
            last_time = current_time


if __name__ == "__main__":
    IMU_IDS = ['154138'] # , '133930']
    main(imu_ids=IMU_IDS)

