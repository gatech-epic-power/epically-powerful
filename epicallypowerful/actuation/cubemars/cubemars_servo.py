import can
import struct
from epicallypowerful.actuation.actuator_abc import Actuator
from epicallypowerful.actuation.motor_data import MotorData
import math
# Servo Mode Functions
DUTY_CYCLE_MODE = 0
CURRENT_LOOP_MODE = 1
CURRENT_BRAKE_MODE = 2
VELOCITY_MODE = 3
POSITION_MODE = 4
SET_ORIGIN_MODE = 5
POSITION_VELOCITY_LOOP_MODE = 6

DEG2RAD = 3.14159265359/180.0
RAD2DEG = 180.0/3.14159265359
DEGPERSEC2RPM = 1/6

def read_servo_message(msg: can.Message) -> list[float]:
    pos = int.from_bytes(msg.data[0:2], byteorder="big", signed=True) * 0.1 * DEG2RAD
    vel = int.from_bytes(msg.data[2:4], byteorder="big", signed=True) * 10 # VALUE IS IN ERPM -> ENSURE CONVERSION IF USING OUTSIDE THIS SCOPE
    current = int.from_bytes(msg.data[4:6], byteorder="big", signed=True) * 0.01
    temp = msg.data[6]
    errs = msg.data[7]
    return [pos, vel, current, temp, errs]


def make_duty_cycle_message(target_id: int, duty_cycle: float) -> can.Message:
    duty_cycle = int(duty_cycle * 100000)
    data = [
        (duty_cycle >> 24) & 0xFF, # Fourth byte
        (duty_cycle >> 16) & 0xFF, # Third byte
        (duty_cycle >> 8) & 0xFF,  # Second byte
        duty_cycle & 0xFF          # First byte
    ]

    return can.Message(
        arbitration_id=target_id | (DUTY_CYCLE_MODE << 8),
        data=data,
        is_extended_id=True
    )


def make_current_loop_message(target_id: int, current: float) -> can.Message:
    # Current values range from -60A to 60A -> gets scaled to -60000 to 60000
    if current > 60:
        current = 60
    elif current < -60:
        current = -60

    current = int(current * 1000)
    data = [
        (current >> 24) & 0xFF, # Fourth byte
        (current >> 16) & 0xFF, # Third byte
        (current >> 8) & 0xFF,  # Second byte
        current & 0xFF          # First byte
    ]
    return can.Message(
        arbitration_id=target_id | (CURRENT_LOOP_MODE << 8),
        data=data,
        is_extended_id=True
    )


def make_current_brake_message(target_id: int, current: float) -> can.Message:
    # Current values range from 0A to 60A -> gets scaled to 0 to 60000
    if current < -60:
        current = -60
    elif current > 60:
        current = 60

    current = int(current * 1000)
    data = [
        (current >> 24) & 0xFF,  # Fourth byte
        (current >> 16) & 0xFF,  # Third byte
        (current >> 8) & 0xFF,  # Second byte
        current & 0xFF          # First byte
    ]
    return can.Message(
        arbitration_id=target_id | (CURRENT_BRAKE_MODE << 8),
        data=data,
        is_extended_id=True
    )


def make_velocity_mode_message(target_id: int, velocity: float) -> can.Message:
    # RPM is in actual values, ranged from -100000 to 100000
    if velocity > 100000:
        velocity = 100000
    elif velocity < -100000:
        velocity = -100000

    velocity = int(velocity)
    data = [
        (velocity >> 24) & 0xFF,
        (velocity >> 16) & 0xFF,
        (velocity >> 8) & 0xFF,
        velocity & 0xFF
    ]
    return can.Message(
        arbitration_id=target_id | (VELOCITY_MODE << 8),
        data=data,
        is_extended_id=True
    )


def make_position_mode_message(target_id: int, position: float) -> can.Message:
    # Position is in degrees and ranges from -36000 deg to 36000 deg, scaled it interally up to -360000000 to 360000000
    if position > 36000:
        position = 36000
    elif position < -36000:
        position = -36000

    position = int(position * 10000)

    data = [
        (position >> 24) & 0xFF,
        (position >> 16) & 0xFF,
        (position >> 8) & 0xFF,
        position & 0xFF
    ]
    return can.Message(
        arbitration_id=target_id | (POSITION_MODE << 8),
        data=data,
        is_extended_id=True
    )


def make_set_origin_mode_message(target_id: int, persistence: int):
    # Persistence specifies the method, 0 will revert the zero setpoint at
    # a power cycle, 1 will change it permanently, 2 will clear to the default
    # setpoint
    if persistence > 2 or persistence < 0:
        raise ValueError("persistence parameter must be in the range 0-2")

    data = [persistence, 0, 0, 0]
    return can.Message(
        arbitration_id=target_id | (SET_ORIGIN_MODE << 8),
        data=data,
        is_extended_id=True
    )


def make_position_velocity_mode_message(target_id: int, position: float, velocity: float, acceleration: float) -> can.Message:
    # Same position and velocity scaling
    if position > 36000:
        position = 36000
    elif position < -36000:
        position = -36000

    if velocity > 100000:
        velocity = 100000
    elif velocity < -100000:
        velocity = -100000

    if acceleration > 100000:
        acceleration = 100000
    elif acceleration < -100000:
        acceleration = -100000

    position = int(position * 10000)

    data = [
        (position >> 24) & 0xFF,
        (position >> 16) & 0xFF,
        (position >> 8) & 0xFF,
        position & 0xFF,
        velocity >> 8 & 0xFF,
        velocity & 0xFF,
        acceleration >> 8 & 0xFF,
        acceleration & 0xFF
    ]
    return can.Message(
        arbitration_id=target_id | (POSITION_VELOCITY_LOOP_MODE << 8),
        data=data,
        is_extended_id=True
    )

class CubeMarsServo(can.Listener, Actuator):
    def __init__(self, can_id: int, motor_type: str, invert: bool = False):
        self.can_id = can_id
        self.motor_type = motor_type
        self.invert = -1 if invert else 1
        self._bus = None
        self.data = MotorData(
            motor_id=self.can_id,
            motor_type=self.motor_type,
            current_position=0,
            current_velocity=0,
            current_torque=0,
            commanded_position=0,
            commanded_velocity=0,
            commanded_torque=0,
            kp=0,
            kd=0,
            timestamp=-1,
            running_torque=(),
            rms_torque=0,
            rms_time_prev=0,
        )
        self._connection_established = False
        self._reconnection_start_time = 0
        self.prev_command_time = 0
        self._over_limit = False
        self.torque_monitor = None

    def on_message_received(self, msg: can.Message):
        """Handles a received CAN message.

        :meta private:
        
        Args:
            msg (can.Message): The received CAN message.
        """
        if msg.arbitration_id == ((0x29 << 8) | (self.can_id)):
            [pos, vel, cur, temp, err] = read_servo_message(msg)
            self.data.current_position = pos * self.invert
            self.data.current_velocity = vel * self.invert * self.data.erpm_to_rpm / DEGPERSEC2RPM * DEG2RAD
            self.data.current_torque = cur * self.invert
            self.data.temperature = temp
            self.data.error_code = err
            self.data.timestamp = msg.timestamp

    def call_response_latency(self):
        return self.data.last_command_time - self.data.timestamp
    
    def set_control(self, pos, vel, torque, kp, kd, degrees = False):
        raise NotImplementedError("CubeMarsServo does not support combined control mode. Use individual control methods instead.")

    def set_torque(self, torque: float):
        """Sets the torque of the motor as a direct current value. Range is -60A to 60A.

        Args:
            torque (float): The current to set the motor to in Amperes.
        """
        torque = torque * self.invert
        self.commanded_torque = torque
        self.commanded_position = 0
        self.commanded_velocity = 0
        self.kp = 0
        self.kd = 0

        msg = make_current_loop_message(self.can_id, torque)
        self._bus.send(msg)
        self.data.commanded_torque = torque
    
    def set_position(self, position, kp: float, kd: float, degrees = False):
        """Sets the position of the motor in position control mode. Range is -36000 to 36000 degrees.

        Args:
            position (float): The position to set the motor to (defaults to radians).
            kp (float): Dummy variable for compatibility, not used in servo mode. To adjust these gains, use the RLink software.
            kd (float): Dummy variable for compatibility, not used in servo mode. To adjust these gains, use the RLink software.
            degrees (bool, optional): Whether the position is in degrees. Defaults to False.
        """
        position = position * self.invert 
        
        if not degrees:
            pos_deg = position * RAD2DEG
        else:
            pos_deg = position

        self.commanded_torque = 0
        self.commanded_position = pos_deg * DEG2RAD
        self.commanded_velocity = 0
        self.kp = 0
        self.kd = 0
        

        msg = make_position_mode_message(self.can_id, pos_deg)
        self._bus.send(msg)

    def set_velocity(self, velocity, kp: float, degrees = False):
        """Sets the velocity of the motor in velocity control mode. Range varies per motor.

        Args:
            velocity (float): The velocity to set the motor to (defaults to radians/second).
            kp (float): Dummy variable for compatibility, not used in servo mode. To adjust these gains, use the RLink software.
            degrees (bool, optional): Whether the velocity is in degrees per second. Defaults to False.
        """
        velocity = velocity * self.invert
        if not degrees:
            vel_deg_per_sec = velocity * RAD2DEG
        else:
            vel_deg_per_sec = velocity

        self.commanded_torque = 0
        self.commanded_position = 0
        self.commanded_velocity = vel_deg_per_sec * DEG2RAD
        self.kp = 0
        self.kd = 0

        # CONVERT DEG per SEC to RPM then to eRPM
        vel_to_send = vel_deg_per_sec * DEGPERSEC2RPM / self.data.erpm_to_rpm
        msg = make_velocity_mode_message(self.can_id, vel_to_send)
        self._bus.send(msg)

    def get_data(self) -> MotorData:
        """Returns the current motor data.

        Returns:
            MotorData: The current data of the motor.
        """
        return self.data
    
    def get_torque(self):
        """Returns the measured current value of the motor. In servo mode, this value is signed in "braking/assisting" convention, and does not indicate the actual clockwise/counterclockwise direction of torque.

        Returns:
            float: The measured current of the motor (Amps).
        """
        return self.data.current_torque * self.invert
    
    def get_position(self, degrees = False):
        """Returns the current position of the motor.

        Args:
            degrees (bool, optional): Whether to return the position in degrees. Defaults to False.

        Returns:
            float: The current position of the motor.
        """
        return self.data.current_position * self.invert if not degrees else self.data.current_position * self.invert * 180.0 / 3.14159265359
    
    def get_velocity(self, degrees = False):
        """Returns the current velocity of the motor.

        Args:
            degrees (bool, optional): Whether to return the velocity in degrees per second. Defaults to False.

        Returns:
            float: The current velocity of the motor.
        """
        return self.data.current_velocity * self.invert if not degrees else self.data.current_velocity* self.invert * 180.0 / 3.14159265359
    
    def get_temperature(self):
        """Returns the current temperature of the motor.

        Returns:
            float: The current temperature of the motor in degrees Celsius.
        """
        return self.data.temperature
    
    def zero_encoder(self):
        """Zeros the encoder position to the current position.
        """
        self._bus.send(make_set_origin_mode_message(self.can_id, 1))

    def _enable(self):
        """Enables the motor by sending a current loop message with zero current.
        """
        self._bus.send(make_current_loop_message(self.can_id, 0))
    
    def _disable(self):
        """Disables the motor by sending a current brake message with zero current.
        """
        os.write("disabling")
        self.set_torque(0)
        #self._bus.send(make_current_loop_message(self.can_id, 0))

    def _set_zero_torque(self):
        """Sets the motor torque to zero.
        """
        self.set_torque(0)

if __name__ == "__main__":
    import time
    from epicallypowerful.actuation import ActuatorGroup
    from epicallypowerful.toolbox import LoopTimer, TimedLoop, DataRecorder
    import statistics
    from scipy.signal import chirp
    import numpy as np
    import plotext as plt
    ACT_ID = 104
    TARGET_FREQ = 20
    FREQ = 200
    DURATION = 20
    SAMPLES = FREQ * DURATION
    act_group = ActuatorGroup( [CubeMarsServo(ACT_ID, "AK10-9-V2.0")] )
    act_group.enable_actuators()
    loop2 = TimedLoop(FREQ)
    recorder = DataRecorder("AK10-9V2.0_chirp_test2A.csv", headers=["pos_desired", "pos_measured"])
    t0 = time.time()
    curs = []
    poss = []
    itter = 0
    times = np.arange(SAMPLES) * 1/FREQ
    time.sleep(1)
    print("PREPARING POSITIONAL TEST")
    chirp_signal = chirp(times, 0, DURATION, TARGET_FREQ)
    step_signal = np.zeros(SAMPLES); step_signal[SAMPLES//2:]=1 
    sine_wave = np.sin(2*np.pi*0.25*times)
    impulse_signal = np.zeros(SAMPLES); impulse_signal[SAMPLES//2:(SAMPLES//2)+100]=1
    signal = sine_wave * 2
    t0 = time.perf_counter()
    while loop2():
        cur = act_group.get_torque(ACT_ID)
        pos = act_group.get_position(ACT_ID)
        vel = act_group.get_velocity(ACT_ID)
        act_group.set_torque(ACT_ID, signal[itter])
        #act_group.set_velocity(ACT_ID, 3, 0)
        curs.append(cur)
        poss.append(pos)
        recorder.save([chirp_signal[itter], curs])
        itter += 1
        if itter == SAMPLES: break
    recorder.finalize()
    plt.plot(times, signal, label="target")
    plt.plot(times, curs, label="measured")
    plt.show()
    #print(statistics.mean(curs))
    #print(time.perf_counter() - t0)
