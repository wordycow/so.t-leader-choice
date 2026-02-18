#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template
from datetime import datetime
import random
import os

from shared.runtime_state import read_state, now_iso

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)

def ts():
    return now_iso()

# --- Mock (fallback) ---
def mock_kpis():
    return {
        "mode": "PRACTICE",
        "equity": 1_000_000,
        "realized_pnl": 0,
        "unrealized_pnl": 0,
        "position_count": 0,
        "timestamp": ts(),
    }

def mock_top20():
    return [{"rank": i+1, "ticker": f"KRW-MOCK{i+1:02d}", "score": round(random.random(), 4)} for i in range(20)]

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
    se = read_state("signal_engine.json", {})
    ex = read_state("execution_engine.json", {})
    return jsonify({
        "status": "healthy",
        "service": "Standalone Dashboard",
        "version": "v9",
        "timestamp": ts(),
        "signal_engine": se,
        "execution_engine": ex,
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
    # 나중에 signal engine이 top20.json 써주면 여기서 바로 실데이터로 바뀜
    top20 = read_state("top20.json", None)
    if top20 is None:
        return jsonify({"items": mock_top20(), "source": "mock", "timestamp": ts()})
    return jsonify({"items": top20, "source": "runtime", "timestamp": ts()})

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
