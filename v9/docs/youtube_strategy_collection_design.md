# YouTube 전략 자동 수집 시스템 설계

## 목표
- 유튜브에서 트레이딩 기법/매매기법 영상을 자동으로 검색
- 자막/스크립트 추출 및 요약
- 전략 라이브러리에 자동 축적
- IMEI가 전략 설명 및 활용 가능

---

## 데이터 파이프라인

```
[YouTube Search]
      ↓
[Video Metadata + Captions]
      ↓
[Text Summarization (LLM)]
      ↓
[Strategy Extraction]
      ↓
[Strategy Library DB]
      ↓
[IMEI Integration]
```

---

## 주요 컴포넌트

### 1. YouTube Searcher
- **기능**: 키워드로 영상 검색
- **API**: YouTube Data API v3
- **검색 키워드**:
  - "upbit 매매기법"
  - "암호화폐 scalping strategy"
  - "비트코인 트레이딩 전략"
  - "알트코인 매수 타이밍"
- **필터링**:
  - 조회수 > 1,000
  - 업로드 기간: 최근 6개월
  - 영상 길이: 5~30분

### 2. Caption Extractor
- **기능**: 영상 자막 추출
- **방법**:
  - Option A: youtube_transcript_api (자막 직접 추출)
  - Option B: yt-dlp (자막 파일 다운로드)
- **언어**: 한국어 우선, 영어 fallback

### 3. Summarizer (LLM)
- **기능**: 긴 자막을 요약
- **모델**: Ollama (qwen2.5:7b) 또는 GPT-4o-mini
- **프롬프트 템플릿**:
```
다음은 트레이딩 유튜브 영상의 자막입니다.
핵심 매매 전략과 기법을 아래 항목으로 요약하세요:

1. 전략 이름
2. 진입 조건
3. 청산 조건
4. 리스크 관리
5. 적용 시장 (비트코인/알트코인)
6. 타임프레임

자막:
{transcript}
```

### 4. Strategy Extractor
- **기능**: 요약에서 구조화된 전략 정보 추출
- **출력 포맷** (JSON):
```json
{
  "strategy_name": "볼린저 밴드 브레이크아웃",
  "source": "youtube",
  "youtube_url": "https://youtube.com/...",
  "channel_name": "코인트레이더TV",
  "video_title": "하루 10% 수익률 매매 기법",
  "summary": "...",
  "entry_conditions": [
    "볼린저 밴드 하단 터치",
    "RSI < 30",
    "거래량 급증"
  ],
  "exit_conditions": [
    "볼린저 밴드 중심선 돌파",
    "2% 익절 또는 1% 손절"
  ],
  "risk_management": "1회 매매당 총 자산의 5% 이하",
  "applicable_markets": ["BTC", "ETH", "altcoins"],
  "timeframe": "15m, 1h",
  "quality_score": 0.85,
  "tags": ["scalping", "bollinger", "RSI"],
  "created_at": "2026-02-18T23:59:00",
  "use_count": 0
}
```

### 5. Strategy Library DB
- **저장소**: `runtime/youtube_strategies.json` (JSON) 또는 SQLite
- **테이블 스키마** (SQLite):
```sql
CREATE TABLE youtube_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_name TEXT NOT NULL,
    youtube_url TEXT UNIQUE NOT NULL,
    channel_name TEXT,
    video_title TEXT,
    summary TEXT,
    entry_conditions TEXT,  -- JSON array
    exit_conditions TEXT,   -- JSON array
    risk_management TEXT,
    applicable_markets TEXT,  -- JSON array
    timeframe TEXT,
    quality_score REAL DEFAULT 0.8,
    tags TEXT,  -- JSON array
    use_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);
```

### 6. IMEI Integration
- **명령어**:
  - "유튜브에서 배운 전략 보여줘"
  - "볼린저 밴드 전략 알려줘"
  - "최근 수집된 기법은?"
- **응답 예시**:
```
📚 유튜브에서 수집한 전략 3개:

1. **볼린저 밴드 브레이크아웃** (코인트레이더TV)
   - 진입: BB 하단 + RSI<30 + 거래량 급증
   - 청산: BB 중심선 돌파 또는 2% 익절
   - 타임프레임: 15m, 1h
   - [영상 보기](https://youtube.com/...)

2. **추세 추종 이동평균선 골든크로스** (BTC매니아)
   - 진입: MA5 > MA20 + 거래량 증가
   - ...

더 자세한 내용은 영상을 참고하세요!
```

---

## 스케줄러 구조

### 주기적 수집 (Cron / APScheduler)
- **수집 주기**: 매일 1회 (새벽 3시)
- **수집량**: 최대 10개 영상/일
- **중복 제거**: URL 기반 체크
- **품질 필터링**:
  - 전략 명확성 > 0.7 (LLM 판단)
  - 실행 가능성 있는 전략만 저장

### 수동 수집
- **명령어**: "유튜브에서 'scalping strategy' 검색해서 수집해줘"
- **즉시 실행**: 검색 → 자막 추출 → 요약 → 저장

---

## 구현 단계

### Phase 1: 기본 파이프라인 (1주)
- ✅ YouTube Search API 연동
- ✅ Caption 추출 (youtube_transcript_api)
- ✅ Ollama 요약 (qwen2.5:7b)
- ✅ JSON 저장 (runtime/youtube_strategies.json)

### Phase 2: 품질 향상 (1주)
- LLM 프롬프트 최적화
- 전략 구조화 강화
- 중복 제거 로직
- 품질 스코어 자동 평가

### Phase 3: IMEI 통합 (3일)
- 전략 검색 명령어
- 자연어 응답 생성
- 영상 링크 표시

### Phase 4: 자동화 (2일)
- APScheduler 스케줄러
- 매일 자동 수집
- 로그 및 모니터링

---

## 파일 구조

```
v9/
├── youtube_collector/
│   ├── __init__.py
│   ├── searcher.py          # YouTube 검색
│   ├── caption_extractor.py # 자막 추출
│   ├── summarizer.py         # LLM 요약
│   ├── strategy_extractor.py# 전략 추출
│   └── scheduler.py          # 스케줄러
├── runtime/
│   ├── youtube_strategies.json  # 전략 DB (JSON)
│   └── youtube_strategies.db    # 전략 DB (SQLite, optional)
└── docs/
    └── youtube_strategy_collection_design.md  # 본 문서
```

---

## 필요한 라이브러리

```bash
pip install youtube-transcript-api
pip install google-api-python-client  # YouTube Data API
pip install apscheduler
pip install yt-dlp  # Optional: fallback
```

---

## 보안 및 제한사항

### YouTube API Quota
- **일일 할당량**: 10,000 units
- **검색 비용**: 100 units/request
- **권장**: 최대 50~100회 검색/일

### 저작권
- 자막은 요약 및 분석 목적으로만 사용
- 원본 영상 URL 항상 출처 표시
- 상업적 재배포 금지

### 데이터 품질
- 자막 없는 영상 제외
- 노이즈 많은 자막 필터링
- LLM 환각(hallucination) 검증

---

## 성공 지표

- **수집 전략 수**: 주당 30~50개
- **품질 스코어 평균**: > 0.7
- **IMEI 활용도**: 주당 10회 이상 전략 검색
- **사용자 피드백**: "유용함" 70% 이상

---

## 다음 단계

1. ✅ 설계 문서 작성 (본 문서)
2. YouTube Search API 키 발급
3. 프로토타입 구현 (searcher + caption + summarizer)
4. 10개 영상 테스트
5. 품질 평가 및 프롬프트 튜닝
6. IMEI 통합
7. 스케줄러 배포

---

**작성일**: 2026-02-18  
**버전**: v1.0  
**담당**: IMEI Development Team
