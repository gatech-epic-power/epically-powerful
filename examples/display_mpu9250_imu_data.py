#/usr/bin/env python3

"""
To Initialize the MPU9250 IMUs, you need to create a dictionary of 
each IMU you're connecting containing its I2C bus, address, and 
channel if you're using a multiplexer to handle multiple units.
"""

##################################################################
# SYSTEM IMPORTS
##################################################################

import time
import numpy as np
from epicallypowerful.toolbox import TimedLoop
from epicallypowerful.sensing import MPU9250IMUs

print("\nIn the script, you will need to specify the I2C bus, multiplexer channel \n(if used), and I2C address for each IMU.\n")

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

OPERATING_FREQ = 200 # operation frequency [Hz]
clocking_loop = TimedLoop(OPERATING_FREQ)

##################################################################
# SET UP MPU9250 IMUS
##################################################################

# Set MPU9250 IMU IDs
MPU9250_IMU_IDS = {
    0: {
        'bus': 1,        # 7 is the default I2C bus on the Jetson
        'channel': -1,   # channel is only used with a multiplexer. If not using one, keep as -1 (default)
        'address': 0x68, # I2C address of the MPU9250. Can be either 0x68 or 0x69
    }
}

# Change IMU operation options (each one has a default)
COMPONENTS = ['acc', 'gyro'] # Which components to sample. Can be `acc`, `gyro`, or `mag`

# Instantiate instance of MPU9250 IMU manager
mpu9250_imus = MPU9250IMUs(
    imu_ids=MPU9250_IMU_IDS,
    components=COMPONENTS,
    calibration_path='../epicallypowerful/sensing/mpu9250/mpu9250_calibrations.json', # Should exist for all actual use cases
    verbose=True,
)

##################################################################
# MAIN LOOP
##################################################################

print("\n")

# Continuously stream data
while clocking_loop():
    print('\033[A\033[A\033[A')
    print(f'| I2C bus | channel | I2C addr. | Acc. (x) m*s^-2 | Acc. (y) m*s^-2 | Acc. (z) m*s^-2 |')

    # Iterate through all connected IMUs
    for imu_id, connection in MPU9250_IMU_IDS.items():
        # Acceleration in x, y, z directions
        mpu_data = mpu9250_imus.get_data(imu_id)
        print(f'| {int(connection['bus']):^7} | {int(connection['channel']):^7} | {int(connection['address']):^9} | {mpu_data.acc_x:^15.2f} | {mpu_data.acc_y:^15.2f} | {mpu_data.acc_z:^15.2f} |')