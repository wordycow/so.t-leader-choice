#!/bin/bash
echo "🧪 Emei 프로필 학습 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 로그인
echo "1️⃣ 로그인..."
LOGIN_RESP=$(curl -s -c /tmp/cookies_profile.txt http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wordycow"}')
echo "$(echo "$LOGIN_RESP" | jq -r '.username // "로그인 완료"')"
echo ""

# Emei 나이 설정
echo "2️⃣ Emei 나이 설정: '너 나이는 25살이야'"
AGE_SET=$(curl -s -b /tmp/cookies_profile.txt http://localhost:5000/api/emei/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"너 나이는 25살이야"}')
echo "$(echo "$AGE_SET" | jq -r '.response')"
echo ""

# Emei 나이 질문
echo "3️⃣ Emei 나이 질문: '너 나이는?'"
AGE_ASK=$(curl -s -b /tmp/cookies_profile.txt http://localhost:5000/api/emei/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"너 나이는?"}')
echo "$(echo "$AGE_ASK" | jq -r '.response')"
echo ""

# 사용자 이름 학습
echo "4️⃣ 사용자 이름 학습: '내 이름은 이유송이야'"
NAME_SET=$(curl -s -b /tmp/cookies_profile.txt http://localhost:5000/api/emei/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"내 이름은 이유송이야"}')
echo "$(echo "$NAME_SET" | jq -r '.response')"
echo ""

# 자기소개 요청
echo "5️⃣ 자기소개 요청: '너는 누구야?'"
INTRO=$(curl -s -b /tmp/cookies_profile.txt http://localhost:5000/api/emei/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"너는 누구야?"}')
echo "$(echo "$INTRO" | jq -r '.response')"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 테스트 완료"
