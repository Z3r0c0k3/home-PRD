import subprocess
from gtts import gTTS

tts = gTTS(text="전력 시스템 복구를 진행하고 서버를 시작합니다. 서버나 누전차단기를 조작하지 마세요.", lang="ko")
tts.save("./audio/button_recovery.mp3")

# def play_message():
#     subprocess.call(["mpg321", "-q", "message.mp3"])