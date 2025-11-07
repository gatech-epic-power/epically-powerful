(Tutorials)=
# Guide

## Before You Start - Resources You'll Need

Everything you need to get your Epically Powerful system up and running is in the [Part Picker](PartPicker), which will be discussed more below. However, we assume that you will have access to basic mechatronics and related items, such as:

* Keyboard + Mouse
* Monitor
* Soldering iron + solder
* Wiring supplies (heat shrink tubing, wire cutters + strippers, soldering flux, dupont jumper wires, 24-28 gauge spare wire)

## First Steps - Get Your Gear
Before you dive into the tutorials and using Epically Powerful, it's important you decide exactly what you will be working with. The [Part Picker](PartPicker) can help you determine what specific devices fit your use case, and the [Ordering Guide](https://docs.google.com/spreadsheets/d/1C3gL_t8qy4Z1Y0Z88K9UOk3GDusG5Bix34zb_12FyFI/edit?usp=sharing) contains links and prices for recommended parts. The key components that you will need to decide on (and the compatible options that we've incorporated) are listed below:

1) **Computer** (Raspberry Pi, NVIDIA Jetson Orin Nano)
2) **Power source** (drill battery, LiPo battery, power bank for separate computer power if desired)
3) **Actuator** (CubeMars AK-Series, CyberGear Micromotor, RobStride)
4) **Sensors** (Microstrain IMUs, OpenIMUs, MPU9250 IMUs)

## Set Up Your Single Board Computer

To begin this step, you'll need your computer and an SD card.

In this step, you'll set up the hardware, OS, and software for your computer. You should follow the instructions on the [Single Board Computers](Computer) page, which will include information for both Raspberry Pi and NVIDIA Jetson Orin Nano set up.

By the end of this step, you should have a functioning computer with Epically Powerful installed, ready to interface with your physical robotic components!  Then, continue on with the steps below.

## Assemble Your Mechatronics

To begin this step, you will need all of your components that you put together in the ordering guide.

In this step, you'll assemble the power and communication subsystems of your robot. The power subsystem will connect the needed battery or batteries along with needed accommodating components with your computer and actuators.  The communication subsystem will connect your computer with the actuators and sensors.

This part may be tricky because there are countless combinations of components that you can use to create your system.  We've outlined some of the key considerations and assembly instructions on the [Mechatronics](Mechatronics) page.

By the end of this step, you should have a fully connected system to interact with your actuators and sensors. Then, move on to getting your system operational!

## Configure Your Actuators

To begin this step, you will need a few different things depending on your actuator type:
* For CubeMars actuators, you will need your actuators, a computer running Windows, an R-Link, and CAN+UART wires that come with your actuator
* For RobStride or CyberGear, you will need your actuators, computer, and your wiring setup from the previous step

In this step, you will assign each actuator a unique CAN ID so that you are able to control multiple actuators at once. Follow the instructions on the [Actuators](Actuators) page.

By the end of this step, you should have a fully prepared system that is prepared for real-time operation!

## Test Your Epically Powerful Robot!

To begin this step, you will need your mechatronics system assembled and powered, with Epically Powerful installed and ready to go.

In this step, we'll verify that you can communicate with your actuators using Epically Powerful's test scripts. The tests scripts are automatically included in the Epically Powerful library. You should follow the instructions on the [Tests](Tests) page for guidance on how to use these tests to validate your operation.

By the end of this step, you will have a fully functioning system and will be ready to start coding your own controller! To start, you can reference our [Example Controllers](ExampleControllers) or start coding some of your own.




