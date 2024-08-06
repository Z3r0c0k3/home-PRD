import asyncio
import subprocess
import time
from playsound import playsound
import RPi.GPIO as GPIO
import bluetooth
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes

# 전역 변수
last_sent_message_id = None
restart_flag = False
target_ip = "192.168.1.3"  # PING IP 주소
btn_pin = 17

# Bluetooth 설정
server_mac_address = "YOUR_BLUETOOTH_MAC_ADDRESS"
port = 1

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(btn_pin, GPIO.IN)

def send_bluetooth_signal(message):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((server_mac_address, port))
        sock.send(message)
        sock.close()
    except bluetooth.btcommon.BluetoothError as err:
        print("Bluetooth Error:", err)

def ping_and_check(target_ip):
    response = subprocess.run(["ping", "-c", "3", target_ip], capture_output=True, text=True)
    return response.returncode == 0

def play_audio(file_path):
    try:
        playsound(file_path)
    except playsound.PlaysoundException as e:
        print("Audio Error:", e)

async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, message_text, reply_markup=None):
    global last_sent_message_id
    chat_id = 5316086823

    if last_sent_message_id:
        await context.bot.delete_message(chat_id=chat_id, message_id=last_sent_message_id)

    sent_message = await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)
    last_sent_message_id = sent_message.message_id

async def callback_listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()
    global restart_flag

    if query.data == "normal":
        play_audio("audio/shutdown.mp3")
        await send_telegram_message(context, "정상 종료 처리되었습니다.")
        while True:
            if ping_and_check(target_ip):
                play_audio("audio/server_reconnected.mp3")
                await send_telegram_message(context, "서버가 온라인 상태입니다.")
                restart_flag = True
                break
            await asyncio.sleep(1)
    elif query.data == "recovery":
        play_audio("audio/remote_recovery.mp3")
        await send_telegram_message(context, "시스템 복구 로직을 진행합니다.")
        send_bluetooth_signal("start_server")
        await asyncio.sleep(60)
        while True:
            if ping_and_check(target_ip):
                play_audio("audio/server_reconnected.mp3")
                await send_telegram_message(context, "서버가 온라인 상태입니다.")
                restart_flag = True
                break
            await asyncio.sleep(1)

async def check_ping(context: ContextTypes.DEFAULT_TYPE):
    global restart_flag
    if not ping_and_check(target_ip):
        keyboard = [
            [
                InlineKeyboardButton("정상 종료", callback_data="normal"),
                InlineKeyboardButton("시스템 복구", callback_data="recovery"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_telegram_message(
            context,
            "서버가 오프라인입니다. 서버명: Proxmox\n아래 버튼을 눌러 처리하십시오.",
            reply_markup=reply_markup
        )

        # 버튼 입력 대기 및 처리 (callback_listener에서 처리)
        while not restart_flag:
            await asyncio.sleep(1)
        restart_flag = False

async def handle_button_press(context: ContextTypes.DEFAULT_TYPE):
    global restart_flag
    while True:
        if GPIO.input(btn_pin) == GPIO.HIGH:
            await asyncio.sleep(5)
            if GPIO.input(btn_pin) == GPIO.HIGH:
                # 정상 종료 로직 (버튼)
                play_audio("audio/shutdown.mp3")
                while True:
                    if ping_and_check(target_ip):
                        play_audio("audio/server_reconnected.mp3")
                        break
                    await asyncio.sleep(1)
            else:
                # 시스템 복구 로직 (버튼)
                play_audio("audio/button_recovery.mp3")
                send_bluetooth_signal("start_server")
                await asyncio.sleep(60)
                while True:
                    if ping_and_check(target_ip):
                        play_audio("audio/server_reconnected.mp3")
                        break
                    await asyncio.sleep(1)
            restart_flag = True
            break

async def main():
    application = ApplicationBuilder().token("7462646393:AAF2M9Isx-g4pudj32DIEgXLkVFZI8vxzGE").build()

    application.job_queue.run_repeating(check_ping, 1.0)
    application.job_queue.run_repeating(handle_button_press, 0.2)  # 버튼 입력 확인 주기 단축

    application.add_handler(CallbackQueryHandler(callback_listener))

    await application.initialize()
    await application.start()

if __name__ == '__main__':
    asyncio.run(main())
