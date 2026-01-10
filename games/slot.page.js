/* games/slot.page.js
 * THE UNIQUE SLOT (cyber)
 * - gate/main에서 저장한 localStorage(uniqueCurrentUser)로 자동 로그인
 * - WORKER_BASE /slot/state, /slot/spin 호출
 * - 안 되면 화면(uiNote/uiResult)에 이유를 “보이게” 찍음
 */
(() => {
  "use strict";

  // ✅ 워커 주소(필요하면 여기만 바꾸면 됨)
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 버전 마커 (캐시/적용 확인용)
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_cyber_fix1";

  // ---------- utils ----------
  const $id = (id) => document.getElementById(id);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return String(Math.floor(x));
  }

  function setText(el, v) {
    if (!el) return;
    el.textContent = String(v ?? "");
  }

  function setNote(msg, isError = false) {
    if (!ui.note) return;
    ui.note.textContent = msg || "";
    ui.note.style.opacity = msg ? "1" : "0.75";
    ui.note.style.color = isError ? "rgba(255,120,160,.95)" : "rgba(215,228,255,.82)";
  }

  function setResult(msg, isError = false) {
    if (!ui.result) return;
    ui.result.textContent = msg || "";
    ui.result.style.color = isError ? "rgba(255,120,160,.95)" : "";
  }

  function getLocalUser() {
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return null;
      const u = JSON.parse(raw);
      const id = String(u?.id || "").trim().toLowerCase();
      if (!id) return null;
      return {
        id,
        name: String(u?.name || "").trim(),
        nickname: String(u?.nickname || "").trim(),
        balance: Number(u?.balance || 0),
      };
    } catch {
      return null;
    }
  }

  function redirectToGate() {
    // /games/slot.html -> 한 단계 위
    location.href = "../the-unique-gate.html";
  }

  async function fetchJSON(url, opt = {}, timeoutMs = 15000) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort("timeout"), timeoutMs);
    try {
      const res = await fetch(url, { ...opt, signal: ctrl.signal, cache: "no-store" });
      const text = await res.text();
      let js = null;
      try { js = JSON.parse(text); } catch { js = { ok: false, error: "bad_json", raw: text }; }
      if (!res.ok && js && typeof js === "object" && !js.error) {
        js.error = `http_${res.status}`;
      }
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  // ---------- DOM binding (slot.html id 기준) ----------
  const ui = {
    title:  $id("uiTitle"),
    player: $id("uiPlayer"),
    wallet: $id("uiWallet"),
    jackpot:$id("uiJackpot"),
    result: $id("uiResult"),
    bet:    $id("uiBet"),
    note:   $id("uiNote"),
    pay:    $id("uiPaytable"),
    reels:  $id("uiReels"),
    reelWrap: $id("uiReelWrap"),
    btnSpin: $id("btnSpin"),
    btnAuto: $id("btnAuto"),
  };

  // ---------- reels ----------
  const ROWS = 3;
  const COLS = 5;

  function ensureCells() {
    if (!ui.reels) return [];
    const need = ROWS * COLS;
    let cells = ui.reels.querySelectorAll(".cell");
    if (!cells || cells.length !== need) {
      ui.reels.innerHTML = "";
      const frag = document.createDocumentFragment();
      for (let i = 0; i < need; i++) {
        const d = document.createElement("div");
        d.className = "cell";
        const sym = document.createElement("div");
        sym.className = "sym";
        d.appendChild(sym);
        frag.appendChild(d);
      }
      ui.reels.appendChild(frag);
      cells = ui.reels.querySelectorAll(".cell");
    }
    return Array.from(cells);
  }

  // 심볼을 SVG로 네온 렌더 (PNG 없어도 “광기” 유지)
  function svgFor(sym) {
    const s = String(sym || "").toUpperCase();
    let g1 = "#21f6ff", g2 = "#ff2bd6";
    if (s.includes("STAR")) { g1 = "#21f6ff"; g2 = "#b7ff2a"; }
    if (s.includes("PRO"))  { g1 = "#ff2bd6"; g2 = "#a98bff"; }
    if (s.includes("JACK")) { g1 = "#ffcc33"; g2 = "#ff2bd6"; }

    // 단순하지만 강한 네온 “엠블럼”
    return `
      <svg viewBox="0 0 200 200" aria-hidden="true">
        <defs>
          <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0" stop-color="${g1}"/>
            <stop offset="1" stop-color="${g2}"/>
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="b"/>
            <feMerge>
              <feMergeNode in="b"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <circle cx="100" cy="100" r="70" fill="rgba(0,0,0,.15)" stroke="url(#g)" stroke-width="10" filter="url(#glow)"/>
        <path d="M100 52 L118 92 L162 92 L126 118 L140 162 L100 136 L60 162 L74 118 L38 92 L82 92 Z"
              fill="url(#g)" filter="url(#glow)" opacity="0.95"/>
      </svg>
    `;
  }

  function renderGrid(grid) {
    const cells = ensureCells();
    if (!cells.length) return;

    // grid: [[..5],[..5],[..5]] 가정
    const flat = [];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        flat.push(grid?.[r]?.[c] ?? "");
      }
    }

    flat.forEach((sym, i) => {
      const cell = cells[i];
      if (!cell) return;
      const box = cell.querySelector(".sym");
      if (!box) return;

      box.innerHTML = sym ? svgFor(sym) : "";
      // PNG가 있으면 “위에 살짝” 얹힘(선택)
      if (sym) {
        const img = document.createElement("img");
        img.src = `../img/slot/${sym}.png`;
        img.alt = sym;
        img.onerror = () => img.remove();
        box.appendChild(img);
      }
    });
  }

  // ---------- state ----------
  let identity = null;
  let autoOn = false;
  let spinning = false;
  let autoTimer = null;

  function stopAuto() {
    autoOn = false;
    if (ui.btnAuto) ui.btnAuto.textContent = "AUTO OFF";
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = null;
  }

  function startAuto() {
    if (autoOn) return;
    autoOn = true;
    if (ui.btnAuto) ui.btnAuto.textContent = "AUTO ON";
    autoTimer = setInterval(() => {
      if (!spinning) spin();
    }, 1200);
  }

  function toggleAuto() {
    if (autoOn) stopAuto();
    else startAuto();
  }

  async function loadState() {
    const u = identity?.id;
    if (!u) return null;

    setNote("SYNC…");
    const js = await fetchJSON(`${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}`, {}, 20000);

    if (!js?.ok) {
      setResult(`STATE ERROR`, true);
      setNote(`state fail: ${js?.error || "unknown"} (NETWORK 탭에서 /slot/state 응답 확인)`, true);
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim() || identity.name || identity.id;

    setText(ui.player, displayName);
    setText(ui.wallet, fmt(js.ut));
    setText(ui.jackpot, fmt(js.jackpot));
    setText(ui.bet, fmt(js.bet ?? 10));

    setResult("READY");
    setNote("");

    // 초기 그리드가 있으면 렌더
    if (js.grid) renderGrid(js.grid);

    return js;
  }

  async function spin() {
    if (spinning) return;
    spinning = true;

    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      setNote("SPINNING…");
      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u })
      }, 20000);

      if (!js?.ok) {
        setResult("SPIN ERROR", true);
        setNote(`spin fail: ${js?.error || "unknown"}`, true);
        if (String(js?.error || "").includes("insufficient")) stopAuto();
        return;
      }

      setText(ui.wallet, fmt(js.ut));
      setText(ui.jackpot, fmt(js.jackpot));
      setText(ui.bet, fmt(js.bet ?? 10));
      renderGrid(js.grid);

      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);
      const delta = win - betCharged;

      if (delta > 0) setResult(`WIN +${fmt(delta)} UT`);
      else if (delta < 0) setResult(`LOSE ${fmt(delta)} UT`);
      else setResult(`EVEN 0 UT`);

      // localStorage 잔액 동기화(메인/게이트와 일치)
      try {
        const raw = localStorage.getItem("uniqueCurrentUser");
        if (raw) {
          const uu = JSON.parse(raw);
          uu.balance = Number(js.ut || 0);
          localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
          localStorage.setItem("myUtPoints", String(Number(js.ut || 0)));
        }
      } catch (_) {}

      setNote("");

    } catch (e) {
      setResult("SPIN ERROR", true);
      setNote(String(e?.message || e), true);
      stopAuto();
    } finally {
      spinning = false;
      if (ui.btnSpin) ui.btnSpin.disabled = false;
    }
  }

  // ---------- boot ----------
  async function boot() {
    // ✅ 게이트/메인에서 저장된 user 없으면 “바로 게이트로”
    identity = getLocalUser();
    if (!identity) return redirectToGate();

    // nickname 보조 저장값
    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    // 버튼 바인딩
    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    // 초기에 빈 그리드라도 생성
    renderGrid(null);

    // 상태 로드
    await loadState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
