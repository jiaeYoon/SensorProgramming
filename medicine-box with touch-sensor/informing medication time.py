import RPi.GPIO as GPIO
import time
from datetime import datetime
import datetime
import os

touch_pin = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)

buzzer = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setwarnings(False)

pwm = GPIO.PWM(buzzer, 262)

medicine_times = ["16:50", "17:00", "20:37"]

def piezo_alarm():
    #pwm.start(0.01)
    time.sleep(5)
    #pwm.stop()
    return
    
def tts_alarm():
    return

def timer():
    start = time.time()
    now = time.time()
    interval_time = now - start
    interval_datetime = datetime.timedelta(seconds=interval_time)
    
    #while(interval_datetime < datetime.timedelta(minutes=10)):
    while(interval_datetime < datetime.timedelta(seconds=15)):
        #print(interval_datetime)
        if(isTouched(index_number)):
            return 1
        time.sleep(1)
        now = time.time()
        interval_datetime = datetime.timedelta(seconds=now-start)
        print("I'm in timer")
    return 0

#take0 = False
#take1 = False
#take2 = False
take = [0, 0, 0]

alarm_3times = 0

def isTouched(index_number):
    if(GPIO.input(touch_pin) == True):
        take[index_number] = True
        return 1
    return 0
        

while True:
    alarm_3times = 0
    now = time.strftime('%H' + ':' + '%M')
    
    if now in medicine_times:
        
        index_number = medicine_times.index(now)
        print("It is ", now)
        print("take index number : ", take[index_number])
        
        while (take[index_number] == False):
            if(GPIO.input(touch_pin) == True):
                print(now)
                print("Touched!")
                take[index_number] = True
                #alarm()
                time.sleep(60)
                break
            else:
                alarm_3times+=1
                if(alarm_3times > 3):
                    print(alarm_3times, "th alarm")
                    break
                piezo_alarm()
                if(timer()):
                    break
    else:
        print("not yet. It's ", now)
        time.sleep(1)
        continue