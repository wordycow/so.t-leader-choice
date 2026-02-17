#!/bin/bash

echo "🔧 OpenAI API 설정 스크립트"
echo "================================"
echo ""
echo "OpenAI API 키를 입력하세요:"
echo "(예: sk-proj-abc123...)"
echo ""
read -p "API Key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ API 키가 입력되지 않았습니다"
    exit 1
fi

# .env 파일 생성
cat > .env << ENVEOF
# OpenAI API 설정
OPENAI_API_KEY=$API_KEY
OPENAI_MODEL=gpt-3.5-turbo

# AI 백엔드
AI_BACKEND=local
AUTO_FALLBACK=true

# 로컬 AI
LOCAL_AI_HOST=https://infinite-keno-casinos-constantly.trycloudflare.com
LOCAL_AI_MODEL=qwen2.5:7b
ENVEOF

echo ""
echo "✅ .env 파일 생성 완료!"
echo ""
echo "🔄 서버 재시작 중..."

# 기존 서버 종료
pkill -f "python.*upbit-smart-bot"

# 새 서버 시작
nohup python3 upbit-smart-bot-v8.0-ULTIMATE.py > server.log 2>&1 &

echo ""
echo "⏳ 5초 대기..."
sleep 5

# 서버 확인
if ps aux | grep -v grep | grep "upbit-smart-bot" > /dev/null; then
    echo "✅ 서버 실행 중!"
    echo ""
    echo "🎉 설정 완료!"
    echo ""
    echo "테스트 URL: https://5000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai"
    echo "로그인: wordycow / 1234"
    echo ""
    echo "이제 이메이와 대화해보세요! 😊"
else
    echo "❌ 서버 시작 실패"
    echo "로그 확인: tail -100 server.log"
fi
