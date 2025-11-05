import can
from epicallypowerful.actuation.actuator_abc import Actuator
from epicallypowerful.actuation.motor_data import MotorData
from epicallypowerful.actuation.torque_monitor import RMSTorqueMonitor
import math
import time

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180.0
DEGPERSEC2RPM = 1.0/6.0

MIT_MODE_ID = 8
ORIGIN_SET_ID = 5


def _float_to_uint(x, x_min, x_max, bits):
    span = float(x_max - x_min)
    return int( (x-x_min) * (((1 << bits)-1) / span))

def _clamp(x, x_min, x_max):
    return max(x_min, min(x_max, x))


def _read_cubemars_message(msg: can.Message) -> list[float]:
    pos = int.from_bytes(msg.data[0:2], byteorder="big", signed=True) * 0.1 * DEG2RAD
    vel = int.from_bytes(msg.data[2:4], byteorder="big", signed=True) * 10 # VALUE IS IN ERPM -> ENSURE CONVERSION IF USING OUTSIDE THIS SCOPE
    #print(msg.data[4:6])
    current = int.from_bytes(msg.data[4:6], byteorder="big", signed=True) * 0.01
    #print(current)
    temp = msg.data[6]
    errs = msg.data[7]
    return [pos, vel, current, temp, errs]

def _create_mit_message(can_id, pos, vel, kp, kd, torque, motor_data) -> can.Message:

    p_min, p_max = motor_data.position_limits
    v_min, v_max = motor_data.velocity_limits
    t_min, t_max = motor_data.torque_limits
    kp_min, kp_max = motor_data.kp_limits
    kd_min, kd_max = motor_data.kd_limits


    pos_uint16 = _float_to_uint(_clamp(pos, p_min, p_max), p_min, p_max, 16)
    torque_uint12 = _float_to_uint(_clamp(torque, t_min, t_max), t_min, t_max, 12)
    vel_uint12 = _float_to_uint(_clamp(vel, v_min, v_max), v_min, v_max, 12)
    kp_uint12 = _float_to_uint(_clamp(kp, kp_min, kp_max), kp_min, kp_max, 12)
    kd_uint12 = _float_to_uint(_clamp(kd, kd_min, kd_max), kd_min, kd_max, 12)

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

class CubeMarsV3(can.Listener, Actuator):
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
        self.torque_monitor = RMSTorqueMonitor(limit=abs(self.data.rated_torque_limits[1]), window=20)
        self._over_limit = False


    def on_message_received(self, msg: can.Message) -> None:
        if msg.arbitration_id == ((0x29 << 8) | (self.can_id)):
            pos, vel, cur, temp, err = _read_cubemars_message(msg)
            self.data.current_position = pos * self.invert
            self.data.current_velocity = vel * self.invert * self.data.erpm_to_rpm / DEGPERSEC2RPM * DEG2RAD
            self.data.current_torque = cur * self.invert
            self.data.temperature = temp
            self.data.error_code = err
            self.data.timestamp = time.perf_counter()
            rms_torque, _ = self.torque_monitor.update(self.data.current_torque)
            self.data.rms_torque = rms_torque
            self._over_limit = self.torque_monitor.over_limit()
            return

    def call_response_latency(self):
        return self.data.last_command_time - self.data.timestamp
    
    def set_control(self, pos, vel, torque, kp, kd, degrees=False):
        pos = self.invert * pos
        vel = self.invert * vel
        torque = self.invert * torque
        if degrees:
            pos *= DEG2RAD
            kp *= RAD2DEG
            kd *= RAD2DEG
        
        self.commanded_torque = torque
        self.commanded_position = pos
        self.commanded_velocity = vel
        self.kp = kp
        self.kd = kd
        msg = _create_mit_message(
                self.can_id, pos, vel, kp, kd, torque, self.data
        )
        self._bus.send(msg)

    def set_torque(self, torque: float) -> None:
        torque = self.invert * torque
        self.data.commanded_torque = torque
        self.data.commanded_position = 0
        self.data.commanded_velocity = 0
        self.data.kp = 0
        self.data.kd = 0
        msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, self.data.commanded_torque, self.data
        )
        self._bus.send(msg)

    def set_position(self, position: float, kp: float, kd: float, degrees: bool = False) -> None:
        if degrees:
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
            self.data.kp, self.data.kd, 0, self.data
        )
        self._bus.send(msg)

    def set_velocity(self, velocity: float, kd: float, degrees: bool = False) -> None:
        if degrees:
            velocity *= DEG2RAD
            kd *= RAD2DEG
        velocity = self.invert * velocity
        self.data.commanded_velocity = velocity
        self.data.kp = 0
        self.data.kd = kd
        self.data.commanded_torque = 0
        self.data.commanded_position = 0
        msg = _create_mit_message(
            self.can_id, 0, self.data.commanded_velocity,
            0, self.data.kd, 0, self.data
        )
        self._bus.send(msg)

    def get_data(self) -> MotorData:
        return self.data
    
    def get_torque(self) -> float:
        return self.data.current_torque
    
    def get_position(self, degrees=False) -> float:
        if degrees:
            return self.data.current_position * RAD2DEG
        return self.data.current_position
    
    def get_velocity(self, degrees=False) -> float:
        if degrees:
            return self.data.current_velocity * RAD2DEG
        return self.data.current_velocity
    
    def get_temperature(self) -> float:
        return self.data.temperature
    
    def zero_encoder(self):
        msg = _create_set_origin_message(self.can_id)
        self._bus.send(msg)

    def _enable(self) -> None:
        #if (time.perf_counter() - self.data.timestamp) > 0.1: return
        zero_trq_msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, 0, self.data
        )
        self._bus.send(zero_trq_msg)
    
    def _disable(self) -> None:
        zero_trq_msg = _create_mit_message(
            self.can_id, 0, 0,
            0, 0, 0, self.data
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
            0, 0, 0, self.data
        )
        self._bus.send(msg)

if __name__ == '__main__':
    from epicallypowerful.actuation.actuator_group import _load_can_drivers
    _load_can_drivers()
    can_id = 67
    motor_data = MotorData(can_id, 'AKE-60-8')
    msg = _create_mit_message(can_id, 0, 0, 2, 0.1, 0, motor_data)
    bus = can.Bus(interface='socketcan', channel='can0')
    import time
    while True:
        time.sleep(0.01)
        bus.send(msg)


