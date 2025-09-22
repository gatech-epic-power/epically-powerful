(GettingStarted)=
# Getting Started
EpicallyPowerful assumes a basic familiarity with some concepts like Python, electrical actuation, linux computers, and inertial sensing. An in depth knowledge is not needed, but it can be helpful to google around for some basic refreshers.


## Quickstart
1) Set up your [Raspberry Pi](RPiSetup)
2) Install EpicallyPowerful Python package
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

## First Steps - Get your gear
Before you dive into the tutorials and using epicallypowerful, it's important you decide exactly what you will be working with. The Parts Picker can help you determine what specific devices fit your use case.  The key components that you will need to decide on (and the compatible options that we've incorporated) are listed below:

1) **Computer** (Raspberry Pi, Nvidia Jetson Orin Nano)
2) **Power source** (drill battery, lipo battery, power bank for separate computer power if desired)
3) **Actuator** (T-Motor AK-Series, Cybergear Micromotor, RobStride)
4) **Sensors** (Microstrain IMUs, MPU9250 IMUs, force sensitive resistors)

:::{tip}
Though specifications may vary for a full robotic setup, you can get can an benchtop epicallypowerful system set up quickly and cheaply!  The minimum required and most inexpensive setup to start moving a motor with epicallypowerful is:
1) **Computer:** Raspberry Pi (with associated Waveshare RS485 CAN hat + microSD card)
2) **Power sources:** 24V battery or benchtop power supply and 5V battery or wall power-supply
3) **Actuator:** T-Motor AK80-9

You will also need access to basic mechatronic resources, such as:
- Soldering equipment
- 14-12 AWG wire
- XT30 connectors (M+F)
- Pre crimped GH1.25 wires
:::


We highly recommend however that you read through the setup and tutorial pages relevant to your application **before** you try to write your code or collect data.


