"""
향상된 이메이 학습 시스템
- 아이에게 가르치듯 간단한 질문으로 학습
- 전체 대화 로그 저장 없이 핵심만 저장
- 사용자별 맞춤 응답
"""
from emei_learning import EmeiLearning, get_emei
from emei_persona_data import get_persona
import re

class EnhancedEmeiLearning:
    """향상된 이메이 - 아이 교육 방식 학습"""
    
    def __init__(self):
        self.base_emei = get_emei()
        self.persona = get_persona()
    
    def chat(self, user_id: str, message: str) -> dict:
        """향상된 대화 처리"""
        # 1️⃣ 사용자 패턴 분석 및 저장
        self.persona.analyze_user_message(user_id, message)
        
        # 2️⃣ 기본 응답 생성
        result = self.base_emei.chat(user_id, message)
        
        # 3️⃣ 이상한 입력 감지 및 학습 유도
        if self._is_unclear_input(message):
            clarification = self._ask_for_clarification(message)
            result['response'] = clarification
            result['learned'] = False
            return result
        
        # 4️⃣ 사용자 스타일에 맞춰 응답 조정
        result['response'] = self.persona.generate_response_with_style(
            user_id, result['response']
        )
        
        # 5️⃣ 상황별 트레이딩 조언 추가
        if any(word in message for word in ['손실', '손해', '마이너스', '물려', '잃었']):
            advice = self.persona.get_trading_advice("손실")
            result['response'] += f"\n\n{advice}"
        elif any(word in message for word in ['수익', '플러스', '익절', '올랐']):
            advice = self.persona.get_trading_advice("수익")
            result['response'] += f"\n\n{advice}"
        elif any(word in message for word in ['살까', '사도', '진입', '매수']):
            advice = self.persona.get_trading_advice("진입")
            result['response'] += f"\n\n{advice}"
        
        return result
    
    def _is_unclear_input(self, message: str) -> bool:
        """이상한 입력인지 판단"""
        # 너무 짧거나 의미 없는 입력
        if len(message.strip()) < 2:
            return True
        
        # 특수문자만 있는 경우
        if re.match(r'^[^\w\s가-힣]+$', message):
            return True
        
        # 숫자만 있는 경우
        if message.strip().isdigit():
            return True
        
        return False
    
    def _ask_for_clarification(self, message: str) -> str:
        """아이에게 묻듯이 의미 물어보기"""
        clarifications = [
            f"'{message}'가 무슨 뜻이에요? 💭 좀 더 자세히 말해주세요!",
            f"음... '{message}'는 처음 들어봐요! 🤔 어떤 의미인지 알려주실래요?",
            f"'{message}'를 이해하고 싶어요! 📚 예를 들어 설명해주시면 배울게요!",
            f"호기심 생겨요! '{message}'에 대해 가르쳐주시면 잘 기억할게요 💡"
        ]
        
        import random
        return random.choice(clarifications)
    
    def teach_simple(self, user_id: str, word: str, meaning: str):
        """간단한 단어/의미 학습"""
        # 핵심만 저장 - 전체 대화 로그 저장 안 함
        self.base_emei.save_knowledge(word, meaning, source="user_teaching", quality_score=0.9)
        
        return {
            "success": True,
            "response": f"알려주셔서 고마워요! '{word}'는 '{meaning}'이군요! 💜 잘 기억할게요!"
        }
    
    def get_user_stats(self, user_id: str) -> dict:
        """사용자별 통계"""
        pattern = self.persona.get_user_pattern(user_id)
        base_stats = self.base_emei.get_stats()
        
        return {
            **base_stats,
            "user_pattern": pattern,
            "persona_name": self.persona.persona['name'],
            "expertise": self.persona.persona['expertise']
        }


# 싱글톤
_enhanced_emei = None

def get_enhanced_emei():
    global _enhanced_emei
    if _enhanced_emei is None:
        _enhanced_emei = EnhancedEmeiLearning()
    return _enhanced_emei
