/* games/slot.page.js
 * THE UNIQUE SLOT (fix paths + symbol normalize)
 * - slot.html 위치: /games/slot.html
 * - 이미지 실제 위치: /games/img/slot/*.png  → 경로는 "./img/slot/"
 * - 사운드 실제 위치: /games/sounds/*.MP3    → 경로는 "./sounds/"
 * - 서버 심볼이 pro09/star03 처럼 0이 붙어도 pro9/star3로 정규화
 */

(() => {
  "use strict";

  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_pathfix_v2";

  // ---------- utils ----------
  const $id = (id) => document.getElementById(id);
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function fmt(n) {
    const x = Number(n ?? 0);
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
    ui.note.style.opacity = msg ? "1" : "0.8";
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
        balance: Number(u?.balance ?? localStorage.getItem("myUtPoints") ?? 0),
      };
    } catch {
      return null;
    }
  }

  function redirectToGate() {
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

  function pickUT(obj) {
    const cands = [
      obj?.ut, obj?.UT,
      obj?.totalUT, obj?.total_ut,
      obj?.totalPoints, obj?.points,
      obj?.myUT, obj?.wallet, obj?.balance,
      obj?.총UT, obj?.["총 UT"], obj?.["total UT"],
    ];
    for (const v of cands) {
      const n = Number(v);
      if (Number.isFinite(n)) return n;
    }
    return null;
  }

  // ---------- DOM binding ----------
  const ui = {
    player: $id("uiPlayer"),
    wallet: $id("uiWallet"),
    jackpot: $id("uiJackpot"),
    result: $id("uiResult"),
    bet: $id("uiBet"),
    note: $id("uiNote"),
    pay: $id("uiPaytable"),
    reels: $id("uiReels"),
    reelWrap: $id("uiReelWrap"),
    btnSpin: $id("btnSpin"),
    btnAuto: $id("btnAuto"),
    btnSound: $id("btnSound"),
    betHint: $id("uiBetHint"),
  };

  // ---------- inject CSS ----------
  function injectStyleOnce() {
    if (document.getElementById("slotPageInjectedStyle")) return;
    const st = document.createElement("style");
    st.id = "slotPageInjectedStyle";
    st.textContent = `
      .btn.tu-compact { padding: 10px 12px !important; border-radius: 14px !important; font-size: 12px !important; }
      .btnAuto.tu-compact { width: 120px !important; }
      .btnSound.tu-compact { width: 130px !important; }

      .tu-betbar{ display:flex; align-items:center; gap:10px; margin-top:10px; }
      .tu-betbtn{
        width:44px; height:40px;
        border-radius:14px;
        border:1px solid rgba(33,246,255,.22);
        background: rgba(4,6,16,.40);
        color: rgba(215,228,255,.92);
        font-weight:900;
        cursor:pointer;
      }
      .tu-betmeta{
        font-family: "Share Tech Mono", ui-monospace, Menlo, monospace;
        font-size: 12px;
        color: rgba(215,228,255,.82);
        letter-spacing: .06em;
      }

      .tu-spin-drop{ animation: tuDrop .35s ease-in forwards; }
      @keyframes tuDrop{
        0%{ transform: translateY(-36px); filter: blur(1px) saturate(1.25); opacity:.0; }
        60%{ opacity:1; }
        100%{ transform: translateY(0); filter:none; opacity:1; }
      }
      .tu-spin-blur{ animation: tuBlur .7s linear infinite; }
      @keyframes tuBlur{
        0%{ transform: translateY(-18px); filter: blur(2px) saturate(1.3); }
        100%{ transform: translateY(18px); filter: blur(2px) saturate(1.3); }
      }

      .tu-paywrap{ margin-top: 12px; }
      .tu-paytitle{
        font-family:"Orbitron", system-ui, sans-serif;
        font-weight:900;
        letter-spacing:.14em;
        font-size:12px;
        color: rgba(215,228,255,.88);
        margin: 4px 0 8px;
        text-transform: uppercase;
      }
    `;
    document.head.appendChild(st);
  }

  // ---------- reels ----------
  const ROWS = 3;
  const COLS = 5;

  // repo에 실제 존재하는 파일만
  const AVAILABLE_PNG = new Set([
    "star1", "star2", "star3",
    "pro1", "pro2", "pro3", "pro4", "pro5", "pro6", "pro7", "pro8", "pro9", "pro10",
  ]);

  // ✅ 심볼 정규화: pro09 → pro9, star03 → star3
  function normalizeKey(sym) {
    const s = String(sym || "").trim().toLowerCase();
    const cleaned = s.replace(/[^a-z0-9]/g, ""); // pro09, star3, pro10...

    if (cleaned.startsWith("pro")) {
      const num = parseInt(cleaned.slice(3), 10);
      if (Number.isFinite(num)) return `pro${num}`;
    }
    if (cleaned.startsWith("star")) {
      const num = parseInt(cleaned.slice(4), 10);
      if (Number.isFinite(num)) return `star${num}`;
    }
    return cleaned;
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

  function svgFor(sym) {
    const key = normalizeKey(sym).toUpperCase();
    let g1 = "#21f6ff", g2 = "#ff2bd6";
    if (key.includes("STAR")) { g1 = "#21f6ff"; g2 = "#b7ff2a"; }
    if (key.includes("PRO"))  { g1 = "#ff2bd6"; g2 = "#a98bff"; }

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
        <circle cx="100" cy="100" r="70" fill="rgba(0,0,0,.10)" stroke="url(#g)" stroke-width="10" filter="url(#glow)"/>
        <path d="M100 52 L118 92 L162 92 L126 118 L140 162 L100 136 L60 162 L74 118 L38 92 L82 92 Z"
              fill="url(#g)" filter="url(#glow)" opacity="0.95"/>
      </svg>
    `;
  }

  function renderGrid(grid) {
    const cells = ensureCells();
    if (!cells.length) return;

    const flat = [];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) flat.push(grid?.[r]?.[c] ?? "");
    }

    flat.forEach((sym, i) => {
      const cell = cells[i];
      const box = cell?.querySelector(".sym");
      if (!cell || !box) return;

      if (!sym) { box.innerHTML = ""; return; }

      box.innerHTML = svgFor(sym);

      const key = normalizeKey(sym);

      // ✅ 경로 FIX: slot.html이 /games/ 에 있으므로 "./img/slot/"
      if (AVAILABLE_PNG.has(key)) {
        const img = document.createElement("img");
        img.src = `./img/slot/${key}.png`;   // ✅ 정답 경로
        img.alt = key;
        img.onerror = () => img.remove();
        box.appendChild(img);
      }
    });
  }

  function randomSymbolKey() {
    const arr = Array.from(AVAILABLE_PNG);
    return arr[(Math.random() * arr.length) | 0];
  }
  function buildRandomGrid() {
    const g = [];
    for (let r = 0; r < ROWS; r++) {
      const row = [];
      for (let c = 0; c < COLS; c++) row.push(randomSymbolKey());
      g.push(row);
    }
    return g;
  }

  async function spinVisual(duration = 700) {
    const cells = ensureCells();
    if (!cells.length) return;

    cells.forEach((cell, i) => {
      cell.classList.remove("tu-spin-drop");
      cell.classList.add("tu-spin-blur");
      const col = i % COLS;
      cell.style.animationDelay = `${col * 45}ms`;
    });

    const start = performance.now();
    while (performance.now() - start < duration) {
      renderGrid(buildRandomGrid());
      await sleep(70);
    }

    cells.forEach((cell) => {
      cell.classList.remove("tu-spin-blur");
      cell.style.animationDelay = "";
    });
  }

  function dropFinal() {
    const cells = ensureCells();
    cells.forEach((cell, i) => {
      const col = i % COLS;
      cell.classList.remove("tu-spin-drop");
      void cell.offsetWidth;
      cell.classList.add("tu-spin-drop");
      cell.style.animationDelay = `${col * 55}ms`;
    });
    setTimeout(() => {
      cells.forEach((cell) => (cell.style.animationDelay = ""));
    }, 600);
  }

  // ---------- sound ----------
  const SOUND_FILES = {
    start: "./sounds/start-button-sound.MP3",
    spin: "./sounds/spining-sound.MP3",
    stop: "./sounds/stop-stop-stop-sound.MP3",
    win:  "./sounds/win-sound.MP3",
    lose: "./sounds/lose-sound.MP3",
    jackpot: "./sounds/jackpot-sound.MP3",
  };

  const sound = {
    enabled: true,
    unlocked: false,
    a: {},
  };

  function loadSoundPref() {
    const v = localStorage.getItem("uniqueSlotSound");
    if (v === "0") sound.enabled = false;
    if (v === "1") sound.enabled = true;
  }
  function saveSoundPref() {
    localStorage.setItem("uniqueSlotSound", sound.enabled ? "1" : "0");
  }

  function ensureAudio() {
    if (sound.a.start) return;
    for (const [k, src] of Object.entries(SOUND_FILES)) {
      const au = new Audio(src);
      au.preload = "auto";
      au.volume = 0.9;
      sound.a[k] = au;
    }
    sound.a.spin.loop = true;
    sound.a.spin.volume = 0.55;
  }

  async function unlockAudioOnce() {
    if (sound.unlocked) return true;
    try {
      ensureAudio();
      const au = sound.a.start;
      au.currentTime = 0;
      await au.play();
      au.pause();
      au.currentTime = 0;
      sound.unlocked = true;
      return true;
    } catch {
      return false;
    }
  }

  function sfx(name) {
    if (!sound.enabled) return;
    ensureAudio();
    const au = sound.a[name];
    if (!au) return;
    try {
      au.pause();
      au.currentTime = 0;
      au.play().catch(() => {});
    } catch {}
  }

  function spinLoop(on) {
    ensureAudio();
    const au = sound.a.spin;
    if (!au) return;
    if (!sound.enabled) {
      au.pause();
      au.currentTime = 0;
      return;
    }
    if (on) au.play().catch(() => {});
    else { au.pause(); au.currentTime = 0; }
  }

  // ---------- state ----------
  let identity = null;
  let autoOn = false;
  let spinning = false;
  let autoTimer = null;

  let betValue = 10;

  function loadBetPref() {
    const v = Number(localStorage.getItem("uniqueSlotBet") || 10);
    if (Number.isFinite(v)) betValue = clamp(Math.round(v / 5) * 5, 10, 500);
  }
  function saveBetPref() {
    localStorage.setItem("uniqueSlotBet", String(betValue));
  }

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
    autoTimer = setInterval(() => { if (!spinning) spin(); }, 1250);
  }
  function toggleAuto() {
    if (autoOn) stopAuto(); else startAuto();
  }

  function setWalletUI(n) {
    const v = Number(n);
    if (!Number.isFinite(v)) return;
    setText(ui.wallet, fmt(v));
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const uu = JSON.parse(raw);
        uu.balance = v;
        localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
      }
      localStorage.setItem("myUtPoints", String(v));
    } catch {}
  }

  function applyCompactButtons() {
    if (ui.btnAuto) ui.btnAuto.classList.add("tu-compact");
    if (ui.btnSpin) ui.btnSpin.classList.add("tu-compact");
    if (ui.btnSound) ui.btnSound.classList.add("btnSound", "tu-compact");
  }

  function ensureSoundButton() {
    if (!ui.btnSpin || ui.btnSound) return;

    const row = ui.btnSpin.closest(".row") || ui.btnSpin.parentElement;
    if (!row) return;

    const btn = document.createElement("button");
    btn.className = "btn btnAuto btnSound tu-compact";
    btn.id = "btnSound";
    btn.textContent = sound.enabled ? "SOUND ON" : "SOUND OFF";
    btn.addEventListener("click", async () => {
      await unlockAudioOnce();
      sound.enabled = !sound.enabled;
      btn.textContent = sound.enabled ? "SOUND ON" : "SOUND OFF";
      saveSoundPref();
      if (!sound.enabled) spinLoop(false);
      sfx("start");
    });

    if (ui.btnAuto && row.contains(ui.btnAuto)) ui.btnAuto.insertAdjacentElement("afterend", btn);
    else row.insertBefore(btn, ui.btnSpin);

    ui.btnSound = btn;
  }

  function ensureBetControls() {
    if (!ui.bet) return;
    const statBox = ui.bet.closest(".stat") || ui.bet.parentElement;
    if (!statBox) return;

    if (document.getElementById("btnBetMinus")) return;

    const bar = document.createElement("div");
    bar.className = "tu-betbar";

    const minus = document.createElement("button");
    minus.id = "btnBetMinus";
    minus.className = "tu-betbtn";
    minus.textContent = "-5";

    const meta = document.createElement("div");
    meta.id = "uiBetHint";
    meta.className = "tu-betmeta";
    meta.textContent = `BET: ${betValue} UT (±5)`;

    const plus = document.createElement("button");
    plus.id = "btnBetPlus";
    plus.className = "tu-betbtn";
    plus.textContent = "+5";

    minus.addEventListener("click", () => {
      betValue = clamp(betValue - 5, 10, 500);
      saveBetPref();
      setText(ui.bet, fmt(betValue));
      meta.textContent = `BET: ${betValue} UT (±5)`;
      sfx("start");
    });

    plus.addEventListener("click", () => {
      betValue = clamp(betValue + 5, 10, 500);
      saveBetPref();
      setText(ui.bet, fmt(betValue));
      meta.textContent = `BET: ${betValue} UT (±5)`;
      sfx("start");
    });

    bar.appendChild(minus);
    bar.appendChild(meta);
    bar.appendChild(plus);
    statBox.appendChild(bar);

    ui.betHint = meta;
  }

  function buildPayTable() {
    if (!ui.pay) return;
    ui.pay.innerHTML = `
      <div class="ptItem"><div class="ptLeft"><div class="badge">2×</div><div>같은 심볼 2개</div></div><div class="ptMul">WIN</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">3×</div><div>같은 심볼 3개</div></div><div class="ptMul">WIN</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">4×</div><div>같은 심볼 4개</div></div><div class="ptMul">BIG WIN</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">5×</div><div>같은 심볼 5개</div></div><div class="ptMul">MEGA</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">JP</div><div><b>PRO10</b> 5개 = JACKPOT</div></div><div class="ptMul">SPECIAL</div></div>
    `;
  }

  function movePayTableUnderReels() {
    if (!ui.reelWrap || !ui.pay) return;
    if (ui.reelWrap.querySelector(".tu-paywrap")) return;

    const wrap = document.createElement("div");
    wrap.className = "tu-paywrap";

    const title = document.createElement("div");
    title.className = "tu-paytitle";
    title.textContent = "PAY TABLE";

    wrap.appendChild(title);
    wrap.appendChild(ui.pay);
    ui.reelWrap.appendChild(wrap);
  }

  async function loadState() {
    const u = identity?.id;
    if (!u) return null;

    setNote("SYNC…");
    const js = await fetchJSON(`${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}`, {}, 20000);

    if (!js?.ok) {
      setResult("STATE ERROR", true);
      setWalletUI(identity.balance);
      setNote(`state fail: ${js?.error || "unknown"}`, true);
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim() ||
      identity.name || identity.nickname || identity.id;

    setText(ui.player, displayName);

    const ut = pickUT(js);
    if (ut !== null) setWalletUI(ut);
    else setWalletUI(identity.balance);

    setText(ui.jackpot, fmt(js.jackpot ?? js.jackpotUT ?? js.jackpot_ut ?? 0));

    const srvBet = Number(js.bet);
    if (Number.isFinite(srvBet) && srvBet > 0) {
      betValue = clamp(Math.round(srvBet / 5) * 5, 10, 500);
      saveBetPref();
    }
    setText(ui.bet, fmt(betValue));
    if (ui.betHint) ui.betHint.textContent = `BET: ${betValue} UT (±5)`;

    setResult("READY");
    setNote("");

    if (js.grid) renderGrid(js.grid);

    return js;
  }

  async function spin() {
    if (spinning) return;
    spinning = true;
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      await unlockAudioOnce();
      sfx("start");

      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      setNote("SPINNING…");
      spinLoop(true);

      const visual = spinVisual(750);

      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u, bet: betValue })
      }, 25000);

      await visual;

      spinLoop(false);
      sfx("stop");

      if (!js?.ok) {
        setResult("SPIN ERROR", true);
        const err = String(js?.error || "unknown");
        if (err.includes("user_not_found_in_sheet")) {
          setNote("유저가 슬롯 시트에 없음 → 메인에서 등록/동기화 후 다시 오세요.", true);
          setWalletUI(Number(localStorage.getItem("myUtPoints") || identity.balance || 0));
          stopAuto();
          return;
        }
        setNote(`spin fail: ${err}`, true);
        if (err.includes("insufficient")) stopAuto();
        return;
      }

      const ut = pickUT(js);
      if (ut !== null) setWalletUI(ut);

      setText(ui.jackpot, fmt(js.jackpot ?? js.jackpotUT ?? js.jackpot_ut ?? 0));

      const srvBet = Number(js.bet);
      if (Number.isFinite(srvBet) && srvBet > 0) {
        betValue = clamp(Math.round(srvBet / 5) * 5, 10, 500);
        saveBetPref();
      }
      setText(ui.bet, fmt(betValue));
      if (ui.betHint) ui.betHint.textContent = `BET: ${betValue} UT (±5)`;

      renderGrid(js.grid);
      dropFinal();

      const betCharged = Number(js.betCharged ?? js.bet_cost ?? betValue);
      const win = Number(js.win ?? js.payout ?? 0);
      const delta = win - betCharged;

      if (delta > 0) { setResult(`WIN +${fmt(delta)} UT`); sfx("win"); }
      else if (delta < 0) { setResult(`LOSE ${fmt(delta)} UT`); sfx("lose"); }
      else setResult("EVEN 0 UT");

      if (js.jackpotHit || js.isJackpot) {
        setResult(`JACKPOT!!! +${fmt(js.jackpotWin ?? win)} UT`);
        sfx("jackpot");
      }

      setNote("");

    } catch (e) {
      spinLoop(false);
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
    injectStyleOnce();

    identity = getLocalUser();
    if (!identity) return redirectToGate();

    loadSoundPref();
    loadBetPref();

    setText(ui.player, identity.name || identity.nickname || identity.id);
    setWalletUI(identity.balance || Number(localStorage.getItem("myUtPoints") || 0));
    setText(ui.bet, fmt(betValue));

    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", () => {
      unlockAudioOnce();
      sfx("start");
      if (autoOn) { autoOn = false; stopAuto(); }
      else startAuto();
    });

    ensureSoundButton();
    ensureBetControls();
    applyCompactButtons();

    buildPayTable();
    movePayTableUnderReels();

    renderGrid(null);
    await loadState();

    console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__ || "no_version");
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
