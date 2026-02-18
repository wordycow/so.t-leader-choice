# 🚀 Go Live - Enable Real Trading

## ⚠️ CRITICAL WARNINGS

**READ THIS ENTIRE DOCUMENT BEFORE PROCEEDING**

Enabling real trading will:
- Execute **REAL** buy/sell orders on Upbit
- Use **REAL** money from your Upbit account
- Incur **REAL** trading fees (0.05% per trade)
- Risk **REAL** capital loss

**ONLY proceed if**:
- ✅ 24-hour practice run **PASSED** all criteria
- ✅ You understand the system completely
- ✅ You accept the risk of capital loss
- ✅ You are ready to monitor actively

---

## 📋 Pre-Live Checklist

Complete **ALL** items before enabling real trading:

### 1. Practice Run Validation

- [ ] 24-hour practice run completed
- [ ] Win rate ≥ 55%
- [ ] Average R:R ≥ 1.5:1
- [ ] Expected value > 0
- [ ] Max drawdown ≤ 5%
- [ ] No system crashes during 24h
- [ ] WebSocket stability >99.5%
- [ ] All exit reasons logged correctly
- [ ] Sample size ≥ 10 trades

### 2. System Understanding

- [ ] Read and understood README.md
- [ ] Read and understood ARCHITECTURE_V9.md
- [ ] Read and understood ONBOARDING.md
- [ ] Studied strategies.json
- [ ] Understand partial exit logic (3%, 5%, 7%)
- [ ] Understand time-stop logic (6 min)
- [ ] Understand safety gates (double-lock)
- [ ] Know emergency stop procedures

### 3. Safety Gates

- [ ] Understand double-lock requirement (ENV + FLAG)
- [ ] Know exposure limit (100,000 KRW first phase)
- [ ] Know circuit breaker trigger (-2% daily drawdown)
- [ ] Know how to disable real trading
- [ ] Know how to force exit all positions
- [ ] Have emergency contact ready

### 4. Upbit Account

- [ ] Upbit API keys generated
- [ ] API keys have trading permissions
- [ ] API keys added to `.env` file
- [ ] Sufficient balance (≥200,000 KRW recommended)
- [ ] Withdrawal address whitelisted (for BTC stacking)
- [ ] 2FA enabled on Upbit account

### 5. Monitoring Setup

- [ ] Dashboard accessible (http://localhost:5000)
- [ ] Phone/computer with alerts configured
- [ ] Telegram/Discord/Email alerts set up (optional)
- [ ] Calendar blocked for first 2 hours of live trading
- [ ] Ready to monitor every trade closely

---

## 🔐 Enable Real Trading (Step-by-Step)

**FOLLOW THESE STEPS EXACTLY**

### Step 1: Stop All Processes

```bash
# Stop all running bot processes
pkill -f "websocket_emitter"
pkill -f "websocket_receiver"
pkill -f "dashboard_app"

# Verify all stopped
ps aux | grep -E "websocket|dashboard" | grep -v grep
# Should show nothing
```

### Step 2: Backup Current State

```bash
# Create backup directory
mkdir -p imei_os/backups/$(date +%Y%m%d_%H%M%S)

# Backup trading log
cp imei_os/TRADING_LOG.csv imei_os/backups/$(date +%Y%m%d_%H%M%S)/

# Backup BTC stacking log
cp imei_os/BTC_STACKING_LOG.json imei_os/backups/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# Backup database
cp upbit_bot.db imei_os/backups/$(date +%Y%m%d_%H%M%S)/

echo "✅ Backup complete"
```

### Step 3: Verify API Keys

```bash
# Test Upbit API connection
python3 -c "
import pyupbit
import os
from dotenv import load_dotenv

load_dotenv('v9/.env')

access = os.getenv('UPBIT_ACCESS_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')

if not access or not secret:
    print('❌ API keys not found in .env')
    exit(1)

upbit = pyupbit.Upbit(access, secret)
balance = upbit.get_balances()

if balance:
    print('✅ API keys valid')
    krw = [b for b in balance if b['currency'] == 'KRW']
    if krw:
        print(f'KRW Balance: {float(krw[0][\"balance\"]):,.0f} KRW')
else:
    print('❌ API keys invalid or no permissions')
    exit(1)
"
```

**Expected output**: `✅ API keys valid` + your KRW balance

### Step 4: Edit Environment Variable

```bash
cd v9/

# Edit .env file
nano .env
```

**Change this line**:
```
ENABLE_REAL_TRADING=false
```

**To**:
```
ENABLE_REAL_TRADING=true
```

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

**Verify change**:
```bash
grep ENABLE_REAL_TRADING .env
```

**Expected output**: `ENABLE_REAL_TRADING=true`

### Step 5: Create Flag File

```bash
# Create the live trading flag file
sudo touch /enable_live.flag

# Verify it exists
ls -l /enable_live.flag
```

**Expected output**: `-rw-r--r-- 1 root root 0 ... /enable_live.flag`

### Step 6: Verify Exposure Limit

```bash
# Check exposure limit
grep FIRST_PHASE_EXPOSURE_LIMIT v9/.env
```

**Expected output**: `FIRST_PHASE_EXPOSURE_LIMIT=100000`

**If different**, edit:
```bash
nano v9/.env
# Set: FIRST_PHASE_EXPOSURE_LIMIT=100000
```

### Step 7: Verify Daily Drawdown Limit

```bash
# Check drawdown limit
grep DAILY_DRAWDOWN_LIMIT_PCT v9/.env
```

**Expected output**: `DAILY_DRAWDOWN_LIMIT_PCT=2.0`

**If different**, edit:
```bash
nano v9/.env
# Set: DAILY_DRAWDOWN_LIMIT_PCT=2.0
```

### Step 8: Start Execution Engine FIRST

**⚠️ IMPORTANT**: Start Execution Engine **BEFORE** Signal Engine

```bash
cd v9/

# Terminal 1: Execution Engine
python3 execution_engine/websocket_receiver.py 2>&1 | tee imei_os/live_logs/execution_engine.log
```

**Watch for**:
```
🔴 LIVE TRADING MODE - Real orders will be executed
```

### Step 9: Verify Safety Gates

In a **new terminal**:

```bash
# Check safety gates status
curl http://localhost:5000/api/safety | jq '.'
```

**Expected output**:
```json
{
  "real_trading_enabled": true,
  "reason": "All safety gates passed",
  "exposure_limit_krw": 100000,
  "circuit_breaker_active": false
}
```

**⚠️ If `real_trading_enabled: false`**:
- Stop immediately
- Review error in `reason` field
- Fix issue before proceeding

### Step 10: Start Signal Engine

```bash
# Terminal 2: Signal Engine
cd v9/
python3 signal_engine/websocket_emitter.py 2>&1 | tee imei_os/live_logs/signal_engine.log
```

**Watch for**:
```
WebSocket connection established
```

### Step 11: Start Dashboard

```bash
# Terminal 3: Dashboard
cd v9/
python3 dashboard/dashboard_app.py 2>&1 | tee imei_os/live_logs/dashboard.log
```

**Open browser**:
```
http://localhost:5000
```

**Verify**:
- Mode badge shows: "🔴 LIVE TRADING MODE"
- KPIs display correctly
- Holdings panel works

### Step 12: Small Test Trade

**CRITICAL**: Monitor the first trade **VERY CLOSELY**

```bash
# Terminal 4: Monitor trades
tail -f imei_os/TRADING_LOG.csv
```

**Watch for**:
1. First signal generated
2. Signal validated
3. **REAL** buy order placed on Upbit
4. Position tracked in dashboard
5. Exit logic triggers (partial or time-stop)
6. **REAL** sell order placed on Upbit
7. Trade logged with reasons

**Verify on Upbit**:
- Log into Upbit web/app
- Check order history
- Confirm orders match bot logs

**If first trade FAILS**:
1. **STOP IMMEDIATELY** (see Emergency Stop below)
2. Review logs for errors
3. Check Upbit order history
4. Fix issue
5. Restart from Step 8

**If first trade SUCCEEDS**:
- ✅ Proceed to Step 13

---

## 👀 Monitor First 10 Trades

**DO NOT LEAVE unattended for first 10 trades**

### Real-Time Monitoring

```bash
# Terminal 4: Real-time status
watch -n 10 '
echo "=== $(date) ==="
echo ""
curl -s http://localhost:5000/api/kpis | jq "{equity, daily_pnl, position_count, trades_today}"
echo ""
curl -s http://localhost:5000/api/holdings | jq ".[]"
echo ""
tail -5 imei_os/TRADING_LOG.csv
'
```

### Checklist (Every Trade)

For **each of the first 10 trades**, verify:

| Trade # | Entry OK? | Exit OK? | Reasons Logged? | Upbit Confirmed? | Notes |
|---------|-----------|----------|-----------------|------------------|-------|
| 1       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 2       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 3       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 4       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 5       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 6       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 7       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 8       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 9       | [ ]       | [ ]      | [ ]             | [ ]              |       |
| 10      | [ ]       | [ ]      | [ ]             | [ ]              |       |

### Watch For Issues

**Immediate stop if**:
- Orders fail to execute on Upbit
- Exit logic not triggering
- Exposure limit breached
- Circuit breaker activates incorrectly
- WebSocket disconnects
- System crash

---

## 📈 Scale Exposure Gradually

After **10 successful trades** with acceptable performance:

### Evaluate Performance

```bash
# Generate report for first 10 trades
python3 v9/scripts/practice_24h_report.py
```

**Requirements to scale**:
- [ ] 10 trades completed
- [ ] Win rate ≥ 55%
- [ ] No major issues
- [ ] Exposure never breached 100k
- [ ] All exits logged correctly

### Increase to 200k KRW

```bash
# Stop Execution Engine
pkill -f "websocket_receiver"

# Edit .env
nano v9/.env
# Change: FIRST_PHASE_EXPOSURE_LIMIT=100000
# To:     FIRST_PHASE_EXPOSURE_LIMIT=200000

# Restart Execution Engine
cd v9/
python3 execution_engine/websocket_receiver.py 2>&1 | tee imei_os/live_logs/execution_engine.log
```

### Scaling Plan

| Phase | Trades | Exposure Limit | Notes |
|-------|--------|----------------|-------|
| 1     | 0-10   | 100,000 KRW    | Very close monitoring |
| 2     | 10-20  | 200,000 KRW    | Close monitoring |
| 3     | 20-50  | 500,000 KRW    | Regular monitoring |
| 4     | 50+    | 1,000,000 KRW  | Established system |

**Only scale if**:
- Previous phase successful
- Win rate maintained ≥55%
- Max drawdown ≤5%
- No system issues

---

## 🚨 Emergency Procedures

### Emergency Stop (All Issues)

```bash
# STEP 1: Kill all processes
pkill -f "websocket_emitter"
pkill -f "websocket_receiver"
pkill -f "dashboard_app"

# STEP 2: Disable real trading
export ENABLE_REAL_TRADING=false
sudo rm /enable_live.flag

# STEP 3: Verify stopped
ps aux | grep -E "websocket|dashboard" | grep -v grep
# Should show nothing

echo "✅ Emergency stop complete"
```

### Force Exit All Positions

**If system crashed but positions still open**:

```bash
cd v9/

python3 << 'EOF'
from execution_engine.trade_executor import TradeExecutor
import os
from dotenv import load_dotenv

load_dotenv('.env')

access = os.getenv('UPBIT_ACCESS_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')

executor = TradeExecutor(access, secret, practice_mode=False)

print("Current positions:")
for ticker in executor.positions:
    print(f"  {ticker}")

confirm = input("\nForce exit ALL positions? (type 'YES' to confirm): ")

if confirm == 'YES':
    for ticker in list(executor.positions.keys()):
        success, msg = executor.execute_exit(ticker, "EMERGENCY_EXIT", 100.0)
        print(f"{ticker}: {msg}")
    print("\n✅ All positions closed")
else:
    print("❌ Cancelled")
EOF
```

### Disable Real Trading (Controlled)

```bash
# Stop processes gracefully
pkill -f "websocket_emitter"
pkill -f "websocket_receiver"

# Edit .env
nano v9/.env
# Change: ENABLE_REAL_TRADING=true
# To:     ENABLE_REAL_TRADING=false

# Remove flag
sudo rm /enable_live.flag

# Restart in practice mode
cd v9/
python3 execution_engine/websocket_receiver.py
```

### Manual Circuit Breaker Reset

**If circuit breaker triggered incorrectly**:

```bash
cd v9/

python3 << 'EOF'
from execution_engine.safety_gates import SafetyGates

gates = SafetyGates()
gates.reset_circuit_breaker()

print("✅ Circuit breaker reset")
EOF
```

---

## 📝 Live Trading Log

Use this to document live trading session:

```
Date: __________
Start Time: __________
End Time: __________

Initial Capital: ______ KRW
Exposure Limit: ______ KRW

First 10 Trades Summary:
- Trades Completed: ______
- Win Rate: ______%
- Total P&L: ______ KRW
- Issues Encountered: 

Scaling Decisions:
- [ ] After 10 trades: Increase to 200k
- [ ] After 20 trades: Increase to 500k
- [ ] After 50 trades: Increase to 1M

Notes:


Signed: __________
```

---

## ✅ Post-Live Checklist

After enabling live trading, ensure:

- [ ] All systems running smoothly
- [ ] First 10 trades monitored
- [ ] Performance acceptable (≥55% win rate)
- [ ] Exposure limit respected
- [ ] Circuit breaker functional
- [ ] Emergency procedures tested (dry run)
- [ ] Daily monitoring schedule established
- [ ] Weekly performance review scheduled

---

## 🎓 Best Practices

### Daily Routine

1. **Morning** (before market open):
   - Check dashboard
   - Review overnight positions
   - Check safety gates status
   - Review circuit breaker not triggered

2. **During Trading**:
   - Monitor active positions
   - Watch for exit triggers
   - Check exposure limit
   - Review new entries

3. **Evening** (after market close):
   - Generate daily report
   - Review win rate
   - Check max drawdown
   - Document any issues

### Weekly Review

- [ ] Total trades
- [ ] Win rate trend
- [ ] R:R trend
- [ ] Max drawdown
- [ ] Strategy performance
- [ ] System stability
- [ ] Adjust parameters if needed

### Monthly Review

- [ ] Overall performance vs targets
- [ ] Exposure scaling decisions
- [ ] Strategy adjustments
- [ ] System optimizations
- [ ] Lessons learned

---

**CONGRATULATIONS!** You are now live trading with v9.

**Remember**:
- Monitor closely, especially first 10 trades
- Scale exposure gradually
- Never exceed risk tolerance
- Emergency stop procedures ready
- Review performance regularly

---

**Created**: 2026-02-18  
**Version**: 9.0  
**Status**: Live trading enablement guide  
**Risk**: HIGH - Real money at risk
