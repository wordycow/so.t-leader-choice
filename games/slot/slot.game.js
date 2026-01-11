(function () {
  const S = (window.S = window.S || {});
  S.game = S.game || {};

  // ✅ 심볼/가중치/배당 (2개는 모두 EVEN(×1))
  const SYMBOLS = [
    { id: "star1",  name: "STAR1",  w: 22, pay: { 2: 1, 3: 2, 4: 5, 5: 12 } },
    { id: "star2",  name: "STAR2",  w: 18, pay: { 2: 1, 3: 2.5, 4: 6, 5: 15 } },
    { id: "star3",  name: "STAR3",  w: 14, pay: { 2: 1, 3: 3, 4: 7, 5: 18 } },

    { id: "pro1",   name: "PRO1",   w: 12, pay: { 2: 1, 3: 4, 4: 9, 5: 22 } },
    { id: "pro2",   name: "PRO2",   w: 9,  pay: { 2: 1, 3: 4.5, 4: 10, 5: 25 } },
    { id: "pro3",   name: "PRO3",   w: 7,  pay: { 2: 1, 3: 5, 4: 12, 5: 28 } },
    { id: "pro4",   name: "PRO4",   w: 5,  pay: { 2: 1, 3: 5.5, 4: 13, 5: 30 } },
    { id: "pro5",   name: "PRO5",   w: 4,  pay: { 2: 1, 3: 6, 4: 14, 5: 33 } },
    { id: "pro6",   name: "PRO6",   w: 3,  pay: { 2: 1, 3: 6.5, 4: 15, 5: 36 } },
    { id: "pro7",   name: "PRO7",   w: 2.5,pay: { 2: 1, 3: 7, 4: 16, 5: 40 } },
    { id: "pro8",   name: "PRO8",   w: 2,  pay: { 2: 1, 3: 8, 4: 18, 5: 45 } },
    { id: "pro9",   name: "PRO9",   w: 1.5,pay: { 2: 1, 3: 9, 4: 20, 5: 55 } },
    { id: "pro10",  name: "PRO10",  w: 1,  pay: { 2: 1, 3: 10, 4: 25, 5: 70 } },
  ];

  const byId = Object.fromEntries(SYMBOLS.map(s => [s.id, s]));
  const totalW = SYMBOLS.reduce((a, s) => a + s.w, 0);

  function pick() {
    let r = Math.random() * totalW;
    for (const s of SYMBOLS) {
      r -= s.w;
      if (r <= 0) return s.id;
    }
    return "star1";
  }

  function countAll(grid) {
    const m = new Map();
    for (const id of grid) m.set(id, (m.get(id) || 0) + 1);
    return m;
  }

  function bestHit(counts, bet) {
    let best = null;

    for (const [id, cnt] of counts.entries()) {
      if (cnt < 2) continue;
      const sym = byId[id];
      const mul = sym?.pay?.[Math.min(5, cnt)] || (cnt === 2 ? 1 : 0);
      const win = bet * mul;
      const net = win - bet;
      if (!best || win > best.win) best = { id, cnt: Math.min(5, cnt), mul, win, net };
    }

    return best;
  }

  // ✅ 잭팟은 “월 1회 느낌”으로 매우 레어 (기본 1/50000)
  function jackpotRoll() {
    return Math.random() < 1 / 50000;
  }

  function makeJackpotGrid(rows, cols) {
    const g = new Array(rows * cols).fill("pro10");
    return g;
  }

  function spin(bet, jackpotPool) {
    const rows = S.CONFIG.ROWS || 3;
    const cols = S.CONFIG.COLS || 5;
    const size = rows * cols;

    // JACKPOT
    if (jackpotRoll()) {
      const grid = makeJackpotGrid(rows, cols);
      const jackpotPay = Math.max(Number(jackpotPool || 0), bet * 500); // 풀 없으면 최소 연출금
      const win = jackpotPay; // 잭팟은 풀(또는 최소치)만 지급으로 단순화
      const netDelta = win - bet;

      return {
        grid,
        type: "JACKPOT",
        hit: { id: "pro10", cnt: 5, mul: 0, win },
        win,
        netDelta,
        lossAmount: 0,
        jackpotPayout: jackpotPay,
      };
    }

    // normal
    const grid = new Array(size).fill(0).map(() => pick());
    const counts = countAll(grid);
    const hit = bestHit(counts, bet);

    if (!hit) {
      return {
        grid,
        type: "MISS",
        hit: null,
        win: 0,
        netDelta: -bet,
        lossAmount: bet,
        jackpotPayout: 0,
      };
    }

    // ✅ 2개 = EVEN (LOSE 느낌 제거 / HIT +0 금지)
    if (hit.cnt === 2) {
      return {
        grid,
        type: "EVEN",
        hit,
        win: bet,
        netDelta: 0,
        lossAmount: 0,
        jackpotPayout: 0,
      };
    }

    // WIN
    return {
      grid,
      type: "WIN",
      hit,
      win: hit.win,
      netDelta: hit.net,
      lossAmount: 0,
      jackpotPayout: 0,
    };
  }

  function paytable() {
    return SYMBOLS.map(s => ({
      id: s.id,
      name: s.name,
      pay: s.pay
    }));
  }

  S.game.spin = spin;
  S.game.paytable = paytable;
})();
