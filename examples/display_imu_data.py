#/usr/bin/env python3

"""
To initiate the Microstrain IMUs, you need to make a list of 
IMU serial IDs corresponding to all the IMUs you'd like to connect
to your system.

USER CHANGES:
- Set IMU IDs (the last 6 digits of the number found on the 
  front of the IMU)
"""

##################################################################
# SYSTEM IMPORTS
##################################################################

from epicallypowerful.toolbox import LoopTimer
from epicallypowerful.sensing import MicrostrainImus as IMUs

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

RATE = 200 # operation rate [Hz]
clocking_loop = LoopTimer(RATE)

##################################################################
# IMUS
##################################################################

# Set IMU IDs
IMU_01 = str(input("Enter the last six digits of the plugged-in Microstrain IMU's serial number (e.g. 154136): "))
# IMU_01 = "154136"
IMU_IDS = [IMU_01]

# Change IMU operation options (each one has a default)
IMU_RATE = RATE # Set collection rate of IMUs
TARE_ON_STARTUP = False # Tare on startup?

# Instantiate instance of Microstrain IMU manager
imus = IMUs(imu_ids=IMU_IDS,
            rate=IMU_RATE,
            tare_on_startup=TARE_ON_STARTUP,
            verbose=False)

##################################################################
# MAIN CONTROLLER LOOP
##################################################################

# Continuously stream data
while True:
    if clocking_loop.continue_loop():
        # Iterate through all connected IMUs
        for imu_id in IMU_IDS:
          # Orientation, angular velocity, linear acceleration
          # print(f'ID: {imu_id} | orient. (w,x,y,z): {imus.get_data(imu_id).orientw:.2f}, {imus.get_data(imu_id).orientx:.2f},{imus.get_data(imu_id).orienty:.2f},{imus.get_data(imu_id).orientz:.2f},\t | ang. vel. (r,p,y):  ({imus.get_data(imu_id).roll:.2f}, {imus.get_data(imu_id).pitch:.2f}, {imus.get_data(imu_id).yaw:.2f}),\t | lin. accel. (x,y,z): ({imus.get_data(imu_id).accx:.2f}, {imus.get_data(imu_id).accy:.2f}, {imus.get_data(imu_id).accz:.2f})')

          # Roll, pitch, yaw only
          print(f'ID: {imu_id} | roll: {imus.get_data(imu_id).roll:.2f},\t pitch: {imus.get_data(imu_id).pitch:.2f},\t yaw: {imus.get_data(imu_id).yaw:.2f}')