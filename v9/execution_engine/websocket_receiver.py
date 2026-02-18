#!/usr/bin/env python3
"""
v9 Execution Engine - WebSocket Receiver
Receives signals from Signal Engine and routes to validator
"""

import asyncio
import websockets
import json
import logging
from typing import Optional, Callable
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import WEBSOCKET
from shared.signal_schema import SignalPayload, validate_signal_payload

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/execution_engine/websocket_receiver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WebSocketReceiver')


class WebSocketReceiver:
    """WebSocket server to receive signals"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8765):
        self.host = host
        self.port = port
        self.signal_handler: Optional[Callable] = None
        self.clients = set()
        
        logger.info(f"WebSocketReceiver initialized ({host}:{port})")
    
    def set_signal_handler(self, handler: Callable):
        """Set callback for incoming signals"""
        self.signal_handler = handler
    
    async def handle_client(self, websocket, path):
        """Handle incoming WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.process_message(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.clients.remove(websocket)
    
    async def process_message(self, message: str, websocket):
        """Process incoming signal"""
        try:
            data = json.loads(message)
            
            # Validate
            if not validate_signal_payload(data):
                logger.error("Invalid signal payload")
                return
            
            logger.info(f"📥 Signal received: {data['signal_type']} | {data['ticker']}")
            
            # Route to handler
            if self.signal_handler:
                await self.signal_handler(data)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def start(self):
        """Start WebSocket server"""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


async def main():
    receiver = WebSocketReceiver()
    
    # Set dummy handler
    async def dummy_handler(signal_data):
        logger.info(f"Dummy handler received: {signal_data['ticker']}")
    
    receiver.set_signal_handler(dummy_handler)
    await receiver.start()


if __name__ == '__main__':
    asyncio.run(main())
