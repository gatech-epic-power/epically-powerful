import argparse

def _rpi_or_jetson():
    import platform
    machine_name = platform.uname().release.lower()
    if "tegra" in machine_name:
        return "jetson"
    elif "rpi" in machine_name or "bcm" in machine_name or "raspi" in machine_name:
        return "rpi"

def _collect_microstrain_imu_data_parser():
    parser = argparse.ArgumentParser(
        prog="collect_microstrain_imu_data",
        description="Collect MicroStrain IMU data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--imu-serial-id", '-id',
        nargs='+',
        required=True,
        type=str,
        help="IMU serial ID multiple can be specified",
    )
    parser.add_argument(
        "--output", '-o',
        default="output.csv",
        help="Output file",
    )
    parser.add_argument(
        "--duration", '-d',
        default=30,
        type=int,
        help="Duration in seconds",
    )
    parser.add_argument(
        "--channels", '-c',
        choices=["acc", "gyro", "mag", "quat", "eul"],
        type=str,
        nargs="+",
        default=["acc", "gyro"],
        help="Types of data to collect",
    )
    parser.add_argument(
        "--remote-sync-channel", '-r',
        type=int,
        action="append",
        help="GPIO pins to use for remote sync channels. Use this argument multiple times to specify multiple channels",
    )
    return parser

def collect_microstrain_imu_data():
    """Run with command-line shortcut `ep-collect-imu-data` [ARGS]."""
    parser = _collect_microstrain_imu_data_parser()
    args = parser.parse_args()
    print(f"output name: {args.output}")
    print(f"MicroStrain serial IDs: {args.imu_serial_id}") # This is a list
    print(f"Duration of trial: {args.duration} seconds")
    print(f"IMU channels: {args.channels}")
    print(f"Remote sync GPIO pin channel: {args.remote_sync_channel}")

    outfile = args.output
    duration = args.duration
    serial_ids = args.imu_serial_id
    channels = args.channels
    remote_sync_channels = args.remote_sync_channel

    from epicallypowerful.sensing.microstrain.microstrain_imu import MicroStrainIMUs
    from epicallypowerful.toolbox.clocking import timed_loop
    from epicallypowerful.toolbox.data_recorder import DataRecorder

    imus = MicroStrainIMUs(serial_ids)

    headers = []
    for serial_id in serial_ids:
        if "acc" in channels:
            headers.extend([
                f"{serial_id}_acc_x",
                f"{serial_id}_acc_y",
                f"{serial_id}_acc_z",
            ])
        if "gyro" in channels:
            headers.extend([
                f"{serial_id}_gyro_x",
                f"{serial_id}_gyro_y",
                f"{serial_id}_gyro_z",
            ])
        if "mag" in channels:
            headers.extend([
                f"{serial_id}_mag_x",
                f"{serial_id}_mag_y",
                f"{serial_id}_mag_z",
            ])
        if "orient" in channels:
            headers.extend([
                f"{serial_id}_quat_w",
                f"{serial_id}_quat_x",
                f"{serial_id}_quat_y",
                f"{serial_id}_quat_z",
            ])
        if "euler" in channels:
            headers.extend([
                f"{serial_id}_eul_x",
                f"{serial_id}_eul_y",
                f"{serial_id}_eul_z",
            ])

    if remote_sync_channels != []:
        if _rpi_or_jetson() == "rpi":
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
        elif _rpi_or_jetson() == "jetson":
            import Jetson.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
        else:
            raise NotImplementedError("This platform does not support GPIO, please utilize a Raspberry Pi or Jetson or other compatible platform")
        for c in remote_sync_channels:
            headers.append(f"sync_{c}")
            GPIO.setup(c, GPIO.IN)

    recorder = DataRecorder(
        outfile, headers,
        delimiter=",",
        overwrite=False,
        buffer_limit=duration*200
    ) # Data is collected at 200Hz, and data is not saved until file is manually closed

    print(f"\nCollecting data for {duration} seconds...")
    for _ in timed_loop(200, duration):
        row_data = []
        for serial_id in serial_ids:
            data = imus.get_data(serial_id)
            if "acc" in channels:
                row_data.extend([
                    data.acc_x,
                    data.acc_y,
                    data.acc_z,
                ])
            if "gyro" in channels:
                row_data.extend([
                    data.gyro_x,
                    data.gyro_y,
                    data.gyro_z,
                ])
            if "mag" in channels:
                row_data.extend([
                    data.mag_x,
                    data.mag_y,
                    data.mag_z,
                ])
            if "quat" in channels:
                row_data.extend([
                    data.quat_w,
                    data.quat_x,
                    data.quat_y,
                    data.quat_z,
                ])
            if "eul" in channels:
                row_data.extend([
                    data.eul_x,
                    data.eul_y,
                    data.eul_z,
                ])
        if remote_sync_channels != []:
            for c in remote_sync_channels:
                row_data.append(GPIO.input(c))
        recorder.save(row_data)

    # Finalize the data saving
    print("Saving data, do not power off device...")
    recorder.finalize()
    print(f'Data saved to {outfile}')
    return 1

def _visualize_dummy_data_parser():
    parser = argparse.ArgumentParser(
        description="Run dummy visualizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ip-address", '-ip',
        required=True,
        type=str,
        help="UDP server IP address",
    )
    parser.add_argument(
        "--port", '-p',
        required=True,
        type=int,
        default=5556,
        help="UDP server port",
    )
    return parser

def visualize_dummy_data():
    """Run with command-line shortcut `ep-dummy-viz [ARGS]`."""
    parser = _visualize_dummy_data_parser()

    args = parser.parse_args()
    udp_server_ip_address = args.ip_address
    port = args.port

    print(f"\nPublishing viz. messages on UDP server with IP address {udp_server_ip_address} on port {port}")

    import sys
    import time
    import math
    from epicallypowerful.toolbox.visualization import PlotJugglerUDPClient
    
    # Initialize visualizer instance
    pj_client = PlotJugglerUDPClient(addr=udp_server_ip_address, port=port)

    # Populate test data for publishing
    t0 = time.time()
    test_data = {
        'example_data': {
            'sine': math.sin(time.time()),
            'cosine': math.cos(time.time())
        },
        'timestamp': time.time() - t0
    }

    print('\n\n')

    # Continuously publish dummy data
    while True:
        time.sleep(0.033)
        test_data = {
            'example_data': {
                'sine': math.sin(time.time()),
                'cosine': math.cos(time.time())
            },
            'timestamp': time.time() - t0
        }

        # Send data to UDP server
        pj_client.send(test_data)

        print('\033[A\033[A\033[A')
        print(f'| Time (s) |  Sine  | Cosine |')
        print(f"| {test_data['timestamp']:^8.2f} | {test_data['example_data']['sine']:^6.2f} | {test_data['example_data']['cosine']:^6.2f} |")

def _stream_microstrain_imu_data_parser():
    parser = argparse.ArgumentParser(
        description="Stream MicroStrain IMU data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--imu-serial-id", '-id',
        nargs='+',
        required=True,
        type=str,
        help="IMU serial ID (multiple can be specified and separated by comma)",
    )
    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=int,
        default=200,
        help="Operating frequency [Hz]",
    )
    return parser

def stream_microstrain_imu_data():
    """Run with command-line shortcut `ep-stream-microstrain-imu [ARGS]`."""
    parser = _stream_microstrain_imu_data_parser()
    args = parser.parse_args()
    serial_ids = args.imu_serial_id[0] # This is a list
    serial_ids = [str(s) for s in serial_ids.replace(" ", "").split(',')]
    print(f"Using IMU(s) with IDs {serial_ids}")
    rate = int(args.rate) # This is an int [Hz]
    
    from epicallypowerful.sensing.microstrain.microstrain_imu import MicroStrainIMUs
    from epicallypowerful.toolbox.clocking import TimedLoop

    # Set clocking loop specifications
    clocking_loop = TimedLoop(rate)
    
    # Change IMU operation options (each one has a default)
    microstrain_imu_freq = rate # Set collection rate of IMUs
    tare_on_startup = False # Zero orientation on startup?
    
    # Instantiate instance of MicroStrain IMU manager
    microstrain_imus = MicroStrainIMUs(
        imu_ids=serial_ids,
        rate=microstrain_imu_freq,
        tare_on_startup=tare_on_startup,
        verbose=False,
    )
    
    # Main loop
    print("\n")

    # Continuously stream data
    try:
        while clocking_loop():
            print('\033[A\033[A\033[A')
            print(f'| IMU addr. | Acc. (x) m*s^-2 | Acc. (y) m*s^-2 | Acc. (z) m*s^-2 |')

            # Iterate through all connected IMUs
            for imu_id in serial_ids:
                # Acceleration in x, y, z direction
                ms_data = microstrain_imus.get_data(imu_id)
                print(f"| {int(imu_id):^9} | {ms_data.acc_x:^15.2f} | {ms_data.acc_y:^15.2f} | {ms_data.acc_z:^15.2f} |")

    except KeyboardInterrupt:
        print("\nClosing MicroStrain IMUs.")

def _stream_mpu9250_imu_data_parser():
    parser = argparse.ArgumentParser(
        description="Stream MPU9250 IMU data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=float,
        default=250,
        help="Operating frequency [Hz]. Defaults to 250 Hz",
    )
    parser.add_argument(
        "--i2c-bus",
        type=int,
        default=None,
        help="Which I2C bus the sensor is on (e.g., --i2c-bus 7). Defaults to 7 for NVIDIA Jetson Orin Nano or 1 for Raspberry Pi",
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=-1,
        help="(If using multiplexer) channel sensor is on (e.g., --channel 1). Defaults to -1 (no multiplexer)",
    )
    parser.add_argument(
        "--address",
        type=int,
        default=68,
        help="I2C address of MPU9250 sensor (e.g., --address 68). Defaults to 68",
    )
    return parser

def stream_mpu9250_imu_data():
    """Run with command-line shortcut `ep-stream-mpu9250-imu [ARGS]`."""
    if _rpi_or_jetson() == "rpi":
        DEFAULT_I2C_BUS = 1
    elif _rpi_or_jetson() == "jetson":
        DEFAULT_I2C_BUS = 7
    else:
        DEFAULT_I2C_BUS = 0

    parser = _stream_mpu9250_imu_data_parser()
        
    args = parser.parse_args()
    bus = args.i2c_bus

    if args.i2c_bus is not None:
        bus = args.i2c_bus
    else:
        bus = DEFAULT_I2C_BUS

    channel = args.channel
    address = int('0x'+str(args.address), 0) # Convert multi-digit address into hex, then int
    rate = int(args.rate) # This is an int [Hz]
    
    from epicallypowerful.sensing.mpu9250.mpu9250_imu import MPU9250IMUs
    from epicallypowerful.toolbox.clocking import TimedLoop

    # Set clocking loop specifications
    clocking_loop = TimedLoop(rate)
    
    # Change IMU operation options (each one has a default)
    mpu9250_imu_freq = rate # Set collection rate of IMUs
    tare_on_startup = False # Zero orientation on startup?

    # Set MPU9250 IMU IDs
    mpu9250_imu_ids = {
        0: {
            'bus': bus,        # 7 is the default I2C bus on the Jetson
            'channel': channel,   # channel is only used with a multiplexer. If not using one, keep as -1 (default)
            'address': address, # I2C address of the MPU9250. Can be either 0x68 or 0x69
        }
    }
    
    # Instantiate instance of MPU9250 IMU manager
    mpu9250_imus = MPU9250IMUs(
        imu_ids=mpu9250_imu_ids,
        components=['acc'],
        calibration_path='', # Just plot raw values, do not look for a calibration file
        verbose=True,
    )
    
    # Main loop
    print("\n")

    # Continuously stream data
    try:
        while clocking_loop():
            print('\033[A\033[A\033[A')
            print(f'| I2C bus | channel | I2C addr. | Acc. (x) m*s^-2 | Acc. (y) m*s^-2 | Acc. (z) m*s^-2 |')

            # Iterate through all connected IMUs
            for imu_id, connection in mpu9250_imu_ids.items():
                # Acceleration in x, y, z directions
                mpu_data = mpu9250_imus.get_data(imu_id)
                print(f"| {int(connection['bus']):^7} | {int(connection['channel']):^7} | {int(connection['address']):^9} | {mpu_data.acc_x:^15.2f} | {mpu_data.acc_y:^15.2f} | {mpu_data.acc_z:^15.2f} |")

    except KeyboardInterrupt:
        print("\nClosing MPU9250 IMUs.")


def _stream_open_imu_data():
    parser = argparse.ArgumentParser(
        description="Stream OpenIMU data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=float,
        default=100,
        help="Operating frequency [Hz]. Defaults to 100 Hz",
    )

    parser.add_argument(
        "--imu-can-id", '-id',
        type=str,
        required=True,
        default='128',
        help="OpenIMU CAN ID (multiple can be specified and separated by comma) (e.g., --imu-can-id 128)",
    )
    return parser


def stream_open_imu_data():
    """Run with command-line shortcut `ep-stream-open-imu [ARGS]`."""
    parser = _stream_open_imu_data()
    
    args = parser.parse_args()
    open_imu_ids = args.imu_can_id
    open_imu_ids = [int(s) for s in open_imu_ids.replace(" ", "").split(',')]
    rate = args.rate # This is an int [Hz]
    
    from epicallypowerful.sensing.open_imu.open_imu import OpenIMUs
    from epicallypowerful.toolbox.clocking import TimedLoop

    # Set clocking loop specifications
    clocking_loop = TimedLoop(rate)
    
    # Change IMU operation options (each one has a default)
    open_imu_freq = rate # Set collection rate of IMUs
    tare_on_startup = False # Zero orientation on startup?
    
    # Instantiate instance of MPU9250 IMU manager
    open_imus = OpenIMUs(
        imu_ids=open_imu_ids,
        components=['acc'],
        rate=open_imu_freq,
        verbose=True,
    )
    
    # Main loop
    print("\n")

    # Continuously stream data
    try:
        while clocking_loop():
            print('\033[A\033[A\033[A')
            print(f'| CAN ID | Acc. (x) m*s^-2 | Acc. (y) m*s^-2 | Acc. (z) m*s^-2 |')

            # Iterate through all connected IMUs
            for imu_id in open_imu_ids:
                # Acceleration in x, y, z directions
                oi_data = open_imus.get_data(imu_id)
                print(f'| {int(imu_id):^6} | {oi_data.acc_x:^15.2f} | {oi_data.acc_y:^15.2f} | {oi_data.acc_z:^15.2f} |')

    except KeyboardInterrupt:
        open_imus._close_loop_resources()
        print("\nClosing OpenIMUs.")


def _stream_actuator_data_parser():
    parser = argparse.ArgumentParser(
        description="Stream actuator data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=int,
        default=200,
        help="Operating frequency [Hz]",
    )
    parser.add_argument(
        "--actuator-type", '-at',
        required=True,
        type=str,
        help="Actuator type (see actuation.motor_data for possible types)",
    )
    parser.add_argument(
        "--actuator-id", '-ai',
        required=True,
        type=str,
        help="Actuator ID (CAN ID)",
    )
    return parser

def stream_actuator_data():
    """Run with command-line shortcut `ep-stream-actuator [ARGS]`."""
    parser = _stream_actuator_data_parser()

    args = parser.parse_args()
    rate = args.rate # This is an int [Hz]
    actuator_type = args.actuator_type
    actuator_ids = [int(s) for s in args.actuator_id.replace(" ","").split(',')]
    
    from epicallypowerful.actuation import ActuatorGroup
    from epicallypowerful.toolbox import TimedLoop
    
    # Set control loop frequency
    operating_freq = 200 # [Hz]
    clocking_loop = TimedLoop(rate=operating_freq)

    # Initialize actuator
    initialization_dict = {actuator_id:actuator_type for actuator_id in actuator_ids}

    # Initialize actuator object from dictionary
    actuators = ActuatorGroup.from_dict(initialization_dict)
    print("\n")

    # Run control loop at set frequency
    try:
        while clocking_loop():
            # Clear terminal output for each actuator's data
            clear_string = '\033[A\033[A' + len(actuator_ids) * '\033[A'
            print(clear_string)
            print(f'| Actuator | Position [rad] | Velocity [rad/s] | Torque [Nm] |')

            # Loop through all actuators and get position, velocity, torque
            for can_id in actuator_ids:
                actuators.set_torque(can_id, 0)
                act_data = actuators.get_data(can_id)
                print(f'| {int(can_id):^8} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')

    except KeyboardInterrupt:
        print("\nClosing actuators.")

def _impedance_control_actuator_parser():
    parser = argparse.ArgumentParser(
        description="Run impedance controller on an actuator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=int,
        default=200,
        help="Operating frequency [Hz]",
    )
    parser.add_argument(
        "--actuator-type", '-at',
        required=True,
        type=str,
        help="Actuator type (see actuation.motor_data for possible types)",
    )
    parser.add_argument(
        "--actuator-id", '-ai',
        required=True,
        type=int,
        help="Actuator ID (CAN ID)",
    )
    return parser

def impedance_control_actuator():
    """Run with command-line shortcut `ep-sample-impedance-ctrl [ARGS]`."""
    parser = _impedance_control_actuator_parser()
    args = parser.parse_args()
    rate = args.rate # This is an int [Hz]
    actuator_type = args.actuator_type
    actuator_id = int(args.actuator_id)

    from epicallypowerful.actuation import ActuatorGroup
    from epicallypowerful.toolbox import TimedLoop
    
    # Set control loop frequency
    operating_freq = 200 # [Hz]
    clocking_loop = TimedLoop(rate=operating_freq)

    # Initialize actuator
    initialization_dict = {actuator_id:actuator_type}

    # Initialize actuator object from dictionary
    actuators = ActuatorGroup.from_dict(initialization_dict)

    # Set controller parameters
    GAIN_KP = 2 # proportional gain
    GAIN_KD = 0.1 # derivative gain
    error_current = 0 # initialize, will change in loop
    prev_error = 0 # initialize, will change in loop
    position_desired = 0 # [rad]

    # Zero actuator encoder
    actuators.zero_encoder(actuator_id)
    print("\n")

    # Run control loop at set frequency
    while clocking_loop():
        print('\033[A\033[A\033[A')
        print(f'| Actuator | Position [rad] | Velocity [rad/s] | Torque [Nm] |')

        # Get data from actuator
        act_data = actuators.get_data(actuator_id)
        
        # Update position error
        position_current = actuators.get_position(can_id=actuator_id, degrees=False)
        prev_error = error_current
        error_current = position_desired - position_current
        errordot_right = (error_current - prev_error) / (1 / operating_freq)

        # Update torques
        torque_desired = GAIN_KP*error_current + GAIN_KD*errordot_right
        actuators.set_torque(can_id=actuator_id, torque=torque_desired)

        print(f'| {int(actuator_id):^5} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')

def _position_control_actuator_parser():
    parser = argparse.ArgumentParser(
        description="Run impedance-based position control on an actuator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=int,
        default=200,
        help="Operating frequency [Hz]",
    )
    parser.add_argument(
        "--actuator-type", '-at',
        required=True,
        type=str,
        help="Actuator type (see actuation.motor_data for possible types)",
    )
    parser.add_argument(
        "--actuator-id", '-ai',
        required=True,
        type=int,
        help="Actuator ID (CAN ID)",
    )
    return parser

def position_control_actuator():
    """Run with command-line shortcut `ep-sample-position-ctrl [ARGS]`."""
    parser = _position_control_actuator_parser()

    args = parser.parse_args()
    rate = args.rate # This is an int [Hz]
    actuator_type = args.actuator_type
    actuator_id = int(args.actuator_id)

    from epicallypowerful.actuation import ActuatorGroup
    from epicallypowerful.toolbox import TimedLoop
    import time # only necessary for sine position control implementation
    import math # only necessary for sine position control implementation
    
    # Set control loop frequency
    operating_freq = 200 # [Hz]
    clocking_loop = TimedLoop(rate=operating_freq)

    # Initialize actuator
    initialization_dict = {actuator_id:actuator_type}

    # Initialize actuator object from dictionary
    actuators = ActuatorGroup.from_dict(initialization_dict)

    # Set controller parameters
    GAIN_KP = 5 # proportional gain
    GAIN_KD = 0.25 # derivative gain
    rad_range = 3.14159 # Angular peak-to-peak sine wave range (rad) that controller will sweep
    error_current = 0 # initialize, will change in loop
    prev_error = 0 # initialize, will change in loop
    t0 = time.time()

    # Zero actuator encoder
    actuators.zero_encoder(actuator_id)
    print("\n")

    # Run control loop at set frequency
    while clocking_loop():
        print('\033[A\033[A\033[A')
        print(f'| Actuator | Position [rad] | Velocity [rad/s] | Torque [Nm] |')

        # Get data from actuator
        act_data = actuators.get_data(actuator_id)

        # Update desired position
        time_since_start = time.time() - t0
        position_desired = math.sin(time_since_start) * (rad_range / 2)
        
        # Update position error
        position_current = actuators.get_position(can_id=actuator_id, degrees=False)
        prev_error = error_current
        error_current = position_desired - position_current
        errordot_right = (error_current - prev_error) / (1 / operating_freq)

        # Update torques
        torque_desired = GAIN_KP*error_current + GAIN_KD*errordot_right
        actuators.set_torque(can_id=actuator_id, torque=torque_desired)

        print(f'| {int(actuator_id):^5} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')

def _position_control_actuator_with_visualizer_parser():
    parser = argparse.ArgumentParser(
        description="Run impedance-based position control on an actuator with visualization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rate", '-r',
        required=False,
        type=int,
        default=200,
        help="Operating frequency [Hz]",
    )
    parser.add_argument(
        "--actuator-type", '-at',
        required=True,
        type=str,
        help="Actuator type (see actuation.motor_data for possible types)",
    )
    parser.add_argument(
        "--actuator-id", '-ai',
        required=True,
        type=int,
        help="Actuator ID (CAN ID)",
    )
    parser.add_argument(
        "--ip-address", '-ip',
        required=True,
        type=str,
        help="UDP server IP address",
    )
    parser.add_argument(
        "--port", '-p',
        required=True,
        type=int,
        default=5556,
        help="UDP server port",
    )
    return parser

def position_control_actuator_with_visualizer():
    """Run with command-line shortcut `ep-sample-actuator-viz [ARGS]`."""
    parser = _position_control_actuator_with_visualizer_parser()

    args = parser.parse_args()
    rate = args.rate # This is an int [Hz]
    actuator_type = args.actuator_type
    actuator_id = int(args.actuator_id)
    udp_server_ip_address = args.ip_address
    port = args.port

    from epicallypowerful.actuation import ActuatorGroup
    from epicallypowerful.toolbox import TimedLoop
    from epicallypowerful.toolbox.visualization import PlotJugglerUDPClient
    import time # only necessary for sine position control implementation
    import math # only necessary for sine position control implementation
    
    # Set control loop frequency
    operating_freq = 200 # [Hz]
    clocking_loop = TimedLoop(rate=operating_freq)

    # Initialize actuator
    initialization_dict = {actuator_id:actuator_type}

    # Initialize actuator object from dictionary
    actuators = ActuatorGroup.from_dict(initialization_dict)

    # Initialize visualizer
    print(f"\nPublishing viz. messages on UDP server with IP address {udp_server_ip_address} on port {port}")

    # Initialize visualizer instance
    pj_client = PlotJugglerUDPClient(addr=udp_server_ip_address, port=port)
    viz_data = {
        'data': {
            'actuator_id': actuator_id,
            'position_desired': 0,
            'position_actual': 0,
            'error': 0,
            'error_dot': 0,
            'torque_desired': 0,
            'actuator_position': 0,
            'actuator_velocity': 0,
            'actuator_torque': 0,
        },
        'timestamp': time.time(),
    }
    pj_client.send(viz_data)

    # Set controller parameters
    GAIN_KP = 5 # proportional gain
    GAIN_KD = 0.25 # derivative gain
    rad_range = 3.14159 # Angular peak-to-peak sine wave range (rad) that controller will sweep
    error_current = 0 # initialize, will change in loop
    prev_error = 0 # initialize, will change in loop
    t0 = time.time()

    # Zero actuator encoder
    actuators.zero_encoder(actuator_id)
    print("\n")

    # Run control loop at set frequency
    while clocking_loop():
        print('\033[A\033[A\033[A')
        print(f'| Actuator | Position [rad] | Velocity [rad/s] | Torque [Nm] |')

        # Get data from actuator
        act_data = actuators.get_data(actuator_id)

        # Update desired position
        time_since_start = time.time() - t0
        position_desired = math.sin(time_since_start) * (rad_range / 2)
        
        # Update position error
        position_current = actuators.get_position(can_id=actuator_id, degrees=False)
        prev_error = error_current
        error_current = position_desired - position_current
        errordot_current = (error_current - prev_error) / (1 / operating_freq)

        # Update torques
        torque_desired = GAIN_KP*error_current + GAIN_KD*errordot_current
        actuators.set_torque(can_id=actuator_id, torque=torque_desired)

        print(f'| {int(actuator_id):^8} | {act_data.current_position:^14.2f} | {act_data.current_velocity:^16.2f} | {act_data.current_torque:^11.2f} |')

        # Send outputs for visualization
        viz_data = {
            'data': {
                'actuator_id': actuator_id,
                'position_desired': position_desired,
                'position_actual': position_current,
                'error': error_current,
                'error_dot': errordot_current,
                'torque_desired': torque_desired,
                'actuator_position': act_data.current_position,
                'actuator_velocity': act_data.current_velocity,
                'actuator_torque': act_data.current_torque,
            },
            'timestamp': time.time(),
        }
        pj_client.send(viz_data)

def _imu_control_actuator_parser():
    parser = argparse.ArgumentParser(
        description="Run actuator with IMU as controller input",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--imu-serial-id", '-id',
        nargs='+',
        required=True,
        type=str,
        help="IMU serial ID (multiple can be specified)",
    )
    parser.add_argument(
        "--rate", '-r',
        nargs='+',
        required=False,
        type=int,
        default=200,
        help="Operating frequency [Hz]",
    )
    parser.add_argument(
        "--actuator-type", '-at',
        required=True,
        type=str,
        help="Actuator type (see actuation.motor_data for possible types)",
    )
    parser.add_argument(
        "--actuator-id", '-ai',
        required=True,
        type=int,
        help="Actuator ID (CAN ID)",
    )
    return parser

def imu_control_actuator():
    """Run with command-line shortcut `ep-sample-imu-ctrl`."""
    parser = _imu_control_actuator_parser()

    args = parser.parse_args()
    serial_id = args.imu_serial_id[0] # This is a list
    serial_id = [str(s) for s in serial_id.replace(" ", "").split(',')]
    print(f"Using IMU(s) with IDs {serial_id}")
    rate = int(args.rate[0]) # This is an int [Hz]
    actuator_type = args.actuator_type
    actuator_id = int(args.actuator_id)

    from epicallypowerful.actuation import ActuatorGroup
    from epicallypowerful.toolbox import TimedLoop
    from epicallypowerful.sensing import MicroStrainIMUs

    # Set control loop frequency
    operating_freq = 200 # [Hz]
    clocking_loop = TimedLoop(rate=operating_freq)
    
    # Change IMU operation options (each one has a default)
    microstrain_imu_freq = rate # Set collection rate of IMUs
    tare_on_startup = False # Zero orientation on startup?

    # Instantiate instance of MicroStrain IMU manager
    microstrain_imus = MicroStrainIMUs(
        imu_ids=serial_id,
        rate=microstrain_imu_freq,
        tare_on_startup=tare_on_startup,
        verbose=False,
    )

    # Initialize actuator
    initialization_dict = {actuator_id:actuator_type}

    # Initialize actuator object from dictionary
    actuators = ActuatorGroup.from_dict(initialization_dict)

    # Set controller parameters
    GAIN_KP = 0.25 # proportional gain
    GAIN_KD = 0.01 # derivative gain
    gyro_current = 0 # initialize, will change in loop
    prev_error = 0 # initialize, will change in loop

    # Zero actuator encoder
    actuators.zero_encoder(actuator_id)
    print("\n")

    # Run control loop at set frequency
    while clocking_loop():
        print('\033[A\033[A\033[A')
        print(f'| Actuator | Torque [Nm] | IMU Addr. | Gyro (x) [rad/s] |')

        # Get data from actuator
        act_data = actuators.get_data(actuator_id)

        # Get MicroStrain IMU gyroscope values
        imu_data = microstrain_imus.get_data(serial_id[0])
        prev_error = gyro_current
        gyro_current = imu_data.gyro_x
        gyrodot_current = (gyro_current - prev_error) / (1 / operating_freq)

        # Update torques
        torque_desired = GAIN_KP*gyro_current + GAIN_KD*gyrodot_current
        actuators.set_torque(can_id=actuator_id, torque=torque_desired)

        # Print out updated results
        print(f'| {int(actuator_id):^8} | {act_data.current_torque:^11.2f} | {serial_id[0]:^9} | {imu_data.gyro_x:^16.2f} |')

def _install_mscl_python_parser():
    parser = argparse.ArgumentParser(
        description="Install MSCL Python package",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dir", '-d',
        type=str,
        default=None,
        help="Directory to install MSCL Python package. This will copy the package from the install directory to the specified directory",
    )
    parser.add_argument(
        "--to-env", '-E',
        action='store_true',
        default=False,
        help="Install MSCL Python package to the current Python environment as well as the system-wide Python environment. This is useful if you want to use the MSCL Python package in a virtual environment or a specific Python environment.",
    )
    return parser

def install_mscl_python():
    """Run with command-line shortcut `ep-install-mscl`."""
    import os
    import sys
    import argparse
    import shutil
    import glob

    CURRENT_VERSION = "67.1.0"

    parser = _install_mscl_python_parser()

    args = parser.parse_args()
    
    # Download the MSCL Python package from GitHub Release.
    pyversion = sys.version_info
    if pyversion.major != 3 or pyversion.minor < 8:
        raise RuntimeError("MSCL Python requires Python 3.8 or higher")
    res = os.system(f"wget https://github.com/LORD-MicroStrain/MSCL/releases/download/v{CURRENT_VERSION}/MSCL_arm64_Python{pyversion.major}.{pyversion.minor}_v{CURRENT_VERSION}.deb -O /tmp/MSCL_arm64_Python{pyversion.major}.{pyversion.minor}_v{CURRENT_VERSION}.deb")
    if res != 0:
        raise RuntimeError("Failed to download MSCL Python package")
    res = os.system(f"sudo apt install /tmp/MSCL_arm64_Python{pyversion.major}.{pyversion.minor}_v{CURRENT_VERSION}.deb")
    res2 = os.system(f"sudo apt install python3.{pyversion.minor}-dev")
    if res != 0:
        raise RuntimeError("Failed to install MSCL Python package")


    if args.dir is not None:
        # Copy the MSCL Python package to the specified directory
        res = os.system(f"cp -r /usr/local/python{pyversion.major}.{pyversion.minor}/dist-packages/*mscl* {parser.dir}")
        if res != 0:
            raise RuntimeError("Failed to copy MSCL Python package to specified directory")

    if args.to_env:
        # Find the current python environment's dist-packages directory (or site-packages directory if it is in the path)
        # Then copy the MSCL Python package to the current python environment's dist-packages directory
        for location in sys.path:
            if "dist-packages" in location or "site-packages" in location:
                mscl_files = glob.glob(f'{location}/*mscl*')
                if mscl_files:
                    for mf in mscl_files:
                        os.remove(mf)

                # res = os.system(f"cp /usr/lib/python{pyversion.major}.{pyversion.minor}/dist-packages/*mscl* {location}")
                shutil.copy2(f"/usr/lib/python{pyversion.major}.{pyversion.minor}/dist-packages/_mscl.so", f"{location}/_mscl.so")
                shutil.copy2(f"/usr/lib/python{pyversion.major}.{pyversion.minor}/dist-packages/mscl.py", f"{location}/mscl.py")
                break
    

