import subprocess
import time
import requests
import RPi.GPIO as GPIO
import bluetooth

# 텔레그램 봇 정보 설정
bot_token = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'
telegram_api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(0, GPIO.IN)  # GPIO 0 입력으로 설정
GPIO.setup(특정_핀_번호, GPIO.OUT)  # 서버 전원 제어 핀 출력으로 설정

# 블루투스 설정
bluetooth_address = 'YOUR_BLUETOOTH_ADDRESS'

# PING 대상 IP 설정
target_ip = 'YOUR_TARGET_IP'

def send_telegram_alert(message):
    data = {'chat_id': chat_id, 'text': message}
    requests.post(telegram_api_url, data=data)

def send_telegram_alert_with_buttons(message):
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "전력복구 및 서버 재시작", "callback_data": "restart"},
                {"text": "정상 종료", "callback_data": "shutdown"}
            ]
        ]
    }
    data = {
        'chat_id': chat_id,
        'text': message,
        'reply_markup': json.dumps(reply_markup)
    }
    requests.post(telegram_api_url, data=data)

def power_cycle_server():
    bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bluetooth_socket.connect((bluetooth_address, 1))  # 포트 번호는 필요에 따라 변경
    bluetooth_socket.send('power_cycle_command')  # 누전차단기 제어 명령 전송
    bluetooth_socket.close()
    time.sleep(10)  # 10초 대기
    GPIO.output(특정_핀_번호, GPIO.HIGH)  # 서버 전원 켜기

def ping_server():
    response = subprocess.call(['ping', '-c', '1', target_ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return response == 0

while True:
    if not ping_server():
        while True:
            send_telegram_alert_with_buttons("서버와의 연결이 끊어졌습니다. 서버 상태를 확인해주세요.\n서버명: Proxmox")
            time.sleep(60)  # 1분 대기
            if ping_server() or GPIO.input(0) == GPIO.HIGH:
                break
    if GPIO.input(0) == GPIO.HIGH:
        time.sleep(2)  # 2초 동안 버튼 입력 확인
        if GPIO.input(0) == GPIO.HIGH:
            power_cycle_server()
        else:
            if ping_server():
                send_telegram_alert("정상 종료가 확인되었습니다. 경보시스템을 종료합니다.")
            else:
                while not ping_server():
                    time.sleep(1)  # 1초 대기
                send_telegram_alert("서버와 연결되었습니다. 전력복구장치 작동을 재개합니다.")
    time.sleep(30)  # 30초 대기
