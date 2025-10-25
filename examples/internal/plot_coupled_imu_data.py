#/usr/bin/env python3

"""
To Initialize the MicroStrain IMUs, you need to make a list of 
IMU serial IDs corresponding to all the IMUs you'd like to connect
to your system.

For the OpenIMUs, you need to make a list of the IMU CAN IDs 
corresponding to all the IMUs you'd like to connect to your system.

"""

##################################################################
# SYSTEM IMPORTS
##################################################################

import time
import numpy as np
from epicallypowerful.toolbox import LoopTimer
from epicallypowerful.sensing import MicroStrainIMUs, OpenIMUs
import matplotlib.pyplot as plt

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

LOOP_RATE = 100 # operation rate [Hz]
clocking_loop = LoopTimer(LOOP_RATE)

##################################################################
# MICROSTRAIN IMUS
##################################################################

# Set MicroStrain IMU IDs
# IMU_01 = str(input("Enter the last six digits of the plugged-in Microstrain IMU's serial number (e.g. 154136): "))
IMU_01 = '133931'
MICROSTRAIN_IMU_IDS = [IMU_01]

# Change IMU operation options (each one has a default)
MICROSTRAIN_IMU_RATE = 100 # Set collection rate of IMUs
TARE_ON_STARTUP = False # Zero orientation on startup?

# Instantiate instance of MicroStrain IMU manager
microstrain_imus = MicroStrainIMUs(
    imu_ids=MICROSTRAIN_IMU_IDS,
    rate=MICROSTRAIN_IMU_RATE,
    tare_on_startup=TARE_ON_STARTUP,
    verbose=False,
)

##################################################################
# OPENIMUS
##################################################################

# Set OpenIMU IDs
# OPEN_IMU_IDS = input("\nEnter the three-digit CAN ID of each OpenIMU(e.g. 132), separating multiple with commas: ")
OPEN_IMU_IDS = '142'
OPEN_IMU_IDS = [int(s) for s in OPEN_IMU_IDS.replace(" ", "").split(',')]

# Set IMU sampling rate. NOTE: this does not change the sampling 
# rate of the IMUs themselves, just the rate at which they return new data
OPEN_IMU_RATE = LOOP_RATE

# Set which channels to sample data from. NOTE: you will need to 
# have configured your OpenIMUs to stream each of the channels you 
# want! Otherwise, it just won't get sampled
COMPONENTS = ['acc', 'gyro'] # Possible options: `acc`, `gyro`, `mag`

# Instantiate instance of MicroStrain IMU manager
open_imus = OpenIMUs(
    imu_ids=OPEN_IMU_IDS,
    components=COMPONENTS,
    rate=OPEN_IMU_RATE,
    verbose=False,
)

##################################################################
# MAIN CONTROLLER LOOP
##################################################################

microstrain_data = []
microstrain_time = []
open_imu_data = []
open_imu_time = []

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

        # for imu_id in OPEN_IMU_IDS:
            # Acceleration in x, y, z directions
            # oi_data = open_imus.get_data(imu_id)
            # open_imu_time.append(oi_data.timestamp - t0)
            # open_imu_data.append([oi_data.acc_x, oi_data.acc_y, oi_data.acc_z])
            # print(f"ID: 00000{imu_id} | ({oi_data.acc_x:.2f}, {oi_data.acc_y:.2f}, {oi_data.acc_z:.2f})")

            # Gyroscopic angular velocity in x, y, z directions
            # oi_data = open_imus.get_data(imu_id)
            # open_imu_time.append(oi_data.timestamp - t0)
            # open_imu_data.append([oi_data.gyro_x, oi_data.gyro_y, oi_data.gyro_z])
            # print(f"ID: 00000{imu_id} | ({oi_data.gyro_x:.2f}, {oi_data.gyro_y:.2f}, {oi_data.gyro_z:.2f})")


        # SWAP AND NEGATE X & Y COORDINATES
        for imu_id in OPEN_IMU_IDS:
            # Acceleration in x, y, z directions
            # oi_data = open_imus.get_data(imu_id)
            # open_imu_time.append(oi_data.timestamp - t0)
            # open_imu_data.append([-oi_data.acc_y, -oi_data.acc_x, oi_data.acc_z])
            # print(f"ID: 00000{imu_id} | ({-oi_data.acc_y:.2f}, {-oi_data.acc_z:.2f}, {oi_data.acc_z:.2f})")

            # Gyroscopic angular velocity in x, y, z directions
            oi_data = open_imus.get_data(imu_id)
            open_imu_time.append(oi_data.timestamp - t0)
            open_imu_data.append([-oi_data.gyro_y, oi_data.gyro_x, -oi_data.gyro_z])
            print(f"ID: 00000{imu_id} | ({-oi_data.gyro_y:.2f}, {oi_data.gyro_x:.2f}, {-oi_data.gyro_z:.2f})")

##################################################################
# VISUALIZE OUTPUTS
##################################################################

# Plot outputs to compare MicroStrain and MPU-9250
axis_labels = ['x', 'y', 'z']
microstrain_time = np.array(microstrain_time)
open_imu_time = np.array(open_imu_time)
microstrain_data = np.array(microstrain_data)
open_imu_data = np.array(open_imu_data)

# plt.style.use('ggplot')
fig,axs = plt.subplots(3,1,figsize=(12,9))

for ii in range(0,len(axis_labels)):
    axs[ii].plot(
        microstrain_time,
        microstrain_data[:,ii],
        label='MicroStrain',
    )
    axs[ii].plot(
        open_imu_time,
        open_imu_data[:,ii],
        label=f'OpenIMU',
    )

    axs[ii].set_ylabel(f'${axis_labels[ii]}$',fontsize=12)
    axs[ii].set_ylim([
        min(
            microstrain_data.min(),
            open_imu_data.min(),
        ),
        max(
            microstrain_data.max(),
            open_imu_data.max(),
        ),
    ])

    if ii == 0:
        # axs[ii].set_title(
        #     'MicroStrain vs. OpenIMU Accelerometer Comparison',
        #     fontsize=14,
        # )
        axs[ii].set_title(
            'MicroStrain vs. OpenIMU Gyroscope Comparison',
            fontsize=14,
        )
    elif ii == len(axis_labels)-1:
        axs[ii].set_xlabel('time [s]',fontsize=12)
        axs[ii].legend(fontsize=12)

    fig.savefig(
        'microstrain_vs_open_imu_comparison.png',
        dpi=300,
        bbox_inches='tight',
        # facecolor='#FCFCFC',
    )

fig.show()