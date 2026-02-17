"""
이메이 학습 지식 저장 시스템
- 모르는 질문 → 웹 검색 → 답변 학습
- 같은 질문 두번째부터 즉시 답변
"""

import json
import os
from datetime import datetime

KNOWLEDGE_FILE = "emei_learned_knowledge.json"

def load_knowledge():
    """학습된 지식 불러오기"""
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_knowledge(knowledge):
    """학습된 지식 저장"""
    with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

def find_similar_question(question, knowledge, threshold=0.7):
    """유사한 질문 찾기 (단순 키워드 매칭)"""
    question_lower = question.lower()
    question_words = set(question_lower.split())
    
    best_match = None
    best_score = 0
    
    for q, data in knowledge.items():
        q_lower = q.lower()
        q_words = set(q_lower.split())
        
        # 자카드 유사도
        intersection = len(question_words & q_words)
        union = len(question_words | q_words)
        score = intersection / union if union > 0 else 0
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = (q, data)
    
    return best_match

def learn_new_knowledge(question, answer, source="web"):
    """새로운 지식 학습"""
    knowledge = load_knowledge()
    
    knowledge[question] = {
        "answer": answer,
        "source": source,
        "learned_at": datetime.now().isoformat(),
        "usage_count": 0
    }
    
    save_knowledge(knowledge)
    return True

def get_learned_answer(question):
    """학습된 답변 가져오기"""
    knowledge = load_knowledge()
    
    # 정확히 같은 질문
    if question in knowledge:
        knowledge[question]["usage_count"] += 1
        save_knowledge(knowledge)
        return knowledge[question]["answer"]
    
    # 유사한 질문 찾기
    match = find_similar_question(question, knowledge)
    if match:
        q, data = match
        data["usage_count"] += 1
        save_knowledge(knowledge)
        return data["answer"]
    
    return None

def get_knowledge_stats():
    """학습 통계"""
    knowledge = load_knowledge()
    return {
        "total_questions": len(knowledge),
        "most_asked": sorted(knowledge.items(), key=lambda x: x[1]["usage_count"], reverse=True)[:5]
    }

