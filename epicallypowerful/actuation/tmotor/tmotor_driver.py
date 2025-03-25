import can
import math
from epicallypowerful.actuation.motor_data import MotorData

# ~~~~ T Motor Constants ~~~~~ #
ENTER_MOTOR_MODE = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC]
EXIT_MOTOR_MODE = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD]
ZERO_MOTOR_POSITION = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE]


# ~~~~~ T Motor Utility and Driver Functions ~~~~~ #
def _uint_to_float(x: int, x_min: int, x_max: int, num_bits: int) -> float:
        """
        Interpolates an unsigned integer of num_bits length to a floating point number between  x_min and x_max.

        Args:
            x (int): The int number to convert
            x_min (int): The minimum value for the floating point number
            x_max (int): The maximum value for the floating point number
            num_bits (int): The number of bits for the unsigned integer

        Returns:
            float: The floating point representation of the unsigned integer
        """
        span = x_max-x_min
        return float(x*span/((1<<num_bits)-1) + x_min)

def _float_to_uint(x: float, x_min: int, x_max: int, num_bits: int) -> int:
        """
        Interpolates a floating point number to an unsigned integer of num_bits length.
        A number of x_max will be the largest integer of num_bits, and x_min would be 0.

        Args:
            x (float): The floating point number to convert
            x_min (float): The minimum value for the floating point number
            x_max (float): The maximum value for the floating point number
            num_bits (int): The number of bits for the unsigned integer

        Returns:
            int: The unsigned integer representation of the floating point number
        """
        span = x_max-x_min
        bitratio = float((1<<num_bits)/span)
        x = _clamp(x,x_min,x_max-(2/bitratio))
        return _clamp(int((x - x_min)*(bitratio)), 0, int((x_max-x_min)*bitratio))

def _clamp(value: float, min_val: float, max_val: float) -> float:
    """clamp a value between a min and max value

    Args:
        value (float): value to clamp
        min_val (float): min value to clamp to
        max_val (float): max value to clamp to

    Returns:
        float: clamped value
    """
    return min(max_val, max(min_val, value))

def _unpack_motor_message(msg: can.Message, motor) -> tuple[int, float, float, float]:
    """takes a can message type as a Motor dataclass defining current
        motor parameters, and unpacks the data to extract the current position,
        velocity, and torque

        Args:
            msg (can.Message): CAN message
            motor (Motor): current motor data state

        Returns:
            list: the appropriate motor ID, current position, velocity, and accleration
    """
    data = msg.data

    # Unpack
    motor_id = data[0]
    position_uint = data[1] <<8 | data[2]
    velocity_uint = ((data[3] << 8) | (data[4]>>4) <<4 ) >> 4
    torque_uint = (data[4]&0x0F)<<8 | data[5]

    pos = _uint_to_float(position_uint, motor.position_limits[0], motor.position_limits[1], 16)
    vel = _uint_to_float(velocity_uint, motor.velocity_limits[0], motor.velocity_limits[1], 12)
    torque = _uint_to_float(torque_uint, motor.torque_limits[0], motor.torque_limits[1], 12)
    return motor_id, pos, vel, torque

def _pack_motor_message(pos: float, vel: float, kp: float, kd: float, t: float, motor: MotorData, verbose=False) -> can.Message:
    """Packs the appropriate data fields into the expected CAN message
    data format.

    Args:
        pos (float): commanded position
        vel (float): commanded velocity
        kp (float): positional impedance parmeter (spring constant)
        kd (float): velocity impedance parameter (damping constant)
        t (float): commanded torque
        motor (MotorData): Motor dataclass describing the current motor state
        verbose (bool, optional): Decides if the message should be print to console during runtime. Defaults to False.

    Returns:
        can.Message: CAN message containing the appropriate data for the desired command.
    """
    position_uint16 = _float_to_uint(pos, motor.position_limits[0], motor.position_limits[1], 16)
    velocity_uint12 = _float_to_uint(vel, motor.velocity_limits[0], motor.velocity_limits[1], 12)
    kp_uint12 = _float_to_uint(kp, motor.kp_limits[0], motor.kp_limits[1], 12)
    kd_uint12 = _float_to_uint(kd, motor.kd_limits[0], motor.kd_limits[1], 12)
    t_uint12 = _float_to_uint(t, motor.torque_limits[0], motor.torque_limits[1], 12)

    data = [
        (position_uint16) >> 8,
        (position_uint16) & 0x00FF,
        (velocity_uint12) >> 4,
        ((velocity_uint12&0x00F)<<4) | (kp_uint12) >> 8,
        (kp_uint12&0x0FF),
        (kd_uint12) >> 4,
        ((kd_uint12&0x00F)<<4) | (t_uint12) >> 8,
        (t_uint12&0x0FF)
    ]
    if verbose: print(data)
    msg = can.Message(
        arbitration_id=motor.motor_id,
        data=data,
        is_extended_id=False
    )

    return msg

def _pack_zero_encoder_message(target_id: int) -> can.Message:
    """Packs the appropriate data fields into the expected CAN message
    data format to zero the encoder position.

    Args:
        target_id (int): The motor ID to zero the encoder position.

    Returns:
        can.Message: CAN message containing the appropriate data for the desired command.
    """
    return can.Message(arbitration_id=target_id, data=ZERO_MOTOR_POSITION, is_extended_id=False)

def _pack_enter_motor_message(target_id: int) -> can.Message:
    """Packs the appropriate data fields into the expected CAN message
    data format to enter motor mode.

    Args:
        target_id (int): The motor ID to enter motor mode.

    Returns:
        can.Message: CAN message containing the appropriate data for the desired command.
    """
    return can.Message(arbitration_id=target_id, data=ENTER_MOTOR_MODE, is_extended_id=False)

def _pack_exit_motor_message(target_id: int) -> can.Message:
    """Packs the appropriate data fields into the expected CAN message
    data format to exit motor mode.

    Args:
        target_id (int): The motor ID to exit motor mode.

    Returns:
        can.Message: CAN message containing the appropriate data for the desired command.
    """
    return can.Message(arbitration_id=target_id, data=EXIT_MOTOR_MODE, is_extended_id=False)
