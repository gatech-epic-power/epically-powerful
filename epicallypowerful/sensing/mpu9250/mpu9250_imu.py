"""epically-powerful module for managing IMUs.

This module contains the classes and commands for initializing
and reading from Microstrain IMUs using the MSCL package.

"""

import os
import sys
import time
import threading
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
HXH          = 0x04
HYH          = 0x06
HZH          = 0x08
AK8963_ST1   = 0x02
AK8963_ST2   = 0x09
AK8963_CNTL  = 0x0A
AK8963_ASAX  = 0x10

# Set constants
MAG_SENS = 4800.0 # magnetometer sensitivity: 4800 uT
SLEEP_TIME = 0.1 # [s]

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
        - work of Joshua Hrisko's GitHub repository for single IMU communication
        - [LINK TO RESOURCE FOR TCA9548A INTEGRATION WITH MPU9250 UNITS]
        - [TDKINVENSENSE MPU9250 DATASHEET]
        - [PCA9548A DATASHEET]

    Many helper functions are included in the :py:class:`IMUData` class to assist with getting data conveniently. Please see that documentation for all options.

    Example (single sensor):
        .. code-block:: python

            from epicpower.sensing import MPU9250IMUs

            [FINISH]

    Example (multiple sensors with I2C multiplexer):
        .. code-block:: python

            from epicpower.sensing import MPU9250IMUs

            [FINISH]

    """

    def __init__(
        self,
        bus: int,
        imu_ids: dict[int,dict[str,hex]],
        use_multiplexer=False,
        components=['acc','gyro'],
        verbose: bool=False
    ) -> None:
        if imu_ids is None:
            raise Exception('`imu_ids` must contain at least one IMU index.')
        elif not isinstance(imu_ids,dict):
            raise Exception ('`imu_ids` must be in the form of dict(int channel, hex imu_id).')

        if not isinstance(bus,list):
            bus = [bus]

        self.bus = {}
        
        for b in bus:
            # self.bus[b] = smbus.SMBus(b)

            # Threading approach
            self.bus[b] = threading.Thread(target=smbus.SMBus, name=b).start()

        self.imu_ids = imu_ids
        self.use_multiplexer = use_multiplexer
        self.components = components
        self.verbose = verbose
        self.imus = {}
        
        # Determine whether to use multiplexer based on number of IMU indices detected
        if not use_multiplexer: # Initialize without multiplexer
            if verbose:
                print("Using only one IMU index defaults to not instantiating multiplexer.")
                print("If you have configured a multiplexer with a single IMU, consider using just the IMU without the multiplexer.")
                print("(You can still use a single IMU with the multiplexer, just set `use_multiplexer` to True.)")
        else: # Initialize with multiplexer
            use_multiplexer = True
            self.prev_channel = -1

            if verbose:
                print("Using multiplexer...")

        # Initialize all MPU9250 units
        for imu_id in self.imu_ids.keys():
            bus_id = self.imu_ids[imu_id]['bus']
            channel = self.imu_ids[imu_id]['channel']
            address = self.imu_ids[imu_id]['address']
        # for bus_id in self.bus.keys():
        #     for channel,idx in imu_ids[bus_id].items():
            if not use_multiplexer:
                # self._check_connected_imu(device_address=idx)
                self.startup_config_vals = self._set_up_connected_imu(
                                                                    bus_id=bus_id,
                                                                    device_address=address,
                                                                    components=self.components,
                                                                    )
            else:
                if channel in range(0,8):
                    if channel is not self.prev_channel:
                        self.bus[bus_id].write_byte_data(MULTIPLEXER_ADDR, 0x04, MULTIPLEXER_ACTIONS[channel])
                        self.prev_channel = channel
                    
                    # self._check_connected_imu(device_address=idx) # TODO: implement
                    self.startup_config_vals = self._set_up_connected_imu(bus_id=bus_id,
                                                                        device_address=address,
                                                                        components=self.components,
                                                                        )
                else:
                    raise Exception('Need channel in range (0,7) for multiplexer.')

            self.imus[imu_id] = IMUData()


    def _check_connected_imu(self, device_address: hex):
        """Check if IMU address is visible through I2C."""
        raise NotImplementedError


    def _set_up_connected_imu(
        self,
        bus_id: int,
        device_address: hex,
        components: list[str]
    ) -> dict[float]:
        """Get +/- ranges of acceleration and gyro, as well as 
        magnetometer coefficients.

        Args:
            bus_id (int): I2C bus on the device.
            device_address (hex): address of the MPU9250 IMU.
            components (list of strings): list of MPU9250 sensing components to get.
                                            Could include `acc`, `gyro`, or `mag`. For 
                                            example, `components = ['acc','gyro','mag']` 
                                            would call on both MPU6050 and AK8963, but 
                                            `components = ['acc','gyro']` would only 
                                            instantiate the MPU6050.
        Returns:
            startup_config_vals (dict of floats): MPU9250 sensor configuration values:
                                                accel_range, gyro_range, mag_coeffx, mag_coeffy, mag_coeffz.
        """
        startup_config_vals = {}

        # Start accelerometer and gyro
        if any([c for c in components if (('acc' in c) or ('gyro' in c))]):
            accel_range, gyro_range = self._set_up_MPU6050(bus_id=bus_id,
                                                            address=device_address,
                                                            )
            startup_config_vals['accel_range'] = accel_range
            startup_config_vals['gyro_range'] = gyro_range

        # Start magnetometer
        if any([c for c in components if 'mag' in c]):
            mag_coeffx, mag_coeffy, mag_coeffz, = self._set_up_AK8963(bus_id=bus_id)
            startup_config_vals['mag_coeffx'] = mag_coeffx
            startup_config_vals['mag_coeffy'] = mag_coeffy
            startup_config_vals['mag_coeffz'] = mag_coeffz

        return startup_config_vals
    

    def _set_up_MPU6050(
        self,
        bus_id: int=1,
        address=MPU6050_ADDR,
        sample_rate_divisor=0,
        accel_idx=0,
        gyro_idx=0,
        sleep_time=SLEEP_TIME,
    ) -> tuple[float]:
        """Set up MPU6050 integrated accelerometer and gyroscope on MPU9250.

        Args:
            bus_id (int): I2C bus on the device. Default: 1.
            address (hex): address of the MPU6050 unit. Default set outside this function.
            sample_rate_divisor (int): divisor term to lower possible sampling rate. 
                                Equation: sampling_rate = 8 kHz/(1+sample_rate_divisor).
                                Default: 0.
            accel_idx (int): index for range of accelerations to collect. Used to 
                            set in byte registers on startup. Default: 0 (+/- 2 g), 
                            but can be:
                            0: +/- 2.0 g's
                            1: +/- 4.0 g's
                            2: +/- 8.0 g's
                            3: +/- 16.0 g's
            gyro_idx (int): index for range of angular velocities to collect. Used to 
                            set in byte registers on startup. Default: 0 (+/- 250.0 deg/s), 
                            but can be:
                            0: +/- 250.0 deg/s
                            1: +/- 500.0 deg/s
                            2: +/- 1000.0 deg/s
                            3: +/- 2000.0 deg/s
            sleep_time (float): time to sleep between sending and receiving signals. 
                                Default: 0.1 seconds (defined outside this function).

        Returns:
            [accel_config_vals, gyro_config_vals] (list of floats): +/- range of values 
                                                            collected for each sensor.
        """
        # Reset all integrated sensors
        self.bus[bus_id].write_byte_data(address, PWR_MGMT_1, 0x80)
        time.sleep(sleep_time)
        self.bus[bus_id].write_byte_data(address, PWR_MGMT_1, 0x00)
        time.sleep(sleep_time)

        # Set power management and crystal settings
        self.bus[bus_id].write_byte_data(address, PWR_MGMT_1, 0x01)
        time.sleep(sleep_time)

        # Set sample rate (stability) --> only do if you don't want to collect at default: 8 kHz
        self.bus[bus_id].write_byte_data(address, SMPLRT_DIV, sample_rate_divisor)
        time.sleep(sleep_time)

        # Write to configuration register
        self.bus[bus_id].write_byte_data(address, CONFIG, 0)
        time.sleep(sleep_time)

        # Write to accel configuration register
        accel_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
        accel_config_vals = [2.0,4.0,8.0,16.0] # +/- val. range [g] (1 g = 9.81 m*s^-2)
        self.bus[bus_id].write_byte_data(address, ACCEL_CONFIG, int(accel_config_sel[accel_idx]))
        time.sleep(sleep_time)

        # Write to gyro configuration register
        gyro_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
        gyro_config_vals = [250.0,500.0,1000.0,2000.0] # +/- val. range [deg/s]
        self.bus[bus_id].write_byte_data(address, GYRO_CONFIG, int(gyro_config_sel[gyro_idx]))
        time.sleep(sleep_time)
        
        # Interrupt register (related to overflow of data [FIFO])
        self.bus[bus_id].write_byte_data(address,INT_PIN_CFG,0x22)
        time.sleep(sleep_time)

        # Enable the AK8963 magnetometer in pass-through mode
        self.bus[bus_id].write_byte_data(address, INT_ENABLE, 1)
        time.sleep(sleep_time)

        return accel_config_vals[accel_idx], gyro_config_vals[gyro_idx]


    def _set_up_AK8963(
        self,
        bus_id: int=1,
        bit_resolution=0b0001, # Select 16-bit res.
        sample_rate=0b0110,    # Select 100 Hz sampling rate
        sleep_time=SLEEP_TIME,
    ) -> tuple:
        """Set up AK8963 integrated magnetometer on MPU9250.

        Args:
            bus_id (int): I2C bus on the device. Default: 1.
            bit_resolution (binary): bit resolution at which to sample data.
                                    Default: 0b0001 (16-bit).
            sample_rate (binary): rate at which to sample. Default: 0b0110 (100 Hz).
                                    Could also do 0b0010 (8 Hz).
            sleep_time (float): time to sleep between sending and receiving signals. 
                                Default: 0.1 seconds (defined outside this function).

        Returns:
            [coeffx, coeffy, coeffz] (list of floats): coefficients for each DOF
        """
        # Initialize magnetometer mode
        self.bus[bus_id].write_byte_data(AK8963_ADDR,AK8963_CNTL,0x00)
        time.sleep(sleep_time)
        self.bus[bus_id].write_byte_data(AK8963_ADDR,AK8963_CNTL,0x0F)
        time.sleep(sleep_time)
        
        # Read coefficient data from circuit address
        coeff_data = self.bus[bus_id].read_i2c_block_data(AK8963_ADDR,AK8963_ASAX,3)
        coeffx = (0.5 * (coeff_data[0] - 128)) / 256.0 + 1.0
        coeffy = (0.5 * (coeff_data[1] - 128)) / 256.0 + 1.0
        coeffz = (0.5 * (coeff_data[2] - 128)) / 256.0 + 1.0
        time.sleep(sleep_time)
        
        # Reinitialize magnetometer
        self.bus[bus_id].write_byte_data(AK8963_ADDR,AK8963_CNTL,0x00)
        time.sleep(sleep_time)

        # Set magnetometer resolution and frequency of communication
        AK8963_mode = (bit_resolution << 4) + sample_rate # bit conversion
        self.bus[bus_id].write_byte_data(AK8963_ADDR,AK8963_CNTL,AK8963_mode)
        time.sleep(sleep_time)

        return coeffx,coeffy,coeffz


    def get_data(self, imu_id: int) -> IMUData:
        """Get acceleration, gyroscope, and magnetometer 
        data from MPU9250.

        Args:
            imu_id (int): IMU ID address.

        Returns:
            imu_data (IMUData): IMU data of the current sensor.
        """
        imu_data = IMUData()
        bus_id = self.imu_ids[imu_id]['bus']
        channel = self.imu_ids[imu_id]['channel']
        address = self.imu_ids[imu_id]['address']

        # If using multiplexer, switch to proper channel
        if use_multiplexer:
            if channel in range(0,8):
                if channel is not self.prev_channel:
                    self.bus[bus_id].write_byte_data(MULTIPLEXER_ADDR, 0x04, MULTIPLEXER_ACTIONS[channel])
                    self.prev_channel = channel
            else:
                raise Exception('Need channel in range (0,7) for multiplexer.')

        # Get accelerometer and gyroscope data
        if any([c for c in self.components if (('acc' in c) or ('gyro' in c))]):
            (imu_data.accx,
            imu_data.accy,
            imu_data.accz,
            imu_data.gyrox,
            imu_data.gyroy,
            imu_data.gyroz
            ) = self.get_MPU6050_data(
                bus_id=bus_id,
                accel_range=self.startup_config_vals['accel_range'],
                gyro_range=self.startup_config_vals['gyro_range'],
                address=address,
            )

        # Get magnetometer data
        if any([c for c in self.components if 'mag' in c]):
            (imu_data.magx,
            imu_data.magy,
            imu_data.magz
            ) = self.get_AK8963_data(
                bus_id=bus_id,
                mag_coeffs=[self.startup_config_vals['mag_coeffx'], startup_config_vals['mag_coeffy'], startup_config_vals['mag_coeffz']],
            )

        # Update IMU data class dictionary
        self.imus[imu_id] = imu_data

        return imu_data


    def get_MPU6050_data(
        self,
        bus_id: int,
        accel_range: float,
        gyro_range: float,
        address: hex=MPU6050_ADDR,
    ) -> tuple[float]:
        """Convert raw binary accelerometer and gyroscope readings to floats.

        Args:
            bus_id (int): I2C bus on the device.
            accel_range (float): +/- range of acceleration being 
                                read from MPU6050. Units are 
                                g's (1 g = 9.81 m*s^-2).
            gyro_range (float): +/- range of gyro being 
                                read from MPU6050. Units are deg/s.
            address (hex): address of the MPU6050 subcircuit.

        Returns:
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z (floats): acceleration and gyroscope values
        """
        # Get raw acceleration bits
        raw_acc_x = self._read_raw_bits(
            bus_id=bus_id,
            address=address,
            register=ACCEL_XOUT_H,
        )
        raw_acc_y = self._read_raw_bits(
            bus_id=bus_id,
            address=address,
            register=ACCEL_YOUT_H,
        )
        raw_acc_z = self._read_raw_bits(
            bus_id=bus_id,
            address=address,
            register=ACCEL_ZOUT_H,
        )
        
        # Get raw gyroscope bits
        raw_gyro_x = self._read_raw_bits(
            bus_id=bus_id,
            address=address,
            register=GYRO_XOUT_H,
        )
        raw_gyro_y = self._read_raw_bits(
            bus_id=bus_id,
            address=address,
            register=GYRO_YOUT_H,
        )
        raw_gyro_z = self._read_raw_bits(
            bus_id=bus_id,
            address=address,
            register=GYRO_ZOUT_H,
        )

        # Convert from bits to g's (accel.) and deg/s (gyro), then 
        # from those base units to m*s^-2 and rad/s respectively
        acc_x = (raw_acc_x / (2.0**15.0)) * accel_range * GRAV_ACC
        acc_y = (raw_acc_y / (2.0**15.0)) * accel_range * GRAV_ACC
        acc_z = (raw_acc_z / (2.0**15.0)) * accel_range * GRAV_ACC

        gyro_x = (raw_gyro_x / (2.0**15.0)) * gyro_range * DEG2RAD
        gyro_y = (raw_gyro_y / (2.0**15.0)) * gyro_range * DEG2RAD
        gyro_z = (raw_gyro_z / (2.0**15.0)) * gyro_range * DEG2RAD

        return acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z


    def get_AK8963_data(
        self,
        bus_id: int=1,
        address=AK8963_ADDR,
        mag_coeffs=[],
    ) -> tuple:
        """Convert raw binary magnetometer readings to floats.

        Args:
            bus_id (int): I2C bus on the device. Default: 1.
            address (hex): address of AK8963 sensor. Should always be default 
                            AK8963_ADDR value (defined outside function).
            mag_coeffs (list of floats): coefficients set from AK8963. Units are 
                                micro-T (uT).

        Returns:
            mag_x, mag_y, mag_z (floats): magnetometer values (in uT).
        """
        # Read raw magnetometer bits
        num_tries = 0
        try_lim = 500

        while num_tries < try_lim:
            raw_mag_x = self._read_raw_bits(bus_id=bus_id,
                                            address=address,
                                            register=HXH,
                                            )
            raw_mag_y = self._read_raw_bits(bus_id=bus_id,
                                            address=address,
                                            register=HYH,
                                            )
            raw_mag_z = self._read_raw_bits(bus_id=bus_id,
                                            address=address,
                                            register=HZH,
                                            )

            # the next line is needed for AK8963
            if (self.bus[bus_id].read_byte_data(address,AK8963_ST2)) & 0x08!=0x08:
                break

            num_tries += 1

        # Convert from bits to uT
        mag_x = (raw_mag_x/(2.0**15.0)) * mag_coeffs[0]
        mag_y = (raw_mag_y/(2.0**15.0)) * mag_coeffs[1]
        mag_z = (raw_mag_z/(2.0**15.0)) * mag_coeffs[2]
        
        return mag_x,mag_y,mag_z


    def _read_raw_bits(
        self,
        bus_id: int,
        address: hex,
        register: hex,
    ) -> int:
        """Method of reading raw data from different subcircuits 
        on the MPU9250 board.

        Args:
            bus_id (int): I2C bus on the device.
            address (hex): address of the subcircuit being read from.
            register (hex): register from which to pull specific data.

        Returns:
            value (int): raw value pulled from specific register and converted 
                        to int.
        """
        if address == MPU6050_ADDR or address == MPU6050_ADDR_AD0_HIGH:
            # Read accel and gyro values
            high = self.bus[bus_id].read_byte_data(address, register)
            low = self.bus[bus_id].read_byte_data(address, register+1)
        elif address == AK8963_ADDR:            
            # read magnetometer values
            high = self.bus[bus_id].read_byte_data(address, register)
            low = self.bus[bus_id].read_byte_data(address, register-1)

        # Combine high and low for unsigned bit value
        value = ((high << 8) | low)
        
        # Convert to +/- value
        if(value > 32768):
            value -= 65536

        return value


def exit_gracefully(self) -> None:
    """Exit MPU-9250 communication across all connected 
    I2C buses gracefully. Handle multithreading as present.

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
    # start I2C driver
    # bus = smbus.SMBus(7) # start comm with i2c bus
    # time.sleep(SLEEP_TIME)
    # gyro_sens,accel_sens = MPU6050_start() # instantiate gyro/accel
    # time.sleep(SLEEP_TIME)
    # # AK8963_coeffs = AK8963_start() # instantiate magnetometer
    # time.sleep(SLEEP_TIME)

    import platform
    machine_name = platform.uname().release.lower()
    if "tegra" in machine_name:
        # bus = [1,7]
        bus = [1,7]
    elif "rpi" in machine_name or "bcm" in machine_name or "raspi" in machine_name:
        bus = 1
    else:
        bus = 1

    loop = LoopTimer(operating_rate=200, verbose=True)

    # imu_ids = {0: 0x68, 1: 0x68, 2: 0x68, 3: 0x68, 4: 0x68, 5: 0x68}
    # imu_ids = {1: 0x68, 1: 0x69, 2: 0x68, 2: 0x69, 4: 0x68, 4: 0x69}
    # imu_ids = {
    #             bus[0]:
    #                 {
    #                     1: 0x68,
    #                     1: 0x69,
    #                 },
    #             bus[1]:
    #                 {
    #                     1: 0x68,
    #                     1: 0x69,
    #                 },
    #         }
    imu_ids = {
        0:
            {
                'bus': bus[0],
                'channel': 1,
                'address': 0x68,
            },
        1:
            {
                'bus': bus[0],
                'channel': 1,
                'address': 0x69,
            },
        2:
            {
                'bus': bus[1],
                'channel': 1,
                'address': 0x68,
            },
        3:
            {
                'bus': bus[1],
                'channel': 1,
                'address': 0x69,
            },
    }

    # imu_ids2 = {
    #     0:
    #         {
    #             'bus': bus[1],
    #             'channel': 1,
    #             'address': 0x68,
    #         },
    #     1:
    #         {
    #             'bus': bus[1],
    #             'channel': 1,
    #             'address': 0x69,
    #         },
    # }
    use_multiplexer = False
    components = ['acc','gyro']
    verbose = True

    # mpu9250_imus = MPU9250IMUs(
    #     bus=bus[0],
    #     imu_ids=imu_ids,
    #     use_multiplexer=use_multiplexer,
    #     components=components,
    #     verbose=verbose,
    # )

    # mpu9250_imus2 = MPU9250IMUs(
    #     bus=bus[1],
    #     imu_ids=imu_ids2,
    #     use_multiplexer=use_multiplexer,
    #     components=components,
    #     verbose=verbose,
    # )

    mpu9250_imus = MPU9250IMUs(
        bus=bus,
        imu_ids=imu_ids,
        use_multiplexer=use_multiplexer,
        components=components,
        verbose=verbose,
    )

    t_diff_array = [0] * 200
    t_old = time.perf_counter()
    t_new = time.perf_counter()

    while True:
        if loop.continue_loop():
            # t_new = time.perf_counter()
            # t_diff = t_new - t_old
            # t_diff_array.pop(0)
            # t_diff_array.append(t_diff)
            # mean_diff = sum(t_diff_array)/len(t_diff_array)

            imu_data0 = mpu9250_imus.get_data(imu_id=0)
            imu_data1 = mpu9250_imus.get_data(imu_id=1)
            # imu_data2 = mpu9250_imus2.get_data(imu_id=0)
            # imu_data3 = mpu9250_imus2.get_data(imu_id=1)

            
            # for imu_id in imu_ids.keys():
            #     imu_data = mpu9250_imus.get_data(imu_id=imu_id)
            
                # print(f"IMU {channel} [{1/t_diff:0.2f} Hz, mean: {1/mean_diff:0.2f} Hz]: acc_x: {imu_data.accx:0.3f}, acc_y: {imu_data.accy:0.3f}, acc_z: {imu_data.accz:0.3f}, gyro_x: {imu_data.gyrox:0.3f}, gyro_y: {imu_data.gyroy:0.3f}, gyro_z: {imu_data.gyroz:0.3f}")

            # t_old = t_new

    mpu9250_imus.exit_gracefully()