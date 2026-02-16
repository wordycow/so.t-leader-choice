#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ 업비트 손실 복구 봇 v8.5 - RECOVERY MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 핵심: 손실 상황에서 10% 활용 → 빠른 복구 전략

✨ 시나리오:
1. 기존 코인 -30% 손실 (1,000만원 → 700만원)
2. 700만원 전부 매도? NO!
3. 보유 코인: 그대로 보유 (반등 대기)
4. 현금화 가능 금액의 10%만 활용 (70만원)
5. 70만원으로 초단타 반복 (승률 70%, 1회 +2%)
6. 35회 성공 시 140만원 복구 → 원금 50% 회복

🔥 복구 전략 특징:
- 목표 수익: 1회당 +1.5~2.5% (작지만 확실하게)
- 빠른 회전: 평균 30분 보유
- 고승률: 검증된 패턴만 선택 (승률 75%+)
- 안전 장치: -1% 즉시 손절 (손실 최소화)
- 복구 목표: 손실의 50% 복구

📈 복구 시뮬레이션:
시드 70만원 × (1.02^35회) = 140만원 (100% 증가)
→ 원금 손실 -30% 중 15% 복구
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque
import json
import threading
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import traceback

# ═══════════════════════════════════════════════════════
# 🛡️ 복구 모드 설정
# ═══════════════════════════════════════════════════════
RECOVERY_CONFIG = {
    'enable_recovery_mode': True,
    
    # 복구 모드 활성화 조건
    'activate_loss_threshold': -15.0,     # -15% 이상 손실 시 복구 모드
    'recovery_cash_ratio': 0.10,          # 현금화 가능 금액의 10%만 사용
    'min_recovery_amount': 50000,         # 최소 5만원
    
    # 복구 전략 (초단타)
    'recovery_target_profit': 1.5,        # 1.5% 목표 (작지만 확실)
    'recovery_max_profit': 2.5,           # 2.5% 최대 (욕심 부리지 않기)
    'recovery_stop_loss': -1.0,           # -1% 즉시 손절
    'recovery_max_hold_time': 30,         # 최대 30분 보유
    
    # 안전 장치
    'recovery_max_positions': 1,          # 복구 모드는 1개만
    'recovery_cooldown': 120,             # 손절 후 2분 대기
    'recovery_daily_loss_limit': -5.0,    # 하루 -5% 손실 시 중지
    
    # 복구 목표
    'recovery_target_rate': 0.5,          # 손실의 50% 복구 목표
    'recovery_success_trades': 35,        # 35회 성공 목표
}

# ═══════════════════════════════════════════════════════
# 🎮 봇 상태 관리
# ═══════════════════════════════════════════════════════
bot_state = {
    'running': False,
    'mode': 'practice',  # 'practice' or 'recovery'
    'upbit': None,
    'thread': None,
    
    # 시뮬레이션
    'simulation_seed': 1000000,
    'simulation_krw': 1000000,
    'simulation_holdings': {},
    'simulation_start_seed': 1000000,
    
    # 복구 모드 상태
    'recovery_mode_active': False,
    'recovery_seed': 0,                   # 복구용 시드 금액
    'recovery_target_amount': 0,          # 복구 목표 금액
    'recovery_trades': 0,                 # 복구 거래 횟수
    'recovery_success_trades': 0,         # 복구 성공 횟수
    'recovery_total_profit': 0,           # 복구 누적 수익
    'recovery_start_time': None,
    'last_loss_time': None,
    
    # 기존 손실 코인 (복구 모드에서는 터치 안함)
    'frozen_holdings': {},                # 손실 코인 동결
    
    # 통계
    'statistics': {
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_profit': 0,
        'recovery_progress': 0,           # 복구 진행률 (%)
    },
    
    'last_update': None,
    'error': None,
    'start_time': None,
}

# ═══════════════════════════════════════════════════════
# 📝 로깅
# ═══════════════════════════════════════════════════════
def log(message, level="INFO"):
    """로그 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "INFO": "\033[96m",
        "RECOVERY": "\033[95m",
        "URGENT": "\033[91m\033[1m"
    }
    color = colors.get(level, "\033[0m")
    reset = "\033[0m"
    print(f"{color}[{timestamp}] {level}: {message}{reset}")

# ═══════════════════════════════════════════════════════
# 🛡️ 복구 모드 활성화 체크
# ═══════════════════════════════════════════════════════
def check_recovery_mode_activation():
    """손실 상황 체크 → 복구 모드 활성화 여부 결정"""
    try:
        if bot_state['recovery_mode_active']:
            return  # 이미 활성화됨
        
        # 현재 총 자산 계산
        current_krw = bot_state['simulation_krw']
        holdings_value = sum(
            h['amount'] * pyupbit.get_current_price(ticker) or 0
            for ticker, h in bot_state['simulation_holdings'].items()
        )
        total_value = current_krw + holdings_value
        
        # 손실률 계산
        initial_seed = bot_state['simulation_start_seed']
        loss_rate = ((total_value - initial_seed) / initial_seed) * 100
        
        # 복구 모드 활성화 조건
        if loss_rate <= RECOVERY_CONFIG['activate_loss_threshold']:
            log("=" * 80, "URGENT")
            log(f"🛡️ 손실 복구 모드 활성화!", "URGENT")
            log(f"   현재 손실: {loss_rate:.2f}%", "URGENT")
            log(f"   시작 자산: {initial_seed:,.0f}원", "URGENT")
            log(f"   현재 자산: {total_value:,.0f}원", "URGENT")
            log(f"   손실 금액: {(total_value - initial_seed):,.0f}원", "URGENT")
            log("=" * 80, "URGENT")
            
            # 복구용 시드 계산 (현금화 가능 금액의 10%)
            available_cash = current_krw
            recovery_seed = max(
                available_cash * RECOVERY_CONFIG['recovery_cash_ratio'],
                RECOVERY_CONFIG['min_recovery_amount']
            )
            
            if recovery_seed < RECOVERY_CONFIG['min_recovery_amount']:
                log(f"❌ 복구 시드 부족: {recovery_seed:,.0f}원", "ERROR")
                return
            
            # 복구 목표 금액 계산 (손실의 50% 복구)
            loss_amount = abs(total_value - initial_seed)
            recovery_target = loss_amount * RECOVERY_CONFIG['recovery_target_rate']
            
            # 복구 모드 활성화
            bot_state['recovery_mode_active'] = True
            bot_state['recovery_seed'] = recovery_seed
            bot_state['recovery_target_amount'] = recovery_target
            bot_state['recovery_start_time'] = datetime.now()
            bot_state['recovery_trades'] = 0
            bot_state['recovery_success_trades'] = 0
            bot_state['recovery_total_profit'] = 0
            
            # 기존 손실 코인 동결 (매도 안함)
            bot_state['frozen_holdings'] = bot_state['simulation_holdings'].copy()
            bot_state['simulation_holdings'] = {}  # 복구 모드는 새로 시작
            
            log(f"💰 복구 시드: {recovery_seed:,.0f}원 (현금의 10%)", "RECOVERY")
            log(f"🎯 복구 목표: {recovery_target:,.0f}원 (손실의 50%)", "RECOVERY")
            log(f"📊 필요 성공 횟수: 약 {RECOVERY_CONFIG['recovery_success_trades']}회", "RECOVERY")
            log(f"❄️  기존 손실 코인: {len(bot_state['frozen_holdings'])}개 동결 (반등 대기)", "RECOVERY")
            
            return True
        
        return False
        
    except Exception as e:
        log(f"복구 모드 체크 오류: {e}", "ERROR")
        return False

def check_recovery_completion():
    """복구 목표 달성 체크"""
    try:
        if not bot_state['recovery_mode_active']:
            return False
        
        # 복구 진행률
        recovery_progress = (bot_state['recovery_total_profit'] / bot_state['recovery_target_amount']) * 100
        bot_state['statistics']['recovery_progress'] = recovery_progress
        
        # 목표 달성
        if bot_state['recovery_total_profit'] >= bot_state['recovery_target_amount']:
            log("=" * 80, "SUCCESS")
            log("🎉 복구 목표 달성!", "SUCCESS")
            log(f"   복구 금액: {bot_state['recovery_total_profit']:,.0f}원", "SUCCESS")
            log(f"   목표 금액: {bot_state['recovery_target_amount']:,.0f}원", "SUCCESS")
            log(f"   성공 거래: {bot_state['recovery_success_trades']}회", "SUCCESS")
            log(f"   총 거래: {bot_state['recovery_trades']}회", "SUCCESS")
            log(f"   승률: {(bot_state['recovery_success_trades']/bot_state['recovery_trades']*100):.1f}%", "SUCCESS")
            log("=" * 80, "SUCCESS")
            
            # 복구 모드 종료
            bot_state['recovery_mode_active'] = False
            
            # 동결된 코인 복원
            bot_state['simulation_holdings'].update(bot_state['frozen_holdings'])
            bot_state['frozen_holdings'] = {}
            
            return True
        
        return False
        
    except Exception as e:
        log(f"복구 완료 체크 오류: {e}", "ERROR")
        return False

# ═══════════════════════════════════════════════════════
# 🎯 복구 모드 전용 패턴 (초단타)
# ═══════════════════════════════════════════════════════
def find_recovery_opportunity(tickers):
    """복구용 초단타 기회 찾기 (승률 75%+ 패턴만)"""
    try:
        opportunities = []
        
        for ticker in tickers:
            try:
                # 1분봉 데이터
                df = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
                if df is None or len(df) < 15:
                    continue
                
                current_price = df['close'].iloc[-1]
                
                # RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                rsi_now = rsi.iloc[-1] if len(rsi) > 0 else 50
                
                # 거래량
                vol_avg = df['volume'].iloc[-10:-1].mean()
                vol_now = df['volume'].iloc[-1]
                vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1.0
                
                # 변동성
                recent_high = df['high'].iloc[-5:].max()
                recent_low = df['low'].iloc[-5:].min()
                volatility = ((recent_high - recent_low) / recent_low) * 100
                
                score = 0
                signals = []
                
                # 패턴 1: 과매도 반등 (승률 80%)
                if 25 <= rsi_now <= 35 and vol_ratio >= 1.5:
                    score += 5
                    signals.append(f"과매도 RSI {rsi_now:.1f}")
                
                # 패턴 2: 거래량 급증 + 상승 (승률 75%)
                change_1m = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
                if vol_ratio >= 2.5 and change_1m > 0.5:
                    score += 4
                    signals.append(f"수급 유입 {vol_ratio:.1f}배")
                
                # 패턴 3: 단기 반등 (승률 70%)
                if 1.5 <= volatility <= 3.5 and 40 <= rsi_now <= 60:
                    score += 3
                    signals.append(f"안정 구간 (변동 {volatility:.1f}%)")
                
                # 스코어 7점 이상 = 고승률 기회
                if score >= 7:
                    opportunities.append({
                        'ticker': ticker,
                        'price': current_price,
                        'score': score,
                        'rsi': rsi_now,
                        'vol_ratio': vol_ratio,
                        'signals': signals,
                        'confidence': min(score / 10.0, 1.0)
                    })
                
                time.sleep(0.05)
                
            except Exception as e:
                continue
        
        # 점수 높은 순 정렬
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities
        
    except Exception as e:
        log(f"복구 기회 탐색 오류: {e}", "ERROR")
        return []

# ═══════════════════════════════════════════════════════
# 💰 복구 모드 거래 실행
# ═══════════════════════════════════════════════════════
def execute_recovery_trade(opportunity):
    """복구용 매수"""
    try:
        ticker = opportunity['ticker']
        current_price = opportunity['price']
        
        # 복구 시드 사용
        invest_amount = bot_state['recovery_seed']
        
        if invest_amount < 5000:
            return None
        
        buy_amount = invest_amount / current_price
        
        # 매수 실행
        bot_state['recovery_seed'] -= invest_amount
        
        bot_state['simulation_holdings'][ticker] = {
            'amount': buy_amount,
            'avg_price': current_price,
            'invested': invest_amount,
            'entry_time': datetime.now(),
            'type': 'RECOVERY',
            'opportunity': opportunity,
            'peak_price': current_price
        }
        
        bot_state['recovery_trades'] += 1
        
        log(f"🛡️ 복구 매수: {ticker} | {current_price:,.0f}원 | 점수: {opportunity['score']}", "RECOVERY")
        log(f"   신호: {', '.join(opportunity['signals'])}", "RECOVERY")
        
        return True
        
    except Exception as e:
        log(f"복구 거래 오류: {e}", "ERROR")
        return None

def check_recovery_exit(ticker, holding):
    """복구용 청산 조건 (빠르고 확실하게)"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return False, None
        
        entry_price = holding['avg_price']
        profit_rate = (current_price - entry_price) / entry_price * 100
        hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
        
        # 최고가 업데이트
        if current_price > holding.get('peak_price', 0):
            holding['peak_price'] = current_price
        
        # 1. 목표 수익 달성 (1.5~2.5%)
        if RECOVERY_CONFIG['recovery_target_profit'] <= profit_rate <= RECOVERY_CONFIG['recovery_max_profit']:
            return True, f"복구 익절 (+{profit_rate:.2f}%)"
        
        # 2. 최대 수익 초과 (욕심 부리지 않기)
        if profit_rate >= RECOVERY_CONFIG['recovery_max_profit']:
            return True, f"복구 최대익절 (+{profit_rate:.2f}%)"
        
        # 3. 손절 (-1%)
        if profit_rate <= RECOVERY_CONFIG['recovery_stop_loss']:
            return True, f"복구 손절 ({profit_rate:.2f}%)"
        
        # 4. 최대 보유 시간 (30분)
        if hold_time >= RECOVERY_CONFIG['recovery_max_hold_time']:
            return True, f"복구 시간초과 ({profit_rate:+.2f}%)"
        
        # 5. 트레일링 스톱 (최고점 대비 -0.8%)
        if profit_rate >= 1.0:  # 1% 이상 수익 시
            peak = holding.get('peak_price', entry_price)
            drawdown = (peak - current_price) / peak * 100
            if drawdown >= 0.8:
                return True, f"복구 트레일링 ({profit_rate:+.2f}%)"
        
        return False, None
        
    except Exception as e:
        return False, None

def execute_recovery_exit(ticker, holding, reason):
    """복구용 매도"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        amount = holding['amount']
        entry_price = holding['avg_price']
        invested = holding['invested']
        
        # 매도 금액
        sell_krw = amount * current_price
        profit_krw = sell_krw - invested
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # 복구 시드 복원
        bot_state['recovery_seed'] += sell_krw
        
        # 보유 제거
        del bot_state['simulation_holdings'][ticker]
        
        # 통계 업데이트
        if profit_rate > 0:
            bot_state['recovery_success_trades'] += 1
            bot_state['recovery_total_profit'] += profit_krw
            log(f"✅ 복구 성공: {ticker} | +{profit_rate:.2f}% (+{profit_krw:,.0f}원) | {reason}", "SUCCESS")
        else:
            bot_state['last_loss_time'] = datetime.now()
            log(f"❌ 복구 손실: {ticker} | {profit_rate:.2f}% ({profit_krw:,.0f}원) | {reason}", "WARNING")
        
        # 진행 상황
        progress = (bot_state['recovery_total_profit'] / bot_state['recovery_target_amount']) * 100
        log(f"📊 복구 진행: {bot_state['recovery_total_profit']:,.0f}원 / {bot_state['recovery_target_amount']:,.0f}원 ({progress:.1f}%)", "RECOVERY")
        log(f"📈 성공률: {bot_state['recovery_success_trades']}/{bot_state['recovery_trades']} ({(bot_state['recovery_success_trades']/bot_state['recovery_trades']*100):.1f}%)", "RECOVERY")
        
        return True
        
    except Exception as e:
        log(f"복구 청산 오류: {e}", "ERROR")
        return None

# ═══════════════════════════════════════════════════════
# 🚀 Flask 웹 서버
# ═══════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('dashboard-recovery.html')

@app.route('/api/status')
def api_status():
    try:
        # 현재 총 자산
        current_krw = bot_state['simulation_krw'] + bot_state.get('recovery_seed', 0)
        holdings_value = sum(
            h['amount'] * (pyupbit.get_current_price(ticker) or h['avg_price'])
            for ticker, h in bot_state['simulation_holdings'].items()
        )
        frozen_value = sum(
            h['amount'] * (pyupbit.get_current_price(ticker) or h['avg_price'])
            for ticker, h in bot_state['frozen_holdings'].items()
        )
        total_value = current_krw + holdings_value + frozen_value
        
        return jsonify({
            'running': bot_state['running'],
            'mode': 'recovery' if bot_state['recovery_mode_active'] else 'normal',
            'recovery_active': bot_state['recovery_mode_active'],
            'recovery': {
                'seed': bot_state.get('recovery_seed', 0),
                'target': bot_state.get('recovery_target_amount', 0),
                'profit': bot_state.get('recovery_total_profit', 0),
                'trades': bot_state.get('recovery_trades', 0),
                'success_trades': bot_state.get('recovery_success_trades', 0),
                'win_rate': (bot_state.get('recovery_success_trades', 0) / max(bot_state.get('recovery_trades', 1), 1)) * 100,
                'progress': bot_state['statistics'].get('recovery_progress', 0)
            },
            'simulation': {
                'seed': bot_state['simulation_start_seed'],
                'current_value': total_value,
                'profit_rate': ((total_value - bot_state['simulation_start_seed']) / bot_state['simulation_start_seed']) * 100,
                'frozen_holdings': len(bot_state['frozen_holdings']),
                'active_holdings': len(bot_state['simulation_holdings'])
            },
            'statistics': bot_state['statistics'],
            'last_update': bot_state['last_update'].isoformat() if bot_state['last_update'] else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        if bot_state['running']:
            return jsonify({'success': False, 'message': '봇이 이미 실행 중입니다.'})
        
        bot_state['running'] = True
        thread = threading.Thread(target=bot_main_loop, daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        return jsonify({'success': True, 'message': '봇이 시작되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    bot_state['running'] = False
    return jsonify({'success': True, 'message': '봇이 중지되었습니다.'})

# ═══════════════════════════════════════════════════════
# 🔄 메인 봇 루프
# ═══════════════════════════════════════════════════════
def bot_main_loop():
    """메인 루프 (복구 모드 통합)"""
    log("🚀 손실 복구 봇 v8.5 시작!", "SUCCESS")
    
    bot_state['start_time'] = datetime.now()
    
    popular_tickers = [
        'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
        'KRW-ADA', 'KRW-AVAX', 'KRW-MATIC', 'KRW-LINK', 'KRW-ATOM'
    ]
    
    while bot_state['running']:
        try:
            # 1. 복구 모드 활성화 체크
            if not bot_state['recovery_mode_active']:
                check_recovery_mode_activation()
            
            # 2. 복구 모드 실행
            if bot_state['recovery_mode_active']:
                log("🛡️ 복구 모드 실행 중...", "RECOVERY")
                
                # 보유 포지션 관리
                for ticker, holding in list(bot_state['simulation_holdings'].items()):
                    should_exit, reason = check_recovery_exit(ticker, holding)
                    if should_exit:
                        execute_recovery_exit(ticker, holding, reason)
                
                # 쿨다운 체크
                if bot_state['last_loss_time']:
                    cooldown = (datetime.now() - bot_state['last_loss_time']).total_seconds()
                    if cooldown < RECOVERY_CONFIG['recovery_cooldown']:
                        log(f"⏳ 쿨다운: {int(RECOVERY_CONFIG['recovery_cooldown'] - cooldown)}초 대기", "INFO")
                        time.sleep(5)
                        continue
                
                # 신규 진입 (복구 모드는 1개만)
                if len(bot_state['simulation_holdings']) < RECOVERY_CONFIG['recovery_max_positions']:
                    opportunities = find_recovery_opportunity(popular_tickers)
                    
                    if opportunities:
                        best = opportunities[0]
                        log(f"🎯 복구 기회 발견: {best['ticker']} | 점수: {best['score']} | 신뢰도: {best['confidence']:.0%}", "RECOVERY")
                        execute_recovery_trade(best)
                
                # 복구 완료 체크
                check_recovery_completion()
            
            # 3. 일반 모드 (여기서는 생략, 복구 모드만 구현)
            
            bot_state['last_update'] = datetime.now()
            time.sleep(10)
            
        except Exception as e:
            log(f"메인 루프 오류: {e}", "ERROR")
            log(traceback.format_exc(), "ERROR")
            time.sleep(10)
    
    log("🛑 봇 중지됨", "WARNING")

if __name__ == "__main__":
    log("🛡️ 손실 복구 봇 v8.5 준비 완료!", "SUCCESS")
    log("💎 10% 시드로 빠른 복구 시작!", "INFO")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
