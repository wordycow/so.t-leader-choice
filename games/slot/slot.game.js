(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  function randKey() {
    const syms = CFG().SYMBOLS || [];
    return syms[Math.floor(Math.random() * syms.length)].key;
  }

  async function animateToKeys(finalKeys, opts = {}) {
    const durationMs = Math.max(600, opts.durationMs || 1200);
    const tickMs = Math.max(50, opts.tickMs || 120); // 스핀 속도
    const minBgMs = 200; // ✅ “최소 속도일때 0.2초”
    const bgMs = Math.min(tickMs, minBgMs) ? Math.max(minBgMs, tickMs) : tickMs; // 안전

    // bg는 스핀 속도와 같게. 단, 느린 쪽 최소 0.2초(200ms)
    const bgInterval = Math.max(minBgMs, tickMs);

    SLOT.ui.startBgSpin(bgInterval);

    const start = Date.now();
    while (Date.now() - start < durationMs) {
      const keys = finalKeys.map(() => randKey());
      SLOT.ui.setKeys(keys);
      await new Promise(r => setTimeout(r, tickMs));
    }

    SLOT.ui.setKeys(finalKeys);
    SLOT.ui.stopBgSpin();
  }

  SLOT.game = {
    animateToKeys
  };
})();
