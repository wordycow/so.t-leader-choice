(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const C = () => SLOT.config;

  let els = {};
  let cellImgs = [];
  let bgTimer = null;
  let bgIndex = 0;

  function q(id) { return document.getElementById(id); }

  function imgUrl(file) {
    return `${C().ASSET.imgBase}/${file}`;
  }

  function setHidden(el, hidden) {
    if (!el) return;
    if (hidden) el.classList.add("hidden");
    else el.classList.remove("hidden");
  }

  function buildGrid() {
    const grid = els.slotGrid;
    grid.innerHTML = "";
    cellImgs = [];

    const total = C().GRID.rows * C().GRID.cols;
    for (let i = 0; i < total; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";

      const img = document.createElement("img");
      img.alt = "";
      img.loading = "eager";
      img.decoding = "async";

      cell.appendChild(img);
      grid.appendChild(cell);
      cellImgs.push(img);
    }
  }

  function renderPaytable() {
    const wrap = els.payWrap;
    const ul = document.createElement("ul");
    ul.className = "payList";
    (C().PAYTABLE_TEXT || []).forEach((t) => {
      const li = document.createElement("li");
      li.textContent = t;
      ul.appendChild(li);
    });
    wrap.innerHTML = "";
    wrap.appendChild(ul);
  }

  function getPayCollapsed() {
    try {
      return localStorage.getItem(C().STORAGE_KEYS.payCollapsed) === "1";
    } catch (_) {
      return false;
    }
  }

  function setPayCollapsed(v) {
    const collapsed = !!v;
    if (els.payWrap) els.payWrap.style.display = collapsed ? "none" : "";
    try {
      localStorage.setItem(C().STORAGE_KEYS.payCollapsed, collapsed ? "1" : "0");
    } catch (_) {}
  }

  function bindPayToggle() {
    els.payToggle.addEventListener("click", () => {
      const now = els.payWrap.style.display === "none";
      setPayCollapsed(!now);
    });
  }

  function setGridKeys(keys) {
    if (!Array.isArray(keys) || keys.length !== cellImgs.length) return;

    for (let i = 0; i < keys.length; i++) {
      const key = keys[i];
      const sym = C().SYMBOL_MAP[key];
      const img = cellImgs[i];
      if (!sym) { img.removeAttribute("src"); continue; }
      img.src = imgUrl(sym.file);
    }
  }

  function randomGrid() {
    const arr = C().SYMBOLS;
    for (let i = 0; i < cellImgs.length; i++) {
      const sym = arr[(Math.random() * arr.length) | 0];
      cellImgs[i].src = imgUrl(sym.file);
    }
  }

  function setBgByIndex(i) {
    const files = C().ASSET.bgFiles || [];
    if (!files.length) return;
    bgIndex = ((i % files.length) + files.length) % files.length;
    els.slotBgImg.src = imgUrl(files[bgIndex]);
  }

  function startBgCycle(intervalMs) {
    stopBgCycle();
    const min = Number(C().SPIN.minBgIntervalMs || 200);
    const ms = Math.max(min, Math.floor(intervalMs || min));
    setBgByIndex(bgIndex); // ensure set
    bgTimer = setInterval(() => {
      setBgByIndex(bgIndex + 1);
    }, ms);
  }

  function stopBgCycle() {
    if (bgTimer) {
      clearInterval(bgTimer);
      bgTimer = null;
    }
  }

  function setPlayer(name) { els.playerName.textContent = name || "-"; }
  function setWallet(n) { els.walletUt.textContent = String(n ?? 0); }
  function setJackpotPool(n) { els.jackpotPool.textContent = String(n ?? 0); }
  function setLastResult(t) { els.lastResult.textContent = t || "READY"; }
  function setBet(n) { els.betUt.textContent = String(n ?? 0); }

  function setButtonsEnabled(enabled) {
    const dis = !enabled;
    ["spinBtn","betDown","betUp","autoBtn","soundBtn","payToggle"].forEach((id) => {
      const el = els[id];
      if (el) el.disabled = dis;
    });
  }

  // ✅ 잭팟 티커
  function showJackpotBanner(text) {
    els.jackpotBannerText.textContent = text;
    setHidden(els.jackpotBanner, false);
  }
  function hideJackpotBanner() {
    setHidden(els.jackpotBanner, true);
  }

  function showLoginOverlay(show) {
    setHidden(els.loginOverlay, !show);
  }

  function preloadAssets() {
    // background preload
    (C().ASSET.bgFiles || []).forEach((f) => {
      const im = new Image();
      im.src = imgUrl(f);
    });
    // symbols preload
    (C().SYMBOLS || []).forEach((s) => {
      const im = new Image();
      im.src = imgUrl(s.file);
    });
  }

  SLOT.ui = {
    init() {
      els = {
        slotGrid: q("slotGrid"),
        slotBgImg: q("slotBgImg"),
        payWrap: q("payWrap"),
        payToggle: q("payToggle"),

        playerName: q("playerName"),
        walletUt: q("walletUt"),
        jackpotPool: q("jackpotPool"),
        lastResult: q("lastResult"),

        betUt: q("betUt"),
        betDown: q("betDown"),
        betUp: q("betUp"),
        autoBtn: q("autoBtn"),
        soundBtn: q("soundBtn"),
        spinBtn: q("spinBtn"),

        loginOverlay: q("loginOverlay"),

        jackpotBanner: q("jackpotBanner"),
        jackpotBannerText: q("jackpotBannerText"),
      };

      buildGrid();
      renderPaytable();
      bindPayToggle();

      // paytable 상태 복원
      setPayCollapsed(getPayCollapsed());

      // bg 초기값
      setBgByIndex(0);

      preloadAssets();
    },

    els: () => els,

    setGridKeys,
    randomGrid,

    startBgCycle,
    stopBgCycle,
    setBgByIndex,

    setPlayer,
    setWallet,
    setJackpotPool,
    setLastResult,
    setBet,
    setButtonsEnabled,

    showJackpotBanner,
    hideJackpotBanner,
    showLoginOverlay,
  };
})();
