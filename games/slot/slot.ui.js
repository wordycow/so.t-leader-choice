(function () {
  const S = (window.S = window.S || {});
  S.ui = S.ui || {};

  const els = {};
  let bgTimer = null;
  let bgIndex = 0;

  function $(id) { return document.getElementById(id); }

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  function init() {
    els.bg = $("bgCycle");

    els.ticker = $("jackpotTicker");
    els.tickerTrack = $("jackpotTickerTrack");

    els.player = $("uiPlayer");
    els.wallet = $("uiWallet");
    els.jackpot = $("uiJackpot");
    els.result = $("uiResult");
    els.bet = $("uiBet");

    els.btnSpin = $("btnSpin");
    els.btnAuto = $("btnAuto");
    els.btnSound = $("btnSound");
    els.btnMinus = $("btnBetMinus");
    els.btnPlus = $("btnBetPlus");
    els.btnPayToggle = $("btnPayToggle");

    els.payBody = $("paytableBody");
    els.grid = $("slotGrid");

    els.celebrate = $("celebrate");
    els.celebrateTitle = $("celebrateTitle");
    els.celebrateAmount = $("celebrateAmount");
    els.celebrateSub = $("celebrateSub");
    els.btnCelebrateClose = $("btnCelebrateClose");

    ensureGridDOM();
    restoreTickerIfAny();
    setBgStatic();
  }

  function ensureGridDOM() {
    if (!els.grid) return;
    if (els.grid.querySelectorAll(".cell").length) return;

    const rows = S.CONFIG.ROWS || 3;
    const cols = S.CONFIG.COLS || 5;

    const frag = document.createDocumentFragment();
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        const img = document.createElement("img");
        img.className = "sym";
        img.alt = "";
        img.loading = "eager";
        img.decoding = "async";
        img.dataset.pos = `${r}-${c}`;
        cell.appendChild(img);
        frag.appendChild(cell);
      }
    }
    els.grid.appendChild(frag);
  }

  function renderGrid(gridIds) {
    if (!els.grid) return;
    const imgs = els.grid.querySelectorAll("img.sym");
    for (let i = 0; i < imgs.length; i++) {
      const id = gridIds[i] || "star1";
      imgs[i].src = `${S.CONFIG.IMG_DIR}/${id}.png`;
    }
  }

  function setPlayer(name) { if (els.player) els.player.textContent = name || "-"; }
  function setWallet(v) { if (els.wallet) els.wallet.textContent = fmt(v); }
  function setJackpot(v) { if (els.jackpot) els.jackpot.textContent = fmt(v); }
  function setResult(t) { if (els.result) els.result.textContent = t || "READY"; }
  function setBet(v) { if (els.bet) els.bet.textContent = fmt(v); }

  // ✅ 이전 코드 호환(에러났던 부분)
  function setWalletUT(v) { setWallet(v); }

  function setSpinEnabled(on) {
    if (els.btnSpin) els.btnSpin.disabled = !on;
  }

  function setAutoLabel(on) {
    if (els.btnAuto) els.btnAuto.textContent = on ? "AUTO ON" : "AUTO OFF";
  }

  function setSoundLabel(on) {
    if (els.btnSound) els.btnSound.textContent = on ? "SOUND ON" : "SOUND OFF";
  }

  function setBgStatic() {
    if (!els.bg) return;
    els.bg.style.backgroundImage = `url("${S.CONFIG.BG_LIST?.[0] || ""}")`;
    els.bg.classList.remove("spinning");
  }

  function startBgCycle() {
    if (!els.bg) return;
    stopBgCycle();
    els.bg.classList.add("spinning");
    const list = S.CONFIG.BG_LIST || [];
    if (!list.length) return;

    bgTimer = setInterval(() => {
      bgIndex = (bgIndex + 1) % list.length;
      els.bg.style.backgroundImage = `url("${list[bgIndex]}")`;
    }, 120);
  }

  function stopBgCycle() {
    if (bgTimer) clearInterval(bgTimer);
    bgTimer = null;
    bgIndex = 0;
    setBgStatic();
  }

  function animateNumber(el, from, to, ms) {
    if (!el) return;
    const a = Number(from || 0);
    const b = Number(to || 0);
    const start = performance.now();
    const dur = Math.max(250, ms || 700);

    function step(now) {
      const t = Math.min(1, (now - start) / dur);
      const v = a + (b - a) * t;
      el.textContent = fmt(v);
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function showCelebrate({ title, amount, sub, ms = 60000 }) {
    if (!els.celebrate) return;
    els.celebrateTitle.textContent = title || "WIN!";
    els.celebrateSub.textContent = sub || "축하드립니다.";
    els.celebrateAmount.textContent = "0";
    els.celebrate.classList.remove("hidden");

    // 금액 카운트업
    animateNumber(els.celebrateAmount, 0, amount || 0, 1200);

    // 자동 종료(기본 60초)
    const t = setTimeout(() => hideCelebrate(), ms);

    const close = () => { clearTimeout(t); hideCelebrate(); };
    els.btnCelebrateClose.onclick = close;
  }

  function hideCelebrate() {
    if (!els.celebrate) return;
    els.celebrate.classList.add("hidden");
  }

  function setTicker(message, untilTs) {
    if (!els.ticker || !els.tickerTrack) return;
    if (!message) return;

    els.tickerTrack.textContent = message;
    els.ticker.classList.remove("hidden");

    try {
      localStorage.setItem("slot_jackpot_ticker", JSON.stringify({ message, untilTs }));
    } catch (_) {}
  }

  function clearTicker() {
    if (!els.ticker) return;
    els.ticker.classList.add("hidden");
    try { localStorage.removeItem("slot_jackpot_ticker"); } catch (_) {}
  }

  function restoreTickerIfAny() {
    try {
      const raw = localStorage.getItem("slot_jackpot_ticker");
      if (!raw) return;
      const o = JSON.parse(raw);
      if (!o?.message || !o?.untilTs) return;
      if (Date.now() > Number(o.untilTs)) { clearTicker(); return; }
      setTicker(o.message, o.untilTs);
    } catch (_) {}
  }

  function midnightKSTTs() {
    const now = new Date();
    // KST 기준 자정
    const kst = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Seoul" }));
    const y = kst.getFullYear();
    const m = kst.getMonth();
    const d = kst.getDate();
    const next = new Date(Date.UTC(y, m, d + 1, 0, 0, 0)); // 대충 UTC 기준 만들고
    // 다시 KST로 맞추는 보정은 localStorage expiry 용도로만 쓰니 이 정도면 충분
    return next.getTime();
  }

  function jackpotTickerFor(name) {
    const msg = `${name}님이 잭팟이 터지셨습니다. 축하드립니다.`;
    setTicker(msg, midnightKSTTs());
  }

  S.ui.init = init;
  S.ui.renderGrid = renderGrid;

  S.ui.setPlayer = setPlayer;
  S.ui.setWallet = setWallet;
  S.ui.setWalletUT = setWalletUT; // 호환
  S.ui.setJackpot = setJackpot;
  S.ui.setResult = setResult;
  S.ui.setBet = setBet;

  S.ui.setSpinEnabled = setSpinEnabled;
  S.ui.setAutoLabel = setAutoLabel;
  S.ui.setSoundLabel = setSoundLabel;

  S.ui.startBgCycle = startBgCycle;
  S.ui.stopBgCycle = stopBgCycle;

  S.ui.animateWallet = (from, to, ms) => animateNumber(els.wallet, from, to, ms);
  S.ui.animateJackpot = (from, to, ms) => animateNumber(els.jackpot, from, to, ms);

  S.ui.showCelebrate = showCelebrate;
  S.ui.jackpotTickerFor = jackpotTickerFor;
})();
