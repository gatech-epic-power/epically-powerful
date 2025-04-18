# Setup conditional dependcies based on the platform -- Will not install the GPIO library if the platform is not a Raspberry Pi or Jetson Nano
from setuptools import setup
import platform

dependencies = ["numpy", "scipy", "python-can"]

machine_name = platform.uname().release.lower()

if "tegra" in machine_name:
    dependencies.append("Jetson.GPIO")
elif "rpi" in machine_name in machine_name:
    dependencies.append("RPi.GPIO")

setup(
    name="epicallypowerful",
    version="0.1.0",
    install_requires=dependencies,
)
