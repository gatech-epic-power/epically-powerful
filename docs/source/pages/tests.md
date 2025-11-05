(Tests)=
# Tests

Here is the fun part.
There are three basic test scripts available to demonstrate motor functionality. They will allow for basic communication and data monitoring, continuous torque command, and use of the built in positional control. For all the example codes if it supports multiple motors, only use ONE type of motor.

## display_motor_data.py

This function will walk you through setting up and viewing data from multiple connected motors. This does not command any torque, so you should be able to test this safely with no output shaft connected to the motor. However as always, an E-Stop should be connected and users should be vigilant to ensure safety. This supports multiple motors.

## basic_continuous_torque.py

This function provides the same data as previously, except with the ability to command a continuous torque at the start of the program. Because this will apply torque until the program is ended, be sure to hold onto or secure the output shaft (both the body and the output shaft). Otherwise the motor will continuously spin. NOTE: torque values should be kept reasonable. Use 1Nm to start just to observe the behavior of the motor.

## basic_position_control.py

This function allows for a desired position, spring constant (Kp), and damping ratio (Kd) to be set at the start, which will be continuously applied. NOTE: Kp and Kd values should be kept reasonable and roughly at a ratio of 10:1. Start with Kp=1 and Kd=0.1 to observe the motor behavior.

## ./examples/
Here, we give an example of how you can use various functions in the software package to interface with your actuators.  The main functions that we anticipate people using regularly will be reading the actuator’s current position, velocity, and torque as well as setting the actuator’s torque (and possibly position or velocity, which we’ve included in the functionality).  The main commands that we anticipate you will need are below.

```
p = motor_group.get_position(motor_id=left_hip)
v = motor_group.get_velocity(motor_id=left_hip)
t = motor_group.get_torque(motor_id=left_hip)
t_desired = motor_group.set_torque(motor_id=left_hip, torque=desired_torque_value)
```

