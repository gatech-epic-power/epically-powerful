from abc import ABC, abstractmethod
from epicallypowerful.actuation.motor_data import MotorData

class Actuator(ABC):
    @abstractmethod
    def set_torque(self, torque: float):
        pass

    @abstractmethod
    def set_position(self, position: float, kp: float, kd:float, degrees: bool = False):
        pass

    @abstractmethod
    def set_velocity(self, velocity: float, kd: float, degrees: bool = False):
        pass

    @abstractmethod
    def zero_encoder(self):
        pass

    @abstractmethod
    def get_data(self) -> MotorData:
        pass

    @abstractmethod
    def get_torque(self) -> float:
        pass

    @abstractmethod
    def get_position(self, degrees: bool = False) -> float:
        pass

    @abstractmethod
    def get_velocity(self, degrees: bool = False) -> float:
        pass

    @abstractmethod
    def call_response_latency(self) -> float:
        pass

    @abstractmethod
    def get_temperature(self) -> float:
        pass

    @abstractmethod
    def _enable(self):
        pass
    
    @abstractmethod
    def _disable(self):
        pass

    @abstractmethod
    def _set_zero_torque(self):
        pass
