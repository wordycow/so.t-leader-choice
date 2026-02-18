# 🎓 Upbit Bot v9 - Onboarding Roadmap

## 📋 Overview

This document provides a **step-by-step onboarding path** from installation to live trading. Follow each step in order.

**Total Time**: 3-7 days (depending on validation period)

---

## 🛣️ Onboarding Path

```
Step 1: README          → Understand features & setup
Step 2: ARCHITECTURE    → Learn system design & data flow
Step 3: TESTING_GUIDE   → Run unit & integration tests
Step 4: strategies.json → Study strategy specifications
Step 5: trade_executor  → Understand exit logic
Step 6: safety_gates    → Learn safety system
Step 7: 24h Practice    → Validate performance
Step 8: Go Live         → Enable real trading
```

---

## 📍 Step 1: Read README.md (15 minutes)

**Goal**: Understand what v9 does and key differences from v8

### What to Learn:
- [x] 2-engine architecture (Signal vs Execution)
- [x] Signal Engine runs on local PC (RTX 5070ti)
- [x] Execution Engine runs on Novita server
- [x] TOP 20 candidate selection (5-min snapshot diff)
- [x] BTC FULL_DOWNTREND regime filter
- [x] Ultra Scalp v2.1 staged exits (3%, 5%, 7%)
- [x] Deep Hunter 3-stage averaging
- [x] Recovery engine for -20% positions
- [x] BTC auto-stacking (profits ≥10k KRW)
- [x] Safety gates (double-lock + limits)

### Action:
```bash
cd /home/user/webapp/v9
cat README.md | less
```

**Next**: Proceed to Step 2

---

## 📍 Step 2: Study ARCHITECTURE_V9.md (30 minutes)

**Goal**: Understand system design, data flow, and boundaries

### What to Learn:
- [x] **Data Flow Diagram**:
  ```
  Upbit → Snapshot Scorer → TOP 20 → Regime Filter → Strategy Monitors
    ↓
  Signal Generation → WebSocket → Execution Engine
    ↓
  Validation → Entry → Position Management → Exits
    ↓
  Trade Log + BTC Stacking + Dashboard
  ```
  
- [x] **Clear Boundaries**:
  - Signal Engine: Never trades, no API keys
  - Execution Engine: All money movement, all validation
  
- [x] **WebSocket Message Schema**:
  ```json
  {
    "signal_id": "uuid",
    "strategy_id": "ULTRA_SCALP",
    "ticker": "KRW-DOGE",
    "confidence": 0.85,
    "snapshot_score": 0.92,
    "btc_regime": "BULL",
    "timestamp": "2026-02-18T14:00:00"
  }
  ```

- [x] **Rate Limiting**:
  - Snapshot fetched every 5 minutes (not per-ticker)
  - Global BTC metrics cached (1H, 4H)
  - Candidate-specific 1m data only for TOP 20

- [x] **Storage Layout**:
  - `imei_os/TRADING_LOG.csv` - All trades
  - `imei_os/BTC_STACKING_LOG.json` - BTC purchases
  - `upbit_bot.db` - Bot state, positions, recovery log

- [x] **Failure Modes**:
  - WS disconnect → Auto-reconnect (5s retry)
  - Snapshot failure → Skip cycle, log warning
  - API 429 → Exponential backoff
  - Execution failure → Log, continue

### Action:
```bash
cat ARCHITECTURE_V9.md | less
```

**Quiz** (answer before proceeding):
1. Which engine holds Upbit API keys? ➜ **Execution Engine**
2. What triggers FULL_DOWNTREND? ➜ **BTC 1H+4H both bearish + stablecoin spike**
3. Where are trade logs stored? ➜ **imei_os/TRADING_LOG.csv**

**Next**: Proceed to Step 3

---

## 📍 Step 3: Run TESTING_GUIDE.md (1-2 hours)

**Goal**: Validate all modules work correctly

### 3.1 Unit Tests (30 min)

Run each test and verify output:

```bash
# Shared modules
python3 -c "from shared.constants import *; print(f'✅ {CAPITAL_PER_TRADE_PCT}% per trade')"

# Signal Engine
python3 signal_engine/snapshot_scorer.py        # TOP 20 list
python3 signal_engine/btc_regime_detector.py    # Regime status
python3 signal_engine/ultra_scalp_monitor.py    # Signal generation
python3 signal_engine/deep_hunter_monitor.py    # Signal generation

# Execution Engine
python3 execution_engine/signal_validator.py    # Validation scenarios
python3 execution_engine/trade_executor.py      # Entry/exit logic
python3 execution_engine/recovery_engine.py     # -20% handling
python3 execution_engine/btc_stacker.py         # Profit → BTC
python3 execution_engine/safety_gates.py        # Double-lock test
```

**Checklist**:
- [ ] All tests run without errors
- [ ] Snapshot scorer returns TOP 20 list
- [ ] Regime detector shows current status
- [ ] Validators reject correctly
- [ ] Safety gates enforce double-lock

### 3.2 Integration Test (30 min)

Test WebSocket communication:

```bash
# Terminal 1: Start Signal Engine
python3 signal_engine/websocket_emitter.py

# Terminal 2: Start Execution Engine  
python3 execution_engine/websocket_receiver.py

# Observe logs in both terminals
```

**Expected**:
- Signal Engine: "Signal sent: {signal_data}"
- Execution Engine: "Signal received: {signal_data}"
- No connection errors

**Checklist**:
- [ ] WebSocket connection established
- [ ] Signals transmitted
- [ ] Signals received & parsed
- [ ] Validation runs

### 3.3 Dashboard Test (10 min)

```bash
# Terminal 3: Start Dashboard
python3 dashboard/dashboard_app.py

# Browser
open http://localhost:5000
```

**Checklist**:
- [ ] Dashboard loads
- [ ] KPIs display
- [ ] TOP 20 panel shows data
- [ ] Holdings panel works
- [ ] Trades panel works
- [ ] API endpoints return JSON

**Next**: Proceed to Step 4

---

## 📍 Step 4: Study strategies.json (20 minutes)

**Goal**: Understand strategy specifications and schema

### Schema Requirements

Every strategy **must** have:

```json
{
  "id": "ULTRA_SCALP",
  "display_name": "Ultra Scalp v2.1",
  "indicators": {
    "bollinger": {"period": 20, "std": 2},
    "rsi": {"period": 14, "threshold": 20}
  },
  "entry_rules": {
    "price_condition": "below_lower_bollinger",
    "rsi_condition": "below_20",
    "candle_pattern": "3_consecutive_red",
    "volume_spike": true
  },
  "exit_rules": {
    "partial_exits": [
      {"profit_pct": 3.0, "exit_pct": 30.0, "action": "MOVE_STOP_BE"},
      {"profit_pct": 5.0, "exit_pct": 40.0, "action": "ENABLE_TRAILING"},
      {"profit_pct": 7.0, "exit_pct": 30.0, "action": "TRAILING_EXIT"}
    ]
  },
  "stop_loss_pct": null,
  "take_profit_pct": 7.0,
  "trailing_stop_pct": 1.5,
  "time_stop_seconds": 360,
  "position_cap_pct": 10.0,
  "notes": "Creator approved spec"
}
```

### YouTube Strategy Import Rule

**CRITICAL**: Only import strategies that conform to schema.

If any required field is missing:
- ❌ **Reject** immediately, OR
- ⚠️ Queue for `creator_review` in `CREATOR_QUESTIONS.md`

**stop_loss_pct** can be `null` ONLY if strategy is:
- Time-based exit (like Ultra Scalp time-stop)
- Regeneration-based (like recovery mode)

**Action**:
```bash
cat strategies.json | python3 -m json.tool
```

**Checklist**:
- [ ] ULTRA_SCALP_V2_1 present
- [ ] DEEP_HUNTER present
- [ ] All required fields present
- [ ] Understand partial exit stages

**Next**: Proceed to Step 5

---

## 📍 Step 5: Study trade_executor.py (30 minutes)

**Goal**: Understand exit logic in detail

### Key Functions

1. **execute_entry()**
   - Receives signal
   - Calculates position size (10% equity)
   - Places buy order (practice or live)
   - Creates position tracking
   - Logs entry with reason

2. **check_exits()**
   - Monitors all open positions
   - Checks exit conditions:
     - Time-stop (6 min without +1%)
     - Trailing stop (after +7%, if -1.8% from peak)
     - Partial exits (+3%, +5%, +7%)
   - Returns list of (ticker, exit_reason, exit_pct)

3. **execute_exit()**
   - Executes sell order (full or partial)
   - Updates position tracking
   - Records exit with reason
   - Logs: PARTIAL_3, PARTIAL_5, TRAIL_7, TIME_STOP

### Ultra Scalp v2.1 Exit Stages

```python
# Stage 1: +3% reached
→ Sell 30% of position
→ Move stop to breakeven (entry price)
→ Log: "PARTIAL_3"

# Stage 2: +5% reached  
→ Sell 40% of remaining position
→ Enable trailing stop (1.5%)
→ Log: "PARTIAL_5"

# Stage 3: +7% reached
→ Sell remaining 30% with trailing
→ If price drops -1.8% from peak → exit
→ Log: "TRAIL_7"

# Time-Stop: 6 minutes elapsed
→ If profit < +1% → full exit
→ Log: "TIME_STOP"
```

### Exit Reason Consistency

All exits **must** log:
- `entry_reason`: Why entry was triggered
- `exit_reason`: Why exit was triggered
- `profit_pct`: Final profit %
- `time_held_min`: Minutes in position

**Action**:
```bash
cat execution_engine/trade_executor.py | grep -A20 "def execute_exit"
```

**Checklist**:
- [ ] Understand partial exit flow
- [ ] Know when stop moves to breakeven
- [ ] Know when trailing activates
- [ ] Understand time-stop logic

**Next**: Proceed to Step 6

---

## 📍 Step 6: Study safety_gates.py (20 minutes)

**Goal**: Understand safety system & real-trading gates

### Double-Lock System

Real trading requires **BOTH**:

```python
# Check 1: Environment variable
ENABLE_REAL_TRADING=true  # in .env

# Check 2: Flag file
/enable_live.flag  # must exist
```

**Default**: Practice mode (both checks fail)

### Hard Limits

```python
# Exposure limit (first phase)
FIRST_PHASE_EXPOSURE_LIMIT = 100000  # KRW

# Daily drawdown circuit breaker
DAILY_DRAWDOWN_LIMIT_PCT = 2.0  # -2% daily loss

# Capital rules
CAPITAL_PER_TRADE_PCT = 10.0      # % per trade
MAX_CONCURRENT_TRADES = 2         # Max positions
MAX_TOTAL_ALLOCATION_PCT = 20.0   # Total equity %
```

### Safety Gate Checks

```python
def is_real_trading_allowed():
    checks = [
        ("ENV", check_env_variable()),
        ("FLAG", check_flag_file()),
        ("CIRCUIT_BREAKER", check_circuit_breaker()),
        ("EXPOSURE", check_exposure_limit()),
        ("DRAWDOWN", check_daily_drawdown())
    ]
    
    # ALL must pass
    return all(ok for _, ok, _ in checks)
```

### Circuit Breaker

**Trigger**: Daily equity drop > 2%

**Actions**:
- ❌ Block new entries
- ✅ Allow exits
- 📝 Log activation
- ⏸️ Manual reset required

**Action**:
```bash
cat execution_engine/safety_gates.py | grep -A30 "class SafetyGates"
```

**Checklist**:
- [ ] Understand double-lock requirement
- [ ] Know exposure limit (100k KRW)
- [ ] Know circuit breaker trigger (-2%)
- [ ] Know how to reset circuit breaker

**Next**: Proceed to Step 7

---

## 📍 Step 7: 24-Hour Practice Run (1-2 days)

**Goal**: Validate system performance before live trading

### 7.1 Start Practice Mode

```bash
# Verify practice mode (default)
grep ENABLE_REAL_TRADING .env
# Should show: ENABLE_REAL_TRADING=false

# Verify no flag file
ls /enable_live.flag
# Should show: No such file or directory

# Start all components
# Terminal 1: Signal Engine
python3 signal_engine/websocket_emitter.py

# Terminal 2: Execution Engine
python3 execution_engine/websocket_receiver.py

# Terminal 3: Dashboard
python3 dashboard/dashboard_app.py

# Terminal 4: Monitor logs
tail -f imei_os/TRADING_LOG.csv
```

### 7.2 Validation Checklist

Monitor for 24 hours and check:

**Candidate Rotation**:
- [ ] TOP 20 list updates every 5 minutes
- [ ] Candidates change based on market movement
- [ ] Scores reflect snapshot diff correctly

**WebSocket Stability**:
- [ ] No disconnections for 24 hours
- [ ] Signals transmitted continuously
- [ ] Latency < 100ms

**Trades Logged**:
- [ ] All entries have `entry_reason`
- [ ] All exits have `exit_reason`
- [ ] Exit reasons match strategy:
  - PARTIAL_3, PARTIAL_5, TRAIL_7, TIME_STOP

**Daily P&L Tracked**:
- [ ] Starting equity recorded
- [ ] Ending equity calculated
- [ ] Daily profit/loss computed
- [ ] Percentage gain/loss tracked

**Max Drawdown Tracked**:
- [ ] Peak equity recorded
- [ ] Current drawdown calculated
- [ ] Max drawdown during 24h period

**Sample Size**:
- [ ] Minimum 10 trades executed
- [ ] At least 3 full entry→exit cycles
- [ ] Both ULTRA_SCALP and DEEP_HUNTER tested

### 7.3 Generate Reports

Run hourly snapshots:

```bash
# Create hourly report script
cat > scripts/hourly_snapshot.sh << 'EOF'
#!/bin/bash
echo "=== $(date) ==="
echo "Positions: $(curl -s http://localhost:5000/api/holdings | jq '.[] | length')"
echo "Trades: $(curl -s http://localhost:5000/api/trades | jq '.[] | length')"
echo "P&L: $(curl -s http://localhost:5000/api/kpis | jq '.daily_pnl')"
echo ""
EOF

chmod +x scripts/hourly_snapshot.sh

# Run every hour (cron or manual)
watch -n 3600 scripts/hourly_snapshot.sh
```

End-of-day summary:

```bash
# Generate 24-hour report
python3 scripts/daily_report.py
# Review: imei_os/DAILY_REPORT_2026-02-18.md
```

### 7.4 PASS/FAIL Criteria

**PASS Requirements** (all must be true):

- [x] Win rate ≥ 55%
- [x] Average R:R ≥ 1.5:1
- [x] Max drawdown ≤ 5%
- [x] Expected value > 0
- [x] No system crashes
- [x] All exits logged correctly
- [x] Circuit breaker not triggered
- [x] Sample size ≥ 10 trades

**FAIL Conditions** (any triggers fail):

- [ ] Win rate < 50%
- [ ] Max drawdown > 10%
- [ ] System crash/freeze
- [ ] Exit reasons missing
- [ ] Circuit breaker triggered incorrectly

### 7.5 Review & Adjust

If **PASS**:
- ✅ Proceed to Step 8 (Go Live)

If **FAIL**:
- ⚠️ Review logs
- 🔧 Adjust thresholds
- 🔄 Re-run 24-hour test

**Action**:
```bash
# Review full report
cat imei_os/DAILY_REPORT_2026-02-18.md
```

**Next**: If PASS → Proceed to Step 8

---

## 📍 Step 8: Go Live (30 minutes setup + ongoing monitoring)

**Goal**: Enable real trading with safety limits

### 8.1 Pre-Live Checklist

Confirm before enabling:

- [x] 24-hour practice run PASSED
- [x] Win rate ≥ 55%
- [x] Max drawdown ≤ 5%
- [x] All tests completed
- [x] Safety gates understood
- [x] Emergency procedures reviewed
- [x] Upbit API keys verified
- [x] Sufficient balance (≥200k KRW recommended)

### 8.2 Enable Real Trading

**Step-by-step** (follow exactly):

```bash
# Step 1: Stop all running processes
pkill -f "websocket_emitter"
pkill -f "websocket_receiver"
pkill -f "dashboard_app"

# Step 2: Edit .env
nano .env
# Change: ENABLE_REAL_TRADING=false
# To:     ENABLE_REAL_TRADING=true
# Save and exit

# Step 3: Create flag file
sudo touch /enable_live.flag
ls -l /enable_live.flag
# Verify file exists

# Step 4: Verify exposure limit
grep FIRST_PHASE_EXPOSURE_LIMIT .env
# Should show: FIRST_PHASE_EXPOSURE_LIMIT=100000

# Step 5: Verify daily drawdown limit
grep DAILY_DRAWDOWN_LIMIT_PCT .env
# Should show: DAILY_DRAWDOWN_LIMIT_PCT=2.0

# Step 6: Restart Execution Engine (DO NOT START SIGNAL ENGINE YET)
python3 execution_engine/websocket_receiver.py

# Step 7: Check safety gates
curl http://localhost:5000/api/safety | jq '.'
# Verify: "real_trading_enabled": true

# Step 8: Start Signal Engine
python3 signal_engine/websocket_emitter.py

# Step 9: Start Dashboard
python3 dashboard/dashboard_app.py
```

### 8.3 Small Live Test

Before full operation, run a **small test trade**:

```bash
# Monitor first trade closely
tail -f imei_os/TRADING_LOG.csv

# Watch dashboard
open http://localhost:5000

# Verify first trade:
# - Entry executed (real order)
# - Position tracked
# - Exit triggered correctly
# - Profit/loss recorded
```

**Checklist**:
- [ ] First trade entry successful (real Upbit order)
- [ ] Position appears in dashboard
- [ ] Exit logic works (partial or time-stop)
- [ ] Trade logged with reasons
- [ ] No errors in execution

### 8.4 Monitor First 10 Trades

**Stay close** for first 10 live trades:

```bash
# Real-time monitoring
watch -n 10 'echo "=== Status ===" && curl -s http://localhost:5000/api/kpis | jq "." && echo "" && curl -s http://localhost:5000/api/holdings | jq "."'
```

**Watch for**:
- ✅ Entries execute correctly
- ✅ Partial exits trigger at +3%, +5%, +7%
- ✅ Time-stops trigger at 6 minutes
- ✅ Exposure stays ≤100k KRW
- ⚠️ No circuit breaker activation

### 8.5 Scale Exposure Gradually

After **10 successful trades** with good performance:

```bash
# Increase exposure limit
nano .env
# Change: FIRST_PHASE_EXPOSURE_LIMIT=100000
# To:     FIRST_PHASE_EXPOSURE_LIMIT=200000

# Restart Execution Engine
pkill -f "websocket_receiver"
python3 execution_engine/websocket_receiver.py
```

**Scaling Plan**:
- 10 trades @ 100k → increase to 200k
- 20 trades @ 200k → increase to 500k
- 50 trades @ 500k → remove limit (or set to 1M)

### 8.6 Emergency Stop

If anything goes wrong:

```bash
# IMMEDIATE STOP
pkill -f "websocket_emitter"
pkill -f "websocket_receiver"

# Disable real trading
export ENABLE_REAL_TRADING=false
rm /enable_live.flag

# Force exit all positions (if needed)
python3 -c "
from execution_engine.trade_executor import TradeExecutor
exec = TradeExecutor('key', 'secret', practice_mode=False)
for ticker in exec.positions:
    exec.execute_exit(ticker, 'EMERGENCY_EXIT', 100.0)
"
```

**Next**: Ongoing monitoring & optimization

---

## 📊 Progress Tracker

Use this to track your onboarding progress:

- [ ] **Step 1**: Read README.md (15 min)
- [ ] **Step 2**: Study ARCHITECTURE_V9.md (30 min)
- [ ] **Step 3**: Run TESTING_GUIDE.md (1-2 hours)
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] Dashboard test
- [ ] **Step 4**: Study strategies.json (20 min)
- [ ] **Step 5**: Study trade_executor.py (30 min)
- [ ] **Step 6**: Study safety_gates.py (20 min)
- [ ] **Step 7**: 24-hour practice run (1-2 days)
  - [ ] Start practice mode
  - [ ] Validate checklist
  - [ ] Generate reports
  - [ ] PASS criteria met
- [ ] **Step 8**: Go live (30 min + ongoing)
  - [ ] Pre-live checklist
  - [ ] Enable real trading
  - [ ] Small test trade
  - [ ] Monitor first 10 trades
  - [ ] Scale exposure

---

## 🎓 Completion

**Congratulations!** You've completed v9 onboarding.

**What's Next**:
1. Monitor daily performance
2. Review weekly reports
3. Adjust strategies based on results
4. Scale exposure as confidence grows
5. Add new strategies (follow schema)

**Support**:
- Questions? See `CREATOR_QUESTIONS.md`
- Issues? Check logs in `imei_os/`
- Emergencies? Follow emergency procedures above

---

**Created**: 2026-02-18  
**Version**: 9.0  
**Status**: Complete onboarding path  
**Estimated Time**: 3-7 days total
