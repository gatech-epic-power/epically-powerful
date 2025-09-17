"""epically-powerful module for managing IMUs.

This module contains functions for calibrating the 
accelerometer, gyroscope, and magnetometer of the MPU9250 IMUs. 
Methodology for these steps is adapted from Joshua Hrisko's work on 

"""

import os
import sys
import time
import platform
import argparse
from typing import Dict
import numpy as np
import smbus2 as smbus # I2C bus library on Raspberry Pi and NVIDIA Jetson Orin Nano
from epicallypowerful.toolbox import LoopTimer
from epicallypowerful.sensing.mpu9250.mpu9250_imu import MPU9250IMUs


# Get default I2C bus depending on which device is currently being used
machine_name = platform.uname().release.lower()

if "tegra" in machine_name:
    DEFAULT_I2C_BUS = 7
elif "rpi" in machine_name or "bcm" in machine_name or "raspi" in machine_name:
    DEFAULT_I2C_BUS = 1
else:
    DEFAULT_I2C_BUS = 0


def calibrate_accelerometer(
    imu_handler: MPU9250IMUs,
    loop_timer: LoopTimer,
    time_to_calibrate: float=2.5,
    write_to_file: bool=True,
    verbose: bool=False,
) -> tuple[float]:
    
    return accel_coeffs


def calibrate_gyroscope(
    imu_handler: MPU9250IMUs,
    loop_timer: LoopTimer,
    time_to_calibrate: float=2.5,
    write_to_file: bool=True,
    verbose: bool=False,
) -> tuple[float]:
    input("Press [ENTER] to calibrate gyroscope. Keep IMU still...")
    gyro_data = []
    t_start = time.perf_counter()

    while time.perf_counter() - t_start <= time_to_calibrate:
        if loop_timer.continue_loop():
            imu_data = imu_handler.get_data(imu_id=0)
            gyro_data.append([imu_data.gyrox, imu_data.gyroy, imu_data.gyroz])

    if verbose:
        print(f"gyro_data size for calibration: {len(gyro_data)} samples")

    gyro_coeffs = np.mean(np.array(gyro_data), 0).tolist()

    if verbose:
        print(f"Calibration complete! gyro_coeffs: ({gyro_coeffs[0]:0.2f}, {gyro_coeffs[1]:0.2f}, {gyro_coeffs[2]:0.2f})")

    return gyro_coeffs


def calibrate_magnetometer(
    imu_handler: MPU9250IMUs,
    loop_timer: LoopTimer,
    time_to_calibrate: float=2.5,
    write_to_file: bool=True,
    verbose: bool=False,
) -> tuple[float]:

    return mag_coeffs


# def store_coefficients() -> None:


def split_strings(arg):
    return arg.split(",")


# Create argument parser
parser = argparse.ArgumentParser(
    description="Calibrate MPU9250 IMU."
)

parser.add_argument(
    "--components",
    type=split_strings,
    default=["acc", "gyro", "mag"],
    help="Which channels to calibrate on the sensor, comma-separated without spaces (e.g., --components acc,gyro)",
)

parser.add_argument(
    "--i2c_bus",
    type=int,
    default=DEFAULT_I2C_BUS,
    help="Which I2C bus the sensor is on (e.g., --i2c_bus 7). Defaults to 7 for NVIDIA Jetson Orin Nano or 1 for Raspberry Pi",
)

parser.add_argument(
    "--channel",
    type=int,
    default=-1,
    help="(If using multiplexer) channel sensor is on (e.g., --channel 1). Defaults to -1 (no multiplexer)",
)

parser.add_argument(
    "--address",
    type=int,
    default=68,
    help="I2C address of MPU9250 sensor (e.g., --address 68). Defaults to 68",
)

parser.add_argument(
    "--rate",
    type=float,
    default=250,
    help="Frequency of MPU9250 sensor [Hz] (e.g., --rate 250). Defaults to 250 Hz",
)


if __name__ == "__main__":
    args = parser.parse_args()
    bus = args.i2c_bus
    channel = args.channel
    address = args.address

    print(f"Initializing MPU9250 IMU at I2C bus {bus} on channel {channel} with address {address}")

    imu_id = {
        0:
            {
                'bus': bus,
                'channel': channel,
                'address': 0x69,
            },
    }

    mpu9250_imus = MPU9250IMUs(
        imu_ids=imu_id,
        components=args.components,
        verbose=True,
    )

    for component in args.components:
        if component == "acc":
            accel_coeffs = calibrate_accelerometer(
                imu_handler=mpu9250_imus,
                loop_timer=LoopTimer(operating_rate=args.rate, verbose=True),
                time_to_calibrate=2.5,
                write_to_file=True,
                verbose=True,
            )

        elif component == "gyro":
            gyro_coeffs = calibrate_gyroscope(
                imu_handler=mpu9250_imus,
                loop_timer=LoopTimer(operating_rate=args.rate, verbose=True),
                time_to_calibrate=2.5,
                write_to_file=True,
                verbose=True,
            )

        elif component == "mag":
            mag_coeffs = calibrate_magnetometer(
                imu_handler=mpu9250_imus,
                loop_timer=LoopTimer(operating_rate=args.rate, verbose=True),
                time_to_calibrate=2.5,
                write_to_file=True,
                verbose=True,
            )




