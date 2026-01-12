(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config || {};

  function loadBool(key, def) {
    try {
      const v = localStorage.getItem(key);
      if (v == null) return def;
      return v === "1";
    } catch (_) {
      return def;
    }
  }

  function saveBool(key, val) {
    try { localStorage.setItem(key, val ? "1" : "0"); } catch (_) {}
  }

  const keySound = cfg.STORAGE_KEYS && cfg.STORAGE_KEYS.sound;

  SLOT.audio = {
    isOn: loadBool(keySound, true),

    set(on) {
      this.isOn = !!on;
      saveBool(keySound, this.isOn);
    },

    toggle() {
      this.set(!this.isOn);
      return this.isOn;
    }
  };
})();
