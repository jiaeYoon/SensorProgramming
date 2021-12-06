from flask import Flask, render_template, request, url_for
app = Flask(__name__, static_url_path='/static')

@app.route('/')
def main_get(num=None):
    return render_template('transfer.html', num=num)

###touch, piezo sensor setting###
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

medicine_times = [0] * 3
index_number=0
take = [0, 0, 0]
alarm_3times = 0

def piezo_alarm():
    pwm.start(0.01)
    time.sleep(5)
    pwm.stop()
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
    return 0

def isTouched(index_number):
    if(GPIO.input(touch_pin) == True):
        take[index_number] = True
        print("Touched")
        return 1
    return 0
        
@app.route('/write', methods=['POST', 'GET'])
def write(num=None, med_time1=None):
    
    #웹에서 입력받은 시간을 저장할 변수 초기화
    time1, time2, time3 = None
    
    #웹에서 입력받은 데이터를 파이썬 변수에 저장
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        time1 = request.args.get('med_time1')
        medicine_times[0] = time1
        time2 = request.args.get('med_time2')
        medicine_times[1] = time2
        time3 = request.args.get('med_time3')
        medicine_times[2] = time3
        print(medicine_times)
        
        prev_time = "00"
        
        while True:
            alarm_3times = 0
            now = time.strftime('%H' + ':' + '%M')
            
            if now in medicine_times:
                index_number = medicine_times.index(now)
                print("It is ", now)
                #print("take index number : ", take[index_number])
                
                alarm_3times = 0
                while (take[index_number] == False):
                    if(GPIO.input(touch_pin) == True):
                        print(now)
                        print("Touched!")
                        isTouched(index_number)
                        time.sleep(60)
                        break
                    else:
                        alarm_3times+=1
                        print(alarm_3times, "th alarm")
                        if(alarm_3times > 3):
                            break
                        piezo_alarm()
                        if(timer()):
                            break
            else:
                if(prev_time != now):
                    print("not yet. It's ", now)
                prev_time = now
                time.sleep(1)
                continue
            
    return render_template('transfer.html', med_time_1=time1, med_time_2=time2, med_time_3=time3)

if __name__ == '__main__':
    app.run()