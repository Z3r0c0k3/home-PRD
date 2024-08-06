import subprocess
from gtts import gTTS

tts = gTTS(text="서버가 오프라인 입니다. 누전 차단기를 확인하고 버튼을 눌러 복구를 시작하세요.", lang="ko")
tts.save("./audio/stop_server.mp3")

# def play_message():
#     subprocess.call(["mpg321", "-q", "message.mp3"])