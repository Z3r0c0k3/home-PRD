import subprocess
from gtts import gTTS
from playsound import playsound
import re
import time

def get_ipv4_address(interface):
    """주어진 네트워크 인터페이스의 IPv4 주소를 가져옵니다."""
    try:
        result = subprocess.run(['ifconfig', interface], capture_output=True, text=True)
        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", result.stdout)
        if match:
            return match.group(1)
    except Exception as e:
        return f"Error getting {interface} address: {e}"

def speak_ipv4_addresses():
    """wlan0 및 eth0의 IPv4 주소를 음성으로 출력합니다."""
    playsound("audio/start.mp3", True)
    wlan0_address = get_ipv4_address('wlan0')
    eth0_address = get_ipv4_address('eth0')
    
    if wlan0_address == None:
        tts_wlan0 = gTTS(text=f"무선랜 주소는 할당되지 않았습니다.", lang='ko')
    else:
        tts_wlan0 = gTTS(text=f"무선랜 주소는 {wlan0_address}입니다.", lang='ko')
    
    if eth0_address == None:
        tts_eth0 = gTTS(text=f"유선랜 주소는 할당되지 않았습니다.", lang='ko')
    else:
        tts_eth0 = gTTS(text=f"유선랜 주소는 {eth0_address}입니다.", lang='ko')
    

    tts_wlan0.save("tmp/wlan0_address.mp3")
    tts_eth0.save("tmp/eth0_address.mp3")

    time.sleep(3)
    playsound("tmp/wlan0_address.mp3", True)  # True: 1.5배속 재생
    playsound("tmp/eth0_address.mp3", True)

if __name__ == "__main__":
    speak_ipv4_addresses()
