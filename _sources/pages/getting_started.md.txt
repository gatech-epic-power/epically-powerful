(GettingStarted)=
# Getting Started
EpicallyPowerful assumes a basic familiarity with some concepts like Python, electrical actuation, Linux computers, and inertial sensing. In-depth knowledge is not needed, but it can be helpful to search around for some basic refreshers.


## Quickstart
1) Set up your [Raspberry Pi](RPiSetup) or [Jetson Orin Nano](JetsonSetup)
2) Install Epically Powerful Python package. In newer versions of Ubuntu, you will likely need some form of ([virtual environment](PythonEnvs)).
   ```console
   $ pip install epicallypowerful
   ```
3) [Set up your actuator's CAN ID](Actuators), then connect your actuator to power and the CAN interface on your single-board computer.
4) Run the basic demo script
   ```console
   $ ep-stream-actuator --id <CAN ID>
   ```
   Ensure that you can see the position, velocity, and torque data appropriately streaming to the terminal.
5) [Optional] Install MSCL library
   ```console
   $ ep-install-mscl
   $ ep-stream-microstrain-imu --serial_id <IMU serial ID (last 6 digits)>
   ```
6) Check out the [example controllers](ExampleControllers) and start writing your own!
   
## What Epically Powerful Provides
* Actuator Control
* Inertial Measurement Unit Reading
* Data Recording & Basic Control Loop Structuring

:::{note}
We highly recommend that you read through the setup and tutorial pages relevant to your application **before** you try to write your code or collect data.
:::



