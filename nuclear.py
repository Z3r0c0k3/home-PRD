import RPi.GPIO as GPIO
from playsound import playsound
import time

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# MP3 파일 경로
mp3_file = "audio/nuclear.mp3"

try:
    while True:
        if GPIO.input(17) == GPIO.HIGH:
            playsound(mp3_file)  # playsound로 MP3 재생

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
