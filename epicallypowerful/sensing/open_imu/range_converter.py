"""Utilities for converting between floats and fixed byte representations.

This is commonly used for custom hardware serialization when messages don't 
change frequently but size is of the essence.

The range of possible input values can be fully specified by including EITHER
a lower bound (low) and an upper bound (high) OR a single bound (low or high)
and a resolution. Allowing for both methods of specification accommodates
varying specifications provided by hardware manufacturers.

Adapted from Abhiram Ghanta's work modernizing existing code.
"""

from typing import Optional


class UnsignedIntConverter:
    """Converts floats to and from an unsigned integer with a given range and precision."""

    _low: float  # Inclusive, '0'*num_bits corresponds to this value
    _high: float  # Inclusive, '1'*num_bits corresponds to this value
    _num_bits: int
    _range: float
    _packing_scale: float

    def __init__(
        self,
        num_bits: int,
        low: Optional[float] = None,
        high: Optional[float] = None,
        resolution: Optional[float] = None,
    ):
        if num_bits < 1:
            raise ValueError("Need at least 1 bit for packing")

        if num_bits > 64:
            raise ValueError("Too many bits, code not tested here.")

        if len([v for v in (low, high, resolution) if v is None]) != 1:
            raise ValueError("Exactly one of (low, high, resolution) must be None.")

        if low is None or high is None:
            if resolution is None or resolution <= 0.0:
                raise ValueError("Resolution must be > 0")

            self._range = (2**num_bits - 1) * resolution

            if low is not None:
                self._low = low
                self._high = low + self._range
            elif high is not None:
                self._low = high - self._range
                self._high = high
        elif resolution is None:
            if high <= low:
                raise ValueError("High must be greater than low")
            self._low = low
            self._high = high
            self._range = high - low

        self._num_bits = num_bits
        self._packing_scale = (2**num_bits - 1) / self._range

    def to_unsigned_int(self, value: float) -> int:
        return int(min(max(value - self._low, 0), self._range) * self._packing_scale)

    def from_unsigned_int(self, packed_value: int) -> float:
        return packed_value / self._packing_scale + self._low


# Convert raw bit data into readable numbers:
# - linear acceleration: m*s^-2
# - angular velocity:  degrees per second
# - magnetometer: Gauss # we think? TODO: verify this
# Reference link: https://openimu.readthedocs.io/en/latest/software/CAN/CAN_J1939_DataPacketMessages.html
# NOTE: in the OpenIMU docs the "high" part of the range is just an approximation
# and is several percent off of the actual resolution-defined value. Only low and
# resolution are accurate.
acceleration_packer = UnsignedIntConverter(16, low=-320, resolution=0.01)
gyroscope_packer = UnsignedIntConverter(16, low=-400, resolution=1.0 / 81)
magnetometer_packer = UnsignedIntConverter(16, low=-8, resolution=1.0 / 4000)
