// games/slot/slot.audio.js
window.SLOT = window.SLOT || {};
(function (S) {
  const audio = {};
  let enabled = true;
  let unlocked = false;

  // ✅ stop 사운드가 3초짜리여도 "틱"처럼 쓰기 위해 잘라서 재생
  const STOP_TICK_MS = 110; // 90~150 추천

  function src(name) {
    // games/slot.html 기준 sounds 폴더는 games/sounds/
    return `sounds/${name}.MP3`;
  }

  function makeAudio(name, { loop = false, volume = 1 } = {}) {
    const a = new Audio();
    a.src = src(name);
    a.loop = loop;
    a.volume = volume;
    a.preload = "auto";
    return a;
  }

  function init() {
    audio.start = makeAudio("start-button-sound", { volume: 0.9 });
    audio.win = makeAudio("win-sound", { volume: 0.9 });
    audio.lose = makeAudio("lose-sound", { volume: 0.9 });
    audio.jackpot = makeAudio("jackpot-sound", { volume: 1.0 });

    // spinning은 루프
    audio.spin = makeAudio("spining-sound", { loop: true, volume: 0.55 });

    // stop은 길어도 OK (틱 재생에서 잘라씀)
    audio.stop = makeAudio("stop-stop-stop-sound", { volume: 0.9 });
  }

  function unlockAudio() {
    if (unlocked) return;
    unlocked = true;

    const tryUnlock = (a) => {
      try {
        a.muted = true;
        const p = a.play();
        if (p && p.then) {
          p.then(() => {
            a.pause();
            a.currentTime = 0;
            a.muted = false;
          }).catch(() => {
            a.muted = false;
          });
        } else {
          a.pause();
          a.currentTime = 0;
          a.muted = false;
        }
      } catch (_) {}
    };
    Object.values(audio).forEach(tryUnlock);
  }

  function setEnabled(on) {
    enabled = !!on;
    if (!enabled) stopSpinSound();
  }

  function toggle() {
    setEnabled(!enabled);
    return enabled;
  }

  function playOne(key) {
    if (key === "stop") return playStopTick();
    if (!enabled) return;
    const a = audio[key];
    if (!a) return;

    try {
      a.currentTime = 0;
      a.play().catch(() => {});
    } catch (_) {}
  }

  function startSpinSound() {
    if (!enabled) return;
    try {
      audio.spin.currentTime = 0;
      audio.spin.play().catch(() => {});
    } catch (_) {}
  }

  function stopSpinSound() {
    try {
      audio.spin.pause();
      audio.spin.currentTime = 0;
    } catch (_) {}
  }

  function playStopTick() {
    if (!enabled) return;
    const base = audio.stop;
    if (!base) return;

    try {
      const a = base.cloneNode();
      a.volume = base.volume;
      a.currentTime = 0;

      a.play().catch(() => {});
      setTimeout(() => {
        try { a.pause(); a.currentTime = 0; } catch (_) {}
      }, STOP_TICK_MS);
    } catch (_) {}
  }

  init();

  S.audio = {
    unlockAudio,
    setEnabled,
    toggle,
    playOne,
    startSpinSound,
    stopSpinSound,
    playStopTick,
    _debug: { STOP_TICK_MS }
  };
})(window.SLOT);
