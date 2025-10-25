#/usr/bin/env python3

"""
To Initialize the MicroStrain IMUs, you need to make a list of 
IMU serial IDs corresponding to all the IMUs you'd like to connect
to your system.
"""

##################################################################
# SYSTEM IMPORTS
##################################################################

import time
import numpy as np
from epicallypowerful.toolbox import TimedLoop
from epicallypowerful.sensing import OpenIMUs

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

OPERATING_FREQ = 100 # operation frequency [Hz]
clocking_loop = TimedLoop(OPERATING_FREQ)

##################################################################
# SET UP OPENIMUS
##################################################################

# Set OpenIMU IDs
open_imu_ids = input("\nEnter the three-digit CAN ID of each OpenIMU(e.g. 132), separating multiple with commas: ")
open_imu_ids = [int(s) for s in open_imu_ids.replace(" ", "").split(',')]

# Set IMU sampling rate. NOTE: this does not change the sampling 
# rate of the IMUs themselves, just the rate at which they return new data
IMU_RATE = OPERATING_FREQ

# Set which channels to sample data from. NOTE: you will need to 
# have configured your OpenIMUs to stream each of the channels you 
# want! Otherwise, it just won't get sampled
COMPONENTS = ['acc', 'gyro'] # Possible options: `acc`, `gyro`, `mag`

# Instantiate instance of MicroStrain IMU manager
open_imus = OpenIMUs(
    imu_ids=open_imu_ids,
    components=COMPONENTS,
    rate=IMU_RATE,
    verbose=False,
)

##################################################################
# MAIN LOOP
##################################################################

print("\n")

# Continuously stream data
while clocking_loop():
    print('\033[A\033[A\033[A')
    print(f'| IMU addr. | Acc. (x) m*s^-2 | Acc. (y) m*s^-2 | Acc. (z) m*s^-2 |')

    # Iterate through all connected IMUs
    for imu_id in open_imu_ids:
        # Acceleration in x, y, z direction
        oi_data = open_imus.get_data(imu_id)
        print(f"| {int(imu_id):^9} | {oi_data.acc_x:^15.2f} | {oi_data.acc_y:^15.2f} | {oi_data.acc_z:^15.2f} |")
