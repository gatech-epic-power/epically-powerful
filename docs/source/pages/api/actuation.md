# Actuation

Example Usage
```python
from epicallypowerful.actuation import ActuatorGroup, TMotor, CyberGear

LEFT = 0x01
RIGHT = 0x02

### Instantiation ---
actuators = ActuatorGroup([
    TMotor(LEFT, 'AK80-9', invert=True),
    CyberGear(RIGHT)
])
# OR
actuators = ActuatorGroup.from_dict({
    LEFT: 'AK80-9',
    RIGHT: 'CyberGear'
}, invert=[LEFT])

### Control ---
actuators[LEFT].set_torque(0.5)
actuators[RIGHT].set_position(0, 0.5, 0.1, 0.1, degrees=True)
# OR
actuators.set_torque(LEFT, 0.5)
actuators.set_position(RIGHT, 0, 0.5, 0.1, 0.1, degrees=True)

### Data ---
print(actuators[LEFT].get_torque())
print(actuators[RIGHT].get_position())
print(actuators[RIGHT].get_temperature())
# OR
print(actuators.get_torque(LEFT))
print(actuators.get_position(RIGHT))
print(actuators.get_temperature(RIGHT))

```

## Actuator Group
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.ActuatorGroup
    :members:
    :undoc-members:
    :member-order: bysource

```

## T Motors
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.TMotor
    :show-inheritance:
    :members:
    :undoc-members:
    :member-order: bysource

```

## CyberGear Motors
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.CyberGear
    :show-inheritance:
    :members:
    :undoc-members:
    :member-order: bysource

```

## Motor Data
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.MotorData
    :members:
    :undoc-members:
    :member-order: bysource

```

## Abstract Classes
These classes are the base classes which many of the classes in this section inherit from. This class is not intended for direct usage, and its inclusion here is for documentation completeness.

```{eval-rst}
.. autoclass:: epicallypowerful.actuation.actuator_abc.Actuator
    :members:
    :undoc-members:

```
