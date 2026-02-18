# IMEI Operating System - Current State

**Last Updated**: 2026-02-18 12:00:00 UTC

## System Overview
- **Bot Version**: v8.0 ULTIMATE
- **Server Status**: ✅ Running on port 5000
- **Trading Mode**: 🔶 Practice Mode (Paper Trading)
- **Real Orders**: 🔴 DISABLED (Default Policy)

## Active Users
1. **wordycow** - Practice seed: 1,000,000 KRW
2. **lee1** - Practice seed: 1,500,000 KRW
3. **guest_10.64.13.98** - Practice seed: 1,000,000 KRW
4. **1** - Practice seed: 1,000,000 KRW

## Trading Engine Status
- **Scan Loop**: ✅ Operational
- **Pattern Analysis**: ✅ Working (9-12s per ticker)
- **Entry Logic**: ✅ Working (max 3 positions normal, 1 in recovery)
- **Exit Logic**: ✅ Working (+2%/-2% or 6h max hold)
- **Recovery Mode**: ✅ Implemented (Martingale-based)

## RAG System Status
- **Knowledge Entries**: 154 items in emei_knowledge table
- **DB Threshold**: 0.62
- **Top-K Retrieval**: 4
- **Fallback**: Ollama (qwen2.5:7b)
- **RAG Debug Endpoint**: ✅ /api/debug/rag_test implemented

## Recent Issues Resolved
1. ✅ Bot thread crash (try-except wrapper added)
2. ✅ Scan logic not executing (indentation fixed)
3. ✅ entry_time datetime conversion (bot_state_manager.py fixed)
4. ✅ Ticker list API delay (fixed list of 50 tickers)
5. ✅ RAG verification endpoint added

## Current Trading Positions (Latest Known)
- **wordycow**: 3 holdings (KRW-NEAR, KRW-BTC, KRW-TRX), Cash: 614,125 KRW
- Other users: Status to be monitored

## Performance Metrics
- **CPU Usage**: 20-30% per bot (80-120% for 4 bots)
- **Memory Usage**: 1.2% per bot (5% for 4 bots)
- **Scan Duration**: ~2.5 minutes (15 tickers × 9-12s each)
- **Loop Interval**: 20s (normal) / 15s (recovery)

## Next Update Cycle
This file should be updated at the start of each major operational loop or debugging session.

---
*Note: This STATE.md file serves as the single source of truth for IMEI's operational context. Never fabricate information. Log unknowns in CREATOR_QUESTIONS.md.*
