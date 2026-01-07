우리는 GitHub Pages 프로젝트에서 The Unique main.html을 12개 JS 모듈로 분리해서 운영 중이다.

✅ 핵심 규칙
- 스케줄 gviz는 main.html에서 직접 로드하지 않고, js/unique.schedule.js가 U.CONFIG.SCHEDULE_GVIZ_URL로 1회 로드한다(중복 방지).
- main.html은 인라인 스크립트 없이 스크립트 로더 역할만 한다.
- HTML onclick 때문에 전역 함수가 반드시 있어야 한다:
  window.openTab, window.registerNickname, window.sendP2P,
  window.handleScheduleSheet, window.onYouTubeIframeAPIReady

✅ main.html 스크립트 로드 순서
1) js/unique.config.js
2) js/unique.state.js
3) js/unique.utils.js
4) js/unique.api.js
5) js/unique.supabase.js
6) js/unique.ui.js
7) js/unique.schedule.js
8) js/unique.rank.js
9) js/unique.ebooks.js
10) js/unique.wallet.js
11) js/unique.youtube.js
12) js/unique.app.js

✅ 부팅
- unique.app.js DOMContentLoaded에서 boot() 실행
- boot() 순서: requireLogin → schedule.init → UI → refreshUserFromSheet → rank.loadAndApply + bindCaptureClicks → refreshRewardConfig → refreshPricing → ebooks.load → youtube.init + bindRewardButton + bindLuckyBox → setInterval(REFRESH_MS)

이 기준으로 다음 수정 작업을 진행해줘.
