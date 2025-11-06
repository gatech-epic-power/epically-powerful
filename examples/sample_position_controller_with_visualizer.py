#/usr/bin/env python3
"""
This script will run the actuator output shaft position through 
a sinusoidal pattern using a PD controller.
"""
import sys
import time
import math
from epicallypowerful.actuation import ActuatorGroup
from epicallypowerful.toolbox import TimedLoop
from epicallypowerful.toolbox.visualization import PlotJugglerUDPClient


##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

# Set control loop frequency
OPERATING_FREQ = 200 # [Hz]
clocking_loop = TimedLoop(rate=OPERATING_FREQ)

##################################################################
# INITIALIZE ACTUATOR
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
# INITIALIZE VISUALIZER
##################################################################

PORT = 5556
udp_server_ip_address = input(
    "\nSpecify IP address of the computer on your network running PlotJuggler (e.g. 192.168.0.227): "
)

print(f"\nPublishing viz. messages on UDP server with IP address {udp_server_ip_address} on port {PORT}")

# Initialize visualizer instance
pj_client = PlotJugglerUDPClient(addr=udp_server_ip_address, port=PORT)
viz_data = {
    'data': {
        'actuator_id': actuator_id,
        'position_desired': 0,
        'position_actual': 0,
        'error': 0,
        'error_dot': 0,
        'torque_desired': 0,
        'actuator_position': 0,
        'actuator_velocity': 0,
        'actuator_torque': 0,
    },
    'timestamp': time.time(),
}
pj_client.send(viz_data)

##################################################################
# SET CONTROLLER PARAMETERS
##################################################################

GAIN_KP = 5 # proportional gain
GAIN_KD = 0.25 # derivative gain
rad_range = 3.14159 # Angular peak-to-peak sine wave range (rad) that controller will sweep
error_current = 0 # initialize, will change in loop
prev_error = 0 # initialize, will change in loop
t0 = time.time()

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
    act_data = acts.get_data(actuator_id)

    # Update desired position
    time_since_start = time.time() - t0
    position_desired = math.sin(time_since_start) * (rad_range / 2)
    
    # Update position error
    position_current = acts.get_position(can_id=actuator_id, degrees=False)
    prev_error = error_current
    error_current = position_desired - position_current
    errordot_current = (error_current - prev_error) / (1 / OPERATING_FREQ)

    # Update torques
    torque_desired = GAIN_KP*error_current + GAIN_KD*errordot_current
    acts.set_torque(can_id=actuator_id, torque=torque_desired)

    print(f'| {int(actuator_id):^5} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')

    # Send outputs for visualization
    viz_data = {
        'data': {
            'actuator_id': actuator_id,
            'position_desired': position_desired,
            'position_actual': position_current,
            'error': error_current,
            'error_dot': errordot_current,
            'torque_desired': torque_desired,
            'actuator_position': act_data.current_position,
            'actuator_velocity': act_data.current_velocity,
            'actuator_torque': act_data.current_torque,
        },
        'timestamp': time.time(),
    }
    pj_client.send(viz_data)



