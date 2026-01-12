/* games/slot/slot.ui.js */
(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config;

  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return Array.from(document.querySelectorAll(sel)); }

  function setText(el, text) {
    if (!el) return;
    el.textContent = text == null ? "" : String(text);
  }

  function setNum(el, n) {
    if (!el) return;
    const v = Number(n);
    el.textContent = Number.isFinite(v) ? String(v) : "0";
  }

  function symbolDef(key) {
    return (cfg.SYMBOLS || []).find(s => s.key === key) || null;
  }

  function symbolImgUrl(key) {
    const s = symbolDef(key);
    if (!s) return "";
    return `${cfg.ASSET.imgBase}${s.file}`;
  }

  function ensureGridCells() {
    // 1) 이미 15칸이 있으면 그대로 사용
    let cells = $all(".slot-cell,[data-slot-cell]");
    if (cells.length === 15) return cells;

    // 2) 없으면 slotGrid 컨테이너 찾아서 15칸 생성
    const grid = $("#slotGrid") || $(".slot-grid") || $("[data-slot-grid]");
    if (!grid) return cells;

    grid.innerHTML = "";
    for (let i = 0; i < 15; i++) {
      const d = document.createElement("div");
      d.className = "slot-cell";
      d.setAttribute("data-slot-cell", "1");
      grid.appendChild(d);
    }
    return $all(".slot-cell,[data-slot-cell]");
  }

  function renderGrid(keys = []) {
    const cells = ensureGridCells();
    if (!cells || !cells.length) return;

    for (let i = 0; i < cells.length; i++) {
      const key = keys[i];
      const cell = cells[i];
      if (!key) { cell.innerHTML = ""; continue; }

      const url = symbolImgUrl(key);
      const s = symbolDef(key);

      // 이미지가 없거나 경로가 틀려도 텍스트로라도 보이게
      cell.innerHTML = url
        ? `<img alt="${s?.label || key}" src="${url}" style="width:100%;height:100%;object-fit:contain;" />`
        : `<div style="display:flex;align-items:center;justify-content:center;height:100%;font-weight:700;">${s?.label || key}</div>`;
    }
  }

  // ====== PAYTABLE 접기/펼치기 ======
  function bindPayTableToggle() {
    const btn =
      document.querySelector("#btnPayToggle") ||
      document.querySelector("#payToggleBtn") ||
      document.querySelector("#payTableToggle") ||
      document.querySelector('[data-action="pay-toggle"]') ||
      Array.from(document.querySelectorAll("button")).find(b => (b.textContent || "").includes("접기/펼치기"));

    if (!btn) return;

    // 버튼이 들어있는 카드(또는 섹션) 찾기
    const card =
      btn.closest("#payTable") ||
      btn.closest(".paytable-card") ||
      btn.closest(".card") ||
      btn.closest("section") ||
      document.querySelector("#payTable") ||
      document.querySelector(".paytable-card");

    if (!card) return;

    // 카드 안에서 “헤더 제외 나머지”를 body로 간주
    const header =
      btn.closest(".card-head") ||
      btn.closest(".panel-head") ||
      btn.parentElement;

    const bodyCandidates = [
      card.querySelector(".paytable-body"),
      card.querySelector(".card-body"),
      card.querySelector(".panel-body"),
      card.querySelector("[data-paytable-body]"),
    ].filter(Boolean);

    let bodies = bodyCandidates.length ? bodyCandidates : [];
    if (!bodies.length) {
      bodies = Array.from(card.children).filter(ch => ch !== header);
    }

    // 초기 상태 복원
    const saved = localStorage.getItem(cfg.STORAGE.payCollapsed);
    let collapsed = saved === "1";
    applyCollapsed(collapsed);

    btn.addEventListener("click", () => {
      collapsed = !collapsed;
      localStorage.setItem(cfg.STORAGE.payCollapsed, collapsed ? "1" : "0");
      applyCollapsed(collapsed);
    });

    function applyCollapsed(isCollapsed) {
      bodies.forEach(el => {
        el.style.display = isCollapsed ? "none" : "";
      });
    }
  }

  // ====== 잭팟 배너(자정까지) ======
  function setJackpotBanner(text) {
    const key = cfg.STORAGE.banner;
    if (!text) {
      localStorage.removeItem(key);
      hideBanner();
      return;
    }

    // 자정까지 유지
    const now = new Date();
    const midnight = new Date(now);
    midnight.setHours(24, 0, 0, 0);

    localStorage.setItem(key, JSON.stringify({ text, until: midnight.getTime() }));
    showBanner(text);
  }

  function restoreJackpotBanner() {
    const key = cfg.STORAGE.banner;
    const raw = localStorage.getItem(key);
    if (!raw) return;
    try {
      const o = JSON.parse(raw);
      if (!o || !o.text || !o.until) return;
      if (Date.now() > Number(o.until)) {
        localStorage.removeItem(key);
        return;
      }
      showBanner(o.text);
    } catch (_) {}
  }

  function showBanner(text) {
    let el = document.querySelector("#jackpotBanner");
    if (!el) {
      el = document.createElement("div");
      el.id = "jackpotBanner";
      el.style.cssText =
        "position:sticky;top:0;z-index:50;background:#0b1226;color:#fff;padding:10px 12px;overflow:hidden;border-bottom:1px solid rgba(255,255,255,.12)";
      el.innerHTML = `<div id="jackpotTicker" style="white-space:nowrap;will-change:transform;display:inline-block;">${escapeHtml(
        text
      )}</div>`;
      document.body.prepend(el);

      // ticker animation
      const ticker = el.querySelector("#jackpotTicker");
      ticker.animate(
        [{ transform: "translateX(100%)" }, { transform: "translateX(-120%)" }],
        { duration: 12000, iterations: Infinity }
      );
    } else {
      const ticker = el.querySelector("#jackpotTicker");
      if (ticker) ticker.textContent = text;
    }
  }

  function hideBanner() {
    const el = document.querySelector("#jackpotBanner");
    if (el) el.remove();
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (m) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[m]));
  }

  // ====== public helpers ======
  function setPlayer(nameOrNick) {
    setText($("#playerValue") || $("#playerName") || $("[data-player]"), nameOrNick || "-");
  }

  function setWallet(ut) {
    setNum($("#walletValue") || $("#walletUt") || $("[data-wallet]"), ut);
  }

  function setJackpotPool(ut) {
    setNum($("#jackpotValue") || $("#jackpotPool") || $("[data-jackpot]"), ut);
  }

  function setLastResult(text) {
    setText($("#lastResultValue") || $("#lastResult") || $("[data-last]"), text || "READY");
  }

  function setBet(ut) {
    setNum($("#betValue") || $("#betUt") || $("[data-bet]"), ut);
  }

  SLOT.ui = {
    renderGrid,
    bindPayTableToggle,
    setPlayer,
    setWallet,
    setJackpotPool,
    setLastResult,
    setBet,
    setJackpotBanner,
    restoreJackpotBanner,
  };
})();
