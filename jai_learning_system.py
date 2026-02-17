#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 자이(JAI) AI 학습 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💜 외부 커뮤니티에서 자동 학습하여 똑똑해지는 AI

핵심 기능:
1. 🐦 트위터 크롤링 - 암호화폐 트렌드 실시간 학습
2. 💬 텔레그램 모니터링 - 코인 채널 대화 분석
3. 🤖 AI 시뮬레이션 - 가상 토론으로 전략 개발
4. 📊 패턴 분석 - 학습한 데이터로 예측 모델 구축
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3
import json
from datetime import datetime, timedelta
import re
from collections import Counter
import asyncio

DB_PATH = 'upbit_bot.db'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 학습 데이터베이스 초기화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def init_learning_tables():
    """학습 시스템 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1️⃣ 학습 패턴 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learned_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT,
            content TEXT NOT NULL,
            sentiment TEXT,
            keywords TEXT,
            coins_mentioned TEXT,
            engagement_score INTEGER DEFAULT 0,
            confidence_score REAL DEFAULT 0.5,
            pattern_type TEXT,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2️⃣ 트렌드 분석 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trend_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            sentiment_score REAL,
            mention_count INTEGER,
            avg_engagement REAL,
            trend_direction TEXT,
            confidence REAL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3️⃣ AI 시뮬레이션 결과
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            participants TEXT,
            discussion TEXT,
            consensus TEXT,
            confidence REAL,
            executed BOOLEAN DEFAULT 0,
            result TEXT,
            simulated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4️⃣ 학습 성과 추적
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id INTEGER,
            prediction TEXT,
            actual_result TEXT,
            accuracy REAL,
            profit_impact REAL,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pattern_id) REFERENCES learned_patterns (id)
        )
    ''')
    
    # 인덱스 생성
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_learned_source ON learned_patterns(source, learned_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trend_coin ON trend_analysis(coin, timeframe, analyzed_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_simulation_topic ON ai_simulations(topic, simulated_at DESC)')
    
    conn.commit()
    conn.close()
    print("✅ JAI 학습 시스템 테이블 초기화 완료")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🐦 트위터 학습 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TwitterLearner:
    """트위터에서 암호화폐 트렌드 학습"""
    
    def __init__(self):
        self.coin_keywords = {
            'BTC': ['비트코인', 'Bitcoin', 'BTC', '비트'],
            'ETH': ['이더리움', 'Ethereum', 'ETH', '이더'],
            'XRP': ['리플', 'Ripple', 'XRP'],
            'SOL': ['솔라나', 'Solana', 'SOL'],
            'ADA': ['에이다', 'Cardano', 'ADA'],
        }
        
        self.sentiment_keywords = {
            'positive': ['상승', '대박', '오른다', '매수', '좋다', '올라', '떡상', '🚀', '💎', '🔥'],
            'negative': ['하락', '손실', '위험', '매도', '나쁘다', '떨어', '물려', '😭', '💀', '📉'],
            'neutral': ['분석', '예상', '전망', '가능성', '관찰', '지켜', '🤔', '📊'],
        }
    
    def learn_from_text(self, text, source_id=None, engagement=0):
        """텍스트에서 패턴 학습"""
        # 감정 분석
        sentiment = self.analyze_sentiment(text)
        
        # 코인 언급 추출
        coins = self.extract_coins(text)
        
        # 키워드 추출
        keywords = self.extract_keywords(text)
        
        # 패턴 타입 분류
        pattern_type = self.classify_pattern(text)
        
        # 신뢰도 계산
        confidence = self.calculate_confidence(text, engagement)
        
        # DB 저장
        return self.save_pattern(
            source='twitter',
            source_id=source_id,
            content=text,
            sentiment=sentiment,
            keywords=keywords,
            coins=coins,
            engagement=engagement,
            confidence=confidence,
            pattern_type=pattern_type
        )
    
    def analyze_sentiment(self, text):
        """감정 분석"""
        scores = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[sentiment] += 1
        
        # 가장 높은 점수의 감정 반환
        max_sentiment = max(scores, key=scores.get)
        return max_sentiment if scores[max_sentiment] > 0 else 'neutral'
    
    def extract_coins(self, text):
        """언급된 코인 추출"""
        mentioned_coins = []
        
        for coin, keywords in self.coin_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    mentioned_coins.append(coin)
                    break
        
        return ', '.join(set(mentioned_coins))
    
    def extract_keywords(self, text):
        """중요 키워드 추출"""
        # 간단한 빈도 기반 추출
        words = re.findall(r'[가-힣]+', text)
        word_freq = Counter(words)
        
        # 상위 5개 키워드
        top_keywords = [word for word, count in word_freq.most_common(5)]
        return ', '.join(top_keywords)
    
    def classify_pattern(self, text):
        """패턴 타입 분류"""
        if any(word in text for word in ['매수', '사자', '진입']):
            return 'buy_signal'
        elif any(word in text for word in ['매도', '팔자', '청산']):
            return 'sell_signal'
        elif any(word in text for word in ['분석', '차트', '지표']):
            return 'technical_analysis'
        elif any(word in text for word in ['뉴스', '발표', '규제']):
            return 'news_event'
        else:
            return 'general_discussion'
    
    def calculate_confidence(self, text, engagement):
        """신뢰도 계산"""
        base_confidence = 0.5
        
        # 참여도 기반 보정
        engagement_boost = min(engagement / 1000, 0.3)
        
        # 명확한 신호 키워드 있으면 추가
        clear_signals = ['확실', '단언', '100%', '보장']
        if any(signal in text for signal in clear_signals):
            base_confidence += 0.2
        
        return min(base_confidence + engagement_boost, 1.0)
    
    def save_pattern(self, source, source_id, content, sentiment, keywords, coins, engagement, confidence, pattern_type):
        """학습 패턴 DB 저장"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learned_patterns 
                (source, source_id, content, sentiment, keywords, coins_mentioned, 
                 engagement_score, confidence_score, pattern_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (source, source_id, content, sentiment, keywords, coins, 
                  engagement, confidence, pattern_type))
            
            pattern_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"💜 학습 완료: {pattern_type} | {coins} | {sentiment} (신뢰도: {confidence:.2f})")
            return pattern_id
            
        except Exception as e:
            print(f"❌ 패턴 저장 실패: {e}")
            return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💬 텔레그램 학습 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TelegramLearner:
    """텔레그램 채널에서 학습"""
    
    def __init__(self):
        self.twitter_learner = TwitterLearner()  # 같은 분석 로직 재사용
    
    def learn_from_message(self, message, channel_name):
        """텔레그램 메시지에서 학습"""
        return self.twitter_learner.learn_from_text(
            text=message,
            source_id=f"{channel_name}_{datetime.now().timestamp()}",
            engagement=0  # 텔레그램은 좋아요 없음
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 트렌드 분석 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TrendAnalyzer:
    """학습한 데이터로 트렌드 분석"""
    
    def analyze_coin_trend(self, coin, timeframe='1h'):
        """특정 코인의 트렌드 분석"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 시간 범위 계산
            if timeframe == '1h':
                time_threshold = datetime.now() - timedelta(hours=1)
            elif timeframe == '24h':
                time_threshold = datetime.now() - timedelta(hours=24)
            elif timeframe == '7d':
                time_threshold = datetime.now() - timedelta(days=7)
            else:
                time_threshold = datetime.now() - timedelta(hours=1)
            
            # 해당 코인 언급 데이터 조회
            cursor.execute('''
                SELECT sentiment, engagement_score, confidence_score
                FROM learned_patterns
                WHERE coins_mentioned LIKE ?
                AND learned_at >= ?
            ''', (f'%{coin}%', time_threshold))
            
            rows = cursor.fetchall()
            
            if not rows:
                return None
            
            # 감정 점수 계산
            sentiment_scores = {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            
            total_engagement = 0
            total_confidence = 0
            
            for sentiment, engagement, confidence in rows:
                sentiment_scores[sentiment] += 1
                total_engagement += engagement
                total_confidence += confidence
            
            mention_count = len(rows)
            avg_engagement = total_engagement / mention_count
            avg_confidence = total_confidence / mention_count
            
            # 트렌드 방향 결정
            if sentiment_scores['positive'] > sentiment_scores['negative'] * 1.5:
                trend_direction = 'bullish'
            elif sentiment_scores['negative'] > sentiment_scores['positive'] * 1.5:
                trend_direction = 'bearish'
            else:
                trend_direction = 'neutral'
            
            # 감정 점수 (positive 비율)
            sentiment_score = sentiment_scores['positive'] / mention_count
            
            # 결과 저장
            cursor.execute('''
                INSERT INTO trend_analysis
                (coin, timeframe, sentiment_score, mention_count, avg_engagement, 
                 trend_direction, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (coin, timeframe, sentiment_score, mention_count, avg_engagement,
                  trend_direction, avg_confidence))
            
            conn.commit()
            conn.close()
            
            result = {
                'coin': coin,
                'timeframe': timeframe,
                'sentiment_score': sentiment_score,
                'mention_count': mention_count,
                'trend_direction': trend_direction,
                'confidence': avg_confidence,
                'sentiment_breakdown': sentiment_scores
            }
            
            print(f"📊 {coin} 트렌드 분석 완료: {trend_direction} (신뢰도: {avg_confidence:.2f})")
            return result
            
        except Exception as e:
            print(f"❌ 트렌드 분석 실패: {e}")
            return None
    
    def get_trending_coins(self, top_n=5):
        """현재 가장 핫한 코인들"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 최근 1시간 데이터
            time_threshold = datetime.now() - timedelta(hours=1)
            
            cursor.execute('''
                SELECT coins_mentioned, COUNT(*) as mentions, AVG(confidence_score) as avg_conf
                FROM learned_patterns
                WHERE learned_at >= ?
                AND coins_mentioned != ''
                GROUP BY coins_mentioned
                ORDER BY mentions DESC, avg_conf DESC
                LIMIT ?
            ''', (time_threshold, top_n))
            
            rows = cursor.fetchall()
            conn.close()
            
            trending = []
            for coins, mentions, confidence in rows:
                trending.append({
                    'coins': coins,
                    'mentions': mentions,
                    'confidence': confidence
                })
            
            return trending
            
        except Exception as e:
            print(f"❌ 트렌딩 코인 조회 실패: {e}")
            return []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 AI 시뮬레이션 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AISimulator:
    """가상 AI 에이전트들과 토론"""
    
    def __init__(self):
        self.agents = {
            '보수적_투자자': {
                'personality': 'risk_averse',
                'bias': 'negative',
                'focus': 'safety'
            },
            '공격적_투자자': {
                'personality': 'aggressive',
                'bias': 'positive',
                'focus': 'profit'
            },
            '기술분석가': {
                'personality': 'technical',
                'bias': 'neutral',
                'focus': 'charts'
            },
            '뉴스분석가': {
                'personality': 'fundamental',
                'bias': 'neutral',
                'focus': 'news'
            }
        }
    
    def simulate_discussion(self, topic, context):
        """AI들끼리 토론 시뮬레이션"""
        discussion = []
        
        for agent_name, agent_config in self.agents.items():
            opinion = self.generate_opinion(agent_name, agent_config, topic, context)
            discussion.append({
                'agent': agent_name,
                'opinion': opinion
            })
        
        # 합의 도출
        consensus = self.synthesize_consensus(discussion, context)
        
        # 결과 저장
        self.save_simulation(topic, discussion, consensus)
        
        return consensus
    
    def generate_opinion(self, agent_name, config, topic, context):
        """에이전트별 의견 생성"""
        # 간단한 규칙 기반 의견 (실제로는 GPT API 사용 가능)
        
        if config['personality'] == 'risk_averse':
            if context.get('trend_direction') == 'bullish':
                return f"상승 추세지만, 조정 가능성을 고려해야 합니다. 분할 매수 추천."
            else:
                return f"현재 시장은 불확실합니다. 관망 추천."
        
        elif config['personality'] == 'aggressive':
            if context.get('trend_direction') == 'bullish':
                return f"강한 상승 모멘텀! 지금 바로 진입하세요!"
            else:
                return f"단기 조정은 매수 기회입니다. 공격적 진입!"
        
        elif config['personality'] == 'technical':
            return f"RSI {context.get('rsi', 50)}, 이평선 배열 {context.get('ma_alignment', 'neutral')}"
        
        else:  # fundamental
            return f"뉴스 심리 {context.get('sentiment_score', 0.5)}, 거래량 증가 {context.get('volume_spike', False)}"
    
    def synthesize_consensus(self, discussion, context):
        """토론 결과 종합"""
        # 각 의견의 강도 분석
        bullish_count = sum(1 for d in discussion if '진입' in d['opinion'] or '매수' in d['opinion'])
        bearish_count = sum(1 for d in discussion if '관망' in d['opinion'] or '매도' in d['opinion'])
        
        if bullish_count > bearish_count:
            action = 'buy'
            confidence = bullish_count / len(discussion)
        elif bearish_count > bullish_count:
            action = 'wait'
            confidence = bearish_count / len(discussion)
        else:
            action = 'neutral'
            confidence = 0.5
        
        return {
            'action': action,
            'confidence': confidence,
            'reasoning': f"{bullish_count}명 긍정, {bearish_count}명 부정"
        }
    
    def save_simulation(self, topic, discussion, consensus):
        """시뮬레이션 결과 저장"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_simulations
                (topic, participants, discussion, consensus, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                topic,
                ', '.join(self.agents.keys()),
                json.dumps(discussion, ensure_ascii=False),
                json.dumps(consensus, ensure_ascii=False),
                consensus['confidence']
            ))
            
            conn.commit()
            conn.close()
            
            print(f"🤖 AI 시뮬레이션 완료: {topic} → {consensus['action']} (신뢰도: {consensus['confidence']:.2f})")
            
        except Exception as e:
            print(f"❌ 시뮬레이션 저장 실패: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 테스트 & 데모
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    # 테이블 초기화
    init_learning_tables()
    
    # 트위터 학습 테스트
    print("\n" + "="*60)
    print("🐦 트위터 학습 테스트")
    print("="*60)
    
    twitter_learner = TwitterLearner()
    
    test_tweets = [
        ("비트코인 지금 매수 타이밍! 떡상 예상 🚀", 150),
        ("이더리움 하락 조심하세요. 손절 고려해야...", 80),
        ("리플 차트 분석 결과 상승 추세 확인", 200),
    ]
    
    for tweet, engagement in test_tweets:
        twitter_learner.learn_from_text(tweet, engagement=engagement)
    
    # 트렌드 분석 테스트
    print("\n" + "="*60)
    print("📊 트렌드 분석 테스트")
    print("="*60)
    
    analyzer = TrendAnalyzer()
    
    for coin in ['BTC', 'ETH', 'XRP']:
        trend = analyzer.analyze_coin_trend(coin, '1h')
        if trend:
            print(f"\n{coin}:")
            print(f"  방향: {trend['trend_direction']}")
            print(f"  언급: {trend['mention_count']}회")
            print(f"  신뢰도: {trend['confidence']:.2%}")
    
    # 트렌딩 코인
    print("\n" + "="*60)
    print("🔥 현재 트렌딩 코인")
    print("="*60)
    
    trending = analyzer.get_trending_coins(top_n=3)
    for rank, item in enumerate(trending, 1):
        print(f"{rank}. {item['coins']}: {item['mentions']}회 언급 (신뢰도: {item['confidence']:.2f})")
    
    # AI 시뮬레이션 테스트
    print("\n" + "="*60)
    print("🤖 AI 시뮬레이션 테스트")
    print("="*60)
    
    simulator = AISimulator()
    
    context = {
        'trend_direction': 'bullish',
        'sentiment_score': 0.7,
        'rsi': 65,
        'volume_spike': True
    }
    
    consensus = simulator.simulate_discussion("BTC 매수 여부", context)
    print(f"\n최종 결론: {consensus['action']} (신뢰도: {consensus['confidence']:.2%})")
    print(f"근거: {consensus['reasoning']}")
