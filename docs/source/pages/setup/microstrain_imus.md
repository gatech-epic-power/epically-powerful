(MSCLInstall)=
# Microstrain IMU Library

The low level driver library for the Microstrain IMUs is maintained by Microstrain by HBK, and is routinely updated on [their github page](https://github.com/LORD-MicroStrain/MSCL). However, the installation is not automatically included with the pip or conda epicallypowerful install. Epicallypowerful can be used without it, however the microstain IMU functions and tools will not be available. **There are two options for installing the package**.

## epicallypoweful Install Helper
Epicallypowerful comes with a helper script that will attempt to automatically install the mscl dependency. Once you've installed epicallypowerful, run `ep-install-mscl`. By default, this will grab the version of MSCL that corresponds with your hardware and python version and attempt to install it into your base python environment. Additionally, if you are using a virtual environment or conda environment, you can run it with the `-E` flag, which will attempt to install it into your virtual environment, or you can use `-d` to manually specify a directory to copy the files into. After this, you will have access to the all the Microstrain IMU functionality.
```console
$ ep-install-mscl -E
```

## Manual
1) First, you need to download the installer. This is a .deb file hosted on the release page of the mscl github (https://github.com/LORD-MicroStrain/MSCL/releases). We recommend going one release back, as the library is only built for python 3.13 or 2.7 in the lastest builds. 
2) Once this is installed, running `sudo dpkg -i MSCL_<architecture>_Python<version>_v<release>.deb` will install the package to the base python installation inside its dist-packages folder. If you are not using a virtual environment, this is all you need to do, and can move on to actually building your robot!
3) If you have a virtual environment, you will need to copy the installed files into one of the folders in that path. If you are using venv or miniforge, the appropriate command will be `cp /usr/share/python3.<version>/dist-packages/*mscl* <path/to/env>


Once this mscl depencency is taken care of, you should be all ready to go with your epicallypowerful base robot!