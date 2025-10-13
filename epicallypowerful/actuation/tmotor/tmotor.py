import can
import time
from epicallypowerful.actuation.motor_data import MotorData
from epicallypowerful.actuation.actuator_abc import Actuator
import epicallypowerful.actuation.tmotor.tmotor_driver as tmd
from epicallypowerful.actuation.torque_monitor import RMSTorqueMonitor
import logging
import math

motorlog = logging.getLogger('motorlog')

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180.0

# ~~~~~ T Motor Class ~~~~~ #
class TMotor(can.Listener, Actuator):
    """Class for controlling an individual TMotor. This class should always be initialized as part of an :py:class:`ActuatorGroup` so that the can bus is appropriately shared between all motors.
    Alternatively, the bus can be set manually after initialization, however this is not recommended. If you want to implement it this way, please consult the `python-can documentation <https://python-can.readthedocs.io/en/stable/>`_.

    This class supports all motors from the AK series. Before use with this package, please follow :ref:`the tutorial for using RLink <Tutorials>` to
    properly configure the motor and CAN IDs.

    The TMotors can be intialized to be inverted by default, which will reverse the default Clockwise/Counter-Clockwise direction of the motor.

    Example:
        .. code-block:: python


            from epicpower.actuation2.tmotor import TMotor
            motor = TMotor(0x01, 'AK80-9')
            group = ActuatorGroup([motor])

            motor.set_torque(0.5)
            # OR
            group[0x01].set_torque(0.5)
            # OR
            group.set_torque(0x01, 0.5)


    Args:
        can_id (int): CAN ID of the motor. This should be unique for each motor in the system, and can be set up with the RLink software.
        motor_type (str): A string representing the type of motor. This is used to set the appropriate limits for the motor. Options include:
            * 'AK80-9'
            * 'AK80-64'
            * Et cetera et cetera
        invert (bool, optional): Whether to invert the motor direction. Defaults to False.


    Attributes:
        data (MotorData): Data from the actuator. Contains up-to-date information from the actuator as of the last time a message was sent to the actuator.
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
        self.torque_monitor = RMSTorqueMonitor(limit=self.data.rated_torque_limits[0], window=20.0)
        self._over_limit = False

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
        if msg.arbitration_id != 0 and msg.arbitration_id != self.can_id: return # ignore messages not for the host (0x0) or the motor (can_id)
        
        motor_id = msg.data[0]
        if motor_id != self.can_id: return # ignore messages not from this motor

        _, pos, vel, torque = tmd._unpack_motor_message(msg, motor=self.data)

        self.data.current_position = pos
        self.data.current_velocity = vel
        self.data.current_torque = torque
        self.data.timestamp = time.perf_counter()

        rms_torque, over_limit = self.torque_monitor.update(self.data.current_torque)
        self.data.rms_torque = rms_torque
        self._over_limit = over_limit
        return

    def call_response_latency(self) -> float:
        return self.data.last_command_time - self.data.timestamp
    
    def set_control(self, pos: float, vel: float, torque: float, kp: float, kd: float, degrees: bool = False) -> None:
        """Sets the control of the motor using full MIT control mode. This uses the built in capability to simultaneously use torque, as well as position and velocity control. It is highly recommended you consult

        Args:
            pos (float): Position to set the actuator to in radians or degrees depending on the ``degrees`` argument.
            vel (float): Velocity to set the actuator to in radians or degrees depending on the ``degrees`` argument.
            torque (float): Torque to set the actuator to in Newton-meters.
            kp (float): Proportional gain to set the actuator to in Newton-meters per radian or Newton-meters per degree depending on the ``degrees`` argument.
            kd (float): Derivative gain to set the actuator to in Newton-meters per radian per second or Newton-meters per degree per second depending on the ``degrees`` argument.
            degrees (bool, optional): Whether the position and velocity are in degrees or radians. Defaults to False.
        """
        # Alter values from degrees to radians (the TMotor needs to be commanded in radians)
        if degrees:
            pos = pos * DEG2RAD
            vel = vel * DEG2RAD
            kp = kp * RAD2DEG
            kd = kd * RAD2DEG

        pos = pos * self.invert
        vel = vel * self.invert
        torque = torque * self.invert

        self.data.commanded_position = pos
        self.data.commanded_velocity = vel
        self.data.commanded_torque = torque
        self.data.kp = kp
        self.data.kd = kd
        _packed_message = tmd._pack_motor_message(
            pos=pos, vel=vel, kp=kp, kd=kd, t=torque,
            motor=self.data
        )
        self._bus.send(_packed_message)

    def set_torque(self, torque: float) -> None:
        """Sets the torque of the motor in Newton-meters. This will saturate if the torque is outside the limits of the motor.
        Positive and negative torques will spin the motor in opposite directions, and this direction will be reversed if the motor is inverted at intialization.

        Args:
            torque (float): The torque to set the motor to in Newton-meters.
        """
        torque = torque * self.invert
        self.data.commanded_torque = torque
        self.data.commanded_velocity = 0
        self.data.commanded_position = 0
        self.data.kp = 0
        self.data.kd = 0
        _packed_message = tmd._pack_motor_message(
            pos=0, vel=0, kp=0, kd=0, t=torque,
            motor=self.data
        )
        self._bus.send(_packed_message)

    def set_position(self, position: float, kp: float, kd: float, degrees: bool = False) -> None:
        """Sets the position of the motor in radians. Positive and negative positions will spin the motor in opposite directions,
        and this direction will be reversed if the motor is inverted at intialization.

        Args:
            position (float): Position to set the actuator to in radians or degrees depending on the ``degrees`` argument.
            kp (float): Set the proportional gain (stiffness) of the actuator in Newton-meters per radian.
            kd (float): Set the derivative gain (damping) of the actuator in Newton-meters per radian per second.
            degrees (bool): Whether the position is in degrees or radians.
        """
        # Alter values from degrees to radians (the TMotor needs to be commanded in radians)
        if degrees:
            position = position * DEG2RAD
            kp = kp * RAD2DEG
            kd = kd * RAD2DEG

        position = position * self.invert
    
        self.data.commanded_position = position
        self.data.kp = kp
        self.data.kd = kd
        self.data.commanded_velocity = 0
        self.data.commanded_torque = 0
        _packed_message = tmd._pack_motor_message(
            pos=position, vel=0, kp=kp, kd=kd, t=0,
            motor=self.data
        )
        self._bus.send(_packed_message)

    def set_velocity(self, velocity: float, kd: float, degrees: bool = False) -> None:
        """Sets the velocity of the motor in radians per second. Positive and negative velocities will spin the motor in opposite directions, and this direction will be reversed if the motor is inverted at intialization.

        Args:
            velocity (float): Velocity to set the actuator to in radians per second or degrees per second depending on the ``degrees`` argument.
            kd (float): Set the derivative gain (damping) of the actuator in Newton-meters per radian per second.
            degrees (bool): Whether the velocity is in degrees per second or radians per second.
        """
        # Alter values from degrees to radians (the TMotor needs to be commanded in radians)
        if degrees:
            velocity = velocity * DEG2RAD
            kd = kd * DEG2RAD

        velocity = velocity * self.invert

        self.data.commanded_torque = 0
        self.data.commanded_velocity = velocity
        self.data.commanded_position = 0
        self.data.kp = 0
        self.data.kd = kd
        _packed_message = tmd._pack_motor_message(
            pos=0, vel=velocity, kp=0, kd=kd, t=0,
            motor=self.data
        )
        self._bus.send(_packed_message)

    def set_control(self, torque: float, velocity: float, kp: float, kd: float, degrees: bool = False) -> None:
        """Uses the built in capability to simultaneously use torque, as well as position and velocity control. It is highly recommended you consult
        the appropriate documentation for the motor controller to understand how to properly use this function, and it is likely in most scenarios direct control through
        ``set_torque``, ``set_position``, and ``set_velocity`` will be more appropriate. For the TMotors, you can find this diagram in the AK series manual.
        """
        raise NotImplementedError("Control mode not implemented for TMotors")
        
    def get_data(self) -> MotorData:
        """Returns the current data of the motor

        Returns:
            MotorData: Data from the actuator. Contains up-to-date information from the actuator as of the last time a message was sent to the actuator.
        """

        data = self.data
        data.current_position *= self.invert
        data.current_velocity *= self.invert
        data.current_torque *= self.invert

        return data

    def get_torque(self) -> float:
        """Returns the current torque of the motor in Newton-meters. Functionally equivalent to or ``get_data().current_torque``.

        Returns:
            float: The current torque of the motor in Newton-meters.
        """
        return self.data.current_torque * self.invert

    def get_position(self, degrees: bool = False) -> float:
        """Returns the current position of the motor in radians. Functionally equivalent to or ``get_data().current_position``.

        Args:
            degrees (bool, optional): Whether to return the position in degrees or radians. Defaults to False.

        Returns:
            float: The current position of the motor in radians or degrees.
        """
        if degrees: return self.data.current_position * self.invert * RAD2DEG
        else: return self.data.current_position * self.invert

    def get_velocity(self, degrees: bool = False) -> float:
        """Returns the current velocity of the motor in radians per second. Functionally equivalent to ``get_data().current_velocity``.

        Args:
            degrees (bool, optional): Whether to return the velocity in degrees. Defaults to False.

        Returns:
            float: The current velocity of the motor in radians per second or degrees per second.
        """
        if degrees: return self.data.current_velocity * self.invert * RAD2DEG
        else: return self.data.current_velocity * self.invert

    def get_temperature(self) -> float:
        """Returns the current temperature of the motor in degrees Celsius. This is not currently implemented and will ALWAYS return 0 for T Motors.

        Returns:
            float: A dummy value of Zero. This does NOT refelect the actual temperature of the motor.
        """
        return 0

    def zero_encoder(self):
        """Zeros the encoder of the motor. This will set the current position of the motor to zero.
        """
        zer_encoder_msg = tmd._pack_zero_encoder_message(self.can_id)
        self._bus.send(zer_encoder_msg)

    def _enable(self) -> None:
        """Enables the motor
        """
        self._bus.send(tmd._pack_enter_motor_message(self.can_id))
        self._connection_established = True
        self.data.initialized = True

    def _disable(self) -> None:
        """Disables the motor
        """
        self._bus.send(tmd._pack_exit_motor_message(self.can_id))
        self._connection_established = False
        self.data.initialized = False

    def _set_zero_torque(self) -> None:
        """Sets the torque of the motor to zero
        """
        torque = 0.0
        self.data.commanded_torque = torque
        self.data.commanded_velocity = 0
        self.data.commanded_position = 0
        self.data.kp = 0
        self.data.kd = 0
        _packed_message = tmd._pack_motor_message(
            pos=0, vel=0, kp=0, kd=0, t=torque,
            motor=self.data
        )
        self._bus.send(_packed_message)
