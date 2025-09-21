from epicallypowerful.actuation.actuator_abc import Actuator
from epicallypowerful.actuation.tmotor import TMotor
from epicallypowerful.actuation.tmotor import TMotorServo
from epicallypowerful.actuation.robstride import Robstride
from epicallypowerful.actuation.cybergear import Cybergear
from epicallypowerful.actuation.motor_data import MotorData, t_motors, cybergears, robstrides
import can
from can import CanOperationError
import time
import signal
import os
import sys
import logging
from typing_extensions import Self, Optional
import platform
import functools
from typing import Callable

# ~~~~~ Logging Setup ~~~~~ #
motorlog = logging.getLogger('motorlog')
fh = logging.FileHandler('motorlog.log')
# fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
motorlog.addHandler(fh)

def _load_can_drivers() -> None:
    """Loads and unload the can drivers, then reloads to ensure fresh driver initialization
    This will load the CAN drivers, but then remove them and load them again...
    Trust the process. Loading them alone will not reset the can drivers.
    If they are not reset, the buffer can fill up due to errors and the buffer
    will not properly reset."""

    dev_uname = platform.uname()
    if 'aarch64' in dev_uname.machine.lower() and 'tegra' in dev_uname.release.lower():
        os.system('sudo modprobe can')
        os.system('sudo modprobe can_raw')
        os.system('sudo modprobe mttcan')

        os.system('sudo /sbin/ip link set can0 down')
        os.system('sudo rmmod can_raw')
        os.system('sudo rmmod can')
        os.system('sudo rmmod mttcan')

        os.system('sudo modprobe can')
        os.system('sudo modprobe can_raw')
        os.system('sudo modprobe mttcan')

        os.system('sudo /sbin/ip link set can0 down')
        os.system('sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000')

    elif 'aarch64' in dev_uname.machine.lower() and ('rpi' in dev_uname.release.lower() or 'raspi' in dev_uname.release.lower() or 'bcm' in dev_uname.release.lower()):
        os.system('sudo /sbin/ip link set can0 down')
        os.system('sudo /sbin/ip link set can0 txqueuelen 1000 up type can bitrate 1000000')


class ActuatorGroup():
    """Controls a group of actuators, which can all have different types (TMotor, Robstride, Cybergear, etc.). You can mix and match different AK Series actuators, as well as Robstride actuators in the same group.


    To control the actuators, you can use the :py:meth:`set_torque`, :py:meth:`set_position`, and :py:meth:`set_velocity` methods by bracket indexing the ActuatorGroup object witht he CAN ID as the key, or
    you can use the AcutorGroups corresponding method with the motor id as the first argument.

    To get data from the actuators, a similar approach can be used. In this case the :py:meth:`get_data`, :py:meth:`get_torque`, :py:meth:`get_position`, and :py:meth:`get_velocity` methods are available. A :py:meth:`get_temperature` method is also available for the Robstrides, and will always return 0 for the TMotors.

    Please see the :py:class:`~epicallypowerful.actuation.TMotor` and :py:class:`~epicallypowerful.actuation.Robstride` classes for more information on the methods available for each actuator and specific relevant details.

    You can also create an ActuatorGroup from a dictionary, where the key is the CAN ID and the value is the actuator type.

    For a list of all supported actuator types, you can import and use the :py:func:`epicallypowerful.actuation.available_actuator_types` function.
    
    Example:
        .. code-block:: python


            from epicallypowerful.actuation import ActuatorGroup, TMotor, Robstride

            ### Instantiation ---
            actuators = ActuatorGroup([TMotor(1, 'AK80-9'), Robstride(2, 'Cybergear'), Robstride(3, 'RS02')])
            # OR
            actuators = ActuatorGroup.from_dict({
                1: 'AK80-9',
                2: 'CyberGear',
                3: 'RS02'
            })

            ### Control ---
            actuators.set_torque(1, 0.5)
            actuators.set_position(2, 0, 0.5, 0.1, 0.1, degrees=True)

            ### Data ---
            print(actuators.get_torque(1))
            print(actuators.get_position(2))
            print(actuators.get_temperature(3))

    Args:
        actuators (list[Actuator]): A list of the actuators to control
        can_args (Optional[dict], optional): A dictionary of arguments to be passed to the :py:class:`can.Bus` object.
            This is only needed if your system does not use SocketCAN as described in the tutorials. Defaults to None.
        enable_on_startup (bool, optional): Whether to attempt to enable the actuators when the object is created. If set False, :py:func:`enable_actuators` needs to be called before any other commands. Defaults to True.

    """
    def __init__(self,
        actuators: list[Actuator],
        can_args: Optional[dict] = None,
        enable_on_startup: bool = True,
        exit_manually: bool = False
    ) -> None:
        _load_can_drivers()
        if can_args is None: can_args = {'bustype': 'socketcan', 'channel': 'can0'}
        self.bus = can.Bus(channel=can_args['channel'], bustype=can_args['bustype'])
        self.notifier = can.Notifier(self.bus, [])

        self.actuators = {}
        # Add all the actuators to the dictionary where the key is the CAN ID, and set the bus to the same bus as the ActuatorGroup
        for actuator in actuators:
            if actuator.can_id in self.actuators:
                self.bus.shutdown()
                raise ValueError(f"Duplicate CAN ID: {actuator.can_id}")
            if not isinstance(actuator, Actuator):
                self.bus.shutdown()
                raise ValueError(f"Invalid actuator type: {type(actuator)}")

            actuator._bus = self.bus
            self.actuators[actuator.can_id] = actuator
            self.notifier.add_listener(actuator)

        self._actuators_enabled = False
        self._priming_reconnection = False
        self._reconnection_start_time = 0
        self.prev_command_time = time.perf_counter()
        
        if not exit_manually:
            signal.signal(signal.SIGINT, self._exit_gracefully)
            signal.signal(signal.SIGTERM, self._exit_gracefully)

        time.sleep(0.1)
        if enable_on_startup: self.enable_actuators()

    def _guard_connection(func: Callable) -> Callable: # Guard connection decorator, will check if all motors are disconnected from the bus
            @functools.wraps(func)
            def wrapper(self, *args, **kw):
                self.prev_command_time = time.perf_counter()
                if self._actuators_enabled == False and not self._priming_reconnection:
                    try:
                        print(f'\rNo actuators detected or actuators not enabled, please check all connections/emergency stop.', end="")
                        self.enable_actuators()
                    except CanOperationError as e:
                        self._actuators_enabled = False
                    else:
                        self._priming_reconnection = True
                        self._reconnection_start_time = time.perf_counter()
                        print(f'\nActuator detected')
                    return
                if self._priming_reconnection == True:
                    print(f'\rPreparing to reconnect to actuators - Operating loop frequency will likely be unstable.', end="")
                    if time.perf_counter() - self._reconnection_start_time >= 0.5:
                        self._priming_reconnection = False
                        self.enable_actuators()
                        print(f'\nReestablished connection to actuators')
                    return

                try:
                    res = func(self, *args, **kw)
                except CanOperationError as e:
                    self._actuators_enabled = False
                    for ids, acts in self.actuators.items():
                        acts.data.responding = False
                    print(f'\rNo actuators detected or actuators not enabled, please check all connections/emergency stop.', end="")
                    return
                return res
            return wrapper

    def enable_actuators(self) -> None:
        """Enables control of the actuators. This will send the appropriate enable command and set torques to zero.
        """
        for can_id, actuator in self.actuators.items():
            actuator._enable()
            time.sleep(0.01)
            actuator._set_zero_torque()

        time.sleep(0.5)
        self._actuators_enabled = True

    def disable_actuators(self) -> None:
        """Disables control of the actuators. This will set the torque to 0 and disable the motors.
        """
        for can_id, actuator in self.actuators.items():
            actuator._set_zero_torque()
            actuator._disable()
            time.sleep(0.05)

        time.sleep(0.1)
        self._actuators_enabled = False

    @_guard_connection
    def set_torque(self, can_id: int, torque: float) -> int:
        """Sets the torque of the actuator with the given CAN ID.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.
            torque (float): Torque to set the actuator to in Newton-meters.
        """
        if self.actuators[can_id].call_response_latency() > 0.25:
            motorlog.error(f'Latency for motor {can_id} is too high, skipping command and attempting to enable')
            self.actuators[can_id].data.responding = False
            self.actuators[can_id].data.last_command_time = time.perf_counter()
            self.actuators[can_id]._enable()
            return -1

        self.actuators[can_id].data.last_command_time = time.perf_counter()
        self.actuators[can_id].set_torque(torque)
        self.actuators[can_id].data.responding = True
        return 1

    @_guard_connection
    def set_position(self, can_id: int, position: float, kp: float, kd: float, degrees: bool = False) -> int:
        """Sets the position of the actuator with the given CAN ID.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.
            position (float): Position to set the actuator to in radians or degrees depending on the ``degrees`` argument.
            kp (float): Set the proportional gain (stiffness) of the actuator in Newton-meters per radian.
            kd (float): Set the derivative gain (damping) of the actuator in Newton-meters per radian per second.
            degrees (bool): Whether the position is in degrees or radians.
        """
        if self.actuators[can_id].call_response_latency() > 0.25:
            motorlog.error(f'Latency for motor {can_id} is too high, skipping command and attempting to enable')
            self.actuators[can_id].data.responding = False
            self.actuators[can_id].data.last_command_time = time.perf_counter()
            self.actuators[can_id]._enable()
            return -1

        self.actuators[can_id].data.last_command_time = time.perf_counter()
        self.actuators[can_id].set_position(position, kp, kd, degrees)
        self.actuators[can_id].data.responding = True
        return 1

    @_guard_connection
    def set_velocity(self, can_id: int, velocity: float, kd: float, degrees: bool = False) -> int:
        """Sets the velocity of the actuator with the given CAN ID.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.
            velocity (float): Velocity to set the actuator to in radians per second or degrees per second depending on the ``degrees`` argument.
            kd (float): Set the derivative gain (damping) of the actuator in Newton-meters per radian per second.
            degrees (bool): Whether the velocity is in degrees per second or radians per second.
        """
        if self.actuators[can_id].call_response_latency() > 0.25:
            motorlog.error(f'Latency for motor {can_id} is too high, skipping command and attempting to enable')
            self.actuators[can_id].data.responding = False
            self.actuators[can_id].data.last_command_time = time.perf_counter()
            self.actuators[can_id]._enable()
            return -1

        self.actuators[can_id].data.last_command_time = time.perf_counter()
        self.actuators[can_id].set_velocity(velocity, kd, degrees)
        self.actuators[can_id].data.responding = True
        return 1

    def is_connected(self, can_id: int) -> bool:
        return self.actuators[can_id].data.responding

    def zero_encoder(self, can_id: int) -> None:
        """Zeros the encoder of the actuator with the given CAN ID.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.
        """
        self.actuators[can_id].zero_encoder()

    def get_data(self, can_id: int) -> MotorData:
        """Returns the data from the actuator with the given CAN ID

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.

        Returns:
            MotorData: Data from the actuator. Contains most up-to-date information from the actuator.
        """
        return self.actuators[can_id].get_data()

    def get_torque(self, can_id: int) -> float:
        """Returns the torque from the actuator with the given CAN ID. Functionally equivalent to ``get_data(can_id).current_torque``.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.

        Returns:
            float: Torque from the actuator in Newton-meters.
        """
        return self.actuators[can_id].get_torque()

    def get_position(self, can_id: int, degrees: bool = False) -> float:
        """Returns the position from the actuator with the given CAN ID. Functionally equivalent to ``actuators.get_data(can_id).current_position``.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.

        Returns:
            float: Position from the actuator in radians.
        """
        return self.actuators[can_id].get_position(degrees = degrees)

    def get_velocity(self, can_id: int, degrees: bool = False) -> float:
        """Returns the velocity from the actuator with the given CAN ID. Functionally equivalent to ``actuators.get_data(can_id).current_velocity``.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.

        Returns:
            float: Position from the actuator in radians.
        """
        return self.actuators[can_id].get_velocity(degrees = degrees)

    def get_temperature(self, can_id: int) -> float:
        """Returns the temperature from the actuator with the given CAN ID. Functionally equivalent to ``actuators.get_data(can_id).temperature``.

        Args:
            can_id (int): CAN ID of the actuator. This should be set by the appropriate manufacturer software.

        Returns:
            float: Temperature from the actuator in degrees Celsius.
        """
        return self.actuators[can_id].get_temperature()

    @classmethod
    def from_dict(cls: Self, actuators: dict[int, str], invert: list=[], enable_on_startup:bool = True, can_args: dict[str,str]=None) -> Self:
        """Creates an ActuatorGroup from a dictionary where the key is the CAN ID and the value is the actuator type.
        For TMotors, you can append "-servo" to the actuator type to create a TMotorServo instead of a TMotor. This controls the device in "servo mode"
        which can allow for higher output torques as direct current control can be used. Please see the :py:class:`~epicallypowerful.actuation.TMotorServo` class for more information.

        Example:
            .. code-block:: python


                actuators = ActuatorGroup.from_dict({ 0x1: 'AK80-9', 0x2: 'AK70-10' })

        Args:
            actuators (dict[int, str]): A dictionary where the key is the CAN ID and the value is the actuator type.
            can_args (dict[str,str], optional): Arguments to provide to the ``can.Bus`` object. Defaults to None.

        Raises:
            ValueError: If the actuator type is not recognized or supported.

        Returns:
            ActuatorGroup: An ActuatorGroup object with the actuators from the dictionary.
        """

        tmotor_types = t_motors()
        robstride_types = robstrides()
        act_list = []
        for a in actuators.keys():
            if "-servo" in actuators[a].lower():
                servomode = True
                actuators[a] = actuators[a].replace("-servo", "")
            else:
                servomode = False
            if a in invert:
                inv = True
            else:
                inv = False
            if actuators[a] in tmotor_types:
                if (servomode):
                    act_list.append(TMotorServo(a, actuators[a], invert=inv))
                else:
                    act_list.append(TMotor(a, actuators[a], invert=inv))
            elif actuators[a] in robstride_types:
                if servomode:
                    raise ValueError(f"Robstride motors do not support servo mode: {actuators[a]}")
                act_list.append(Robstride(a, actuators[a], invert=inv))
            else:
                raise ValueError(f"Invalid actuator type: {actuators[a]}")

        return cls(actuators=act_list, can_args=can_args, enable_on_startup=enable_on_startup)

    def __getitem__(self, idx: int) -> Actuator:
        """Returns the actuator with the given CAN ID. This method is better used for bracket indexing the ActuatorGroup object.

        Example:
            .. code-block:: python


                # ... Create the ActuatorGroup object ...
                actuators[0x1].set_torque(0.5)

                actuator_one = actuators[0x1]

                print(actuators[0x1].get_torque())

        Args:
            idx (int): CAN ID of the actuator

        Returns:
            Actuator: The actuator with the given CAN ID
        """
        return self.actuators[idx]

    def _exit_gracefully(self, signum, frame) -> None:
        """Exits the program gracefully. This will disable the motors and shutdown the CAN bus.

        Args:
            signum (_type_): _description_
            frame (_type_): _description_
        """
        os.write(sys.stdout.fileno(), b"Exiting gracefully\n")
        if self._actuators_enabled:
            try:
                self.disable_actuators()
            except:
                sys.exit("Failed to disable motors, please ensure power is safely disconnected\n")
            finally:
                self.notifier.stop()
                self.bus.shutdown()
        os.write(sys.stdout.fileno(), b"Shutdown finished\n")
        sys.exit(0)



if __name__ == '__main__':
    acts = ActuatorGroup([Robstride(2, 'Cybergear'), Robstride(1, 'RS02'), TMotor(3, 'AK80-9')])
    import time
    while True:
        res1 = acts.set_torque(1, 0.0)
        res2 = acts.set_torque(2, 0.0)
        res3 = acts.set_torque(3, 0.0)
        print(acts.is_connected(1), acts.is_connected(2), acts.is_connected(3))
        time.sleep(0.005)






