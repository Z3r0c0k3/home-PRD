import asyncio
import subprocess
import time
from playsound import playsound
import RPi.GPIO as GPIO
import bluetooth
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, JobQueue

# 설정 값
TELEGRAM_BOT_TOKEN = "7462646393:AAF2M9Isx-g4pudj32DIEgXLkVFZI8vxzGE"
TELEGRAM_CHAT_ID = 5316086823
TARGET_IP = "192.168.1.3"
BLUETOOTH_MAC_ADDRESS = "YOUR_BLUETOOTH_MAC_ADDRESS"
BUTTON_PIN = 17

# 전역 변수
last_sent_message_id = None
restart_flag = False

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)

# Bluetooth 통신 함수
def send_bluetooth_signal(message):
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((BLUETOOTH_MAC_ADDRESS, 1))  # 포트는 1로 가정
        sock.send(message)
        sock.close()
    except bluetooth.btcommon.BluetoothError as err:
        print(f"Bluetooth Error: {err}")

# 네트워크 연결 확인 함수
def ping_and_check(target_ip):
    response = subprocess.run(["ping", "-c", "3", target_ip], capture_output=True, text=True)
    return response.returncode == 0

# 오디오 재생 함수
def play_audio(file_path):
    try:
        playsound(file_path)
    except playsound.PlaysoundException as e:
        print(f"Audio Error: {e}")

# 텔레그램 메시지 전송 함수
async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, message_text, reply_markup=None):
    global last_sent_message_id
    if last_sent_message_id:
        await context.bot.delete_message(chat_id=TELEGRAM_CHAT_ID, message_id=last_sent_message_id)
    sent_message = await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message_text, reply_markup=reply_markup)
    last_sent_message_id = sent_message.message_id

# 텔레그램 버튼 콜백 처리 함수
async def callback_listener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()
    global restart_flag

    if query.data == "normal":
        # 정상 종료 로직
        play_audio("audio/shutdown.mp3")
        await send_telegram_message(context, "정상 종료 처리되었습니다.")
        while not ping_and_check(TARGET_IP):
            await asyncio.sleep(1)
        play_audio("audio/server_reconnected.mp3")
        await send_telegram_message(context, "서버가 온라인 상태입니다.")
        restart_flag = True
    elif query.data == "recovery":
        # 시스템 복구 로직
        play_audio("audio/remote_recovery.mp3")
        await send_telegram_message(context, "시스템 복구 로직을 진행합니다.")
        send_bluetooth_signal("start_server")
        await asyncio.sleep(60)  # 복구 시간 대기
        while not ping_and_check(TARGET_IP):
            await asyncio.sleep(1)
        play_audio("audio/server_reconnected.mp3")
        await send_telegram_message(context, "서버가 온라인 상태입니다.")
        restart_flag = True

# 네트워크 연결 상태 주기적 확인 함수
async def check_ping(context: ContextTypes.DEFAULT_TYPE):
    global restart_flag
    if not ping_and_check(TARGET_IP):
        keyboard = [[InlineKeyboardButton("정상 종료", callback_data="normal"), InlineKeyboardButton("시스템 복구", callback_data="recovery")]]
        await send_telegram_message(context, "서버가 오프라인입니다. 서버명: Proxmox\n아래 버튼을 눌러 처리하십시오.", InlineKeyboardMarkup(keyboard))
        while not restart_flag:
            await asyncio.sleep(1)
        restart_flag = False

# 버튼 입력 감지 및 처리 함수
async def handle_button_press(context: ContextTypes.DEFAULT_TYPE):
    global restart_flag
    if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        await asyncio.sleep(5)  # 5초 동안 버튼이 계속 눌려있는지 확인 (debounce)
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            # 정상 종료 로직 (버튼)
            play_audio("audio/shutdown.mp3")
        else:
            # 시스템 복구 로직 (버튼)
            play_audio("audio/button_recovery.mp3")
            send_bluetooth_signal("start_server")
        while not ping_and_check(TARGET_IP):
            await asyncio.sleep(1)
        play_audio("audio/server_reconnected.mp3")
        restart_flag = True

# 메인 함수
async def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).concurrent_updates(True).build()
    job_queue = application.job_queue
    job_queue.run_repeating(check_ping, 1.0)  # 1초마다 ping 확인
    job_queue.run_repeating(handle_button_press, 0.2)  # 0.2초마다 버튼 입력 확인

    application.add_handler(CallbackQueryHandler(callback_listener))

    await application.initialize()
    await application.start()

if __name__ == '__main__':
    asyncio.run(main())
