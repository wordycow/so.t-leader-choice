/* games/slot/slot.game.js */
(function () {
  "use strict";

  window.SLOT = window.SLOT || {};
  const S = window.SLOT;

  // =========================
  // Constants
  // =========================
  const ROWS = 3;
  const COLS = 5;

  const SYMBOLS = [
    { id: "star1", label: "STAR1" },
    { id: "star2", label: "STAR2" },
    { id: "star3", label: "STAR3" },
    { id: "pro1", label: "PRO1" },
    { id: "pro10", label: "PRO10" },
  ];

  const PAY = {
    star1: { 2: 1, 3: 2, 4: 5, 5: 12 },
    star2: { 2: 1, 3: 2.5, 4: 6, 5: 15 },
    star3: { 2: 1, 3: 3, 4: 7, 5: 18 },
    pro1: { 2: 1, 3: 3.5, 4: 8, 5: 20 },
    pro10: { 2: 1, 3: 4, 4: 10, 5: 25 },
  };

  // ✅ 유송: bg는 PNG 확정
  const BG_LIST_DEFAULT = [
    "img/slot/bg1.png",
    "img/slot/bg2.png",
    "img/slot/bg3.png",
    "img/slot/bg4.png",
    "img/slot/bg5.png",
  ];

  // (있으면 사용, 없어도 무방)
  const SOUND = {
    spin: "sounds/spin.mp3",
    win: "sounds/win.mp3",
    jackpot: "sounds/jackpot.mp3",
  };

  // =========================
  // State
  // =========================
  const state = {
    cfg: {},
    weights: { star1: 22, star2: 18, star3: 14, pro1: 12, pro10: 1 },
    bgList: BG_LIST_DEFAULT.slice(),
    bgTimer: null,
    bgA: null,
    bgB: null,
    bgIdx: 0,
    bgFlip: false,
    soundOn: true,
    isSpinning: false,
    grid: null,
    mountEl: null,
    gridEl: null,
  };

  // =========================
  // Public API
  // =========================
  S.game = S.game || {};

  S.game.setConfig = function setConfig(cfg) {
    state.cfg = cfg || {};
    // weights from config (있으면 반영)
    const w = {};
    w.star1 = num(cfg.SLOT_W_STAR1, state.weights.star1);
    w.star2 = num(cfg.SLOT_W_STAR2, state.weights.star2);
    w.star3 = num(cfg.SLOT_W_STAR3, state.weights.star3);
    w.pro1 = num(cfg.SLOT_W_PRO1, state.weights.pro1);
    w.pro10 = num(cfg.SLOT_W_PRO10, state.weights.pro10);
    state.weights = w;

    // bg list override (optional)
    if (Array.isArray(cfg.SLOT_BG_LIST) && cfg.SLOT_BG_LIST.length) {
      state.bgList = cfg.SLOT_BG_LIST.slice();
    } else {
      state.bgList = BG_LIST_DEFAULT.slice();
    }
  };

  S.game.setSound = function setSound(on) {
    state.soundOn = !!on;
  };

  S.game.ensureMounted = function ensureMounted() {
    if (state.mountEl && state.gridEl) return;

    const mount = findMount_();
    state.mountEl = mount;

    // ✅ 절대 mount.innerHTML = "" 같은 “전체 삭제” 안 함 (유송이 겪은 블럭 꼬임 방지)
    let gridEl = mount.querySelector(".slot-grid");
    if (!gridEl) {
      gridEl = document.createElement("div");
      gridEl.className = "slot-grid";
      gridEl.style.display = "grid";
      gridEl.style.gridTemplateColumns = `repeat(${COLS}, 1fr)`;
      gridEl.style.gap = "14px";
      gridEl.style.width = "100%";
      gridEl.style.maxWidth = "720px";
      gridEl.style.margin = "0 auto";
      gridEl.style.padding = "18px 18px 22px";
      gridEl.style.boxSizing = "border-box";
      mount.appendChild(gridEl);
    }
    state.gridEl = gridEl;

    if (!state.grid) state.grid = makeRandomGrid_();
    renderGrid_(state.grid);
    ensureBgLayers_();
  };

  // spin: returns result object
  S.game.spin = async function spin(opts) {
    S.game.ensureMounted();

    const bet = Math.max(0, Number(opts && opts.bet) || 0);
    if (state.isSpinning) return { ok: false, error: "busy" };

    state.isSpinning = true;
    startBgCycle_();
    play_("spin");

    // 10s-ish spin animation
    const spinMs = 1050;
    const ticks = 12;

    for (let t = 0; t < ticks; t++) {
      state.grid = makeRandomGrid_();
      renderGrid_(state.grid);
      await wait_(spinMs / ticks);
    }

    // ✅ “라스베가스 느낌” 결과 고정: 한 줄만 맞추고 나머지는 최대한 흩트림
    const outcome = rollOutcomeType_();
    const final = buildOutcomeGrid_(outcome);
    state.grid = final;
    renderGrid_(state.grid);

    const evalRes = evaluateGrid_(final, bet, outcome);

    // sounds
    if (evalRes.jackpot) play_("jackpot");
    else if (evalRes.netDelta > 0) play_("win");

    stopBgCycle_();

    state.isSpinning = false;
    return Object.assign({ ok: true }, evalRes, { grid: final });
  };

  // =========================
  // Outcome / Evaluation
  // =========================

  function rollOutcomeType_() {
    // jackpot PPM (optional)
    const ppm = num(state.cfg.SLOT_JACKPOT_PPM, 20); // 20ppm = 0.002%
    const pJackpot = Math.max(0, ppm) / 1_000_000;

    const r = Math.random();
    if (r < pJackpot) return { kind: "jackpot", match: 5, line: randInt_(0, 2) };

    // ✅ 체감 확률(대충 “작은 승리 자주, 큰 승리 아주 가끔”)
    const r2 = Math.random();
    if (r2 < 0.004) return { kind: "five", match: 5, line: randInt_(0, 2) };      // 0.4%
    if (r2 < 0.024) return { kind: "four", match: 4, line: randInt_(0, 2) };      // 2.0%
    if (r2 < 0.144) return { kind: "three", match: 3, line: randInt_(0, 2) };     // 12.0%
    if (r2 < 0.404) return { kind: "two", match: 2, line: randInt_(0, 2) };       // 26.0%
    return { kind: "lose", match: 0, line: -1 };                                  // 나머지
  }

  function buildOutcomeGrid_(outcome) {
    const g = makeRandomGrid_();

    if (!outcome || outcome.kind === "lose") {
      // 최대한 2개 이상 같은 줄 안 나오게 살짝 정리
      return antiAccidentalWin_(g);
    }

    const sym = weightedPickSymbol_();
    const line = clamp_(outcome.line, 0, 2);
    const m = outcome.match;

    // 한 라인만 맞춤
    for (let c = 0; c < m; c++) g[line][c] = sym;

    // 나머지 칸은 “그 심볼”이 같은 줄로 더 이어지지 않도록 정리
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        if (r === line && c < m) continue;
        if (g[r][c] === sym) {
          g[r][c] = pickDifferent_(sym);
        }
      }
    }

    // 4/5 맞춘 줄도 “뒤쪽 동일 심볼”로 연장되지 않도록
    if (m < 5) {
      for (let c = m; c < COLS; c++) {
        if (g[line][c] === sym) g[line][c] = pickDifferent_(sym);
      }
    }

    // 다른 라인에서 같은 심볼로 우연히 3~5가 이어질 위험 줄이기
    return antiAccidentalWin_(g, sym);
  }

  function evaluateGrid_(grid, bet, outcome) {
    const lines = [
      grid[0],
      grid[1],
      grid[2],
    ];

    let best = { mult: 0, sym: null, match: 0, line: -1 };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const first = line[0];
      let cnt = 1;
      for (let c = 1; c < COLS; c++) {
        if (line[c] === first) cnt++;
        else break;
      }
      if (cnt >= 2) {
        const mult = (PAY[first] && PAY[first][cnt]) ? PAY[first][cnt] : 0;
        if (mult > best.mult) best = { mult, sym: first, match: cnt, line: i };
      }
    }

    const payout = round2_(bet * (best.mult || 0));
    const netDelta = round2_(payout - bet);
    const lossAmount = netDelta < 0 ? round2_(Math.abs(netDelta)) : 0;

    const jackpot = !!(outcome && outcome.kind === "jackpot");

    // ✅ 유송 룰: 2개 본전은 LOSE 느낌 제거 → EVEN / HIT +0 UT
    let label;
    if (netDelta === 0 && bet > 0) label = "EVEN";
    else if (netDelta > 0) label = "WIN";
    else label = "LOSE";

    let resultText = "";
    if (label === "EVEN") resultText = `HIT +0 UT`;
    else if (label === "WIN") resultText = `WIN +${fmt_(netDelta)} UT`;
    else resultText = `LOSE -${fmt_(Math.abs(netDelta))} UT`;

    if (jackpot) {
      label = "JACKPOT";
      resultText = `JACKPOT +${fmt_(netDelta)} UT`;
    }

    return {
      bet,
      payout,
      netDelta,
      lossAmount,
      label,
      resultText,
      match: best.match,
      symbol: best.sym,
      line: best.line,
      jackpot,
    };
  }

  // =========================
  // Render
  // =========================
  function renderGrid_(grid) {
    const el = state.gridEl;
    if (!el) return;

    // build cells
    el.innerHTML = "";
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const cell = document.createElement("div");
        cell.className = "slot-cell";
        cell.style.borderRadius = "16px";
        cell.style.border = "1px solid rgba(255,255,255,0.08)";
        cell.style.background = "rgba(0,0,0,0.18)";
        cell.style.backdropFilter = "blur(6px)";
        cell.style.aspectRatio = "1 / 1";
        cell.style.display = "grid";
        cell.style.placeItems = "center";
        cell.style.boxShadow = "inset 0 0 0 1px rgba(0,255,255,0.05)";
        cell.style.overflow = "hidden";

        const img = document.createElement("img");
        img.alt = grid[r][c];
        img.style.maxWidth = "78%";
        img.style.maxHeight = "78%";
        img.style.transform = "translateZ(0)";

        // 이미지 경로는 기존 리소스 구조를 그대로 따라감
        img.src = `img/slot/${grid[r][c]}.png`;
        img.onerror = () => {
          img.style.display = "none";
          cell.textContent = grid[r][c];
          cell.style.color = "#cbd5e1";
          cell.style.fontSize = "12px";
        };

        cell.appendChild(img);
        el.appendChild(cell);
      }
    }
  }

  // =========================
  // Background (flash only while spinning)
  // =========================
  function ensureBgLayers_() {
    if (state.bgA && state.bgB) return;

    const a = document.createElement("div");
    const b = document.createElement("div");

    [a, b].forEach((d) => {
      d.style.position = "fixed";
      d.style.inset = "0";
      d.style.backgroundSize = "cover";
      d.style.backgroundPosition = "center";
      d.style.backgroundRepeat = "no-repeat";
      d.style.transition = "opacity 220ms linear";
      d.style.opacity = "0";
      d.style.pointerEvents = "none";
      d.style.zIndex = "-1"; // ✅ 컨텐츠 아래
    });

    document.body.appendChild(a);
    document.body.appendChild(b);

    state.bgA = a;
    state.bgB = b;
  }

  function startBgCycle_() {
    if (!state.bgA || !state.bgB) ensureBgLayers_();
    if (state.bgTimer) clearInterval(state.bgTimer);

    state.bgIdx = 0;
    state.bgFlip = false;

    // 첫 장만 살짝 보여주고, 스핀 중에만 현란하게 변경
    setBg_(state.bgList[state.bgIdx % state.bgList.length]);
    state.bgTimer = setInterval(() => {
      state.bgIdx++;
      setBg_(state.bgList[state.bgIdx % state.bgList.length]);
    }, 180);
  }

  function stopBgCycle_() {
    if (state.bgTimer) clearInterval(state.bgTimer);
    state.bgTimer = null;

    // 스핀 종료 후엔 “변경만 멈춤”(배경은 남아있음)
    if (state.bgA) state.bgA.style.opacity = "1";
    if (state.bgB) state.bgB.style.opacity = "0";
  }

  function setBg_(src) {
    const a = state.bgA, b = state.bgB;
    if (!a || !b) return;

    const next = state.bgFlip ? a : b;
    const prev = state.bgFlip ? b : a;

    next.style.backgroundImage = `url("${src}")`;
    next.style.opacity = "1";
    prev.style.opacity = "0";

    state.bgFlip = !state.bgFlip;
  }

  // =========================
  // Helpers
  // =========================
  function findMount_() {
    // ✅ “릴 영역”만 잡는다. 큰 컨테이너를 잡아서 지우는 실수 방지.
    const selectors = [
      "#reelMount",
      "#slotReels",
      "#reels",
      ".reel-mount",
      ".slot-reels",
      ".slot-stage",
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    // 마지막 fallback: body(하지만 절대 비우지 않음)
    return document.body;
  }

  function makeRandomGrid_() {
    const g = [];
    for (let r = 0; r < ROWS; r++) {
      const row = [];
      for (let c = 0; c < COLS; c++) row.push(weightedPickSymbol_());
      g.push(row);
    }
    return g;
  }

  function weightedPickSymbol_() {
    const entries = Object.entries(state.weights || {});
    let sum = 0;
    entries.forEach(([, w]) => (sum += Math.max(0, Number(w) || 0)));

    if (sum <= 0) return "star1";

    let r = Math.random() * sum;
    for (const [k, wRaw] of entries) {
      const w = Math.max(0, Number(wRaw) || 0);
      r -= w;
      if (r <= 0) return k;
    }
    return entries[0][0];
  }

  function pickDifferent_(notSym) {
    const pool = SYMBOLS.map((s) => s.id).filter((x) => x !== notSym);
    return pool[randInt_(0, pool.length - 1)];
  }

  function antiAccidentalWin_(g, avoidSym) {
    // 다른 줄에서 “앞에서부터” 동일 심볼이 3개 이상 이어지면 끊어준다.
    for (let r = 0; r < ROWS; r++) {
      const first = g[r][0];
      let cnt = 1;
      for (let c = 1; c < COLS; c++) {
        if (g[r][c] === first) cnt++;
        else break;
      }
      if (cnt >= 3) {
        // 3번째부터 끊기
        for (let c = 2; c < cnt; c++) g[r][c] = pickDifferent_(first);
      }
      // avoidSym가 길게 이어지면 끊기
      if (avoidSym) {
        let k = 1;
        for (let c = 1; c < COLS; c++) {
          if (g[r][c] === avoidSym && g[r][c - 1] === avoidSym) k++;
          else k = 1;
          if (k >= 3) g[r][c] = pickDifferent_(avoidSym);
        }
      }
    }
    return g;
  }

  function play_(which) {
    if (!state.soundOn) return;
    const src = SOUND[which];
    if (!src) return;
    try {
      const a = new Audio(src);
      a.volume = 0.9;
      a.play().catch(() => {});
    } catch (_) {}
  }

  function wait_(ms) {
    return new Promise((res) => setTimeout(res, ms));
  }

  function num(v, d) {
    const n = Number(v);
    return Number.isFinite(n) ? n : d;
  }

  function round2_(n) {
    return Math.round(Number(n) * 100) / 100;
  }

  function fmt_(n) {
    const x = Number(n) || 0;
    return x % 1 === 0 ? String(x) : x.toFixed(2);
  }

  function randInt_(a, b) {
    return Math.floor(Math.random() * (b - a + 1)) + a;
  }

  function clamp_(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }
})();
