import subprocess
import time
from playsound import playsound
import RPi.GPIO as GPIO
import bluetooth
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

## 전역변수
last_sent_message_id = None
restart_flag = False
updater = Application.builder().token("7462646393:AAF2M9Isx-g4pudj32DIEgXLkVFZI8vxzGE").build()

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

async def tg_button_message(application: Application) -> None:
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
        await application.bot.delete_message(chat_id=id, message_id=last_sent_message_id)
        # 새로운 메시지 보내기
        sent_message = await application.bot.send_message(chat_id=id, text="서버가 오프라인입니다. 서버명: Proxmox\n아래 버튼을 눌러 처리하십시오.", reply_markup=reply_markup)
        last_sent_message_id = sent_message.message_id
    else:
        await application.bot.send_message(chat_id=id, text="서버가 오프라인입니다. 서버명: Proxmox\n아래 버튼을 눌러 처리하십시오.", reply_markup=reply_markup)

async def callback_listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    global restart_flag
    callback = query.data
    if callback == "normal":
        play_audio("audio/shutdown.mp3")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"정상 종료처리 되었습니다.")
        while True:
            if ping_and_check(target_ip):
                play_audio("audio/server_reconnected.mp3")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"서버가 온라인 상태입니다.")
                restart_flag = True
                break
    elif callback == "recovery":
        play_audio("audio/remote_recovery.mp3")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"시스템 복구 로직을 진행합니다.")
        send_bluetooth_signal("start_server")
        time.sleep(60)
        while True:
            if ping_and_check(target_ip):
                play_audio("audio/server_reconnected.mp3")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"서버가 온라인 상태입니다.")
                restart_flag = True
                break
            time.sleep(1)

async def on_startup(application: Application):  # post_init 대신 on_startup 사용
    await tg_button_message(application)

def main():
    global restart_flag
    global updater
    POLLING_TIMEOUT = 10

    while True:
        if not ping_and_check(target_ip):
            while True:
                play_audio("audio/stop_server.mp3")
                ## 버튼 로직
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
                ## 원격 처리 로직 
                updater.post_init(tg_button_message)
                updater.add_handler(CallbackQueryHandler(callback_listener))
                try:
                    asyncio.run(updater.start_polling(timeout=POLLING_TIMEOUT))
                except asyncio.TimeoutError:
                    pass  # 폴링 시간 초과 시 다음 반복으로 넘어감
        if restart_flag:
            restart_flag = False
            break

async def main_task():
    # 텔레그램 폴링을 백그라운드에서 실행
    await updater.start_polling()

if __name__ == '__main__':
    ## GPIO 설정
    btn_pin = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn_pin, GPIO.IN)

    ## PING IP 주소
    target_ip = "192.168.1.3"

    # 비동기 작업 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main_task())
    while True:
        main()