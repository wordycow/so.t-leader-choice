#!/usr/bin/env python3
"""
IMEI Persistent Memory Engine v3.0

Features:
- Always-on context logging (30-90 days retention)
- Long-term memory with trigger keywords
- Sensitive data redaction
- Export/Import for cloning
- Knowledge sync between instances
"""

import logging
import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a memory entry"""
    memory_id: str
    user_id: str
    memory_type: str  # "conversation", "long_term", "knowledge"
    content: str
    metadata: Dict
    created_at: datetime
    expires_at: Optional[datetime]
    sensitive_redacted: bool


class PersistentMemoryEngine:
    """
    Manages all memory operations for IMEI
    
    Memory Types:
    1. Context (conversations) - 30-90 day retention
    2. Long-term (explicit saves) - No expiration
    3. Knowledge pool - Shared across clones
    """
    
    # Trigger keywords for long-term memory
    MEMORY_TRIGGERS = [
        "학습해", "저장해", "기억해줘", "기억해", 
        "메모해", "알지?", "save", "remember"
    ]
    
    # Sensitive patterns to redact
    SENSITIVE_PATTERNS = [
        (r'\b\d{3,4}[-\s]?\d{4}\b', '[OTP_REDACTED]'),  # OTP codes
        (r'\b[A-Za-z0-9]{32,}\b', '[API_KEY_REDACTED]'),  # API keys
        (r'\b0x[a-fA-F0-9]{40,}\b', '[WALLET_REDACTED]'),  # Crypto wallets
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]'),  # Card numbers
        (r'\b\d{6}[-\s]?\d{7}\b', '[ID_REDACTED]'),  # National ID
        (r'password[:\s]*[^\s]+', 'password: [REDACTED]'),  # Passwords
    ]
    
    def __init__(self, db_path: str = "upbit_bot.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize memory tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Context conversations (30-90 day retention)
        c.execute('''
            CREATE TABLE IF NOT EXISTS emei_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                learned BOOLEAN DEFAULT 0,
                youtube_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        # Long-term user memory (no expiration)
        c.execute('''
            CREATE TABLE IF NOT EXISTS emei_user_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT,
                tags TEXT,
                sensitive_redacted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Knowledge pool (shared across clones)
        c.execute('''
            CREATE TABLE IF NOT EXISTS emei_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                quality_score REAL DEFAULT 0.8,
                use_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Agent state (for export/import)
        c.execute('''
            CREATE TABLE IF NOT EXISTS emei_agent_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_key TEXT UNIQUE NOT NULL,
                state_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Memory engine initialized")
    
    def redact_sensitive_data(self, text: str) -> Tuple[str, bool]:
        """
        Redact sensitive information from text
        
        Returns (redacted_text, was_redacted)
        """
        redacted = text
        was_redacted = False
        
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            if re.search(pattern, redacted, re.IGNORECASE):
                redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
                was_redacted = True
        
        return redacted, was_redacted
    
    def save_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        retention_days: int = 30
    ):
        """
        Save conversation to context log
        Auto-expires after retention_days
        """
        # Redact sensitive data
        message_clean, msg_redacted = self.redact_sensitive_data(message)
        response_clean, resp_redacted = self.redact_sensitive_data(response)
        
        expires_at = datetime.now() + timedelta(days=retention_days)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO emei_conversations
            (user_id, message, response, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message_clean, response_clean, expires_at))
        
        conn.commit()
        conn.close()
        
        if msg_redacted or resp_redacted:
            logger.warning(f"🔒 Sensitive data redacted in conversation")
    
    def check_memory_trigger(self, message: str) -> bool:
        """Check if message contains memory trigger keywords"""
        return any(trigger in message for trigger in self.MEMORY_TRIGGERS)
    
    def save_long_term_memory(
        self,
        user_id: str,
        message: str,
        response: str
    ) -> Dict:
        """
        Save long-term memory (triggered by keywords)
        
        Returns memory card data
        """
        # Extract summary
        summary = self._extract_summary(message, response)
        
        # Redact sensitive data
        summary_clean, was_redacted = self.redact_sensitive_data(summary)
        
        # Generate memory ID
        memory_id = f"mem_{user_id}_{int(datetime.now().timestamp())}"
        
        # Extract tags
        tags = self._extract_tags(message)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO emei_user_memory
            (memory_id, user_id, summary, details, tags, sensitive_redacted)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (memory_id, user_id, summary_clean, response, json.dumps(tags), was_redacted))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Long-term memory saved: {memory_id}")
        
        return {
            "memory_id": memory_id,
            "summary": summary_clean,
            "tags": tags,
            "sensitive_redacted": was_redacted,
            "created_at": datetime.now().isoformat()
        }
    
    def _extract_summary(self, message: str, response: str) -> str:
        """Extract concise summary from conversation"""
        # Simple extraction - first 200 chars of message
        summary = message[:200]
        if len(message) > 200:
            summary += "..."
        return summary
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        # Simple keyword extraction
        keywords = ["trading", "strategy", "bitcoin", "upbit", "profit", "loss"]
        found_tags = [kw for kw in keywords if kw in text.lower()]
        return found_tags
    
    def get_user_memories(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's long-term memories"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT memory_id, summary, tags, created_at, sensitive_redacted
            FROM emei_user_memory
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        memories = []
        for row in c.fetchall():
            memories.append({
                "memory_id": row['memory_id'],
                "summary": row['summary'],
                "tags": json.loads(row['tags']) if row['tags'] else [],
                "created_at": row['created_at'],
                "sensitive_redacted": bool(row['sensitive_redacted'])
            })
        
        conn.close()
        return memories
    
    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete a specific memory"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            DELETE FROM emei_user_memory
            WHERE memory_id = ? AND user_id = ?
        ''', (memory_id, user_id))
        
        deleted = c.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"🗑️ Memory deleted: {memory_id}")
        
        return deleted
    
    def save_knowledge(
        self,
        question: str,
        answer: str,
        source: str = "manual",
        quality_score: float = 0.8
    ):
        """Save to knowledge pool (shared across clones)"""
        # Redact sensitive data
        answer_clean, was_redacted = self.redact_sensitive_data(answer)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO emei_knowledge
            (question, answer, source, quality_score)
            VALUES (?, ?, ?, ?)
        ''', (question, answer_clean, source, quality_score))
        
        conn.commit()
        conn.close()
        
        if was_redacted:
            logger.warning(f"🔒 Sensitive data redacted in knowledge")
    
    def export_state(self, include_user_memory: bool = False) -> Dict:
        """
        Export agent state for cloning
        
        Includes:
        - Agent state
        - Knowledge pool
        - Optionally: user memory (isolated)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        export_data = {
            "version": "3.0",
            "exported_at": datetime.now().isoformat(),
            "agent_state": {},
            "knowledge_pool": [],
            "user_memory": [] if include_user_memory else None
        }
        
        # Export agent state
        c.execute('SELECT state_key, state_value FROM emei_agent_state')
        for row in c.fetchall():
            export_data["agent_state"][row['state_key']] = json.loads(row['state_value'])
        
        # Export knowledge pool
        c.execute('SELECT question, answer, source, quality_score FROM emei_knowledge')
        for row in c.fetchall():
            export_data["knowledge_pool"].append({
                "question": row['question'],
                "answer": row['answer'],
                "source": row['source'],
                "quality_score": row['quality_score']
            })
        
        # Optionally export user memory
        if include_user_memory:
            c.execute('SELECT user_id, memory_id, summary, tags FROM emei_user_memory')
            for row in c.fetchall():
                export_data["user_memory"].append({
                    "user_id": row['user_id'],
                    "memory_id": row['memory_id'],
                    "summary": row['summary'],
                    "tags": json.loads(row['tags']) if row['tags'] else []
                })
        
        conn.close()
        
        logger.info(f"📤 State exported: {len(export_data['knowledge_pool'])} knowledge items")
        
        return export_data
    
    def import_state(self, import_data: Dict, merge: bool = True) -> Dict:
        """
        Import agent state from another instance
        
        Args:
            import_data: Exported state dict
            merge: If True, merge with existing data; if False, replace
        
        Returns:
            Import statistics
        """
        stats = {
            "knowledge_imported": 0,
            "knowledge_duplicates": 0,
            "user_memory_imported": 0,
            "agent_state_updated": 0
        }
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Import knowledge pool (deduplicate)
        for item in import_data.get("knowledge_pool", []):
            # Check if exists
            c.execute('''
                SELECT id FROM emei_knowledge
                WHERE question = ? AND answer = ?
            ''', (item['question'], item['answer']))
            
            if c.fetchone():
                stats["knowledge_duplicates"] += 1
            else:
                c.execute('''
                    INSERT INTO emei_knowledge
                    (question, answer, source, quality_score)
                    VALUES (?, ?, ?, ?)
                ''', (
                    item['question'],
                    item['answer'],
                    item['source'],
                    item['quality_score']
                ))
                stats["knowledge_imported"] += 1
        
        # Import user memory (keep isolated - don't auto-merge)
        if import_data.get("user_memory"):
            logger.warning("⚠️ User memory import skipped (must be manually reviewed)")
        
        # Import agent state
        for key, value in import_data.get("agent_state", {}).items():
            c.execute('''
                INSERT OR REPLACE INTO emei_agent_state
                (state_key, state_value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value), datetime.now()))
            stats["agent_state_updated"] += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"📥 State imported: {stats}")
        
        return stats
    
    def cleanup_expired(self):
        """Remove expired conversations"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            DELETE FROM emei_conversations
            WHERE expires_at < ?
        ''', (datetime.now(),))
        
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"🗑️ Cleaned up {deleted} expired conversations")


if __name__ == "__main__":
    # Test memory engine
    logging.basicConfig(level=logging.INFO)
    
    engine = PersistentMemoryEngine()
    
    print("\n=== Test 1: Save conversation ===")
    engine.save_conversation(
        "test_user",
        "비트코인 가격은 어떻게 되나요?",
        "현재 비트코인 가격은 123,456,789원입니다."
    )
    
    print("\n=== Test 2: Memory trigger ===")
    has_trigger = engine.check_memory_trigger("이거 기억해줘")
    print(f"Has trigger: {has_trigger}")
    
    print("\n=== Test 3: Save long-term memory ===")
    memory_card = engine.save_long_term_memory(
        "test_user",
        "내 트레이딩 전략은 RSI 20 이하에서 매수하는 거야. 기억해줘.",
        "네, 기억했습니다. RSI 20 이하 매수 전략을 저장했어요."
    )
    print(f"Memory saved: {memory_card}")
    
    print("\n=== Test 4: Sensitive data redaction ===")
    text = "내 API 키는 1234567890abcdef1234567890abcdef이고 OTP는 123456이야"
    redacted, was_redacted = engine.redact_sensitive_data(text)
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    print(f"Was redacted: {was_redacted}")
    
    print("\n=== Test 5: Export state ===")
    export = engine.export_state(include_user_memory=True)
    print(f"Exported: {len(export['knowledge_pool'])} knowledge items")
    
    print("\n=== Test 6: Get user memories ===")
    memories = engine.get_user_memories("test_user")
    print(f"User has {len(memories)} memories")
