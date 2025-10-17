(GettingStarted)=
# Getting Started
EpicallyPowerful assumes a basic familiarity with some concepts like Python, electrical actuation, Linux computers, and inertial sensing. An in depth knowledge is not needed, but it can be helpful to search around for some basic refreshers.


## Quickstart
1) Set up your [Raspberry Pi](RPiSetup)
2) Install EpicallyPowerful Python package. In newer versions of ubuntu, you will likely need some form of virtual environment ([see here](PythonEnvs)).
   ```console
   $ pip install epicallypowerful
   ```
3) Set up your actuators CAN ID, and connect your actuator to [power and the CAN interface on your Pi](Actuators) 
4) Run the basic demo script
   ```console
   $ ep-stream-actuator --id <CAN ID>
   ```
   Ensure that you can see the position, velocity, and torque data appropriately streaming to the terminal.
5) [Optional] Install MSCL library
   ```console
   $ ep-install-mscl
   $ ep-stream-imu --serial_id <IMU serial ID (last 6 digits)>
   ```
6) Check out the [example controllers](https://github.com/gatech-epic-power/epically-powerful/tree/main/examples) and start writing your own!
## What does EpicallyPowerful Provide
* Actuator Control
* Inertial Measurement Unit Reading
* Data Recording & Basic Control Loop Structuring


We highly recommend however that you read through the setup and tutorial pages relevant to your application **before** you try to write your code or collect data.


