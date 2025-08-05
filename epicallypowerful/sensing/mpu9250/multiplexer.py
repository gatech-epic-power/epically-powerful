#!/usr/bin/python3

"""
This code has been tested on Raspberry Pi 3B+ and 
NVIDIA Jetson Orin Nano with two MPU9250 units. Here, 
the magnetometer functionality of the MPU9250 IMU has 
not been enabled as there are kernel issues with the 
current functionality of the AK8963 magnetometer boards 
on the MPU9250 units. 

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


class Multiplexer():
	def __init__(self, bus):
		self.bus = SMBus(bus)

	def channel(self, address=0x70, channel=0):
		# Values 0-7 indicate the channel, anything else (e.g. -1) turns off all channels	
		if (channel == 0):
			action = 0x01
		elif (channel == 1):
			action = 0x02
		elif (channel == 2):
			action = 0x04
		elif (channel == 3):
			action = 0x08
		elif (channel == 4):
			action = 0x10
		elif (channel == 5):
			action = 0x20
		elif (channel == 6):
			action = 0x40
		elif (channel == 7):
			action = 0x80
		else:
			action = 0x00

		self.bus.write_byte_data(address, 0x04, action) # 0x04 is the register for switching channels


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
	channels = [0,1]
	
	# Initialize multiplexer
	plexer = Multiplexer(bus=BUS)
	
	# Iterate through channels, setting up connected IMUs
	for c in channels:
		plexer.channel(address=MULTIPLEXER_ADDR, channel=c)
		mpu9250_init(bus=plexer.bus, device=MPU9250_ADDR)
		time.sleep(1)

	# Iterate through connected IMUs, reading in data
	while True:
		for c in channels:
			plexer.channel(address=MULTIPLEXER_ADDR, channel=c)
			
			ax,ay,az = read_mpu(bus=plexer.bus, device=MPU9250_ADDR)
			
			print(f"IMU {c} (x,y,z): ({ax:.2f}, {ay:.2f}, {az:.2f})")
			
			time.sleep(0.1)
		












