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
actuators.set_torque(LEFT, 0.5)
actuators.set_position(RIGHT, 0, 0.5, 0.1, 0.1, degrees=True)

### Data ---
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

## CubeMars Actuators
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.cubemars.CubeMars
    :show-inheritance:
    :members:
    :undoc-members:
    :member-order: bysource

.. autoclass:: epicallypowerful.actuation.cubemars.CubeMarsServo
    :show-inheritance:
    :members:
    :undoc-members:
    :member-order: bysource

.. autoclass:: epicallypowerful.actuation.cubemars.CubeMarsV3
    :show-inheritance:
    :members:
    :undoc-members:
    :member-order: bysource
```

## RobStride Motors
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.robstride.Robstride
    :show-inheritance:
    :members:
    :undoc-members:
    :member-order: bysource

```

## CyberGear Motors
```{eval-rst}
.. autoclass:: epicallypowerful.actuation.cybergear.CyberGear
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
