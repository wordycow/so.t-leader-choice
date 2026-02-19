#!/usr/bin/env python3
"""
자동 메모리 백업 스크립트
매일 실행되어 imei_memory.db를 백업
"""

import os
import shutil
import sqlite3
from datetime import datetime

BACKUP_DIR = "runtime/backup"
DB_PATH = "imei_memory.db"

def backup_memory():
    """메모리 DB 백업"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"imei_memory_{timestamp}.db")
    
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, backup_file)
        print(f"✅ Memory backed up: {backup_file}")
        
        # 백업 메타데이터
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 통계
        c.execute("SELECT COUNT(*) FROM emei_user_memory")
        memory_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM emei_conversations WHERE datetime(expires_at) > datetime('now')")
        conversation_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM emei_knowledge")
        knowledge_count = c.fetchone()[0]
        
        conn.close()
        
        print(f"   - User memories: {memory_count}")
        print(f"   - Active conversations: {conversation_count}")
        print(f"   - Knowledge entries: {knowledge_count}")
        
        return backup_file
    else:
        print(f"❌ DB not found: {DB_PATH}")
        return None

if __name__ == "__main__":
    backup_memory()
