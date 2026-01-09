// games/slot/slot_audio.js
window.SLOT = window.SLOT || {};
(function (S) {

  const BASE = "sounds/"; // /games/sounds/

  // ✅ 너의 실제 파일명 그대로(대문자 .MP3 + 철자 포함)
  const FILES = {
    start:   "start-button-sound.MP3",
    spin:    "spining-sound.MP3",       // ⚠️ 파일명이 spining 이면 그대로 써야함
    stop:    "stop-stop-stop-sound.MP3",
    win:     "win-sound.MP3",
    lose:    "lose-sound.MP3",
    jackpot: "jackpot-sound.MP3",
  };

  const audio = {};
  let enabled = true;
  let unlocked = false;
  let spinLoop = null;

  function loadOne(key) {
    const a = new Audio(BASE + FILES[key]);
    a.preload = "auto";
    a.addEventListener("error", () => {
      // 404여도 게임은 계속 돌게(사운드만 무시)
      audio[key] = null;
    });
    audio[key] = a;
  }

  function preload() {
    Object.keys(FILES).forEach(loadOne);
    // spin 루프는 별도(Audio loop)
    const s = new Audio(BASE + FILES.spin);
    s.preload = "auto";
    s.loop = true;
    spinLoop = s;
  }

  function play(key) {
    if (!enabled || !unlocked) return;
    const a = audio[key];
    if (!a) return;
    try {
      a.currentTime = 0;
      a.play().catch(() => {});
    } catch (_) {}
  }

  function startSpinSound() {
    if (!enabled || !unlocked || !spinLoop) return;
    try {
      spinLoop.currentTime = 0;
      spinLoop.play().catch(() => {});
    } catch (_) {}
  }

  function stopSpinSound() {
    if (!spinLoop) return;
    try {
      spinLoop.pause();
      spinLoop.currentTime = 0;
    } catch (_) {}
  }

  function unlockAudio() {
    if (unlocked) return;
    unlocked = true;

    // iOS: 유저 제스처 이후에만 가능
    try {
      const a = new Audio(BASE + FILES.start);
      a.muted = true;
      a.play().then(() => {
        a.pause();
        a.currentTime = 0;
        a.muted = false;
      }).catch(() => {});
    } catch (_) {}
  }

  function setEnabled(on) {
    enabled = !!on;
    localStorage.setItem("slot_sound_on", enabled ? "1" : "0");
    if (!enabled) stopSpinSound();
  }

  function getEnabled() {
    const saved = localStorage.getItem("slot_sound_on");
    enabled = (saved === null) ? true : saved === "1";
    return enabled;
  }

  // public API (slot_app.js가 쓰는 이름 유지)
  S.audio = {
    preload,
    unlockAudio,
    playOne: play,
    startSpinSound,
    stopSpinSound,
    setEnabled,
    getEnabled,
  };

})(window.SLOT);
