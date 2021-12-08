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
from gtts import gTTS
import pygame

touch_pin = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)

buzzer = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setwarnings(False)

pwm = GPIO.PWM(buzzer, 262)

medicine_times = [0] * 3        # 입력받은 복약시간 저장
take = [False, False, False]    # 복약여부 표시
index_number = 0                # take[] array's index
alarm_3times = 0                # 재알림 횟수 저장(최대 3번 재알림)

# piezo 알림
def piezo_alarm():
    pwm.start(0.01)
    time.sleep(2)
    pwm.stop()
    return
    
# TTS 알림
def tts_alarm(h, m):
    time = str(h)+'시'+str(m)+'분'
    sText = "현재시각" + time + ": 복약 시간입니다."
    tts = gTTS(text=sText, lang='ko', slow = False)
    tts.save("tts.mp3")
    
    pygame.mixer.init()  #pygame 초기화
    pygame.mixer.music.load("tts.mp3")  #mp3 파일 불러와서 정의
    pygame.mixer.music.play()  #mp3 파일 한번 재생
    return

# 재알림 간격 10분을 재는 타이머
def timer():
    start = time.time()
    now = time.time()
    interval_time = now - start
    interval_datetime = datetime.timedelta(seconds=interval_time)
    
    #while(interval_datetime < datetime.timedelta(minutes=10)):
    while(interval_datetime < datetime.timedelta(seconds=20)):
        if(isTouched(index_number)):
            return 1
        time.sleep(1)
        now = time.time()
        interval_datetime = datetime.timedelta(seconds=now-start)
    return 0

# 터치 여부 판별 및 복용했음을 표시
def isTouched(index_number):
    if(GPIO.input(touch_pin) == True):
        take[index_number] = True
        print("Touched")
        return 1
    return 0

# 현재 시간을 가져옴
def get_time_now():
    now = time.strftime('%H' + ':' + '%M')  #'시:분'으로 시간 형식 맞춤
    return now

# 현재 시간에서 '시'를 구함
def get_hour_of_now():
    hour = int(time.strftime('%H'))
    return hour

# 현재 시간에서 '분'을 구함
def get_min_of_now():
    minute = int(time.strftime('%M'))
    return minute

# 현재 시간으로부터 1분 뒤 시간 구함
# 한 자리 숫자를 두자리 숫자로 시간 형식 맞춤(예: 8 -> 08)
def OneMinLaterFromNow(hour, minute):
    if((hour < 10) and (minute + 1 < 10)):
        min_later = '0' + str(hour) + ':0' + str(minute+1)
    elif((hour < 10) and (minute + 1 > 10)):
        min_later = '0' + str(hour) + ':' + str(minute+1)
    elif((hour > 10) and (minute + 1 < 10)):
        min_later = str(hour) + ':0' + str(minute+1)
    else:
        min_later = str(hour) + ':' + str(minute+1)
    return min_later

# 현재 시간에서 1분 지날때까지 기다림
def WaitUntilOneMinPassed(now, min_later):
    while(now != min_later):
        # print("sleeeep 10sec")
        time.sleep(5)
        now = get_time_now()
        # print(time.strftime('%H' + ':' + '%M' + ':' + '%S'))  # 10초 기다리기 지루해서 초 단위 확인용
    return
        
@app.route('/write', methods=['POST', 'GET'])
def write(num=None, med_time1=None):
    
    # 웹에서 입력받은 시간을 저장할 변수 초기화
    time1, time2, time3 = None
    
    # 웹에서 입력받은 데이터를 파이썬 변수에 저장
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        time1 = request.args.get('med_time1')
        medicine_times[0] = time1
        time2 = request.args.get('med_time2')
        medicine_times[1] = time2
        time3 = request.args.get('med_time3')
        medicine_times[2] = time3
        
        while True:
            now = get_time_now()                            # 현재 시간 받아옴
            hour = get_hour_of_now()                        # tts에 넣기 위해 변형
            minute = get_min_of_now()
            min_later = OneMinLaterFromNow(hour, minute)
            
            if now in medicine_times:
                index_number = medicine_times.index(now)            # match to check if user take medicine or not
                print("It is ", now, ". Time to take medicine")     # print present time
                tts_alarm(hour, minute)
                
                alarm_3times = 0                        # 재알람 횟수 초기화(최대 3번까지 알람 줌)
                while (take[index_number] == False):    # 약 복용하지 않았다면 계속 루프 돌림
                    if(GPIO.input(touch_pin) == True):  # 터치되면 <해당 타임에 복용했음을 표시> + <루프에서 빠져나옴>
                        #print(now)
                        #print("Touched!")
                        isTouched(index_number)         # 터치 됐음을 표시
                        WaitUntilOneMinPassed(now, min_later)         # 1분 지날때까지 쉼(복용여부 확인 while문(바로 상위) 빠져나갔을 때 시간이 1분 미만으로 지나있을 가능성을 대비)
                        break
                    
                    else:                               # 알람이 울리는 동안(?) 약통을 터치하지 않은 경우
                        alarm_3times+=1                 # 재알람
                        if(alarm_3times > 3):           # 최대 3번까지 재알람
                            break
                        print(alarm_3times, "th alarm")
                        piezo_alarm()
                        tts_alarm(int(get_hour_of_now()), int(get_min_of_now()))
                        if(timer()):                    # 10분에 한번씩 울리도록 10분을 재는 타이머(터치되면 그 즉시 1을 반환함)
                            if((alarm_3times == 1) and (now == time.strftime('%H' + ':' + '%M'))):  # 첫번째 재알림이고, 복약시간 알림으로부터 1분이 지나지 않은 경우
                                WaitUntilOneMinPassed(now, min_later)  
                            break                       # 타이머 리턴 값이 1이면 터치됐음을 의미, 루프에서 빠짐(여기서 계속 같은 시간일 경우는 고려?)
                        
            else:                                       # 약 먹을 시간이 아닌 경우
                print("not yet. It's ", now)            # 시간을 매초 측정하지만 1분에 한번씩만 복약시간이 아님을 알림
                WaitUntilOneMinPassed(now, min_later)
                time.sleep(1)                           # 복약시간인지 1초에 한 번씩 확인
            
    return render_template('transfer.html', med_time_1=time1, med_time_2=time2, med_time_3=time3)

if __name__ == '__main__':
    app.run()