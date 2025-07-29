import can
from epicallypowerful.actuation.actuator_abc import Actuator
from epicallypowerful.actuation.motor_data import MotorData
import math

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180.0

MIT_MODE_ID = 8
ORIGIN_SET_ID = 5

P_MIN = -12.56
P_MAX = 12.56
V_MIN = -28.0
V_MAX = 28.0
T_MIN = -54.0
T_MAX = 54.0
KP_MIN = 0
KP_MAX = 500.0
KD_MIN = 0
KD_MAX = 5.0


def _float_to_uint(x, x_min, x_max, bits):
    span = float(x_max - x_min)
    return int( (x-x_min) * (((1 << bits)-1) / span))

def _clamp(x, x_min, x_max):
    return max(x_min, min(x_max, x))


def _read_cubemars_message(msg: can.Message) -> list[float]:
    pos_int = msg.data[0] << 8 | msg.data[1]
    vel_int = msg.data[2] << 8 | msg.data[3]
    current_int = msg.data[4] << 8 | msg.data[5]
    
    pos = pos_int*0.1
    vel = vel_int*10.0
    current = current_int*0.01
    temp = msg.data[6]
    errs = msg.data[7]
    return [pos, vel, current, temp, errs]

def _create_mit_message(can_id, pos, vel, kp, kd, torque) -> can.Message:
    pos_uint16 = _float_to_uint(_clamp(pos), P_MIN, P_MAX, 16)
    torque_uint12 = _float_to_uint(_clamp(torque), T_MIN, T_MAX, 12)
    vel_uint12 = _float_to_uint(_clamp(vel), V_MIN, V_MAX, 12)
    kp_uint12 = _float_to_uint(_clamp(kp), KP_MIN, KP_MAX, 12)
    kd_uint12 = _float_to_uint(_clamp(kd), KD_MIN, KD_MAX, 12)

    buffer = [
        kp_uint12 >> 4, # KP High 4 bits
        ((kp_uint12 & 0xF) << 4) | (kd_uint12 >> 8),  # KP Low 4 bits, Kd High 4 bits
        kd_uint12 & 0xFF,  # Kd low 8 bits
        pos_uint16 >> 8,  # position high 8 bits
        pos_uint16 & 0xFF,  # position low 8 bits
        vel_uint12 >> 4,  # speed high 8 bits
        ((vel_uint12 & 0xF) << 4) | (torque_uint12 >> 8),  # speed low 4 bits torque high 4 bits
        torque_uint12 & 0xFF  # torque low 8 bits
    ]

    arbitration_id = MIT_MODE_ID << 8 | can_id
    return can.Message(
        arbitration_id=arbitration_id,
        data=buffer,
        is_extended_id=True
    )

def _create_set_origin_message(can_id: int) -> can.Message:
    buffer = [0] * 8
    arbitration_id = ORIGIN_SET_ID << 8 | can_id
    return can.Message(
        arbitration_id=arbitration_id,
        data=buffer,
        is_extended_id=True
    )

class TMotorV3(can.Listener, Actuator):
    def __init__(self, can_id: int, motor_type: str, invert: bool = False):
        self.can_id = can_id
        self.motor_type = motor_type
        self.invert = -1 if invert else 1
        self._bus = None
        self.data = MotorData(
            motor_id=self.can_id, motor_type=self.motor_type,
            current_position=0, current_velocity=0, current_torque=0,
            commanded_position=0, commanded_velocity=0, commanded_torque=0,
            kp=0, kd=0, timestamp=-1,
            running_torque=(), rms_torque=0, rms_time_prev=0
        )

        self._connection_established = False
        self._reconnection_start_time = 0
        self.prev_command_time = 0


    def on_message_received(self, msg: can.Message) -> None:
        # print(f"Received message: {msg}") # Uncomment for debugging
        if msg.arbitration_id == (0x2900 + self.can_id) + (1 << 32): # Message is from the motor, shift the check by 
            pos, vel, current, temp, errs = _read_cubemars_message(msg)
            self.data.current_position = pos
            self.data.current_velocity = vel
            self.data.current_torque = current # This is not necessarily correct, the torque != to current in all cases
            self.data.temperature = temp
            # Ignoring errors for now

    def call_response_latency(self):
        return self.data.last_command_time - self.data.timestamp
    
    def set_torque(self, torque: float) -> None:
        torque = self.invert * torque
        self.data.commanded_torque = torque
        self.data.commanded_position = 0
        self.data.commanded_velocity = 0
        self.data.kp = 0
        self.data.kd = 0
        msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, self.data.commanded_torque
        )
        self._bus.send(msg)

    def set_position(self, position: float, kp: float, kd: float, degree: bool = False) -> None:
        if degree:
            position *= DEG2RAD
            kp *= RAD2DEG
            kd *= RAD2DEG
        position = self.invert * position
        self.data.commanded_position = position
        self.data.kp = kp
        self.data.kd = kd
        self.data.commanded_torque = 0
        self.data.commanded_velocity = 0
        msg = _create_mit_message(
            self.can_id, self.data.commanded_position, 0,
            self.data.kp, self.data.kd, self.data.commanded_torque
        )
        self._bus.send(msg)

    def set_velocity(self, velocity: float, kd: float, degree: bool = False) -> None:
        if degree:
            velocity *= DEG2RAD
            kd *= RAD2DEG
        velocity = self.invert * velocity
        self.data.commanded_velocity = velocity
        self.data.kd = kd
        self.data.commanded_torque = 0
        self.data.commanded_position = 0
        msg = _create_mit_message(
            self.can_id, 0, self.data.commanded_velocity,
            0, self.data.kd, self.data.commanded_torque
        )
        self._bus.send(msg)

    def get_data(self) -> MotorData:
        return self.data
    
    def get_torque(self) -> float:
        return self.data.current_torque * self.invert
    
    def get_position(self) -> float:
        return self.data.current_position * self.invert
    
    def get_velocity(self) -> float:
        return self.data.current_velocity * self.invert
    
    def get_temperature(self) -> float:
        return self.data.temperature
    
    def zero_encoder(self):
        msg = _create_set_origin_message(self.can_id)
        self._bus.send(msg)

    def _enable(self) -> None:
        zero_trq_msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, 0
        )
        self._bus.send(zero_trq_msg)
    
    def _disable(self) -> None:
        zero_trq_msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, 0
        )
        self._bus.send(zero_trq_msg)

    def _set_zero_torque(self):
        self.data.commanded_torque = 0.0
        self.data.commanded_position = 0.0
        self.data.commanded_velocity = 0.0
        self.data.kp = 0.0
        self.data.kd = 0.0
        msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, 0
        )
        self._bus.send(msg)
