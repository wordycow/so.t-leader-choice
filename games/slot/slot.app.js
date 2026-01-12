(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const UI = () => SLOT.ui;
  const API = () => SLOT.api;
  const GAME = () => SLOT.game;
  const CFG = () => SLOT.config;

  const state = {
    id: "",
    user: null,
    bet: 10,
    auto: false,
    sound: true,
    spinning: false,
  };

  function readLoginId() {
    const qs = new URLSearchParams(location.search);
    const idFromUrl = (qs.get("id") || "").trim().toLowerCase();
    if (idFromUrl) {
      localStorage.setItem("unique_user_id", idFromUrl);
      return idFromUrl;
    }
    return (localStorage.getItem("unique_user_id") || "").trim().toLowerCase();
  }

  function clampBet(n) {
    const b = CFG().BET;
    n = Math.floor(Number(n || 0));
    if (n < b.min) n = b.min;
    if (n > b.max) n = b.max;
    // step 스냅
    const step = Math.max(1, Number(b.step || 1));
    const snapped = Math.round(n / step) * step;
    return Math.min(b.max, Math.max(b.min, snapped));
  }

  function nextMidnightTs() {
    const d = new Date();
    d.setHours(24, 0, 0, 0);
    return d.getTime();
  }

  function saveJackpotBanner(text) {
    const payload = { text, exp: nextMidnightTs() };
    localStorage.setItem("slot_jackpot_banner", JSON.stringify(payload));
  }

  function loadJackpotBanner() {
    try {
      const raw = localStorage.getItem("slot_jackpot_banner");
      if (!raw) return null;
      const o = JSON.parse(raw);
      if (!o?.text || !o?.exp) return null;
      if (Date.now() > Number(o.exp)) return null;
      return o.text;
    } catch (_) {
      return null;
    }
  }

  async function sync() {
    const r = await API().getSlotState(state.id);
    state.user = r.user;

    UI().setPlayer(r.user);
    UI().setWallet(r.user.balance);
    UI().setJackpotPool(r.jackpotTotal);
    UI().setLast("READY");
  }

  function setBet(n) {
    state.bet = clampBet(n);
    UI().setBet(state.bet);
  }

  function setAuto(on) {
    state.auto = !!on;
    UI().setAuto(state.auto);
  }

  function setSound(on) {
    state.sound = !!on;
    UI().setSound(state.sound);
  }

  async function spinOnce() {
    if (state.spinning) return;
    state.spinning = true;
    UI().clearHit();
    UI().setButtonsDisabled(true);
    UI().setLast("SPINNING...");

    try {
      // ✅ 서버가 결과/키/정산을 결정
      const r = await API().slotSpin(state.id, state.bet);
      const keys = r.spin.keys;

      // 배경 랜덤(없어도 됨)
      const bgs = CFG().ASSETS.bg || [];
      if (bgs.length) UI().setBackground(bgs[Math.floor(Math.random() * bgs.length)]);

      await GAME().animateSpin(UI(), keys);

      // 가운데줄 연속 구간 하이라이트(표시용)
      const run = GAME().bestRun(keys);
      if (run.len >= 2) UI().setHit(run.indices);

      // 결과 표시
      const kind = r.spin.kind;
      const label =
        kind === "lose" ? "LOSE" :
        kind === "even" ? "EVEN" :
        kind === "win3" ? "WIN (3)" :
        kind === "win4" ? "WIN (4)" :
        kind === "mega" ? "MEGA" :
        kind === "jackpot" ? "JACKPOT" :
        String(kind || "RESULT");

      UI().setLast(`${label} | Δ ${r.spin.netDelta}`);

      // 잔액/풀 반영
      UI().setWallet(r.user.balance);
      UI().setJackpotPool(r.jackpotTotal);

      // ✅ 잭팟 배너(자정까지 유지)
      if (kind === "jackpot") {
        const displayName = state.user?.nickname || state.user?.name || state.user?.id || "누군가";
        const text = `${displayName}님이 잭팟이 터지셨습니다. 축하드립니다.`;
        saveJackpotBanner(text);
        UI().showBanner(text);
      }
    } catch (err) {
      UI().setLast(`ERROR: ${String(err?.message || err)}`);
    } finally {
      state.spinning = false;
      UI().setButtonsDisabled(false);
    }
  }

  function wire() {
    UI().el.betUp?.addEventListener("click", () => setBet(state.bet + CFG().BET.step));
    UI().el.betDown?.addEventListener("click", () => setBet(state.bet - CFG().BET.step));

    UI().el.autoBtn?.addEventListener("click", async () => {
      setAuto(!state.auto);
      if (state.auto && !state.spinning) {
        while (state.auto) {
          await spinOnce();
          await new Promise(r => setTimeout(r, 250));
        }
      }
    });

    UI().el.soundBtn?.addEventListener("click", () => {
      setSound(!state.sound);
      try { SLOT.audio?.setEnabled?.(state.sound); } catch(_) {}
    });

    UI().el.spinBtn?.addEventListener("click", () => spinOnce());

    UI().el.payToggle?.addEventListener("click", () => {
      // 간단 토글
      const wrap = UI().el.payWrap;
      if (!wrap) return;
      wrap.classList.toggle("hidden");
    });
  }

  async function boot() {
    UI().init();
    UI().makeGrid();
    UI().renderPaytable();
    UI().hideOverlay();

    // banner 복원
    const banner = loadJackpotBanner();
    if (banner) UI().showBanner(banner);
    else UI().hideBanner();

    state.id = readLoginId();
    if (!state.id) {
      UI().showOverlay();
      return;
    }

    setBet(CFG().BET.default || 10);
    setAuto(false);
    setSound(true);

    wire();
    await sync();
  }

  SLOT.app = { boot };
})();
