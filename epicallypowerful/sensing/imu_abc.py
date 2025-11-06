from abc import ABC, abstractmethod
from epicallypowerful.sensing.imu_data import IMUData

class IMU(ABC):
    @abstractmethod
    def get_data(self) -> IMUData:
        """Return data from call to IMU."""
        pass

    @abstractmethod
    def _set_up_connected_imus(self, imu_ids: list) -> None:
        """Initialize all IMUs."""
        pass