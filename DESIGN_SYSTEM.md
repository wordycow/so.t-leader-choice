# 🎨 THE UNIQUE 디자인 시스템 - 완벽한 통일성과 독창성

## 📅 생성일: 2026-02-15
## 🎯 목적: 모든 UI 요소의 통일성, 독창성, 명분을 갖춘 디자인 시스템 구축

---

## 🎯 **디자인 철학**

```
통일성 (Consistency) + 독창성 (Uniqueness) = 명분 (Purpose)
```

### **핵심 원칙**
1. **모든 버튼은 이유가 있다** (Purpose-driven Design)
2. **색상은 의미를 전달한다** (Color Psychology)
3. **크기는 중요도를 나타낸다** (Visual Hierarchy)
4. **애니메이션은 피드백을 준다** (Interactive Feedback)

---

## 🎨 **컬러 시스템**

### **Primary Colors (주 색상)**

#### **타로 카드 테마**
```css
/* 신비로움 - 퍼플 계열 */
--tarot-primary: #9333ea;      /* 메인 퍼플 */
--tarot-light: #c084fc;        /* 라이트 퍼플 */
--tarot-dark: #581c87;         /* 다크 퍼플 */

/* 프리미엄 - 골드 계열 */
--tarot-gold: #fbbf24;         /* 메인 골드 */
--tarot-gold-light: #fde68a;   /* 라이트 골드 */

/* 용도별 */
--tarot-accent: #c084fc;       /* 강조 */
--tarot-success: #10b981;      /* 성공 */
--tarot-warning: #f59e0b;      /* 경고 */
--tarot-danger: #ef4444;       /* 위험 */
```

#### **사주팔자 테마**
```css
/* 전통 - 골드 계열 */
--saju-primary: #d4af37;       /* 메인 골드 */
--saju-light: #f0d98c;         /* 라이트 골드 */

/* 권위 - 레드 계열 */
--saju-accent: #c41e3a;        /* 메인 레드 */
--saju-red-light: #e63946;     /* 라이트 레드 */

/* 배경 - 베이지 계열 */
--saju-bg: #f9f5e8;            /* 한지 베이지 */
--saju-bg-dark: #6b4423;       /* 다크 브라운 */
```

#### **슬랭 사전 테마**
```css
/* 트렌디 - 네온 계열 */
--slang-cyan: #06b6d4;         /* 시안 */
--slang-pink: #ec4899;         /* 핑크 */
--slang-yellow: #facc15;       /* 옐로우 */
--slang-purple: #a855f7;       /* 퍼플 */

/* 배경 */
--slang-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### **Semantic Colors (의미 색상)**

```css
/* 상태 */
--success: #10b981;    /* 성공 - 녹색 */
--warning: #f59e0b;    /* 경고 - 주황 */
--error: #ef4444;      /* 에러 - 빨강 */
--info: #3b82f6;       /* 정보 - 파랑 */

/* 텍스트 */
--text-primary: #111827;    /* 주 텍스트 */
--text-secondary: #6b7280;  /* 보조 텍스트 */
--text-disabled: #d1d5db;   /* 비활성 */
--text-inverse: #ffffff;    /* 반전 (어두운 배경용) */
```

---

## 🔘 **버튼 시스템**

### **버튼 종류 및 용도**

#### **1. Primary Button (주 버튼)**
- **용도**: 핵심 액션 (카드 뽑기, 사주 보기, 검색)
- **색상**: 테마 Primary 색상
- **크기**: 48px 이상
- **위치**: 화면 중앙 하단

```css
.btn-primary {
  background: linear-gradient(135deg, 
    var(--primary) 0%, 
    var(--primary-dark) 100%
  );
  color: white;
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 700;
  border: none;
  box-shadow: 
    0 8px 24px rgba(0,0,0,0.3),
    0 0 20px var(--primary-glow);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.btn-primary:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 
    0 12px 32px rgba(0,0,0,0.4),
    0 0 40px var(--primary-glow);
}

.btn-primary:active {
  transform: translateY(-2px) scale(1.02);
}
```

#### **2. Secondary Button (보조 버튼)**
- **용도**: 부가 액션 (뒤로가기, 취소)
- **색상**: 테마 Secondary 색상
- **크기**: 40px
- **위치**: Primary 버튼 옆

```css
.btn-secondary {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  color: var(--text-inverse);
  border: 2px solid rgba(255,255,255,0.3);
  /* ... */
}
```

#### **3. Icon Button (아이콘 버튼)**
- **용도**: 설정, 닫기, 정보
- **크기**: 40×40px
- **위치**: 화면 모서리

```css
.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* ... */
}
```

### **버튼 상태 (States)**

```css
/* 기본 상태 */
.btn { opacity: 1; cursor: pointer; }

/* Hover 상태 */
.btn:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

/* Active 상태 (클릭 중) */
.btn:active { 
  transform: translateY(0px) scale(0.98); 
}

/* Disabled 상태 */
.btn:disabled { 
  opacity: 0.5; 
  cursor: not-allowed; 
  filter: grayscale(1);
}

/* Loading 상태 */
.btn.loading::after {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
```

---

## 📐 **간격 시스템 (Spacing)**

### **기본 단위: 4px**

```css
/* 간격 변수 */
--spacing-xs: 4px;    /* 0.25rem */
--spacing-sm: 8px;    /* 0.5rem */
--spacing-md: 16px;   /* 1rem */
--spacing-lg: 24px;   /* 1.5rem */
--spacing-xl: 32px;   /* 2rem */
--spacing-2xl: 48px;  /* 3rem */
--spacing-3xl: 64px;  /* 4rem */
```

### **사용 규칙**
- 요소 내부 패딩: `md` (16px)
- 요소 간 간격: `lg` (24px)
- 섹션 간 간격: `2xl` (48px)
- 페이지 여백: `xl` ~ `2xl`

---

## 🎯 **타이포그래피 시스템**

### **폰트 스케일**

```css
/* 크기 체계 (1.25배 비율) */
--text-xs: 12px;      /* 캡션, 라벨 */
--text-sm: 14px;      /* 보조 텍스트 */
--text-base: 16px;    /* 본문 */
--text-lg: 20px;      /* 강조 텍스트 */
--text-xl: 24px;      /* 소제목 */
--text-2xl: 32px;     /* 제목 */
--text-3xl: 40px;     /* 대제목 */
--text-4xl: 48px;     /* 페이지 타이틀 */
--text-5xl: 64px;     /* 히어로 타이틀 */
```

### **폰트 무게**

```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
--font-black: 900;
```

### **사용 규칙**
- **타이틀**: `3xl` ~ `5xl`, `bold` ~ `black`
- **본문**: `base`, `normal` ~ `medium`
- **캡션**: `xs` ~ `sm`, `normal`

---

## 🎭 **애니메이션 시스템**

### **타이밍 함수**

```css
/* 기본 */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* 바운스 */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* 부드러운 시작 */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* 빠른 종료 */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
```

### **지속 시간**

```css
--duration-instant: 0.1s;   /* 즉각 반응 */
--duration-fast: 0.2s;      /* 빠른 전환 */
--duration-normal: 0.3s;    /* 일반 전환 */
--duration-slow: 0.5s;      /* 느린 전환 */
--duration-slower: 0.8s;    /* 매우 느린 전환 */
```

### **표준 애니메이션**

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(30px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

/* Scale In */
@keyframes scaleIn {
  from { 
    opacity: 0; 
    transform: scale(0.9); 
  }
  to { 
    opacity: 1; 
    transform: scale(1); 
  }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

---

## 🎯 **통일성 체크리스트**

### **모든 버튼은...**
- [ ] 48px 이상의 터치 영역을 가지는가?
- [ ] Hover 시 시각적 피드백이 있는가?
- [ ] Active 시 눌리는 느낌이 있는가?
- [ ] Disabled 상태가 명확한가?
- [ ] 라벨이 명확한가? (동사 사용)

### **모든 색상은...**
- [ ] 의미가 있는가? (Primary, Secondary, Accent)
- [ ] 충분한 대비를 가지는가? (WCAG AA 이상)
- [ ] 테마와 일치하는가?
- [ ] 색맹 사용자도 구분 가능한가?

### **모든 텍스트는...**
- [ ] 읽기 쉬운가? (최소 16px)
- [ ] 계층 구조가 명확한가?
- [ ] 라인 높이가 적절한가? (1.5 ~ 1.8)
- [ ] 자간이 적절한가?

---

## 📝 **컴포넌트 라이브러리**

### **공통 컴포넌트**

```html
<!-- Primary Button -->
<button class="btn btn-primary">
  <span class="btn-icon">✨</span>
  <span class="btn-text">카드 뽑기</span>
</button>

<!-- Card Component -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">타로 리딩</h3>
  </div>
  <div class="card-body">
    <!-- 내용 -->
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">시작하기</button>
  </div>
</div>

<!-- Input Component -->
<div class="input-group">
  <label class="input-label">질문을 입력하세요</label>
  <input 
    type="text" 
    class="input-field" 
    placeholder="예: 오늘의 운세는?"
  >
  <span class="input-helper">선택사항입니다</span>
</div>
```

---

## 🎯 **독창성 포인트**

### **THE UNIQUE만의 특징**

1. **그라데이션 테두리 애니메이션**
   - 모든 주요 카드에 흐르는 그라데이션 테두리
   - 4초 무한 루프

2. **Glassmorphism + 전통**
   - 유리 효과 + 한지 텍스처 결합
   - 서양 + 동양 융합

3. **다층 박스섀도우**
   - 깊이감을 주는 3중 그림자
   - 골드 + 퍼플 글로우

4. **의미 있는 애니메이션**
   - 카드 뒤집기: 운명의 변화
   - Float: 우주에 떠 있는 느낌
   - Pulse: 생명력, 에너지

---

## 📊 **품질 검증**

### **출시 전 체크리스트**

#### **통일성**
- [ ] 모든 페이지가 같은 컬러 시스템을 사용하는가?
- [ ] 버튼 스타일이 일관되는가?
- [ ] 간격이 체계적인가? (4px 단위)
- [ ] 타이포그래피가 일관되는가?

#### **독창성**
- [ ] 다른 사이트와 차별화되는가?
- [ ] THE UNIQUE만의 시그니처가 있는가?
- [ ] 기억에 남는 디자인인가?

#### **명분 (Purpose)**
- [ ] 모든 디자인 결정에 이유가 있는가?
- [ ] 사용자 경험을 향상시키는가?
- [ ] 브랜드 가치를 전달하는가?

---

## 📝 **업데이트 로그**

### v1.0 - 2026-02-15
- 디자인 시스템 초안 작성
- 컬러 시스템 정의
- 버튼 시스템 구축
- 타이포그래피 체계 수립
- 애니메이션 표준 정의

---

**💎 목표: 경외감을 주는 통일되고 독창적인 디자인 시스템**
**🎯 모든 픽셀에 의미와 목적이 있다**
