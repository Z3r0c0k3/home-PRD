import subprocess
import threading
import time
from playsound import playsound
import RPi.GPIO as GPIO
import bluetooth
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

async def on_startup(application: Application):  
    await tg_button_message(application)

## 전역변수
last_sent_message_id = None
restart_flag = False
updater = Application.builder().token("7462646393:AAF2M9Isx-g4pudj32DIEgXLkVFZI8vxzGE").post_init(on_startup).build() # on_startup 연결

# Bluetooth 설정
server_mac_address = "YOUR_BLUETOOTH_MAC_ADDRESS"  # Bluetooth MAC 주소
port = 1
backlog = 1
size = 1024

def send_bluetooth_signal(message):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((server_mac_address, port))
        sock.send(message)
        sock.close()
    except bluetooth.btcommon.BluetoothError as err:
        print("Bluetooth Error:", err)

# 1. 기본 수행
def ping_and_check(target_ip):
    response = subprocess.run(["ping", "-c", "3", target_ip], capture_output=True, text=True)
    return response.returncode == 0

def play_audio(file_path):
    playsound(file_path)

def tg_button_message(application: Application) -> None:
    id = 5316086823
    keyboard = [
        [
            InlineKeyboardButton("정상 종료", callback_data="normal"),
            InlineKeyboardButton("시스템 복구", callback_data="recovery"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    global last_sent_message_id
    # 이전에 보낸 메시지가 있다면 삭제
    if last_sent_message_id:
        application.bot.delete_message(chat_id=id, message_id=last_sent_message_id)
        # 새로운 메시지 보내기
        sent_message = application.bot.send_message(chat_id=id, text="서버가 오프라인입니다. 서버명: Proxmox\n아래 버튼을 눌러 처리하십시오.", reply_markup=reply_markup)
        last_sent_message_id = sent_message.message_id
    else:
        application.bot.send_message(chat_id=id, text="서버가 오프라인입니다. 서버명: Proxmox\n아래 버튼을 눌러 처리하십시오.", reply_markup=reply_markup)

def callback_listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()
    global restart_flag
    callback = query.data
    if callback == "normal":
        play_audio("audio/shutdown.mp3")
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"정상 종료처리 되었습니다.")
        while True:
            if ping_and_check(target_ip):
                play_audio("audio/server_reconnected.mp3")
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"서버가 온라인 상태입니다.")
                restart_flag = True
                break
    elif callback == "recovery":
        play_audio("audio/remote_recovery.mp3")
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"시스템 복구 로직을 진행합니다.")
        send_bluetooth_signal("start_server")
        time.sleep(60)
        while True:
            if ping_and_check(target_ip):
                play_audio("audio/server_reconnected.mp3")
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"서버가 온라인 상태입니다.")
                restart_flag = True
                break
            time.sleep(1)

def main():
    global restart_flag
    POLLING_TIMEOUT = 10
    restart_flag = False

    while True:
        if not ping_and_check(target_ip):
            tg_button_message() # 텔레그램 메시지 전송 (이제 비동기가 아니므로 await 필요 없음)

            # 버튼 로직을 스레드로 실행
            button_thread = threading.Thread(target=handle_button)
            button_thread.start()

            # 텔레그램 폴링을 스레드로 실행
            telegram_thread = threading.Thread(target=updater.start_polling, args=(POLLING_TIMEOUT,))
            telegram_thread.start()

            # 두 스레드가 종료될 때까지 대기
            button_thread.join()
            telegram_thread.join()

        if restart_flag:
            restart_flag = False
            break

        time.sleep(1)

def handle_button():
    global restart_flag
    while True:
        if GPIO.input(btn_pin) == GPIO.HIGH:
            time.sleep(5)
            if GPIO.input(btn_pin) == GPIO.HIGH:
                ## 정상 종료 로직 (버튼)
                play_audio("audio/shutdown.mp3")
                while True:
                    if ping_and_check(target_ip):
                        play_audio("audio/server_reconnected.mp3")
                        break
                    time.sleep(1)
            else:
                ## 시스템 복구 로직 (버튼)
                play_audio("audio/button_recovery.mp3")
                send_bluetooth_signal("start_server")
                time.sleep(60)
                while True:
                    if ping_and_check(target_ip):
                        play_audio("audio/server_reconnected.mp3")
                        break
                    time.sleep(1)
            restart_flag = True
            break

if __name__ == '__main__':
    ## GPIO 설정
    btn_pin = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn_pin, GPIO.IN)

    ## PING IP 주소
    target_ip = "192.168.1.3"

    # 핸들러 등록
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_listener))

    # 텔레그램 봇 시작
    tg_button_message() # 텔레그램 초기 메시지 전송

    while True:
        main()