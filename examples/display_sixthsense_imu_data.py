#!/usr/bin/env python3

"""
To Initialize the SixthSense IMUs, you need to make a list of 
CAN base IDs corresponding to all the IMUs you'd like to connect
to your system.
"""

##################################################################
# SYSTEM IMPORTS
##################################################################

import sys
import time
import numpy as np
from epicallypowerful.toolbox import TimedLoop
from epicallypowerful.sensing import SixthSenseIMUs

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

OPERATING_FREQ = 200  # operation frequency [Hz]
clocking_loop = TimedLoop(OPERATING_FREQ)

##################################################################
# SET UP SIXTHSENSE IMUS
##################################################################

# Set SixthSense IMU IDs (CAN base IDs)
sixthsense_imu_ids = input(
    "\nEnter the CAN base IDs of each SixthSense IMU (e.g. 100, 110), separating multiple with commas: "
)
sixthsense_imu_ids = [int(s) for s in sixthsense_imu_ids.replace(" ", "").split(",")]  #

# Instantiate instance of SixthSense IMU manager
sixthsense_imus = SixthSenseIMUs(
    imu_ids=sixthsense_imu_ids,
    port=None,
    timeout=0.0,
    verbose=False,
)

##################################################################
# MAIN LOOP
##################################################################

PRINT_EVERY = 8  # 200 Hz / 8 = 25 Hz terminal refresh
num_lines = len(sixthsense_imu_ids) + 1  # 1 header + 1 row per IMU
sys.stdout.write("\n" * num_lines)
sys.stdout.flush()

tick = 0
try:
    # Continuously stream data
    while clocking_loop():
        # Read all IMUs at full 200 Hz
        samples = [(imu_id, sixthsense_imus.get_data(imu_id)) for imu_id in sixthsense_imu_ids]

        # Render to terminal at 25 Hz
        tick += 1
        if tick >= PRINT_EVERY:
            tick = 0
            output = [
                f"\r\033[{num_lines}A\033[J"
                "| IMU addr. | Connected | SoC (%) | Acc. (x) m*s^-2 | Acc. (y) m*s^-2 | Acc. (z) m*s^-2 |"
            ]

            for imu_id, ss_data in samples:
                conn_str = "YES" if ss_data.connected else "NO"
                output.append(
                    f"| {imu_id:^9} | {conn_str:^9} | {ss_data.soc:^7} | "
                    f"{ss_data.acc_x:^15.2f} | {ss_data.acc_y:^15.2f} | {ss_data.acc_z:^15.2f} |"
                )

            sys.stdout.write("\n".join(output) + "\n")
            sys.stdout.flush()
except KeyboardInterrupt:
    print("\nStopping stream...")
finally:
    sixthsense_imus.close()