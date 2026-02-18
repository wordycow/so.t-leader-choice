# IMEI Knowledge Sources Registry

**Last Updated**: 2026-02-18 12:00:00 UTC

---

## 1. Manual Learning Entries
**Source Type**: User-provided Q&A pairs via chat interface  
**Format**: "학습: [question] => [answer]"  
**Storage**: `emei_knowledge` table in `upbit_bot.db`  
**Quality Score**: 1.0 (manual entries)  
**Count**: Part of 154 total entries  
**Retrieval**: Jaccard + SequenceMatcher hybrid scoring  
**Last Verified**: 2026-02-18  

**Example Entry**:
```
Q: RSI 지표가 뭐야
A: RSI(Relative Strength Index)는 과매수/과매도를 판단하는 지표입니다.
```

---

## 2. Database Knowledge (emei_knowledge table)
**Location**: `/home/user/webapp/upbit_bot.db`  
**Table**: `emei_knowledge`  
**Columns**:
- `id` (INTEGER PRIMARY KEY)
- `question` (TEXT)
- `answer` (TEXT)
- `source` (TEXT) - e.g., 'manual', 'youtube', 'backtest'
- `quality_score` (REAL) - default 1.0, range [0.0, 3.0]
- `use_count` (INTEGER) - increments on each retrieval
- `last_used` (TIMESTAMP)
- `created_at` (TIMESTAMP)

**Total Entries**: 154  
**Retrieval Method**: 
1. Tokenize query
2. Compute Jaccard similarity + SequenceMatcher ratio
3. Apply quality weighting: `score = (0.55*jac + 0.45*seq) * (0.85 + 0.15*qscore)`
4. Return top-4 results
5. Use if best score ≥ 0.62 (EMIE_DB_THRESHOLD)

**Last Indexed**: 2026-02-18  

---

## 3. YouTube Learning Data
**Status**: 🔶 TO BE VERIFIED (Step 4)  
**Expected Storage**: TBD (Check for transcript/subtitle tables or embeddings)  
**Ingest Pipeline**: TBD (Check for indexing/embedding scripts)  
**Integration**: Should appear in emei_knowledge.source = 'youtube'  

**Action Required**:
- [ ] Identify YouTube data storage location
- [ ] Verify ingest/embedding pipeline exists
- [ ] Confirm YouTube sources appear in RAG top-k results
- [ ] Document in REPORT_03_YOUTUBE_RAG.md

---

## 4. Backtest Pattern Data
**Source**: Historical pattern analysis results  
**Location**: Likely in `emei_knowledge` with source='backtest'  
**Purpose**: Provide empirical evidence for strategy decisions  
**Files**: `backtest_patterns.py`, `show_backbacktest_report.py`  

---

## 5. Trading Log Data (Future)
**Source**: Real-time trade execution logs  
**Storage**: `imei_os/TRADING_LOG.csv`  
**Purpose**: Ground RAG responses in actual trading performance  
**Status**: 🔴 Not yet implemented (Step 3)  

---

## 6. Ollama Fallback Knowledge
**Model**: qwen2.5:7b (primary), gemma3:4b (backup)  
**URL**: http://ollama.thetheunique.com  
**Trigger**: When DB search score < 0.62 threshold  
**Context Injection**: Top-4 DB results included in prompt even on fallback  
**Temperature**: 0.4 (normal), 0.65 (retry for diversity)  

---

## Source Priority Hierarchy
1. **DB Exact Match** (score ≥ 0.62) → Direct answer from emei_knowledge
2. **Profile-based Auto Response** → Immediate return
3. **Ollama + Context** → LLM with top-4 DB results as context
4. **Fallback Message** → "지금 정보로는 확실히 모르겠어요..."

---

## Maintenance Notes
- DB entries with `use_count > 0` indicate active retrieval
- `last_used` timestamp tracks recent relevance
- Quality scores can be manually adjusted for tuning
- New sources should be appended to this document with verification date

---

*This registry must remain synchronized with actual system state. All sources must be verifiable.*
