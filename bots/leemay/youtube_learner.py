# -*- coding: utf-8 -*-
"""
YouTube Learner Bot
유튜브에서 학습하는 봇
"""

import time
import os

print("📺 YouTube Learner Bot 시작됨!")
print(f"PID: {os.getpid()}")

# 무한 실행
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("YouTube Learner Bot 종료")
