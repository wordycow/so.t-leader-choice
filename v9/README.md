# Upbit Bot v9 - Complete System

## 🎯 Overview

Upbit Bot v9 is a complete rewrite with **2-engine architecture** for aggressive yet controlled cryptocurrency trading on Upbit.

### Key Features
- **Signal Engine** (RTX 5070ti): Generates signals, never touches money
- **Execution Engine** (Novita server): Validates, executes, manages all trades
- **Ultra Scalp** + **Deep Hunter** strategies
- Partial exits (3%, 5%, 7%) with trailing stops
- Recovery engine for -20% positions
- BTC auto-stacking from profits ≥10k KRW
- Double-lock safety gates
- Single-screen compact dashboard

---

## 📁 Directory Structure

```
v9/
├── shared/                    # Shared modules
│   ├── constants.py           # System-wide constants
│   └── signal_schema.py       # Signal/response data classes
│
├── signal_engine/             # Signal Engine (local PC)
│   ├── snapshot_scorer.py     # TOP 20 candidate selector
│   ├── btc_regime_detector.py # FULL_DOWNTREND detection
│   ├── ultra_scalp_monitor.py # 1m Bollinger strategy
│   ├── deep_hunter_monitor.py # 1h oversold strategy
│   └── websocket_emitter.py   # Signal → Execution WS
│
├── execution_engine/          # Execution Engine (Novita server)
│   ├── websocket_receiver.py  # Receives signals from Signal Engine
│   ├── signal_validator.py    # Re-validates all filters
│   ├── trade_executor.py      # Entry + partial exits
│   ├── recovery_engine.py     # Portfolio recovery (-20% handling)
│   ├── btc_stacker.py         # Auto-convert profits to BTC
│   └── safety_gates.py        # Double-lock + exposure limits
│
├── dashboard/                 # Web dashboard
│   ├── dashboard_app.py       # Flask app
│   ├── templates/
│   │   └── index.html         # Compact single-page dashboard
│   └── static/                # CSS/JS assets
│
├── strategies.json            # Strategy definitions (ULTRA_SCALP, DEEP_HUNTER, etc.)
├── .env.example               # Environment variable template
└── ARCHITECTURE_V9.md         # Detailed architecture doc

```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd v9/

# Copy environment template
cp .env.example .env

# Edit .env and add your Upbit API keys
nano .env
```

### 2. Install Dependencies

```bash
pip install pyupbit pandas numpy websockets flask
```

### 3. Run Signal Engine (Local PC with RTX 5070ti)

```bash
python3 signal_engine/websocket_emitter.py
```

### 4. Run Execution Engine (Novita Server)

```bash
python3 execution_engine/websocket_receiver.py
```

### 5. Run Dashboard

```bash
python3 dashboard/dashboard_app.py
```

Access dashboard at: `http://localhost:5000`

---

## 🔒 Safety Gates

### Double-Lock System

Real trading requires **BOTH**:
1. Environment variable: `ENABLE_REAL_TRADING=true`
2. Flag file exists: `/enable_live.flag`

### Hard Limits

- **First phase exposure**: 100,000 KRW max
- **Daily drawdown**: -2% triggers circuit breaker
- **Capital per trade**: 10% of equity
- **Max concurrent trades**: 2
- **Total allocation**: ≤20% of equity

### Testing Safety Gates

```python
from v9.execution_engine.safety_gates import SafetyGates

gates = SafetyGates()

# Check status
status = gates.is_real_trading_allowed(
    current_equity=1000000,
    current_invested=50000
)

print(f"Real trading enabled: {status.real_trading_enabled}")
print(f"Reason: {status.reason}")
```

---

## 📊 Strategies

### ULTRA_SCALP (Active)
- **Timeframe**: 1 minute
- **Entry**: Price below lower Bollinger (20,2) + RSI < 20 + 3 red candles + volume spike
- **Exit**: +3% → sell 30%, +5% → sell 40%, +7% → sell 30% trailing
- **Time-stop**: 6 min without +1%
- **Capital**: 10% per trade, max 2 concurrent

### DEEP_HUNTER (Active)
- **Timeframe**: 1 hour
- **Entry**: RSI < 30 + declining volume + support level
- **Strategy**: 3-stage averaging (40%, 30%, 30%)
- **Exit**: +8% profit target, 2% trailing stop
- **Time-stop**: 48 hours
- **Capital**: 10% per trade, max 2 concurrent

---

## 🧪 Testing Checklist

### Signal Engine Tests

```bash
# Test snapshot scorer
python3 signal_engine/snapshot_scorer.py

# Test BTC regime detector
python3 signal_engine/btc_regime_detector.py

# Test Ultra Scalp monitor
python3 signal_engine/ultra_scalp_monitor.py

# Test Deep Hunter monitor
python3 signal_engine/deep_hunter_monitor.py
```

### Execution Engine Tests

```bash
# Test signal validator
python3 execution_engine/signal_validator.py

# Test trade executor
python3 execution_engine/trade_executor.py

# Test recovery engine
python3 execution_engine/recovery_engine.py

# Test BTC stacker
python3 execution_engine/btc_stacker.py

# Test safety gates
python3 execution_engine/safety_gates.py
```

### Integration Tests

1. **WebSocket Communication**: Start Signal Engine + Execution Engine, verify signal flow
2. **End-to-End Trade**: Generate signal → validate → execute → partial exit → log
3. **Recovery Scenario**: Simulate -20% position → verify liquidation logic
4. **BTC Stacking**: Realize 15k profit → verify BTC purchase
5. **Circuit Breaker**: Simulate -2.5% daily loss → verify auto-halt

---

## 📸 Required Test Logs/Screenshots

1. **TOP 20 rotation** - 5-min snapshot diff showing candidate updates
2. **WebSocket active** - Signal Engine → Execution Engine connection established
3. **Ultra Scalp partial exits** - 3%, 5%, 7% executions with logs
4. **Time-stop** - 6-minute exit trigger
5. **FULL_DOWNTREND activation** - Regime detection blocking new entries
6. **Recovery action** - -20% position triggering liquidation
7. **BTC stacking** - Profit conversion to BTC with log entry
8. **Safety gate test** - Real trading blocked (no env/flag), then enabled

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for full list. Key variables:

- `ENABLE_REAL_TRADING` - Enable real orders (default: false)
- `UPBIT_ACCESS_KEY` - Upbit API access key
- `UPBIT_SECRET_KEY` - Upbit API secret key
- `FIRST_PHASE_EXPOSURE_LIMIT` - Max exposure in KRW (default: 100000)
- `DAILY_DRAWDOWN_LIMIT_PCT` - Daily loss limit % (default: 2.0)

### Strategy Configuration

Edit `strategies.json` to modify strategy parameters:
- Entry indicators
- Exit logic
- Capital rules
- Time-stops

---

## 📈 Monitoring

### Dashboard KPIs

- Total Equity
- Daily P&L
- Cash / Invested
- Position Count
- Trades Today

### Panels

- **TOP 20 Candidates**: Score, price change %, volume
- **Holdings**: Ticker, strategy, profit %, time held
- **Recent Trades**: Time, type, ticker, exit reason, P&L

### API Endpoints

- `GET /api/kpis` - KPI metrics
- `GET /api/top20` - TOP 20 candidates
- `GET /api/holdings` - Current positions
- `GET /api/trades` - Recent trades
- `GET /api/safety` - Safety gates status
- `GET /api/recovery` - Recovery engine status
- `GET /api/btc_stacking` - BTC accumulation status

---

## 🚨 Emergency Procedures

### Manual Circuit Breaker Reset

```python
from v9.execution_engine.safety_gates import SafetyGates

gates = SafetyGates()
gates.reset_circuit_breaker()
```

### Force Exit All Positions

```python
from v9.execution_engine.trade_executor import TradeExecutor

executor = TradeExecutor(access_key, secret_key, practice_mode=False)

for ticker in executor.positions:
    executor.execute_exit(ticker, "EMERGENCY_EXIT", 100.0)
```

### Disable Real Trading

```bash
# Remove flag file
rm /enable_live.flag

# Or set environment variable
export ENABLE_REAL_TRADING=false
```

---

## 📝 Logs

### Trade Log CSV

Location: `imei_os/TRADING_LOG.csv`

Columns: timestamp, type, ticker, strategy, amount, entry_price, exit_price, profit_krw, profit_pct, exit_reason, time_held_min, fee_krw

### BTC Stacking Log

Location: `imei_os/BTC_STACKING_LOG.json`

Contains: total BTC accumulated, total profit invested, purchase history

### Recovery Log

Embedded in Recovery Engine status API

Contains: trigger ticker, trigger loss %, action taken, result

---

## 🎓 Next Steps

1. **Complete 24-hour practice run** - Verify all systems in practice mode
2. **Review logs** - Check trade quality, win rate, drawdown
3. **Adjust thresholds** - Fine-tune entry/exit logic based on results
4. **Enable real trading** - Set env variable + create flag file
5. **Monitor first 10 trades** - Stay close for first live phase
6. **Scale gradually** - Increase exposure limit after validation

---

## 📞 Support

- Architecture: See `ARCHITECTURE_V9.md`
- Strategy details: See `strategies.json`
- Safety: See `safety_gates.py`
- Issues: Create issue in repo

---

## 📜 License

Proprietary - For authorized use only

**Created**: 2026-02-18  
**Version**: 9.0  
**Author**: Yusong + Claude  
**Status**: Complete - Ready for testing
