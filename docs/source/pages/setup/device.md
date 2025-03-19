(Devices)=
# Devices

This library is designed to be used on a linux computer, typically with GPIO capability. Most often, this is a verion of the Raspberry Pi device, a single board computer with wide community support. Additionally, we provide instructions for setup and use of this package with the Jetson Orin Nano device, which has built-in CAN bus capabilities and a more powerful GPU for machine learning or computer vision tasks. For details on exact parts needed for each setup, please consult the Parts Picker. Setup instructions for each device can be found below. 

:::{attention}
Please read through the entire section for you device before starting.
:::


## Required Components
* MicroSD card
* Computer able to use Balena Etcher or Raspberry Pi Imager
* Raspberry Pi and CAN enabling hat + HDMI cable

  OR
* Jetson Orin Nano and CAN transciever + Display Port Cable
* Keyboard + Mouse
* Monitor
* Power supply for device


(RPiSetup)=
## Raspberry Pi



### Basic Setup
The instructions on basic setup of the device are provided by the Raspberry Pi foundation [here](https://www.raspberrypi.com/documentation/). They will guide you through everything you need to get the computer up and running, depending on the version you have. One consideration is whether to use the full Raspberry Pi OS, or the Lite version. We typically recommended the full version, at least when getting started as it has a normal desktop environment and graphical tools to work with. The lite version, which does not include a graphical interface, can be useful if you need to squeeze out some extra processing power or memory for your application.

To move onto the next steps, please follow the Raspberry Pi documentation until you have your OS correctly installed, and are able to interact with the Pi's operating system, either through the GUI or terminal.

### Set Up CAN Bus capability
If you are not using any actuation (motors) in your application, you may skip this step.

1) First, double check what CAN bus enabling device you are using. Most likely it will be a [PiCAN2/3](https://copperhilltech.com/pican3-can-bus-board-for-raspberry-pi-4-with-3a-smps-and-rtc/) or the [Waveshare RS485 CAN Hat](https://www.waveshare.com/rs485-can-hat.htm). Either way, both are MCP2515 based devices, and require setting up its overlay in the device tree. 

   It it is **HIGHLY RECOMMENDED** that you consult the manufacturer's documentation on setup for the specific device, as new iterations and versions can require minor differences in setup. In general though, it will involve adding these lines to your `/boot/firmware/config.txt`. Make sure you edit as sudo or it will not allow you to save.

    ```
    dtparam=spi=on
    dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=2000000
    ```

2) Connect the CAN Hat and reboot the Raspberry Pi. Once this is done, you should have CAN bus available to you through the linux kernel's socketcan API. To enable it manually, you can use the following commands in your terminal. This however will be taken care of by epicallypowerful when you go to use it.
    ```bash
    $ sudo ip link set can0 up type can bitrate 1000000
    $ sudo ifconfig can0 txqueuelen 65536
    $ sudo ifconfig can0 up
    ````

3) **IF USING PICAN**. The PiCAN devices have a small input that needs to have some form of jumper wire soldered to it to connect the 120 Ohm terminating resistor to your CAN Bus. Without this, your CAN devices will not work. Please consult the following video on how we recommend this be done.

    ::::{youtube} ZmGDCIQdqTw
    ::::

### Python environment
While everything can be run using the system python environment, we highly recommend using some form of virtual environment, as incompatible versions and installed modules have the potential to interfere with operating system application if something goes wrong. Some options for this can be found [here](PythonEnvs).

### Microstrain Communication Library Setup
If you do not use the Microstrain IMUs in your application, you can skip this.

The low level interface library for communicating with the microstrain IMUs are currently unavailable through pip or anaconda, and must be installed manually. please see the specific guide for installing [here](MSCLInstall).

### Installing epicallypowerful
Now you are all ready to get up and running with epicallypowerful! To install, activate your virtual environment (if you're using one), and then use one of the methods below.
1) Clone the git repository, navigate into that directory using your terminal, and run 
   
   ```bash
   $ pip install -e .
   ```
   
   This will create a local editable installation of epicallypowerful, which will now be available to your python environment as long as you do not move this folder.
2) *NOT YET IMPLEMENTED*
   Simply directly install using
   ```bash
   $ pip install epicallypowerful
   ```

   OR

   ```bash
   $ conda install epicallypowerful -c conda-forge
   ```



(JetsonSetup)=
## Jetson Orin Nano

