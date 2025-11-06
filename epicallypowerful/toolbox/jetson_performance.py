import os


def _rpi_or_jetson():
    import platform
    machine_name = platform.uname().release.lower()
    if "tegra" in machine_name:
        return "jetson"
    elif "rpi" in machine_name or "bcm" in machine_name or "raspi" in machine_name:
        return "rpi"

def increase_jetson_performance(verbose=False) -> bool:
    """Set the Jetson performance mode to use the maximum GPU power. Note, this is only applicable for Jetson devices, and will pass and return False otherwise.

    Args:
        verbose (bool, optional): If True, print verbose output. Defaults to False.

    Returns:
        bool: True if the performance mode was set, False otherwise.
    """
    if _rpi_or_jetson() == "jetson":
        if verbose:
            print("Setting jetson power mode and clock speed")
        os.system("sudo nvpmodel -m 0")
        os.system("sudo jetson_clocks")
        print("Jetson performance mode set")
        return True
    else:
        if verbose:
            print("Not running on a Jetson device, skipping performance mode settings")
        return False
