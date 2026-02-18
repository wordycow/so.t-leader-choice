#!/usr/bin/env python3
"""
IMEI Auto Web Search Learning v3.0

When RAG confidence is low:
1. Show "검색 중..." indicator
2. Perform web search
3. Summarize results
4. Answer question
5. Save to knowledge pool
"""

import logging
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSearchLearning:
    """
    Automatic web search and knowledge acquisition
    """
    
    def __init__(
        self,
        search_api_key: Optional[str] = None,
        ollama_url: str = "http://localhost:11434"
    ):
        self.search_api_key = search_api_key
        self.ollama_url = ollama_url
        self.confidence_threshold = 0.7  # Below this, trigger search
    
    def should_search(self, rag_confidence: float) -> bool:
        """
        Determine if web search is needed
        
        Args:
            rag_confidence: Confidence score from RAG (0.0 - 1.0)
        
        Returns:
            True if should perform web search
        """
        return rag_confidence < self.confidence_threshold
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform web search
        
        Args:
            query: Search query
            num_results: Number of results to fetch
        
        Returns:
            List of search results with title, snippet, url
        """
        # Mock implementation - replace with actual search API
        # (Google Custom Search, Bing, etc.)
        
        logger.info(f"🔍 Searching web for: {query}")
        
        # Mock results for testing
        mock_results = [
            {
                "title": "비트코인 트레이딩 가이드",
                "snippet": "비트코인 트레이딩의 기본 전략과 RSI, MACD 등의 지표 활용법을 설명합니다.",
                "url": "https://example.com/bitcoin-trading-guide"
            },
            {
                "title": "암호화폐 투자 전략",
                "snippet": "장기 투자와 단기 트레이딩의 차이, 포트폴리오 구성 방법을 다룹니다.",
                "url": "https://example.com/crypto-investment-strategy"
            }
        ]
        
        return mock_results[:num_results]
    
    def summarize_results(self, query: str, results: List[Dict]) -> str:
        """
        Summarize search results using LLM
        
        Args:
            query: Original query
            results: Search results
        
        Returns:
            Summarized content
        """
        # Build context from results
        context = ""
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\n{result['snippet']}\n\n"
        
        # Generate summary using Ollama
        prompt = f"""Based on these search results, provide a concise answer to: "{query}"

Search Results:
{context}

Please provide a clear, factual answer in Korean. Cite sources where relevant."""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                summary = response.json().get('response', '')
                logger.info(f"✅ Search results summarized")
                return summary
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return self._fallback_summary(results)
        
        except Exception as e:
            logger.error(f"❌ Summarization failed: {e}")
            return self._fallback_summary(results)
    
    def _fallback_summary(self, results: List[Dict]) -> str:
        """Fallback summary if LLM fails"""
        summary = "웹 검색 결과:\n\n"
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n{result['snippet']}\n\n"
        return summary
    
    def learn_from_search(
        self,
        query: str,
        memory_engine
    ) -> Dict:
        """
        Complete learning pipeline:
        1. Search web
        2. Summarize
        3. Save to knowledge
        
        Args:
            query: User query
            memory_engine: PersistentMemoryEngine instance
        
        Returns:
            Learning result with answer and metadata
        """
        # Step 1: Search
        results = self.search_web(query)
        
        if not results:
            return {
                "success": False,
                "message": "검색 결과를 찾을 수 없습니다.",
                "answer": None
            }
        
        # Step 2: Summarize
        summary = self.summarize_results(query, results)
        
        # Step 3: Save to knowledge pool
        memory_engine.save_knowledge(
            question=query,
            answer=summary,
            source="web_search",
            quality_score=0.7  # Lower than manual entries
        )
        
        logger.info(f"📚 Knowledge acquired from web search")
        
        return {
            "success": True,
            "message": "검색 결과를 학습했습니다.",
            "answer": summary,
            "sources": [r['url'] for r in results],
            "learned_at": datetime.now().isoformat()
        }
    
    def get_search_indicator_html(self) -> str:
        """Get HTML for search indicator"""
        return """
<div class="search-indicator" style="
    display: inline-block;
    padding: 8px 16px;
    background: #e3f2fd;
    border-radius: 20px;
    color: #1976d2;
    font-size: 14px;
    margin: 10px 0;
">
    🔍 검색 중...
</div>
"""


if __name__ == "__main__":
    # Test web search learning
    logging.basicConfig(level=logging.INFO)
    
    # Mock memory engine
    class MockMemoryEngine:
        def save_knowledge(self, question, answer, source, quality_score):
            print(f"Knowledge saved: {question[:50]}...")
    
    search = WebSearchLearning()
    memory = MockMemoryEngine()
    
    print("\n=== Test 1: Should search? ===")
    print(f"Confidence 0.9: {search.should_search(0.9)}")  # False
    print(f"Confidence 0.5: {search.should_search(0.5)}")  # True
    
    print("\n=== Test 2: Web search ===")
    results = search.search_web("비트코인 트레이딩 전략")
    for r in results:
        print(f"- {r['title']}")
    
    print("\n=== Test 3: Learn from search ===")
    result = search.learn_from_search(
        "RSI 지표는 어떻게 사용하나요?",
        memory
    )
    print(f"Success: {result['success']}")
    print(f"Answer: {result.get('answer', 'N/A')[:100]}...")
    
    print("\n=== Test 4: Search indicator ===")
    print(search.get_search_indicator_html())
