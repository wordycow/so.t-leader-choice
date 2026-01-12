(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  let bgTimer = null;
  let bgIndex = 0;
  let bgUrls = [];

  function setPageBg(url) {
    // 전체 페이지 배경
    document.documentElement.style.setProperty("--slot-bg", `url("${url}")`);

    // 슬롯 스테이지 배경(img)도 같이(원하면 더 화려해짐)
    const bgImg = document.getElementById("slotBgImg");
    if (bgImg) bgImg.src = url;
  }

  function buildBgUrls() {
    const base = SLOT.config?.ASSET?.imgBase || "./img/slot";
    const files = SLOT.config?.ASSET?.bgFiles || ["bg1.png", "bg2.png", "bg3.png", "bg4.png", "bg5.png"];
    bgUrls = files.map((f) => `${base}/${f}`);
    bgIndex = Math.floor(Math.random() * bgUrls.length);
    setPageBg(bgUrls[bgIndex]);
  }

  function startBgCycle() {
    if (bgTimer) return;
    const maxInterval = SLOT.config?.BG_CYCLE?.maxIntervalMs ?? 200;

    // “최소속도일때 0.2초” = 절대 200ms보다 느려지지 않게(=max 200ms)
    const intervalMs = Math.max(50, Math.min(maxInterval, 200));

    bgTimer = setInterval(() => {
      if (!bgUrls.length) return;
      bgIndex = (bgIndex + 1) % bgUrls.length;
      setPageBg(bgUrls[bgIndex]);
    }, intervalMs);
  }

  function stopBgCycle() {
    if (!bgTimer) return;
    clearInterval(bgTimer);
    bgTimer = null;
  }

  function setupPayToggle() {
    const btn = document.getElementById("payToggle");
    const card = document.getElementById("paytableCard");
    if (!btn || !card) return;

    const key = SLOT.config?.STORAGE_KEYS?.payCollapsed || "slot_pay_collapsed_v1";

    const apply = (collapsed) => {
      card.classList.toggle("collapsed", !!collapsed);
      btn.textContent = collapsed ? "펼치기" : "접기";
      try {
        localStorage.setItem(key, collapsed ? "1" : "0");
      } catch (_) {}
    };

    // 초기 상태
    let collapsed = false;
    try {
      collapsed = localStorage.getItem(key) === "1";
    } catch (_) {}
    apply(collapsed);

    btn.addEventListener("click", () => {
      collapsed = !card.classList.contains("collapsed");
      apply(collapsed);
    });
  }

  function setupSpinHooks() {
    const spinBtn = document.getElementById("spinBtn");
    const lastEl = document.getElementById("lastResult");

    const isSpinningText = () => {
      const t = (lastEl?.textContent || "").toUpperCase();
      return t.includes("SPINNING");
    };

    const onSpinStart = () => {
      startBgCycle();
      SLOT.audio?.unlock?.();
      SLOT.audio?.playStart?.();
      SLOT.audio?.startSpinning?.();
    };

    const onSpinStop = () => {
      stopBgCycle();
      SLOT.audio?.stopSpinning?.();
      SLOT.audio?.playStop?.();
    };

    // 클릭으로 시작(사용자 제스처 확보)
    spinBtn?.addEventListener("click", () => {
      onSpinStart();
    });

    // LAST RESULT 변화 감시해서 멈춤 처리
    if (lastEl) {
      const mo = new MutationObserver(() => {
        if (isSpinningText()) {
          startBgCycle();
          SLOT.audio?.startSpinning?.();
        } else {
          onSpinStop();
        }
      });
      mo.observe(lastEl, { childList: true, subtree: true, characterData: true });
    }

    // 탭 비활성화 시 정지
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stopBgCycle();
        SLOT.audio?.stopSpinning?.();
      } else {
        if (isSpinningText()) {
          startBgCycle();
          SLOT.audio?.startSpinning?.();
        }
      }
    });
  }

  function hideRuleLine() {
    const rule = document.querySelector("#paytableCard .ruleLine");
    if (rule) rule.style.display = "none";
  }

  function boot() {
    try {
      SLOT.audio?.init?.();
    } catch (_) {}

    buildBgUrls();
    setupPayToggle();
    setupSpinHooks();
    hideRuleLine();
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
