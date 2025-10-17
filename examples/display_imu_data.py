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

import time
import numpy as np
from epicallypowerful.toolbox import LoopTimer
from epicallypowerful.sensing import MicroStrainIMUs, MPU9250IMUs
import matplotlib.pyplot as plt

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

LOOP_RATE = 200 # operation rate [Hz]
clocking_loop = LoopTimer(LOOP_RATE)

##################################################################
# MICROSTRAIN IMUS
##################################################################

# Set MicroStrain IMU IDs
IMU_01 = str(input("Enter the last six digits of the plugged-in Microstrain IMU's serial number (e.g. 154136)"))
# IMU_01 = '133932'
MICROSTRAIN_IMU_IDS = [IMU_01]

# Change IMU operation options (each one has a default)
MICROSTRAIN_IMU_RATE = LOOP_RATE # Set collection rate of IMUs
TARE_ON_STARTUP = False # Zero orientation on startup?

# Instantiate instance of MicroStrain IMU manager
microstrain_imus = MicroStrainIMUs(
    imu_ids=MICROSTRAIN_IMU_IDS,
    rate=MICROSTRAIN_IMU_RATE,
    tare_on_startup=TARE_ON_STARTUP,
    verbose=False,
)

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
    calibration_path='../epicallypowerful/sensing/mpu9250/mpu9250_calibrations.json', # Should exist for all actual use cases
    verbose=True,
)

##################################################################
# MAIN CONTROLLER LOOP
##################################################################

microstrain_data = []
microstrain_time = []
mpu9250_data = []
mpu9250_time = []

TEST_DURATION = 5 # [s]
t0 = time.perf_counter()

# Continuously stream data
while time.perf_counter() - t0 <= TEST_DURATION:
    if clocking_loop.continue_loop():
        # Iterate through all connected IMUs
        for imu_id in MICROSTRAIN_IMU_IDS:
            # Orientation, angular velocity, linear acceleration
            # print(f'ID: {imu_id} | quat. (w,x,y,z): {imus.get_data(imu_id).quat_w:.2f}, {imus.get_data(imu_id).quat_x:.2f},{imus.get_data(imu_id).quat_y:.2f},{imus.get_data(imu_id).quat_z:.2f},\t | ang. vel. (x,y,z):  ({imus.get_data(imu_id).gyro_x:.2f}, {imus.get_data(imu_id).gyro_y:.2f}, {imus.get_data(imu_id).gyro_z:.2f}),\t | lin. accel. (x,y,z): ({imus.get_data(imu_id).acc_x:.2f}, {imus.get_data(imu_id).acc_y:.2f}, {imus.get_data(imu_id).acc_z:.2f})')

            # Acceleration in x, y, z direction
            # ms_data = microstrain_imus.get_data(imu_id)
            # microstrain_time.append(ms_data.timestamp - t0)
            # microstrain_data.append([ms_data.acc_x, ms_data.acc_y, ms_data.acc_z])
            # print(f"ID: {imu_id} | ({ms_data.acc_x:.2f}, {ms_data.acc_y:.2f}, {ms_data.acc_z:.2f})")

            # Gyroscopic angular velocity in x, y, z direction
            ms_data = microstrain_imus.get_data(imu_id)
            microstrain_time.append(ms_data.timestamp - t0)
            microstrain_data.append([ms_data.gyro_x, ms_data.gyro_y, ms_data.gyro_z])
            print(f"ID: {imu_id} | ({ms_data.gyro_x:.2f}, {ms_data.gyro_y:.2f}, {ms_data.gyro_z:.2f})")

            # Roll, eul_y, eul_z only
            # print(f"ID: {imu_id}\t| eul_x: {microstrain_imus.get_data(imu_id).eul_x:.2f},\t eul_y: {microstrain_imus.get_data(imu_id).eul_y:.2f},\t eul_z: {microstrain_imus.get_data(imu_id).eul_z:.2f}")

        for imu_id in MPU9250_IMU_IDS:
            # Acceleration in x, y, z directions
            # mpu_data = mpu9250_imus.get_data(imu_id)
            # mpu9250_time.append(mpu_data.timestamp - t0)
            # mpu9250_data.append([mpu_data.acc_x, mpu_data.acc_y, mpu_data.acc_z])
            # print(f"ID: 00000{imu_id} | ({mpu_data.acc_x:.2f}, {mpu_data.acc_y:.2f}, {mpu_data.acc_z:.2f})")

            # Gyroscopic angular velocity in x, y, z directions
            mpu_data = mpu9250_imus.get_data(imu_id)
            mpu9250_time.append(mpu_data.timestamp - t0)
            mpu9250_data.append([mpu_data.gyro_x, mpu_data.gyro_y, mpu_data.gyro_z])
            print(f"ID: 00000{imu_id} | ({mpu_data.gyro_x:.2f}, {mpu_data.gyro_y:.2f}, {mpu_data.gyro_z:.2f})")

##################################################################
# VISUALIZE OUTPUTS
##################################################################

# Plot outputs to compare MicroStrain and MPU-9250
axis_labels = ['x', 'y', 'z']
microstrain_time = np.array(microstrain_time)
mpu9250_time = np.array(mpu9250_time)
microstrain_data = np.array(microstrain_data)
mpu9250_data = np.array(mpu9250_data)

# TROUBLESHOOTING
# print(f"{microstrain_time.shape}, {mpu9250_time.shape}, {microstrain_data.shape}, {mpu9250_data.shape}")

# plt.style.use('ggplot')
fig,axs = plt.subplots(3,1,figsize=(12,9))

for ii in range(0,len(axis_labels)):
    axs[ii].plot(
        microstrain_time,
        microstrain_data[:,ii],
        label='MicroStrain',
    )
    axs[ii].plot(
        mpu9250_time,
        mpu9250_data[:,ii],
        label=f'MPU9250',
    )

    axs[ii].set_ylabel(f'${axis_labels[ii]}$',fontsize=12)
    axs[ii].set_ylim([
        min(
            microstrain_data.min(),
            mpu9250_data.min(),
        ),
        max(
            microstrain_data.max(),
            mpu9250_data.max(),
        ),
    ])

    if ii == 0:
        # axs[ii].set_title(
        #     'MicroStrain vs. MPU-9250 Accelerometer Comparison',
        #     fontsize=14,
        # )
        axs[ii].set_title(
            'MicroStrain vs. MPU-9250 Gyroscope Comparison',
            fontsize=14,
        )
    elif ii == len(axis_labels)-1:
        axs[ii].set_xlabel('time [s]',fontsize=12)
        axs[ii].legend(fontsize=12)

    fig.savefig(
        'microstrain_vs_mpu9250_comparison.png',
        dpi=300,
        bbox_inches='tight',
        # facecolor='#FCFCFC',
    )

fig.show()