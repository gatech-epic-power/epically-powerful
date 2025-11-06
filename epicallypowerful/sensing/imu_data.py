from dataclasses import dataclass
import numpy as np

@dataclass
class IMUData:
    """Dataclass for IMU data. This includes fields for 
    measurements from both MicroStrain and MPU9250 units.
    """

    # Orientation (Rotation matrix) [MICROSTRAIN ONLY]
    m11: float = 0.0
    m12: float = 0.0
    m13: float = 0.0
    m21: float = 0.0
    m22: float = 0.0
    m23: float = 0.0
    m31: float = 0.0
    m32: float = 0.0
    m33: float = 0.0

    # Orientation (inv. ref. rotation matrix (for reorientation)) [MICROSTRAIN ONLY].
    # Multiply this rotation matrix by the raw rotation matrix
    # to get `zeroed` orientation values (e.g. zeroed_mat = ref_mat * raw_mat)
    ref_m11: float = 0.0
    ref_m12: float = 0.0
    ref_m13: float = 0.0
    ref_m21: float = 0.0
    ref_m22: float = 0.0
    ref_m23: float = 0.0
    ref_m31: float = 0.0
    ref_m32: float = 0.0
    ref_m33: float = 0.0

    # Orientation (Quaternion) [MICROSTRAIN ONLY]
    quat_x: float = 0.0
    quat_y: float = 0.0
    quat_z: float = 0.0
    quat_w: float = 1.0

    ef_quat_x: float = 0.0
    ef_quat_y: float = 0.0
    ef_quat_z: float = 0.0
    ef_quat_w: float = 1.0

    # Orientation (Euler) [MICROSTRAIN ONLY]
    eul_x: float = 0.0
    eul_y: float = 0.0
    eul_z: float = 0.0

    # Gyro [MICROSTRAIN & MPU9250]
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0

    # Linear acceleration [MICROSTRAIN & MPU9250]
    acc_x: float = 0.0
    acc_y: float = 0.0
    acc_z: float = 0.0

    # Magnetometer readings (raw) [MICROSTRAIN & MPU9250]
    mag_x: float = 0.0
    mag_y: float = 0.0
    mag_z: float = 0.0

    # Temperature readings [MPU9250 ONLY]
    temp: float = 0.0

    timestamp: float = 0.0

    @property
    def accelerometer(self):
        return [self.acc_x, self.acc_y, self.acc_z]

    @property
    def gyroscope(self):
        return [self.gyro_x, self.gyro_y, self.gyro_z]

    @property
    def magnetometer(self):
        return [self.mag_x, self.mag_y, self.mag_z]

    @property
    def quaternion(self):
        return [self.quat_x, self.quat_y, self.quat_z, self.quat_w]

    @property
    def ef_quaternion(self):
        return [self.ef_quat_x, self.ef_quat_y, self.ef_quat_z, self.ef_quat_w]

    @property
    def euler(self):
        return [self.eul_x, self.eul_y, self.eul_z]

    @property
    def rot_matrix(self):
        return np.array([
            [self.m11, self.m12, self.m13],
            [self.m21, self.m22, self.m23],
            [self.m31, self.m32, self.m33],
        ])

    @property
    def ref_rot_matrix(self):
        return np.array([
            [self.ref_m11, self.ref_m12, self.ref_m13],
            [self.ref_m21, self.ref_m22, self.ref_m23],
            [self.ref_m31, self.ref_m32, self.ref_m33],
        ])