#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════"
echo "🏆 Upbit Smart Bot v8.0 ULTIMATE"
echo "═══════════════════════════════════════════════════"
echo ""

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 오류: Python3가 설치되어 있지 않습니다.${NC}"
    echo ""
    echo "Python 3.8 이상을 설치하세요:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Python 확인 완료${NC}"
echo ""

# 의존성 확인 및 설치
echo "📦 필수 라이브러리 확인 중..."
if ! python3 -c "import pyupbit" &> /dev/null; then
    echo ""
    echo "📥 필수 라이브러리 설치 중..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}❌ 오류: 라이브러리 설치 실패${NC}"
        exit 1
    fi
    echo ""
    echo -e "${GREEN}✅ 라이브러리 설치 완료${NC}"
fi

echo -e "${GREEN}✅ 라이브러리 확인 완료${NC}"
echo ""

# config.json 확인
if [ ! -f "config.json" ]; then
    echo -e "${RED}❌ 오류: config.json 파일이 없습니다.${NC}"
    echo ""
    echo "config.json 파일을 생성하고 API 키를 입력하세요."
    echo ""
    exit 1
fi

# API 키 설정 확인
if grep -q "여기에_업비트" config.json; then
    echo ""
    echo -e "${YELLOW}⚠️  경고: API 키가 설정되지 않았습니다.${NC}"
    echo ""
    echo "config.json 파일을 열어 API 키를 입력하세요."
    echo "연습 모드로는 실행 가능하지만, 실전 모드는 API 키 필요합니다."
    echo ""
    echo "계속하려면 Enter를 누르세요..."
    read
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "🚀 봇 시작 중..."
echo "═══════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}웹 대시보드: http://localhost:5000${NC}"
echo ""
echo "봇을 중지하려면 Ctrl+C를 누르세요."
echo ""

# 봇 실행
python3 upbit-smart-bot-v8.0-ULTIMATE.py

echo ""
echo "═══════════════════════════════════════════════════"
echo "봇이 종료되었습니다."
echo "═══════════════════════════════════════════════════"
