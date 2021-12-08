import smbus			#import SMBus module of I2C
import time
from time import sleep
from twilio.rest import Client


#사용할 값들이 저장되는 레지스터 주소
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

#레지스터를 사용하기 위해 초기값 설정하는 메서드
#initilizing values to use register
def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

#레지스터에서 값 읽어오는 메서드
#read value from register
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

#레지스터에 초기값 입력
MPU_Init()


#initializing accel x,y value
#문의 움직임을 비교할 때 측정 전 문의 가속도
post_x = 0.0
post_z = 0.0

#check the time when the door is moving or not moving
#문이 움직인 시간과 멈춰있는 시간을 저장할 변수
movingTime = time.time()
stopTime = time.time()


#twilio 사용하기 위한 sid와 token
account_sid ='AC9e3a8c48be5b64a26dc9b5f20ee438ed'
auth_token = 'f74036107c72e2bdcb78ba6cb89b8346'
client = Client(account_sid, auth_token)


while True:
    #레지스터에서 읽어온 가속도 값
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)

    #레지스터에서 가져온 가속도 값 조정
    Ax = acc_x/16384.0
    Ay = acc_y/16384.0
    Az = acc_z/16384.0

    tmp_x = Ax
    tmp_z = Az

    #문이 움직이면 콘솔창에서 문이 움직였다는 메세지 출력
    if(abs(tmp_z-post_z)>0.05):
        print("The Door is Moving")
        movingTime = time.time()
    else:
        stopTime = time.time()


    #일정 시간 이상 문이 움직이지 않으면 보호자에게 비상 메세지 전달
    if(stopTime-movingTime>3):
        #86400 : 1day
        print("SIREN")
        message = client.messages.create(to="+821074232998", from_="+19062088820",body="긴급 문자 \n 000님의 움직임이 24시간동안 발견되지 않았습니다.\n보호자님의 확인이 필요합니다.")

        print(message.sid)
        break

    #현재의 가속도를 이전의 가속도를 저장하는 변수에 저장
    post_x = Ax
    post_z = Az

    #0.5초마다 while문 재실행
    sleep(0.5)
