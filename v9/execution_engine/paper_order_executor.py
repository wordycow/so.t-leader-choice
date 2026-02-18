#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 PAPER Order Executor
PRACTICE 모드: 실제 주문 없이 PAPER fill 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List
from datetime import datetime
import uuid
import json
import logging

from shared.runtime_state import write_state, read_state, now_iso

logger = logging.getLogger("PaperOrderExecutor")


class PaperOrderExecutor:
    """PRACTICE 모드 PAPER 체결 생성기"""
    
    def __init__(self):
        self.paper_fills: List[Dict] = []
        self.last_execution_at = None
        self.execution_count = 0
        
        # trades.json 초기화 (비어있으면)
        existing_trades = read_state("trades.json", None)
        if existing_trades is None:
            write_state("trades.json", [])
    
    async def execute_signal(self, signal: Dict) -> Dict:
        """
        신호 수신 → PAPER fill 생성
        
        Args:
            signal: Top20StrategyEngine에서 생성한 신호
        
        Returns:
            Trade event dict
        """
        try:
            # PAPER fill 생성
            trade = self._create_paper_fill(signal)
            
            # trades.json에 저장
            self._save_trade(trade)
            
            # 통계 업데이트
            self.paper_fills.append(trade)
            self.execution_count += 1
            self.last_execution_at = now_iso()
            
            # 상태 갱신
            self._update_execution_state(trade)
            
            logger.info(f"✅ PAPER fill created: {trade['ticker']} {trade['side']} @ {trade['price']}")
            
            return trade
            
        except Exception as e:
            logger.error(f"Failed to create PAPER fill: {e}", exc_info=True)
            return None
    
    def _create_paper_fill(self, signal: Dict) -> Dict:
        """
        PAPER 체결 생성 (Trade JSON 스키마 준수)
        """
        # 가격/수량 계산
        price = signal["ref"]["price"]
        # PRACTICE: 기본 10만원어치
        default_krw = 100_000
        qty = default_krw / price if price > 0 else 0
        
        return {
            "ts": now_iso(),
            "mode": signal.get("mode", "PRACTICE"),
            "ticker": signal["ticker"],
            "side": signal["side"],
            "qty": round(qty, 8),
            "price": price,
            "strategy_name": signal["strategy_name"],
            "why": signal["why"],
            "trigger_conditions": signal["trigger_conditions"],
            "pnl": None,  # 매수 시점에는 PnL 없음
            "order_id": f"paper-{uuid.uuid4().hex[:12]}",
            "status": "FILLED",
            "confidence": signal.get("confidence", 0.0),
            "risk_reason": signal.get("risk_reason", ""),
        }
    
    def _save_trade(self, trade: Dict):
        """trades.json에 추가"""
        try:
            trades = read_state("trades.json", [])
            if not isinstance(trades, list):
                trades = []
            
            trades.append(trade)
            
            # 최근 100개만 유지
            if len(trades) > 100:
                trades = trades[-100:]
            
            write_state("trades.json", trades)
            
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
    
    def _update_execution_state(self, trade: Dict):
        """execution_engine.json 상태 업데이트"""
        write_state("execution_engine.json", {
            "service": "execution_engine",
            "status": "running",
            "last_execution_received_at": self.last_execution_at,
            "execution_received_count": self.execution_count,
            "last_paper_fill_at": self.last_execution_at,
            "paper_fill_count": len(self.paper_fills),
            "last_trade_at": self.last_execution_at,
            "last_trade": {
                "ticker": trade["ticker"],
                "side": trade["side"],
                "strategy_name": trade["strategy_name"],
                "why": trade["why"],
            },
            "_updated_at": now_iso(),
        })
    
    def get_stats(self) -> Dict:
        """통계 조회"""
        return {
            "paper_fill_count": len(self.paper_fills),
            "last_execution_at": self.last_execution_at,
            "execution_count": self.execution_count,
        }
