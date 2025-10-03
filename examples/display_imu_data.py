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
# IMU_01 = str(input("Enter the last six digits of the plugged-in Microstrain IMU's serial number (e.g. 154136)"))
MICROSTRAIN_IMU_IDS = ['133932']

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
            # print(f'ID: {imu_id} | orient. (w,x,y,z): {imus.get_data(imu_id).orientw:.2f}, {imus.get_data(imu_id).orientx:.2f},{imus.get_data(imu_id).orienty:.2f},{imus.get_data(imu_id).orientz:.2f},\t | ang. vel. (r,p,y):  ({imus.get_data(imu_id).gyrox:.2f}, {imus.get_data(imu_id).gyroy:.2f}, {imus.get_data(imu_id).gyroz:.2f}),\t | lin. accel. (x,y,z): ({imus.get_data(imu_id).accx:.2f}, {imus.get_data(imu_id).accy:.2f}, {imus.get_data(imu_id).accz:.2f})')

            # Acceleration in x, y, z direction
            # ms_data = microstrain_imus.get_data(imu_id)
            # microstrain_time.append(ms_data.timestamp - t0)
            # microstrain_data.append([ms_data.accx, ms_data.accy, ms_data.accz])
            # print(f"ID: {imu_id} | ({ms_data.accx:.2f}, {ms_data.accy:.2f}, {ms_data.accz:.2f})")

            # Gyroscopic angular velocity in x, y, z direction
            ms_data = microstrain_imus.get_data(imu_id)
            microstrain_time.append(ms_data.timestamp - t0)
            microstrain_data.append([ms_data.gyrox, ms_data.gyroy, ms_data.gyroz])
            print(f"ID: {imu_id} | ({ms_data.gyrox:.2f}, {ms_data.gyroy:.2f}, {ms_data.gyroz:.2f})")

            # Roll, pitch, yaw only
            # print(f"ID: {imu_id}\t| roll: {microstrain_imus.get_data(imu_id).roll:.2f},\t pitch: {microstrain_imus.get_data(imu_id).pitch:.2f},\t yaw: {microstrain_imus.get_data(imu_id).yaw:.2f}")

        for imu_id in MPU9250_IMU_IDS:
            # Acceleration in x, y, z directions
            # mpu_data = mpu9250_imus.get_data(imu_id)
            # mpu9250_time.append(mpu_data.timestamp - t0)
            # mpu9250_data.append([mpu_data.accx, mpu_data.accy, mpu_data.accz])
            # print(f"ID: 00000{imu_id} | ({mpu_data.accx:.2f}, {mpu_data.accy:.2f}, {mpu_data.accz:.2f})")

            # Gyroscopic angular velocity in x, y, z directions
            mpu_data = mpu9250_imus.get_data(imu_id)
            mpu9250_time.append(mpu_data.timestamp - t0)
            mpu9250_data.append([mpu_data.gyrox, mpu_data.gyroy, mpu_data.gyroz])
            print(f"ID: 00000{imu_id} | ({mpu_data.gyrox:.2f}, {mpu_data.gyroy:.2f}, {mpu_data.gyroz:.2f})")

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