(DisplayMicroStrainData)=
# Display MicroStrain IMU Data
This example will stream data from a specific MicroStrainIMU to the terminal, displaying the accelerometer data in the x, y, and z directions. In this examples, you can see how to initialize a MicroStrain IMU and read data from it in a loop.

## Demo Video
::::{youtube} eSRS-K47a7s
::::


## Code
```python
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
from epicallypowerful.sensing import MicroStrainIMUs

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

OPERATING_FREQ = 200 # operation frequency [Hz]
clocking_loop = TimedLoop(OPERATING_FREQ)

##################################################################
# SET UP MICROSTRAIN IMUS
##################################################################

# Set MicroStrain IMU IDs
microstrain_imu_ids = input("\nEnter the last six digits of each MicroStrain IMU's serial number (e.g. 154136), separating multiple with commas: ")
microstrain_imu_ids = [str(s) for s in microstrain_imu_ids.replace(" ", "").split(',')]

# Change IMU operation options (each one has a default)
MICROSTRAIN_IMU_FREQ = OPERATING_FREQ # Set collection rate of IMUs
TARE_ON_STARTUP = False # Zero orientation on startup?

# Instantiate instance of MicroStrain IMU manager
microstrain_imus = MicroStrainIMUs(
    imu_ids=microstrain_imu_ids,
    rate=MICROSTRAIN_IMU_FREQ,
    tare_on_startup=TARE_ON_STARTUP,
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
    for imu_id in microstrain_imu_ids:
        # Acceleration in x, y, z direction
        ms_data = microstrain_imus.get_data(imu_id)
        print(f"| {int(imu_id):^9} | {ms_data.acc_x:^15.2f} | {ms_data.acc_y:^15.2f} | {ms_data.acc_z:^15.2f} |")
```
::::{button-link} https://github.com/gatech-epic-power/epically-powerful/blob/main/examples/display_microstrain_imu_data.py
    :expand:
    :color: primary
    :shadow:
    **Code is available here**
::::