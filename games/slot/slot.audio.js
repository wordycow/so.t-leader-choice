// games/slot/slot.audio.js
window.SLOT = window.SLOT || {};
(function (S) {
  const audio = {};
  let enabled = true;
  let unlocked = false;

  // ✅ stop 사운드가 3초짜리여도 "틱"처럼 쓰기 위해 잘라서 재생
  const STOP_TICK_MS = 140; // 120~180 사이로 취향 조절 가능

  function src(name) {
    // games/slot.html 기준 sounds 폴더는 games/sounds/
    // (= slot.html이 games/ 아래에 있으니 "sounds/..."가 맞음)
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
    // 실제 파일명에 맞춰 매핑
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

    // iOS/모바일: 사용자 제스처 이후 한 번 play/pause로 언락
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
    if (!enabled) {
      stopSpinSound();
    }
  }

  function toggle() {
    setEnabled(!enabled);
    return enabled;
  }

  function playOne(key) {
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

  // ✅ 긴 STOP 파일을 "틱" 소리처럼 사용 (짧게 끊기)
  function playStopTick() {
    if (!enabled) return;
    const base = audio.stop;
    if (!base) return;

    try {
      const a = base.cloneNode(); // 겹쳐도 자연스럽게
      a.volume = base.volume;
      a.currentTime = 0;

      a.play().catch(() => {});
      setTimeout(() => {
        try {
          a.pause();
          a.currentTime = 0;
        } catch (_) {}
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
