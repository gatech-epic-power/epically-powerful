import can

MASTER_CAN_ID = 0

CMD_GET_DEVICE_ID = 0
CMD_SET_MOTION = 1
CMD_ENABLE_MOTION = 3
CMD_DISABLE_MOTION = 4
CMD_SET_ZERO = 6
CMD_CHANGE_DEVICE_ID = 7
CMD_READ_PARAM = 17
CMD_WRITE_PARAM = 18


RESPONSE_MOTION = 2
RESPONSE_IDENTITY = 0
RESPONSE_IDENTITY_CHECK_FLAG = 0xFE
RESPONSE_FAULT = 21
RESPONSE_PARAM = 17

# Motion response motor mode options
MODE_STATUS_RESET = 0
MODE_STATUS_CALIBRATE = 1
MODE_STATUS_RUN = 2

MOTOR_MODE_OPERATION = 0
MOTOR_MODE_POSITION = 1
MOTOR_MODE_VELOCITY = 2
MOTOR_MODE_CURRENT = 3

T_MIN = {'Cybergear': -12.0, 'RS02': -17.0}
T_MAX = {'Cybergear': 12.0, 'RS02': 17.0}
P_MIN = {'Cybergear': -12.5, 'RS02': -12.5}
P_MAX = {'Cybergear': 12.5, 'RS02': 12.5}
V_MIN = {'Cybergear': -30.0, 'RS02': -44.0}
V_MAX = {'Cybergear': 30.0, 'RS02': 44.0}
KP_MIN = 0
KP_MAX = 500
KD_MIN = 0
KD_MAX = 5
N_BITS = 16

# --- Parameter Indices ---
# CUR - Current loop related value
# TRQ - Torque related value
IDX_RUN = 0x7005
IDX_IQ_REF = 0x7006
IDX_SPD_REF = 0x700A
IDX_TRQ_LIM = 0x700B
IDX_CUR_KP = 0x7010
IDX_CUR_KI = 0x7011
IDX_CUR_FILT_GAIN = 0x7014
IDX_LOC_REF = 0x7016
IDX_SPD_LIM = 0x7017
IDX_CUR_LIM = 0x7018
IDX_MECH_POS = 0x7019
IDX_IQ_FILT_VAL = 0x701A # also references a 'f' in documentation
IDX_MECH_VEL = 0x701B
IDX_BUS_VOLT = 0x701C
IDX_NUM_ROTS = 0x701D
IDX_LOC_KP = 0x701E
IDX_SPD_KP = 0x701F
IDX_SPD_KI = 0x7020

VALID_PARAMS = {
    IDX_RUN,
    IDX_IQ_REF,
    IDX_SPD_REF,
    IDX_TRQ_LIM,
    IDX_CUR_KP,
    IDX_CUR_KI,
    IDX_CUR_FILT_GAIN,
    IDX_LOC_REF,
    IDX_SPD_LIM,
    IDX_CUR_LIM,
    IDX_MECH_POS,
    IDX_IQ_FILT_VAL,
    IDX_MECH_VEL,
    IDX_BUS_VOLT,
    IDX_NUM_ROTS,
    IDX_LOC_KP,
    IDX_SPD_KP,
    IDX_SPD_KI
}

PARAM_NUM_BYTES = {
    IDX_RUN:1,
    IDX_IQ_REF:4,
    IDX_SPD_REF:4,
    IDX_TRQ_LIM:4,
    IDX_CUR_KP:4,
    IDX_CUR_KI:4,
    IDX_CUR_FILT_GAIN:4,
    IDX_LOC_REF:4,
    IDX_SPD_LIM:4,
    IDX_CUR_LIM:4,
    IDX_MECH_POS:4,
    IDX_IQ_FILT_VAL:4,
    IDX_MECH_VEL:4,
    IDX_BUS_VOLT:4,
    IDX_NUM_ROTS:2,
    IDX_LOC_KP:4,
    IDX_SPD_KP:4,
    IDX_SPD_KI:4
}

PARAM_READ_WRITE_STATUS = { # r indicates READ only, w indicates both READ and WRITE, there are no write only
    IDX_RUN:'w',
    IDX_IQ_REF:'w',
    IDX_SPD_REF:'w',
    IDX_TRQ_LIM:'w',
    IDX_CUR_KP:'w',
    IDX_CUR_KI:'w',
    IDX_CUR_FILT_GAIN:'w',
    IDX_LOC_REF:'w',
    IDX_SPD_LIM:'w',
    IDX_CUR_LIM:'w',
    IDX_MECH_POS:'r',
    IDX_IQ_FILT_VAL:'r',
    IDX_MECH_VEL:'r',
    IDX_BUS_VOLT:'r',
    IDX_NUM_ROTS:'w',
    IDX_LOC_KP:'w',
    IDX_SPD_KP:'w',
    IDX_SPD_KI:'w'
}

# BELOW ARE HELPER FUNCTIONS FOR CONSTRUCTING RELEVANT CYBERGEAR CAN MESSAGES.
# This stops short of sending the messages to allow for simulated enviornments and
# testing. Generally, the structure of a CAN message for these motors is as such.
# Arbitration ID contains three used 'fields'. The left most field (bit 28-24) contains
# the "communication type" indicating how the host or motor should respond to and unpack
# the command. This can always be extracted first to determine how to read the rest
# of the message. The middle field (bit 23-8) is a secondary data field. This can be
# used to carry additional information that the host or motor can act on. The 
# rightmost field is the 'target', i.e. which device the message is intended for.
# For messages intended for the host (coming from the motor), this is 0. Some messages use a 
# constant check value however. The data field is an 8 byte field with the majority of the
# message information. The functions below intend to preserve this notation and 
# distinciton to avoid confusion with documentation and minimize comments.

def float_to_uint(x:float, x_min:float, x_max:float, n_bits:int) -> int:
    x = x_min if x < x_min else x_max if x > x_max else x # clamp x to [x_min, x_max]
    return int((x-x_min)*(((1<<n_bits)-1))/(x_max - x_min)) # scale x to [0, 2^n_bits-1]

def uint_to_float(x:int, x_min:float, x_max:float, n_bits:int) -> float:
    return (x / ((1<<n_bits)-1) * (x_max - x_min)) + x_min

def build_arbitration_id(target_id:int, cmd_id:int, data_field:int) -> int:
    return (cmd_id << 24) | (data_field << 8) | target_id

def parse_message(msg: can.Message):
    communication_type = (msg.arbitration_id & 0x3F000000) >> 24
    target_id = msg.arbitration_id & 0xFF
    if target_id != MASTER_CAN_ID and target_id != RESPONSE_IDENTITY_CHECK_FLAG:
        return -1
    if communication_type == RESPONSE_IDENTITY:
        return parse_identity_response(msg) 
    elif communication_type == RESPONSE_PARAM:
        return parse_param_response(msg)
    elif communication_type == RESPONSE_FAULT:
        return
    elif communication_type == RESPONSE_MOTION:
        return parse_motion_response(msg)

def parse_param_response(msg: can.Message) -> list:
    data = msg.data
    host_id = msg.arbitration_id & 0xFF
    cmd_id = (msg.arbitration_id & 0x3F000000) >> 24
    motor_id = (msg.arbitration_id & 0xFF00) >> 8
    param_index = (data[1] << 8) | data[0]
    num_param_bytes = PARAM_NUM_BYTES[param_index]
    if num_param_bytes == 1:
        return param_index, data[4], motor_id
    elif num_param_bytes == 2:
        return param_index, int.from_bytes(data[4:6]), motor_id
    elif num_param_bytes == 4:
        return param_index, int.from_bytes(data[4:]), motor_id



def parse_motion_response(msg: can.Message, actuator_model) -> list:
    # Core information
    temperature = (msg.data[7] | (msg.data[6] << 8))/10.0
    position = uint_to_float(msg.data[1] | (msg.data[0] << 8), P_MIN[actuator_model], P_MAX[actuator_model], N_BITS)
    velocity = uint_to_float(msg.data[3] | (msg.data[2] << 8), V_MIN[actuator_model], V_MAX[actuator_model], N_BITS)
    torque = uint_to_float(msg.data[5] | (msg.data[4] << 8), T_MIN[actuator_model], T_MAX[actuator_model], N_BITS)
    # Fault Information
    motor_can_id = (msg.arbitration_id >> 8) & 0xFF
    motor_mode = (msg.arbitration_id >> 22) & 0x3
    calibration_fault = (msg.arbitration_id >> 21) & 0x1
    hall_encoder_fault = (msg.arbitration_id >> 20) & 0x1
    magnetic_encoder_fault = (msg.arbitration_id >> 19) & 0x1
    overtemp_fault = (msg.arbitration_id >> 18) & 0x1
    overcurrent_fault = (msg.arbitration_id >> 17 ) & 0x1
    undervoltage_fault = (msg.arbitration_id >> 16) & 0x1

    return [
        position,
        velocity, 
        torque, 
        temperature,
        motor_can_id,
        motor_mode, 
        calibration_fault, 
        hall_encoder_fault,
        magnetic_encoder_fault,
        overtemp_fault,
        overcurrent_fault,
        undervoltage_fault 
    ]

def parse_identity_response(msg: can.Message) -> list:
    check_flag = msg.arbitration_id & 0xFF  
    cmd_id = (msg.arbitration_id & 0x3F000000) >> 24
    motor_id = (msg.arbitration_id & 0x7FFF80) >> 8
    unique_identity = int.from_bytes(msg.data, byteorder='big')
    #print(f'{check_flag:x}')
    #print(cmd_id)
    if cmd_id == RESPONSE_IDENTITY and check_flag == RESPONSE_IDENTITY_CHECK_FLAG:
        return unique_identity, motor_id
    return False, False

def create_enable_motion_message(target_motor_id: int):
    enable_motion = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_ENABLE_MOTION, data_field=MASTER_CAN_ID),
        data=[0]*8,
        is_extended_id=True
    )
    return enable_motion

def create_disable_motion_message(target_motor_id: int, clear_fault:bool=False):
    data = [1,0,0,0,0,0,0,0] if clear_fault else [0]*8
    disable_motion = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_DISABLE_MOTION, data_field=MASTER_CAN_ID),
        data=data,
        is_extended_id=True
    )
    return disable_motion

def create_read_device_id_message(target_motor_id: int):
    read_device_id = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_GET_DEVICE_ID, data_field=MASTER_CAN_ID),
        data=[0]*8,
        is_extended_id=True
    )
    return read_device_id

def create_set_can_id_message(target_motor_id: int, new_motor_id: int):
    set_device_id = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_CHANGE_DEVICE_ID, data_field=(new_motor_id<<8 | MASTER_CAN_ID)),
        data=[0]*8,
        is_extended_id=True
    )
    return set_device_id

def create_read_param_message(target_motor_id: int, param_index: int):
    if param_index not in VALID_PARAMS:
        raise ValueError(f'{param_index} is not a valid parameter index. Please use the defined constant indices')
    read_param = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_READ_PARAM, data_field=MASTER_CAN_ID),
        data=[param_index & 0xFF, (param_index >> 8) & 0xFF, 0, 0, 0, 0, 0, 0],
        is_extended_id=True
    )
    return read_param

def create_zero_position_message(target_motor_id:int):
    zero_position = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_SET_ZERO, data_field=MASTER_CAN_ID),
        data=[1,0,0,0,0,0,0,0],
        is_extended_id=True
    )
    return zero_position

def create_motion_message(target_motor_id:int, position:float, velocity:float, kp:float, kd:float, torque:float, actuator_model:str):
    pos_field = float_to_uint(position, P_MIN[actuator_model], P_MAX[actuator_model], N_BITS)
    vel_field = float_to_uint(velocity, V_MIN[actuator_model], V_MAX[actuator_model], N_BITS)
    kp_field = float_to_uint(kp, KP_MIN, KP_MAX, N_BITS)
    kd_field = float_to_uint(kd, KD_MIN, KD_MAX, N_BITS)
    torque_field = float_to_uint(torque, T_MIN[actuator_model], T_MAX[actuator_model], N_BITS)
    #print(T_MIN[actuator_model], T_MAX[actuator_model])

    motion = can.Message(
        arbitration_id=build_arbitration_id(target_id=target_motor_id, cmd_id=CMD_SET_MOTION, data_field=torque_field),
        data=[
            (pos_field >> 8),
            (pos_field & 0xFF),
            (vel_field >> 8),
            (vel_field & 0xFF),
            (kp_field >> 8),
            (kp_field & 0xFF),
            (kd_field >> 8),
            (kd_field & 0xFF)
        ],
        is_extended_id=True
    )
    return motion
