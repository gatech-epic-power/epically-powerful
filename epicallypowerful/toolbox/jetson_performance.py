import os

def jetson_performance() -> None:
    print("Setting jetson power mode and clock speed")
    os.system("sudo nvpmodel -m 0")
    os.system("sudo jetson_clocks")
    return
