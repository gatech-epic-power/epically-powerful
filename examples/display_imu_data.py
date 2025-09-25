#/usr/bin/env python3

"""
To Initialize the MicroStrain IMUs, you need to make a list of 
IMU serial IDs corresponding to all the IMUs you'd like to connect
to your system.

For the MPU9250 IMUs, you need to create a dictionary of each IMU
you're connecting containing its I2C bus, address, and channel if 
you're using a multiplexer to handle multiple units.

USER CONFIRMS CHANGES: IMU configuration and setup

"""

##################################################################
# SYSTEM IMPORTS
##################################################################

from epicallypowerful.toolbox import LoopTimer
from epicallypowerful.sensing import MicroStrainIMUs, MPU9250IMUs

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

LOOP_RATE = 200 # operation rate [Hz]
clocking_loop = LoopTimer(LOOP_RATE)

##################################################################
# MICROSTRAIN IMUS
##################################################################

# Set MicroStrain IMU IDs
# IMU_01 = str(input("Enter the last six digits of the plugged-in Microstrain IMU's serial number (e.g. 154136)"))
MICROSTRAIN_IMU_IDS = ['193821']

# Change IMU operation options (each one has a default)
MICROSTRAIN_IMU_RATE = LOOP_RATE # Set collection rate of IMUs
TARE_ON_STARTUP = False # Zero orientation on startup?

# Instantiate instance of MicroStrain IMU manager
# microstrain_imus = MicroStrainIMUs(
#     imu_ids=MICROSTRAIN_IMU_IDS,
#     rate=MICROSTRAIN_IMU_RATE,
#     tare_on_startup=TARE_ON_STARTUP,
#     verbose=False,
# )

##################################################################
# MICROSTRAIN IMUS
##################################################################

# Set MicroStrain IMU IDs
# IMU_01 = str(input("Enter the last six digits of the plugged-in Microstrain IMU's serial number (e.g. 154136): "))
MPU9250_IMU_IDS = {
    0: {
        'bus': 1,        # 7 is the default I2C bus on the Jetson
        'channel': -1,   # channel is only used with a multiplexer. If not using one, keep as -1
        'address': 0x69, # I2C address of the MPU9250. Can be either this or 0x68
    }
}

# Change IMU operation options (each one has a default)
COMPONENTS = ['acc', 'gyro'] # Which components to sample. Can be `acc`, `gyro`, or `mag`

# Instantiate instance of MPU9250 IMU manager
mpu9250_imus = MPU9250IMUs(
    imu_ids=MPU9250_IMU_IDS,
    components=COMPONENTS,
    verbose=False,
)

##################################################################
# MAIN CONTROLLER LOOP
##################################################################

# Continuously stream data
while True:
    if clocking_loop.continue_loop():
        # Iterate through all connected IMUs
        # for imu_id in MICROSTRAIN_IMU_IDS:
        #     # Orientation, angular velocity, linear acceleration
        #     # print(f'ID: {imu_id} | orient. (w,x,y,z): {imus.get_data(imu_id).orientw:.2f}, {imus.get_data(imu_id).orientx:.2f},{imus.get_data(imu_id).orienty:.2f},{imus.get_data(imu_id).orientz:.2f},\t | ang. vel. (r,p,y):  ({imus.get_data(imu_id).gyrox:.2f}, {imus.get_data(imu_id).gyroy:.2f}, {imus.get_data(imu_id).gyroz:.2f}),\t | lin. accel. (x,y,z): ({imus.get_data(imu_id).accx:.2f}, {imus.get_data(imu_id).accy:.2f}, {imus.get_data(imu_id).accz:.2f})')

        #     # Acceleration in x, y, z direction
        #     print(f"ID: {imu_id} | ({microstrain_imus.get_data(imu_id).accx:.2f}, {microstrain_imus.get_data(imu_id).accy:.2f}, {microstrain_imus.get_data(imu_id).accz:.2f})")

            # Gyroscopic angular velocity in x, y, z direction
            # print(f"ID: {imu_id}\t| ({microstrain_imus.get_data(imu_id).gyrox:.2f}, {microstrain_imus.get_data(imu_id).gyroy:.2f}, {microstrain_imus.get_data(imu_id).gyroz:.2f})")

            # Roll, pitch, yaw only
            # print(f"ID: {imu_id}\t| roll: {microstrain_imus.get_data(imu_id).roll:.2f},\t pitch: {microstrain_imus.get_data(imu_id).pitch:.2f},\t yaw: {microstrain_imus.get_data(imu_id).yaw:.2f}")

        for imu_id in MPU9250_IMU_IDS:
            imu_data = mpu9250_imus.get_data(imu_id)
            # Acceleration in x, y, z directions
            print(f"ID: 00000{imu_id} | ({imu_data.accx:.2f}, {imu_data.accy:.2f}, {imu_data.accz:.2f})")

            # Gyroscopic angular velocity in x, y, z directions
            # print(f"ID: 00000{imu_id}\t| roll: {imu_data.gyrox:.2f}, \t pitch: {imu_data.gyroy:.2f}, \t yaw: {imu_data.gyroz:.2f}")