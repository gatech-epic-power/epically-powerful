(ImpedanceControl)=
# Impedance Control

```python
# IMPORTS
from epicallypowerful import actuation, toolbox

# MOTOR SETUP
right_hip = 0x1
left_hip = 0x2
actuator_type = 'AK80-9'
actuator_dict_to_init = {left_hip:actuator_type, right_hip:actuator_type}
actuator_group = actuation.ActuatorGroup.from_dict(actuator_dict_to_init)

# CLOCKING
operating_rate = 200
clocking_loop = toolbox.TimedLoop(operating_rate)

# IMPEDANCE PARAMETERS
stiffness = 1
damping = 0.1
position_des = 0

# MAIN LOOP
while clocking_loop.continue_loop():

    # UPDATE TORQUES - LEFT
    position_curr_L = actuator_group.get_position(can_id=left_hip)
    velocity_curr_L = actuator_group.get_velocity(can_id=left_hip)
    impedance_torque_L = (position_des-position_curr_L)*stiffness + velocity_curr_L*damping
    actuator_group.set_torque(can_id=left_hip, torque=impedance_torque_L)

    # UPDATE TORQUES - RIGHT
    position_curr_R = actuator_group.get_position(can_id=right_hip)
    velocity_curr_R = actuator_group.get_velocity(can_id=right_hip)
    impedance_torque_R = (position_des-position_curr_R)*stiffness + velocity_curr_R*damping
    actuator_group.set_torque(can_id=right_hip, torque=impedance_torque_R)

actuator_group.cleanup()
```