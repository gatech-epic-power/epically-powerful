(Actuators)=
# Actuators

## T-Motor AK Series Actuators
The T-Motors in the system should run right out of the box with no issue. Each one has a default ID for CAN communication (usually CAN_ID = 0 or 1 by default). If there are multiple actuators in the system that are all connected over the same CAN wiring network, their CAN IDs must be differentiated so that commands to one are not interpreted by another. Each actuator's CAN ID can be set from 0-127 using the custom flashing software and serial port module (called Rubik Link or R-Link) from CubeMars (a sister brand of T-Motor). The version of the R-Link module and flashing software to use depends on the version of AK-series actuator being configured. The possible versions are V1.0 or V2.0. To determine which one the actuator is, simply check the CAN port on the actuator (see below). If the port has two pins, the actuator is V1.0. Four pins indicate V2.0. 

![tmotor1](/res/tmotor1.png){height="200"}


To change CAN IDs, the following components and packages are required:
1.  Computer running Windows 10 (11 may work, but has not been tested)
2.  T-Motor AK-series actuator(s)
3.  Power cable connecting battery to actuator(s) via E-stop (see Section: More About the Components)
4.  R-Link unit
a.  If V1.0: the silver serial port module will simply say "R-Link" on it.
b.  If V2.0: the silver metal serial port module will say "R-Link V2.0" on it.
5.  Actuator configuration software
a.  If V1.0: Use the "T-Motor configuration tool", which can be downloaded from T-Motor's website here. On the page, simply click the link indicated below at the bottom of the page for the "R-LINK upper computer installation program".
b.  If V2.0: Use the "CubeMars tool", which can be downloaded from CubeMars' website here. On the page, simply click the link indicated below at the bottom of the page for the "R-LINK V2.0 upper computer installation program".

To change CAN IDs, the following components and packages are required:
1.  Computer running Windows 10 (11 may work, but has not been tested)
2.  T-Motor AK-series actuator(s)
3.  Power cable connecting battery to actuator(s) via E-stop (see Section: More About the Components)
4.  R-Link unit
      - If V1.0: the silver serial port module will simply say "R-Link" on it.
      - If V2.0: the silver metal serial port module will say "R-Link V2.0" on it.
5.  Actuator configuration software
      - If V1.0: Use the "T-Motor configuration tool", which can be downloaded from T-Motor's website here. On the page, simply click the link indicated below at the bottom of the page for the "R-LINK upper computer installation program".
      - If V2.0: Use the "CubeMars tool", which can be downloaded from CubeMars' website here. On the page, simply click the link indicated below at the bottom of the page for the "R-LINK V2.0 upper computer installation program".

### Steps for Setting Up V1.0 Actuators

1.  Connect the R-Link module to the computer over USB and to the actuator's CAN and UART ports:
    ![tmotor11](/res/tmotor1_1.png){width="700"}

2.  To start up the configuration software:
      - Open Command Prompt (WIN+R and type `cmd` then hit ENTER)
      - Navigate to the directory in which the software is stored:
      `cd [CONFIGURATION DIRECTORY]`
      - Run the executable (example: `R-LINK Config Tool.exe` + ENTER)

3.  Set the COM port to the right serial connection for the R-Link unit
    ![tmotor12](/res/tmotor1_2.png){width="700"}

4.  In the "Configuration" tab, type in "s" to go to the "Setup" mode
    ![tmotor13](/res/tmotor1_3.png){width="700"}

5.  Type "i [CAN ID]" to change the CAN ID for the connected actuator

    ![tmotor14](/res/tmotor1_4.png){width="700"}

6.  Check actuator performance in the main tab

    ![tmotor15](/res/tmotor1_5.png){width="700"}

### Steps for setting up V2.0 actuators

1.  Connect the R-Link module to the computer over USB and to the actuator's CAN and UART ports:
    ![tmotor21](/res/tmotor2_1.png){width="700"}

2.  To start up the configuration software:
      - Open Command Prompt (WIN+R and type `cmd` then hit ENTER)
      - Navigate to the directory in which the software is stored: `cd [CONFIGURATION DIRECTORY]`
      - If the executable ends with ".downloading", it can still run. For formality, the executable can be renamed by deleting the ".downloading" portion. As long as the filetype is still ".exe", then it can be executed without issue.
      - Run the executable (Example: `CubeMarstool_V1.32.exe` + ENTER)
3.  Change the application language from Mandarin to English
     ![tmotor22](/res/tmotor2_2.png){width="700"}

4.  Set the COM port to the right serial connection for the R-Link unit
     ![tmotor23](/res/tmotor2_3.png){width="700"}
 
5.  Once it connects, set the actuator mode to "Bootloader Mode"
     ![tmotor24](/res/tmotor2_4.png){width="700"}

6.  Next, set the actuator to Mit Mode
     ![tmotor25](/res/tmotor2_5.png){width="700"}

7.  Move to the debugging terminal in MIT mode to change the CAN ID
     ![tmotor26](/res/tmotor2_6.png){width="700"}
 
8.  Change the CAN ID with the command set_can_id [CAN ID] 
     ![tmotor27](/res/tmotor2_7.png){width="700"}
 
9.  Check the performance of the actuator using the "Waveform display" output. 

      To check whether the CAN ID is properly set, in step 1: set ID to what the actuator ID should be. In step 2, keep all parameter values at 0. 

      To check two-way communication and command changes, in step 2: set "des P" = 0.5, "KP" = 1, "KD" = 0.1. Keep other boxes ("des S", "des T") set to 0. If you don't get responses from these values, you can slowly increase them, starting with "KP".
      :::{caution}
      Make sure to limit the output shaft's range of motion and keep a hand on the E-stop in case the motor response is too aggressive.
      :::
      ![tmotor28](/res/tmotor2_8.png){width="700"}

## Robstride Actuators & Cybergear Micromotors
The Robstride and Cybergear branded actuators use the same underlying control protocol, so for all setup steps they will be identical. Do take note of the actual spec differences between all the RS0# series actuators and the Cybergear actuators in actual use.

### Steps for setting up the Cybergear and Robstride actuators
The Robstride & Cybergear Micromotor Actuators utilize a CAN bus protocol for control, and are set up to work correctly with the provided library out of the box. Each actuator has a pre-programmed CAN ID, which defaults to 127. In order to address more than one actuator simultaneously, you will need to re-configure the actuator IDs. Robstride provides a tool to configure the actuator IDs, along with other parameters, and to use this you will need the CAN bus USB adapter. 

Alternatively, if you do not have the adapter, EpicallyPowerful comes with a software tool for this. To use it, follow along with the wiring setup found [here](Mechatronics). Once you are able to connect your Robstride/Cybergear actuator to power and the CAN interface on your Raspberry Pi or Jetson, you can run `ep-robstride-setup` to launch a web GUI that will allow you to change the CAN ID of your actuator and perform some basic visualization to ensure everything is working smoothly.

1. Plug the acutators in and launch the setup tool
2. Select "Scan for actuators". This will attempt to find all actuators connected to the bus and their CAN IDs. If this fails to find your device, you likely have a wiring issue.
3. Now, use the bottom selector to change the CAN ID to a new desired one. This change will persist after power cycles.
4. You can click "Enable Device", which will begin allowing the device to stream data to the GUI. (TODO: work in progress)

At this point, your actuator will be ready to use with the set CAN ID using the EpicallyPowerful actuator utilities.


 

