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
TMOTOR_V3 = 'TMotorV3'
CUBEMARS = 'CubeMars'
ROBSTRIDE = 'Robstride'
AK80_9 = 'AK80-9'
AK80_8 = 'AK80-8'
AK80_6 = 'AK80-6'
AK80_64 = 'AK80-64'
AK70_10 = 'AK70-10'
AK10_9_V2_0 = 'AK10-9-V2.0'


MOTOR_PARAMS = {
    'AKE80-8-V3': {
        'position_limits': (-12.56, 12.56),
        'velocity_limits': (-20.0, 20.0),
        'torque_limits': (-35.0, 35.0),
        'rated_torque_limits': (-12.0, 12.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 14,
        'gear_ratio': 8,
        'super_type': 'CubeMars'
    },
    'AKE60-8-V3': {
        'position_limits': (-12.56, 12.56),
        'velocity_limits': (-40.0, 40.0),
        'torque_limits': (-15.0, 15.0),
        'rated_torque_limits': (-5.0, 5.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 14,
        'gear_ratio': 8,
        'super_type': 'CubeMars'
    },
    'AK80-9-V3': {
        'position_limits': (-12.56, 12.56),
        'velocity_limits': (-65.0, 65.0),
        'torque_limits': (-18.0, 18.0),
        'rated_torque_limits': (-9.0, 9.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'CubeMars'
    },
    'AK70-9-V3': {
        'position_limits': (-12.56, 12.56),
        'velocity_limits': (-30.0, 30.0),
        'torque_limits': (-32.0, 32.0),
        'rated_torque_limits': (-8.5, 8.5),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'CubeMars'
    },
    'AK60-6-V3': {
        'position_limits': (-12.56, 12.56),
        'velocity_limits': (-60.0, 60.0),
        'torque_limits': (-12.0, 12.0),
        'rated_torque_limits': (-3.0, 3.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'CubeMars'
    },
    'AK10-9-V3': {
        'position_limits': (-12.56, 12.56),
        'velocity_limits': (-28.0, 28.0),
        'torque_limits': (-54.0, 54.0),
        'rated_torque_limits': (-18.0, 18.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'super_type': 'CubeMars'
    },
    'AK10-9-V2.0': { # 24V/48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-48.0, 48.0),
        'rated_torque_limits': (-18.0, 18.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 21,
        'gear_ratio': 9,
        'super_type': 'CubeMars',
    },
    'AK60-6-V1.1': { # 24V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-9.0, 9.0),
        'rated_torque_limits': (-3.0, 3.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 14,
        'gear_ratio': 6,
        'super_type': 'CubeMars',
    },
    'AK70-10': { # 24V/48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-24.8, 24.8),
        'rated_torque_limits': (-10.0, 10.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 21,
        'gear_ratio': 10,
        'super_type': 'CubeMars',
    },
    'AK80-6': { # 48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-12.0, 12.0),
        'rated_torque_limits': (-6.0, 6.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 21,
        'gear_ratio': 6,
        'super_type': 'CubeMars',
    },
    'AK80-8': { # 48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-25.0, 25.0),
        'rated_torque_limits': (-10.0, 10.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 21,
        'gear_ratio': 8,
        'super_type': 'CubeMars',
    },
    'AK80-9': { # 48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-18.0, 18.0),
        'rated_torque_limits': (-9.0, 9.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 21,
        'gear_ratio': 9,
        'super_type': 'CubeMars',
    },
    'AK80-64': { # 24V/48V operation
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-120.0, 120.0),
        'rated_torque_limits': (-48.0, 48.0),
        'kp_limits': (0.0, 500.0),
        'kd_limits': (0.0, 5.0),
        'pole_pairs': 21,
        'gear_ratio': 64,
        'super_type': 'CubeMars',
    },
    'CyberGear': {
        'position_limits': (-12.5, 12.5),
        'velocity_limits': (-30.0, 30.0),
        'torque_limits': (-12.0, 12.0),
        'rated_torque_limits': (-4.0, 4.0),
        'kp_limits': (0, 500.0),
        'kd_limits': (0, 5.0),
        'super_type': 'Robstride',
    },
    'RS00': {
        'position_limits': (-12.566, 12.566),
        'velocity_limits': (-33.0, 33.0),
        'torque_limits': (-14.0, 14.0),
        'rated_torque_limits': (-5.0, 5.0),
        'kp_limits': (0, 500.0),
        'kd_limits': (0, 5.0),
        'super_type': 'Robstride'

    },
    'RS01': {
        'position_limits': (-12.7, 12.7),
        'velocity_limits': (-44.0, 44.0),
        'torque_limits': (-17.0, 17.0),
        'rated_torque_limits': (-6.0, 6.0),
        'kp_limits': (0, 500.0),
        'kd_limits': (0, 5.0),
        'super_type': 'Robstride'
    },
    'RS02': {
        'position_limits': (-12.7, 12.7),
        'velocity_limits': (-44.0, 44.0),
        'torque_limits': (-17.0, 17.0),
        'rated_torque_limits': (-6.0, 6.0),
        'kp_limits': (0, 500.0),
        'kd_limits': (0, 5.0),
        'super_type': 'Robstride'
    },
    'RS03': {
        'position_limits': (-12.7, 12.7),
        'velocity_limits': (-20.0, 20.0),
        'torque_limits': (-60.0, 60.0),
        'rated_torque_limits': (-20.0, 20.0),
        'kp_limits': (0, 5000.0),
        'kd_limits': (0, 100.0),
        'super_type': 'Robstride'
    },
    'RS04': {
        'position_limits': (-12.7, 12.7),
        'velocity_limits': (-15.0, 15.0),
        'torque_limits': (-120.0, 120.0),
        'rated_torque_limits': (-40.0, 40.0),
        'kp_limits': (0, 5000.0),
        'kd_limits': (0, 100.0),
        'super_type': 'Robstride'
    },
    'RS05': {
        'position_limits': (-12.7, 12.7),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-5.5, 5.5),
        'rated_torque_limits': (-1.6, 1.6),
        'kp_limits': (0, 500.0),
        'kd_limits': (0, 5.0),
        'super_type': 'Robstride'
    },
    'RS06': {
        'position_limits': (-12.7, 12.7),
        'velocity_limits': (-50.0, 50.0),
        'torque_limits': (-36.0, 36.0),
        'rated_torque_limits': (-11.0, 11.0),
        'kp_limits': (0, 5000.0),
        'kd_limits': (0, 100.0),
        'super_type': 'Robstride'
    }
}

def get_motor_details(motor_type):
    if motor_type not in MOTOR_PARAMS.keys():
        raise ValueError(f'{motor_type} is not a valid motor type, must be one of {list(MOTOR_PARAMS.keys())}')
    return MOTOR_PARAMS[motor_type]

def cubemars():
    return [motor_key for motor_key in MOTOR_PARAMS.keys() if MOTOR_PARAMS[motor_key]['super_type'] == 'CubeMars']

def cybergears():
    return [motor_key for motor_key in MOTOR_PARAMS.keys() if MOTOR_PARAMS[motor_key]['super_type'] == 'Robstride']
    
def robstrides():
    return [motor_key for motor_key in MOTOR_PARAMS.keys() if MOTOR_PARAMS[motor_key]['super_type'] == 'Robstride']

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
    responding: bool = False
    unique_hardware_id: int = -1
    running_torque: list = None
    rms_torque: float = 0
    rms_time_prev: float = 0
    motor_mode: float = 0
    internal_params = {}
    erpm_to_rpm: float = None

    def __post_init__(self):
        """Initializes the motor limits based on the motor type

        Raises:
            ValueError: Raised if the motor type is not specified
        """
        if self.motor_type is None:
            raise ValueError('motor_type must be specified')
        details = get_motor_details(self.motor_type)
        self.position_limits = details.get('position_limits')
        self.velocity_limits = details.get('velocity_limits')
        self.torque_limits = details.get('torque_limits')
        self.kp_limits = details.get('kp_limits')
        self.kd_limits = details.get('kd_limits')
        self.rated_torque_limits = details.get('rated_torque_limits')
        if details.get('pole_pairs', None) is None or details.get('gear_ratio', None) is None:
            self.erpm_to_rpm = 1
        else:
            self.erpm_to_rpm = (1 / details.get('pole_pairs')) * (1 / details.get('gear_ratio'))
