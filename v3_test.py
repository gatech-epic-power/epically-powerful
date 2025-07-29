from epicallypowerful.actuation.tmotor.tmotor_v3 import TmotorV3
from epicallypowerful.actuation import ActuatorGroup
import time


ID = 1 # Make this whatever you need

cmd_torque = 0.0 # Nm
cmd_position = 0.0 # rad
cmd_velocity = 0.0 # rad/s
cmd_kp = 0.0 # Nms/rad
cmd_kd = 0.0 # Nms/rad/s

acts = ActuatorGroup( TmotorV3(ID, "AK80-9-V3") )

acts.enable()

while True:
    acts.set_torque(ID, cmd_torque)
    # acts.set_position(ID, cmd_position, cmd_kp, cmd_kd)
    # acts.set_velocity(ID, cmd_velocity)
    time.sleep(1)
    print(f'{acts.get_torque(ID)} Nm, {acts.get_position(ID)} rad, {acts.get_velocity(ID)} rad/s, {acts.get_temperature(ID)} C')