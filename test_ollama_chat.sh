#!/bin/bash

echo "🤖 노트북 Ollama에게 질문 중..."
echo ""

curl -s https://infinite-keno-casinos-constantly.trycloudflare.com/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "prompt": "안녕! 너는 누구야? 짧게 한 문장으로 대답해줘.",
    "stream": false
  }' | jq -r '.response'

echo ""
echo "✅ 응답 완료!"
