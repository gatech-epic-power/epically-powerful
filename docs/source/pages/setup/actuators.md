(Actuators)=
# Actuators

## CubeMars AK Series Actuators
The CubeMars actuators in the system should run right out of the box with no issue. Each one has a default ID for CAN communication (usually CAN_ID = 0 or 1 by default). If there are multiple actuators in the system that are all connected over the same CAN wiring network, their CAN IDs must be differentiated so that commands to one are not interpreted by another. Each actuator's CAN ID can be set from 0-127 using the custom flashing software and serial port module (called Rubik Link or R-Link) from CubeMars. The version of the R-Link module and flashing software to use depends on the version of AK-series actuator being configured (be sure to align actuator and R-Link version as described in the [Part Picker](PartPicker) section). The possible versions are V1.0, V2.0, or V3.0 (which may include additional versions in the future). To determine which one the actuator is, simply check the CAN port on the actuator (see below). If the port has two CAN pins, the actuator is V1.0. If it has four pins, the actuator is V2.0. If it has a combined two CAN/power port, the actuator is V3.0. See the diagram below for images of these ports.

![tmotor1](/res/tmotor1.png){height="200"}


To change CAN IDs, the following components and packages are required:
1.  Computer running Windows 10 (11 works with R-Link V2, but has not been tested with V1)
2.  CubeMars AK-series actuator(s)
3.  Power cable connecting battery to actuator(s) via E-stop (find setup information in the [Mechatronics](Mechatronics) section)
4.  R-Link unit
      * If V1.0: The silver serial port module will simply say "R-Link" on it (this may no longer be available)
      * If V2.0: The silver metal serial port module will say "R-Link V2.0" on it
      * If V3.0: The silver metal serial port module will say "R-Link V3.0" on it
5.  Actuator configuration software
    Various versions of the CubeMars configuration tool may or may not be available via the CubeMars website. We have all versions of the download on our [GitHub](https://github.com/gatech-epic-power/epically-powerful) page in the "CubeMars Configuration" folder.

### Steps for Setting Up V1.0 Actuators

1.  Connect the R-Link module to the computer via USB and to the actuator's CAN and UART ports
    ![tmotor11](/res/tmotor1_1.png){width="700"}

2.  To start up the configuration software:
      * Open Command Prompt (WIN+R and type `cmd` then hit ENTER)
      * Navigate to the directory in which the software is stored:
      `cd [CONFIGURATION DIRECTORY]`
      * Run the executable (example: `R-LINK Config Tool.exe` + ENTER)

3.  Set the COM port to the right serial connection for the R-Link unit
    ![tmotor12](/res/tmotor1_2.png){width="700"}

4.  In the "Configuration" tab, type in "s" to go to the "Setup" mode
    ![tmotor13](/res/tmotor1_3.png){width="700"}

5.  Type "i [CAN ID]" to change the CAN ID for the connected actuator

    ![tmotor14](/res/tmotor1_4.png){width="700"}

6.  In the main tab, check that actuator data is streaming and responding to movement of the output shaft

    ![tmotor15](/res/tmotor1_5.png){width="700"}

### Steps for setting up V2.0 actuators

1.  Connect the R-Link module to the computer via USB and to the actuator's CAN and UART ports
    ![tmotor21](/res/tmotor2_1.png){width="700"}

2.  To start up the configuration software:
      * Open Command Prompt (WIN+R and type `cmd` then hit ENTER)
      * Navigate to the directory in which the software is stored: `cd [CONFIGURATION DIRECTORY]`
      * If the executable ends with ".downloading", it can still run. For formality, the executable can be renamed by deleting the ".downloading" portion. As long as the filetype is still ".exe", then it can be executed without issue.
      * Run the executable (Example: `CubeMarstool_V1.32.exe` + ENTER)
3.  Change the application language from Mandarin to English (if you don't speak Mandarin)
     ![tmotor22](/res/tmotor2_2.png){width="700"}

4.  Set the COM port to the right serial connection for the R-Link unit
     ![tmotor23](/res/tmotor2_3.png){width="700"}
 
5.  Once it connects, set the actuator mode to "Bootloader Mode"
     ![tmotor24](/res/tmotor2_4.png){width="700"}

6.  Next, set the actuator to MIT Mode
     ![tmotor25](/res/tmotor2_5.png){width="700"}

7.  Move to the debugging terminal in MIT mode to change the CAN ID
     ![tmotor26](/res/tmotor2_6.png){width="700"}
 
8.  Change the CAN ID with the command set_can_id [CAN ID] 
     ![tmotor27](/res/tmotor2_7.png){width="700"}
 
9.  In the "Waveform display" tab, check that actuator data is streaming and responding to movement of the output shaft (follow the instructions in the image)
     ![tmotor28](/res/tmotor2_8.png){width="700"}

10. Check two-way communication and command changes
      * Set "des P" = 0.5, "KP" = 1, "KD" = 0.1, keep other boxes ("des S", "des T") set to 0
      * If you don't get responses from these values, you can slowly increase them, starting with "KP"

      :::{caution}
      Make sure to limit the output shaft's range of motion and keep a hand on the E-stop in case the motor response is too aggressive.
      :::
      

## Robstride Actuators & Cybergear Micromotors
The Robstride and Cybergear branded actuators use the same underlying control protocol, so for all setup steps they will be identical. However, you should note that these actuators of course may have different specifications (such as peak and rated torque, required voltage, etc.). The Robstride & Cybergear Micromotor Actuators utilize a CAN bus protocol for control, and are set up to work correctly with the provided library out of the box. Each actuator has a pre-programmed CAN ID, which defaults to 127. In order to address more than one actuator simultaneously, you will need to re-configure the actuator IDs. 

### Steps for setting up the Cybergear and Robstride actuators
Because Robstride requires an additional adapter for configuring CAN IDs, we created and included a adapter-less software tool in Epically Powerful with this functionality.
1. Ensure Epically Powerful is installed
2. Connect your Robstride or Cybergear actuator to power and the CAN interface on your Raspberry Pi or Jetson according to the the wiring setup found on the [Mechatronics](Mechatronics) page
3. Run `ep-robstride-setup` to launch our web GUI
4. Select "Scan for actuators"
      * This will attempt to find all actuators connected to the bus and their CAN IDs
      * If this fails to find your device, you likely have a wiring issue
5. Use the bottom selector to change the CAN ID to a new desired one

At this point, your actuator will be ready to use with the set CAN ID using the EpicallyPowerful actuator utilities.

Robstride provides a tool to configure the actuator IDs, along with other parameters, and to use this you will need the CAN bus USB adapter. If you want additional functionality that this provides (configure additional parameters, alter internal torque limits or current gains, etc.), you will need to use their tool.



 

