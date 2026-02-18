"""
모드 시스템 + 접근 제어 (간소화 버전)
PRACTICE / LIVE 모드 분리
"""
import os

class ModeSystem:
    def __init__(self):
        self.mode = os.getenv('TRADING_MODE', 'PRACTICE')
    
    def get_mode(self):
        return self.mode
    
    def is_practice(self):
        return self.mode == 'PRACTICE'
    
    def is_live(self):
        return self.mode == 'LIVE'

mode_system = ModeSystem()
