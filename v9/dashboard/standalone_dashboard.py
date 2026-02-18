#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template
from datetime import datetime
import random
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.runtime_state import read_state, now_iso
from shared.upbit_market_data import UpbitMarketData

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)

def ts():
    return now_iso()

# --- Mock (fallback) - KPI only ---
def mock_kpis():
    return {
        "mode": "PRACTICE",
        "equity": 1_000_000,
        "realized_pnl": 0,
        "unrealized_pnl": 0,
        "position_count": 0,
        "timestamp": ts(),
    }

# --- UI ---
@app.route("/")
def index():
    # 템플릿 없으면 기본 텍스트라도 반환
    try:
        return render_template("index.html")
    except Exception:
        return "<h1>Standalone Dashboard</h1><p>/api/kpis /health 확인</p>"

@app.route("/imei_dashboard.html")
def imei_dashboard():
    try:
        return render_template("imei_dashboard.html")
    except Exception:
        return "<h1>IMEI Dashboard</h1>"

# --- Health ---
@app.route("/health")
def health():
    """
    ✅ 확장된 Health 체크 (유송 운영 편의)
    - 각 엔진 상태 + 실제 동작 지표 (시각/카운트)
    """
    se = read_state("signal_engine.json", {})
    ex = read_state("execution_engine.json", {})
    
    return jsonify({
        "status": "healthy",
        "service": "Standalone Dashboard",
        "version": "v9",
        "timestamp": ts(),
        
        # Signal Engine
        "signal_engine": {
            "status": se.get("status", "unknown"),
            "last_top20_scan_at": se.get("last_top20_scan_at"),
            "top20_count": se.get("top20_count", 0),
            "last_signal_at": se.get("last_signal_at"),
            "signal_sent_count": se.get("signal_sent_count", 0),
            "tracked_tickers": se.get("tracked_tickers", 0),
        },
        
        # Execution Engine
        "execution_engine": {
            "status": ex.get("status", "unknown"),
            "last_execution_received_at": ex.get("last_execution_received_at"),
            "execution_received_count": ex.get("execution_received_count", 0),
            "last_paper_fill_at": ex.get("last_paper_fill_at"),
            "paper_fill_count": ex.get("paper_fill_count", 0),
            "last_trade_at": ex.get("last_trade_at"),
        },
    })

# --- APIs ---
@app.route("/api/kpis")
def api_kpis():
    se = read_state("signal_engine.json", {})
    ex = read_state("execution_engine.json", {})

    data = mock_kpis()
    # ✅ “실제 상태”를 여기서 같이 보여줌
    data["signal_engine"] = {
        "connected": se.get("connected"),
        "reconnect_attempts": se.get("reconnect_attempts"),
        "last_ping_at": se.get("last_ping_at"),
        "last_sent_at": se.get("last_sent_at"),
        "status": se.get("status"),
        "_updated_at": se.get("_updated_at"),
    }
    data["execution_engine"] = {
        "client_count": ex.get("client_count"),
        "received_count": ex.get("received_count"),
        "last_signal": ex.get("last_signal"),
        "status": ex.get("status"),
        "_updated_at": ex.get("_updated_at"),
    }
    data["timestamp"] = ts()
    return jsonify(data)

@app.route("/api/top20")
def api_top20():
    """
    ✅ 실제 Upbit 시장 데이터를 가져옴 (거래량 Top20)
    - ticker, rank, trade_price, acc_trade_price_24h, signed_change_rate
    - source: "upbit" (실데이터), timestamp
    """
    try:
        top20_data = UpbitMarketData.get_top20_by_volume()
        return jsonify({
            "items": top20_data,
            "source": "upbit",
            "timestamp": ts()
        })
    except Exception as e:
        # 에러시 빈 리스트 (mock 없이)
        return jsonify({
            "items": [],
            "source": "error",
            "error": str(e),
            "timestamp": ts()
        }), 500

@app.route("/api/holdings")
def api_holdings():
    holdings = read_state("holdings.json", None)
    if holdings is None:
        return jsonify({"items": [], "source": "empty", "timestamp": ts()})
    return jsonify({"items": holdings, "source": "runtime", "timestamp": ts()})

@app.route("/api/trades")
def api_trades():
    trades = read_state("trades.json", None)
    if trades is None:
        return jsonify({"items": [], "source": "empty", "timestamp": ts()})
    return jsonify({"items": trades, "source": "runtime", "timestamp": ts()})

@app.route("/api/safety")
def api_safety():
    return jsonify({"gate": "LOCKED", "reason": "ENABLE_REAL_TRADING not set", "timestamp": ts()})

@app.route("/api/recovery")
def api_recovery():
    return jsonify({"status": "idle", "timestamp": ts()})

@app.route("/api/btc_stacking")
def api_btc_stacking():
    return jsonify({"btc_stack": 0.0, "timestamp": ts()})

@app.route("/api/watch_state")
def api_watch_state():
    """
    ✅ Signal Engine의 watch_state 조회
    - 각 티커/전략별 추적 상태 (WATCHING/ARMED/TRIGGERED/COOLDOWN)
    """
    se = read_state("signal_engine.json", {})
    return jsonify({
        "watch_states": se.get("watch_states", {}),
        "tracked_tickers": se.get("tracked_tickers", 0),
        "last_top20_scan_at": se.get("last_top20_scan_at"),
        "signal_sent_count": se.get("signal_sent_count", 0),
        "timestamp": ts()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
