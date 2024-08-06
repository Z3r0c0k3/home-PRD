# 0. 사용할 모듈 정의

- mp3 파일 스피커로 출력시, playsound 사용
- ping 요청은 subprocess 사용
- telegram 봇 관련은 python-telegram-bot  사용
- 나머지는 각각 적합한 모듈로 사용

# 1. 기본 수행

특정 IP로 PING 30초 당 3번씩 보내기.

## 1-1. PING 요청 후 정상적으로 응답이 오지 않으면

"audio/stop_server.mp3" 파일을 스피커로 출력하고 콜백이 오거나 GPIO 17에 입력이 있을 때까지 계속 1분에 1번씩 연결된 스피커로 출력되게 만들고 Telegram 봇으로 "서버와의 연결이 끊어졌습니다. 서버 상태를 확인해주세요. 서버명: Proxmox"라는 메시지와 '전력복구 및 서버 재시작' 버튼과 '정상 종료' 버튼을 보내고 버튼 콜백 또는 GPIO 17의 입력을 대기하기.

### 1-1-1. '전력 복구 및 서버 재시작' 콜백이 오면

"audio/remote_recovery.mp3" 파일을 스피커로 출력하고 wifi-direct로 누전 차단기에 있는 센서로 신호보내고 10초 정도 대기하다가 GPIO 27로 신호 출력해서 서버 전원 키기.

### 1-1-2. '정상 종료' 콜백이 오면

"audio/shutdown.mp3" 파일을 스피커로 출력하고 특정 IP로 PING을 3번이상 받을때까지 순차적으로 보내고 PING을 받으면 "server_recovery.mp3" 파일을 스피커로 출력하면서 '1.기본 수행' 단계로 되돌아가기.

### 1-2-1. GPIO 0에서 신호가 2초 미만 들어오면

"button_recovery.mp3" 파일을 스피커로 출력하고 wifi-direct로 누전 차단기 측 라즈베리 파이로 'recovery' 신호보내고 1분 정도 대기하다가 GPIO 27로 신호 출력해서 서버 전원 키기.

### 1-2-2. GPIO 0에서 신호가 5초 이상 들어오면

"audio/shudown.mp3" 파일을 스피커로 출력하고 특정 IP로 PING을 3번이상 받을때까지 순차적으로 보내고 PING을 받으면 "audio/server_reconnected.mp3" 파일을 스피커로 출력하고 "기본 수행" 단계로 되돌아가기.
