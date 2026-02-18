#!/bin/bash
# Hourly snapshot for 24h practice run

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOGFILE="imei_os/practice_logs/hourly_snapshots.log"

# Create log directory if needed
mkdir -p imei_os/practice_logs

echo "=== $TIMESTAMP ===" | tee -a $LOGFILE

# KPIs
echo "📊 KPIs:" | tee -a $LOGFILE
curl -s http://localhost:5000/api/kpis 2>/dev/null | jq '{equity, daily_pnl, position_count, trades_today}' 2>/dev/null | tee -a $LOGFILE || echo "⚠️ Dashboard not accessible" | tee -a $LOGFILE

# Holdings
echo "" | tee -a $LOGFILE
echo "💼 Holdings:" | tee -a $LOGFILE
HOLDINGS_COUNT=$(curl -s http://localhost:5000/api/holdings 2>/dev/null | jq 'length' 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "Position count: $HOLDINGS_COUNT" | tee -a $LOGFILE
else
    echo "⚠️ Holdings not accessible" | tee -a $LOGFILE
fi

# Safety
echo "" | tee -a $LOGFILE
echo "🔒 Safety:" | tee -a $LOGFILE
curl -s http://localhost:5000/api/safety 2>/dev/null | jq '{real_trading_enabled, circuit_breaker_active}' 2>/dev/null | tee -a $LOGFILE || echo "⚠️ Safety status not accessible" | tee -a $LOGFILE

# Trade count
echo "" | tee -a $LOGFILE
echo "📈 Trades:" | tee -a $LOGFILE
if [ -f "imei_os/TRADING_LOG.csv" ]; then
    TRADE_COUNT=$(($(wc -l < imei_os/TRADING_LOG.csv) - 1))
    echo "Total trades: $TRADE_COUNT" | tee -a $LOGFILE
else
    echo "⚠️ No trading log found" | tee -a $LOGFILE
fi

echo "" | tee -a $LOGFILE
echo "---" | tee -a $LOGFILE
