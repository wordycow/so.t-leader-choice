#!/usr/bin/env python3
"""
BTC Stacker for Execution Engine
Auto-converts realized profits ≥10,000 KRW into BTC spot
Maintains separate BTC accumulation log
"""

import logging
import pyupbit
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class BTCPurchase:
    """Represents a BTC purchase"""
    timestamp: datetime
    profit_source: str  # e.g., "KRW-DOGE_PARTIAL_5"
    profit_krw: float
    btc_amount: float
    btc_price: float
    fee_krw: float
    net_btc: float


class BTCStacker:
    """Handles automatic BTC accumulation from profits"""
    
    def __init__(self, upbit_access: str, upbit_secret: str, practice_mode: bool = True):
        self.practice_mode = practice_mode
        
        if not practice_mode:
            self.upbit = pyupbit.Upbit(upbit_access, upbit_secret)
            logger.info("🔴 LIVE BTC STACKING - Real BTC purchases")
        else:
            self.upbit = None
            logger.info("📝 PRACTICE BTC STACKING - Simulated purchases")
        
        self.MIN_PROFIT_THRESHOLD = 10000  # KRW
        self.purchases: List[BTCPurchase] = []
        self.total_btc_accumulated = 0.0
        self.total_profit_invested = 0.0
        
        # Load existing log if available
        self.log_file = "imei_os/BTC_STACKING_LOG.json"
        self._load_log()
    
    def _load_log(self):
        """Load existing BTC stacking log"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.total_btc_accumulated = data.get('total_btc', 0.0)
                    self.total_profit_invested = data.get('total_profit_krw', 0.0)
                    
                    # Load purchases
                    for p in data.get('purchases', []):
                        self.purchases.append(BTCPurchase(
                            timestamp=datetime.fromisoformat(p['timestamp']),
                            profit_source=p['profit_source'],
                            profit_krw=p['profit_krw'],
                            btc_amount=p['btc_amount'],
                            btc_price=p['btc_price'],
                            fee_krw=p['fee_krw'],
                            net_btc=p['net_btc']
                        ))
                    
                    logger.info(f"📊 BTC Stacking log loaded: {self.total_btc_accumulated:.8f} BTC "
                              f"from {self.total_profit_invested:,.0f} KRW profit")
            except Exception as e:
                logger.error(f"❌ Failed to load BTC stacking log: {e}")
    
    def _save_log(self):
        """Save BTC stacking log to JSON"""
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            data = {
                "total_btc": self.total_btc_accumulated,
                "total_profit_krw": self.total_profit_invested,
                "purchase_count": len(self.purchases),
                "last_update": datetime.now().isoformat(),
                "purchases": [
                    {
                        "timestamp": p.timestamp.isoformat(),
                        "profit_source": p.profit_source,
                        "profit_krw": p.profit_krw,
                        "btc_amount": p.btc_amount,
                        "btc_price": p.btc_price,
                        "fee_krw": p.fee_krw,
                        "net_btc": p.net_btc
                    }
                    for p in self.purchases
                ]
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 BTC stacking log saved: {len(self.purchases)} purchases")
        except Exception as e:
            logger.error(f"❌ Failed to save BTC stacking log: {e}")
    
    def process_profit(self, profit_krw: float, source: str) -> bool:
        """
        Process realized profit and convert to BTC if threshold met
        
        Args:
            profit_krw: Profit amount in KRW
            source: Source of profit (e.g., "KRW-DOGE_PARTIAL_3")
        
        Returns:
            True if BTC purchase was executed
        """
        if profit_krw < self.MIN_PROFIT_THRESHOLD:
            logger.info(f"💰 Profit {profit_krw:,.0f} KRW below threshold {self.MIN_PROFIT_THRESHOLD:,.0f} - no BTC purchase")
            return False
        
        try:
            # Get current BTC price
            btc_price = pyupbit.get_current_price("KRW-BTC")
            if btc_price is None:
                logger.error(f"❌ Failed to get BTC price")
                return False
            
            # Calculate BTC amount (after 0.05% fee)
            fee_rate = 0.0005
            fee_krw = profit_krw * fee_rate
            net_profit = profit_krw - fee_krw
            btc_amount = net_profit / btc_price
            
            if self.practice_mode:
                logger.info(f"📝 [PRACTICE] BTC STACK: {profit_krw:,.0f} KRW → {btc_amount:.8f} BTC "
                          f"@ {btc_price:,.0f} (fee: {fee_krw:,.0f}) from {source}")
            else:
                # Real BTC purchase
                order = self.upbit.buy_market_order("KRW-BTC", profit_krw)
                if order is None or 'error' in order:
                    logger.error(f"❌ BTC purchase failed: {order}")
                    return False
                
                logger.info(f"🟠 [LIVE] BTC STACK: {profit_krw:,.0f} KRW → {btc_amount:.8f} BTC "
                          f"@ {btc_price:,.0f} (fee: {fee_krw:,.0f}) from {source}")
            
            # Record purchase
            purchase = BTCPurchase(
                timestamp=datetime.now(),
                profit_source=source,
                profit_krw=profit_krw,
                btc_amount=btc_amount,
                btc_price=btc_price,
                fee_krw=fee_krw,
                net_btc=btc_amount
            )
            
            self.purchases.append(purchase)
            self.total_btc_accumulated += btc_amount
            self.total_profit_invested += profit_krw
            
            # Save log
            self._save_log()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ BTC stacking failed: {e}")
            return False
    
    def get_stacking_status(self) -> Dict:
        """Get current BTC stacking status"""
        current_btc_price = pyupbit.get_current_price("KRW-BTC")
        current_value = 0
        if current_btc_price:
            current_value = self.total_btc_accumulated * current_btc_price
        
        return {
            "total_btc_accumulated": self.total_btc_accumulated,
            "total_profit_invested_krw": self.total_profit_invested,
            "current_btc_price": current_btc_price,
            "current_value_krw": current_value,
            "purchase_count": len(self.purchases),
            "avg_btc_price": self.total_profit_invested / self.total_btc_accumulated if self.total_btc_accumulated > 0 else 0,
            "recent_purchases": [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "source": p.profit_source,
                    "profit_krw": p.profit_krw,
                    "btc_amount": p.btc_amount,
                    "btc_price": p.btc_price
                }
                for p in self.purchases[-5:]  # Last 5 purchases
            ]
        }
    
    def get_roi(self) -> float:
        """Calculate ROI of BTC accumulation"""
        if self.total_profit_invested == 0:
            return 0.0
        
        current_btc_price = pyupbit.get_current_price("KRW-BTC")
        if current_btc_price is None:
            return 0.0
        
        current_value = self.total_btc_accumulated * current_btc_price
        roi = ((current_value - self.total_profit_invested) / self.total_profit_invested) * 100
        
        return roi


if __name__ == "__main__":
    # Test BTC stacker
    logging.basicConfig(level=logging.INFO)
    
    stacker = BTCStacker("", "", practice_mode=True)
    
    print("\n=== Test 1: Below threshold ===")
    result = stacker.process_profit(5000, "KRW-DOGE_PARTIAL_3")
    print(f"Purchase executed: {result}")
    
    print("\n=== Test 2: Above threshold ===")
    result = stacker.process_profit(15000, "KRW-XRP_PARTIAL_5")
    print(f"Purchase executed: {result}")
    
    print("\n=== Test 3: Multiple purchases ===")
    stacker.process_profit(12000, "KRW-ADA_TRAIL_7")
    stacker.process_profit(20000, "KRW-SOL_PARTIAL_3")
    
    print("\n=== BTC Stacking Status ===")
    status = stacker.get_stacking_status()
    print(f"Total BTC: {status['total_btc_accumulated']:.8f}")
    print(f"Total Invested: {status['total_profit_invested_krw']:,.0f} KRW")
    print(f"Current Value: {status['current_value_krw']:,.0f} KRW")
    print(f"ROI: {stacker.get_roi():.2f}%")
    print(f"Purchases: {status['purchase_count']}")
