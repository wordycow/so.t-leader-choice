# 🎨 THE UNIQUE 브랜드 DNA - 디자인 학습 데이터베이스

## 📅 생성일: 2026-02-15
## 🎯 목적: THE UNIQUE 브랜드의 시각적 정체성을 지속적으로 학습하고 발전시킴

---

## 1️⃣ **핵심 브랜드 정체성**

### **브랜드 키워드**
- 🏆 **프리미엄 (Premium)**: 고급스러움, 럭셔리
- ✨ **미스틱 (Mystic)**: 신비로움, 마법적, 영적
- 🌌 **우주적 (Cosmic)**: 광활함, 깊이감, 무한
- 💎 **고전+현대 융합 (Classic+Modern)**: 전통과 혁신의 조화

### **감정/분위기 (Mood)**
- 경외감 (Awe)
- 신비로움 (Mystery)
- 고요함 (Serenity)
- 권위 (Authority)
- 영성 (Spirituality)

---

## 2️⃣ **컬러 팔레트 (Color Palette)**

### **Primary Colors (메인 컬러)**
```css
/* 골드 계열 - 럭셔리, 프리미엄 */
--gold: #fbbf24;           /* 메인 골드 */
--gold-light: #fde68a;     /* 라이트 골드 */
--gold-dark: #f59e0b;      /* 다크 골드 */
--gold-accent: #FACC15;    /* 액센트 골드 */

/* 퍼플 계열 - 신비, 마법 */
--purple: #9333ea;         /* 메인 퍼플 */
--purple-light: #c084fc;   /* 라이트 퍼플 */
--purple-dark: #581c87;    /* 다크 퍼플 */
--purple-deep: #1a0f2e;    /* 딥 퍼플 */

/* 배경 계열 - 깊이감, 우주적 */
--bg-dark: #0a0515;        /* 최고 어두운 배경 */
--bg-purple: #1a0f2e;      /* 퍼플 배경 */
--bg-card: #1e2848;        /* 카드 배경 */
```

### **Secondary Colors (보조 컬러)**
```css
/* 블루 계열 - 신뢰, 전문성 */
--blue-deep: #0B1120;
--blue-slate: #334155;

/* 레드 계열 - 전통, 사주용 */
--red: #c41e3a;
--red-soft: #ff0055;

/* 화이트/그레이 - 텍스트, 구분 */
--text-light: #f9fafb;
--text-muted: #d1d5db;
--text-gray: #94a3b8;
```

---

## 3️⃣ **타이포그래피 (Typography)**

### **영문 폰트**
- **Cinzel**: 고급스러운 세리프, 타이틀용
  - Weight: 400 (Regular), 600 (SemiBold), 700 (Bold), 900 (Black)
  - 용도: 메인 타이틀, 브랜드명, 헤딩

### **한글 폰트**
- **Noto Serif KR**: 우아한 세리프, 본문용
  - Weight: 400, 600, 700
  - 용도: 본문, 설명, 결과 텍스트
  
- **Nanum Myeongjo**: 전통적인 명조, 사주용
  - Weight: 400, 700, 800
  - 용도: 사주팔자, 한자, 전통 콘텐츠

- **Pretendard**: 모던한 고딕, UI용
  - 용도: 버튼, 레이블, 시스템 텍스트

---

## 4️⃣ **디자인 패턴 (Design Patterns)**

### **그라데이션 스타일**
1. **다층 그라데이션** (Multi-layer Gradient)
   ```css
   background: linear-gradient(135deg, 
     rgba(10,5,21,0.95) 0%, 
     rgba(26,15,46,0.92) 25%,
     rgba(88,28,135,0.90) 50%,
     rgba(147,51,234,0.85) 75%,
     rgba(192,132,252,0.80) 100%
   );
   ```

2. **Radial 글로우** (Radial Glow)
   ```css
   background: 
     radial-gradient(circle at 20% 20%, rgba(251,191,36,0.15) 0%, transparent 40%),
     radial-gradient(circle at 80% 80%, rgba(147,51,234,0.20) 0%, transparent 50%);
   ```

3. **텍스트 그라데이션** (Text Gradient)
   ```css
   background: linear-gradient(135deg, #fbbf24 0%, #c084fc 50%, #fbbf24 100%);
   -webkit-background-clip: text;
   -webkit-text-fill-color: transparent;
   ```

### **애니메이션 스타일**
1. **Float** (부유)
   - Duration: 3-10초
   - Easing: ease-in-out
   - Movement: translateY(-5px ~ -10px)

2. **Glow Pulse** (빛 펄스)
   - Duration: 2-4초
   - Opacity: 0.6 ~ 1.0
   - Shadow spread: 동적 변화

3. **Gradient Flow** (그라데이션 흐름)
   - Duration: 4-5초
   - Background-position: 0% → 200%
   - Infinite loop

4. **3D Lift** (3D 들어올림)
   - Transform: translateY(-8px) scale(1.03)
   - Transition: cubic-bezier(0.175, 0.885, 0.32, 1.275)

---

## 5️⃣ **시각 효과 (Visual Effects)**

### **Glassmorphism** (유리 효과)
```css
background: rgba(26,15,46,0.85);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
border: 2px solid rgba(255,255,255,0.1);
```

### **박스 섀도우** (Box Shadow)
```css
/* 다층 그림자 */
box-shadow: 
  0 30px 80px rgba(0,0,0,0.9),        /* 깊이 */
  0 0 80px rgba(147,51,234,0.3),       /* 글로우 */
  inset 0 1px 0 rgba(255,255,255,0.1); /* 하이라이트 */
```

### **텍스트 섀도우** (Text Shadow)
```css
/* 다중 섀도우 */
filter: 
  drop-shadow(0 0 20px rgba(251,191,36,0.4))
  drop-shadow(0 0 40px rgba(147,51,234,0.3));
```

---

## 6️⃣ **컴포넌트 스타일 가이드**

### **카드 (Card)**
- Border-radius: 20-32px (부드러운 곡선)
- Padding: 30-50px
- Border: 2-3px 그라데이션
- Background: 반투명 + 블러
- Hover: translateY(-8px) + scale(1.03)

### **버튼 (Button)**
- Border-radius: 12-16px
- Padding: 14-18px
- Font-weight: 700-900
- Transition: 0.3-0.4s
- Active: scale(0.98)

### **입력 필드 (Input)**
- Border-radius: 10-12px
- Border: 1-2px solid
- Focus: border-color + box-shadow glow
- Background: 어두운 배경 (#0f172a)

---

## 7️⃣ **페이지별 특성**

### **타로 카드 (Tarot)**
- **컬러**: 퍼플 중심, 골드 액센트
- **분위기**: 우주적, 신비로움
- **효과**: 많은 애니메이션, 화려함
- **패턴**: 별, 우주, 마법진

### **사주팔자 (Saju)**
- **컬러**: 골드+레드 중심, 전통적
- **분위기**: 고요함, 권위
- **효과**: 절제된 애니메이션, 우아함
- **패턴**: 한지, 먹, 오행

### **슬랭 사전 (Slang)**
- **컬러**: 밝은 그라데이션, 네온
- **분위기**: 활기찬, 현대적
- **효과**: 경쾌한 애니메이션
- **패턴**: 깔끔함, Glassmorphism

---

## 8️⃣ **학습 데이터 로그**

### **2026-02-15 - 초기 분석**
- ✅ 기존 페이지 분석 완료
- ✅ 컬러 팔레트 추출
- ✅ 타이포그래피 시스템 정리
- ✅ 타로 카드 페이지 리디자인 완료

### **타로 카드 v2.0 개선사항**
- 5단계 그라데이션 배경
- 7색 타이틀 그라데이션 + 흐름 애니메이션
- Glassmorphism 카드
- 그라데이션 테두리 애니메이션
- 3D Float 효과
- SVG 별 패턴

### **2026-02-15 21:50 - 사주팔자 리서치**
- ✅ 한국 전통 디자인 이미지 리서치 완료
- ✅ 오행 (五行) 시각 자료 수집
- ✅ 한지/먹 텍스처 스타일 분석
- ✅ 사주 배경 이미지 생성 (한지 + 금박 + 붉은색)
- 🔄 사주팔자 페이지 리디자인 시작

### **사주팔자 디자인 컨셉**
- **컬러**: 골드 (#d4af37) + 레드 (#c41e3a) + 베이지 (#f9f5e8)
- **텍스처**: 한지 종이, 먹 번짐 효과
- **패턴**: 구름, 산, 한자
- **분위기**: 고요함, 권위, 전통+현대 융합
- **폰트**: Nanum Myeongjo (명조체)
- **효과**: 절제된 애니메이션, 우아한 전환

### **다음 학습 목표**
- [x] 사주팔자 전통 이미지 리서치
- [x] 한지/먹 텍스처 스타일 개발
- [x] 오행 컬러 시스템 구축
- [ ] 사주팔자 페이지 완성
- [ ] 슬랭 사전 네온 스타일 연구

---

## 9️⃣ **디자인 원칙 (Design Principles)**

### **DO's** ✅
1. **대비 사용**: 골드 vs 퍼플, 밝음 vs 어두움
2. **부드러운 곡선**: border-radius 16px 이상
3. **다층 효과**: 그림자, 그라데이션 중첩
4. **애니메이션**: 모든 인터랙션에 부드러운 전환
5. **공간감**: 충분한 padding과 margin
6. **계층 구조**: z-index, 그림자로 깊이 표현

### **DON'T's** ❌
1. ❌ 각진 모서리 (border-radius: 0)
2. ❌ 단색 배경 (항상 그라데이션 사용)
3. ❌ 갑작스러운 전환 (transition 필수)
4. ❌ 회색 텍스트만 사용 (골드/퍼플 액센트 추가)
5. ❌ 평평한 디자인 (그림자로 깊이감 필수)

---

## 🔟 **기술 스펙 (Technical Specs)**

### **성능 최적화**
- GPU 가속: `transform`, `opacity` 사용
- Will-change: 애니메이션 요소에 적용
- 60FPS 목표: 부드러운 애니메이션
- 경량화: CSS만 사용, 불필요한 이미지 제거

### **반응형**
- Mobile: 360px+
- Tablet: 768px+
- Desktop: 1024px+
- Max-width: 1100-1200px

### **브라우저 지원**
- Chrome/Edge: 최신 3버전
- Firefox: 최신 3버전
- Safari: 최신 2버전
- 모바일: iOS 14+, Android 9+

---

## 📝 **업데이트 로그**

### v1.0 - 2026-02-15 21:50
- 초기 브랜드 DNA 문서 생성
- 타로 카드 v2.0 디자인 완료
- 컬러 팔레트 정의
- 타이포그래피 시스템 구축
- 디자인 패턴 정리

---

**이 문서는 계속 업데이트됩니다.** 🔄
**모든 디자인 결정은 이 DNA를 기반으로 합니다.** 🎨
