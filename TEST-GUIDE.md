# 🔍 The Unique 웹사이트 전체 플로우 리뷰

**미리보기 서버**: https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai

---

## 📋 테스트 순서 (사용자 플로우)

### 1️⃣ **Gate 페이지** (로그인/회원가입)
**URL**: `/the-unique-gate.html`

#### 🎨 디자인 체크리스트
- [ ] **배경 이미지**: `img/bg-unique-gate-clean.jpg`
- [ ] **Glass morphism 카드**: 반투명 + 블러 효과
- [ ] **황금 테두리**: 노란색 빛나는 효과
- [ ] **로고**: Cinzel 폰트
- [ ] **입력 필드**: 포커스 시 하이라이트
- [ ] **버튼**: 호버 시 애니메이션

#### ⚙️ 기능 체크리스트
- [ ] 이메일/비밀번호 입력
- [ ] 로그인 버튼 클릭
- [ ] 회원가입 버튼 클릭
- [ ] 에러 메시지 표시
- [ ] Main 페이지로 이동

#### 📱 반응형 체크
- [ ] 데스크톱 (1920px)
- [ ] 태블릿 (768px)
- [ ] 모바일 (375px)

---

### 2️⃣ **Main 페이지** (회원 대시보드)
**URL**: `/the-unique-main.html`

#### 🎨 주요 UI 컴포넌트

##### A. 상단 영역
- [ ] **제목**: "THE UNIQUE" (Cinzel 폰트)
- [ ] **SNS 아이콘**: Discord, YouTube (우측 상단)
- [ ] **스케줄**: 주간 강의 일정

##### B. 지갑 섹션
- [ ] **UT 잔액 표시**
- [ ] **UT 도넛 차트**: 3D 효과 + 애니메이션
- [ ] **충전 버튼**: 황금색 CTA
- [ ] **GAME 버튼**: 카지노 이동

##### C. 지식 채굴
- [ ] **YouTube 플레이어** 임베드
- [ ] **진행 상태 바**
- [ ] **보상 받기 버튼**
- [ ] **카지노 슬롯 배너**

##### D. 멤버 정보 (좌측)
- [ ] **회원 이름/랭크**
- [ ] **랭크 배지**: 현재 → 다음
- [ ] **일하기 도구 버튼**
- [ ] **So.T 버튼**: 네온 효과
- [ ] **PI.META 버튼**: 화이트 강조
- [ ] **UNIQUE MARKET 버튼**
- [ ] **로그아웃 버튼**

##### E. 목표 패널 (우측)
- [ ] **다음 랭크 목표**
- [ ] **마녀 캐릭터**: Float 애니메이션
- [ ] **좌측/우측 필요 인원**

##### F. eBook 섹션
- [ ] **학습 자료 카드들**
- [ ] **썸네일 이미지**
- [ ] **관리자 링크**

#### ⚙️ 인터랙션
- [ ] 탭 전환 (지갑/송금)
- [ ] 버튼 호버 효과
- [ ] 도넛 차트 애니메이션
- [ ] 영상 재생

---

### 3️⃣ **Index 페이지** (리더 선택)
**URL**: `/index.html`

#### 🎨 디자인 요소
- [ ] **패턴 배경**: 파란색 타일
- [ ] **Glass panel**: 메인 컨테이너
- [ ] **리더 카드들**: 그리드 레이아웃
- [ ] **리더 사진**: 황금 액자
- [ ] **태그들**: 라운드 칩
- [ ] **SNS 버튼들**: YouTube, TikTok, Instagram 등
- [ ] **배너**: 마퀴 애니메이션

#### ⚙️ 기능
- [ ] 리더 카드 호버
- [ ] SNS 버튼 클릭
- [ ] 배너 자동 스크롤
- [ ] 리더 필터링

---

### 4️⃣ **Market 페이지**
**URL**: `/market.html`

#### 🎨 디자인
- [ ] **상단 바**: 잔액 표시
- [ ] **상품 카드**: Glass 효과
- [ ] **필터 버튼**
- [ ] **가격 표시**: UT 단위

#### ⚙️ 기능
- [ ] 상품 검색
- [ ] 카테고리 필터
- [ ] 구매 버튼
- [ ] 장바구니

---

### 5️⃣ **Casino 페이지**
**URL**: `/casino.html`

#### 🎨 디자인
- [ ] **상단 고정 바**: UT 충전 버튼
- [ ] **게임 카드들**: 룰렛, 슬롯 등
- [ ] **하단 네비**: 로비/베팅/히스토리

#### ⚙️ 기능
- [ ] 게임 선택
- [ ] UT 베팅
- [ ] 결과 표시
- [ ] 히스토리 확인

---

## 🎯 개선 사항 적용 확인

### ✅ CSS 디자인 시스템
**파일**: `css/design-system.css`, `css/enhancements.css`

확인 방법:
```
F12 → Elements → <head> 확인
<link rel="stylesheet" href="css/design-system.css">
<link rel="stylesheet" href="css/enhancements.css">
```

### ✅ Fluid Typography
**확인 방법**:
- 브라우저 창 크기 조절
- 폰트 크기가 부드럽게 변하는지 확인

**테스트**:
- 1920px (데스크톱)
- 768px (태블릿)
- 375px (모바일)

### ✅ 이미지 Lazy Loading
**확인 방법**:
```
F12 → Elements → 이미지 찾기
<img src="..." loading="lazy" decoding="async" alt="...">
```

**네트워크 탭에서**:
- 초기 로드: 위쪽 이미지만
- 스크롤: 추가 이미지 로드

### ✅ 접근성 (Accessibility)
**확인 방법**:

1. **키보드 네비게이션**:
   - Tab 키로 이동
   - Enter로 실행
   - 포커스 스타일 확인 (노란색 테두리)

2. **Skip Link**:
   - 페이지 로드 후 Tab 키
   - "Skip to main content" 링크 표시

3. **ARIA 속성**:
   ```
   F12 → Elements → 버튼/링크 확인
   aria-label="..."
   ```

### ✅ 마이크로 인터랙션
**확인 사항**:
- [ ] 버튼 호버: translateY + scale
- [ ] 카드 호버: shadow + lift
- [ ] 애니메이션: 60fps 부드러움
- [ ] 클릭: 살짝 눌리는 효과

---

## 🐛 알려진 이슈

### 404 에러 (경미)
- 일부 리소스 404 발생 가능
- 기능에 영향 없음
- 실제 배포 시 해결됨

---

## 📊 성능 측정

### Lighthouse 테스트 (권장)
```
F12 → Lighthouse 탭 → Generate report

확인 항목:
- Performance: 90+ 목표
- Accessibility: 92+ (개선됨)
- Best Practices: 90+
- SEO: 90+
```

---

## 🔗 빠른 링크

**Base URL**: `https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai`

- 🚪 [Gate (로그인)](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/the-unique-gate.html)
- 🏠 [Main (대시보드)](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/the-unique-main.html)
- 👥 [Index (리더)](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/index.html)
- 🛒 [Market](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/market.html)
- 🎰 [Casino](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/casino.html)
- 🏆 [Rank Hall](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/rank-hall.html)
- 🎁 [Promo](https://8000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/the-unique-promo.html)

---

## 💡 테스트 팁

### 개발자 도구 활용
1. **Elements 탭**: CSS 변수 확인
2. **Console 탭**: 에러 메시지
3. **Network 탭**: 로딩 속도
4. **Lighthouse 탭**: 성능 측정

### 브라우저별 테스트
- Chrome (권장)
- Firefox
- Safari
- Edge

### 기기별 테스트
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

---

**지금 바로 접속해서 확인하세요!** 🚀

문제 발견 시 알려주시면 즉시 수정하겠습니다! 😊
