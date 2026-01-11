/* games/slot/slot.game.js */
/* slot.html 구조(#uiReels) 기준: 3x5 그리드 렌더 + 마운트/이미지 경로 폴백 */

window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const ROWS = 3;
  const COLS = 5;

  const FALLBACK_GRID = [
    ["star1", "star2", "star3", "pro1", "pro5"],
    ["star2", "star3", "pro1", "pro5", "pro10"],
    ["star1", "star2", "star3", "pro1", "pro5"],
  ];

  // ✅ slot.html 실제 마운트(#uiReels) 우선
  function findMount() {
    return (
      document.getElementById("uiReels") ||     // ✅ slot.html
      document.getElementById("reels") ||
      document.getElementById("reelMount") ||
      document.getElementById("slotStage") ||
      document.getElementById("stage") ||
      document.querySelector("[data-slot-stage]") ||
      document.querySelector(".slot-stage") ||
      document.querySelector(".stage") ||
      null
    );
  }

  // ✅ 없으면 slot.html의 래퍼(#uiReelWrap)에 uiReels를 만들어 붙임
  function ensureMount() {
    let mount = findMount();
    if (mount) return mount;

    const wrap =
      document.getElementById("uiReelWrap") ||                 // ✅ slot.html
      document.querySelector(".reelWrap") ||
      document.getElementById("gameStage") ||
      document.querySelector(".right-panel") ||
      document.querySelector(".panel-right") ||
      document.querySelector(".stage-wrap") ||
      document.querySelector(".board") ||
      document.body;

    mount = document.createElement("div");
    mount.id = "uiReels";
    mount.className = "reels"; // ✅ slot.html CSS를 그대로 타게
    wrap.appendChild(mount);

    return mount;
  }

  // ✅ grid 형태를 3x5로 강제
  function normalizeGrid(grid) {
    const g = Array.isArray(grid) ? grid : FALLBACK_GRID;
    const out = [];

    for (let r = 0; r < ROWS; r++) {
      const row = Array.isArray(g[r]) ? g[r] : [];
      const outRow = [];
      for (let c = 0; c < COLS; c++) {
        outRow.push(String(row[c] || FALLBACK_GRID[r][c] || "star1"));
      }
      out.push(outRow);
    }
    return out;
  }

  // ✅ 이미지 경로: 환경마다 다르니까 여러 후보를 순차 시도(onerror 폴백)
  function imgCandidates(id) {
    // 외부에서 지정 가능: SLOT.IMG_PATH(id) 또는 SLOT.IMG_BASE
    if (typeof S.IMG_PATH === "function") {
      try {
        const p = S.IMG_PATH(id);
        if (p) return [String(p)];
      } catch (_) {}
    }

    const base = (S.IMG_BASE ? String(S.IMG_BASE) : "").replace(/\/+$/, "");

    const list = [];
    if (base) list.push(`${base}/${id}.png`);

    // slot.html 위치: /games/slot.html 기준으로 흔한 케이스들
    list.push(`img/slot/${id}.png`);           // /games/img/slot/...
    list.push(`../img/slot/${id}.png`);        // /img/slot/...
    list.push(`./slot/img/slot/${id}.png`);    // /games/slot/img/slot/...
    list.push(`./img/${id}.png`);              // /games/img/...
    list.push(`../img/${id}.png`);             // /img/...

    // 중복 제거
    return Array.from(new Set(list));
  }

  function makeImg(id) {
    const img = document.createElement("img");
    img.alt = id;

    const candidates = imgCandidates(id);
    let idx = 0;

    img.src = candidates[idx] || "";
    img.onerror = function () {
      idx += 1;
      if (idx < candidates.length) {
        img.src = candidates[idx];
      }
    };

    return img;
  }

  // ✅ 15칸(.cell)을 slot.html CSS 구조에 맞게 생성/유지
  function ensureCells(mount) {
    // 이미 .cell이 15개 있으면 그대로 사용
    const existing = mount.querySelectorAll(".cell");
    if (existing && existing.length === ROWS * COLS) return Array.from(existing);

    // 아니면 재구성
    mount.innerHTML = "";

    // mount가 slot.html CSS(.reels)가 아니라면 최소한의 fallback
    if (!mount.classList.contains("reels")) mount.classList.add("reels");

    const cells = [];
    for (let i = 0; i < ROWS * COLS; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";

      const sym = document.createElement("div");
      sym.className = "sym";

      cell.appendChild(sym);
      mount.appendChild(cell);
      cells.push(cell);
    }
    return cells;
  }

  // ✅ 그리드 렌더 (slot.html 스타일 그대로 타게)
  function renderGrid(grid, opts) {
    const mount = ensureMount();
    if (!mount) return;

    const g = normalizeGrid(grid);
    const cells = ensureCells(mount);

    const animate = !!(opts && opts.animate);

    let k = 0;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const id = g[r][c];
        const cell = cells[k++];
        const sym = cell.querySelector(".sym");
        if (!sym) continue;

        sym.innerHTML = "";
        sym.appendChild(makeImg(id));

        if (animate) {
          // slot.html에 있는 tick 애니메이션 클래스 사용
          cell.classList.remove("tick");
          // reflow
          void cell.offsetWidth;
          cell.classList.add("tick");
        }
      }
    }
  }

  // ✅ 초기 릴 생성(기존 호출부 호환)
  function buildReels() {
    renderGrid(FALLBACK_GRID, { animate: false });
  }

  // 외부 노출
  S.game = S.game || {};
  S.game.buildReels = buildReels;
  S.game.renderGrid = renderGrid;

})(window.SLOT);
