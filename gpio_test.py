import RPi.GPIO as GPIO
import time

# GPIO 핀 번호 설정 (BCM 모드)
GPIO_PIN = 17  # 사용할 GPIO 핀 번호를 입력하세요.

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

while True:
    try:
        if GPIO.input(GPIO_PIN) == GPIO.HIGH:
            print("GPIO{} is HIGH".format(GPIO_PIN))
        else:
            print("GPIO{} is LOW".format(GPIO_PIN))
    
        # 0.5초마다 상태 확인
        time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("종료합니다.")
    
    finally:
        # GPIO 정리
        GPIO.cleanup()
