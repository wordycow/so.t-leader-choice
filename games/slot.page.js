/* games/slot.page.js
 * THE UNIQUE SLOT (final-ish)
 * - localStorage(uniqueCurrentUser) 기반 자동 로그인
 * - WORKER_BASE /slot/state, /slot/spin
 * - UT 표시 필드(ut/totalUT/총UT 등) 다 흡수
 * - 사운드 ON/OFF + 베팅 -5/+5 (기본 10)
 * - pay table을 릴 아래로 이동(HTML 수정 없이 JS로 재배치)
 * - 이미지 요청은 repo에 실제 존재하는 pro1~pro10, star1~3만 로드(404 방지)
 * - 스핀 시 위→아래로 “떨어지는” 느낌의 수직 드롭 애니 + 랜덤 프리롤
 */

(() => {
  "use strict";

  // ✅ 워커 주소(필요하면 여기만)
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 버전 마커
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_final_v1";

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
    // 메인/게이트에서 저장한 값 우선 사용
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
        // balance가 있을 수도 / myUtPoints가 있을 수도
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
      try {
        js = JSON.parse(text);
      } catch {
        js = { ok: false, error: "bad_json", raw: text };
      }
      if (!res.ok && js && typeof js === "object" && !js.error) js.error = `http_${res.status}`;
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  function pickUT(obj) {
    // ✅ 시트/워커가 필드명을 바꿔도 여기서 다 흡수
    // 가능한 후보들을 다 뒤진다.
    const cands = [
      obj?.ut,
      obj?.UT,
      obj?.totalUT,
      obj?.total_ut,
      obj?.totalPoints,
      obj?.points,
      obj?.myUT,
      obj?.wallet,
      obj?.balance,
      obj?.총UT,
      obj?.["총 UT"],
      obj?.["total UT"],
      obj?.["TOTAL_UT"],
    ];
    for (const v of cands) {
      const n = Number(v);
      if (Number.isFinite(n)) return n;
    }
    return null;
  }

  // ---------- DOM binding (slot.html id 기준) ----------
  const ui = {
    title: $id("uiTitle"),
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
    // (없으면 JS가 만들어줌)
    btnSound: $id("btnSound"),
    btnBetMinus: $id("btnBetMinus"),
    btnBetPlus: $id("btnBetPlus"),
    betHint: $id("uiBetHint"),
  };

  // ---------- inject minimal CSS (애니/버튼/배치) ----------
  function injectStyleOnce() {
    if (document.getElementById("slotPageInjectedStyle")) return;
    const st = document.createElement("style");
    st.id = "slotPageInjectedStyle";
    st.textContent = `
      /* 버튼 사이즈 강제 축소 */
      .btn.tu-compact { padding: 10px 12px !important; border-radius: 14px !important; font-size: 12px !important; }
      .btnAuto.tu-compact { width: 120px !important; }
      .btnSound.tu-compact { width: 140px !important; }

      /* 베팅 컨트롤 */
      .tu-betbar{ display:flex; align-items:center; gap:10px; margin-top:10px; }
      .tu-betbtn{
        width:44px; height:40px;
        border-radius:14px;
        border:1px solid rgba(33,246,255,.22);
        background: rgba(4,6,16,.40);
        color: rgba(215,228,255,.92);
        font-weight:900;
        cursor:pointer;
        box-shadow: 0 0 0 1px rgba(255,43,214,.10) inset, 0 18px 50px rgba(0,0,0,.25);
      }
      .tu-betmeta{
        font-family: "Share Tech Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 12px;
        color: rgba(215,228,255,.82);
        letter-spacing: .06em;
      }

      /* 스핀 드롭 애니 (위→아래) */
      .tu-spin-drop{
        animation: tuDrop .35s ease-in forwards;
      }
      @keyframes tuDrop{
        0%{ transform: translateY(-36px); filter: blur(1px) saturate(1.25); opacity:.0; }
        60%{ opacity:1; }
        100%{ transform: translateY(0); filter:none; opacity:1; }
      }
      .tu-spin-blur{
        animation: tuBlur .7s linear infinite;
      }
      @keyframes tuBlur{
        0%{ transform: translateY(-18px); filter: blur(2px) saturate(1.3); }
        100%{ transform: translateY(18px); filter: blur(2px) saturate(1.3); }
      }

      /* paytable을 릴 아래로 옮길 때 프레임 유지 */
      .tu-paywrap{
        margin-top: 12px;
      }
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

  // repo에 실제 있는 파일만 요청(404 방지)
  const AVAILABLE_PNG = new Set([
    "star1", "star2", "star3",
    "pro1", "pro2", "pro3", "pro4", "pro5", "pro6", "pro7", "pro8", "pro9", "pro10",
  ]);

  // 서버 심볼값 -> 파일키로 정규화
  function toKey(sym) {
    const s = String(sym || "").trim().toLowerCase();
    // 예: "STAR1" / "star_1" / "star-1" / "pro10" / "PRO 10"
    const cleaned = s.replace(/[^a-z0-9]/g, "");
    return cleaned; // star1, pro10
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

  // 네온 SVG(이미지 없어도 괜찮게)
  function svgFor(sym) {
    const key = toKey(sym).toUpperCase();
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

    // grid: [[..5],[..5],[..5]]
    const flat = [];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) flat.push(grid?.[r]?.[c] ?? "");
    }

    flat.forEach((sym, i) => {
      const cell = cells[i];
      const box = cell?.querySelector(".sym");
      if (!cell || !box) return;

      if (!sym) {
        box.innerHTML = "";
        return;
      }

      box.innerHTML = svgFor(sym);

      // ✅ 실제 존재하는 파일만 얹는다(404 방지)
      const key = toKey(sym);
      if (AVAILABLE_PNG.has(key)) {
        const img = document.createElement("img");
        img.src = `../img/slot/${key}.png`; // ✅ 실제 repo: games/img/slot/pro1.png ...
        img.alt = key;
        img.onload = () => {};
        img.onerror = () => img.remove();
        box.appendChild(img);
      }
    });
  }

  function randomSymbolKey() {
    // 프리롤용 랜덤
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

    // blur 애니 on
    cells.forEach((cell, i) => {
      cell.classList.remove("tu-spin-drop");
      cell.classList.add("tu-spin-blur");
      // 열별 딜레이 느낌 주기
      const col = i % COLS;
      cell.style.animationDelay = `${col * 45}ms`;
    });

    const start = performance.now();
    while (performance.now() - start < duration) {
      renderGrid(buildRandomGrid());
      await sleep(70);
    }

    // blur off, drop on (최종 결과는 호출하는 쪽에서 renderGrid 후 drop)
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
      // reflow
      void cell.offsetWidth;
      cell.classList.add("tu-spin-drop");
      cell.style.animationDelay = `${col * 55}ms`;
    });

    // 애니 끝나면 딜레이 제거
    setTimeout(() => {
      cells.forEach((cell) => (cell.style.animationDelay = ""));
    }, 600);
  }

  // ---------- sound ----------
  const SOUND_FILES = {
    start: "../sounds/start-button-sound.MP3",
    spin: "../sounds/spining-sound.MP3",           // ✅ repo 이름: spining-sound.MP3 (오타 그대로)
    stop: "../sounds/stop-stop-stop-sound.MP3",
    win:  "../sounds/win-sound.MP3",
    lose: "../sounds/lose-sound.MP3",
    jackpot: "../sounds/jackpot-sound.MP3",
  };

  const sound = {
    enabled: true,
    unlocked: false,
    a: {},
    spinLoop: null,
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
      // 아주 짧게 재생했다가 멈춤(브라우저 정책 해제)
      const au = sound.a.start;
      au.currentTime = 0;
      await au.play();
      au.pause();
      au.currentTime = 0;
      sound.unlocked = true;
      return true;
    } catch {
      // 사용자가 “직접” 클릭하면 다시 시도되게 둔다
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
    if (on) {
      au.play().catch(() => {});
    } else {
      au.pause();
      au.currentTime = 0;
    }
  }

  // ---------- state ----------
  let identity = null;
  let autoOn = false;
  let spinning = false;
  let autoTimer = null;

  // bet local override (서버가 bet을 안 주거나 무시해도 UI 유지)
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
    autoTimer = setInterval(() => {
      if (!spinning) spin();
    }, 1250);
  }

  function toggleAuto() {
    if (autoOn) stopAuto();
    else startAuto();
  }

  function applyCompactButtons() {
    if (ui.btnAuto) ui.btnAuto.classList.add("tu-compact");
    if (ui.btnSpin) ui.btnSpin.classList.add("tu-compact");
    if (ui.btnSound) ui.btnSound.classList.add("btnSound", "tu-compact");
  }

  function ensureSoundButton() {
    if (!ui.btnSpin || ui.btnSound) return;

    // 버튼 줄에 SOUND 버튼 삽입 (AUTO | SOUND | SPIN)
    const row = ui.btnSpin.closest(".row") || ui.btnSpin.parentElement;
    if (!row) return;

    const btn = document.createElement("button");
    btn.className = "btn btnAuto btnSound tu-compact";
    btn.id = "btnSound";
    btn.textContent = sound.enabled ? "SOUND ON" : "SOUND OFF";
    btn.style.width = "140px";
    btn.addEventListener("click", async () => {
      await unlockAudioOnce();
      sound.enabled = !sound.enabled;
      btn.textContent = sound.enabled ? "SOUND ON" : "SOUND OFF";
      saveSoundPref();
      if (!sound.enabled) spinLoop(false);
      sfx("start");
    });

    // AUTO 다음에 넣기
    if (ui.btnAuto && row.contains(ui.btnAuto)) {
      ui.btnAuto.insertAdjacentElement("afterend", btn);
    } else {
      row.insertBefore(btn, ui.btnSpin);
    }

    ui.btnSound = btn;
  }

  function ensureBetControls() {
    // slot.html의 BET 영역(uiBet) 아래에 -5 / 메타 / +5 줄 생성
    if (!ui.bet) return;
    const statBox = ui.bet.closest(".stat") || ui.bet.parentElement;
    if (!statBox) return;

    // 이미 있으면 패스
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

    // BET 숫자 아래에 삽입
    statBox.appendChild(bar);

    ui.btnBetMinus = minus;
    ui.btnBetPlus = plus;
    ui.betHint = meta;
  }

  function buildPayTable() {
    // ✅ 쓸데없는 “느낌” 같은 문장 제거
    // 지금은 “족보”만 딱 보여주고, 배당/확률은 서버 로직에서 결정
    if (!ui.pay) return;

    ui.pay.innerHTML = `
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">2×</div><div>같은 심볼 2개</div></div>
        <div class="ptMul">WIN</div>
      </div>
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">3×</div><div>같은 심볼 3개</div></div>
        <div class="ptMul">WIN</div>
      </div>
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">4×</div><div>같은 심볼 4개</div></div>
        <div class="ptMul">BIG WIN</div>
      </div>
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">5×</div><div>같은 심볼 5개</div></div>
        <div class="ptMul">MEGA</div>
      </div>
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">JP</div><div><b>PRO10</b> 5개 = JACKPOT</div></div>
        <div class="ptMul">SPECIAL</div>
      </div>
    `;
  }

  function movePayTableUnderReels() {
    // ✅ pay table을 릴 아래로 이동 (HTML 수정 없이)
    if (!ui.reelWrap || !ui.reels || !ui.pay) return;
    const already = ui.reelWrap.querySelector(".tu-paywrap");
    if (already) return;

    const wrap = document.createElement("div");
    wrap.className = "tu-paywrap";

    const title = document.createElement("div");
    title.className = "tu-paytitle";
    title.textContent = "PAY TABLE";

    wrap.appendChild(title);
    wrap.appendChild(ui.pay); // 기존 paytable 요소를 통째로 이동
    ui.reelWrap.appendChild(wrap);
  }

  function setWalletUI(n) {
    const v = Number(n);
    if (!Number.isFinite(v)) return;
    setText(ui.wallet, fmt(v));
    // localStorage 동기화
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

  async function loadState() {
    const u = identity?.id;
    if (!u) return null;

    setNote("SYNC…");
    const js = await fetchJSON(`${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}`, {}, 20000);

    if (!js?.ok) {
      setResult("STATE ERROR", true);
      // ✅ UT는 로컬값이라도 보여주고, 에러만 노트에 표시
      setWalletUI(identity.balance);
      setNote(`state fail: ${js?.error || "unknown"}`, true);
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim() ||
      identity.name ||
      identity.nickname ||
      identity.id;

    setText(ui.player, displayName);

    // ✅ UT 필드 흡수
    const ut = pickUT(js);
    if (ut !== null) setWalletUI(ut);
    else setWalletUI(identity.balance);

    setText(ui.jackpot, fmt(js.jackpot ?? js.jackpotUT ?? js.jackpot_ut ?? 0));

    // bet
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

      // ✅ 먼저 “도는 연출” (API 기다리는 동안)
      const visual = spinVisual(750);

      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u, bet: betValue }) // 서버가 bet 받으면 적용, 아니면 무시
      }, 25000);

      await visual;

      spinLoop(false);
      sfx("stop");

      if (!js?.ok) {
        setResult("SPIN ERROR", true);

        const err = String(js?.error || "unknown");
        if (err.includes("user_not_found_in_sheet")) {
          setNote("유저가 슬롯 시트에 없음 → 메인에서 등록/동기화 후 다시 오세요.", true);
          // 로컬 UT는 유지 표시
          setWalletUI(Number(localStorage.getItem("myUtPoints") || identity.balance || 0));
          stopAuto();
          return;
        }

        setNote(`spin fail: ${err}`, true);
        if (err.includes("insufficient")) stopAuto();
        return;
      }

      // ✅ UT 필드 흡수
      const ut = pickUT(js);
      if (ut !== null) setWalletUI(ut);

      setText(ui.jackpot, fmt(js.jackpot ?? js.jackpotUT ?? js.jackpot_ut ?? 0));

      // bet 서버가 내려주면 동기화
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

      if (delta > 0) {
        setResult(`WIN +${fmt(delta)} UT`);
        sfx("win");
      } else if (delta < 0) {
        setResult(`LOSE ${fmt(delta)} UT`);
        sfx("lose");
      } else {
        setResult(`EVEN 0 UT`);
      }

      // jackpot 플래그(있으면)
      if (js.jackpotHit || js.isJackpot) {
        setResult(`JACKPOT!!! +${fmt(js.jackpotWin ?? win)} UT`);
        sfx("jackpot");
        if (ui.reelWrap) ui.reelWrap.classList.add("jackpotPulse");
        setTimeout(() => ui.reelWrap && ui.reelWrap.classList.remove("jackpotPulse"), 1400);
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

    // UI 초기 표시 (서버 전이라도 UT 먼저 띄우기)
    setText(ui.player, identity.name || identity.nickname || identity.id);
    setWalletUI(identity.balance || Number(localStorage.getItem("myUtPoints") || 0));

    setText(ui.bet, fmt(betValue));

    // 버튼 바인딩
    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", () => {
      unlockAudioOnce();
      sfx("start");
      toggleAuto();
    });

    // 동적 UI 생성
    ensureSoundButton();
    ensureBetControls();
    applyCompactButtons();

    // paytable 처리
    buildPayTable();
    movePayTableUnderReels();

    // 초기 빈 그리드
    renderGrid(null);

    // 상태 로드
    await loadState();

    console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__ || "no_version");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
