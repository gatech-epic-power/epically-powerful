#!/usr/bin/python3

"""
This code has been tested on Raspberry Pi 3B+ and 
NVIDIA Jetson Orin Nano with two MPU9250 units. Here, 
the magnetometer functionality has not been enabled as there are 
kernel issues with the current functionality of the 
AK8963 magnetometer boards on the MPU9250 units. 

TODO:
- Read in acceleration and gyro data
- Test on up to 7,8 MPU9250 units
- Perform operating frequency checks [UNNECESSARY BEYOND BASIC CHECK]
- Convert code into a set of class-based methods in the style of 
  the `microstrain_imus.py` code
- Incorporate temperature sensing for units
- Check calibration and sensor range code to ensure proper units 
  and startup
"""


import time
from smbus2 import SMBus

BUS = 7 # 0 for rev1 Raspberry Pi boards, 7 for NVIDIA Jetson Orin Nano
MULTIPLEXER_ADDR = 0x70
MPU9250_ADDR = 0x68
WHO_AM_I = 0x75
PWR_MGM_1 = 0x6b
SMP_DIV = 0x19
ACC_CONFIG = 0x1c
ACC_CONFIG2 = 0x1d
ACCX_H = 0x3b


def mpu9250_init(bus, device, pwr_mgm_1=PWR_MGM_1, smp_div=SMP_DIV, acc_config=ACC_CONFIG, acc_config2=ACC_CONFIG2):
	bus.write_byte_data(device, pwr_mgm_1,0x00)
	bus.write_byte_data(device, smp_div,0x00)
	bus.write_byte_data(device, acc_config,0x00)
	bus.write_byte_data(device, acc_config2,0x00)


def read_mpu(bus, device):
	raw = bus.read_i2c_block_data(device, 0x3b, 6)
	ax = (float)((raw[0]<<8|raw[1])) / 2048	
	ay = (float)((raw[2]<<8|raw[3])) / 2048	
	az = (float)((raw[4]<<8|raw[5])) / 2048
	
	return ax,ay,az

if __name__ == "__main__":
	bus = SMBus(BUS)
	mpu9250_init(bus=bus, device=MPU9250_ADDR)

	# Iterate through connected IMUs, reading in data
	while True:
		ax,ay,az = read_mpu(bus=bus, device=MPU9250_ADDR)
		
		print(f"IMU (x,y,z): ({ax:.2f}, {ay:.2f}, {az:.2f})")
			
		time.sleep(0.1)
		












