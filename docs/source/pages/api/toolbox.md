# Toolbox

## Data Recorder
```{eval-rst}
.. autoclass:: epicallypowerful.toolbox.DataRecorder
    :members:
    :undoc-members:
    :member-order: bysource

```

## Clocking
```{eval-rst}
.. autoclass:: epicallypowerful.toolbox.LoopTimer
    :members:
    :undoc-members:
    :member-order: bysource

```

## Command Line Tools
Epically Powerful also includes a few cli tools to quickly test your system and get up and going.

```{eval-rst}
.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _install_mscl_python_parser
    :prog: ep-install-mscl
    :title: Install MSCL dependencies for MicroStrain IMUs

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _collect_microstrain_imu_data_parser
    :prog: ep-collect-imu-data
    :title: Collect MicroStrain IMU Data

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _visualize_dummy_data_parser
    :prog: ep-dummy-viz
    :title: Visualize Dummy Data

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _stream_microstrain_imu_data_parser
    :prog: ep-stream-microstrain-imu
    :title: Stream MicroStrain IMU Data

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _stream_mpu9250_imu_data_parser
    :prog: ep-stream-mpu9250-imu
    :title: Stream MPU9250 IMU Data

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _stream_actuator_data_parser
    :prog: ep-stream-actuator
    :title: Stream Actuator Data

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _impedance_control_actuator_parser
    :prog: ep-sample-impedance-ctrl
    :title: Impedance Control Example

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _position_control_actuator_parser
    :prog: ep-sample-position-ctrl
    :title: Position Control Example

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _position_control_actuator_with_visualizer_parser
    :prog: ep-sample-actuator-viz
    :title: Position Control with Visualization

.. sphinx_argparse_cli::
    :module: epicallypowerful.toolbox.cli
    :func: _imu_control_actuator_parser
    :prog: ep-sample-imu-ctrl
    :title: IMU Gyroscope Controled Actuator Position

```