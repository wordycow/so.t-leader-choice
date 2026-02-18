# V9 Testing & Validation Guide

## 🎯 Testing Objectives

1. Verify Signal Engine signal generation
2. Verify Execution Engine trade execution
3. Verify WebSocket communication
4. Verify partial exit logic (3%, 5%, 7%)
5. Verify recovery engine for -20% positions
6. Verify BTC stacking from profits
7. Verify safety gates double-lock
8. Verify circuit breaker activation
9. Verify dashboard real-time data

---

## 📋 Pre-Test Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pyupbit pandas numpy websockets flask`
- [ ] `.env` file configured with Upbit API keys
- [ ] Ollama running (for IMEI chat integration)
- [ ] `ENABLE_REAL_TRADING=false` (practice mode)
- [ ] `/enable_live.flag` does NOT exist

---

## 🧪 Test Suite

### Test 1: Shared Modules

**Objective**: Verify constants and signal schema

```bash
cd /home/user/webapp/v9

python3 -c "from shared.constants import *; print(f'✅ Constants loaded: {CAPITAL_PER_TRADE_PCT}% per trade')"

python3 -c "from shared.signal_schema import Signal; from datetime import datetime; s = Signal('test_001', 'ULTRA_SCALP', 'KRW-BTC', 0.85, 0.92, 'BULL', datetime.now()); print(f'✅ Signal created: {s.ticker} confidence={s.confidence}')"
```

**Expected**: No errors, values printed

**Status**: [ ] Pass [ ] Fail

---

### Test 2: Signal Engine - Snapshot Scorer

**Objective**: Verify TOP 20 candidate selection

```bash
python3 signal_engine/snapshot_scorer.py
```

**Expected Output**:
- Fetches all KRW tickers
- Calculates snapshot scores
- Returns TOP 20 list
- Each candidate has: ticker, score, price_change, delta_money, delta_volume

**Check**:
- [ ] Score calculation correct
- [ ] Top 20 sorted by score descending
- [ ] Execution time < 60s

**Status**: [ ] Pass [ ] Fail

---

### Test 3: Signal Engine - BTC Regime Detector

**Objective**: Verify FULL_DOWNTREND detection

```bash
python3 signal_engine/btc_regime_detector.py
```

**Expected Output**:
- Fetches BTC 1H + 4H data
- Calculates trends
- Detects FULL_DOWNTREND (if both bearish + spike)
- Returns regime status

**Check**:
- [ ] Regime detected correctly
- [ ] Logs show trend analysis
- [ ] FULL_DOWNTREND blocks entries

**Status**: [ ] Pass [ ] Fail

---

### Test 4: Signal Engine - Ultra Scalp Monitor

**Objective**: Verify 1m Bollinger + RSI < 20 detection

```bash
python3 signal_engine/ultra_scalp_monitor.py
```

**Expected Output**:
- Fetches 1m data for test ticker
- Calculates Bollinger bands (20,2)
- Calculates RSI (14)
- Detects entry signal when conditions met

**Check**:
- [ ] Bollinger bands calculated
- [ ] RSI < 20 detected
- [ ] Volume spike detected
- [ ] Signal generated with confidence

**Status**: [ ] Pass [ ] Fail

---

### Test 5: Signal Engine - Deep Hunter Monitor

**Objective**: Verify 1h oversold detection

```bash
python3 signal_engine/deep_hunter_monitor.py
```

**Expected Output**:
- Fetches 1h data
- Calculates RSI < 30
- Detects declining volume
- Identifies support level
- Generates staged entry signal

**Check**:
- [ ] RSI oversold detected
- [ ] Support level identified
- [ ] 3-stage allocation calculated

**Status**: [ ] Pass [ ] Fail

---

### Test 6: Execution Engine - Signal Validator

**Objective**: Verify all filters

```bash
python3 execution_engine/signal_validator.py
```

**Expected Output**:
- Test 1: Normal validation → EXECUTE
- Test 2: FULL_DOWNTREND regime → REJECT
- Test 3: Max positions reached → REJECT

**Check**:
- [ ] All validation scenarios work
- [ ] Correct action returned (EXECUTE/REJECT)
- [ ] Reason provided

**Status**: [ ] Pass [ ] Fail

---

### Test 7: Execution Engine - Trade Executor

**Objective**: Verify entry + partial exits

```bash
python3 execution_engine/trade_executor.py
```

**Expected Output**:
- Entry executed (practice mode)
- Position created
- Portfolio status returned

**Check**:
- [ ] Entry logged
- [ ] Fee calculated (0.05%)
- [ ] Position tracked

**Manual Test** (requires running bot):
- Wait for +3% → verify 30% exit + stop to breakeven
- Wait for +5% → verify 40% exit + trailing enabled
- Wait for +7% → verify 30% exit with trailing
- Wait 6 min without +1% → verify TIME_STOP

**Status**: [ ] Pass [ ] Fail

---

### Test 8: Execution Engine - Recovery Engine

**Objective**: Verify -20% position handling

```bash
python3 execution_engine/recovery_engine.py
```

**Expected Output**:
- Critical position detected (-21%)
- Least-negative positions identified
- Partial liquidation executed (10-50%)
- Recovery action logged

**Check**:
- [ ] -20% trigger works
- [ ] Correct liquidation candidates
- [ ] Capital raised
- [ ] Re-allocation decision based on regime

**Status**: [ ] Pass [ ] Fail

---

### Test 9: Execution Engine - BTC Stacker

**Objective**: Verify profit → BTC conversion

```bash
python3 execution_engine/btc_stacker.py
```

**Expected Output**:
- Test 1: 5k profit → no purchase (below threshold)
- Test 2: 15k profit → BTC purchase
- Test 3: Multiple purchases logged
- BTC stacking status returned

**Check**:
- [ ] Threshold respected (10k KRW)
- [ ] BTC amount calculated correctly
- [ ] Log saved to `imei_os/BTC_STACKING_LOG.json`
- [ ] ROI calculated

**Status**: [ ] Pass [ ] Fail

---

### Test 10: Execution Engine - Safety Gates

**Objective**: Verify double-lock system

```bash
python3 execution_engine/safety_gates.py
```

**Expected Output**:
- Test 1: No env/flag → DISABLED
- Test 2: Env set → still DISABLED (no flag)
- Test 3: Exposure breach → DISABLED
- Test 4: Daily drawdown -3% → Circuit breaker activated

**Check**:
- [ ] Both env + flag required
- [ ] Exposure limit enforced (100k)
- [ ] Daily drawdown limit enforced (-2%)
- [ ] Circuit breaker triggers

**Status**: [ ] Pass [ ] Fail

---

### Test 11: WebSocket Integration

**Objective**: Verify Signal Engine → Execution Engine communication

**Steps**:
1. Terminal 1: `python3 signal_engine/websocket_emitter.py`
2. Terminal 2: `python3 execution_engine/websocket_receiver.py`
3. Observe logs in both terminals

**Expected**:
- Signal Engine connects on ws://localhost:8765
- Signals generated every X seconds
- Execution Engine receives signals
- Signals validated
- Trade actions taken (if filters pass)

**Check**:
- [ ] WebSocket connection established
- [ ] Signals transmitted
- [ ] Signals received and parsed
- [ ] No connection errors

**Status**: [ ] Pass [ ] Fail

---

### Test 12: Dashboard

**Objective**: Verify dashboard UI and APIs

**Steps**:
1. `python3 dashboard/dashboard_app.py`
2. Open browser: `http://localhost:5000`
3. Test all API endpoints

**Expected**:
- Dashboard loads with KPIs
- TOP 20 panel shows candidates
- Holdings panel shows positions
- Trades panel shows recent trades

**API Tests**:
```bash
curl http://localhost:5000/api/kpis
curl http://localhost:5000/api/top20
curl http://localhost:5000/api/holdings
curl http://localhost:5000/api/trades
curl http://localhost:5000/api/safety
curl http://localhost:5000/api/recovery
curl http://localhost:5000/api/btc_stacking
```

**Check**:
- [ ] Dashboard UI loads
- [ ] All panels display data
- [ ] APIs return valid JSON
- [ ] Auto-refresh works (10s)

**Status**: [ ] Pass [ ] Fail

---

## 📸 Required Test Evidence

### Screenshot 1: TOP 20 Rotation
- Run snapshot scorer twice (5 min apart)
- Show different candidates due to market movement
- Highlight score changes

### Screenshot 2: WebSocket Active
- Show Signal Engine terminal with "Signal sent" logs
- Show Execution Engine terminal with "Signal received" logs
- Show signal payload (JSON)

### Screenshot 3: Ultra Scalp Partial Exits
- Position at +3.2% → 30% exit log
- Stop moved to breakeven log
- Position at +5.1% → 40% exit log
- Trailing stop enabled log
- Position at +7.5% → 30% exit with trailing log

### Screenshot 4: Time-Stop Trigger
- Position held 6 min without reaching +1%
- TIME_STOP exit log
- Full position closed

### Screenshot 5: FULL_DOWNTREND Activation
- BTC regime detector showing both 1H + 4H bearish
- Stable-coin spike detected
- FULL_DOWNTREND = TRUE
- New entry signal → REJECTED with reason

### Screenshot 6: Recovery Action
- Position showing -21% loss
- Recovery engine activated
- Least-negative position liquidated (30%)
- Capital raised log
- Recovery action saved

### Screenshot 7: BTC Stacking
- Trade exit with 15,000 KRW profit
- BTC purchase triggered
- BTC amount calculated
- Log entry in `BTC_STACKING_LOG.json`
- Total BTC accumulated updated

### Screenshot 8: Safety Gate Test
- Check status without env/flag → DISABLED
- Set `ENABLE_REAL_TRADING=true` → still DISABLED
- Create `/enable_live.flag` → ENABLED
- Simulate -2.5% daily loss → Circuit breaker ACTIVE

---

## ✅ Test Summary

| Test | Status | Notes |
|------|--------|-------|
| Shared Modules | [ ] | |
| Snapshot Scorer | [ ] | |
| BTC Regime Detector | [ ] | |
| Ultra Scalp Monitor | [ ] | |
| Deep Hunter Monitor | [ ] | |
| Signal Validator | [ ] | |
| Trade Executor | [ ] | |
| Recovery Engine | [ ] | |
| BTC Stacker | [ ] | |
| Safety Gates | [ ] | |
| WebSocket Integration | [ ] | |
| Dashboard | [ ] | |

**Overall Status**: [ ] All Pass [ ] Some Failures

---

## 🐛 Known Issues

(Document any issues found during testing)

---

## 📝 Test Notes

(Add any observations, edge cases, or recommendations)

---

## 🚀 Next Steps After Testing

1. [ ] Fix any identified bugs
2. [ ] Re-run failed tests
3. [ ] Complete 24-hour practice run
4. [ ] Generate performance report (win rate, R:R, MDD)
5. [ ] Review with creator (Yusong)
6. [ ] Approve real-trading phase
7. [ ] Create `/enable_live.flag`
8. [ ] Monitor first 10 live trades
9. [ ] Scale exposure limit if successful

---

**Test Date**: ___________  
**Tested By**: ___________  
**Test Duration**: ___________  
**Result**: [ ] PASS [ ] FAIL
