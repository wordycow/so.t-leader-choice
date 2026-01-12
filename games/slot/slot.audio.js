(function () {
  window.SLOT = window.SLOT || {};
  const { ASSET } = window.SLOT.config;

  const AudioSys = {
    enabled: true,
    audio: null,
    init() {
      try {
        const a = {
          start: new Audio(ASSET.sndBase + ASSET.sound.start),
          spin:  new Audio(ASSET.sndBase + ASSET.sound.spin),
          stop:  new Audio(ASSET.sndBase + ASSET.sound.stop),
          win:   new Audio(ASSET.sndBase + ASSET.sound.win),
          lose:  new Audio(ASSET.sndBase + ASSET.sound.lose),
          jackpot:new Audio(ASSET.sndBase + ASSET.sound.jackpot),
        };
        a.spin.loop = true;
        this.audio = a;
        this.apply();
      } catch (_) {
        this.enabled = false;
        this.audio = null;
      }
    },
    setEnabled(on) {
      this.enabled = !!on;
      this.apply();
    },
    apply() {
      if (!this.audio) return;
      const vol = this.enabled ? 1 : 0;
      for (const k of Object.keys(this.audio)) {
        try { this.audio[k].volume = vol; } catch(_){}
      }
    },
    play(name) {
      if (!this.audio || !this.enabled) return;
      const a = this.audio[name];
      if (!a) return;
      try { a.currentTime = 0; a.play().catch(()=>{}); } catch(_){}
    },
    spinLoop(on) {
      if (!this.audio) return;
      const a = this.audio.spin;
      if (!a) return;
      try {
        if (on) { a.currentTime = 0; a.play().catch(()=>{}); }
        else { a.pause(); a.currentTime = 0; }
      } catch(_){}
    }
  };

  window.SLOT.audio = AudioSys;
})();
