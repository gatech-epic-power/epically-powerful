from epicallypowerful.actuation.cubemars.cubemars_v3 import CubeMarsV3
from epicallypowerful.actuation.actuator_group import ActuatorGroup
import numpy as np
import time
ACT_ID = 1
#acts = ActuatorGroup([Cybergear(2)])
acts = ActuatorGroup([CubeMarsV3(ACT_ID, 'AK80-9-V3')])

t0 = time.perf_counter()
cmds = []
measured = []
while True:
    #acts.set_position(ACT_ID, 0, 2, 0.1)
    #acts.set_velocity(ACT_ID, 3, 2) 
    acts.set_torque(ACT_ID, 2)
    print(f'{acts.get_position(ACT_ID):.2f}, {acts.get_velocity(ACT_ID):.2f}, {acts.get_torque(ACT_ID):.2f}')
    if time.perf_counter() - t0 > 10:
        break
    time.sleep(0.01)
print("Stopping")
acts.set_torque(ACT_ID, 0)
print("Done")
