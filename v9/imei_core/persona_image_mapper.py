"""
IMEI Persona-based Image Mapping System

Maps persona types to corresponding emotional images.
"""

# Persona → Image mapping
# TODO: Replace with individual images after splitting emei-happy-set.jpg and emei-serious-set.jpg
PERSONA_IMAGES = {
    # Bold Leader (대담한 리더) - 자신감, 결단력
    "bold_leader": {
        "default": "emei-happy-set.jpg",      # 임시: 자신감 있는 표정
        "decision": "emei-happy-set.jpg",     # 임시: 결단 내릴 때
        "greeting": "emei-happy-set.jpg",     # 임시: 인사할 때
    },
    
    # Warm Support (따뜻한 지원) - 부드러움, 공감
    "warm_support": {
        "default": "emei-happy-set.jpg",      # 임시: 미소
        "comfort": "emei-happy-set.jpg",      # 임시: 위로할 때
        "empathy": "emei-happy-set.jpg",      # 임시: 공감할 때
    },
    
    # Analytical Expert (분석 전문가) - 집중, 진지함
    "analytical_expert": {
        "default": "emei-serious-set.jpg",    # 임시: 집중하는 표정
        "analysis": "emei-serious-set.jpg",   # 임시: 분석 중
        "thinking": "emei-serious-set.jpg",   # 임시: 생각 중
    },
    
    # Risk Manager (리스크 관리자) - 경계, 걱정
    "risk_manager": {
        "default": "emei-serious-set.jpg",    # 임시: 걱정하는 표정
        "alert": "emei-serious-set.jpg",      # 임시: 경고할 때
        "cautious": "emei-serious-set.jpg",   # 임시: 주의를 줄 때
    },
    
    # Trading Analysis (거래 분석) - 차트 분석
    "trading_analysis": {
        "default": "emei-serious-set.jpg",    # 임시: 차트 보는 표정 (분석 중)
        "chart": "emei-serious-set.jpg",      # 임시: 차트 분석 중
        "data": "emei-serious-set.jpg",       # 임시: 데이터 확인 중
    },
    
    # Emotional Support (감정 지원) - 공감, 위로
    "emotional_support": {
        "default": "emei-happy-set.jpg",      # 임시: 부드러운 표정
        "comfort": "emei-happy-set.jpg",      # 임시: 위로할 때
        "encouragement": "emei-happy-set.jpg", # 임시: 격려할 때
    },
}

# Context → Image mapping (추가 컨텍스트 매핑)
# TODO: Replace with individual images
CONTEXT_IMAGES = {
    # Trading contexts
    "chart_analysis": "emei-serious-set.jpg",  # 임시: 분석 표정
    "profit": "emei-happy-set.jpg",            # 임시: 밝은 표정
    "loss": "emei-serious-set.jpg",            # 임시: 걱정 표정
    "risk_warning": "emei-serious-set.jpg",    # 임시: 놀람 표정
    
    # Emotional contexts
    "greeting": "emei-happy-set.jpg",          # 임시: 미소
    "encouragement": "emei-happy-set.jpg",     # 임시: 자신감
    "empathy": "emei-happy-set.jpg",           # 임시: 부드러움
    "concern": "emei-serious-set.jpg",         # 임시: 걱정
    
    # Decision contexts
    "decision_making": "emei-happy-set.jpg",   # 임시: 자신감
    "uncertainty": "emei-serious-set.jpg",     # 임시: 집중
    "analysis": "emei-serious-set.jpg",        # 임시: 진지함
}

def get_persona_image(persona_type: str, context: str = "default") -> str:
    """
    Get image filename based on persona and context.
    
    Args:
        persona_type: Persona type (e.g., "bold_leader")
        context: Specific context (e.g., "decision", "comfort")
        
    Returns:
        Image filename (e.g., "emei-confident.jpg")
    """
    # Try persona-specific image first
    if persona_type in PERSONA_IMAGES:
        persona_map = PERSONA_IMAGES[persona_type]
        if context in persona_map:
            return persona_map[context]
        return persona_map.get("default", "emei-official.jpg")
    
    # Fallback to context-based image
    if context in CONTEXT_IMAGES:
        return CONTEXT_IMAGES[context]
    
    # Final fallback
    return "emei-official.jpg"


def detect_context_from_message(message: str) -> str:
    """
    Detect context from user message.
    
    Args:
        message: User message text
        
    Returns:
        Context string
    """
    message_lower = message.lower()
    
    # Trading keywords
    if any(word in message for word in ["차트", "분석", "그래프", "캔들"]):
        return "chart_analysis"
    if any(word in message for word in ["수익", "이익", "올랐"]):
        return "profit"
    if any(word in message for word in ["손실", "손해", "떨어졌", "하락"]):
        return "loss"
    if any(word in message for word in ["위험", "조심", "경고"]):
        return "risk_warning"
    
    # Emotional keywords
    if any(word in message for word in ["안녕", "하이", "hi", "hello"]):
        return "greeting"
    if any(word in message for word in ["힘들", "어렵", "슬프"]):
        return "empathy"
    if any(word in message for word in ["걱정", "불안", "두렵"]):
        return "concern"
    
    # Decision keywords
    if any(word in message for word in ["해야", "할까", "어떻게"]):
        return "decision_making"
    if any(word in message for word in ["모르겠", "확실", "애매"]):
        return "uncertainty"
    
    return "default"
