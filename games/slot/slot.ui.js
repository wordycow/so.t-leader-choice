(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config || {};

  const els = {};

  function $(id) { return document.getElementById(id); }

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return String(Math.round(x * 100) / 100);
  }

  function symbolToSrc(key) {
    const s = (cfg.SYMBOL_MAP && cfg.SYMBOL_MAP[key]) ? cfg.SYMBOL_MAP[key] : null;
    const base = cfg.ASSET && cfg.ASSET.imgBase ? cfg.ASSET.imgBase : "";
    if (!base || !s || !s.file) return "";
    return `${base}/${s.file}`;
  }

  function ensureGrid() {
    const grid = els.slotGrid;
    if (!grid) return;

    const rows = (cfg.GRID && cfg.GRID.rows) || 3;
    const cols = (cfg.GRID && cfg.GRID.cols) || 5;

    grid.innerHTML = "";
    const cells = [];

    for (let i = 0; i < rows * cols; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";

      const img = document.createElement("img");
      img.className = "cellImg";
      img.alt = "";

      const label = document.createElement("div");
      label.className = "cellLabel";
      label.textContent = "";

      cell.appendChild(img);
      cell.appendChild(label);
      grid.appendChild(cell);

      cells.push({ cell, img, label });
    }

    els._cells = cells;
  }

  function renderPaytable() {
    const wrap = els.payWrap;
    if (!wrap) return;

    const lines = cfg.PAYTABLE_TEXT || [];
    wrap.innerHTML = "";

    const box = document.createElement("div");
    box.className = "payBox";

    const ul = document.createElement("ul");
    ul.className = "payList";

    lines.forEach(t => {
      const li = document.createElement("li");
      li.textContent = t;
      ul.appendChild(li);
    });

    box.appendChild(ul);
    wrap.appendChild(box);
  }

  function togglePaytable() {
    const wrap = els.payWrap;
    if (!wrap) return;

    // ✅ CSS에 의존하지 않고 무조건 토글
    const now = wrap.style.display;
    wrap.style.display = (now === "none") ? "" : "none";
  }

  function showOverlay(title, htmlText) {
    const ov = els.loginOverlay;
    if (!ov) return;

    const t = els.overlayTitle;
    const tx = els.overlayText;
    if (t) t.textContent = title || "";
    if (tx) tx.innerHTML = htmlText || "";

    ov.classList.remove("hidden");
  }

  function hideOverlay() {
    const ov = els.loginOverlay;
    if (!ov) return;
    ov.classList.add("hidden");
  }

  function setBanner(msg) {
    if (!els.jackpotBanner || !els.jackpotBannerText) return;
    els.jackpotBannerText.textContent = msg || "";
    if (msg) els.jackpotBanner.classList.remove("hidden");
    else els.jackpotBanner.classList.add("hidden");
  }

  SLOT.ui = {
    init() {
      els.slotGrid = $("slotGrid");
      els.slotBgImg = $("slotBgImg");
      els.payWrap = $("payWrap");
      els.payToggle = $("payToggle");

      els.playerName = $("playerName");
      els.walletUt = $("walletUt");
      els.jackpotPool = $("jackpotPool");
      els.lastResult = $("lastResult");

      els.betUt = $("betUt");
      els.betDown = $("betDown");
      els.betUp = $("betUp");

      els.autoBtn = $("autoBtn");
      els.soundBtn = $("soundBtn");
      els.spinBtn = $("spinBtn");

      els.loginOverlay = $("loginOverlay");
      els.overlayTitle = $("overlayTitle");
      els.overlayText = $("overlayText");

      els.jackpotBanner = $("jackpotBanner");
      els.jackpotBannerText = $("jackpotBannerText");

      // bg
      const bg = cfg.ASSET && cfg.ASSET.bg ? cfg.ASSET.bg : "";
      if (els.slotBgImg) {
        if (bg) {
          els.slotBgImg.src = bg;
          els.slotBgImg.style.display = "";
        } else {
          els.slotBgImg.removeAttribute("src");
          els.slotBgImg.style.display = "none";
        }
      }

      ensureGrid();
      renderPaytable();

      if (els.payToggle) {
        els.payToggle.addEventListener("click", (e) => {
          e.preventDefault();
          togglePaytable();
        });
      }
    },

    setPlayer(name) { if (els.playerName) els.playerName.textContent = name || "-"; },
    setWallet(n) { if (els.walletUt) els.walletUt.textContent = fmt(n); },
    setJackpotPool(n) { if (els.jackpotPool) els.jackpotPool.textContent = fmt(n); },
    setLastResult(t) { if (els.lastResult) els.lastResult.textContent = t || "READY"; },

    setBet(n) { if (els.betUt) els.betUt.textContent = String(n || 0); },

    applyKeys(keys) {
      const cells = els._cells || [];
      if (!Array.isArray(keys) || keys.length !== cells.length) return;

      keys.forEach((k, i) => {
        const c = cells[i];
        const src = symbolToSrc(k);

        if (c.img) {
          if (src) {
            c.img.src = src;
            c.img.style.display = "";
          } else {
            c.img.removeAttribute("src");
            c.img.style.display = "none";
          }
        }
        if (c.label) {
          const info = (cfg.SYMBOL_MAP && cfg.SYMBOL_MAP[k]) ? cfg.SYMBOL_MAP[k] : null;
          c.label.textContent = info ? info.label : (k || "");
        }
      });
    },

    showLoginOverlayMissingId() {
      showOverlay(
        "로그인 정보가 없습니다",
        `URL에 <b>?id=아이디</b>를 붙이거나 MAIN에서 로그인 후 들어오세요.<br/>
         예: <code>.../games/slot.html?id=wordycow</code>`
      );
    },

    showOverlayConfigMissing() {
      showOverlay(
        "설정이 필요합니다",
        `slot.config.js의 <b>SCRIPT_URL</b>에 Apps Script 웹앱(/exec) 주소를 넣어주세요.`
      );
    },

    hideOverlay,

    // ✅ 잭팟 배너: 자정까지 유지(로컬 저장)
    persistBannerUntilMidnight(msg) {
      try {
        const key = cfg.STORAGE_KEYS && cfg.STORAGE_KEYS.banner;
        if (!key) return;

        const now = new Date();
        const end = new Date(now);
        end.setHours(23, 59, 59, 999);

        localStorage.setItem(key, JSON.stringify({
          msg: msg || "",
          until: end.getTime()
        }));
      } catch (_) {}
    },

    loadPersistedBanner() {
      try {
        const key = cfg.STORAGE_KEYS && cfg.STORAGE_KEYS.banner;
        if (!key) return;

        const raw = localStorage.getItem(key);
        if (!raw) return;

        const data = JSON.parse(raw);
        if (!data || !data.msg || !data.until) return;

        if (Date.now() <= Number(data.until)) {
          setBanner(String(data.msg));
        } else {
          localStorage.removeItem(key);
        }
      } catch (_) {}
    },

    showBanner(msg) { setBanner(msg); }
  };
})();
