#/usr/bin/env python3
"""
This script will match the actuator output shaft position to 
a MicroStrain IMU's Euler angle (x) using a PD controller.
"""

from epicallypowerful.actuation import ActuatorGroup
from epicallypowerful.actuation.tmotor import TMotor
from epicallypowerful.toolbox import TimedLoop
from epicallypowerful.sensing import MicroStrainIMUs


##################################################################
# SET CLOCK SPECIFICATIONS
##################################################################

# Set control loop frequency
OPERATING_FREQ = 200 # [Hz]
clocking_loop = TimedLoop(rate=OPERATING_FREQ)

##################################################################
# SET UP MICROSTRAIN IMUS
##################################################################

# Set MicroStrain IMU IDs
microstrain_imu_id = input(
    "\nEnter the last six digits of the MicroStrain IMU's serial number (e.g. 154136): "
)
microstrain_imu_id = [str(microstrain_imu_id)]

# Change IMU operation options (each one has a default)
MICROSTRAIN_IMU_FREQ = OPERATING_FREQ # Set collection rate of IMUs
TARE_ON_STARTUP = False # Zero orientation on startup?

# Instantiate instance of MicroStrain IMU manager
microstrain_imus = MicroStrainIMUs(
    imu_ids=microstrain_imu_id,
    rate=MICROSTRAIN_IMU_FREQ,
    tare_on_startup=TARE_ON_STARTUP,
    verbose=False,
)

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
actuators = ActuatorGroup.from_dict(initialization_dict)

##################################################################
# SET CONTROLLER PARAMETERS (PLAY AROUND WITH THESE!)
##################################################################

GAIN_KP = 0.25 # proportional gain
GAIN_KD = 0.01 # derivative gain
gyro_current = 0 # initialize, will change in loop
prev_error = 0 # initialize, will change in loop

##################################################################
# MAIN OPERATING LOOP
##################################################################

# Zero actuator encoder
actuators.zero_encoder(actuator_id)
print("\n")

# Run control loop at set frequency
while clocking_loop():
    print('\033[A\033[A\033[A')
    print(f'| Actuator | Torque [Nm] | IMU Addr. | Gyro (x) [rad/s] |')

    # Get data from actuator
    act_data = actuators.get_data(actuator_id)

    # Get MicroStrain IMU gyroscope values
    imu_data = microstrain_imus.get_data(microstrain_imu_id[0])
    prev_error = gyro_current
    gyro_current = imu_data.gyro_x
    gyrodot_current = (gyro_current - prev_error) / (1 / OPERATING_FREQ)

    # Update torques
    torque_desired = GAIN_KP*gyro_current + GAIN_KD*gyrodot_current
    actuators.set_torque(can_id=actuator_id, torque=torque_desired)

    # Print out updated results
    print(f'| {int(actuator_id):^8} | {act_data.current_torque:^11.2f} | {microstrain_imu_id[0]:^9} | {imu_data.gyro_x:^16.2f} |')