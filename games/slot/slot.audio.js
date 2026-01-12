(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const C = () => SLOT.config;

  function getSoundOn() {
    try { return localStorage.getItem(C().STORAGE_KEYS.sound) !== "0"; }
    catch (_) { return true; }
  }

  function setSoundOn(v) {
    const on = !!v;
    try { localStorage.setItem(C().STORAGE_KEYS.sound, on ? "1" : "0"); } catch(_) {}
    return on;
  }

  SLOT.audio = {
    getSoundOn,
    setSoundOn,
    // 필요하면 여기에 효과음 추가
    playClick() {},
    playSpin() {},
    playWin() {},
  };
})();
