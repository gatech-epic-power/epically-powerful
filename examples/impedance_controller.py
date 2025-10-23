#/usr/bin/env python3
"""
This script will run the actuator output shaft position through 
a sinusoidal pattern using a PD controller.
"""

from epicallypowerful.actuation import ActuatorGroup
from epicallypowerful.toolbox import TimedLoop


##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

# Set control loop frequency
OPERATING_FREQ = 200 # [Hz]
clocking_loop = TimedLoop(rate=OPERATING_FREQ)

##################################################################
# INITIALIZE DEVICES & VISUALIZER
##################################################################

# Determine number of connected actuators. This assumes a uniform actuator type (i.e. all are AK80-9)
actuator_type = input(
    "\nSpecify actuator type (see actuation.motor_data for possible types): "
)

# Get actuator IDs
actuator_id = input("Specify actuator id: ")
actuator_id = int(actuator_id)
initialization_dict = {actuator_id:actuator_type}

# Initialize actuator object from dictionary
acts = ActuatorGroup.from_dict(initialization_dict)

##################################################################
# SET CONTROLLER PARAMETERS (PLAY AROUND WITH THESE!)
##################################################################

GAIN_KP = 2 # proportional gain
GAIN_KD = 0.1 # derivative gain
error_current = 0 # initialize, will change in loop
prev_error = 0 # initialize, will change in loop
position_desired = 0 # [rad]

##################################################################
# MAIN OPERATING LOOP
##################################################################

# Zero actuator encoder
acts.zero_encoder(actuator_id)

# Run control loop at set frequency
while clocking_loop():
    print('\033[A\033[A\033[A')
    print(f'| Actuator | Position [rad] | Velocity [rad/s] | Torque [Nm] |')

    # Get data from actuator
    act_data = acts.get_data(ACT_ID)

    # Update position error
    position_current = acts.get_position(can_id=ACT_ID, degrees=False)
    prev_error = error_current
    error_current = position_desired - position_current
    errordot_right = (error_current - prev_error) / (1 / OPERATING_FREQ)

    # Update torques
    torque_desired = GAIN_KP*error_current + GAIN_KD*errordot_right
    acts.set_torque(can_id=ACT_ID, torque=torque_desired)

    print(f'| {int(ACT_ID):^5} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')




