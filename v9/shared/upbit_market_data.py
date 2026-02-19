"""
Upbit Market Data Fetcher (No API Key Required)

Fetches real-time market data from Upbit public API.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class UpbitMarketData:
    """
    Upbit 공개 API를 사용하여 실시간 시장 데이터 수집
    (API 키 불필요)
    """
    
    BASE_URL = "https://api.upbit.com/v1"
    
    @classmethod
    def get_krw_markets(cls) -> List[str]:
        """
        KRW 마켓 목록 조회
        
        Returns:
            List of KRW market tickers (e.g., ["KRW-BTC", "KRW-ETH", ...])
        """
        try:
            response = requests.get(
                f"{cls.BASE_URL}/market/all",
                params={"isDetails": "false"},
                timeout=5
            )
            response.raise_for_status()
            
            markets = response.json()
            krw_markets = [m["market"] for m in markets if m["market"].startswith("KRW-")]
            
            return krw_markets
            
        except Exception as e:
            print(f"❌ Failed to fetch KRW markets: {e}")
            return []
    
    @classmethod
    def get_ticker_data(cls, markets: List[str]) -> List[Dict]:
        """
        현재 시세 정보 조회
        
        Args:
            markets: Market ticker list (e.g., ["KRW-BTC", "KRW-ETH"])
            
        Returns:
            List of ticker data with current price, volume, change rate, etc.
        """
        if not markets:
            return []
        
        try:
            # Upbit API는 최대 100개까지 한 번에 조회 가능
            markets_param = ",".join(markets[:100])
            
            response = requests.get(
                f"{cls.BASE_URL}/ticker",
                params={"markets": markets_param},
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Failed to fetch ticker data: {e}")
            return []
    
    @classmethod
    def get_top20_by_volume(cls) -> List[Dict]:
        """
        24시간 거래대금 기준 상위 21개 코인 조회
        
        Returns:
            Top 21 coins sorted by 24h trading volume
            
        Example:
            [
                {
                    "rank": 1,
                    "ticker": "KRW-BTC",
                    "trade_price": 50000000,
                    "acc_trade_price_24h": 500000000000,
                    "signed_change_rate": 0.05,
                    "timestamp": "2026-02-18T12:00:00",
                    "source": "upbit"
                },
                ...
            ]
        """
        # 1. Get all KRW markets
        krw_markets = cls.get_krw_markets()
        
        if not krw_markets:
            print("⚠️  No KRW markets found")
            return []
        
        # 2. Get ticker data
        tickers = cls.get_ticker_data(krw_markets)
        
        if not tickers:
            print("⚠️  No ticker data found")
            return []
        
        # 3. Sort by 24h trading volume (acc_trade_price_24h)
        sorted_tickers = sorted(
            tickers,
            key=lambda x: x.get("acc_trade_price_24h", 0),
            reverse=True
        )
        
        # 4. Get top 21
        top20 = sorted_tickers[:21]
        
        # 5. Format output
        result = []
        for rank, ticker in enumerate(top20, start=1):
            result.append({
                "rank": rank,
                "ticker": ticker.get("market"),
                "trade_price": ticker.get("trade_price"),
                "acc_trade_price_24h": ticker.get("acc_trade_price_24h"),
                "signed_change_rate": ticker.get("signed_change_rate"),
                "change_rate": ticker.get("change_rate"),
                "acc_trade_volume_24h": ticker.get("acc_trade_volume_24h"),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "upbit",
                # Watchlist reason
                "reason": f"거래대금 상위 {rank}위",
                "status": "watching",  # 추적중
            })
        
        return result
    
    @classmethod
    def get_candles(cls, market: str, interval: str = "minutes", count: int = 200) -> List[Dict]:
        """
        캔들 데이터 조회
        
        Args:
            market: Market ticker (e.g., "KRW-BTC")
            interval: Candle interval ("minutes", "days", "weeks", "months")
            count: Number of candles (max 200)
            
        Returns:
            List of candle data
        """
        try:
            if interval == "minutes":
                unit = 1  # 1분봉
                endpoint = f"{cls.BASE_URL}/candles/minutes/{unit}"
            elif interval == "days":
                endpoint = f"{cls.BASE_URL}/candles/days"
            elif interval == "weeks":
                endpoint = f"{cls.BASE_URL}/candles/weeks"
            elif interval == "months":
                endpoint = f"{cls.BASE_URL}/candles/months"
            else:
                raise ValueError(f"Invalid interval: {interval}")
            
            response = requests.get(
                endpoint,
                params={"market": market, "count": count},
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Failed to fetch candles for {market}: {e}")
            return []


# Quick test
if __name__ == "__main__":
    print("🔍 Testing Upbit Market Data...")
    
    # Test 1: Get KRW markets
    markets = UpbitMarketData.get_krw_markets()
    print(f"✅ Found {len(markets)} KRW markets")
    print(f"   First 5: {markets[:5]}")
    
    # Test 2: Get top 20
    top20 = UpbitMarketData.get_top20_by_volume()
    print(f"\n✅ Top 20 by volume:")
    for item in top20[:5]:
        print(f"   {item['rank']}. {item['ticker']}: {item['acc_trade_price_24h']:,.0f} KRW")
    
    print(f"\n🎯 Total top20 items: {len(top20)}")
    print(f"   Source: {top20[0]['source'] if top20 else 'N/A'}")
