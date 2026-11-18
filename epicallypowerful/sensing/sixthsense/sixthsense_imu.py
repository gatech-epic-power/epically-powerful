"""epically-powerful module for managing SixthSense IMUs.

This module contains the classes and commands for initializing and reading
from SixthSense IMUs streamed over one or more serial (UART / USB-CDC) links.

A SixthSense node configured in CENTRAL mode collects its own IMU data
plus the data of up to 5 PERIPHERAL nodes (received over CAN or ESP-NOW) and
forwards all of it over serial. This module parses those binary streams across
all connected Central nodes.

For UART communication, each frame is::

        0xFD 0xAC | info (u8) | millis (u32) | N x sensor block | XOR checksum (u8)

    0xFD 0xAC is the magic word, followed by an info byte, a ms timestamp, and sensor readouts.

    "info" high nibble = number of active sensors, low nibble = field flags
    (bit0 accel+gyro, bit1 mag, bit2 euler, bit3 quat). Each sensor block is::

        can_id (u16) | [accel xyz, gyro xyz] | [mag xyz] | [roll pitch yaw] | [qw qx qy qz] | soc (u16)

    All values are little-endian float32, except can_id and soc which are uint16.
    Accel is in m/s^2, gyro in rad/s, Euler angles in degrees. The checksum is the XOR of
    every byte after the magic word. Sensors are identified by their CAN base ID (e.g. 100, 110).
"""

import glob
import os
import struct
import threading
import time
from dataclasses import replace

import numpy as np

from epicallypowerful.sensing.imu_abc import IMU
from epicallypowerful.sensing.imu_data import IMUData

try:
    import serial
    import serial.tools.list_ports

    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

# Set constants
DEFAULT_PORT = "/dev/ttyACM0"
DEFAULT_BAUDRATE = 115200  # Ignored for native USB-CDC, no change necessary
ESPRESSIF_VID = 0x303A     # Espressif native USB Vendor ID (ESP32-S3)
DEG2RAD = np.pi / 180.0

# Binary communication constants
MAGIC = b"\xFD\xAC"
HEADER_LEN = 7  # magic (2) + info (1) + millis (4)
FLAG_ACCEL_GYRO = 1 << 0
FLAG_MAG = 1 << 1
FLAG_EULER = 1 << 2
FLAG_QUAT = 1 << 3


def _block_size(flags: int) -> int:
    """Bytes per sensor block in a binary frame for the given field flags."""
    size = 2  # CAN ID (uint16_t)
    if flags & FLAG_ACCEL_GYRO:
        size += 24
    if flags & FLAG_MAG:
        size += 12
    if flags & FLAG_EULER:
        size += 12
    if flags & FLAG_QUAT:
        size += 16
    size += 2  # SoC (uint16_t)
    return size


class _PortWorker:
    """Holds serial handle, reader thread, and connection state for one Central USB port."""

    def __init__(self, port: str, assigned_ids: set[int]) -> None:
        self.port = port
        self.assigned_ids = assigned_ids
        self.serial: serial.Serial | None = None
        self.thread: threading.Thread | None = None
        self.connected = False


class SixthSenseIMUs(IMU):
    """Class for receiving data from SixthSense IMUs over one or more serial ports.
    Getting data from each IMU is as simple as calling :py:meth:`get_data` with the
    respective identifier as the argument.

    One background thread per Central serial port continuously reads incoming bytes and
    updates the latest sample for every sensor, so :py:meth:`get_data` never blocks on
    serial I/O (beyond the optional `timeout` wait for a fresh sample). Automatically
    reconnects if any USB port disconnects.

    Args:
        imu_ids (list[int]): CAN base IDs (e.g. [100, 110]) of the sensors to read.
        port (str | list[str] | None): Serial port(s) of CENTRAL SixthSense node(s).
            If None, scans all connected USB serial devices in parallel to find matching
            ports automatically. Default: None.
        baudrate (int): Baud rate. Ignored for native USB-CDC. Default: 115200.
        timeout (float): Max time [s] :py:meth:`get_data` waits for a sample newer than
            the previous call before returning the latest one. Default: 0.0002.
        num_retries (int): Number of 0.1s retries waiting for all requested IMUs to appear.
            Default: 10.
        reconnect_delay (float): Delay [s] between reconnection attempts on disconnect.
            Default: 0.25.
        stale_timeout (float): Time [s] with no incoming serial bytes before forcing a
            port reconnect. Default: 0.5.
        active_timeout (float): Max age [s] of a sensor's last packet before its
            `IMUData.connected` flag becomes False. Default: 0.05.
        verbose (bool): Print connection and discovery diagnostics. Default: False.
    """

    def __init__(
        self,
        imu_ids: list[int],
        port: str | list[str] | None = None,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = 0.0002,
        num_retries: int = 10,
        reconnect_delay: float = 0.25,
        stale_timeout: float = 0.5,
        active_timeout: float = 0.05,
        verbose: bool = False,
    ) -> None:
        if not PYSERIAL_AVAILABLE:
            raise ModuleNotFoundError(
                "pyserial not found, please install it to use SixthSense IMUs: `pip install pyserial`."
            )

        self.verbose = verbose
        self.timeout = timeout
        self.baudrate = baudrate
        self.reconnect_delay = reconnect_delay
        self.stale_timeout = stale_timeout
        self.active_timeout = active_timeout
        self._requested_ids = list(imu_ids)
        self._fixed_ports = (
            [port] if isinstance(port, str) else (list(port) if port is not None else None)
        )

        # Shared state between reader threads and callers
        self._lock = threading.Lock()
        self._new_sample = threading.Condition(self._lock)
        self._last_seen_count = {}
        self._stop_event = threading.Event()
        self._workers: list[_PortWorker] = []
        self.frames_received = 0
        self.frames_dropped = 0
        self.last_flags = 0

        # Ensure serial port permissions BEFORE scanning/opening ports
        self._grant_acm_permissions()

        # Resolve all ports carrying the requested IMUs
        port_map = self._resolve_ports(self._requested_ids)
        self.ports = list(port_map.keys())
        self.port = self.ports[0] if self.ports else None

        # Open all matching ports and wait for requested IMUs to show up
        self._imu_nodes = self._set_up_connected_imus(
            imu_ids=self._requested_ids, port_map=port_map
        )
        for i in range(num_retries):
            missing = self._missing_imus()
            if not missing:
                break
            if i == num_retries - 1:
                print(
                    f"[SixthSense] Warning: Not all requested IMUs seen across {self.ports} after "
                    f"{num_retries} attempts. Missing: {missing}. Seen: {self.seen_ids()}"
                )
            elif verbose:
                print(f"[SixthSense] Waiting for missing IMUs {missing}...")
            time.sleep(0.1)

    # -------------------------------------------------------------- discovery

    @staticmethod
    def _grant_acm_permissions() -> None:
        """Grant read/write access to /dev/ttyACM* devices if not already accessible."""
        acm_ports = glob.glob("/dev/ttyACM*")
        if acm_ports and not all(os.access(p, os.R_OK | os.W_OK) for p in acm_ports):
            os.system("sudo chmod 777 /dev/ttyACM*")

    @staticmethod
    def _open_serial(port: str, baudrate: int, timeout: float) -> "serial.Serial":
        """Open a serial port without blocking on USB control-line ioctls."""
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            rtscts=False,
            dsrdtr=False,
        )
        try:
            ser.dtr = True
        except OSError:
            pass
        return ser

    @staticmethod
    def _probe_single_port(
        device: str, scan_timeout: float, baudrate: int, verbose: bool = False
    ) -> tuple[str, list[int] | None]:
        """Probe one serial port for a valid SixthSense binary frame."""
        for attempt in range(3):
            try:
                ser = SixthSenseIMUs._open_serial(device, baudrate=baudrate, timeout=0.02)
                with ser:
                    ser.reset_input_buffer()
                    buf = bytearray()
                    deadline = time.perf_counter() + scan_timeout

                    while time.perf_counter() < deadline:
                        chunk = ser.read(ser.in_waiting or 1)
                        if not chunk:
                            continue
                        buf.extend(chunk)

                        start = buf.find(MAGIC)
                        if start < 0:
                            del buf[: max(0, len(buf) - 1)]
                            continue
                        if start > 0:
                            del buf[:start]
                        if len(buf) < HEADER_LEN:
                            continue

                        info = buf[2]
                        count, flags = info >> 4, info & 0x0F
                        block_sz = _block_size(flags)
                        frame_len = HEADER_LEN + count * block_sz + 1
                        if len(buf) < frame_len:
                            continue

                        checksum = 0
                        for b in buf[2 : frame_len - 1]:
                            checksum ^= b
                        if checksum != buf[frame_len - 1]:
                            del buf[:2]
                            continue

                        ids = []
                        offset = HEADER_LEN
                        for _ in range(count):
                            (can_id,) = struct.unpack_from("<H", buf, offset)
                            ids.append(can_id)
                            offset += block_sz

                        return device, sorted(ids)

                if verbose:
                    print(f"[SixthSense] {device}: opened, but no valid frame in {scan_timeout}s")
                return device, None

            except (serial.SerialException, OSError) as e:
                if verbose:
                    print(f"[SixthSense] {device} (attempt {attempt + 1}/3): {e}")
                time.sleep(0.15)

        return device, None

    @staticmethod
    def discover_devices(
        scan_timeout: float = 0.4, baudrate: int = DEFAULT_BAUDRATE, verbose: bool = False
    ) -> dict[str, list[int]]:
        """Scan all connected USB serial ports in parallel and passively read one binary frame
        to map each SixthSense Central port to its active sensor CAN IDs.
        """
        SixthSenseIMUs._grant_acm_permissions()
        if not PYSERIAL_AVAILABLE:
            return {}

        candidate_set = set()
        for p in serial.tools.list_ports.comports():
            if p.vid == ESPRESSIF_VID or any(
                tag in p.device for tag in ("ttyACM", "ttyUSB", "COM")
            ):
                candidate_set.add(p.device)
        candidate_set.update(glob.glob("/dev/ttyACM*"))

        candidates = sorted(candidate_set)
        if not candidates:
            return {}

        discovered: dict[str, list[int]] = {}
        results_lock = threading.Lock()

        def _worker(dev: str) -> None:
            port_name, ids = SixthSenseIMUs._probe_single_port(
                dev, scan_timeout=scan_timeout, baudrate=baudrate, verbose=verbose
            )
            if ids is not None:
                with results_lock:
                    discovered[port_name] = ids

        threads = [threading.Thread(target=_worker, args=(dev,)) for dev in candidates]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return dict(sorted(discovered.items()))

    def _resolve_ports(self, requested_ids: list[int]) -> dict[str, set[int]]:
        """Map every relevant serial port to the subset of `requested_ids` it streams."""
        if self._fixed_ports is not None:
            for p in self._fixed_ports:
                self._check_port_access(p)
            return {p: set(requested_ids) for p in self._fixed_ports}

        req_set = set(requested_ids)
        discovered: dict[str, list[int]] = {}

        for _ in range(3):
            discovered = self.discover_devices(baudrate=self.baudrate, verbose=self.verbose)
            found_ids = {i for ids in discovered.values() for i in ids}
            if req_set.issubset(found_ids):
                break
            time.sleep(0.2)

        if not discovered:
            raise FileNotFoundError(
                "No SixthSense Central node found on any serial port. "
                "Check USB connection and ensure `verbose_uart = 0` in firmware."
            )

        port_map: dict[str, set[int]] = {}
        for dev_port, active_ids in discovered.items():
            matched = req_set.intersection(active_ids)
            if matched:
                self._check_port_access(dev_port)
                port_map[dev_port] = matched

        if not port_map:
            raise FileNotFoundError(
                f"None of the requested IDs {requested_ids} were found on {discovered}."
            )

        if self.verbose:
            print(f"[SixthSense] Discovered devices: {discovered} -> Selected {port_map}")
        return port_map

    # ------------------------------------------------------------------ setup

    @staticmethod
    def _check_port_access(port: str) -> None:
        """Check that a serial port exists and is accessible."""
        if not os.path.exists(port):
            raise FileNotFoundError(
                f"Serial port {port} not found. Is the SixthSense Central node plugged in?"
            )
        if not os.access(port, os.R_OK | os.W_OK):
            raise PermissionError(
                f"No permission to open {port}. Run `sudo usermod -aG dialout $USER` "
                f"and log out/in (or `sudo chmod 666 {port}` for this session)."
            )

    def _set_up_connected_imus(
        self, imu_ids: list[int], port_map: dict[str, set[int]]
    ) -> dict:
        """Open each Central serial port, create data holders, and start a reader thread per port."""
        imus = {}
        for imu_id in imu_ids:
            imus[imu_id] = [0, 0, IMUData(soc=0, connected=False)]
            self._last_seen_count[imu_id] = 0

        self._seen = set()
        self._imu_nodes = imus
        self._workers = []

        for idx, (dev_port, assigned_ids) in enumerate(port_map.items()):
            if idx > 0:
                time.sleep(0.03)  # Stagger USB-CDC open control transfers across hub ports

            worker = _PortWorker(port=dev_port, assigned_ids=assigned_ids)
            worker.serial = self._open_serial(dev_port, baudrate=self.baudrate, timeout=0.01)
            worker.serial.reset_input_buffer()
            worker.connected = True
            worker.thread = threading.Thread(
                target=self._read_loop,
                args=(worker,),
                name=f"SixthSenseReader-{os.path.basename(dev_port)}",
                daemon=True,
            )
            self._workers.append(worker)
            worker.thread.start()

            if self.verbose:
                print(f"[SixthSense] Opened {dev_port}, listening for IMUs: {sorted(assigned_ids)}")

        return imus

    @property
    def connected(self) -> bool:
        """Return True if at least one Central serial port is currently connected."""
        return any(w.connected for w in self._workers)

    def _missing_imus(self) -> list[int]:
        with self._lock:
            return [i for i in self._imu_nodes if i not in self._seen]

    def seen_ids(self) -> list[int]:
        """IDs of all sensors seen on the stream so far (including ones not requested)."""
        with self._lock:
            return sorted(self._seen)

    # ------------------------------------------------------------- reading

    def _reconnect_worker(self, worker: _PortWorker) -> bool:
        """Close a broken serial handle and reconnect to the port streaming its assigned IDs."""
        worker.connected = False
        if worker.serial is not None:
            try:
                worker.serial.close()
            except Exception:
                pass
            worker.serial = None

        try:
            self._grant_acm_permissions()
            if self._fixed_ports is not None:
                candidate_port = worker.port
            else:
                discovered = self.discover_devices(baudrate=self.baudrate, verbose=self.verbose)
                in_use = {w.port for w in self._workers if w is not worker and w.connected}
                matches = [
                    p
                    for p, ids in discovered.items()
                    if p not in in_use and worker.assigned_ids.intersection(ids)
                ]
                if not matches:
                    return False
                candidate_port = matches[0]

            if not os.path.exists(candidate_port) or not os.access(
                candidate_port, os.R_OK | os.W_OK
            ):
                return False

            ser = self._open_serial(candidate_port, baudrate=self.baudrate, timeout=0.01)
            ser.reset_input_buffer()
            worker.port = candidate_port
            worker.serial = ser
            worker.connected = True
            print(f"[SixthSense] Reconnected {sorted(worker.assigned_ids)} on {worker.port}")
            return True
        except Exception:
            return False

    def _read_loop(self, worker: _PortWorker) -> None:
        """Background thread per port: read serial bytes, parse frames, and auto-reconnect."""
        buf = bytearray()
        last_rx_time = time.perf_counter()

        while not self._stop_event.is_set():
            if not worker.connected or worker.serial is None:
                buf.clear()
                if self._reconnect_worker(worker):
                    last_rx_time = time.perf_counter()
                else:
                    self._stop_event.wait(self.reconnect_delay)
                continue

            try:
                chunk = worker.serial.read(worker.serial.in_waiting or 1)
                if chunk:
                    last_rx_time = time.perf_counter()
                    buf.extend(chunk)
                    self._parse_binary(buf)
                elif (
                    self.stale_timeout > 0
                    and (time.perf_counter() - last_rx_time) > self.stale_timeout
                ):
                    if self.verbose:
                        print(f"[SixthSense] Stream stalled on {worker.port}, reconnecting...")
                    worker.connected = False
            except (serial.SerialException, OSError, TypeError) as e:
                if self._stop_event.is_set():
                    break
                print(
                    f"[SixthSense] Disconnected from {worker.port} ({e}). Waiting to reconnect..."
                )
                worker.connected = False

    def _parse_binary(self, buf: bytearray) -> None:
        """Consume complete binary frames from `buf` (in place)."""
        while True:
            start = buf.find(MAGIC)
            if start < 0:
                del buf[: max(0, len(buf) - 1)]
                return
            if start > 0:
                del buf[:start]
            if len(buf) < HEADER_LEN:
                return

            info = buf[2]
            count, flags = info >> 4, info & 0x0F
            frame_len = HEADER_LEN + count * _block_size(flags) + 1
            if len(buf) < frame_len:
                return

            checksum = 0
            for b in buf[2 : frame_len - 1]:
                checksum ^= b
            if checksum != buf[frame_len - 1]:
                with self._lock:
                    self.frames_dropped += 1
                del buf[:2]
                continue

            (device_ms,) = struct.unpack_from("<I", buf, 3)
            host_t = time.perf_counter()
            offset = HEADER_LEN
            samples = []
            for _ in range(count):
                (can_id,) = struct.unpack_from("<H", buf, offset)
                offset += 2
                values, offset = self._unpack_fields(buf, offset, flags)
                samples.append((can_id, values))
            del buf[:frame_len]

            self._store(samples, flags, device_ms, host_t)

    @staticmethod
    def _unpack_fields(buf: bytearray, offset: int, flags: int):
        values = {}
        if flags & FLAG_ACCEL_GYRO:
            values["accel_gyro"] = struct.unpack_from("<6f", buf, offset)
            offset += 24
        if flags & FLAG_MAG:
            values["mag"] = struct.unpack_from("<3f", buf, offset)
            offset += 12
        if flags & FLAG_EULER:
            values["euler"] = struct.unpack_from("<3f", buf, offset)
            offset += 12
        if flags & FLAG_QUAT:
            values["quat"] = struct.unpack_from("<4f", buf, offset)
            offset += 16

        (values["soc"],) = struct.unpack_from("<H", buf, offset)
        offset += 2
        return values, offset

    def _store(self, samples, flags: int, device_ms: int, host_t: float) -> None:
        """Write parsed samples into the per-IMU data holders."""
        with self._new_sample:
            self.frames_received += 1
            self.last_flags = flags
            for imu_id, values in samples:
                self._seen.add(imu_id)
                node = self._imu_nodes.get(imu_id)
                if node is None:
                    continue
                d = node[2]
                d.timestamp = host_t
                d.connected = True
                if "accel_gyro" in values:
                    d.acc_x, d.acc_y, d.acc_z, d.gyro_x, d.gyro_y, d.gyro_z = values["accel_gyro"]
                if "mag" in values:
                    d.mag_x, d.mag_y, d.mag_z = values["mag"]
                if "quat" in values:
                    d.quat_w, d.quat_x, d.quat_y, d.quat_z = values["quat"]
                if "euler" in values:
                    roll, pitch, yaw = values["euler"]
                    d.eul_x, d.eul_y, d.eul_z = roll * DEG2RAD, pitch * DEG2RAD, yaw * DEG2RAD
                if "soc" in values:
                    d.soc = int(values["soc"])
                node[0] += 1
                node[1] = device_ms
            self._new_sample.notify_all()

    # ------------------------------------------------------------ public API

    def get_data(self, imu_id: int) -> IMUData:
        """Get orientation, angular velocity, linear acceleration, SoC, and connection
        status from a SixthSense IMU.

        Args:
            imu_id (int): CAN base ID of the IMU.
        Returns:
            IMUData: Dataclass with orientation, angular velocity [rad/s], linear
                acceleration [m/s^2], `soc` [%], and `connected` status.
        """
        with self._new_sample:
            node = self._imu_nodes[imu_id]
            if node[0] == self._last_seen_count[imu_id] and self.timeout > 0:
                self._new_sample.wait_for(
                    lambda: node[0] != self._last_seen_count[imu_id], timeout=self.timeout
                )
            self._last_seen_count[imu_id] = node[0]
            imu_data = replace(node[2])

        # Reflect live sensor status: True only if seen and updated within active_timeout
        imu_data.connected = (
            imu_data.timestamp > 0.0
            and (time.perf_counter() - imu_data.timestamp) <= self.active_timeout
        )

        return imu_data

    def is_connected(self, imu_id: int) -> bool:
        """Return True if at least one packet has been received from `imu_id`."""
        with self._lock:
            return imu_id in self._seen

    def is_active(self, imu_id: int, max_age: float | None = None) -> bool:
        """Return True if `imu_id` has received a frame within `max_age` seconds."""
        limit = self.active_timeout if max_age is None else max_age
        with self._lock:
            node = self._imu_nodes.get(imu_id)
            if node is None or node[2].timestamp == 0.0:
                return False
            return (time.perf_counter() - node[2].timestamp) <= limit

    def get_device_time_ms(self, imu_id: int) -> int:
        """Firmware `millis()` of the latest binary frame containing this IMU."""
        with self._lock:
            return self._imu_nodes[imu_id][1]

    def close(self) -> None:
        """Stop all reader threads and close all serial ports."""
        self._stop_event.set()
        for worker in self._workers:
            if worker.thread is not None:
                worker.thread.join(timeout=1.0)
            if worker.serial is not None and worker.serial.is_open:
                worker.serial.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def __getitem__(self, index: int) -> IMUData:
        return self.get_data(index)


def main(imu_ids: list[int] | None = None, port: str | list[str] | None = None) -> None:
    """Test implementation that auto-discovers and streams data from all connected IMUs."""
    if not imu_ids:
        discovered = SixthSenseIMUs.discover_devices(verbose=True)
        if not discovered:
            raise RuntimeError("No SixthSense Central node detected.")
        port = list(discovered.keys())
        imu_ids = sorted({i for ids in discovered.values() for i in ids})
        print(f"Auto-discovered {discovered} -> Streaming {imu_ids}")

    imus = SixthSenseIMUs(
        imu_ids=imu_ids,
        port=port,
        verbose=True,
    )
    last_time = time.perf_counter()

    try:
        while True:
            for imu_id in imu_ids:
                d = imus.get_data(imu_id)
                current_time = time.perf_counter()
                print(
                    f"[{(1 / (current_time - last_time)):.1f}]: ID: {imu_id} | "
                    f"conn: {d.connected} | SoC: {d.soc}% | "
                    f"roll: {d.eul_x:.2f},\t pitch: {d.eul_y:.2f},\t yaw: {d.eul_z:.2f} | "
                    f"gyro: {d.gyro_x:.3f}, {d.gyro_y:.3f}, {d.gyro_z:.3f}"
                )
                last_time = current_time
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        imus.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stream data from SixthSense IMUs.")
    parser.add_argument(
        "ids",
        nargs="*",
        type=int,
        default=None,
        help="CAN IDs of the sensors (omit to auto-discover all active IDs).",
    )
    parser.add_argument(
        "--port",
        nargs="*",
        default=None,
        help="Serial port(s) (omit to auto-discover across all ports).",
    )
    args = parser.parse_args()
    main(imu_ids=args.ids, port=args.port)