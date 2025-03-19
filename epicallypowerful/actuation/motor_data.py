from dataclasses import dataclass

"""This list of parameters was last updated on: 26 February 2024
Sites from which information was sourced:
- TMotor AK page: https://store.tmotor.com/categorys/robot-dynamics
- CubeMars AK page: https://www.cubemars.com/category-122-AK+Series+Robotic+Actuation+Module.html

Units of below limits:
- Position [rad]
- Velocity [rad/s]
- Torque [Nm]
"""

TMOTOR = 'TMotor'
CUBEMARS = 'CubeMars'
AK80_9 = 'AK80-9'
AK80_8 = 'AK80-8'
AK80_6 = 'AK80-6'
AK80_64 = 'AK80-64'
AK70_10 = 'AK70-10'
AK10_9_V2_0 = 'AK10-9-V2.0'


MOTOR_PARAMS = { # Listed with increasing
    'AK10-9-V2.0': { # 24V/48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-48.0, 48.0),
        'rated_torque_limits': (-18.0, 18.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'AK60-6-V1.1': { # 24V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-9.0, 9.0),
        'rated_torque_limits': (-3.0, 3.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'AK70-10': { # 24V/48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-24.8, 24.8),
        'rated_torque_limits': (-10.0, 10.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'AK80-6': { # 48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-12.0, 12.0),
        'rated_torque_limits': (-6.0, 6.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'AK80-8': { # 48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-25.0, 25.0),
        'rated_torque_limits': (-10.0, 10.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'AK80-9': { # 48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-18.0, 18.0),
        'rated_torque_limits': (-9.0, 9.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'AK80-64': { # 24V/48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-120.0, 120.0),
        'rated_torque_limits': (-48.0, 48.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'TMotor'
    },
    'CyberGear': {
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-30.0, 30.0),
        'torque_limits': (-12.0, 12.0),
        'rated_torque_limits': (-4.0, 4.0),
        'kp_limits': (0, 500.0),
        'kd_limits': (0, 5.0),
        'super_type': 'CyberGear'
    }
}

def get_motor_limits(motor_type):
    if motor_type not in MOTOR_PARAMS.keys():
        raise ValueError(f'{motor_type} is not a valid motor type, must be one of {list(MOTOR_PARAMS.keys())}')
    return MOTOR_PARAMS[motor_type].values()


def t_motors():
    return [motor_key for motor_key in MOTOR_PARAMS.keys() if MOTOR_PARAMS[motor_key]['super_type'] == 'TMotor']

def cybergears():
    return [motor_key for motor_key in MOTOR_PARAMS.keys() if MOTOR_PARAMS[motor_key]['super_type'] == 'CyberGear']

@dataclass
class MotorData:
    """Stores the most recent state of the current motor. This data is typically updated by a CAN Listener class.

    This contains the parameters relevant for control, (i.e. commanded and current position, velocity, torque, etc.), as well as the motor limits.
    The same data structure is used for all motors, but the limits are specific to the motor type. Additionally, some fields are not used for all motor types, and thus
    it is advised to use the getter methods for each motor instead of the dataclass directly.
    """
    motor_id: int
    motor_type: str
    current_position: float = 0.0
    current_velocity: float = 0.0
    current_torque: float = 0.0
    current_temperature: float = 0.0
    commanded_position: float = 0
    commanded_velocity: float = 0
    commanded_torque: float = 0
    kp: float = 0
    kd: float = 0
    torque_limits: tuple = (0,0)
    rated_torque_limits: tuple = (0,0)
    velocity_limits: tuple = (0,0)
    position_limits: tuple = (0,0)
    kp_limits: tuple = (0,0)
    kd_limits: tuple = (0,0)
    timestamp: float = -1
    last_command_time: float = -1
    initialized: bool = False
    unique_hardware_id: int = -1
    running_torque: list = None
    rms_torque: float = 0
    rms_time_prev: float = 0
    motor_mode: float = 0
    internal_params = {}

    def __post_init__(self):
        """Initializes the motor limits based on the motor type

        Raises:
            ValueError: Raised if the motor type is not specified
        """
        if self.motor_type is None:
            raise ValueError('motor_type must be specified')
        self.position_limits, self.velocity_limits, self.torque_limits, self.rated_torque_limits, self.kp_limits, self.kd_limits, _ = get_motor_limits(self.motor_type)