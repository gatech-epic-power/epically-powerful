#/usr/bin/env python3

"""
To Initialize the actuators, you need to make a dictionary of all 
actuator types and their CAN IDs corresponding to all the actuators
you'd like to connect to your system.
"""

##################################################################
# SYSTEM IMPORTS
##################################################################

from epicallypowerful.actuation import ActuatorGroup
from epicallypowerful.toolbox import TimedLoop


print('epicallypowerful: Basic Motor Connection Demo')
print(
"""
This script gives a quick test of the actuator connection as well as a way
to easily view the raw incoming data. By default, this script runs at 
200 Hz, but feel free to edit this file/make a copy to change this value. 
Angles will be presented in radians and torques will be presented in Nm, 
with the default CCW as positive convention. Additionally, it is assumed 
that all actuators are of the same type for this script (not necessary 
for typical use).
"""
)

##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

# Set control loop frequency
OPERATING_FREQ = 200 # [Hz]
clocking_loop = TimedLoop(rate=OPERATING_FREQ)

##################################################################
# SET ACTUATORS VIA TYPES AND IDS
##################################################################

# Determine number of connected actuators. This assumes a uniform actuator type (i.e. all are AK80-9)
actuator_type = input(
    "\nSpecify actuator type (see actuation.motor_data for possible types): "
)

# Get actuator IDs
actuator_ids = input("Specify actuator ids (separate multiple with commas): ")
actuator_ids = [int(s) for s in actuator_ids.replace(" ","").split(',')]
initialization_dict = {actuator_id:actuator_type for actuator_id in actuator_ids}

# Initialize actuator object from dictionary
actuators = ActuatorGroup.from_dict(initialization_dict)

##################################################################
# MAIN LOOP
##################################################################

# Run actuators at specified rate
while clocking_loop():
    print('\033[A\033[A\033[A')
    print(f'| Actuator | Position [rad] | Velocity [rad/s] | Torque [Nm] |')

    # Loop through all actuators and get position, velocity, torque
    for can_id in actuator_ids:
        actuators.set_torque(can_id, 0)
        act_data = actuators.get_data(can_id)
        print(f'| {int(can_id):^8} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')