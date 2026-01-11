// js/unique.config.js
(function () {
  window.UNIQUE = window.UNIQUE || {};
  window.UNIQUE.CONFIG = window.UNIQUE.CONFIG || {};

  const C = window.UNIQUE.CONFIG;
  const stripSlash = (s) => String(s || "").trim().replace(/\/+$/, "");

  // ✅ 구글 Apps Script (시트 백엔드)
  C.GOOGLE_SCRIPT_URL =
    "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // ✅ “단일 워커” (vault가 api + slot 다 처리)
  C.VAULT_API_BASE = stripSlash("https://the-unique-vault-api.wordycow0001.workers.dev");
  C.SLOT_API_BASE  = C.VAULT_API_BASE; // ✅ 슬롯도 vault로

  // ✅ 신/구 호환 키
  C.VAULT_WORKER_BASE = C.VAULT_API_BASE;
  C.SLOT_WORKER_BASE  = C.SLOT_API_BASE;

  // ✅ 레거시 전역 (여러 페이지/모듈이 직접 참조)
  window.VAULT_API_BASE = C.VAULT_API_BASE;
  window.SLOT_API_BASE  = C.SLOT_API_BASE;

  // (옵션) 나머지 기존 설정 유지
  C.UT_PRICE_FACTOR = 0.30;
  C.RANK_JSON = "rank-hall.json";
  C.RANK_PAGE = "rank-hall.html";
  C.PROMO_PAGE = "the-unique-promo.html";
  C.REFRESH_MS = 30000;

  console.log("[UNIQUE.CONFIG loaded]", {
    VAULT_WORKER_BASE: C.VAULT_WORKER_BASE,
    GOOGLE_SCRIPT_URL: C.GOOGLE_SCRIPT_URL
  });
})();
