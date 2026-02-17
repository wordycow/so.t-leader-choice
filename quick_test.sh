#!/bin/bash
# 🧪 빠른 연결 테스트

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧪 노트북 Ollama 연결 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "노트북 IP: 72.14.201.167"
echo "포트: 11434"
echo ""
echo "⏳ 연결 시도 중..."
echo ""

# 1. 기본 연결 테스트
if curl -s --connect-timeout 5 http://72.14.201.167:11434/api/tags > /dev/null 2>&1; then
    echo "✅ 연결 성공!"
    echo ""
    echo "📚 사용 가능한 모델:"
    curl -s http://72.14.201.167:11434/api/tags | python3 -c "
import sys, json
data = json.load(sys.stdin)
for model in data.get('models', []):
    size_gb = model['size'] / 1e9
    print(f\"   - {model['name']} ({size_gb:.1f}GB)\")
"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🎉 연결 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🚀 다음 단계:"
    echo "   1. 환경 변수 설정:"
    echo "      export AI_BACKEND=local"
    echo "      export LOCAL_AI_HOST=72.14.201.167"
    echo ""
    echo "   2. 전체 테스트:"
    echo "      python3 test_local_ai.py"
    echo ""
    echo "   3. Flask 실행:"
    echo "      pm2 restart upbit-bot"
    echo ""
    exit 0
else
    echo "❌ 연결 실패!"
    echo ""
    echo "💡 해결 방법:"
    echo ""
    echo "1. 노트북에서 Ollama 실행 확인:"
    echo "   PowerShell> ollama serve"
    echo ""
    echo "2. 환경 변수 설정 확인 (노트북):"
    echo "   PowerShell> \$env:OLLAMA_HOST = \"0.0.0.0:11434\""
    echo ""
    echo "3. 방화벽 포트 11434 열기 (노트북):"
    echo "   PowerShell> New-NetFirewallRule -DisplayName \"Ollama\" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow"
    echo ""
    echo "4. 같은 네트워크인지 확인"
    echo ""
    exit 1
fi
