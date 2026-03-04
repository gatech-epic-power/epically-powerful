(ReviewingBasics)=
# Reviewing the Basics


Epically Powerful incorporates several tools that it will help to have familiarity with. Before jumping in to EP, it is important to understand these tools as well as what EP is intended and not intended to do. This will help you know where to look for solutions when troubleshooting, when to read the EP documentation, when to Google, and when to open a GitHub issue to report any possible bugs to our team. Before using EP, here are the main things you should be familiar with that will help things move along smoothly.  We will provide a quick overview:

- Python
- GitHub
- Ubuntu
- NVIDIA Jetson Orin Nano
- JetsonGPIO

For each of these components, plenty of documentation exists that is readily findable via Google (which is where most of the following startup guide comes from). We will link to that if it is a better explanation than we can give, but I will include most things you should know here.  This is meant to be a very quick overview, but we recommend reading further if desired.

## Python
Python is a high-level programming language, with a very English-language-like syntax. If you are familiar with other programming languages, Python is relatively easy to pick up. Most minor syntax details can be solved with a quick question to Google or ChatGPT. In our context, Python is the language that our controllers are written in, due to its easy-to-use libraries. If you are unfamiliar with Python, we recommend going over some basic tutorials before diving in to code your controller.


<style>
    .custom-button {
        background-color: #E03645;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: transform 0.2s ease-in-out;
    }
    .custom-button:hover {
        transform: scale(0.95); /* Shrinks the button */
    }
</style>

<button class="custom-button" onclick="window.open('https://www.py4e.com/lessons', '_blank');">
    Python tutorials
</button>

## Python Environments
One quirk of Python is that many computers use Python as the language to run essential components of the operating system, so if you try to use the default version of Python, you will be using that core executable. This can lead to issues and incompatibilities when trying to upgrade or downgrade your Python packages. To alleviate these issues, it is HIGHLY recommended to use some sort of Python virtual environment. This allows you to separate out environment needs for different projects, and save snapshots of that environment to recreate later. There are a few ways to do this, but these are the two that I recommend:
venv -simple venv is a Python tool that writes Python virtual environments. The syntax for this is simple and requires minimal setup.However, venv doesn’t let you change your version of Python very easily and is not as feature rich as the next option.
micromamba -better If you are at all familiar with Anaconda, micromamba/mamba is just an alternative version of that. This allows you not only to install Python packages, but can contain non-Python tools as well, and is faster to install than native anaconda/conda. I recommend this approach, and when you go to install, just make sure to follow the instructions according to your operating system (the Jetsons are Linux/Unix devices with ARM64 onboard architectures).

## GitHub
Git is a tool used to track changes to a project by allow you to commit groups of changes with messages. This can let you go back to old versions of a project, or temporarily branch off a test version of a project while still retaining a working version. GitHub is an online resource which allows you to remotely store Git projects. While often used synonymously, they are different, and understanding the differences can prevent some headaches later on. EP is stored on GitHub, allowing you to download and use an up-to-date version of that project. Similarly, you should also be saving your projects in a Git repository and uploading them to GitHub. Here, I have two main recommendations. The best way to do so depends on the operating system you are using:
Windows: use the GitHubdesktop app. It is way better at helping track commits, pushes and branches than using your brain/terminal commands. 
Linux:you only need to really learn the basic commands, which are to clone, pull, add, commit, push, and fetch.

## Ubuntu
This portion is shallower, but can be gone through more quickly. Ubuntu is an operating system you may all be familiar with (or at least have heard of). It is only really interesting in that it is Linux-based and the NVIDIA Jetson (and Raspberry Pi) models use a version of it as their operating system. Besides that the only thing that you really need to know is that it uses a package manager called apt. If you ever see tutorials or guides telling you to run sudo apt install whatever, it's basically just installing the `whatever` package from the Ubuntu app store.

## NVIDIA Jetson
The NVIDIA Jetson is a microprocessor with a GPU in it, making it useful to us for running real-time machine learning models. However, its unique GPU configuration is both a blessing and a curse, since its added capabilities are inexorably linked with much less online support than the similar Raspberry Pi. The Jetsons currently all use microSD card-based storage, which contains the operating system. (Side note: it is also possible to load an NVMe SSD board onto a Jetson in place of a microSD card, but these are more expensive and less common across the lab). Occasionally, you may end up messing something up on your device, which will require a reinstall of the operating system. This is a simple process with the SD card and a complicated process with the NVIDIA SDK. Most of the time, you will be using the SD card method, although occasionally you may need to use the NVIDIA SDK. If you do need to use that approach to upgrade to an even more recent version of Jetpack 6 (or to fix some hardware level issues on a brand new Jetson) please consult the PDF included with this doc (Or not, NVIDIA has recently provided new instructions so the SDK method is likely outmoded).

## Jetson.GPIO
Jetson.GPIO is a great example of what EP does not aim to do. Namely, things that already exist. JetsonGPIO provides a Python interface with the GPIO pins on the NVIDIA Jetson devices. It allows for setting input and output pins, interrupts, and even pulse width modulation (PWM) if you configure it correctly. This is the primary library you will need to utilize the hard-wire synchronization functionality from the Vicon systems that is included in the `epicpower/utils/triggers` portion of EP. You do not need to be completely comfortable with all the tools of Jetson.GPIO just now, but it is important that you know that it exists.

## CAN Commuication
CAN is a communication protocol, along with things like UART, I2C, and SPI.  One benefit of CAN is that each CAN object (sensor, actuator) can be configured to have a unique CAN ID, which essentially acts as the object that a message is addressed to.  This allows multiple CAN lines to be connected into one line, where the computer can send out a command that includes the CAN ID and only the only device to read it will be the device that the message is 'addressed' to.

When your computer sends out messages (such as sending a torque command to an actuator) or tries to receive messages (such as reading an encoder value from an actuator), it will only

TODO: WHY CAN
Actuators output a high/low CAN line (conventionally blue/white wires, respectively), which need to be converted to a CTX/CRX line before communicating with a computer.  We achieve that with a commercially available CAN transceiver.  This transceiver contains 6 pins: CAN high, CAN low, CTX, CRX, power, and ground.  One of the benefits of using CAN communication is the ability to daisy-chain your actuators.  






