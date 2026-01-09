// games/slot/slot.audio.js
window.SLOT = window.SLOT || {};
(function (S) {
  const audio = {};
  let enabled = true;
  let unlocked = false;

  // ✅ stop 사운드(긴 MP3)를 "틱"처럼 쓰기 위해 잘라서 재생
  const STOP_TICK_MS = 110; // 90~180 사이 취향 조절

  function src(name) {
    // slot.html이 games/ 아래 → sounds 폴더는 games/sounds/
    // 파일 확장자는 전부 .MP3 (대문자)
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
    // ✅ 실제 파일명 매핑 (확장자/대소문자 주의: .MP3)
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
    if (!enabled) stopSpinSound();
  }

  function toggle() {
    setEnabled(!enabled);
    return enabled;
  }

  // ✅ 어디서 playOne("stop") 호출하든 자동으로 틱 처리
  function playOne(key) {
    if (!enabled) return;
    if (key === "stop") return playStopTick();

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
      // cloneNode로 겹쳐도 자연스럽게 (릴 5개 연속 멈춤 대응)
      const a = base.cloneNode();
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
