(function () {
  const S = (window.S = window.S || {});
  S.audio = S.audio || {};

  let enabled = true;
  let unlocked = false;
  const aud = {};

  function safeCreate(src) {
    try {
      const a = new Audio(src);
      a.preload = "auto";
      return a;
    } catch (_) {
      return null;
    }
  }

  function init() {
    const cfg = S.CONFIG?.SOUNDS || {};
    aud.start = safeCreate(cfg.start);
    aud.spin = safeCreate(cfg.spin);
    aud.stop = safeCreate(cfg.stop);
    aud.win = safeCreate(cfg.win);
    aud.lose = safeCreate(cfg.lose);
    aud.jackpot = safeCreate(cfg.jackpot);

    if (aud.spin) aud.spin.loop = true;

    // ✅ 모바일 오디오 잠금 해제: 첫 사용자 터치에 한 번만
    const unlock = () => {
      if (unlocked) return;
      unlocked = true;
      Object.values(aud).forEach((a) => {
        if (!a) return;
        try {
          a.muted = true;
          a.play().then(() => {
            a.pause();
            a.currentTime = 0;
            a.muted = false;
          }).catch(() => {
            a.muted = false;
          });
        } catch (_) {}
      });
      window.removeEventListener("pointerdown", unlock);
      window.removeEventListener("touchstart", unlock);
    };
    window.addEventListener("pointerdown", unlock, { once: true });
    window.addEventListener("touchstart", unlock, { once: true });
  }

  function setEnabled(v) {
    enabled = !!v;
    try { localStorage.setItem("slot_sound", enabled ? "1" : "0"); } catch (_) {}
  }

  function loadEnabled() {
    try {
      const v = localStorage.getItem("slot_sound");
      if (v === "0") enabled = false;
    } catch (_) {}
    return enabled;
  }

  function stopSpin() {
    if (aud.spin) {
      try { aud.spin.pause(); aud.spin.currentTime = 0; } catch (_) {}
    }
  }

  function play(name) {
    if (!enabled) return;
    const a = aud[name];
    if (!a) return;
    try {
      if (name !== "spin") a.currentTime = 0;
      a.play().catch(() => {});
    } catch (_) {}
  }

  S.audio.init = init;
  S.audio.play = play;
  S.audio.stopSpin = stopSpin;
  S.audio.setEnabled = setEnabled;
  S.audio.loadEnabled = loadEnabled;
})();
