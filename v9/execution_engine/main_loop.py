#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Execution Engine Main
WebSocket 신호 수신 → PAPER 체결 생성
"""

import asyncio
import sys
import os
import logging
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution_engine.websocket_receiver import WebSocketReceiver
from execution_engine.paper_order_executor import PaperOrderExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ExecutionEngineMain")


class ExecutionEngineMain:
    """메인: WebSocket 수신 → PAPER 체결"""
    
    def __init__(self):
        self.ws_receiver = WebSocketReceiver(host="0.0.0.0", port=8765)
        self.paper_executor = PaperOrderExecutor()
        
        # 신호 핸들러 등록
        self.ws_receiver.set_signal_handler(self.handle_signal)
    
    async def handle_signal(self, signal: Dict):
        """신호 수신 → PAPER 체결 생성"""
        try:
            logger.info(f"📥 Signal received: {signal['ticker']} {signal['side']} ({signal['strategy_name']})")
            
            # PAPER fill 생성
            trade = await self.paper_executor.execute_signal(signal)
            
            if trade:
                logger.info(f"✅ Trade created: {trade['order_id']}")
            else:
                logger.error("❌ Failed to create trade")
                
        except Exception as e:
            logger.error(f"Handle signal error: {e}", exc_info=True)
    
    async def run(self):
        """메인 실행"""
        logger.info("🚀 Execution Engine v9 Starting...")
        logger.info(f"📡 WebSocket server: {self.ws_receiver.host}:{self.ws_receiver.port}")
        
        # WebSocket 서버 시작
        async with websockets.serve(
            self.ws_receiver.handle_client,
            self.ws_receiver.host,
            self.ws_receiver.port
        ):
            logger.info("✅ WebSocket server started")
            await asyncio.Future()  # Run forever


if __name__ == "__main__":
    import websockets
    engine = ExecutionEngineMain()
    asyncio.run(engine.run())
