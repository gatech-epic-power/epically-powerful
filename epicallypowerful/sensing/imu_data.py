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
    orientx: float = 0.0
    orienty: float = 0.0
    orientz: float = 0.0
    orientw: float = 1.0

    ef_orientx: float = 0.0
    ef_orienty: float = 0.0
    ef_orientz: float = 0.0
    ef_orientw: float = 1.0

    # Orientation (Euler) [MICROSTRAIN ONLY]
    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0

    # Gyro [MICROSTRAIN & MPU9250]
    gyrox: float = 0.0
    gyroy: float = 0.0
    gyroz: float = 0.0

    # Linear acceleration [MICROSTRAIN & MPU9250]
    accx: float = 0.0
    accy: float = 0.0
    accz: float = 0.0

    # Magnetometer readings (raw) [MICROSTRAIN & MPU9250]
    magx: float = 0.0
    magy: float = 0.0
    magz: float = 0.0

    # Temperature readings [MPU9250 ONLY]
    temp: float = 0.0

    timestamp: float = 0.0

    @property
    def gyro(self):
        return [self.gyrox, self.gyroy, self.gyroz]

    @property
    def accel(self):
        return [self.accx, self.accy, self.accz]

    @property
    def magnetometer(self):
        return [self.magx, self.magy, self.magz]

    @property
    def quaternion(self):
        return [self.orientx, self.orienty, self.orientz, self.orientw]

    @property
    def ef_quaternion(self):
        return [self.ef_orientx, self.ef_orienty, self.ef_orientz, self.ef_orientw]

    @property
    def euler(self):
        return [self.roll, self.pitch, self.yaw]

    @property
    def matrix(self):
        return np.array([
            [self.m11, self.m12, self.m13],
            [self.m21, self.m22, self.m23],
            [self.m31, self.m32, self.m33],
        ])

    @property
    def ref_matrix(self):
        return np.array([
            [self.ref_m11, self.ref_m12, self.ref_m13],
            [self.ref_m21, self.ref_m22, self.ref_m23],
            [self.ref_m31, self.ref_m32, self.ref_m33],
        ])