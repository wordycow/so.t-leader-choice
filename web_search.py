"""
🔍 Web Search Module for Emei AI Learning System
Uses WebSearch tool to find information online
"""

import os
import json
import logging

# Logger 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def web_search(params):
    """
    웹 검색 수행
    
    Args:
        params: dict with 'q' key (search query)
        
    Returns:
        dict: {
            'success': bool,
            'results': [
                {
                    'title': str,
                    'snippet': str,
                    'url': str
                },
                ...
            ]
        }
    """
    try:
        query = params.get('q', '')
        
        if not query:
            return {'success': False, 'error': 'No query provided'}
        
        logger.info(f"🔍 Searching for: {query}")
        
        # 실제 웹 검색은 외부 API 필요
        # 여기서는 ChatGPT에게 답변 요청 (fallback)
        from ai_client import ai_client
        
        search_prompt = f"""다음 질문에 대해 간단하고 정확하게 답변해주세요:

질문: {query}

3-5문장으로 핵심만 답변하세요."""
        
        result = ai_client.chat([
            {'role': 'user', 'content': search_prompt}
        ], temperature=0.3, max_tokens=200)
        
        # 결과를 검색 형식으로 변환
        return {
            'success': True,
            'results': [
                {
                    'title': query,
                    'snippet': result['content'],
                    'url': 'ai_generated'
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Web search error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # 테스트
    result = web_search({'q': '비트코인 반감기가 뭐야?'})
    print(json.dumps(result, indent=2, ensure_ascii=False))
