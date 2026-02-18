#!/usr/bin/env python3
import os
os.environ['OLLAMA_URL'] = 'http://ollama.thetheunique.com'
os.environ['OLLAMA_MODEL'] = 'qwen2.5:7b'

from emei_response_router import EmeiRouter

router = EmeiRouter(
    db_path="/home/user/webapp/upbit_bot.db",
    ollama_url="http://ollama.thetheunique.com",
    ollama_model="qwen2.5:7b"
)

print("🧪 EmeiRouter 직접 테스트\n")

# 테스트 1: DB 답변
result1 = router.chat(user_id="test", message="안녕")
print(f"✅ DB 테스트: {result1['response'][:50]}...")
print(f"   응답 시간: {result1['response_time']}초\n")

# 테스트 2: AI 생성 (DB에 없는 질문)
result2 = router.chat(user_id="test", message="오늘 비트코인 시장 전망은 어때?")
print(f"✅ AI 테스트: {result2['response'][:100]}...")
print(f"   응답 시간: {result2['response_time']}초")
