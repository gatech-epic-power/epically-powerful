import can
import time
import sys
import numpy as np
from epicallypowerful.actuation.robstride.robstride_driver import *
from epicallypowerful.actuation.actuator_group import _load_can_drivers
import atexit

class RobstrideScanningListener(can.Listener):
    def __init__(self) -> None:
        super().__init__()

    def on_message_received(self, msg):
        print(msg)



class RobstrideConfigure():
    def __init__(self, max_can_id=127):
        _load_can_drivers()
        self._bus = can.Bus(channel='can0', bustype='socketcan', receive_own_messages=False)
        self.max_can_id = max_can_id
        self.available_devices = set()
        atexit.register(self._bus.shutdown)

    def scan(self):
        print(f"Starting scan from 1 up to id {self.max_can_id}")
        for i in range(1, self.max_can_id + 1):
            read_id_msg = create_read_device_id_message(i)
            self._bus.send(read_id_msg)
            msg = self._bus.recv(.01)
            if (msg is not None) and (not msg.is_error_frame):
                    unique_id, motor_id = parse_identity_response(msg)
                    # print(f"Found device with CAN ID {motor_id}, Unique ID {unique_id}")
                    self.available_devices.add(motor_id)
        print(f"Scan complete. Found {len(self.available_devices)} devices.")
        return list(self.available_devices)
   
    def change_id(self, target_id, goal_id):
        print(f"Changing ID From {target_id} to {goal_id}")
        msg = create_set_can_id_message(target_id, goal_id)
        self._bus.send(msg)
        resp = self._bus.recv(0.1)
        return resp

    def enable(self, target_id):
        print(f'Enabling motor id {target_id}')
        if (target_id is None): return
        # First go through and send the disable message to all devices we know of
        # Next, enable the target device. Then wait for a response, return if successful
        msg = create_enable_motion_message(target_id)
        self._bus.send(msg)
        resp = self._bus.recv(0.1)
        return resp
    
    def disable(self, target_id):
        print(f'Disabling motor id {target_id}')
        msg = create_disable_motion_message(target_id)
        self._bus.send(msg)
        resp = self._bus.recv(0.1)
        return resp


    def motion_command(self, target_id):
        # Send a motion command to the target device, the scanning listener will handle the response, and its internal state will be updated

        # The GUI will periodically check the listener state to update the UI.
        pass
