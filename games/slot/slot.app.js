(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;
  const $ = (id) => document.getElementById(id);

  const dom = {
    betUt: $("betUt"),
    betDown: $("betDown"),
    betUp: $("betUp"),
    autoBtn: $("autoBtn"),
    soundBtn: $("soundBtn"),
    spinBtn: $("spinBtn"),
  };

  const state = {
    id: "",
    bet: 10,
    auto: false,
    sound: true,
    spinning: false,
  };

  function clampBet(n) {
    const { min, max, step } = CFG().BET;
    const v = Math.max(min, Math.min(max, n));
    // step 단위로 정렬
    const snapped = Math.round(v / step) * step;
    return Math.max(min, Math.min(max, snapped));
  }

  function setBet(n) {
    state.bet = clampBet(n);
    dom.betUt.textContent = String(state.bet);
    try { localStorage.setItem(CFG().STORAGE_KEYS.bet, String(state.bet)); } catch (_) {}
  }

  function loadLocal() {
    try {
      const b = Number(localStorage.getItem(CFG().STORAGE_KEYS.bet) || CFG().BET.def);
      state.bet = clampBet(b);
      state.auto = localStorage.getItem(CFG().STORAGE_KEYS.auto) === "1";
      state.sound = localStorage.getItem(CFG().STORAGE_KEYS.sound) !== "0";
    } catch (_) {
      state.bet = CFG().BET.def;
      state.auto = false;
      state.sound = true;
    }
    dom.betUt.textContent = String(state.bet);
    dom.autoBtn.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
    dom.soundBtn.textContent = state.sound ? "SOUND ON" : "SOUND OFF";
  }

  function setAuto(on) {
    state.auto = !!on;
    dom.autoBtn.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
    try { localStorage.setItem(CFG().STORAGE_KEYS.auto, state.auto ? "1" : "0"); } catch (_) {}
  }

  function setSound(on) {
    state.sound = !!on;
    dom.soundBtn.textContent = state.sound ? "SOUND ON" : "SOUND OFF";
    try { localStorage.setItem(CFG().STORAGE_KEYS.sound, state.sound ? "1" : "0"); } catch (_) {}
    SLOT.audio.setOn(state.sound);
  }

  function setSpinEnabled(on) {
    dom.spinBtn.disabled = !on;
    dom.betDown.disabled = !on;
    dom.betUp.disabled = !on;
  }

  async function refreshState() {
    const res = await SLOT.api.getSlotState(state.id);
    const user = res.user || {};
    SLOT.ui.setPlayer(user.nickname || user.name || user.id || "-");
    SLOT.ui.setWallet(user.balance || 0);
    SLOT.ui.setJackpotPool(res.jackpotTotal || 0);
    SLOT.ui.setLastResult("READY");
  }

  async function doSpinOnce() {
    if (state.spinning) return;
    state.spinning = true;
    setSpinEnabled(false);
    SLOT.ui.setLastResult("SPINNING...");

    try {
      const res = await SLOT.api.slotSpin(state.id, state.bet);
      const spin = res.spin || {};
      const keys = spin.keys || [];

      // 스핀 애니메이션(속도/배경 동기화)
      await SLOT.game.animateToKeys(keys, {
        durationMs: 1200,
        tickMs: 120
      });

      // 결과 표시
      const kind = String(spin.kind || "");
      if (kind === "lose") SLOT.ui.setLastResult("LOSE");
      else if (kind === "even") SLOT.ui.setLastResult("EVEN");
      else if (kind === "win3") SLOT.ui.setLastResult("WIN");
      else if (kind === "win4") SLOT.ui.setLastResult("BIG WIN");
      else if (kind === "mega") SLOT.ui.setLastResult("MEGA");
      else if (kind === "jackpot") SLOT.ui.setLastResult("JACKPOT!");
      else SLOT.ui.setLastResult("DONE");

      const user = res.user || {};
      SLOT.ui.setWallet(user.balance || 0);
      SLOT.ui.setJackpotPool(res.jackpotTotal || 0);

    } catch (e) {
      SLOT.ui.stopBgSpin();
      SLOT.ui.setLastResult("ERROR");
      console.error(e);
      alert(String(e.message || e));
    } finally {
      state.spinning = false;
      setSpinEnabled(true);
    }
  }

  function bind() {
    dom.betDown.addEventListener("click", () => setBet(state.bet - CFG().BET.step));
    dom.betUp.addEventListener("click", () => setBet(state.bet + CFG().BET.step));
    dom.autoBtn.addEventListener("click", () => setAuto(!state.auto));
    dom.soundBtn.addEventListener("click", () => setSound(!state.sound));

    dom.spinBtn.addEventListener("click", async () => {
      await doSpinOnce();
      if (state.auto) {
        // auto는 쉬지 않고 연속
        while (state.auto) {
          await new Promise(r => setTimeout(r, 200));
          await doSpinOnce();
        }
      }
    });
  }

  SLOT.app = {
    async boot(id) {
      state.id = String(id || "").trim().toLowerCase();
      if (!state.id) {
        SLOT.ui.showOverlay(true);
        return;
      }
      SLOT.ui.showOverlay(false);

      loadLocal();
      bind();
      await refreshState();
    }
  };
})();
