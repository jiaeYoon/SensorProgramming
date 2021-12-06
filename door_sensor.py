import smbus			#import SMBus module of I2C
import time
from time import sleep
import math
from twilio.rest import Client


#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
    #write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    #Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    #Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    #Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    #Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    #Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)

    #concatenate higher and lower value
    value = ((high << 8) | low)

    #to get signed value from mpu6050
    if(value > 32768):
        value = value - 65536
    return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

#alert when you start program
print (" Reading Data of Gyroscope and Accelerometer")

#initializing accel x,y value
post_x = 0.0
post_z = 0.0

#
movingTime = time.time()
stopTime = time.time()
account_sid ='AC9e3a8c48be5b64a26dc9b5f20ee438ed'
auth_token = 'f74036107c72e2bdcb78ba6cb89b8346'
client = Client(account_sid, auth_token)

while True:
    #Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)

    #Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x/16384.0
    Ay = acc_y/16384.0
    Az = acc_z/16384.0

    tmp_x = Ax
    tmp_z = Az

    if(abs(tmp_z-post_z)>0.05):
        print("The Door is Moving")
        movingTime = time.time()
    else:
        stopTime = time.time()

    if(stopTime-movingTime>3):
        #86400 : 1day
        print("SIREN")
        message = client.messages.create(to="+821074232998", from_="+19062088820",body="SIREN!")
        print(message.sid)
        break;

    #print("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g\n\n" %Az)
    post_x = Ax
    post_z = Az
    sleep(0.5)
