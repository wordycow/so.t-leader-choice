#!/usr/bin/env python3
"""
v9 Execution Engine - WebSocket Receiver
Receives signals from Signal Engine and routes to handler
"""

import asyncio
import websockets
import json
import logging
from typing import Optional, Callable
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.constants import LOG_FORMAT, LOG_DATE_FORMAT
from shared.signal_schema import validate_signal_payload
from shared.runtime_state import write_state, now_iso

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("WebSocketReceiver")

class WebSocketReceiver:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.signal_handler: Optional[Callable] = None
        self.clients = set()

        self.received_count = 0
        self.last_signal = None

        self._flush_state("starting")
        logger.info(f"WebSocketReceiver initialized ({host}:{port})")

    def _flush_state(self, status: str = "running"):
        write_state("execution_engine.json", {
            "service": "execution_engine",
            "role": "websocket_receiver",
            "host": self.host,
            "port": self.port,
            "client_count": len(self.clients),
            "received_count": self.received_count,
            "last_signal": self.last_signal,
            "status": status,
            "last_update_at": now_iso(),
        })

    def set_signal_handler(self, handler: Callable):
        self.signal_handler = handler

    async def handle_client(self, websocket):
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        self._flush_state("client_connected")

        try:
            async for message in websocket:
                await self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            if websocket in self.clients:
                self.clients.remove(websocket)
            self._flush_state("client_disconnected")

    async def process_message(self, message: str):
        try:
            data = json.loads(message)

            if not validate_signal_payload(data):
                logger.error("Invalid signal payload")
                return

            self.received_count += 1
            self.last_signal = {
                "signal_type": data.get("signal_type"),
                "ticker": data.get("ticker"),
                "strategy_id": data.get("strategy_id"),
                "confidence": data.get("confidence"),
                "btc_regime": data.get("btc_regime"),
                "signal_id": data.get("signal_id"),
                "timestamp": data.get("timestamp"),
            }
            self._flush_state("signal_received")

            logger.info(f"Signal received: {data['signal_type']} | {data['ticker']}")

            if self.signal_handler:
                await self.signal_handler(data)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._flush_state("error")

    async def start(self):
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        self._flush_state("listening")

        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # run forever

async def main():
    receiver = WebSocketReceiver()

    async def dummy_handler(signal_data):
        # 여기에 나중에 TradeExecutor 연결하면 됨
        logger.info(f"Handler got: {signal_data['ticker']}")

    receiver.set_signal_handler(dummy_handler)
    await receiver.start()

if __name__ == "__main__":
    asyncio.run(main())
