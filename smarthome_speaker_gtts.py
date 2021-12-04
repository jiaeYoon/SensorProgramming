from gtts import gTTS
import pygame

def speak(h,m):
    time = str(h)+'시'+str(m)+'분'
    sText = "현재시각" + time + ": 복약 시간입니다."
    tts = gTTS(text=sText, lang='ko', slow = False)
    tts.save("tts.mp3")
    
    pygame.mixer.init()  #pygame 초기화
    pygame.mixer.music.load("tts.mp3")  #mp3 파일 불러와서 정의
    pygame.mixer.music.play()  #mp3 파일 한번 재생
    
h=1
m=18
speak(h,m)

