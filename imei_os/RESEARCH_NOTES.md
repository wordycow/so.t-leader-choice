# IMEI Research & Development Notes

**Last Updated**: 2026-02-18 12:00:00 UTC

---

## Current Research Focus

### 1. RAG System Performance Optimization
**Date**: 2026-02-18  
**Status**: ✅ Verified functional, threshold tuning needed  

**Findings**:
- Current DB threshold: 0.62
- Test query "급등 포착하는 방법" → Top score: 0.0581 (below threshold)
- Test query "RSI 과매수" → Top score: 0.3297 (below threshold)
- Most queries fall back to Ollama due to low similarity scores

**Hypothesis**:
The 0.62 threshold may be too high for Korean-language Q&A with current similarity algorithm (Jaccard + SequenceMatcher).

**Proposed Experiments**:
1. Test with threshold values: [0.3, 0.4, 0.5, 0.62, 0.7]
2. Compare answer quality at each threshold
3. Consider implementing BM25 or embedding-based retrieval
4. Evaluate Korean-specific tokenization (morphological analysis)

**Next Steps**:
- [ ] Run A/B test with 100 sample queries
- [ ] Measure precision/recall at different thresholds
- [ ] Document optimal threshold in this file

---

### 2. Trading Strategy Performance Analysis
**Date**: 2026-02-18  
**Status**: 🔶 In Progress (24-hour paper trading initiated)  

**Current Strategies Implemented**:
- Volume Hunter (volume surge detection)
- Dip Hunter (price drop + RSI oversold)
- Squeeze Momentum (Bollinger Bands + TTM Squeeze)
- Box Range (range-bound consolidation)
- Gap Down Reversal (placeholder)

**Metrics to Track** (Step 3):
- Win Rate per strategy
- Average Risk:Reward ratio
- Expected Value (EV)
- Max Drawdown
- Daily P/L
- Trade count per strategy
- Average hold time

**Baseline Performance** (2026-02-18 09:00-10:00):
- User: wordycow
- Starting capital: 1,000,000 KRW
- Ending capital: 614,125 KRW (cash) + 385,875 KRW (invested)
- Trades executed: 3 (KRW-NEAR, KRW-BTC, KRW-TRX)
- Unrealized P/L: To be calculated after exits

**Research Questions**:
1. Which strategy has highest win rate in current market?
2. Does recovery mode (Martingale) improve overall EV?
3. What is optimal max_hold_time (currently 6 hours)?
4. Should we adjust TP/SL from ±2%?

---

### 3. YouTube Learning Integration
**Date**: 2026-02-18  
**Status**: 🔴 Not Yet Verified (Step 4)  

**Research Objective**:
Verify that YouTube subtitle/transcript data is:
1. Properly stored in database
2. Indexed for RAG retrieval
3. Actually appearing in top-k search results

**Files to Investigate**:
- `emei_learning.py`
- `enhanced_emei_learning.py`
- `restore_all_learning_data.py`
- Any scripts with "youtube" or "transcript" in name

**Expected Outcome**:
YouTube-sourced knowledge entries should:
- Have `source='youtube'` in emei_knowledge table
- Appear in `/api/debug/rag_test` results when relevant
- Contribute to better trading strategy selection

**Verification Test**:
Query: "비트코인 투자 전략" → Should retrieve YouTube-learned content

---

### 4. Pattern Analysis Latency Reduction
**Date**: 2026-02-18  
**Current**: 9-12 seconds per ticker  
**Target**: <5 seconds per ticker  

**Bottleneck Analysis**:
- `detect_squeeze_momentum()` calls multiple Upbit API endpoints
- RSI, Bollinger Bands calculation requires 200 candles
- No caching of recent candle data

**Proposed Optimizations**:
1. **Batch API Calls**: Request multiple tickers in single call
2. **Candle Caching**: Store last 200 candles, only fetch latest
3. **Parallel Processing**: Use ThreadPoolExecutor for pattern analysis
4. **Indicator Reuse**: Share RSI/BB calculations across strategies

**Expected Impact**:
- Reduce scan duration from 2.5 min → ~1 min
- Enable scanning 30 tickers instead of 15
- Faster response to market opportunities

---

### 5. Recovery Mode Effectiveness
**Date**: 2026-02-18  
**Status**: 🔶 Implemented, not yet validated  

**Current Logic**:
- Triggered after 3 consecutive losses
- Reduces max_positions to 1
- 2-minute cooldown after loss
- Searches only top 10 tickers
- Position size formula: `capital * 0.3 * (1.2 ** consecutive_losses)`

**Concerns**:
- Martingale can amplify losses in trending market
- 120-second cooldown may miss recovery opportunities
- Top 10 tickers may not have best recovery setups

**Validation Plan**:
1. Run 7-day backtest with/without recovery mode
2. Compare max drawdown and recovery time
3. Test alternative recovery strategies (mean reversion, etc.)
4. Document findings with statistical significance

---

## Experimental Ideas (Future)

### A. Multi-Model Ensemble
Use multiple Ollama models (qwen, gemma, llama) and vote on answers.

### B. Reinforcement Learning for Strategy Selection
Train RL agent to select best strategy based on market regime.

### C. Real-time Alert System
Telegram/Discord bot for:
- Trade notifications
- Unusual pattern detection
- System health alerts

### D. Web Dashboard Enhancements
- Live candlestick charts
- Position P/L tracking
- Strategy performance breakdown
- RAG query inspector

---

## Research Log Format

```
### [Topic]
**Date**: YYYY-MM-DD
**Status**: 🔴 Not Started | 🔶 In Progress | ✅ Completed
**Findings**: ...
**Next Steps**: ...
```

---

*All research notes must be grounded in empirical data or clearly marked as hypotheses.*
