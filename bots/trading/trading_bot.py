# -*- coding: utf-8 -*-
"""
Trading Bot
트레이딩 봇
"""

import time
import os

print("💹 Trading Bot 시작됨!")
print(f"PID: {os.getpid()}")

# 무한 실행
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Trading Bot 종료")
