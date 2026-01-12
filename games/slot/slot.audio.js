(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const K = () => SLOT.config.STORAGE_KEYS;

  const SOUND_BASE = "./sounds"; // games/sounds

  // ✅ GitHub는 대소문자 구분: 파일명 그대로
  const FILES = {
    start:   `${SOUND_BASE}/start-button-sound.MP3`,
    spin:    `${SOUND_BASE}/spining-sound.MP3`,
    stop:    `${SOUND_BASE}/stop-stop-stop-sound.MP3`,
    win:     `${SOUND_BASE}/win-sound.MP3`,
    lose:    `${SOUND_BASE}/lose-sound.MP3`,
    jackpot: `${SOUND_BASE}/jackpot-sound.MP3`,
  };

  const aud = {};
  let enabled = true;
  let unlocked = false;

  function loadAll() {
    Object.entries(FILES).forEach(([k, src]) => {
      const a = new Audio(src);
      a.preload = "auto";
      aud[k] = a;
    });
    // spin은 루프
    aud.spin.loop = true;
  }

  function readEnabled() {
    const v = localStorage.getItem(K().sound);
    if (v === null) return true;
    return v === "1";
  }

  function setEnabled(on) {
    enabled = !!on;
    localStorage.setItem(K().sound, enabled ? "1" : "0");
    if (!enabled) stopAll();
  }

  async function unlock() {
    if (unlocked) return true;
    try {
      // 모바일 정책: 유저 제스처에서 1회 재생 시도 필요
      const a = aud.start;
      a.volume = 0.001;
      await a.play();
      a.pause();
      a.currentTime = 0;
      a.volume = 1;
      unlocked = true;
      return true;
    } catch (_) {
      // 조용히 실패(브라우저 정책)
      return false;
    }
  }

  function stopAll() {
    Object.values(aud).forEach(a => {
      try { a.pause(); a.currentTime = 0; } catch(_) {}
    });
  }

  async function play(name, { loop=false, volume=1 } = {}) {
    if (!enabled) return;
    const a = aud[name];
    if (!a) return;
    try {
      a.loop = !!loop;
      a.volume = volume;
      a.currentTime = 0;
      await a.play();
    } catch (_) {
      // 정책/상태로 막혀도 UI는 계속 진행
    }
  }

  function stop(name) {
    const a = aud[name];
    if (!a) return;
    try { a.pause(); a.currentTime = 0; } catch(_) {}
  }

  loadAll();
  enabled = readEnabled();

  SLOT.audio = { FILES, unlock, play, stop, stopAll, setEnabled, get enabled(){ return enabled; } };
})();
