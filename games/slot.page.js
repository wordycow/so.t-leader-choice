/* games/slot.page.js
 * THE UNIQUE SLOT (cyber + vertical spin)
 * - localStorage(uniqueCurrentUser)로 자동 로그인
 * - WORKER_BASE /slot/state, /slot/spin 호출
 * - 스핀 연출: 위->아래로 빠르게 롤링하다가 결과 착지
 * - 사운드: start/spin/stop/win/lose/jackpot
 */
(() => {
  "use strict";

  // ✅ 워커 주소(필요하면 여기만 바꾸면 됨)
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 버전 마커 (캐시/적용 확인용)
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_vertical_spin_v1";
  console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__ || "no_version");

  // ---------- utils ----------
  const $id = (id) => document.getElementById(id);

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
      if (!res.ok && js && typeof js === "object" && !js.error) js.error = `http_${res.status}`;
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  // ---------- DOM binding ----------
  const ui = {
    title:   $id("uiTitle"),
    player:  $id("uiPlayer"),
    wallet:  $id("uiWallet"),
    jackpot: $id("uiJackpot"),
    result:  $id("uiResult"),
    bet:     $id("uiBet"),
    note:    $id("uiNote"),
    pay:     $id("uiPaytable"),
    reels:   $id("uiReels"),
    reelWrap:$id("uiReelWrap"),
    btnSpin: $id("btnSpin"),
    btnAuto: $id("btnAuto"),
  };

  // ---------- sounds (GitHub는 대소문자 구분!) ----------
  const SND = {
    start:   new Audio("./sounds/start-button-sound.MP3"),
    spin:    new Audio("./sounds/spining-sound.MP3"),
    stop:    new Audio("./sounds/stop-stop-stop-sound.MP3"),
    win:     new Audio("./sounds/win-sound.MP3"),
    lose:    new Audio("./sounds/lose-sound.MP3"),
    jackpot: new Audio("./sounds/jackpot-sound.MP3"),
  };
  SND.spin.loop = true;
  function play(a, vol = 0.9) {
    try {
      a.pause();
      a.currentTime = 0;
      a.volume = vol;
      a.play().catch(() => {});
    } catch {}
  }
  function startLoop(a, vol = 0.6) {
    try {
      a.volume = vol;
      a.play().catch(() => {});
    } catch {}
  }
  function stopLoop(a) {
    try { a.pause(); a.currentTime = 0; } catch {}
  }

  // ---------- reels ----------
  const ROWS = 3;
  const COLS = 5;

  // 실제 이미지 폴더에 있는 이름들 기준(소문자)
  const SYMBOL_POOL = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10",
    "slide1","slide2","slide3","slide4","slide5","slide6","slide7","slide8",
    "jackpot"
  ];

  function pickSym() {
    return SYMBOL_POOL[(Math.random() * SYMBOL_POOL.length) | 0];
  }

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

  // 네온 SVG(기본 광기 유지용) + PNG 오버레이(있으면 더 미침)
  function svgFor(symLower) {
    const s = String(symLower || "").toUpperCase();
    let g1 = "#21f6ff", g2 = "#ff2bd6";
    if (s.includes("STAR")) { g1 = "#21f6ff"; g2 = "#b7ff2a"; }
    if (s.includes("PRO"))  { g1 = "#ff2bd6"; g2 = "#a98bff"; }
    if (s.includes("JACK")) { g1 = "#ffcc33"; g2 = "#ff2bd6"; }

    return `
      <svg viewBox="0 0 200 200" aria-hidden="true">
        <defs>
          <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0" stop-color="${g1}"/>
            <stop offset="1" stop-color="${g2}"/>
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="7" result="b"/>
            <feMerge>
              <feMergeNode in="b"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <circle cx="100" cy="100" r="76" fill="rgba(0,0,0,.15)" stroke="url(#g)" stroke-width="10" filter «=« "url(#glow)"/>
        <path d="M100 46 L122 92 L172 92 L132 122 L148 172 L100 142 L52 172 L68 122 L28 92 L78 92 Z"
              fill="url(#g)" filter="url(#glow)" opacity="0.96"/>
      </svg>
    `.replace("filter «=«", "filter=");
  }

  function renderOneCell(box, symAny) {
    const sym = String(symAny ?? "");
    const symLower = sym ? sym.toLowerCase() : "";
    box.innerHTML = symLower ? svgFor(symLower) : "";

    if (symLower) {
      const img = document.createElement("img");
      // ✅ 폴더가 games/img/slot 이니까 ./img/slot 이 맞음
      img.src = `./img/slot/${symLower}.png`;
      img.alt = symLower;
      img.onerror = () => img.remove();
      box.appendChild(img);
    }
  }

  function renderGrid(grid) {
    const cells = ensureCells();
    if (!cells.length) return;

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
      renderOneCell(box, sym);
    });
  }

  // ---------- vertical spin animation (위 -> 아래) ----------
  let spinTimer = null;
  let spinCols = null; // COLS 배열, 각 col은 ROWS 길이

  function initSpinState() {
    spinCols = Array.from({ length: COLS }, () =>
      Array.from({ length: ROWS }, () => pickSym())
    );
  }

  function drawSpinState() {
    const cells = ensureCells();
    if (!cells.length || !spinCols) return;

    // cells index = r*COLS + c
    for (let c = 0; c < COLS; c++) {
      for (let r = 0; r < ROWS; r++) {
        const i = r * COLS + c;
        const cell = cells[i];
        const box = cell?.querySelector?.(".sym");
        if (!box) continue;
        renderOneCell(box, spinCols[c][r]);
      }
    }
  }

  function tickSpinDown() {
    // 위에서 아래로: r2 <- r1, r1 <- r0, r0 <- new
    for (let c = 0; c < COLS; c++) {
      const col = spinCols[c];
      col[2] = col[1];
      col[1] = col[0];
      col[0] = pickSym();
    }
    drawSpinState();
  }

  function startSpinFX() {
    if (spinTimer) return;
    initSpinState();
    drawSpinState();

    if (ui.reelWrap) ui.reelWrap.classList.add("shake");
    setTimeout(() => ui.reelWrap && ui.reelWrap.classList.remove("shake"), 260);

    // 빠르게 “굴러가는” 느낌
    spinTimer = setInterval(tickSpinDown, 65);
  }

  function stopSpinFX(finalGrid) {
    if (spinTimer) clearInterval(spinTimer);
    spinTimer = null;

    // 착지(결과)
    renderGrid(finalGrid);

    if (ui.reelWrap) {
      ui.reelWrap.classList.add("winFlash");
      setTimeout(() => ui.reelWrap && ui.reelWrap.classList.remove("winFlash"), 650);
    }
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
    }, 1300);
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
      setNote(`state fail: ${js?.error || "unknown"}`, true);
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim() || identity.name || identity.id;

    setText(ui.player, displayName);
    setText(ui.wallet, fmt(js.ut));
    setText(ui.jackpot, fmt(js.jackpot));
    setText(ui.bet, fmt(js.bet ?? 10));

    setResult("READY");
    setNote("");

    if (js.grid) renderGrid(js.grid);
    return js;
  }

  async function spin() {
    if (spinning) return;
    spinning = true;
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    // 사운드 + 연출 시작
    play(SND.start, 0.9);
    startSpinFX();
    startLoop(SND.spin, 0.55);
    setNote("SPINNING…");

    try {
      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u })
      }, 25000);

      stopLoop(SND.spin);

      if (!js?.ok) {
        stopSpinFX(null);

        setResult("SPIN ERROR", true);
        setNote(`spin fail: ${js?.error || "unknown"}`, true);

        // ✅ 지금 네 화면에 뜬 케이스: 시트에 유저가 없음
        if (String(js?.error || "") === "user_not_found_in_sheet") {
          setNote("유저가 슬롯 시트에 없음 → 게이트에서 등록 후 다시 오세요.", true);
          // 자동중단
          stopAuto();
        }
        return;
      }

      // 착지
      stopSpinFX(js.grid);
      play(SND.stop, 0.85);

      setText(ui.wallet, fmt(js.ut));
      setText(ui.jackpot, fmt(js.jackpot));
      setText(ui.bet, fmt(js.bet ?? 10));

      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);
      const delta = win - betCharged;

      if (js.jackpotHit || String(js.hit || "").toLowerCase().includes("jackpot")) {
        setResult(`JACKPOT +${fmt(win)} UT`);
        play(SND.jackpot, 0.9);
        ui.reelWrap?.classList?.add("jackpotPulse");
        setTimeout(() => ui.reelWrap?.classList?.remove("jackpotPulse"), 900);
      } else if (delta > 0) {
        setResult(`WIN +${fmt(delta)} UT`);
        play(SND.win, 0.85);
      } else if (delta < 0) {
        setResult(`LOSE ${fmt(delta)} UT`);
        play(SND.lose, 0.85);
      } else {
        setResult(`EVEN 0 UT`);
      }

      // localStorage 잔액 동기화
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
      stopLoop(SND.spin);
      stopSpinFX(null);

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
    identity = getLocalUser();
    if (!identity) return redirectToGate();

    // nickname 보조
    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    // 첫 화면: 빈 그리드 + 네온 기본
    initSpinState();
    drawSpinState();

    await loadState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
