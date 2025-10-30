(PythonEnvs)=
# Python Environment
Python virtual environments are a useful concept to employ when working with Python, particularly when a lot of dependencies are involved. For Epically Powerful, we recommend using some form of virtual environment, as this can prevent dependency conflicts with required system packages or other programs you may want to run on the same hardware. If you are confident that no other code will be run on your device, you can get away without one, but these are some easy options to get started with one.

Conda and venv are both options for operating virtual environments. Conda is typically preferable because it allows you to specify Python versions, which is why this is our recommended approach. However, both options are serviceable.

## Conda
Many data scientists may already be familiar with Anaconda. Anaconda is a collection of utility packages built on top of the conda package manager, which itself provides excellent tooling for virtual environments. To work with conda alone, there are several ways to get it installed, including [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main), [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html), and [miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install). 

While that's a lot of different options, we recommend [miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install) as it is community-supported and contains the conda-forge repository by default, which many packages are hosted on. To install, follow the instructions [here](https://conda-forge.org/download/). We summarize them below, but as always, the source documentation will be most up to date!

In short, you can go to the [conda-forge download page](https://conda-forge.org/download/), and grab the installer for your architecture. If you are on the Jetson or Raspberry Pi, your architecture is aarch64. Once downloaded, run `bash Miniforge3-$(uname)-$(uname -m).sh` to install miniforge.

Once installed, you can invoke the `conda` and `mamba` commands. To create an environment, run `conda create -n <name of environment> python=3.XX`. The Python version can be whatever you want, but please make it 3.9 or greater to work with Epically Powerful. To activate and use the environment, run `conda activate <name of environment>`. From there, run wild with installing all the packages you want. If things go wrong, it's simple enough to recreate/delete the old environment and start over, without impacting anything on your system. To deactivate the environment, run `conda deactivate`.

:::{note}
If you're using this environment for Epically Powerful, you do not need to install any other packages! When you `pip install epicallypowerful`, it will automatically download any needed package dependencies.
:::

Environments managed with conda can also use pip, and so 9 times out of 10, if there is a Python package you want, `pip install <the thing you want>` will work just fine.

## venv
Python has first-party support for virtual environments in the form of venv. The [documentation](http://docs.python.org/3/library/venv.html) is very comprehensive, and more detailed instructions can be found there. This tool lets you create virtual environments in a specific directory, typically located right next to your project. On most computers, venv must be first installed in your base Python installation. On Ubuntu-based systems, `sudo apt install python3-venv` should do the trick. Other systems should have this process readily documented online. Once venv is installed, you simply need to run the command `python3 -m venv <venv>`, replacing the `<venv>` with the desired name of your virtual environment. For many people, a simple structure is to have the virtual environment called `venv`, and to keep a `venv` folder in every single project that needs one. Once you've successfully run the command, you should have a folder in your directory with the name of your virtual environment. To use it, run `source <venv>/bin/activate`, which activates your environment and you should see a little `(<venv>)` next to your console prompt now. To deactivate it, run `deactivate`.

```console
$ sudo apt install python3-venv
$ cd <path/to/install/at>
$ python3 -m venv <nameofvenv>
```
