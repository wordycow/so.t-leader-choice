#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Engine Main Loop
Top20 실데이터 → 전략 조건 검사 → WebSocket 신호 발생
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.upbit_market_data import UpbitMarketData
from shared.runtime_state import write_state, now_iso
from signal_engine.top20_strategy_engine import Top20StrategyEngine
from signal_engine.websocket_emitter import WebSocketEmitter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("SignalEngineMain")


class SignalEngineMain:
    """메인 루프: Top20 갱신 → 전략 검사 → 신호 발송"""
    
    def __init__(self):
        self.strategy_engine = Top20StrategyEngine()
        self.ws_emitter = WebSocketEmitter()
        self.scan_interval = 60  # 60초마다 Top20 갱신
        self.signal_count = 0
        self.last_top20_scan_at = None
        self.last_signal_at = None
        
    async def run(self):
        """메인 루프 실행"""
        logger.info("🚀 Signal Engine v9 Starting...")
        logger.info(f"📊 Top20 scan interval: {self.scan_interval}s")
        
        # WebSocket 연결
        await self.ws_emitter.connect()
        
        # 메인 루프
        while True:
            try:
                await self._scan_and_signal()
                await asyncio.sleep(self.scan_interval)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _scan_and_signal(self):
        """Top20 스캔 → 신호 생성 → 발송"""
        try:
            # 1. Top20 실데이터 가져오기
            logger.info("📊 Fetching Top20 data...")
            top20_data = UpbitMarketData.get_top20_by_volume()
            self.last_top20_scan_at = now_iso()
            
            if not top20_data:
                logger.warning("⚠️ No Top20 data received")
                self._update_health()
                return
            
            logger.info(f"✅ Top20 fetched: {len(top20_data)} items")
            
            # 2. 전략 조건 검사 → 신호 생성
            signals = self.strategy_engine.update_top20(top20_data)
            
            if signals:
                logger.info(f"🎯 {len(signals)} signals generated")
                
                # 3. WebSocket으로 신호 발송
                for signal in signals:
                    await self._send_signal(signal)
            else:
                logger.info("⏳ No signals (conditions not met)")
            
            # 4. 상태 업데이트
            self._update_health()
            
        except Exception as e:
            logger.error(f"Scan error: {e}", exc_info=True)
    
    async def _send_signal(self, signal: dict):
        """신호 WebSocket 발송"""
        try:
            await self.ws_emitter.send_signal(signal)
            self.signal_count += 1
            self.last_signal_at = now_iso()
            logger.info(f"📤 Signal sent: {signal['ticker']} {signal['side']} ({signal['strategy_name']})")
        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
    
    def _update_health(self):
        """Health 상태 업데이트"""
        watch_state = self.strategy_engine.get_watch_state()
        
        # signal_engine_state.json에 저장 (websocket_emitter와 충돌 방지)
        write_state("signal_engine_state.json", {
            "service": "signal_engine",
            "status": "running",
            "last_top20_scan_at": self.last_top20_scan_at,
            "top20_count": 20,
            "last_signal_at": self.last_signal_at,
            "signal_sent_count": self.signal_count,
            "tracked_tickers": watch_state.get("tracked_tickers", 0),
            "watch_states": watch_state.get("watch_states", {}),
            "condition_checklists": watch_state.get("condition_checklists", {}),
            "_updated_at": now_iso(),
        })


if __name__ == "__main__":
    engine = SignalEngineMain()
    asyncio.run(engine.run())
