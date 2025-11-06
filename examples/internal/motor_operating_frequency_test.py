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
            1:AK80_9,
            3:AK80_9,
            2:AK80_9,
            4:AK80_9,
            5:AK80_9,
            6:AK80_9,
            7:AK80_9,
            8:AK80_9,
        })


RUNNING_TIME = 60

while not converged:
    freq = (min_f + max_f)/2
    # freq = 200
    print(f'Running at {freq} Hz')
    loop = LoopTimer(freq)
    t0 = time.perf_counter()
    run_events = ""
    failure_occured = False
    while time.perf_counter() - t0 < RUNNING_TIME:
        if loop.continue_loop():
            # Set torque to get a response
            motors.set_torque(3, 0)
            motors.set_torque(2, 0)
            motors.set_torque(4, 0)
            motors.set_torque(1, 0)
            motors.set_torque(7, 0)
            motors.set_torque(6, 0)
            motors.set_torque(5, 0)
            motors.set_torque(8, 0)

            # Collect Data
            d1 = motors.get_data(1)
            d3 = motors.get_data(3)
            d5 = motors.get_data(5)
            d2 = motors.get_data(2)
            d4 = motors.get_data(4)
            d8 = motors.get_data(8)
            d7 = motors.get_data(7)
            d6 = motors.get_data(6)
            # print(d3.current_position)
            # print(d5.current_position, d3.current_position, d2.current_position, d4.current_position, d8.current_position, d1.current_position, d7.current_position)
            if time.perf_counter() - t0 > 10:
                for i in [1, 2, 3, 4, 5, 8]:
                    if not motors.is_connected(i):
                        run_events += f"\nm:{i} disconnected"
                        print(run_events)
                        failure_occured = True
            if failure_occured:
                print(f'Failure at {freq}')
                break
    if failure_occured:
        max_f = freq
    else:
        min_f = freq


    if max_f - min_f < 100:
        converged = True

print(f'Found {min_f} Hz as max operating rate')

