#!/bin/bash
echo "🧪 Emei API 테스트 (Named Tunnel 사용)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 로그인 (wordycow)
echo "1️⃣ 로그인..."
LOGIN_RESP=$(curl -s -c /tmp/cookies.txt http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wordycow"}')
echo "$LOGIN_RESP" | jq -r '.message // .username // "로그인 완료"'
echo ""

# DB 기반 답변 테스트
echo "2️⃣ DB 답변 테스트 (안녕)..."
DB_TEST=$(curl -s -b /tmp/cookies.txt http://localhost:5000/api/emei/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"안녕"}')
echo "$DB_TEST" | jq -r '.response // .message' | head -5
echo ""

# AI 생성 테스트 (새로운 질문)
echo "3️⃣ AI 생성 테스트 (비트코인 전망)..."
AI_TEST=$(curl -s -b /tmp/cookies.txt http://localhost:5000/api/emei/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"오늘 비트코인 시장 분위기는 어때?"}')
echo "$AI_TEST" | jq -r '.response // .message' | head -10
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 테스트 완료"
