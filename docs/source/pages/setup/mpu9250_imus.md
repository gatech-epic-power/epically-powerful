(MSCLInstall)=
# MicroStrain IMU Library

The low level driver library for the MicroStrain IMUs is maintained by MicroStrain by HBK, and is routinely updated on [their github page](https://github.com/LORD-MicroStrain/MSCL). However, the installation is not automatically included with the pip or conda Epically Powerful install. Epically Powerful can be used without it, however the MicroStrain IMU functions and tools will not be available. **There are two options for installing the package**.

## Epically Powerful Install Helper
Epically Powerful comes with a helper script that will attempt to automatically install the MSCL dependency. Once you've installed Epically Powerful, run `ep-install-mscl`. By default, this will grab the version of MSCL that corresponds with your hardware and Python version and attempt to install it into your base Python environment. Additionally, if you are using a virtual environment or conda environment, you can run it with the `-E` flag, which will attempt to install it into your virtual environment, or you can use `-d` to manually specify a directory to copy the files into. After this, you will have access to the all the MicroStrain IMU functionality.

Run this to install the library:
```console
$ ep-install-mscl -E
```

## Manual
We recommend using the Epically Powerful installer, but in case you need the manual version for your application, we are providing that below.
1) First, you need to download the installer. This is a .deb file hosted on the release page of the [MSCL GitHub](https://github.com/LORD-MicroStrain/MSCL/releases). We recommend going one release back, as the library is only built for Python 3.13 or 2.7 in the latest builds.
2) Once this is installed, running `sudo dpkg -i MSCL_<architecture>_Python<version>_v<release>.deb` will install the package to the base Python installation inside its dist-packages folder. If you are not using a virtual environment, this is all you need to do, and can move on to actually building your robot!
3) If you have a virtual environment, you will need to copy the installed files into one of the folders in that path. If you are using venv or miniforge, the appropriate command will be `cp /usr/share/python3.<version>/dist-packages/*mscl* <path/to/env>`

Once this MSCL depencency is taken care of, you should be all ready to go with your Epically Powerful powered robot!