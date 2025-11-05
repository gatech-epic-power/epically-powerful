
from epicallypowerful.actuation.robstride import Robstride

class CyberGear(Robstride):
    """Class for controlling an individual CyberGear Micromotor. This class should always be initialized as part of an ActuatorGroup so that the can bus is appropriately shared between all motors.
    Alternatively, the bus can be set manually after initialization, however this is not recommended.

    **NOTE: The CyberGear class is simply an inherited version of the Robstride class, which automatically passes the `motor_type` argument as "CyberGear". In general, this is provided as a convenience function and will potentially be deprecated to ensure consistency between the CyberGear and other Robstride motors.
    The CyberGears can be initialized to be inverted by default, which will reverse the default Clockwise/Counter-Clockwise direction of the motor.


    Example:
        .. code-block:: python


            from epicpower.actuation2 import CyberGear, ActuatorGroup

            motor = Cybergear(0x01)
            group = ActuatorGroup([motor])

            motor.set_torque(0.5)
            # OR
            group[0x01].set_torque(0.5)
            # OR
            group.set_torque(0x01, 0.5)

    Args:
        can_id (int): CAN ID of the motor. This should be unique for each motor in the system, and can be set up with the RLink software.
        motor_type (str, optional): A string representing the type of motor. This is not necessary as there is only one type of motor. Defaults to "CyberGear".
        invert (bool, optional): Whether to invert the motor direction. Defaults to False.
    """
    def __init__(self, can_id: int, motor_type: str="CyberGear", invert: bool=False):
        super().__init__(can_id, motor_type, invert)
