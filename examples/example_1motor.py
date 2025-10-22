# EXAMPLE CONTROLLER SCRIPT
#   This script will run the actuator output shaft position through a sinusoidal pattern
#   using a PD controller

from epicallypowerful.actuation import ActuatorGroup
from epicallypowerful.actuation.tmotor import TMotor
from epicallypowerful.sensing import MicroStrainIMUs
from epicallypowerful.toolbox import TimedLoop, LoopTimer, PlotJugglerUDPClient

import time # only necessary for sine position control implementation
import math # only necessary for sine position control implementation

# DEFINE DEVICE IDS + OTHER PARAMETERS ---------------------------------------------------
OPERATING_FREQ = 200 # Hz
ACT_RIGHT = 0x1 # CAN ID
ACT_LEFT = 0x2 

# INITIALIZE DEVICES + CLOCKS + VISUALIZER -----------------------------------------------
# acts = ActuatorGroup.from_dict({ACT_RIGHT:'AK80-9'})
# acts = ActuatorGroup.from_dict({ACT_RIGHT:'AK10-9-V2.0'})
acts = ActuatorGroup([TMotor(ACT_RIGHT, 'AK80-9'), TMotor(ACT_LEFT, 'AK80-9')])
# acts = ActuatorGroup([TMotor(ACT_RIGHT, 'AK10-9-V2.0')])
timed_loop = TimedLoop(rate=OPERATING_FREQ)
# timed_loop = LoopTimer(operating_rate=OPERATING_FREQ, verbose=True)

# CONTROLLER PARAMETERS ------------------------------------------------------------------
GAIN_KP = 0.3 # proportional gain
GAIN_KD = 0.01 # derivative gain
degree_range = 20 # degrees, peak to peak distance that controller will sweep
error_right = 0 # initialize, will change in loop
errorprev_right = 0 # initialize, will change in loop
t0 = time.time()

# MAIN OPERATING LOOP --------------------------------------------------------------------
acts.zero_encoder(ACT_RIGHT)
while timed_loop(): # controls loop to run at set frequency
    # acts.set_torque(can_id=ACT_RIGHT, torque=0)
    # acts[ACT_RIGHT].set_torque(0)

    # GET DATA FROM DEVICES --------------------------------------------------------------
    act_right_data = acts.get_data(ACT_RIGHT)
    act_left_data = acts.get_data(ACT_LEFT)
    # POSITION CONTROLLER ----------------------------------------------------------------
    # Update desired position
    time_since_start = time.time()-t0
    # position_desired = math.sin(time_since_start)*degree_range/2
    position_desired = 0
    # Update errors
    position_right = acts.get_position(can_id=ACT_RIGHT, degrees=False) # radians by default
    errorprev_right = error_right
    error_right = position_desired-position_right
    errordot_right = (error_right-errorprev_right)/(1/OPERATING_FREQ)

    # Update torques
    torque_right = GAIN_KP*error_right # - GAIN_KD*errordot_right
    # torque_right = 0
    acts.set_torque(can_id=ACT_RIGHT, torque=0)
    acts.set_torque(can_id=ACT_LEFT,  torque=0)
    print(f"p right: {act_right_data.current_position}, p left: {act_left_data.current_position}")
    




