"""
이메이 감정 감지 & 표정 전환 시스템
"""

def detect_emotion(text):
    """
    텍스트에서 감정을 감지합니다.
    
    Returns:
        str: 감정 이름 (happy, sad, angry, surprised, thinking, confident, loving, playful, neutral)
    """
    text = text.lower()
    
    # 감정 키워드 사전
    emotion_keywords = {
        'happy': ['좋아', '감사', '고마워', '최고', '훌륭', '완벽', '성공', '수익', '올랐', '상승', '익절', '대박'],
        'sad': ['아쉽', '슬프', '손실', '하락', '떨어졌', '손해', '실패', '망했', '걱정', '불안'],
        'angry': ['화나', '짜증', '실망', '최악', '멍청', '바보', '욕'],
        'surprised': ['헐', '진짜', '대박', '놀라', '믿을수없', '세상에', '와'],
        'thinking': ['생각', '고민', '어떻게', '궁금', '뭐', '왜', '언제', '어디', '질문'],
        'confident': ['자신', '확신', '믿어', '당연', '물론', '가능', '할수있', '문제없'],
        'loving': ['사랑', '좋아해', '이뻐', '예뻐', '귀여', '멋져', '최애', '좋아요'],
        'playful': ['ㅋㅋ', 'ㅎㅎ', 'ㅜㅜ', 'ㅠㅠ', '히히', '크크', '장난', '농담']
    }
    
    # 각 감정별 점수 계산
    emotion_scores = {}
    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            emotion_scores[emotion] = score
    
    # 가장 높은 점수의 감정 반환
    if emotion_scores:
        return max(emotion_scores, key=emotion_scores.get)
    
    return 'neutral'  # 기본: 중립 (beautiful-v1 사용)


def get_emotion_image(emotion):
    """
    감정에 맞는 이미지 파일 경로를 반환합니다.
    
    Args:
        emotion (str): 감정 이름
        
    Returns:
        str: 이미지 경로
    """
    emotion_images = {
        'happy': '/static/images/emei-emotion-happy.jpg',
        'sad': '/static/images/emei-emotion-sad.jpg',
        'angry': '/static/images/emei-emotion-angry.jpg',
        'surprised': '/static/images/emei-emotion-surprised.jpg',
        'thinking': '/static/images/emei-emotion-thinking.jpg',
        'confident': '/static/images/emei-emotion-confident.jpg',
        'loving': '/static/images/emei-emotion-loving.jpg',
        'playful': '/static/images/emei-emotion-playful.jpg',
        'neutral': '/static/images/emei-beautiful-v1.jpg'
    }
    
    return emotion_images.get(emotion, emotion_images['neutral'])


def analyze_conversation(user_message, ai_response):
    """
    사용자 메시지와 AI 응답을 분석하여 적절한 감정을 결정합니다.
    
    Args:
        user_message (str): 사용자 메시지
        ai_response (str): AI 응답
        
    Returns:
        dict: {
            'user_emotion': str,
            'ai_emotion': str,
            'user_image': str,
            'ai_image': str
        }
    """
    user_emotion = detect_emotion(user_message)
    ai_emotion = detect_emotion(ai_response)
    
    return {
        'user_emotion': user_emotion,
        'ai_emotion': ai_emotion,
        'user_image': get_emotion_image(user_emotion),
        'ai_image': get_emotion_image(ai_emotion)
    }


# 테스트
if __name__ == '__main__':
    test_messages = [
        "와 수익률 20% 올랐어! 대박이야!",
        "손실이 너무 커서 걱정돼...",
        "이 전략이 정말 효과 있을까?",
        "비트코인 언제 사야 해?",
        "너 진짜 똑똑하다 ㅋㅋㅋ",
    ]
    
    print("🎭 감정 감지 테스트\n")
    for msg in test_messages:
        emotion = detect_emotion(msg)
        image = get_emotion_image(emotion)
        print(f"메시지: {msg}")
        print(f"감정: {emotion}")
        print(f"이미지: {image}\n")
