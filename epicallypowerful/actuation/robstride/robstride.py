import can
import time
from can import CanOperationError
from epicallypowerful.actuation.motor_data import MotorData
from epicallypowerful.actuation.actuator_abc import Actuator
import math
from typing import Callable
import functools
import epicallypowerful.actuation.robstride.robstride_driver as rsd

class Robstride(can.Listener, Actuator):
    """Class for controlling an individual Robstride actuator. This class should always be initialized as part of an ActuatorGroup so that the can bus is appropriately shared between all motors.
    Alternatively, the bus can be set manually after initialization, however this is not recommended.

    The Cybergears can be initialized to be inverted by default, which will reverse the default Clockwise/Counter-Clockwise direction of the motor.

    Example:
        .. code-block:: python


            from epicpower.actuation2 import Cybergear, ActuatorGroup
            motor = Cybergear(0x01)
            group = ActuatorGroup([motor])

            motor.set_torque(0.5)
            # OR
            group[0x01].set_torque(0.5)
            # OR
            group.set_torque(0x01, 0.5)

    Args:
        can_id (int): CAN ID of the motor. This should be unique for each motor in the system, and can be set up with the RLink software.
        motor_type (str, optional): A string representing the type of motor.
        invert (bool, optional): Whether to invert the motor direction. Defaults to False.
    """
    def __init__(self, can_id: int, motor_type: str, invert: bool=False):
        self.can_id = can_id
        self.motor_type = motor_type
        if invert: self.invert = -1
        else: self.invert = 1
        self._bus = None
        self.data = MotorData(
            motor_id=self.can_id, motor_type=self.motor_type,
            current_position=0, current_velocity=0, current_torque=0,
            commanded_position=0, commanded_velocity=0, commanded_torque=0,
            kp=0, kd=0, timestamp=-1,
            running_torque=(), rms_torque=0, rms_time_prev=0
        )

        self._connection_established = False
        self._priming_reconnection = False
        self._reconnection_start_time = 0
        self.prev_command_time = 0

    def on_message_received(self, msg: can.Message) -> None:
        """Interprets the message received from the CAN bus

        :meta private:

        Args:
            msg (can.Message): the most recent message received on the bus
        """
        if (not msg.is_extended_id) or msg.is_error_frame or (not msg.is_rx): return -1

        communication_type = (msg.arbitration_id & 0x3F000000) >> 24
        target_id = msg.arbitration_id & 0xFF # Which device the message is intended for. This is typically 0 for the host, or a message specifying it is an identity check.

        if (target_id != rsd.MASTER_CAN_ID) and (target_id != rsd.RESPONSE_IDENTITY_CHECK_FLAG): return -1

        if communication_type == rsd.RESPONSE_IDENTITY: # This is the response to the identity check
            unique_id, can_id = rsd.parse_identity_response(msg)
            if can_id != self.can_id: return -1
            self.data.unique_hardware_id=unique_id

        if communication_type == rsd.RESPONSE_PARAM:
            param_index, data_value, can_id = rsd.parse_param_response(msg)
            if can_id != self.can_id: return -1
            self.data.internal_params[param_index] = data_value

        if communication_type == rsd.RESPONSE_FAULT: return -1

        if communication_type == rsd.RESPONSE_MOTION:
            pos, vel, trq, temp, can_id, motor_mode, cal_fault, hall_enc_fault, mag_enc_fault, overtemp_fault, overcurr_fault, undervolt_fault = rsd.parse_motion_response(msg, self.data.motor_type)
            if can_id != self.can_id: return -1
            self.data.current_position = pos
            self.data.current_velocity = vel
            self.data.current_torque = trq
            self.data.motor_mode = motor_mode
            self.data.current_temperature = temp
            self.data.timestamp = time.perf_counter()


    def _ping_actuator(self) -> None:
        self._bus.send(rsd.create_read_device_id_message(self.can_id))

    def _send_motion_command(self, can_id: int, position: float, velocity: float, torque: float, kp: float, kd: float) -> int:
        # Account for inversion
        position *= self.invert
        velocity *= self.invert
        torque *= self.invert

        self.data.commanded_position = position
        self.data.commanded_velocity = velocity
        self.data.commanded_torque = torque
        self.data.kp = kp
        self.data.kd = kd

        motion_message = rsd.create_motion_message(target_motor_id=can_id, position=position, velocity=velocity, kp=kp, kd=kd, torque=torque, actuator_model=self.data.motor_type)
        self._bus.send(motion_message, timeout=0)

        return 1

    def call_response_latency(self) -> float:
        return self.data.last_command_time - self.data.timestamp

    def set_torque(self, torque: float) -> None:
        """Sets the torque of the motor in Newton-meters. This will saturate if the torque is outside the limits of the motor.
        Positive and negative torques will spin the motor in opposite directions, and this direction will be reversed if the motor is inverted at initialization.

        Args:
            torque (float): The torque to set the motor to in Newton-meters.
        """
        return self._send_motion_command(self.can_id, 0, 0, torque, 0, 0)

    def set_position(self, position: float, kp: float, kd: float, degrees: bool = False) -> None:
        """Sets the position of the motor in radians. Positive and negative positions will spin the motor in opposite directions, and this direction will be reversed if the motor is inverted at initialization.

        Args:
            position (float): Position to set the actuator to in radians or degrees depending on the ``degrees`` argument.
            kp (float): Set the proportional gain (stiffness) of the actuator in Newton-meters per radian.
            kd (float): Set the derivative gain (damping) of the actuator in Newton-meters per radian per second.
            degrees (bool): Whether the position is in degrees or radians.
        """
        return self._send_motion_command(self.can_id, position, 0, 0, kp, kd)

    def set_velocity(self, velocity: float, kd: float, degrees: bool = False) -> None:
        """Sets the velocity of the motor in radians per second. Positive and negative velocities will spin the motor in opposite directions, and this direction will be reversed if the motor is inverted at initialization.

        Args:
            velocity (float): Velocity to set the actuator to in radians per second or degrees per second depending on the ``degrees`` argument.
            kd (float): Set the derivative gain (damping) of the actuator in Newton-meters per radian per second.
            degrees (bool): Whether the velocity is in degrees per second or radians per second.
        """
        return self._send_motion_command(self.can_id, 0, velocity, 0, 0, kd)

    def zero_encoder(self):
        return self._bus.send(rsd.create_zero_position_message(self.can_id))

    def get_data(self) -> MotorData:
        """Returns the current data of the motor

        Returns:
            MotorData: Data from the actuator. Contains up-to-date information from the actuator as of the last time a message was sent to the actuator.
        """
        return self.data

    def get_torque(self) -> float:
        """Returns the current torque of the motor in Newton-meters. Functionally equivalent to the property ``torque`` or ``get_data().current_torque``.

        Returns:
            float: The current torque of the motor in Newton-meters.
        """
        return self.data.current_torque * self.invert

    def get_position(self, degrees: bool = False) -> float:
        """Returns the current position of the motor in radians. Functionally equivalent to the property ``position`` or ``get_data().current_position``.

        Args:
            degrees (bool, optional): Whether to return the position in degrees or radians. Defaults to False.

        Returns:
            float: The current position of the motor in radians or degrees.
        """
        if degrees: return self.data.current_position * self.invert * 180/math.pi
        else: return self.data.current_position * self.invert

    def get_velocity(self, degrees: bool = False) -> float:
        """Returns the current velocity of the motor in radians per second. Functionally equivalent to the property ``velocity`` or ``get_data().current_velocity``.

        Args:
            degrees (bool, optional): Whether to return the velocity in degrees. Defaults to False.

        Returns:
            float: The current velocity of the motor in radians per second or degrees per second.
        """
        if degrees: return self.data.current_velocity * self.invert * 180/math.pi
        else: return self.data.current_velocity * self.invert

    def get_temperature(self) -> float:
        """Returns the current temperature of the motor in degrees Celsius.

        Returns:
            float: The current temperature of the motor in degrees Celsius.
        """
        return self.data.temperature

    def _enable(self) -> None:
        """Enables the motor
        """
        self._ping_actuator()
        enable_motion_message = rsd.create_enable_motion_message(target_motor_id=self.can_id)
        res = self._bus.send(enable_motion_message)
        self._connection_established = True
        self.data.initialized = True

    def _disable(self) -> None:
        """Disables the motor
        """
        disable_motion_message = rsd.create_disable_motion_message(target_motor_id=self.can_id)
        self._bus.send(disable_motion_message)
        self._connection_established = False
        self.data.initialized = False

    def _set_zero_torque(self) -> None:
        """Sets the torque of the motor to zero
        """
        return self._send_motion_command(self.can_id, 0, 0, 0.0, 0, 0)
        

