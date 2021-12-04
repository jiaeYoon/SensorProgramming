import RPi.GPIO as GPIO
import signal
import sys
import time
import Adafruit_DHT

def signal_handler(signal, frame): #예외처리
    print('process stop')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

GPIO.setmode(GPIO.BCM)

DHT = 4
FAN = 21
GPIO.setup(FAN,GPIO.OUT)

while True:
    h,t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT) #온습도 측정 함수
    print('Humidity =', h)

    if(h > 10):                   #습도 기준값 설정
        GPIO.output(FAN,1)
    else:
        GPIO.output(FAN,0)
    #time.sleep(5)
    
