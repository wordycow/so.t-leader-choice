(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const C = () => SLOT.config;

  function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }

  function getIdFromUrl() {
    const u = new URL(location.href);
    const id = (u.searchParams.get("id") || "").trim().toLowerCase();
    return id || "";
  }

  function getBet() {
    const def = C().BET.def;
    try {
      const v = Number(localStorage.getItem(C().STORAGE_KEYS.bet));
      if (Number.isFinite(v)) return clamp(v, C().BET.min, C().BET.max);
    } catch (_) {}
    return def;
  }

  function setBet(v) {
    const n = clamp(Math.round(v), C().BET.min, C().BET.max);
    SLOT.ui.setBet(n);
    try { localStorage.setItem(C().STORAGE_KEYS.bet, String(n)); } catch (_) {}
    return n;
  }

  function getAutoOn() {
    try { return localStorage.getItem(C().STORAGE_KEYS.auto) === "1"; }
    catch (_) { return false; }
  }
  function setAutoOn(v) {
    const on = !!v;
    try { localStorage.setItem(C().STORAGE_KEYS.auto, on ? "1" : "0"); } catch (_) {}
    return on;
  }

  // ✅ 자정까지 유지되는 잭팟 배너
  function nextMidnightTs() {
    const d = new Date();
    d.setHours(24, 0, 0, 0);
    return d.getTime();
  }

  function saveBanner(text) {
    const payload = { text, expiresAt: nextMidnightTs() };
    try { localStorage.setItem(C().STORAGE_KEYS.banner, JSON.stringify(payload)); } catch (_) {}
  }

  function loadBanner() {
    try {
      const raw = localStorage.getItem(C().STORAGE_KEYS.banner);
      if (!raw) return null;
      const obj = JSON.parse(raw);
      if (!obj || !obj.text || !obj.expiresAt) return null;
      if (Date.now() > Number(obj.expiresAt)) return null;
      return obj;
    } catch (_) {
      return null;
    }
  }

  async function boot() {
    SLOT.ui.init();

    const id = getIdFromUrl();
    if (!id) {
      SLOT.ui.showLoginOverlay(true);
      return;
    }
    SLOT.ui.showLoginOverlay(false);

    // 버튼 라벨 초기화
    const els = SLOT.ui.els();
    els.autoBtn.textContent = getAutoOn() ? "AUTO ON" : "AUTO OFF";
    els.soundBtn.textContent = SLOT.audio.getSoundOn() ? "SOUND ON" : "SOUND OFF";

    // 베팅값 복원
    let bet = setBet(getBet());

    // 잭팟 배너 복원
    const banner = loadBanner();
    if (banner) SLOT.ui.showJackpotBanner(banner.text);

    // 슬롯 상태 불러오기
    try {
      SLOT.ui.setLastResult("LOADING...");
      const state = await SLOT.api.getSlotState(id);
      if (!state?.ok) throw new Error(state?.error || "getSlotState_failed");

      const user = state.user || {};
      SLOT.ui.setPlayer(user.name || user.nickname || id);
      SLOT.ui.setWallet(user.balance ?? 0);
      SLOT.ui.setJackpotPool(state.jackpotTotal ?? 0);
      SLOT.ui.setLastResult("READY");
    } catch (e) {
      SLOT.ui.setLastResult(`ERROR: ${e.message}`);
      return;
    }

    // 베팅 버튼
    els.betDown.addEventListener("click", () => {
      bet = setBet(bet - C().BET.step);
    });
    els.betUp.addEventListener("click", () => {
      bet = setBet(bet + C().BET.step);
    });

    // 오토
    els.autoBtn.addEventListener("click", () => {
      const on = setAutoOn(!getAutoOn());
      els.autoBtn.textContent = on ? "AUTO ON" : "AUTO OFF";
    });

    // 사운드
    els.soundBtn.addEventListener("click", () => {
      const on = SLOT.audio.setSoundOn(!SLOT.audio.getSoundOn());
      els.soundBtn.textContent = on ? "SOUND ON" : "SOUND OFF";
    });

    // 스핀
    let spinning = false;

    async function doSpinOnce() {
      if (spinning) return;
      spinning = true;
      SLOT.ui.setButtonsEnabled(false);
      SLOT.ui.setLastResult("SPINNING...");

      try {
        const res = await SLOT.api.slotSpin(id, bet);
        if (!res?.ok) throw new Error(res?.error || "slotSpin_failed");

        const spin = res.spin || {};
        const user = res.user || {};

        // ✅ 스핀 애니메이션(배경 동기화 포함)
        await SLOT.game.animateSpin(spin.keys, C().SPIN.durationMs);

        // UI 업데이트
        SLOT.ui.setWallet(user.balance ?? 0);
        SLOT.ui.setJackpotPool(res.jackpotTotal ?? 0);

        const kind = String(spin.kind || "");
        const payout = spin.payout ?? 0;
        const fee = spin.fee ?? 0;
        const net = spin.netDelta ?? 0;

        SLOT.ui.setLastResult(`${kind.toUpperCase()} | payout ${payout} | fee ${fee} | net ${net}`);

        // ✅ 잭팟이면 티커(자정까지 유지)
        if (kind === "jackpot") {
          // 이름은 화면 PLAYER 기준(운영자 요구 문구)
          const playerText = SLOT.ui.els().playerName.textContent || "플레이어";
          const text = `${playerText}님이 잭팟이 터지셨습니다. 축하드립니다.`;
          saveBanner(text);
          SLOT.ui.showJackpotBanner(text);
        }
      } catch (e) {
        SLOT.ui.setLastResult(`ERROR: ${e.message}`);
      } finally {
        SLOT.ui.setButtonsEnabled(true);
        spinning = false;
      }

      // AUTO면 다음 스핀
      if (getAutoOn()) {
        setTimeout(() => { doSpinOnce(); }, 250);
      }
    }

    els.spinBtn.addEventListener("click", doSpinOnce);
  }

  SLOT.app = { boot };
})();
