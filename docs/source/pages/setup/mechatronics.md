(Mechatronics)=
# Mechatronics

The mechatronic system to run motors with your computer can be broken down into three main components: 
1.  **Computer:** Jetson (which requires 19V/1-3.5A) or RasPi (5V)
2.  **Actuator:** T-Motor AK-series actuator (which requires 20/24V, depending on the model), CyberGear Micromotor (~24V), or Robstride actuator (~24V)
3.  **Batteries:** Either a uniform power source (powers both computer and actuators) or two separate power sources

## Power System

**What you will need:**
- 12 gauge black and red wire
- XT30 connectors
- E-stop
- Fuse holder
- Fuse (TODO: Specs per system!)

- Buck converter (if using unified power for computer and actuators)
- Power bank connection cable (if using separate power for computer)
- Battery mount (if using drill battery)

:::{tip} Throughout the construction of your system, we recommend planning out where you want components to sit and adding length in the red/black wiring accordingly.  The "//" symbols throughout the diagrams are natural places to add length between components.

Additionally, we recommend adding XT30 male/female connections in your wiring setup to enable easy removal/replacement of any sections of the power setup that you may want to be modular or easily replaceable.
:::


REC - TRIM DOWN FUSE CABLES
BUCK CONVERTER BIDIRECTIONAL?
![tmotor1](/res/power_entiresetup.png)

### Power - Battery Connections
In the diagram below, we show 4 possible setups.  The only differences in these configurations is which battery you're using (lipo vs. drill) and if you're using unified or separate power for your computer.

If you're using a...
- **Lipo battery:** Solder black/red wire onto a female XT60 connector
- **Drill battery:** Solder black/red wire onto the corresponding black/red wire protruding from the 


**You will need:**
- Drill battery mount OR XT60 female connector

![tmotor1](/res/power_battery.png){width="700"}

### Power - Actuator Connections
:::{tip}  If you order the recommended fuse holders, we recommend trimming the included red wire because it is significantly less flexible that the generic 12-gauge red/black wire.
:::

First, you will need to check which XT30 connector your actuator uses. For older models of the TMotor AK-Series, this is a standard XT30 connector. However, the V3 devices along with the Robstride and Cybergear devices use an XT30 2+2 design, where the CAN bus wiring is directly integreated with the power connector



**You will need:**
- 12 gauge black and red wire
- E-stop
- Fuse holders and fuses (number needed = number of actuators)
- XT30 male connectors (number needed = number of actuators)

![tmotor1](/res/power_actuators.png){width="500"}



### Power - Computer Connections
If you're using
![tmotor1](/res/power_computer.png){width="700"}


**You will need:**
- 12 gauge black and red wire
- Buck converter
- Fuse holder and fuse
- Computer power cable (barrel jack, micro-USB, OR USB-C)


## Actuator Communication System

![install_ep](/res/comms_entiresetup.png)

























TODO: TUNE BUCK CONVERTER??
 

