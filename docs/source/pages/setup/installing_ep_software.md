(PythonEnvs)=
# Installing EP Software

## Requirements
- Internet connection
- Monitor with DisplayPort connection
- Mouse & Keyboard
- Github account

## Installing Epically Powerful Python Package
1)	From epically-powerful github, clone the repository or download as a zip file (and unzip to desired location)

![install_ep](/res/install_ep.png)

2)	Open a terminal (click on terminal app or ctrl+alt+t)
3)	cd into the epically-powerful folder and run the command pip install -e . The period in that command is supposed to be there, it's not a typo.

:::{tip} 
If you get an error that says something like "editable install is not supported", run the command ```pip install pip -U```
:::

4)	Now, you will be able to import “epicallypowerful” to the top of your scripts to use the various tools. Consult the ‘tests’ folder for examples and demonstrations.
