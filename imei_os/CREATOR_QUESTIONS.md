# Questions for Creator (Yusong)

**Last Updated**: 2026-02-18 12:00:00 UTC

---

## Priority: HIGH 🔴

### 1. Real Order Approval Gate
**Asked**: 2026-02-18  
**Context**: Currently real orders are disabled by default. Need approval mechanism before enabling.  
**Question**: 
- What is the approval process for enabling real orders?
- Should there be a manual switch, or automatic after X successful paper trades?
- Any specific capital limits or risk checks required?

**Status**: ⏳ Awaiting Response

---

### 2. YouTube Learning Data Location
**Asked**: 2026-02-18  
**Context**: Need to verify YouTube subtitle/transcript integration for Step 4.  
**Question**:
- Where is YouTube data stored? (Table name, file location?)
- Is there an indexing/embedding pipeline already built?
- Are subtitles being ingested automatically or manually?

**Status**: ⏳ Awaiting Response

---

### 3. RAG Threshold Tuning Authority
**Asked**: 2026-02-18  
**Context**: Current threshold 0.62 seems high; most queries fall back to Ollama.  
**Question**:
- Can we adjust EMIE_DB_THRESHOLD in production?
- What was the original rationale for 0.62?
- Should we run systematic threshold optimization experiments?

**Status**: ⏳ Awaiting Response

---

## Priority: MEDIUM 🔶

### 4. Trading Strategy Priority
**Asked**: 2026-02-18  
**Question**:
Which strategies should be prioritized for optimization?
- Volume Hunter (current workhorse)
- Dip Hunter
- Squeeze Momentum
- Recovery Mode (Martingale)
- New strategies to develop?

**Status**: ⏳ Awaiting Response

---

### 5. Performance Metrics Targets
**Asked**: 2026-02-18  
**Question**:
What are acceptable performance metrics for paper trading validation?
- Minimum win rate? (e.g., >55%)
- Minimum R:R ratio? (e.g., >1.5)
- Maximum drawdown tolerance? (e.g., <20%)
- Minimum sample size before going live? (e.g., 100 trades)

**Status**: ⏳ Awaiting Response

---

### 6. Multi-User Session Management
**Asked**: 2026-02-18  
**Context**: Currently 4 users running simultaneously (wordycow, lee1, guest, "1")  
**Question**:
- Is this intentional or should we consolidate to single user?
- How to handle session conflicts (e.g., same ticker bought by 2 users)?
- Priority order if capital allocation conflicts arise?

**Status**: ⏳ Awaiting Response

---

## Priority: LOW 🟢

### 7. Logging Verbosity Control
**Asked**: 2026-02-18  
**Question**:
Debug logs are currently very verbose (per-user files in /tmp/).
- Should we implement log level control (DEBUG/INFO/WARNING/ERROR)?
- Rotate logs daily or keep indefinitely?
- Centralized logging service (e.g., ELK stack)?

**Status**: ⏳ Awaiting Response

---

### 8. API Rate Limit Strategy
**Asked**: 2026-02-18  
**Context**: Upbit API has rate limits; currently using fixed 50-ticker list.  
**Question**:
- Should we dynamically adjust ticker count based on API quota?
- Implement exponential backoff on rate limit errors?
- Use Upbit Pro/Enterprise API tier?

**Status**: ⏳ Awaiting Response

---

### 9. Backup and Disaster Recovery
**Asked**: 2026-02-18  
**Question**:
- How often should we backup upbit_bot.db?
- Where to store backups? (AI Drive, external S3?)
- Automated backup script needed?

**Status**: ⏳ Awaiting Response

---

## Resolved Questions ✅

### ~~Bot Thread Crash Issue~~
**Asked**: 2026-02-18 09:00  
**Resolved**: 2026-02-18 10:00  
**Solution**: Wrapped bot_main_loop in try-except, fixed indentation  

### ~~entry_time Datetime Conversion~~
**Asked**: 2026-02-18 09:30  
**Resolved**: 2026-02-18 09:45  
**Solution**: Added `datetime.fromisoformat()` in bot_state_manager.py  

### ~~Scan Logic Not Running~~
**Asked**: 2026-02-18 09:50  
**Resolved**: 2026-02-18 10:00  
**Solution**: Fixed else-block indentation, scan now executes properly  

---

## Question Submission Guidelines

**Format**:
```markdown
### [Question Title]
**Asked**: YYYY-MM-DD  
**Context**: Brief background  
**Question**: Clear, specific question(s)  
**Status**: ⏳ Awaiting Response | ✅ Resolved | 🔴 Urgent
```

**Rules**:
1. Never fabricate answers - mark as "⏳ Awaiting Response"
2. Link to relevant code/docs when available
3. Move resolved questions to bottom section
4. Tag with priority: 🔴 HIGH | 🔶 MEDIUM | 🟢 LOW

---

*This file serves as a permanent record of unknowns. Check here before making assumptions.*
