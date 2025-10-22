import os
from epicallypowerful import actuation, utils

print('epicallypowerful version 0.1.0: Basic Motor Connection Demo')
print("BASIC MOTOR CONNECTION DEMO")

print(
"""
This script gives a quick test of the motor connection as well as a way
to easily view the raw incoming data. By default, this script runs at 
200Hz, but feel free to edit this file/make a copy to change this value. 
Data will be presented in the units of radians, with the default CCW as 
positive convention. Additionally, it is assumed that all motors are of 
the same type for this script (not necessary for typical use).
"""
)

# Determine number of connected motors. This assumes a uniform motor type (i.e. all are AK80-9).
motor_type = input(
    "\nWhich motor type: AK80-9, AK70-10, AK80-8, AK10-9, AK80-64?"
)
motor_type = 'AK10-9-V2.0'

motor_ids = input("What are all the motor ids (seperate each by a comma)? ")
motor_ids = [int(s) for s in motor_ids.replace(" ","").split(',')]
initialization_dict = {motor_id:motor_type for motor_id in motor_ids}



clocker = utils.clocking.LoopTimer(200)
motors = actuation.ActuatorGroup.from_dict(initialization_dict)

while True:
    if clocker.continue_loop():
        all_data = {}
        print('\033[A\033[A\033[A')
        print(f'| Motor | Position (rad) | Velocity (rad/s) | Torque (Nm) |')
        for id in motor_ids:
            motors.set_torque(id, 0)
            all_data = motors.get_data(id)
            print(f'| {id:^5.2f} | {all_data.current_position:^14.2f} | {all_data.current_velocity:^16.2f} | {all_data.current_torque:^11.2f} |')
            