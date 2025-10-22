from epicallypowerful.actuation import ActuatorGroup
from epicallypowerful.toolbox import LoopTimer, DataRecorder
import time

AK80_9 = 'AK80-9'

# frequency_steps = [50, 100, 200, 400, 1000, 1600, 2000, 4000, 9000]

min_f = 50
max_f = 9000

converged = False

events = []
motors = ActuatorGroup.from_dict({
            # 1:AK80_9,
            # 3:AK80_9,
            # 2:AK80_9,
            5:AK80_9,
            # 5:AK80_9,
            # 6:AK80_9,
            # 7:AK80_9,
            # 8:AK80_9,
        })


RUNNING_TIME = 300

freq = 3965
t0 = time.perf_counter()
loop = LoopTimer(freq)
failure_occured = False
while time.perf_counter() - t0 < RUNNING_TIME:
    if loop.continue_loop():
        # Set torque to get a response
        # motors.set_torque(3, 0)
        # motors.set_torque(2, 0)
        motors.set_torque(5, 0)
        # motors.set_torque(1, 0)
        # motors.set_torque(7, 0)
        # motors.set_torque(6, 0)
        # motors.set_torque(5, 0)
        # motors.set_torque(8, 0)

        # Collect Data
        # d1 = motors.get_data(1)
        # d3 = motors.get_data(3)
        # d5 = motors.get_data(5)
        # d2 = motors.get_data(2)
        d4 = motors.get_data(5)
        # d8 = motors.get_data(8)
        # d7 = motors.get_data(7)
        # d6 = motors.get_data(6)

        # print(d2.current_position, d3.current_position, d4.current_position, d5.current_position, d6.current_position, d7.current_position, d8.current_position)
        if time.perf_counter() - t0 > 10:
            for i in [5]:
                if not motors.is_connected(i):
                    failure_occured = True
                    print(f'{i} not connected')
        if failure_occured:
            print(f'Failure at {freq}')
            print(time.perf_counter() - t0)
            break

