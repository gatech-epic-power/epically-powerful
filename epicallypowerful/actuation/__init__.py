# Import management for epicallypowerful actuation modules
import epicallypowerful.actuation.cubemars
import epicallypowerful.actuation.cybergear
import epicallypowerful.actuation.robstride
import epicallypowerful.actuation.actuator_group
import epicallypowerful.actuation.motor_data

from .actuator_group import ActuatorGroup
from .cubemars import CubeMars
from .cubemars import CubeMarsServo
from .cybergear import Cybergear
from .robstride import Robstride
from .motor_data import MotorData

def available_actuator_types():
    print("Available actuator types:")
    print(list(epicallypowerful.actuation.motor_data.MOTOR_PARAMS.keys()))
