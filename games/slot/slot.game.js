(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const C = () => SLOT.config;

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  async function animateSpin(finalKeys, durationMs) {
    const total = C().GRID.rows * C().GRID.cols;
    if (!Array.isArray(finalKeys) || finalKeys.length !== total) {
      // 키가 이상하면 그냥 랜덤으로라도 표시
      finalKeys = Array.from({ length: total }, () => C().SYMBOLS[(Math.random() * C().SYMBOLS.length) | 0].key);
    }

    const dur = Math.max(600, Math.floor(durationMs || C().SPIN.durationMs || 1600));
    // 그리드 난수 갱신 간격 = 스핀 속도 느낌
    const tickMs = Math.max(60, Math.min(250, Math.floor(dur / 18)));
    // ✅ 배경은 스핀 속도랑 같이(최소 200ms)
    const bgMs = Math.max(Number(C().SPIN.minBgIntervalMs || 200), tickMs);

    SLOT.ui.startBgCycle(bgMs);

    const start = Date.now();
    while (Date.now() - start < dur) {
      SLOT.ui.randomGrid();
      await sleep(tickMs);
    }

    SLOT.ui.stopBgCycle();
    SLOT.ui.setGridKeys(finalKeys);
  }

  SLOT.game = {
    animateSpin,
  };
})();
