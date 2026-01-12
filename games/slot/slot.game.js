(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  function pickWeighted() {
    const syms = CFG().SYMBOLS;
    const total = syms.reduce((a, s) => a + (Number(s.w) || 0), 0);
    let r = Math.random() * total;
    for (const s of syms) {
      r -= (Number(s.w) || 0);
      if (r <= 0) return s.key;
    }
    return syms[syms.length - 1].key;
  }

  function randomKeys() {
    const keys = [];
    for (let i = 0; i < 15; i++) keys.push(pickWeighted());
    return keys;
  }

  // 가운데줄(인덱스 5~9)에서 “최대 연속” 구간 찾기
  function bestRun(keys15) {
    const mid = keys15.slice(5, 10);
    let best = { key: mid[0], len: 1, start: 0 };

    let curKey = mid[0], curLen = 1, curStart = 0;
    for (let i = 1; i < mid.length; i++) {
      if (mid[i] === curKey) {
        curLen++;
      } else {
        if (curLen > best.len) best = { key: curKey, len: curLen, start: curStart };
        curKey = mid[i];
        curLen = 1;
        curStart = i;
      }
    }
    if (curLen > best.len) best = { key: curKey, len: curLen, start: curStart };

    // 전체 그리드 인덱스로 변환 (가운데줄은 row=1이니까 +5)
    const indices = [];
    for (let i = 0; i < best.len; i++) indices.push(5 + best.start + i);

    return { ...best, indices };
  }

  async function animateSpin(UI, finalKeys, durationMs = 900, tickMs = 70) {
    const endAt = Date.now() + durationMs;

    while (Date.now() < endAt) {
      UI.setGrid(randomKeys());
      await new Promise(r => setTimeout(r, tickMs));
    }
    UI.setGrid(finalKeys);
  }

  SLOT.game = { randomKeys, bestRun, animateSpin };
})();
