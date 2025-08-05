#########################################
# Copyright (c) 2020 Maker Portal LLC
# Author: Joshua Hrisko
#########################################
#
# This code handles the smbus 
# communications between the RPi and the
# MPU9250 IMU. For testing the MPU9250
# see: imu_test.py
#
#########################################
#

import time
# import smbus # Older method
import smbus2 as smbus

# Set MPU6050 registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
ACCEL_CONFIG = 0x1C
INT_PIN_CFG  = 0x37
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
TEMP_OUT_H   = 0x41
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

# Set AK8963 registers
AK8963_ADDR  = 0x0C
AK8963_ST1   = 0x02
HXH          = 0x04
HYH          = 0x06
HZH          = 0x08
AK8963_ST1   = 0x02
AK8963_ST2   = 0x09
AK8963_CNTL  = 0x0A
AK8963_ASAX  = 0x10

# Set constants
MAG_SENS = 4800.0 # magnetometer sensitivity: 4800 uT


class MPU9250():
    def __init__():


    def _check_connected_imu(self):
        raise NotImplementedError


    def _set_up_connected_imu(self,
                                bus=bus,
                                address=MPU6050_ADDR,
                                pwr_mgmt_1=PWR_MGMT_1,
                                smplrt_div=SMPLRT_DIV,
                                config=CONFIG,
                                gyro_config=GYRO_CONFIG,
                                accel_config=ACCEL_CONFIG,
                                int_pin_cfg=INT_PIN_CFG,
                                int_enable=INT_ENABLE):
        # Reset sensor
        bus.write_byte_data(address, pwr_mgmt_1, 0x80)
        time.sleep(0.1)
        bus.write_byte_data(address, pwr_mgmt_1, 0x00)
        time.sleep(0.1)
        
        # Power management and crystal settings
        bus.write_byte_data(address, pwr_mgmt_1, 0x01)
        time.sleep(0.1)
        
        # Alter sample rate (stability)        
        samp_rate_div = 0 # sample rate = 8 kHz/(1+samp_rate_div)
        bus.write_byte_data(address, smplrt_div, samp_rate_div)
        time.sleep(0.1)
        
        # Write to configuration register
        bus.write_byte_data(address, config, 0)
        time.sleep(0.1)
        
        # Write to gyro configuration register
        gyro_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
        gyro_config_vals = [250.0,500.0,1000.0,2000.0] # [degrees/sec]
        gyro_indx = 0
        bus.write_byte_data(address, gyro_config, int(gyro_config_sel[gyro_indx]))
        time.sleep(0.1)
        
        # Write to accel configuration register
        accel_config_sel = [0b00000,0b01000,0b10000,0b11000] # byte registers
        accel_config_vals = [2.0,4.0,8.0,16.0] # [g (g = 9.81 m/s^2)]
        accel_indx = 0
        bus.write_byte_data(address, accel_config, int(accel_config_sel[accel_indx]))
        time.sleep(0.1)
        
        # Interrupt register (related to overflow of data [FIFO])
        bus.write_byte_data(address, int_pin_cfg, 0x22)
        time.sleep(0.1)
        
        # Enable the AK8963 magnetometer in pass-through mode
        bus.write_byte_data(address, int_enable, 1)
        time.sleep(0.1)
        
        return gyro_config_vals[gyro_indx],accel_config_vals[accel_indx]


    def read_raw_bits(self,
                        address=address,
                        register):
        # Read accel and gyro values
        high = bus.read_byte_data(address, register)
        low = bus.read_byte_data(address, register+1)

        # Combine high and low for unsigned bit value
        value = ((high << 8) | low)
        
        # Convert to +/- value
        if(value > 32768):
            value -= 65536
        return value


    def get_data(self):
        raise NotImplementedError




def convert_MPU6050():
    # raw acceleration bits
    acc_x = read_raw_bits(ACCEL_XOUT_H)
    acc_y = read_raw_bits(ACCEL_YOUT_H)
    acc_z = read_raw_bits(ACCEL_ZOUT_H)
    
    # raw gyroscope bits
    gyro_x = read_raw_bits(GYRO_XOUT_H)
    gyro_y = read_raw_bits(GYRO_YOUT_H)
    gyro_z = read_raw_bits(GYRO_ZOUT_H)

    #convert to acceleration in g and gyro dps
    a_x = (acc_x/(2.0**15.0))*accel_sens
    a_y = (acc_y/(2.0**15.0))*accel_sens
    a_z = (acc_z/(2.0**15.0))*accel_sens

    w_x = (gyro_x/(2.0**15.0))*gyro_sens
    w_y = (gyro_y/(2.0**15.0))*gyro_sens
    w_z = (gyro_z/(2.0**15.0))*gyro_sens
    
    return a_x,a_y,a_z,w_x,w_y,w_z


def AK8963_start():
    bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,0x00)
    time.sleep(0.1)
    bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,0x0F)
    time.sleep(0.1)
    coeff_data = bus.read_i2c_block_data(AK8963_ADDR,AK8963_ASAX,3)
    AK8963_coeffx = (0.5*(coeff_data[0]-128)) / 256.0 + 1.0
    AK8963_coeffy = (0.5*(coeff_data[1]-128)) / 256.0 + 1.0
    AK8963_coeffz = (0.5*(coeff_data[2]-128)) / 256.0 + 1.0
    time.sleep(0.1)
    bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,0x00)
    time.sleep(0.1)
    AK8963_bit_res = 0b0001 # 0b0001 = 16-bit
    AK8963_samp_rate = 0b0110 # 0b0010 = 8 Hz, 0b0110 = 100 Hz
    AK8963_mode = (AK8963_bit_res <<4)+AK8963_samp_rate # bit conversion
    bus.write_byte_data(AK8963_ADDR,AK8963_CNTL,AK8963_mode)
    time.sleep(0.1)
    return [AK8963_coeffx,AK8963_coeffy,AK8963_coeffz] 
    

def AK8963_reader(register):
    # read magnetometer values
    low = bus.read_byte_data(AK8963_ADDR, register-1)
    high = bus.read_byte_data(AK8963_ADDR, register)
    # combine higha and low for unsigned bit value
    value = ((high << 8) | low)
    # convert to +- value
    if(value > 32768):
        value -= 65536
    
    return value


def AK8963_conv():
    # raw magnetometer bits
    while 1:
##        if ((bus.read_byte_data(AK8963_ADDR,AK8963_ST1) & 0x01))!=1:
##            return 0,0,0
        mag_x = AK8963_reader(HXH)
        mag_y = AK8963_reader(HYH)
        mag_z = AK8963_reader(HZH)

        # the next line is needed for AK8963
        if (bus.read_byte_data(AK8963_ADDR,AK8963_ST2)) & 0x08!=0x08:
            break
        
    #convert to acceleration in g and gyro dps
##    m_x = AK8963_coeffs[0]*(mag_x/(2.0**15.0))*MAG_SENS
##    m_y = AK8963_coeffs[1]*(mag_y/(2.0**15.0))*MAG_SENS
##    m_z = AK8963_coeffs[2]*(mag_z/(2.0**15.0))*MAG_SENS
    m_x = (mag_x/(2.0**15.0))*MAG_SENS
    m_y = (mag_y/(2.0**15.0))*MAG_SENS
    m_z = (mag_z/(2.0**15.0))*MAG_SENS
    return m_x,m_y,m_z


# start I2C driver
bus = smbus.SMBus(7) # start comm with i2c bus
time.sleep(0.1)
gyro_sens,accel_sens = MPU6050_start() # instantiate gyro/accel
time.sleep(0.1)
# AK8963_coeffs = AK8963_start() # instantiate magnetometer
time.sleep(0.1)


def main():
    raise NotImplementedError
