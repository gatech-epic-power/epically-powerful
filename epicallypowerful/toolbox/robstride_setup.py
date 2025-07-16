import can
import time
import sys
import numpy as np
from epicallypowerful.actuation.robstride.robstride_driver import *
from epicallypowerful.actuation.actuator_group import _load_can_drivers

class RobstrideScanningListener(can.Listener):
    def __init__(self) -> None:
        super().__init__()

    def on_message_received(self, msg):
        pass



class RobstrideConfigure(can.Listener):
    def __init__(self, max_can_id=127):
        self._bus = can.Bus(channel='can0', bustype='socketcan', receive_own_messages=False)
        self.max_can_id = max_can_id
        self.available_devices = set()

    def scan(self):
        print(f"Starting scan from 1 up to id {self.max_can_id}")
        for i in range(1, self.max_can_id + 1):
            enable_msg = create_enable_motion_message(i)
            self._bus.send(enable_msg)
            msg = self.bus.recv(.1)
            if (msg is not None) and (not msg.is_error_frame):
                    unique_identity, motor_id = parse_identity_response(msg)
                    print(f"Found device with CAN ID {motor_id}, Unique ID {unique_identity}")
                    self.available_devices.add(motor_id)
        print(f"Scan complete. Found {len(self.available_devices)} devices.")
        return list(self.available_devices)
    
    def enable(self, target_id):
        # First go through and send the disable message to all devices we know of

        # Next, enable the target device. Then wait for a response, return if successful
        pass

    def motion_command(self, target_id):
        # Send a motion command to the target device, the scanning listener will handle the response, and its internal state will be updated

        # The GUI will periodically check the listener state to update the UI.
        pass