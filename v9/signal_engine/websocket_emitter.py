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
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import WEBSOCKET
from shared.signal_schema import SignalPayload

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/signal_engine/websocket_emitter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WebSocketEmitter')


class WebSocketEmitter:
    """
    Maintains persistent WebSocket connection to Execution Engine
    Sends signals as JSON payloads
    Handles reconnection on failure
    """
    
    def __init__(self, server_url: str = WEBSOCKET['signal_to_execution_url']):
        self.server_url = server_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = WEBSOCKET['max_reconnect_attempts']
        self.reconnect_delay = WEBSOCKET['reconnect_delay']
        
        logger.info(f"WebSocketEmitter initialized (server: {server_url})")
    
    async def connect(self):
        """
        Establish WebSocket connection
        """
        try:
            logger.info(f"Connecting to {self.server_url}...")
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            self.reconnect_attempts = 0
            logger.info("✅ WebSocket connected successfully")
            
            # Start heartbeat
            asyncio.create_task(self.heartbeat())
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            await self.reconnect()
    
    async def reconnect(self):
        """
        Attempt to reconnect with exponential backoff
        """
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts > self.max_reconnect_attempts:
            logger.error("Max reconnect attempts reached - giving up")
            return
        
        delay = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
        logger.warning(f"Reconnecting in {delay}s (attempt {self.reconnect_attempts})...")
        
        await asyncio.sleep(delay)
        await self.connect()
    
    async def heartbeat(self):
        """
        Send periodic heartbeat to keep connection alive
        """
        while self.connected:
            try:
                if self.websocket:
                    await self.websocket.ping()
                    logger.debug("Heartbeat sent")
                
                await asyncio.sleep(WEBSOCKET['heartbeat_interval'])
                
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                self.connected = False
                await self.reconnect()
                break
    
    async def send_signal(self, signal: SignalPayload) -> bool:
        """
        Send signal to Execution Engine
        Returns True if successful, False otherwise
        """
        if not self.connected or not self.websocket:
            logger.error("Cannot send signal - not connected")
            return False
        
        try:
            # Convert signal to JSON
            payload = json.dumps(signal.to_dict())
            
            # Send via WebSocket
            await self.websocket.send(payload)
            
            logger.info(
                f"📤 Signal sent: {signal.signal_type} | {signal.strategy_id} | "
                f"{signal.ticker} | confidence={signal.confidence:.2f}"
            )
            
            # Optionally wait for acknowledgment
            # ack = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            # logger.debug(f"Received ack: {ack}")
            
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logger.error("Connection closed during send")
            self.connected = False
            await self.reconnect()
            return False
            
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            return False
    
    async def close(self):
        """
        Close WebSocket connection gracefully
        """
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("WebSocket connection closed")
    
    # === Synchronous wrapper for easier integration ===
    def send_signal_sync(self, signal: SignalPayload) -> bool:
        """
        Synchronous wrapper for send_signal
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.send_signal(signal))


# === Global emitter instance ===
_emitter_instance: Optional[WebSocketEmitter] = None

def get_emitter() -> WebSocketEmitter:
    """
    Get global emitter instance (singleton)
    """
    global _emitter_instance
    if _emitter_instance is None:
        _emitter_instance = WebSocketEmitter()
    return _emitter_instance


async def main():
    """
    Test/demo mode
    """
    emitter = WebSocketEmitter()
    await emitter.connect()
    
    # Keep alive
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await emitter.close()


if __name__ == '__main__':
    asyncio.run(main())
