(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  const $ = (id) => document.getElementById(id);

  const dom = {
    grid: $("slotGrid"),
    bgImg: $("slotBgImg"),
    payToggle: $("payToggle"),
    payWrap: $("payWrap"),
    playerName: $("playerName"),
    walletUt: $("walletUt"),
    jackpotPool: $("jackpotPool"),
    lastResult: $("lastResult"),
    overlay: $("loginOverlay"),
  };

  let cells = []; // {el, img}
  let bgTimer = null;
  let bgIndex = 0;

  function imgUrl(file) {
    return `${CFG().ASSET.imgBase}/${file}`;
  }

  function buildGrid() {
    const { rows, cols } = CFG().GRID;
    dom.grid.innerHTML = "";
    cells = [];

    dom.grid.style.setProperty("--r", rows);
    dom.grid.style.setProperty("--c", cols);

    for (let i = 0; i < rows * cols; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";

      const img = document.createElement("img");
      img.className = "cellImg";
      img.alt = "";
      img.decoding = "async";
      img.loading = "eager";

      cell.appendChild(img);
      dom.grid.appendChild(cell);
      cells.push({ el: cell, img });
    }
  }

  function setCellKey(i, key) {
    const sym = CFG().SYMBOL_MAP[key];
    if (!cells[i]) return;
    if (!sym) {
      cells[i].img.removeAttribute("src");
      return;
    }
    const src = imgUrl(sym.file);
    cells[i].img.src = src;
  }

  function setKeys(keys = []) {
    for (let i = 0; i < cells.length; i++) setCellKey(i, keys[i]);
  }

  function renderPaytable() {
    const lines = CFG().PAYTABLE_TEXT || [];
    const ul = document.createElement("ul");
    ul.className = "payList";
    lines.forEach(t => {
      const li = document.createElement("li");
      li.textContent = t;
      ul.appendChild(li);
    });
    dom.payWrap.innerHTML = "";
    dom.payWrap.appendChild(ul);
  }

  function bindPayToggle() {
    if (!dom.payToggle) return;
    dom.payToggle.addEventListener("click", () => {
      dom.payWrap.classList.toggle("collapsed");
    });
  }

  function setBgByIndex(nextIdx) {
    const files = CFG().ASSET.bgFiles || [];
    if (!files.length) return;

    bgIndex = ((nextIdx % files.length) + files.length) % files.length;
    const src = imgUrl(files[bgIndex]);

    // src 바꾸기
    dom.bgImg.src = src;
  }

  function startBgSpin(intervalMs) {
    stopBgSpin();
    const ms = Math.max(50, Math.floor(intervalMs || 120));
    setBgByIndex(bgIndex);

    bgTimer = setInterval(() => {
      setBgByIndex(bgIndex + 1);
    }, ms);
  }

  function stopBgSpin() {
    if (bgTimer) {
      clearInterval(bgTimer);
      bgTimer = null;
    }
  }

  function initBgIdle() {
    // 대기 시 첫 배경 고정
    setBgByIndex(0);
  }

  function showOverlay(show) {
    if (!dom.overlay) return;
    dom.overlay.classList.toggle("hidden", !show);
  }

  function setPlayer(name) { dom.playerName.textContent = name || "-"; }
  function setWallet(n) { dom.walletUt.textContent = String(n ?? 0); }
  function setJackpotPool(n) { dom.jackpotPool.textContent = String(n ?? 0); }
  function setLastResult(t) { dom.lastResult.textContent = t || "READY"; }

  SLOT.ui = {
    init() {
      if (!CFG() || !CFG().ASSET || !CFG().ASSET.imgBase) {
        throw new Error("slot.config not loaded");
      }
      buildGrid();
      renderPaytable();
      bindPayToggle();
      initBgIdle();
      setLastResult("READY");
    },

    setKeys,
    startBgSpin,
    stopBgSpin,

    showOverlay,
    setPlayer,
    setWallet,
    setJackpotPool,
    setLastResult,
  };
})();
