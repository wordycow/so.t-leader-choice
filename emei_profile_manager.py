#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Emei 프로필 관리 시스템
- 사용자가 말한 Emei 정보를 영구 저장
- "너 나이는?" → DB에서 불러와서 "저는 25살이에요!"
"""

import sqlite3
import json
from datetime import datetime

class EmeiProfileManager:
    """Emei 프로필 저장 및 불러오기"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """프로필 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        
        # Emei 기본 프로필 테이블
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emei_profile (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 사용자별 Emei 학습 데이터
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emei_user_memory (
                user_id TEXT NOT NULL,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, memory_key)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Emei 프로필 테이블 초기화 완료")
    
    def set_profile(self, key: str, value: str):
        """Emei 프로필 저장
        
        예: set_profile("age", "25")
            set_profile("gender", "female")
            set_profile("personality", "친절하고 따뜻함")
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO emei_profile (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        conn.commit()
        conn.close()
        print(f"✅ Emei 프로필 저장: {key}={value}")
    
    def get_profile(self, key: str, default=None):
        """Emei 프로필 불러오기"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT value FROM emei_profile WHERE key = ?", (key,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return row[0]
        return default
    
    def get_all_profiles(self):
        """모든 프로필 불러오기"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("SELECT key, value FROM emei_profile")
        profiles = {row[0]: row[1] for row in cur.fetchall()}
        conn.close()
        return profiles
    
    def remember_user(self, user_id: str, key: str, value: str):
        """사용자별 정보 기억
        
        예: remember_user("wordycow", "name", "이유송")
            remember_user("wordycow", "gender", "male")
            remember_user("wordycow", "preference", "비트코인 위주")
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO emei_user_memory (user_id, memory_key, memory_value, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, key, value))
        conn.commit()
        conn.close()
        print(f"✅ 사용자 기억: [{user_id}] {key}={value}")
    
    def recall_user(self, user_id: str, key: str, default=None):
        """사용자 정보 회상"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            SELECT memory_value FROM emei_user_memory 
            WHERE user_id = ? AND memory_key = ?
        """, (user_id, key))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return row[0]
        return default
    
    def recall_all_user_info(self, user_id: str):
        """사용자에 대한 모든 기억"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            SELECT memory_key, memory_value FROM emei_user_memory 
            WHERE user_id = ?
        """, (user_id,))
        memories = {row[0]: row[1] for row in cur.fetchall()}
        conn.close()
        return memories
    
    def get_introduction(self):
        """Emei 자기소개 생성"""
        profiles = self.get_all_profiles()
        
        age = profiles.get("age", "알 수 없음")
        gender = profiles.get("gender", "female")
        personality = profiles.get("personality", "친절하고 따뜻한")
        
        gender_kr = "여자" if gender == "female" else "남자"
        
        intro = f"저는 이메이예요! 💜 {age}살 {gender_kr}이고, {personality} 성격이에요. "
        intro += "트레이딩 파트너로서 차트 분석, 리스크 관리, 심리 상담 다 해드릴게요!"
        
        return intro


# 테스트 코드
if __name__ == "__main__":
    profile = EmeiProfileManager("/home/user/webapp/upbit_bot.db")
    
    # 기본 프로필 설정
    profile.set_profile("age", "25")
    profile.set_profile("gender", "female")
    profile.set_profile("personality", "친절하고 따뜻하며 함께하려는 의지가 강함")
    profile.set_profile("experience", "3년차 트레이더")
    
    # 사용자 기억
    profile.remember_user("wordycow", "name", "이유송")
    profile.remember_user("wordycow", "gender", "male")
    profile.remember_user("wordycow", "role", "창조자")
    
    # 확인
    print("\n📊 Emei 프로필:")
    print(profile.get_all_profiles())
    
    print("\n👤 wordycow 정보:")
    print(profile.recall_all_user_info("wordycow"))
    
    print("\n👋 Emei 자기소개:")
    print(profile.get_introduction())
