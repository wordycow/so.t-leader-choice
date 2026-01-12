/* games/slot/slot.app.js */
(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config;

  const state = {
    id: "",
    bet: cfg.SPIN.betDefault,
    spinning: false,
  };

  function clampBet(b) {
    b = Math.floor(Number(b) || cfg.SPIN.betDefault);
    if (b < cfg.SPIN.betMin) b = cfg.SPIN.betMin;
    if (b > cfg.SPIN.betMax) b = cfg.SPIN.betMax;
    // step 맞추기
    const step = cfg.SPIN.betStep || 10;
    b = Math.round(b / step) * step;
    return b;
  }

  async function init(userId) {
    state.id = String(userId || "").trim().toLowerCase();
    if (!state.id) throw new Error("missing id");

    // 저장된 bet 복원
    const savedBet = localStorage.getItem(cfg.STORAGE.bet);
    state.bet = clampBet(savedBet || state.bet);

    SLOT.ui.setBet(state.bet);
    localStorage.setItem(cfg.STORAGE.userId, state.id);

    // 서버에서 유저/풀 상태
    const r = await SLOT.api.call("getSlotState", { id: state.id });

    const u = r.user || {};
    SLOT.ui.setPlayer(u.nickname || u.name || u.id || "-");
    SLOT.ui.setWallet(u.balance || 0);
    SLOT.ui.setJackpotPool(r.jackpotTotal || 0);
    SLOT.ui.setLastResult("READY");
  }

  function changeBet(deltaSteps) {
    const step = cfg.SPIN.betStep || 10;
    state.bet = clampBet(state.bet + deltaSteps * step);
    SLOT.ui.setBet(state.bet);
    localStorage.setItem(cfg.STORAGE.bet, String(state.bet));
  }

  async function spin() {
    if (state.spinning) return;
    state.spinning = true;

    try {
      SLOT.ui.setLastResult("SPINNING...");
      const r = await SLOT.api.call("slotSpin", { id: state.id, bet: state.bet });

      const spin = r.spin || {};
      const keys = spin.keys || [];

      SLOT.ui.renderGrid(keys);

      // 결과 표시
      const kind = spin.kind || "lose";
      const payout = Number(spin.payout || 0);
      const fee = Number(spin.fee || 0);
      const net = Number(spin.netDelta || 0);

      // 지갑/풀 업데이트
      SLOT.ui.setWallet(r.user?.balance || 0);
      SLOT.ui.setJackpotPool(r.jackpotTotal || 0);

      if (kind === "jackpot") {
        SLOT.ui.setLastResult(`JACKPOT! +${net} (payout:${payout}, fee:${fee})`);
        SLOT.ui.setJackpotBanner(`${state.id}님이 잭팟이 터지셨습니다. 축하드립니다.`);
      } else if (kind === "even") {
        SLOT.ui.setLastResult(`EVEN (fee:-${fee})`);
      } else if (kind === "win3" || kind === "win4" || kind === "mega") {
        SLOT.ui.setLastResult(`${kind.toUpperCase()} +${net} (payout:${payout})`);
      } else {
        SLOT.ui.setLastResult(`LOSE ${net} (fee:-${fee})`);
      }
    } finally {
      state.spinning = false;
    }
  }

  SLOT.app = { init, spin, changeBet };
})();
