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

  // ✅ Worker 주소
  C.VAULT_API_BASE = stripSlash("https://the-unique-vault-api.wordycow0001.workers.dev");

  // (참고) 분리 슬롯 워커가 따로 있을 때를 대비해서 남겨둠
  C.SLOT_DEDICATED_API_BASE = stripSlash("https://the-unique-slot-api.wordycow0001.workers.dev");

  // ✅ 신/구 호환 키(절대 undefined 안 나게)
  C.VAULT_WORKER_BASE = C.VAULT_API_BASE;
  C.VAULT_WORKER_URL  = C.VAULT_API_BASE;

  // ✅ 현재 슬롯의 실제 엔드포인트는 vault 워커의 /slot/state, /slot/spin 사용
  // 그래서 슬롯 쪽도 vault로 통일
  C.SLOT_API_BASE     = C.VAULT_API_BASE;
  C.SLOT_WORKER_BASE  = C.VAULT_API_BASE;

  // ✅ 전역 브릿지 (모듈들이 이걸 직접 읽음)
  window.VAULT_API_BASE = C.VAULT_API_BASE;
  window.SLOT_API_BASE  = C.VAULT_API_BASE;

  // ✅ 경제/설정
  C.UT_PRICE_FACTOR = 0.30;

  C.RANK_JSON = "rank-hall.json";
  C.RANK_PAGE = "rank-hall.html";
  C.PROMO_PAGE = "the-unique-promo.html";

  C.EBOOK_JSON = "ebook-config.json";
  C.EBOOK_FALLBACK = [
    { id:"unique-basic", title:"협력을 배우고 협력을 만들어낸다.", description:"THE UNIQUE 기본 매뉴얼", cover:"img/ebook-the-unique-system-book.jpg", link:"ebook.html", visible:true, order:1, posY:50 },
    { id:"unique-sot", title:"현대 사회에 맞는 여행도구 so.t", description:"so.t 안에서 서로를 챙겨주며 함께 여행을 그린다.", cover:"img/ebook-network-marketing-cover.jpg", link:"ebook1.html", visible:true, order:2, posY:50 }
  ];

  C.SCHEDULE_GVIZ_URL =
    "https://docs.google.com/spreadsheets/d/1C4fyJtyBHSaBIWyN_lM75Zp7myvtz3cKfHYUbAmoVQY/gviz/tq?gid=0&tqx=responseHandler:handleScheduleSheet";

  C.YT_VIDEO_ID = "DBcSLPRz0HI";
  C.REFRESH_MS = 30000;

  // ✅ 디버그 확인용
  console.log("[UNIQUE.CONFIG READY]", {
    VAULT_API_BASE: C.VAULT_API_BASE,
    VAULT_WORKER_BASE: C.VAULT_WORKER_BASE,
    SLOT_API_BASE: C.SLOT_API_BASE
  });
})();
