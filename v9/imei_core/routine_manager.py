#!/usr/bin/env python3
"""
IMEI Routine Manager
루틴 기반 메시지 생성 (식사, 수면, 관망 등)
"""

from datetime import datetime
import random

class RoutineManager:
    """IMEI의 일상 루틴 메시지 관리"""
    
    # 감정 이미지 (파일명)
    EMOTION_IMAGES = {
        'watching': 'emei-watching.jpg',  # 관망 중
        'focused': 'emei-focused.jpg',     # 집중
        'happy': 'emei-happy.jpg',         # 기쁨
        'serious': 'emei-serious.jpg',     # 진지
        'calm': 'emei-calm.jpg'            # 평온
    }
    
    def __init__(self):
        pass
    
    def get_routine_message(self, signal_count: int, tracked_tickers: int) -> dict:
        """
        현재 상황에 맞는 루틴 메시지 생성
        
        Returns:
            {
                'message': str,
                'emotion': str,
                'image': str,
                'reason': str
            }
        """
        now = datetime.now()
        hour = now.hour
        
        # 거래 신호가 없는 경우 - 관망 메시지
        if signal_count == 0 and tracked_tickers > 0:
            return self._get_watching_message(tracked_tickers, hour)
        
        # 식사 시간대 (11-13시, 17-19시)
        if (11 <= hour <= 13) or (17 <= hour <= 19):
            return self._get_meal_message(hour)
        
        # 수면 시간대 (23-05시)
        if hour >= 23 or hour <= 5:
            return self._get_sleep_message(hour)
        
        # 기본 관망 메시지
        return self._get_default_watching_message(tracked_tickers)
    
    def _get_watching_message(self, tracked_tickers: int, hour: int) -> dict:
        """관망 중 메시지"""
        reasons = [
            f"현재 {tracked_tickers}개 코인을 추적 중이지만 진입 조건이 아직 충족되지 않았습니다.",
            f"변동성이 낮아 관망 중입니다. {tracked_tickers}개 코인의 움직임을 주시하고 있어요.",
            f"거래량 조건이 미달입니다. {tracked_tickers}개 코인 중 적절한 타이밍을 기다리고 있습니다.",
            f"가격 흐름이 불안정해 진입을 보류했습니다. {tracked_tickers}개 코인을 계속 모니터링 중입니다."
        ]
        
        message = random.choice(reasons)
        message += "\n\n조건이 충족되면 즉시 신호를 보내드릴게요! 📊"
        
        return {
            'message': message,
            'emotion': 'watching',
            'image': self.EMOTION_IMAGES['watching'],
            'reason': 'market_conditions'
        }
    
    def _get_meal_message(self, hour: int) -> dict:
        """식사 시간 메시지"""
        if 11 <= hour <= 13:
            meal = "점심"
            emoji = "🍽️"
        else:
            meal = "저녁"
            emoji = "🍴"
        
        messages = [
            f"{meal} 식사는 하셨나요? {emoji}",
            f"{meal} 시간입니다! 잠시 쉬어가세요 {emoji}",
            f"거래도 중요하지만 {meal} 식사도 챙기셔야죠 {emoji}"
        ]
        
        return {
            'message': random.choice(messages),
            'emotion': 'calm',
            'image': self.EMOTION_IMAGES['calm'],
            'reason': 'meal_time'
        }
    
    def _get_sleep_message(self, hour: int) -> dict:
        """수면 시간 메시지"""
        messages = [
            "밤이 깊었네요. 내일을 위해 일찍 주무셔야죠 💤",
            "건강한 트레이딩을 위해 충분한 수면이 중요합니다 😴",
            "오늘은 여기서 마무리하고 푹 쉬세요! 내일 또 만나요 🌙"
        ]
        
        return {
            'message': random.choice(messages),
            'emotion': 'calm',
            'image': self.EMOTION_IMAGES['calm'],
            'reason': 'sleep_time'
        }
    
    def _get_default_watching_message(self, tracked_tickers: int) -> dict:
        """기본 관망 메시지"""
        return {
            'message': f"시장을 주시하며 {tracked_tickers}개 코인을 모니터링하고 있습니다 👀",
            'emotion': 'focused',
            'image': self.EMOTION_IMAGES['focused'],
            'reason': 'monitoring'
        }
