import argparse

def rpi_or_jetson():
    import platform
    machine_name = platform.uname().release.lower()
    if "tegra" in machine_name:
        return "jetson"
    elif "rpi" in machine_name:
        return "rpi"


def collect_imu_data():
    parser = argparse.ArgumentParser(description="Collect IMU data", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--imu-serial-id", '-id', nargs='+', required=True, type=str, help="IMU serial ID multiple can be specified")
    parser.add_argument("--output", '-o', default="output.csv", help="Output file")
    parser.add_argument("--duration", '-d', default=30, type=int, help="Duration in seconds")
    parser.add_argument("--channels", '-c', choices=["acc", "gyro", "mag", "orient", "euler"], type=str, nargs="+", default=["acc", "gyro"], help="Types of data to collect")
    parser.add_argument("--remote-sync-channel", '-r', type=int, action="append", help="GPIO pins to use for remote sync channels. Use this argument multiple times to specify multiple channels")

    args = parser.parse_args()
    print(args.output)
    print(args.imu_serial_id) # This is a list
    print(args.duration)
    print(args.channels)
    print(args.remote_sync_channel)

    
    outfile = args.output
    duration = args.duration
    serial_ids = args.imu_serial_id
    channels = args.channels
    remote_sync_channels = args.remote_sync_channel

    from epicallypowerful.sensing.microstrain_imu import MicrostrainImus
    from epicallypowerful.toolbox.clocking import timed_loop
    from epicallypowerful.toolbox.data_recorder import DataRecorder

    imus = MicrostrainImus(serial_ids)

    headers = []
    for serial_id in serial_ids:
        if "acc" in channels:
            headers.extend([f"{serial_id}_acc_x", f"{serial_id}_acc_y", f"{serial_id}_acc_z"])
        if "gyro" in channels:
            headers.extend([f"{serial_id}_gyro_x", f"{serial_id}_gyro_y", f"{serial_id}_gyro_z"])
        if "mag" in channels:
            headers.extend([f"{serial_id}_mag_x", f"{serial_id}_mag_y", f"{serial_id}_mag_z"])
        if "orient" in channels:
            headers.extend([f"{serial_id}_orient_w", f"{serial_id}_orient_x", f"{serial_id}_orient_y", f"{serial_id}_orient_z"])
        if "euler" in channels:
            headers.extend([f"{serial_id}_roll", f"{serial_id}_pitch", f"{serial_id}_yaw"])
    
    if remote_sync_channels != []:
        if rpi_or_jetson() == "rpi":
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BORD)
        elif rpi_or_jetson() == "jetson":
            import Jetson.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
        else:
            raise NotImplementedError("This platform does not support GPIO, please utilize a Raspberry Pi or Jetson or other compatible platform")
        for c in remote_sync_channels:
            headers.append(f"sync_{c}")
            GPIO.setup(c, GPIO.IN)

    recorder = DataRecorder(outfile, headers, delimiter=",", overwrite=False, buffer_limit=duration*200) # Data is collected at 200Hz, and data is not saved until file is manually closed

    print(f"Collecting data for {duration} seconds")
    for _ in timed_loop(200, duration):
        row_data = []
        for serial_id in serial_ids:
            data = imus.get_data(serial_id)
            if "acc" in channels:
                row_data.extend([data.accx, data.accy, data.accz])
            if "gyro" in channels:
                row_data.extend([data.gyrox, data.gyroy, data.gyroz])
            if "mag" in channels:
                row_data.extend([data.magx, data.magy, data.magz])
            if "orient" in channels:
                row_data.extend([data.orientw, data.orientx, data.orienty, data.orientz])
            if "euler" in channels:
                row_data.extend([data.roll, data.pitch, data.yaw])
        if remote_sync_channels != []:
            for c in remote_sync_channels:
                row_data.append(GPIO.input(c))
        recorder.save(row_data)

    # Finalize the data saving
    print("Saving data, do not power off device...")
    recorder.finalize()
    print(f'Data saved to {outfile}')
    return 1

def motor_control():
    raise NotImplementedError