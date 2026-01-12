(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config || {};

  function qs() { return new URLSearchParams(location.search); }

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }

  function loadNum(key, def) {
    try {
      const v = localStorage.getItem(key);
      if (v == null) return def;
      const n = Number(v);
      return Number.isFinite(n) ? n : def;
    } catch (_) {
      return def;
    }
  }

  function saveNum(key, n) {
    try { localStorage.setItem(key, String(n)); } catch (_) {}
  }

  const keyBet = cfg.STORAGE_KEYS && cfg.STORAGE_KEYS.bet;
  const keyAuto = cfg.STORAGE_KEYS && cfg.STORAGE_KEYS.auto;

  SLOT.app = {
    state: {
      id: "",
      bet: loadNum(keyBet, (cfg.BET && cfg.BET.def) || 10),
      auto: (function(){
        try { return (localStorage.getItem(keyAuto) === "1"); } catch(_) { return false; }
      })(),
      spinning: false,
      timer: null
    },

    async boot() {
      SLOT.ui.init();
      SLOT.ui.loadPersistedBanner();

      // SCRIPT_URL 확인
      if (!cfg.SCRIPT_URL || !String(cfg.SCRIPT_URL).includes("/exec")) {
        SLOT.ui.showOverlayConfigMissing();
        return;
      }

      const id = (qs().get("id") || "").trim().toLowerCase();
      if (!id) {
        SLOT.ui.showLoginOverlayMissingId();
        return;
      }

      this.state.id = id;
      SLOT.ui.hideOverlay();

      // bet 세팅
      const betMin = (cfg.BET && cfg.BET.min) || 10;
      const betMax = (cfg.BET && cfg.BET.max) || 1000;
      const betStep = (cfg.BET && cfg.BET.step) || 5;

      this.state.bet = clamp(this.state.bet, betMin, betMax);
      // step 정렬(원치 않으면 제거 가능)
      this.state.bet = Math.round(this.state.bet / betStep) * betStep;

      SLOT.ui.setBet(this.state.bet);
      SLOT.ui.setLastResult("READY");

      // 버튼 바인딩
      this.bindControls();

      // 상태 로드
      await this.refreshState();

      // auto 복구
      this.updateAutoUi();
      if (this.state.auto) this.startAuto();
    },

    bindControls() {
      const betStep = (cfg.BET && cfg.BET.step) || 5;
      const betMin = (cfg.BET && cfg.BET.min) || 10;
      const betMax = (cfg.BET && cfg.BET.max) || 1000;

      const down = document.getElementById("betDown");
      const up = document.getElementById("betUp");
      const spin = document.getElementById("spinBtn");
      const auto = document.getElementById("autoBtn");
      const sound = document.getElementById("soundBtn");

      if (down) down.addEventListener("click", () => {
        this.state.bet = clamp(this.state.bet - betStep, betMin, betMax);
        SLOT.ui.setBet(this.state.bet);
        saveNum(keyBet, this.state.bet);
      });

      if (up) up.addEventListener("click", () => {
        this.state.bet = clamp(this.state.bet + betStep, betMin, betMax);
        SLOT.ui.setBet(this.state.bet);
        saveNum(keyBet, this.state.bet);
      });

      if (spin) spin.addEventListener("click", () => this.spinOnce());

      if (auto) auto.addEventListener("click", () => {
        this.state.auto = !this.state.auto;
        try { localStorage.setItem(keyAuto, this.state.auto ? "1" : "0"); } catch(_) {}
        this.updateAutoUi();
        if (this.state.auto) this.startAuto();
        else this.stopAuto();
      });

      if (sound) {
        // 초기 표시
        sound.textContent = (SLOT.audio && SLOT.audio.isOn) ? "SOUND ON" : "SOUND OFF";
        sound.addEventListener("click", () => {
          const on = SLOT.audio.toggle();
          sound.textContent = on ? "SOUND ON" : "SOUND OFF";
        });
      }
    },

    updateAutoUi() {
      const auto = document.getElementById("autoBtn");
      if (auto) auto.textContent = this.state.auto ? "AUTO ON" : "AUTO OFF";
    },

    startAuto() {
      if (this.state.timer) return;
      this.state.timer = setInterval(() => {
        // 너무 빨리 돌리면 서버/시트 부담. 1.2초 텀
        this.spinOnce();
      }, 1200);
    },

    stopAuto() {
      if (!this.state.timer) return;
      clearInterval(this.state.timer);
      this.state.timer = null;
    },

    async refreshState() {
      const res = await SLOT.api.getSlotState(this.state.id);
      if (!res || !res.ok) {
        console.error("[SLOT] getSlotState failed:", res);
        // UI에 에러문구 박지 말고 READY 유지
        SLOT.ui.setLastResult("READY");
        return;
      }

      const u = res.user || {};
      SLOT.ui.setPlayer(u.nickname || u.name || u.id || "-");
      SLOT.ui.setWallet(u.balance || 0);
      SLOT.ui.setJackpotPool(res.jackpotTotal || 0);
      SLOT.ui.setLastResult("READY");
    },

    async spinOnce() {
      if (this.state.spinning) return;
      this.state.spinning = true;

      try {
        SLOT.ui.setLastResult("SPINNING...");

        const res = await SLOT.api.slotSpin(this.state.id, this.state.bet);
        if (!res || !res.ok) {
          console.error("[SLOT] slotSpin failed:", res);
          SLOT.ui.setLastResult("READY");
          return;
        }

        const spin = res.spin || {};
        const user = res.user || {};

        SLOT.ui.setWallet(user.balance || 0);
        SLOT.ui.setJackpotPool(res.jackpotTotal || 0);

        // 결과 문구(원하면 더 세분화 가능)
        let msg = "READY";
        if (spin.kind === "lose") msg = "LOSE";
        else if (spin.kind === "even") msg = "EVEN";
        else if (spin.kind === "win3") msg = `WIN (x3) +${spin.netDelta || 0}`;
        else if (spin.kind === "win4") msg = `WIN (x10) +${spin.netDelta || 0}`;
        else if (spin.kind === "mega") msg = `MEGA (x25) +${spin.netDelta || 0}`;
        else if (spin.kind === "jackpot") msg = `JACKPOT +${spin.netDelta || 0}`;

        SLOT.ui.setLastResult(msg);

        // 그리드 반영
        if (Array.isArray(spin.keys)) {
          SLOT.game.applySpin(spin.keys);
        }

        // 잭팟 배너(자정까지 유지)
        if (spin.kind === "jackpot") {
          const player = document.getElementById("playerName")?.textContent || this.state.id;
          const bannerMsg = `${player}님이 잭팟이 터지셨습니다. 축하드립니다.`;
          SLOT.ui.showBanner(bannerMsg);
          SLOT.ui.persistBannerUntilMidnight(bannerMsg);
        }
      } finally {
        this.state.spinning = false;
      }
    }
  };
})();
