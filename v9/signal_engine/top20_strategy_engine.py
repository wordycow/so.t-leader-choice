#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Top20 Strategy Engine
실데이터 기반 4대 전략 조건 검사 + 신호 발생
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from shared.upbit_market_data import UpbitMarketData

logger = logging.getLogger("Top20StrategyEngine")


class WatchState:
    """각 티커의 전략별 추적 상태"""
    WATCHING = "WATCHING"      # 기본 추적
    ARMED = "ARMED"            # 조건 거의 충족
    TRIGGERED = "TRIGGERED"    # 신호 발생
    COOLDOWN = "COOLDOWN"      # 쿨다운 (재신호 방지)


class StrategyCondition:
    """전략 조건 체크 결과"""
    def __init__(self, name: str, met: bool, reason: str):
        self.name = name
        self.met = met
        self.reason = reason


class Top20StrategyEngine:
    """
    4대 전략:
    1. SurgeHunter: 급등 캐치
    2. DipHunter: 급락 후 반등
    3. BoxTrader: 박스권 돌파
    4. TrendFollower: 추세 추종
    """
    
    def __init__(self):
        self.watch_states: Dict[str, Dict[str, str]] = {}  # {ticker: {strategy: state}}
        self.last_signals: Dict[str, datetime] = {}  # {ticker: last_signal_time}
        self.cooldown_minutes = 10  # 같은 코인 재신호 최소 간격 (완화: 30분 → 10분)
        
        # 히스토리 (간단한 가격 추적)
        self.price_history: Dict[str, List[Dict]] = {}  # {ticker: [{price, ts, change_rate}]}
        self.max_history = 20  # 최근 20개 데이터포인트
        
        # 조건 체크리스트 (운영 가시성)
        self.condition_checklists: Dict[str, Dict[str, Dict]] = {}  # {ticker: {strategy: {condition: met}}}
        
    def update_top20(self, top20_data: List[Dict]) -> List[Dict]:
        """
        Top20 실데이터를 받아서 조건 검사 → 신호 생성
        
        Returns:
            List of signal dicts (발생한 신호들)
        """
        signals = []
        
        for item in top20_data:
            ticker = item["ticker"]
            
            # 히스토리 업데이트
            self._update_history(ticker, item)
            
            # 쿨다운 체크
            if self._is_cooldown(ticker):
                continue
            
            # 각 전략별로 조건 검사
            for strategy_name in ["SurgeHunter", "DipHunter", "BoxTrader", "TrendFollower"]:
                signal = self._check_strategy(ticker, item, strategy_name)
                if signal:
                    signals.append(signal)
                    self.last_signals[ticker] = datetime.utcnow()
                    # 신호 발생 후 상태 업데이트
                    self._set_state(ticker, strategy_name, WatchState.TRIGGERED)
        
        return signals
    
    def _update_history(self, ticker: str, item: Dict):
        """가격 히스토리 업데이트"""
        if ticker not in self.price_history:
            self.price_history[ticker] = []
        
        self.price_history[ticker].append({
            "price": item.get("trade_price", 0),
            "ts": datetime.utcnow(),
            "change_rate": item.get("signed_change_rate", 0),
            "volume": item.get("acc_trade_price_24h", 0),
        })
        
        # 오래된 데이터 제거
        if len(self.price_history[ticker]) > self.max_history:
            self.price_history[ticker] = self.price_history[ticker][-self.max_history:]
    
    def _is_cooldown(self, ticker: str) -> bool:
        """쿨다운 체크 (같은 코인 재신호 방지)"""
        if ticker not in self.last_signals:
            return False
        
        elapsed = datetime.utcnow() - self.last_signals[ticker]
        return elapsed < timedelta(minutes=self.cooldown_minutes)
    
    def _get_state(self, ticker: str, strategy: str) -> str:
        """현재 상태 조회"""
        if ticker not in self.watch_states:
            self.watch_states[ticker] = {}
        return self.watch_states[ticker].get(strategy, WatchState.WATCHING)
    
    def _set_state(self, ticker: str, strategy: str, state: str):
        """상태 업데이트"""
        if ticker not in self.watch_states:
            self.watch_states[ticker] = {}
        self.watch_states[ticker][strategy] = state
    
    def _save_condition_checklist(self, ticker: str, strategy: str, conditions: List[StrategyCondition], all_met: bool):
        """조건 체크리스트 저장 (운영 판단용)"""
        if ticker not in self.condition_checklists:
            self.condition_checklists[ticker] = {}
        
        self.condition_checklists[ticker][strategy] = {
            "conditions": [{"name": c.name, "met": c.met, "reason": c.reason} for c in conditions],
            "all_met": all_met,
            "state": self._get_state(ticker, strategy),
            "checked_at": datetime.utcnow().isoformat(),
        }
    
    def _check_strategy(self, ticker: str, item: Dict, strategy_name: str) -> Optional[Dict]:
        """전략별 조건 검사 → 신호 생성"""
        
        if strategy_name == "SurgeHunter":
            return self._check_surge_hunter(ticker, item)
        elif strategy_name == "DipHunter":
            return self._check_dip_hunter(ticker, item)
        elif strategy_name == "BoxTrader":
            return self._check_box_trader(ticker, item)
        elif strategy_name == "TrendFollower":
            return self._check_trend_follower(ticker, item)
        
        return None
    
    def _check_surge_hunter(self, ticker: str, item: Dict) -> Optional[Dict]:
        """
        SurgeHunter: 급등 캐치
        조건 (완화됨):
        1. 변동률 +5% 이상 (기존 +10%)
        2. 거래대금 50억 이상 (기존 100억)
        3. 상승 추세 (2회 이상)
        """
        change_rate = item.get("signed_change_rate", 0)
        volume = item.get("acc_trade_price_24h", 0)
        
        conditions = [
            StrategyCondition("변동률 +5% 이상", change_rate >= 0.05, f"현재: {change_rate*100:.1f}%"),
            StrategyCondition("거래대금 50억 이상", volume >= 5_000_000_000, f"현재: {volume/1e9:.1f}억"),
        ]
        
        # 히스토리 체크 (상승 추세 - 2회만 체크)
        history = self.price_history.get(ticker, [])
        if len(history) >= 2:
            recent_changes = [h["change_rate"] for h in history[-2:]]
            trending_up = recent_changes[-1] > recent_changes[0]  # 마지막이 첫번째보다 높으면 OK
            conditions.append(StrategyCondition("상승 추세", trending_up, f"최근 변화: {recent_changes}"))
        else:
            # 데이터 부족 시에도 통과 (초기 스캔에서도 거래 가능)
            conditions.append(StrategyCondition("상승 추세", True, "초기 스캔 - 통과"))
        
        # 모든 조건 충족?
        all_met = all(c.met for c in conditions)
        
        # 상태 업데이트
        current_state = self._get_state(ticker, "SurgeHunter")
        if all_met:
            self._set_state(ticker, "SurgeHunter", WatchState.ARMED)
        
        # 조건 체크리스트 저장 (운영 가시성)
        self._save_condition_checklist(ticker, "SurgeHunter", conditions, all_met)
        
        # 신호 발생 (ARMED 상태에서 조건 충족 시)
        if current_state == WatchState.ARMED and all_met:
            return self._create_signal(
                ticker=ticker,
                side="BUY",
                strategy_name="SurgeHunter",
                why=f"급등 포착: {change_rate*100:.1f}% 상승, 거래대금 {volume/1e9:.1f}억",
                trigger_conditions=[c.reason for c in conditions if c.met],
                confidence=0.85,
                item=item
            )
        
        return None
    
    def _check_dip_hunter(self, ticker: str, item: Dict) -> Optional[Dict]:
        """
        DipHunter: 급락 후 반등
        조건 (완화됨):
        1. 변동률 -5% 이하 (기존 -8%)
        2. 거래대금 30억 이상 (기존 50억)
        3. 반등 시작 (최근 상승 전환)
        """
        change_rate = item.get("signed_change_rate", 0)
        volume = item.get("acc_trade_price_24h", 0)
        
        conditions = [
            StrategyCondition("변동률 -5% 이하", change_rate <= -0.05, f"현재: {change_rate*100:.1f}%"),
            StrategyCondition("거래대금 30억 이상", volume >= 3_000_000_000, f"현재: {volume/1e9:.1f}억"),
        ]
        
        # 히스토리 체크 (반등 시작) - 조건 완화
        history = self.price_history.get(ticker, [])
        if len(history) >= 2:
            last_change = history[-1]["change_rate"]
            prev_change = history[-2]["change_rate"]
            bouncing = last_change > prev_change and last_change > -0.08  # -5% → -8%로 완화
            conditions.append(StrategyCondition("반등 시작", bouncing, f"이전: {prev_change*100:.1f}% → 현재: {last_change*100:.1f}%"))
        else:
            # 데이터 부족 시에도 통과
            conditions.append(StrategyCondition("반등 시작", True, "초기 스캔 - 통과"))
        
        all_met = all(c.met for c in conditions)
        current_state = self._get_state(ticker, "DipHunter")
        
        if all_met:
            self._set_state(ticker, "DipHunter", WatchState.ARMED)
        
        # 조건 체크리스트 저장
        self._save_condition_checklist(ticker, "DipHunter", conditions, all_met)
        
        if current_state == WatchState.ARMED and all_met:
            return self._create_signal(
                ticker=ticker,
                side="BUY",
                strategy_name="DipHunter",
                why=f"급락 후 반등: {change_rate*100:.1f}% 하락 후 상승 전환",
                trigger_conditions=[c.reason for c in conditions if c.met],
                confidence=0.75,
                item=item
            )
        
        return None
    
    def _check_box_trader(self, ticker: str, item: Dict) -> Optional[Dict]:
        """
        BoxTrader: 박스권 돌파
        조건 (완화됨):
        1. 변동률 +3% ~ +15% (기존 +5%)
        2. 거래량 증가 (이전 대비 1.5배 이상) - 기존 2배
        3. 지지/저항 돌파
        """
        change_rate = item.get("signed_change_rate", 0)
        volume = item.get("acc_trade_price_24h", 0)
        
        conditions = [
            StrategyCondition("변동률 적정 범위", 0.03 <= change_rate <= 0.15, f"현재: {change_rate*100:.1f}%"),
        ]
        
        # 히스토리 체크 (거래량 증가) - 1.5배로 완화
        history = self.price_history.get(ticker, [])
        if len(history) >= 2:
            current_vol = history[-1]["volume"]
            prev_vol = history[-2]["volume"]
            volume_surge = current_vol > prev_vol * 1.5
            conditions.append(StrategyCondition("거래량 증가", volume_surge, f"이전: {prev_vol/1e9:.1f}억 → 현재: {current_vol/1e9:.1f}억"))
        else:
            # 데이터 부족 시에도 통과
            conditions.append(StrategyCondition("거래량 증가", True, "초기 스캔 - 통과"))
        
        all_met = all(c.met for c in conditions)
        current_state = self._get_state(ticker, "BoxTrader")
        
        if all_met:
            self._set_state(ticker, "BoxTrader", WatchState.ARMED)
        
        # 조건 체크리스트 저장
        self._save_condition_checklist(ticker, "BoxTrader", conditions, all_met)
        
        if current_state == WatchState.ARMED and all_met:
            return self._create_signal(
                ticker=ticker,
                side="BUY",
                strategy_name="BoxTrader",
                why=f"박스권 돌파: {change_rate*100:.1f}% 상승 + 거래량 증가",
                trigger_conditions=[c.reason for c in conditions if c.met],
                confidence=0.80,
                item=item
            )
        
        return None
    
    def _check_trend_follower(self, ticker: str, item: Dict) -> Optional[Dict]:
        """
        TrendFollower: 추세 추종
        조건 (완화됨):
        1. 변동률 +2% 이상 (기존 +3%)
        2. 지속적 상승 (최근 2개만 양수) - 기존 5개
        3. 거래대금 20억 이상 (기존 30억)
        """
        change_rate = item.get("signed_change_rate", 0)
        volume = item.get("acc_trade_price_24h", 0)
        
        conditions = [
            StrategyCondition("변동률 +2% 이상", change_rate >= 0.02, f"현재: {change_rate*100:.1f}%"),
            StrategyCondition("거래대금 20억 이상", volume >= 2_000_000_000, f"현재: {volume/1e9:.1f}억"),
        ]
        
        # 히스토리 체크 (지속 상승) - 2개만 체크
        history = self.price_history.get(ticker, [])
        if len(history) >= 2:
            recent_changes = [h["change_rate"] for h in history[-2:]]
            sustained = all(c > 0 for c in recent_changes)
            conditions.append(StrategyCondition("지속적 상승", sustained, f"최근 2개: {[f'{c*100:.1f}%' for c in recent_changes]}"))
        else:
            # 데이터 부족 시에도 통과
            conditions.append(StrategyCondition("지속적 상승", True, "초기 스캔 - 통과"))
        
        all_met = all(c.met for c in conditions)
        current_state = self._get_state(ticker, "TrendFollower")
        
        if all_met:
            self._set_state(ticker, "TrendFollower", WatchState.ARMED)
        
        # 조건 체크리스트 저장
        self._save_condition_checklist(ticker, "TrendFollower", conditions, all_met)
        
        if current_state == WatchState.ARMED and all_met:
            return self._create_signal(
                ticker=ticker,
                side="BUY",
                strategy_name="TrendFollower",
                why=f"추세 추종: {change_rate*100:.1f}% 지속 상승",
                trigger_conditions=[c.reason for c in conditions if c.met],
                confidence=0.70,
                item=item
            )
        
        return None
    
    def _create_signal(
        self,
        ticker: str,
        side: str,
        strategy_name: str,
        why: str,
        trigger_conditions: List[str],
        confidence: float,
        item: Dict
    ) -> Dict:
        """신호 JSON 생성 (스키마 준수)"""
        return {
            "ts": datetime.utcnow().isoformat(),
            "mode": "PRACTICE",  # 기본값 (나중에 .env에서 읽기)
            "ticker": ticker,
            "side": side,
            "strategy_name": strategy_name,
            "why": why,
            "trigger_conditions": trigger_conditions,
            "confidence": confidence,
            "risk_reason": self._assess_risk(item),
            "ref": {
                "rank": item.get("rank", 0),
                "acc_trade_price_24h": item.get("acc_trade_price_24h", 0),
                "signed_change_rate": item.get("signed_change_rate", 0),
                "price": item.get("trade_price", 0),
            }
        }
    
    def _assess_risk(self, item: Dict) -> str:
        """리스크 평가"""
        change_rate = abs(item.get("signed_change_rate", 0))
        
        if change_rate > 0.20:
            return "극단적 변동성 - 고위험"
        elif change_rate > 0.15:
            return "높은 변동성 - 중간 위험"
        elif change_rate < 0.03:
            return "낮은 변동성 - 저위험"
        else:
            return "적정 변동성"
    
    def get_watch_state(self) -> Dict:
        """현재 추적 상태 전체 반환 (API용 + 조건 체크리스트 포함)"""
        return {
            "watch_states": self.watch_states,
            "condition_checklists": self.condition_checklists,
            "last_signals": {k: v.isoformat() for k, v in self.last_signals.items()},
            "tracked_tickers": len(self.watch_states),
            "timestamp": datetime.utcnow().isoformat(),
        }
