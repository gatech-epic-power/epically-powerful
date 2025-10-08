from abc import ABC, abstractmethod
from epicallypowerful.sensing.imu_data import IMUData

class IMU(ABC):
    @abstractmethod
    def _set_up_connected_imus(self):

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def exit_gracefully(self):
        pass