#!/bin/bash
# 🛡️ 트레이딩 봇 안전성 자동 체크 스크립트

echo "=========================================="
echo "🛡️ 트레이딩 봇 안전성 자동 체크"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_FILE="$SCRIPT_DIR/upbit-smart-bot-v8.0-ULTIMATE.py"

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 함수
check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARN_COUNT++))
}

echo "1️⃣ 투자 보호 체크"
echo "-------------------"

# 투자유의 종목 필터 체크
if grep -q "market_warning.*CAUTION" "$BOT_FILE" && \
   ! grep -q "except:.*pass.*# API 실패 시 그냥 진행" "$BOT_FILE"; then
    check_pass "투자유의 종목 필터 존재 (Fail-Safe)"
else
    check_fail "투자유의 종목 필터 미비 또는 except:pass 발견"
fi

# 최소 매수 금액 체크
if grep -q "invest_amount.*<.*5000" "$BOT_FILE"; then
    check_pass "최소 매수 금액 체크 (5,000원)"
else
    check_warn "최소 매수 금액 체크 누락 가능성"
fi

echo ""
echo "2️⃣ 손실 방지 체크"
echo "-------------------"

# 손절 로직 체크
if grep -q "profit_from_first" "$BOT_FILE" && \
   grep -q "dca_count > 0" "$BOT_FILE"; then
    check_pass "물타기 중 최초가 기준 손절 로직 존재"
else
    check_fail "물타기 손절 로직 누락"
fi

# 익절 로직 체크
if grep -q "take_profit" "$BOT_FILE"; then
    check_pass "익절 로직 존재"
else
    check_fail "익절 로직 누락"
fi

# 물타기 제한 체크
if grep -q "dca_count" "$BOT_FILE"; then
    check_pass "물타기 단계 관리"
else
    check_warn "물타기 제한 로직 확인 필요"
fi

echo ""
echo "3️⃣ 데이터 무결성 체크"
echo "-------------------"

# DB 저장 체크
if grep -q "strategy_perf_json" "$BOT_FILE" && \
   grep -q "save_bot_state_to_db" "$BOT_FILE"; then
    check_pass "전략 성과 DB 저장"
else
    check_fail "전략 성과 DB 저장 누락"
fi

# 거래 기록 저장 체크
if grep -q "save_trade_to_db" "$BOT_FILE"; then
    check_pass "거래 기록 DB 저장"
else
    check_fail "거래 기록 저장 누락"
fi

echo ""
echo "4️⃣ API 안전성 체크"
echo "-------------------"

# 위험한 except: pass 패턴 체크 (execute_trade 함수 내부만)
DANGEROUS_IN_TRADE=$(sed -n '/def execute_trade/,/^def /p' "$BOT_FILE" | grep "except:$" | wc -l)
if [ "$DANGEROUS_IN_TRADE" -eq 0 ]; then
    check_pass "거래 함수 내 위험한 'except:' 없음"
else
    check_fail "거래 함수에 위험한 'except:' ${DANGEROUS_IN_TRADE}개 발견"
fi

# Timeout 설정 체크
if grep -q "timeout.*=" "$BOT_FILE"; then
    check_pass "API Timeout 설정 존재"
else
    check_warn "API Timeout 설정 확인 필요"
fi

echo ""
echo "5️⃣ 수수료 & 계산 체크"
echo "-------------------"

# 수수료 계산 체크
if grep -q "FEE_RATE.*0.0005" "$BOT_FILE"; then
    check_pass "수수료 0.05% 설정"
else
    check_fail "수수료 설정 누락 또는 오류"
fi

# 수익률 계산 체크
if grep -q "profit_rate.*=.*current_price.*-.*price.*/" "$BOT_FILE"; then
    check_pass "수익률 계산 로직 존재"
else
    check_warn "수익률 계산 로직 확인 필요"
fi

echo ""
echo "6️⃣ 전략 & 리스크 체크"
echo "-------------------"

# 과매매 방지 체크
if grep -q "score > 0.8" "$BOT_FILE"; then
    check_pass "매수 점수 임계값 (0.8)"
else
    check_warn "매수 점수 임계값 낮음 (과매매 위험)"
fi

# 재진입 쿨다운 체크
if grep -q "last_trade_times" "$BOT_FILE"; then
    check_pass "코인별 재진입 쿨다운"
else
    check_warn "재진입 쿨다운 누락"
fi

# 일일 거래 제한 체크
if grep -q "daily_trade_count" "$BOT_FILE"; then
    check_pass "하루 거래 제한"
else
    check_warn "일일 거래 제한 누락"
fi

# 포지션 관리 체크
if grep -q "max_positions" "$BOT_FILE"; then
    check_pass "최대 포지션 관리"
else
    check_fail "포지션 관리 누락"
fi

echo ""
echo "7️⃣ 로깅 체크"
echo "-------------------"

# 매수 이유 로그 체크
if grep -q "매수 이유" "$BOT_FILE"; then
    check_pass "매수 이유 로깅"
else
    check_warn "매수 이유 로그 누락"
fi

# 에러 로그 체크
if grep -q "log.*ERROR" "$BOT_FILE"; then
    check_pass "에러 로깅"
else
    check_warn "에러 로그 확인 필요"
fi

echo ""
echo "=========================================="
echo "📊 최종 결과"
echo "=========================================="
echo -e "${GREEN}✅ PASS: $PASS_COUNT${NC}"
echo -e "${YELLOW}⚠️  WARN: $WARN_COUNT${NC}"
echo -e "${RED}❌ FAIL: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 필수 체크 통과!${NC}"
    echo "커밋을 진행할 수 있습니다."
    exit 0
else
    echo -e "${RED}⚠️  ${FAIL_COUNT}개의 필수 체크 실패!${NC}"
    echo "수정 후 다시 실행하세요."
    exit 1
fi
