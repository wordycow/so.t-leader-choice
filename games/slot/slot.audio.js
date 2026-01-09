/* global window */
(() => {
  const C = window.SLOT?.CONFIG || {};
  const SOUND_BASE = (C.SOUND_BASE || "sounds/"); // /games/sounds/

  const AudioMgr = {
    enabled: true,
    unlocked: false,
    sounds: {},

    init() {
      const saved = localStorage.getItem(C?.LS?.SOUND || "slot_sound_on");
      this.enabled = saved === null ? true : saved === "1";
      return this.enabled;
    },

    setEnabled(on) {
      this.enabled = !!on;
      localStorage.setItem(C?.LS?.SOUND || "slot_sound_on", this.enabled ? "1" : "0");
    },

    unlockOnce() {
      if (this.unlocked) return;
      this.unlocked = true;

      // iOS 오디오 정책: 유저 제스처 이후에만 재생 가능
      try {
        const a = new Audio();
        a.muted = true;
        a.play().catch(() => {});
      } catch (_) {}
    },

    _make(name, fileExact) {
      const url = `${SOUND_BASE}${fileExact}`;
      const a = new Audio(url);
      a.preload = "auto";
      a.addEventListener("error", () => {
        // 404여도 게임이 죽지 않게 조용히 무시
        this.sounds[name] = null;
      });
      this.sounds[name] = a;
    },

    preload() {
      // ✅ 너의 실제 파일명(대문자 .MP3) 그대로만 요청한다.
      //    (GitHub Pages는 대소문자 구분 + 철자도 구분)
      this._make("click",   "start-button-sound.MP3");
      this._make("spin",    "spining-sound.MP3");      // ✅ 철자 "spining" 그대로
      this._make("stop",    "stop-stop-stop-sound.MP3");
      this._make("win",     "win-sound.MP3");
      this._make("lose",    "lose-sound.MP3");
      this._make("jackpot", "jackpot-sound.MP3");
    },

    play(name) {
      if (!this.enabled) return;
      if (!this.unlocked) return; // 유저 클릭 전 재생 금지 (iOS)
      const a = this.sounds[name];
      if (!a) return;

      try {
        a.currentTime = 0;
        a.play().catch(() => {});
      } catch (_) {}
    },
  };

  window.SLOT = window.SLOT || {};
  window.SLOT.Audio = AudioMgr;
})();
