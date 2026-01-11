// js/unique.config.js
(function () {
  window.UNIQUE = window.UNIQUE || {};
  window.UNIQUE.CONFIG = window.UNIQUE.CONFIG || {};

  const stripSlash = (s) => String(s || "").replace(/\/+$/, "");

  const C = window.UNIQUE.CONFIG;

  // ✅ 공통 백엔드
  C.SUPABASE_URL = "https://lrpscubricemcgfssjgg.supabase.co";
  C.SUPABASE_KEY = "sb_publishable_8mMA4oEsuB9j0rc6KsLmtQ_UkJo0Zaq";

  C.GOOGLE_SCRIPT_URL =
    "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // ✅ Worker 주소(여기만 바꾸면 전부 따라오게)
  // - slot.page.js 는 SLOT_WORKER_BASE를 읽음
  // - 기존 코드들은 SLOT_API_BASE를 읽는 경우가 있어서 둘 다 유지(동일값)
  C.VAULT_API_BASE = stripSlash("https://the-unique-vault-api.wordycow0001.workers.dev");
  C.SLOT_API_BASE  = stripSlash("https://the-unique-slot-api.wordycow0001.workers.dev");

  // ✅ 신/구 호환 키(중요)
  C.VAULT_WORKER_BASE = C.VAULT_API_BASE;
  C.SLOT_WORKER_BASE  = C.SLOT_API_BASE;

  // ✅ (옵션) games/slot/slot.api.js 가 window.SLOT_API_BASE도 보므로 같이 세팅
  //   - 모듈형 슬롯을 다시 쓸 때도 자동으로 동일 워커로 붙음
  window.SLOT_API_BASE = C.SLOT_API_BASE;

  // ✅ 경제/설정
  C.UT_PRICE_FACTOR = 0.30;

  C.RANK_JSON = "rank-hall.json";
  C.RANK_PAGE = "rank-hall.html";
  C.PROMO_PAGE = "the-unique-promo.html";

  C.EBOOK_JSON = "ebook-config.json";
  C.EBOOK_FALLBACK = [
    {
      id: "unique-basic",
      title: "협력을 배우고 협력을 만들어낸다.",
      description: "THE UNIQUE 기본 매뉴얼",
      cover: "img/ebook-the-unique-system-book.jpg",
      link: "ebook.html",
      visible: true,
      order: 1,
      posY: 50,
    },
    {
      id: "unique-sot",
      title: "현대 사회에 맞는 여행도구 so.t",
      description: "so.t 안에서 서로를 챙겨주며 함께 여행을 그린다.",
      cover: "img/ebook-network-marketing-cover.jpg",
      link: "ebook1.html",
      visible: true,
      order: 2,
      posY: 50,
    },
  ];

  C.SCHEDULE_GVIZ_URL =
    "https://docs.google.com/spreadsheets/d/1C4fyJtyBHSaBIWyN_lM75Zp7myvtz3cKfHYUbAmoVQY/gviz/tq?gid=0&tqx=responseHandler:handleScheduleSheet";

  C.YT_VIDEO_ID = "DBcSLPRz0HI";
  C.REFRESH_MS = 30000;

  // 디버그 확인용
  console.log("[UNIQUE.CONFIG]", {
    SLOT_WORKER_BASE: C.SLOT_WORKER_BASE,
    VAULT_WORKER_BASE: C.VAULT_WORKER_BASE,
  });
  // 슬롯 모듈들이 window.SLOT_API_BASE 를 직접 읽으므로 브릿지로 연결
window.VAULT_API_BASE = window.UNIQUE.CONFIG.VAULT_API_BASE;
window.SLOT_API_BASE  = window.UNIQUE.CONFIG.VAULT_API_BASE; // ✅ 슬롯은 vault의 /slot/state, /slot/spin을 사용

})();
