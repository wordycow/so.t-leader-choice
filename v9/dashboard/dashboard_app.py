#!/usr/bin/env python3
"""
Compact Dashboard Flask App for Execution Engine
Serves single-page dashboard with real-time data
"""

import logging
from flask import Flask, render_template, jsonify
from datetime import datetime
import os

logger = logging.getLogger(__name__)

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)


class DashboardServer:
    """Dashboard server for Execution Engine"""
    
    def __init__(self, executor, validator, recovery, btc_stacker, safety_gates):
        self.executor = executor
        self.validator = validator
        self.recovery = recovery
        self.btc_stacker = btc_stacker
        self.safety_gates = safety_gates
        
        # Store reference for routes
        app.config['DASHBOARD'] = self
    
    def get_kpi_data(self):
        """Get KPI metrics for dashboard"""
        portfolio = self.executor.get_portfolio_status()
        
        total_invested = portfolio['total_invested_krw']
        position_count = portfolio['position_count']
        
        # Calculate total equity (simplified - would need actual cash balance)
        cash_balance = 1000000 - total_invested  # Mock
        total_equity = cash_balance + total_invested
        
        # Daily P&L (mock - would need start-of-day tracking)
        daily_pnl = 15000
        daily_pnl_pct = (daily_pnl / total_equity) * 100
        
        # Trade count today
        trade_count_today = len([
            t for t in self.executor.trade_log 
            if t['timestamp'].date() == datetime.now().date()
        ])
        
        return {
            "total_equity": total_equity,
            "daily_pnl": daily_pnl,
            "daily_pnl_pct": daily_pnl_pct,
            "cash": cash_balance,
            "invested": total_invested,
            "invested_pct": (total_invested / total_equity) * 100,
            "position_count": position_count,
            "max_positions": 2,
            "trades_today": trade_count_today
        }
    
    def get_top20_candidates(self):
        """Get TOP 20 candidates (would come from Signal Engine via WebSocket)"""
        # Mock data - in production, this comes from Signal Engine
        return [
            {"ticker": "KRW-DOGE", "score": 0.92, "price_change_pct": 5.2, "volume_surge": 350},
            {"ticker": "KRW-XRP", "score": 0.88, "price_change_pct": 3.1, "volume_surge": 280},
            {"ticker": "KRW-ADA", "score": 0.85, "price_change_pct": 2.8, "volume_surge": 220},
        ]
    
    def get_holdings(self):
        """Get current holdings"""
        portfolio = self.executor.get_portfolio_status()
        return portfolio['positions']
    
    def get_recent_trades(self, limit=10):
        """Get recent trades"""
        trades = self.executor.trade_log[-limit:]
        return [
            {
                "timestamp": t['timestamp'].strftime("%H:%M"),
                "type": t['type'],
                "ticker": t['ticker'],
                "reason": t.get('reason', '-'),
                "profit_pct": t.get('profit_pct', 0)
            }
            for t in reversed(trades)
        ]
    
    def run(self, host='0.0.0.0', port=5000):
        """Start dashboard server"""
        logger.info(f"🌐 Starting dashboard server on {host}:{port}")
        app.run(host=host, port=port, debug=False)


# Flask routes
@app.route('/')
def index():
    """Serve dashboard HTML"""
    return render_template('index.html')


@app.route('/api/kpis')
def api_kpis():
    """Get KPI data"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    return jsonify(dashboard.get_kpi_data())


@app.route('/api/top20')
def api_top20():
    """Get TOP 20 candidates"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    return jsonify(dashboard.get_top20_candidates())


@app.route('/api/holdings')
def api_holdings():
    """Get current holdings"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    return jsonify(dashboard.get_holdings())


@app.route('/api/trades')
def api_trades():
    """Get recent trades"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    return jsonify(dashboard.get_recent_trades())


@app.route('/api/safety')
def api_safety():
    """Get safety gates status"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    status = dashboard.safety_gates.is_real_trading_allowed(
        current_equity=1000000,  # Mock
        current_invested=150000   # Mock
    )
    
    return jsonify({
        "real_trading_enabled": status.real_trading_enabled,
        "reason": status.reason,
        "exposure_limit_krw": status.exposure_limit_krw,
        "circuit_breaker_active": status.circuit_breaker_active
    })


@app.route('/api/recovery')
def api_recovery():
    """Get recovery engine status"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    return jsonify(dashboard.recovery.get_recovery_status())


@app.route('/api/btc_stacking')
def api_btc_stacking():
    """Get BTC stacking status"""
    dashboard = app.config.get('DASHBOARD')
    if not dashboard:
        return jsonify({"error": "Dashboard not initialized"}), 500
    
    return jsonify(dashboard.btc_stacker.get_stacking_status())


if __name__ == "__main__":
    # Test server
    logging.basicConfig(level=logging.INFO)
    
    # Mock dependencies
    class MockExecutor:
        def get_portfolio_status(self):
            return {
                "position_count": 2,
                "total_invested_krw": 150000,
                "positions": []
            }
        trade_log = []
    
    class MockValidator:
        pass
    
    class MockRecovery:
        def get_recovery_status(self):
            return {"recovery_active": False, "recovery_log": []}
    
    class MockBTCStacker:
        def get_stacking_status(self):
            return {"total_btc_accumulated": 0.0}
    
    class MockSafetyGates:
        def is_real_trading_allowed(self, current_equity, current_invested):
            from v9.execution_engine.safety_gates import SafetyStatus
            return SafetyStatus(
                real_trading_enabled=False,
                reason="Test mode",
                exposure_limit_krw=100000,
                daily_drawdown_limit_pct=2.0,
                circuit_breaker_active=False
            )
    
    dashboard = DashboardServer(
        MockExecutor(),
        MockValidator(),
        MockRecovery(),
        MockBTCStacker(),
        MockSafetyGates()
    )
    
    dashboard.run(port=5001)
