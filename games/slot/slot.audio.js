(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const C = () => SLOT.config || {};
  const K = () => (C().STORAGE_KEYS ? C().STORAGE_KEYS.sound : "slot_sound_on");

  let enabled = true;
  let unlocked = false;

  const aud = {
    start: null,
    spinning: null,
    stop: null,
    win: null,
    lose: null,
    jackpot: null,
  };

  function loadAudio(name, file, { loop = false, volume = 0.9 } = {}) {
    const base = C().SOUND?.base || "./sounds";
    const url = `${base}/${file}`;
    const a = new Audio(url);
    a.preload = "auto";
    a.loop = loop;
    a.volume = volume;
    return a;
  }

  function init() {
    // localStorage
    try {
      const v = localStorage.getItem(K());
      enabled = v === null ? true : v === "1";
    } catch (_) {}

    const files = C().SOUND?.files || {};
    aud.start = loadAudio("start", files.start || "start-button-sound.MP3", { loop: false, volume: 0.9 });
    aud.spinning = loadAudio("spinning", files.spinning || "spinning-sound.MP3", { loop: true, volume: 0.7 });
    aud.stop = loadAudio("stop", files.stop || "stop-stop-stop-sound.MP3", { loop: false, volume: 0.85 });
    aud.win = loadAudio("win", files.win || "win-sound.MP3", { loop: false, volume: 0.9 });
    aud.lose = loadAudio("lose", files.lose || "lose-sound.MP3", { loop: false, volume: 0.9 });
    aud.jackpot = loadAudio("jackpot", files.jackpot || "jackpot-sound.MP3", { loop: false, volume: 1.0 });

    bindSoundButton();
    bindUnlockOnce();
    refreshSoundBtnText();
  }

  function bindUnlockOnce() {
    const unlockOnce = () => {
      unlock();
      window.removeEventListener("pointerdown", unlockOnce);
      window.removeEventListener("keydown", unlockOnce);
    };
    window.addEventListener("pointerdown", unlockOnce, { once: true, passive: true });
    window.addEventListener("keydown", unlockOnce, { once: true });
  }

  function unlock() {
    if (unlocked) return;
    unlocked = true;

    // “한 번 재생 시도”로 오디오 정책 해제 유도
    try {
      const a = aud.start;
      if (!a) return;
      const prevMuted = a.muted;
      a.muted = true;
      const p = a.play();
      if (p && typeof p.then === "function") {
        p.then(() => {
          a.pause();
          a.currentTime = 0;
          a.muted = prevMuted;
        }).catch(() => {
          a.muted = prevMuted;
        });
      } else {
        a.muted = prevMuted;
      }
    } catch (_) {}
  }

  function setEnabled(on) {
    enabled = !!on;
    try {
      localStorage.setItem(K(), enabled ? "1" : "0");
    } catch (_) {}

    if (!enabled) stopSpinning();
    refreshSoundBtnText();
  }

  function isEnabled() {
    return enabled;
  }

  function playOne(a) {
    if (!enabled || !a) return;
    try {
      a.currentTime = 0;
      const p = a.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch (_) {}
  }

  function startSpinning() {
    if (!enabled || !aud.spinning) return;
    try {
      const p = aud.spinning.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    } catch (_) {}
  }

  function stopSpinning() {
    const a = aud.spinning;
    if (!a) return;
    try {
      a.pause();
      a.currentTime = 0;
    } catch (_) {}
  }

  function bindSoundButton() {
    const btn = document.getElementById("soundBtn");
    if (!btn) return;

    btn.addEventListener("click", () => {
      unlock();
      setEnabled(!enabled);
    });
  }

  function refreshSoundBtnText() {
    const btn = document.getElementById("soundBtn");
    if (!btn) return;
    btn.textContent = enabled ? "SOUND ON" : "SOUND OFF";
  }

  // 외부에서 쓰기 좋은 API
  SLOT.audio = {
    init,
    unlock,
    setEnabled,
    isEnabled,

    playStart: () => playOne(aud.start),
    playStop: () => playOne(aud.stop),
    playWin: () => playOne(aud.win),
    playLose: () => playOne(aud.lose),
    playJackpot: () => playOne(aud.jackpot),

    startSpinning,
    stopSpinning,
  };
})();
