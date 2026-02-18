#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Engine - WebSocket Emitter
Sends signals from Signal Engine to Execution Engine via WebSocket
"""

import asyncio
import websockets
import json
import logging
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.constants import WEBSOCKET, LOG_FORMAT, LOG_DATE_FORMAT
from shared.signal_schema import SignalPayload
from shared.runtime_state import write_state, now_iso

# ✅ Windows-safe logging: console only (START_ALL_BOTS에서 stdout을 logs/*.log로 리다이렉트함)
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("WebSocketEmitter")

class WebSocketEmitter:
    def __init__(self, server_url: str = WEBSOCKET["signal_to_execution_url"]):
        self.server_url = server_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = WEBSOCKET["max_reconnect_attempts"]
        self.reconnect_delay = WEBSOCKET["reconnect_delay"]
        self.last_ping_at = None
        self.last_sent_at = None

        write_state("signal_engine.json", {
            "service": "signal_engine",
            "role": "websocket_emitter",
            "server_url": self.server_url,
            "connected": self.connected,
            "reconnect_attempts": self.reconnect_attempts,
            "last_ping_at": self.last_ping_at,
            "last_sent_at": self.last_sent_at,
            "status": "starting",
        })

        logger.info(f"WebSocketEmitter initialized (server: {server_url})")

    def _flush_state(self, status: str = "running"):
        write_state("signal_engine.json", {
            "service": "signal_engine",
            "role": "websocket_emitter",
            "server_url": self.server_url,
            "connected": self.connected,
            "reconnect_attempts": self.reconnect_attempts,
            "last_ping_at": self.last_ping_at,
            "last_sent_at": self.last_sent_at,
            "status": status,
        })

    async def connect(self):
        try:
            logger.info(f"Connecting to {self.server_url}...")
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            self.reconnect_attempts = 0
            logger.info("✅ WebSocket connected successfully")
            self._flush_state("connected")
            asyncio.create_task(self.heartbeat())
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            self._flush_state("connect_failed")
            await self.reconnect()

    async def reconnect(self):
        self.reconnect_attempts += 1
        self._flush_state("reconnecting")

        if self.reconnect_attempts > self.max_reconnect_attempts:
            logger.error("Max reconnect attempts reached - giving up")
            self._flush_state("dead")
            return

        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
        logger.warning(f"Reconnecting in {delay}s (attempt {self.reconnect_attempts})...")
        await asyncio.sleep(delay)
        await self.connect()

    async def heartbeat(self):
        while self.connected:
            try:
                if self.websocket:
                    await self.websocket.ping()
                    self.last_ping_at = now_iso()
                    self._flush_state("connected")
                await asyncio.sleep(WEBSOCKET["heartbeat_interval"])
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                self.connected = False
                self._flush_state("heartbeat_failed")
                await self.reconnect()
                break

    async def send_signal(self, signal: SignalPayload) -> bool:
        if not self.connected or not self.websocket:
            logger.error("Cannot send signal - not connected")
            self._flush_state("not_connected")
            return False

        try:
            payload = json.dumps(signal.to_dict())
            await self.websocket.send(payload)
            self.last_sent_at = now_iso()
            self._flush_state("connected")

            logger.info(
                f"Signal sent: {signal.signal_type} | {signal.strategy_id} | "
                f"{signal.ticker} | confidence={signal.confidence:.2f}"
            )
            return True
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection closed during send")
            self.connected = False
            self._flush_state("conn_closed")
            await self.reconnect()
            return False
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            self._flush_state("send_error")
            return False

    async def close(self):
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        self._flush_state("closed")
        logger.info("WebSocket connection closed")

async def main():
    emitter = WebSocketEmitter()
    await emitter.connect()

    # ✅ 필요하면 데모 신호를 흘려서 파이프라인 확인 (기본 OFF)
    # Windows: set EMIT_DEMO_SIGNAL=1
    # Linux/Mac: EMIT_DEMO_SIGNAL=1 ./start_all_bots.sh
    demo = os.getenv("EMIT_DEMO_SIGNAL", "0") == "1"
    try:
        while True:
            if demo and emitter.connected:
                sig = SignalPayload.create_entry_signal(
                    strategy_id="ULTRA_SCALP_V2_1",
                    ticker="KRW-BTC",
                    confidence=0.77,
                    snapshot_score=0.55,
                    btc_regime="NORMAL",
                    indicators={"demo": 1.0}
                )
                await emitter.send_signal(sig)
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await emitter.close()

if __name__ == "__main__":
    asyncio.run(main())
