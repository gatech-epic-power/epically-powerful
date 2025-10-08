"""epically-powerful module for managing IMUs.

This module contains the classes and commands for initializing
and reading from MPU9250 IMUs.
"""

import os
import sys
import time
import json
from typing import Dict
import smbus2 as smbus # I2C bus library on Raspberry Pi and NVIDIA Jetson Orin Nano
from epicallypowerful.toolbox import LoopTimer
from epicallypowerful.sensing.imu_data import IMUData

# Unit conversions
PI = 3.1415926535897932384
GRAV_ACC = 9.81 # [m*s^-2]
DEG2RAD = PI/180
RAD2DEG = 180/PI

# Set MPU6050 (accelerometer) registers
MPU6050_ADDR = 0x68
MPU6050_ADDR_AD0_HIGH = 0x69
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
ACCEL_CONFIG = 0x1C
INT_PIN_CFG  = 0x37
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
TEMP_OUT_H   = 0x41
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

# Set AK8963 (magnetometer) registers
AK8963_ADDR  = 0x0C
AK8963_ST1   = 0x02
HXL          = 0x03
HXH          = 0x04
HYL          = 0x05
HYH          = 0x06
HZL          = 0x07
HZH          = 0x08
AK8963_ST1   = 0x02
AK8963_ST2   = 0x09
AK8963_CNTL  = 0x0A
AK8963_ASAX  = 0x10

# Set constants
MAG_SENS        = 4800.0 # magnetometer sensitivity: 4800 uT
MAG_RATE_8HZ    = 0b0010 # magnetometer sampling rate at 8 Hz
MAG_RATE_100HZ  = 0b0110 # magnetometer sampling rate at 100 Hz
ACC_RANGE_2G    = 0 # Set MPU6050 accelerometer resolution to +/- 2 g's
ACC_RANGE_4G    = 1 # Set MPU6050 accelerometer resolution to +/- 4 g's
ACC_RANGE_8G    = 2 # Set MPU6050 accelerometer resolution to +/- 8 g's
ACC_RANGE_16G   = 3 # Set MPU6050 accelerometer resolution to +/- 16 g's
GYRO_RANGE_250_DEG_PER_S  = 0 # Set MPU6050 gyroscope resolution to +/- 250.0 deg/s
GYRO_RANGE_500_DEG_PER_S  = 1 # Set MPU6050 gyroscope resolution to +/- 500.0 deg/s
GYRO_RANGE_1000_DEG_PER_S = 2 # Set MPU6050 gyroscope resolution to +/- 1000.0 deg/s
GYRO_RANGE_2000_DEG_PER_S = 3 # Set MPU6050 gyroscope resolution to +/- 1000.0 deg/s
SLEEP_TIME   = 0.1 # [s]

# Set PCA9548A (variant of TCA9548A) multiplexer register, channels and actions
MULTIPLEXER_ADDR = 0x70
MULTIPLEXER_ACTIONS = {
    0: 0x01,
    1: 0x02,
    2: 0x04,
    3: 0x08,
    4: 0x10,
    5: 0x20,
    6: 0x40,
    7: 0x80,
}


class MPU9250IMUs:
    """Class for interfacing with the MPU9250 IMU using I2C communication, leveraging the TCA9548A multiplexer for communicating with multiple units at the same time.

    This class draws from the following resources:
        - https://github.com/makerportal/mpu92-calibration
        - [LINK TO RESOURCE FOR TCA9548A INTEGRATION WITH MPU9250 UNITS]
        - [TDKINVENSENSE MPU9250 DATASHEET]
        - [PCA9548A DATASHEET]

    Many helper functions are included in the :py:class:`IMUData` class to assist with getting data conveniently. Please see that documentation for all options.

    Example (single sensor):
        .. code-block:: python

            from epicallypowerful.sensing import MPU9250IMUs

            ### Instantiation ---
            imu_ids = {
                0: {
                    'bus': 1,
                    'channel': -1, # -1 --> no multiplexer, otherwise --> multiplexer channel
                    'address': 0x68,
                },
                1: {
                    'bus': 1,
                    'channel': -1,
                    'address': 0x69,
                },
            }

            imus = MPU9250IMUs(
                imu_ids=imu_ids,
                components=['acc', 'gyro'],
            )

            ### Stream data ---
            print(imus.get_data(imu_id=0).accx)
            print(imus.get_data(imu_id=1).accx)

    Args:
        imu_ids (dict): dictionary of each IMU and the I2C bus number, multiplexer channel (if used), and I2C address needed to access it.
        components (list of strings): list of MPU9250 sensing components to get. Could include `acc`, `gyro`, or `mag`. For example, `components = ['acc','gyro','mag']` would call on both the MPU9250's MPU6050 and AK8963 boards, but `components = ['acc','gyro']` would only instantiate the MPU6050.
        acc_range_selector (int): index for range of accelerations to collect. Default: 2 (+/- 8 g), but can be:
            0: +/- 2.0 g's
            1: +/- 4.0 g's
            2: +/- 8.0 g's
            3: +/- 16.0 g's
        gyro_range_selector (int): index for range of angular velocities to collect. Default: 2 (+/- 1000.0 deg/s), but can be:
            0: +/- 250.0 deg/s
            1: +/- 500.0 deg/s
            2: +/- 1000.0 deg/s
            3: +/- 2000.0 deg/s
        calibration_path (str): path to JSON file with calibration values for IMUs to be connected. NOTE: this file indexes IMUs by which bus, multiplexer channel (if used), and I2C address they are connected to. Be careful not to use the calibration for one IMU connected in this way on another unit by mistake.
        verbose (bool): whether to print verbose output from IMU operation. Default: False.
    """

    def __init__(
        self,
        imu_ids: dict[int, dict[int, str, hex]],
        components=['acc','gyro'],
        acc_range_selector=ACC_RANGE_8G,
        gyro_range_selector=GYRO_RANGE_1000_DEG_PER_S,
        calibration_path='',
        verbose: bool=False,
    ) -> None:
        if imu_ids is None:
            raise Exception('`imu_ids` must contain at least one IMU index.')
        elif not isinstance(imu_ids,dict):
            raise Exception ('`imu_ids` must be in the form of dict(int, dict(int bus_id, int channel, hex imu_id).')

        # Initialize all IMU-specific class attributes
        self.imu_ids = imu_ids
        self.components = components
        self.acc_range_selector = acc_range_selector
        self.gyro_range_selector = gyro_range_selector
        self.verbose = verbose
        self.bus = {}
        self.calibration_dict = {}
        self.prev_channel = -1

        # Look for existing calibrations for IMUs
        if len(calibration_path) > 0:
            if self.verbose:
                print(f"Looking for calibration at: {calibration_path}")
            
            if os.path.isfile(calibration_path):                
                with open(calibration_path, "r") as f:
                    self.calibration_dict = json.load(f)

                if self.verbose:
                    print(f"Found calibration file!")
            else:        
                if self.verbose:
                    print("No calibration file found. Proceeding with raw values...")
        else:
            if self.verbose:
                print(f"No calibration path provided. Proceeding with raw values...")

        # Initialize all MPU9250 units
        self.imus, self.startup_config_vals = self._set_up_connected_imus(imu_ids=self.imu_ids)


    def _set_up_connected_imus(
        self,
        imu_ids: dict[int, dict[int, int, hex]],
    ) -> tuple[list[float]]:
        """Initialize all IMUs from dictionary of IMU IDs, buses, channels, and addresses. Here you specify which IMU components to start, as well as their corresponding sensing resolution.

        Args:
            imu_ids (dict): dictionary of each IMU and the I2C bus number, multiplexer channel (if used), and I2C address needed to access it.

        Returns:
            startup_config_vals (dict of floats): MPU9250 sensor configuration values: acc_range, gyro_range, mag_coeffx, mag_coeffy, mag_coeffz.
        """
        imus = {}

        for imu_id in imu_ids.keys():
            # Get all relevant components to communicate with IMU
            bus_id = imu_ids[imu_id]['bus'] 
            channel = imu_ids[imu_id]['channel']
            address = imu_ids[imu_id]['address']

            # Initialize I2C bus if it hasn't been initialized yet
            if bus_id not in self.bus.keys():
                self.bus[bus_id] = smbus.SMBus(bus_id)

            # If channel is in range for multiplexion (not default -1 value) 
            # and no channel-switching command has already been sent on current bus, 
            # send multiplexer channel switch command
            if channel in range(0, 8):
                if channel is not self.prev_channel:
                    self.bus[bus_id].write_byte_data(
                        i2c_addr=MULTIPLEXER_ADDR,
                        register=0x04,
                        value=MULTIPLEXER_ACTIONS[channel],
                    )
                    self.prev_channel = channel

            startup_config_vals = {}

            # Start accelerometer and gyro if configured to do so
            if any([c for c in self.components if (('acc' in c) or ('gyro' in c))]):
                (startup_config_vals[imu_id]['acc_range'],
                startup_config_vals[imu_id]['gyro_range'],
                ) = self._set_up_MPU6050(
                        bus=bus,
                        address=address,
                        acc_range_idx=self.acc_range_selector,
                        gyro_range_idx=self.gyro_range_selector,
                )
            
            # Start magnetometer if configured to do so
            if any([c for c in self.components if 'mag' in c]):
                (startup_config_vals[imu_id]['mag_coeffx'],
                startup_config_vals[imu_id]['mag_coeffy'],
                startup_config_vals[imu_id]['mag_coeffz'],
                ) = self._set_up_AK8963(bus=bus)

            if self.verbose:
                print(f"IMU {imu_id} startup_config_vals: {startup_config_vals[imu_id]}\n")

            imus[imu_id] = IMUData()
        
        return imus, startup_config_vals


    def _set_up_MPU6050(
        self,
        bus: smbus.SMBus=smbus.SMBus(),
        address=MPU6050_ADDR,
        acc_range_idx=ACC_RANGE_8G,
        gyro_range_idx=GYRO_RANGE_1000_DEG_PER_S,
        sample_rate_divisor=0,
        sleep_time=SLEEP_TIME,
    ) -> tuple[float]:
        """Set up MPU6050 integrated accelerometer and gyroscope on MPU9250.

        Args:
            bus (smbus.SMBus): I2C bus instance on the device.
            address (hex): address of the MPU6050 unit. Default set outside this function.
            acc_range_idx (int): index for range of accelerations to collect. Used to set in byte registers on startup. Default: 2 (+/- 8 g), but can be:
                0: +/- 2.0 g's
                1: +/- 4.0 g's
                2: +/- 8.0 g's
                3: +/- 16.0 g's
            gyro_range_idx (int): index for range of angular velocities to collect. Used to set in byte registers on startup. Default: 2 (+/- 1000.0 deg/s), but can be:
                0: +/- 250.0 deg/s
                1: +/- 500.0 deg/s
                2: +/- 1000.0 deg/s
                3: +/- 2000.0 deg/s
            sample_rate_divisor (int): divisor term to lower possible sampling rate. Equation: sampling_rate = 8 kHz/(1+sample_rate_divisor). Default: 0.
            sleep_time (float): time to sleep between sending and receiving signals. Default: 0.1 seconds.

        Returns:
            acc_config_vals (list of floats): +/- range of accelerometer values collected for each sensor.
            gyro_config_vals (list of floats): +/- range of gyroscope values collected for each sensor.
        """
        # Reset all integrated sensors
        bus.write_byte_data(address, PWR_MGMT_1, 0x80)
        time.sleep(sleep_time)
        bus.write_byte_data(address, PWR_MGMT_1, 0x00)
        time.sleep(sleep_time)

        # Set power management and crystal settings
        bus.write_byte_data(address, PWR_MGMT_1, 0x01)
        time.sleep(sleep_time)

        # Set sample rate (stability) --> only change 
        # sample_rate_divisor if you don't want to collect at default (8 kHz)
        bus.write_byte_data(address, SMPLRT_DIV, sample_rate_divisor)
        time.sleep(sleep_time)

        # Write to configuration register
        bus.write_byte_data(address, CONFIG, 0)
        time.sleep(sleep_time)

        # Write to accel configuration register
        acc_config_sel = [0b00000, 0b01000, 0b10000, 0b11000] # byte registers
        acc_config_vals = [2.0, 4.0, 8.0, 16.0] # +/- val. range [g] (1 g = 9.81 m*s^-2)
        bus.write_byte_data(address, ACCEL_CONFIG, int(acc_config_sel[acc_range_idx]))
        time.sleep(sleep_time)

        # Write to gyro configuration register
        gyro_config_sel = [0b00000, 0b01000, 0b10000, 0b11000] # byte registers
        gyro_config_vals = [250.0, 500.0, 1000.0, 2000.0] # +/- val. range [deg/s]
        bus.write_byte_data(address, GYRO_CONFIG, int(gyro_config_sel[gyro_range_idx]))
        time.sleep(sleep_time)
        
        # Interrupt register (related to overflow of data [FIFO])
        bus.write_byte_data(address,INT_PIN_CFG,0x22)
        time.sleep(sleep_time)

        # Enable the AK8963 magnetometer in pass-through mode
        bus.write_byte_data(address, INT_ENABLE, 1)
        time.sleep(sleep_time)

        return acc_config_vals[acc_range_idx], gyro_config_vals[gyro_range_idx]


    def _set_up_AK8963(
        self,
        bus: smbus.SMBus=smbus.SMBus(),
        rate_selector=MAG_RATE_100HZ,
        sleep_time=SLEEP_TIME,
    ) -> tuple:
        """Set up AK8963 integrated magnetometer on MPU9250.

        Args:
            bus (smbus.SMBus): I2C bus instance on the device.
            rate_selector (binary): rate at which to sample. Default: 0b0110 (100 Hz). Could also do 0b0010 (8 Hz).
            sleep_time (float): time to sleep between sending and receiving signals. Default: 0.1 seconds.

        Returns:
            [coeffx, coeffy, coeffz] (list of floats): coefficients for each DOF.
        """
        # Initialize magnetometer mode
        bus.write_byte_data(AK8963_ADDR,AK8963_CNTL, 0x00)
        time.sleep(sleep_time)
        bus.write_byte_data(AK8963_ADDR,AK8963_CNTL, 0x0F)
        time.sleep(sleep_time)
        
        # Read coefficient data from circuit address
        coeff_data = bus.read_i2c_block_data(AK8963_ADDR, AK8963_ASAX, 3)
        coeffx = (0.5 * (coeff_data[0] - 128)) / 256.0 + 1.0
        coeffy = (0.5 * (coeff_data[1] - 128)) / 256.0 + 1.0
        coeffz = (0.5 * (coeff_data[2] - 128)) / 256.0 + 1.0
        time.sleep(sleep_time)
        
        # Reinitialize magnetometer
        bus.write_byte_data(AK8963_ADDR, AK8963_CNTL, 0x00)
        time.sleep(sleep_time)

        # Set magnetometer resolution and frequency of communication
        bit_resolution = 0b0001 # specifies 16-bit precision
        AK8963_mode = (bit_resolution << 4) + rate_selector
        bus.write_byte_data(AK8963_ADDR, AK8963_CNTL, AK8963_mode)
        time.sleep(sleep_time)

        return coeffx, coeffy, coeffz


    def get_data(self, imu_id: int) -> IMUData:
        """Get acceleration, gyroscope, and magnetometer data from MPU9250.

        Args:
            imu_id (int): IMU number (index number from starting dict, not address).

        Returns:
            imu_data (IMUData): IMU data of the current sensor.
        """
        imu_data = IMUData()
        bus = self.bus[self.imu_ids[imu_id]['bus']]
        channel = self.imu_ids[imu_id]['channel']
        address = self.imu_ids[imu_id]['address']
        cal_id = f"{self.imu_ids[imu_id]['bus']}_{channel}_{address}"
        
        # If using multiplexer, switch to proper channel
        if channel in range(0,8):
            if channel is not self.prev_channel:
                bus.write_byte_data(
                    i2c_addr=MULTIPLEXER_ADDR,
                    register=0x04,
                    value=MULTIPLEXER_ACTIONS[channel],
                )
                self.prev_channel = channel

        # Get accelerometer and gyroscope data
        if any([c for c in self.components if (('acc' in c) or ('gyro' in c))]):
            (imu_data.accx,
            imu_data.accy,
            imu_data.accz,
            imu_data.gyrox,
            imu_data.gyroy,
            imu_data.gyroz,
            imu_data.temp,
            ) = self.get_MPU6050_data(
                bus=bus,
                acc_range=self.startup_config_vals['acc_range'],
                gyro_range=self.startup_config_vals['gyro_range'],
                address=address,
            )

            # If calibrations exist for current IMU, apply them
            if cal_id in self.calibration_dict.keys():
                # Calibrate accelerometer readings using a linear fit
                if len(self.calibration_dict[cal_id]["acc"]) > 0:
                    m_x = self.calibration_dict[cal_id]["acc"][0][0] # slope
                    b_x = self.calibration_dict[cal_id]["acc"][0][1] # offset
                    imu_data.accx = m_x * (imu_data.accx) + b_x

                    m_y = self.calibration_dict[cal_id]["acc"][1][0] # slope
                    b_y = self.calibration_dict[cal_id]["acc"][1][1] # offset
                    imu_data.accy = m_y * (imu_data.accy) + b_y

                    m_z = self.calibration_dict[cal_id]["acc"][2][0] # slope
                    b_z = self.calibration_dict[cal_id]["acc"][2][1] # offset
                    imu_data.accz = m_z * (imu_data.accz) + b_z

                # Calibrate gyroscope by subtracting an offset from each axis
                if len(self.calibration_dict[cal_id]["gyro"]) > 0:
                    imu_data.gyrox = imu_data.gyrox - self.calibration_dict[cal_id]["gyro"][0]
                    imu_data.gyroy = imu_data.gyroy - self.calibration_dict[cal_id]["gyro"][1]
                    imu_data.gyroz = imu_data.gyroz - self.calibration_dict[cal_id]["gyro"][2]

        # Get magnetometer data
        if any([c for c in self.components if 'mag' in c]):
            (imu_data.magx,
            imu_data.magy,
            imu_data.magz,
            ) = self.get_AK8963_data(
                bus=bus,
                mag_coeffs=[
                    self.startup_config_vals['mag_coeffx'],
                    self.startup_config_vals['mag_coeffy'],
                    self.startup_config_vals['mag_coeffz'],
                ],
            )

            # If calibrations exist for current IMU, apply them
            if cal_id in self.calibration_dict.keys():
                # Calibrate gyroscope by subtracting an offset from each axis
                if len(self.calibration_dict[cal_id]["mag"]) > 0:
                    imu_data.magx = imu_data.magx - self.calibration_dict[cal_id]["mag"][0]
                    imu_data.magy = imu_data.magy - self.calibration_dict[cal_id]["mag"][1]
                    imu_data.magz = imu_data.magz - self.calibration_dict[cal_id]["mag"][2]

        # Update IMU data class dictionary
        imu_data.timestamp = time.perf_counter()
        self.imus[imu_id] = imu_data

        return imu_data


    def get_MPU6050_data(
        self,
        bus: smbus.SMBus,
        acc_range: float,
        gyro_range: float,
        address: hex=MPU6050_ADDR,
    ) -> tuple[float]:
        """Convert raw binary accelerometer, gyroscope, and temperature readings to floats.

        Args:
            bus (smbus.SMBus): I2C bus instance on the device.
            acc_range (float): +/- range of acceleration being read from MPU6050. Raw units are g's (1 g = 9.81 m*s^-2).
            gyro_range (float): +/- range of gyro being read from MPU6050. Raw units are deg/s.
            address (hex): address of the MPU6050 subcircuit.

        Returns:
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temp (floats): acceleration [g], gyroscope [deg/s], and temperature [Celsius] values.
        """
        data = bus.read_i2c_block_data(
            i2c_addr=address,
            register=ACCEL_XOUT_H,
            length=14,
        )

        # Convert from bytes to ints
        raw_acc_x = self._convert_raw_data(data[0], data[1])
        raw_acc_y = self._convert_raw_data(data[2], data[3])
        raw_acc_z = self._convert_raw_data(data[4], data[5])
        raw_temp = self._convert_raw_data(data[6], data[7])
        raw_gyro_x = self._convert_raw_data(data[8], data[9])
        raw_gyro_y = self._convert_raw_data(data[10], data[11])
        raw_gyro_z = self._convert_raw_data(data[12], data[13])

        # Convert from bits to g's (accel.), deg/s (gyro), and  then 
        # from those base units to m*s^-2 and rad/s respectively
        acc_x = (raw_acc_x / (2.0**15.0)) * acc_range * GRAV_ACC
        acc_y = (raw_acc_y / (2.0**15.0)) * acc_range * GRAV_ACC
        acc_z = (raw_acc_z / (2.0**15.0)) * acc_range * GRAV_ACC
        gyro_x = (raw_gyro_x / (2.0**15.0)) * gyro_range * DEG2RAD
        gyro_y = (raw_gyro_y / (2.0**15.0)) * gyro_range * DEG2RAD
        gyro_z = (raw_gyro_z / (2.0**15.0)) * gyro_range * DEG2RAD
        temp = (raw_temp / 333.87 + 21.0) # TODO: CHECK THIS

        return (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temp)


    def get_AK8963_data(
        self,
        bus: smbus.SMBus,
        address=AK8963_ADDR,
        mag_coeffs=[],
    ) -> tuple:
        """Convert raw binary magnetometer readings to floats.

        Args:
            bus (smbus.SMBus): I2C bus instance on the device.
            address (hex): address of AK8963 sensor. Should always be default AK8963_ADDR value (defined outside function).
            mag_coeffs (list of floats): coefficients set from AK8963. Raw units are micro-T (uT).

        Returns:
            mag_x, mag_y, mag_z (floats): magnetometer values (in uT).
        """
        # Read raw magnetometer bits
        num_tries = 0
        try_lim = 500

        while num_tries < try_lim:
            data = bus.read_i2c_block_data(
                i2c_addr=address,
                register=HXL,
                length=7,
            )

            # The next line is needed for AK8963
            if (bus.read_byte_data(address, AK8963_ST2)) & 0x08!=0x08:
                break

            num_tries += 1

        raw_mag_x = self._convert_raw_data(data[0], data[1])
        raw_mag_y = self._convert_raw_data(data[2], data[3])
        raw_mag_z = self._convert_raw_data(data[4], data[5])

        # Convert from bits to uT
        mag_x = (raw_mag_x/(2.0**15.0)) * mag_coeffs[0]
        mag_y = (raw_mag_y/(2.0**15.0)) * mag_coeffs[1]
        mag_z = (raw_mag_z/(2.0**15.0)) * mag_coeffs[2]
        
        return mag_x, mag_y, mag_z


    def _read_raw_bytes(
        self,
        bus: smbus.SMBus,
        address: hex,
        register: hex,
    ) -> int:
        raise NotImplementedError

        """Method of reading raw data from different subcircuits 
        on the MPU9250 board.

        Args:
            bus (smbus.SMBus): I2C bus instance on the device.
            address (hex): address of the subcircuit being read from.
            register (hex): register from which to pull specific data.

        Returns:
            value (int): raw value pulled from specific register and converted to int.
        """
        if address == MPU6050_ADDR or address == MPU6050_ADDR_AD0_HIGH:
            # Read accel and gyro values
            high = bus.read_byte_data(address, register)
            low = bus.read_byte_data(address, register+1)
        elif address == AK8963_ADDR:            
            # read magnetometer values
            high = bus.read_byte_data(address, register)
            low = bus.read_byte_data(address, register-1)

        # Combine high and low for unsigned bit value
        value = ((high << 8) | low)
        
        # Convert to +/- value
        if(value > 32768):
            value -= 65536

        return value


    def _convert_raw_data(
        self,
        high_data: int,
        low_data: int,
    ) -> int:
        # Combine high and low for unsigned bit value
        value = ((high_data << 8) | low_data)
        
        # Convert to +/- value
        if(value > 32768):
            value -= 65536

        return value


    def exit_gracefully(self) -> None:
        """Exit MPU-9250 communication across all connected I2C buses gracefully. Handle multithreading as present.

        Args:
            None

        Returns:
            None
        """
        raise NotImplementedError

        os.write(sys.stdout.fileno(), b"Exiting gracefully\n")

        try:
            for b in self.bus.keys():
                self.bus[b].join()
        except:
            sys.exit("Failed to kill threads for I2C buses.\n")

        os.write(sys.stdout.fileno(), b"Shutdown finished.\n")
        sys.exit(0)


if __name__ == "__main__":
    import platform
    machine_name = platform.uname().release.lower()
    if "tegra" in machine_name:
        bus_ids = [1,7]
    elif "rpi" in machine_name or "bcm" in machine_name or "raspi" in machine_name:
        bus_ids = [1,4]
    else:
        bus_ids = [1]

    imu_ids = {
        0:
            {
                'bus': bus_ids[0],
                'channel': -1,
                'address': 0x68,
            },
        1:
            {
                'bus': bus_ids[0],
                'channel': -1,
                'address': 0x69,
            },
        2:
            {
                'bus': bus_ids[1],
                'channel': 2,
                'address': 0x68,
            },
        3:
            {
                'bus': bus_ids[1],
                'channel': 2,
                'address': 0x69,
            },
        4:
            {
                'bus': bus_ids[1],
                'channel': 4,
                'address': 0x68,
            },
        5:
            {
                'bus': bus_ids[1],
                'channel': 4,
                'address': 0x69,
            },
    }

    components = ['acc','gyro']
    verbose = True

    mpu9250_imus = MPU9250IMUs(
        imu_ids=imu_ids,
        components=components,
        verbose=verbose,
    )

    loop = LoopTimer(operating_rate=160, verbose=True)
    
    while True:
        if loop.continue_loop():
            # Get data
            for imu_id in imu_ids.keys():
                imu_data = mpu9250_imus.get_data(imu_id=imu_id)
                print(f"{imu_id}: acc_x: {imu_data.accx:0.2f}, acc_y: {imu_data.accy:0.2f}, acc_z: {imu_data.accz:0.2f}, gyro_x: {imu_data.gyrox:0.2f}, gyro_y: {imu_data.gyroy:0.2f}, gyro_z: {imu_data.gyroz:0.2f}")

    mpu9250_imus.exit_gracefully()