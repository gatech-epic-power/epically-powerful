#############################################################
# SYSTEM IMPORTS
#############################################################

from epicallypowerful import actuation, toolbox

#############################################################
# MOTORS
#############################################################

""" 
To initiate the motors, you need to make a motor list that contains two types of 
information - (1) the CAN ID of the actuator and (2) the actuator type.  This 
list can be any length to incorporate any number of actuators you want in your
configuration.  You need to ensure that your CAN IDs are properly set up via the
R-Link UART interface prior to running this script.

USER CHANGES: Alter the below CAN IDs and motor types to match your desired test
set up.
"""

# DEFINE DESIRED MOTORS
left_hip = 1
right_hip = 2
actuator_type = 'AK80-9'
motor_list_to_init = {left_hip:actuator_type, right_hip:actuator_type} # We wont actually use the right hip in this example


# INITIALIZE MOTOR GROUP
motor_group = actuation.ActuatorGroup.from_dict(motor_list_to_init)

#############################################################
# SET UP CLOCK SPECIFICATIONS
#############################################################

operating_rate = 200 # This is main loop operation rate in Hz
clocking_loop = toolbox.LoopTimer(operating_rate, verbose=True)

#############################################################
# MAIN CONTROLLER LOOP
#############################################################

# Initiate your main while loop - this can be ended using Ctrl-C or using a key press
while True:
	if clocking_loop.continue_loop():
		"""IMPEDANCE CONTROLLER IMPLEMENTATION
		Note that position control is available to run a stiffness controller by default.
		In this instance, we write out the calculations for a impedance (spring/damper)
		controller for the purposes of demonstrating how to both read data from the 
		actuator and command torques to the actuator.
		"""
		constant_stiffness = 1
		constant_damping = 0.1
		position_desired = 0

		current_pos = motor_group.get_position(left_hip)
		current_vel = motor_group.get_velocity(left_hip)

		impedance_torque = (position_desired-current_pos)*constant_stiffness - current_vel*constant_damping

		motor_group.set_torque(left_hip, impedance_torque)
		print('\033[A\033[A\033[A')
		print(f'| Motor | Position (rad) | Velocity (rad/s) | Torque (Nm) |')
		print(f'| {left_hip:^5.2f} | {current_pos:^14.2f} | {current_vel:^16.2f} | {impedance_torque:^11.2f} |')

motor_group.cleanup()
