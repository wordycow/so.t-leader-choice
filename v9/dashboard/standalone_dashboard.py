#!/usr/bin/env python3
"""
Standalone Dashboard for Upbit Bot v9
단독 실행 가능한 대시보드
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Mock data for testing
def get_mock_data():
    """Return mock data for dashboard"""
    return {
        'mode': 'PRACTICE',
        'equity': 1000000,
        'realized_pnl': 0,
        'unrealized_pnl': 0,
        'position_count': 0,
        'candidates': [
            {'rank': i+1, 'symbol': f'KRW-COIN{i+1}', 'score': 0.9-i*0.05, 'change_pct': 5.0-i*0.5}
            for i in range(20)
        ],
        'holdings': [],
        'trades': [],
        'btc_regime': {
            'regime': 'normal',
            'block_new_entries': False,
            'explanation': '정상 레짐'
        }
    }


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/imei_dashboard.html')
def imei_dashboard():
    """IMEI dashboard page"""
    try:
        return render_template('imei_dashboard.html')
    except Exception as e:
        return f"IMEI Dashboard not found: {str(e)}", 404


@app.route('/api/kpis')
def get_kpis():
    """Get system KPIs"""
    data = get_mock_data()
    return jsonify({
        'mode': data['mode'],
        'equity': data['equity'],
        'realized_pnl': data['realized_pnl'],
        'unrealized_pnl': data['unrealized_pnl'],
        'position_count': data['position_count'],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/top20')
def get_top20():
    """Get TOP 20 candidates"""
    data = get_mock_data()
    return jsonify({
        'candidates': data['candidates'],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/holdings')
def get_holdings():
    """Get current holdings"""
    data = get_mock_data()
    return jsonify({
        'holdings': data['holdings'],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    data = get_mock_data()
    return jsonify({
        'trades': data['trades'],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/safety')
def get_safety():
    """Get safety gate status"""
    return jsonify({
        'real_trading_enabled': False,
        'flag_file_exists': False,
        'exposure_limit': 100000,
        'current_exposure': 0,
        'daily_drawdown_limit': 2.0,
        'current_drawdown': 0.0,
        'blocked': False,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/recovery')
def get_recovery():
    """Get recovery engine status"""
    return jsonify({
        'positions_in_recovery': [],
        'total_recovery_positions': 0,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/btc_stacking')
def get_btc_stacking():
    """Get BTC stacking status"""
    return jsonify({
        'total_stacked': 0,
        'stacking_events': [],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Standalone Dashboard',
        'version': 'v9',
        'timestamp': datetime.utcnow().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Upbit Bot v9 - Standalone Dashboard")
    print("=" * 60)
    print(f"Starting Flask server...")
    print(f"Access dashboard at: http://localhost:5000")
    print(f"IMEI dashboard at: http://localhost:5000/imei_dashboard.html")
    print(f"Health check: http://localhost:5000/health")
    print("=" * 60)
    print("")
    print("⚠️  NOTE: This is a standalone dashboard with mock data.")
    print("   For real trading data, run the full system with:")
    print("   - Signal Engine (websocket_emitter.py)")
    print("   - Execution Engine (websocket_receiver.py)")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
