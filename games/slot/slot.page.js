/* games/slot/slot.page.js */
(() => {
  const S = (window.SLOT = window.SLOT || {});
  const api = S.api;

  const els = {
    bg: document.getElementById("bg"),
    hint: document.getElementById("hintText"),
    player: document.getElementById("playerName"),
    wallet: document.getElementById("walletUt"),
    jackpot: document.getElementById("jackpotVal"),
    win: document.getElementById("winVal"),

    betMinus: document.getElementById("betMinus"),
    betPlus: document.getElementById("betPlus"),
    betAmount: document.getElementById("betAmount"),

    payTable: document.getElementById("payTable"),
    payline: document.getElementById("payline"),

    spinBtn: document.getElementById("spinBtn"),
    autoBtn: document.getElementById("autoBtn"),
    autoText: document.getElementById("autoText"),

    reels: [
      document.getElementById("reel0"),
      document.getElementById("reel1"),
      document.getElementById("reel2"),
      document.getElementById("reel3"),
      document.getElementById("reel4"),
    ],
  };

  const SYMBOLS = [
    { id: "star1", name: "STAR 1", payout: 2 },
    { id: "star2", name: "STAR 2", payout: 3 },
    { id: "star3", name: "STAR 3", payout: 5 },

    { id: "pro1", name: "PRO 1", payout: 8 },
    { id: "pro2", name: "PRO 2", payout: 12 },
    { id: "pro3", name: "PRO 3", payout: 16 },
    { id: "pro4", name: "PRO 4", payout: 24 },
    { id: "pro5", name: "PRO 5", payout: 32 },
    { id: "pro6", name: "PRO 6", payout: 48 },
    { id: "pro7", name: "PRO 7", payout: 64 },
    { id: "pro8", name: "PRO 8", payout: 96 },
    { id: "pro9", name: "PRO 9", payout: 128 },
    { id: "pro10", name: "PRO 10", payout: 200 },
  ];

  function imgOf(id) {
    // slot.html(= games/slot.html) 기준으로 img/slot/<id>.png
    return `img/slot/${id}.png`;
  }

  const state = {
    spinning: false,
    auto: false,

    ut: 0,
    jackpot: 0,
    bet: 10,

    betMin: 10,
    betMax: 1000,
    betStep: 10,

    displayName: "",
    lastWin: 0,
    lastBet: 0,
  };

  // ---------- UI helpers ----------
  function flashBg() {
    if (!els.bg) return;
    els.bg.classList.add("flash");
    setTimeout(() => els.bg.classList.remove("flash"), 280);
  }
  function hint(t) {
    if (els.hint) els.hint.textContent = t;
  }

  function setAuto(on) {
    state.auto = !!on;
    if (state.auto) {
      els.autoBtn.classList.add("active");
      els.autoText.textContent = "AUTO ON";
    } else {
      els.autoBtn.classList.remove("active");
      els.autoText.textContent = "AUTO OFF";
    }
  }

  function updateUI() {
    const ident = api?.getUserIdentity?.() || { display: "Guest" };
    els.player.textContent = state.displayName || ident.display || "Guest";
    els.wallet.textContent = Number(state.ut || 0).toFixed(2);
    els.jackpot.textContent = String(Math.floor(Number(state.jackpot || 0)));

    // ✅ "얼마 따고/얼마 잃었다"
    const w = Math.floor(Number(state.lastWin || 0));
    const b = Math.floor(Number(state.lastBet || 0));
    if (w === 0 && b === 0) {
      els.win.textContent = "0";
    } else {
      els.win.textContent = `+${w} / -${b}`;
    }

    els.betAmount.textContent = String(state.bet);
  }

  function buildPayTable() {
    els.payTable.innerHTML = "";
    [...SYMBOLS].reverse().forEach((s) => {
      const div = document.createElement("div");
      div.className = "pay-item";
      div.innerHTML = `
        <img class="pay-img" src="${imgOf(s.id)}" onerror="this.src='https://via.placeholder.com/26?text=?'">
        <div class="pay-name">${s.name}</div>
        <div class="pay-mul">x${s.payout}</div>
      `;
      els.payTable.appendChild(div);
    });
  }

  // ---------- Reel visuals ----------
  function randomSymbolId() {
    return SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)].id;
  }

  function stripHtml(count, loop = false) {
    const n = loop ? Math.max(count, 22) : count;
    let html = "";
    for (let i = 0; i < n; i++) {
      const id = randomSymbolId();
      html += `<div class="symbol"><img src="${imgOf(id)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>`;
    }
    if (loop) {
      for (let i = 0; i < n; i++) {
        const id = randomSymbolId();
        html += `<div class="symbol"><img src="${imgOf(id)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>`;
      }
    }
    return html;
  }

  function initReels() {
    for (let i = 0; i < 5; i++) {
      const strip = els.reels[i];
      strip.innerHTML = stripHtml(3, false);
      strip.style.transform = "translateY(0)";
      strip.classList.remove("spinning");
    }
  }

  function startSpinVisual() {
    for (let i = 0; i < 5; i++) {
      const strip = els.reels[i];
      strip.innerHTML = stripHtml(22, true);
      strip.classList.add("spinning");
      strip.style.animationDelay = `${i * 0.08}s`;
      strip.style.transform = "translateY(0)";
    }
  }

  function stopReel(i, final3) {
    const strip = els.reels[i];
    strip.classList.remove("spinning");

    const top = final3[0] || randomSymbolId();
    const mid = final3[1] || randomSymbolId();
    const bot = final3[2] || randomSymbolId();

    strip.innerHTML = `
      <div class="symbol"><img src="${imgOf(top)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
      <div class="symbol"><img src="${imgOf(mid)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
      <div class="symbol"><img src="${imgOf(bot)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
    `;
    strip.style.transform = "translateY(0)";
  }

  // ---------- Controls ----------
  function changeBet(delta) {
    if (state.spinning) return;
    const next = Math.max(state.betMin, Math.min(state.betMax, state.bet + delta));
    const step = Math.max(1, state.betStep);
    const aligned = Math.round(next / step) * step;
    state.bet = Math.max(state.betMin, Math.min(state.betMax, aligned));
    S.audio?.playOne?.("start");
    updateUI();
  }

  async function spinOnce() {
    if (state.spinning) return;
    state.spinning = true;

    els.spinBtn.disabled = true;
    els.payline.classList.remove("show");

    state.lastWin = 0;
    state.lastBet = Math.floor(Number(state.bet || 0));
    updateUI();

    S.audio?.unlockAudio?.();
    S.audio?.playOne?.("start");

    hint("Spinning... 숨참기 😈");
    startSpinVisual();
    S.audio?.startSpinSound?.();

    let out;
    try {
      out = await api.spin(state.bet);
      if (!out || !out.ok) throw new Error(out?.error || "spin_failed");
    } catch (e) {
      S.audio?.stopSpinSound?.();
      initReels();
      state.spinning = false;
      els.spinBtn.disabled = false;

      hint("에러났음. (이름/아이디/시트 매칭) 확인 ㄱㄱ");
      alert("Spin Error: " + (e?.message || e));
      if (state.auto) setAuto(false);
      return;
    }

    // 서버 반영
    if (out.displayName) state.displayName = out.displayName;
    if (out.ut != null) state.ut = Number(out.ut);
    if (out.jackpot != null) state.jackpot = Number(out.jackpot);

    const grid = out.grid;
    const win = Math.floor(Number(out.win || 0));
    state.lastWin = win;

    await new Promise((r) => setTimeout(r, 850));

    for (let i = 0; i < 5; i++) {
      await new Promise((r) => setTimeout(r, 230 + i * 160));
      const col3 = [grid?.[0]?.[i], grid?.[1]?.[i], grid?.[2]?.[i]];
      stopReel(i, col3);
      S.audio?.playStopTick?.();
    }

    S.audio?.stopSpinSound?.();
    updateUI();

    const wt = String(out.winType || "").toLowerCase();
    if (win > 0) {
      flashBg();
      els.payline.classList.add("show");

      if (wt.includes("jackpot")) {
        hint("잭팟! PRO10 터졌다 👑");
        S.audio?.playOne?.("jackpot");
      } else {
        hint("승리! UT 쌓이는 맛 🔥");
        S.audio?.playOne?.("win");
      }
    } else {
      hint("다음 판이 진짜다 😅");
      S.audio?.playOne?.("lose");
    }

    state.spinning = false;
    els.spinBtn.disabled = false;

    if (state.auto) {
      setTimeout(() => {
        if (!state.auto) return;
        if (Number(state.ut || 0) < Number(state.bet || 0)) {
          setAuto(false);
          hint("UT 부족. AUTO OFF");
          return;
        }
        spinOnce();
      }, 1200);
    }
  }

  async function boot() {
    if (!api || !api.getState) {
      hint("slot.api.js 로드가 먼저 필요함(스크립트 순서 확인)");
      return;
    }

    buildPayTable();
    initReels();

    els.betMinus.addEventListener("click", () => changeBet(-state.betStep));
    els.betPlus.addEventListener("click", () => changeBet(+state.betStep));

    els.autoBtn.addEventListener("click", () => {
      S.audio?.unlockAudio?.();
      S.audio?.playOne?.("start");
      setAuto(!state.auto);
      if (state.auto && !state.spinning) spinOnce();
    });

    els.spinBtn.addEventListener("click", () => spinOnce());

    hint("서버 상태 불러오는 중...");
    const st = await api.getState();

    if (!st || !st.ok) {
      const ident = api.getUserIdentity();
      hint(
        !ident.name
          ? "이름 정보가 없음. (회원가입 시 입력한 이름) 저장이 필요함."
          : "유저 상태를 못 불러옴. (이름/아이디가 시트에 있는지) 확인"
      );
      updateUI();
      return;
    }

    state.displayName = st.displayName || "";
    state.ut = st.ut != null ? Number(st.ut) : 0;
    state.jackpot = Number(st.jackpot || 0);

    const cfg = st.slot_config || {};
    state.bet = Number(st.bet || cfg.BET_UT || state.bet);
    state.betMin = Number(cfg.BET_MIN || state.betMin);
    state.betMax = Number(cfg.BET_MAX || state.betMax);
    state.betStep = Number(cfg.BET_STEP || state.betStep);
    state.bet = Math.max(state.betMin, Math.min(state.betMax, state.bet));

    updateUI();
    hint("준비 완료. SPIN 눌러라 😈");
  }

  window.addEventListener("load", boot);
})();
