/* games/slot.page.js
 * THE UNIQUE SLOT - FINAL v4
 * ✅ UT 즉시 표시 + worker 동기화
 * ✅ SOUND ON/OFF 버튼
 * ✅ BET -5 / +5 (기본 10, 5~200 범위)
 * ✅ 세로(위→아래) 슬롯 스핀 연출 + 컬럼별 멈춤
 * ✅ pay table: 2/3/4/5 매치 안내 + PRO10 5개 = JACKPOT(희귀)
 * ✅ 404 제거: 존재하는 이미지(pro1~10, star1~3)만 요청
 */

(() => {
  "use strict";

  // ======================
  // CONFIG
  // ======================
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";
  const VERSION = "slot.page.js@2026-01-10_final_v4";
  window.__UNIQUE_SLOT_PAGE__ = VERSION;

  // slot.html(= /games/slot.html) 기준 상대경로
  const IMG_BASE = "./img/slot/";
  const SOUND_BASE = "./sounds/";

  // 실제 존재하는 심볼만 (slide1~8 제거 반영)
  const SYMBOLS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // BET 규칙
  const BET_STEP = 5;
  const BET_MIN = 5;
  const BET_MAX = 200;
  const BET_DEFAULT = 10;

  // ======================
  // DOM
  // ======================
  const $id = (id) => document.getElementById(id);

  const ui = {
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

  // ======================
  // STYLE INJECT
  // ======================
  function injectStyleOnce() {
    if (document.getElementById("unique-slot-style-v4")) return;
    const s = document.createElement("style");
    s.id = "unique-slot-style-v4";
    s.textContent = `
      /* 컨트롤 바 (BET +/- , SOUND) */
      .slotCtlRow{ display:flex; gap:10px; align-items:center; margin-top:10px; }
      .slotMiniBtn{
        cursor:pointer;
        border-radius:12px;
        padding:8px 10px;
        font-weight:900;
        letter-spacing:.08em;
        font-family: "Orbitron", system-ui, sans-serif;
        border:1px solid rgba(33,246,255,.20);
        background: rgba(4,6,16,.40);
        color: rgba(215,228,255,.92);
        box-shadow: 0 0 0 1px rgba(255,43,214,.10) inset, 0 12px 28px rgba(0,0,0,.35);
        user-select:none;
      }
      .slotMiniBtn:active{ transform: translateY(1px); }
      .slotMiniBtn[disabled]{ opacity:.55; cursor:not-allowed; }
      .slotPill{
        padding:7px 10px;
        border-radius:999px;
        border:1px solid rgba(140,170,255,.14);
        background: rgba(4,6,16,.30);
        font-family:"Share Tech Mono", ui-monospace, monospace;
        font-size:12px;
        color: rgba(215,228,255,.82);
        white-space:nowrap;
      }

      /* 스핀 연출(위→아래) */
      #uiReels.isSpinning { filter: blur(.6px) saturate(1.2) contrast(1.08); }
      #uiReels.isSpinning .cell .sym{ animation: symDrop .10s linear infinite; }
      @keyframes symDrop { 0%{transform:translateY(-10px); opacity:.75} 100%{transform:translateY(10px); opacity:.95} }

      /* 컬럼 멈출 때 타격감 */
      .colSnap { animation: colSnap .16s ease-out 1; }
      @keyframes colSnap { 0%{transform:scale(.985)} 100%{transform:scale(1)} }

      #uiReels.winFlash { animation: winFlash .55s ease-out 1; }
      @keyframes winFlash{
        0%{ box-shadow: 0 0 0 rgba(0,0,0,0); }
        45%{ box-shadow: 0 0 28px rgba(33,246,255,.22), 0 0 34px rgba(255,43,214,.16); }
        100%{ box-shadow: 0 0 0 rgba(0,0,0,0); }
      }

      #uiReelWrap.jackpotPulse { animation: jackpotPulse .9s ease-in-out 2; }
      @keyframes jackpotPulse{
        0%{ transform: scale(1); }
        50%{ transform: scale(1.015); }
        100%{ transform: scale(1); }
      }

      /* paytable 좀 더 읽기 좋게 */
      .ptTitle{
        font-family:"Orbitron", system-ui, sans-serif;
        font-weight:900;
        letter-spacing:.12em;
        font-size:12px;
        opacity:.85;
        margin-bottom:8px;
      }
      .ptGrid{ display:grid; gap:8px; }
      .ptRow{
        display:flex; align-items:center; justify-content:space-between;
        padding:9px 10px;
        border-radius:14px;
        border:1px solid rgba(140,170,255,.12);
        background: rgba(4,6,16,.30);
        box-shadow: 0 0 0 1px rgba(33,246,255,.07) inset;
        font-size:12px;
      }
      .ptLeft{ display:flex; align-items:center; gap:10px; }
      .ptBadge{
        width:26px;height:26px;border-radius:10px;
        border:1px solid rgba(33,246,255,.22);
        display:flex;align-items:center;justify-content:center;
        background: rgba(2,6,23,.35);
        font-weight:900;
        font-family:"Share Tech Mono", ui-monospace, monospace;
        box-shadow: 0 0 18px rgba(33,246,255,.12);
        flex:0 0 26px;
      }
      .ptHint{ opacity:.78; font-family:"Share Tech Mono", ui-monospace, monospace; }
    `;
    document.head.appendChild(s);
  }

  // ======================
  // Utils
  // ======================
  const toNum = (v) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  };

  function fmtInt(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return "0";
    return String(Math.floor(n));
  }

  function setText(el, v) {
    if (!el) return;
    el.textContent = String(v ?? "");
  }

  function setNote(msg, isError=false) {
    if (!ui.note) return;
    ui.note.textContent = msg || "";
    ui.note.style.opacity = msg ? "1" : "0.75";
    ui.note.style.color = isError ? "rgba(255,120,160,.95)" : "rgba(215,228,255,.82)";
  }

  function setResult(msg, isError=false) {
    if (!ui.result) return;
    ui.result.textContent = msg || "";
    ui.result.style.color = isError ? "rgba(255,120,160,.95)" : "";
  }

  function pickUT(js) {
    if (!js || typeof js !== "object") return null;
    const candidates = [
      js.ut, js.UT, js.balance, js.wallet, js.points, js.utPoints, js.myUtPoints,
      js.user?.ut, js.user?.balance, js.data?.ut, js.data?.balance, js.state?.ut
    ];
    for (const c of candidates) {
      const n = toNum(c);
      if (n !== null) return n;
    }
    return null;
  }

  async function fetchJSON(url, opt = {}, timeoutMs = 20000) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort("timeout"), timeoutMs);
    try {
      const res = await fetch(url, { ...opt, signal: ctrl.signal, cache: "no-store" });
      const text = await res.text();
      let js;
      try { js = JSON.parse(text); } catch { js = { ok:false, error:"bad_json", raw:text }; }
      if (!res.ok && js && typeof js === "object" && !js.error) js.error = `http_${res.status}`;
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  // ======================
  // Local User / State
  // ======================
  function getLocalUser() {
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return null;
      const u = JSON.parse(raw);
      const id = String(u?.id || "").trim().toLowerCase();
      if (!id) return null;

      const myUt = toNum(localStorage.getItem("myUtPoints"));
      const bal = toNum(u?.balance);

      return {
        id,
        name: String(u?.name || "").trim(),
        nickname: String(u?.nickname || "").trim(),
        balance: bal ?? myUt ?? 0,
      };
    } catch {
      return null;
    }
  }

  function redirectToGate() {
    location.href = "../the-unique-gate.html";
  }

  function betKey(uid){ return `slotBet_${uid}`; }
  function soundKey(uid){ return `slotSound_${uid}`; }

  function loadBet(uid) {
    const v = toNum(localStorage.getItem(betKey(uid)));
    if (v === null) return BET_DEFAULT;
    return clampBet(v);
  }

  function saveBet(uid, v) {
    localStorage.setItem(betKey(uid), String(clampBet(v)));
  }

  function clampBet(v) {
    let n = Number(v);
    if (!Number.isFinite(n)) n = BET_DEFAULT;
    n = Math.round(n / BET_STEP) * BET_STEP;
    if (n < BET_MIN) n = BET_MIN;
    if (n > BET_MAX) n = BET_MAX;
    return n;
  }

  function loadSoundOn(uid) {
    const raw = localStorage.getItem(soundKey(uid));
    if (raw === null) return true; // 기본 ON
    return raw === "1";
  }
  function saveSoundOn(uid, on) {
    localStorage.setItem(soundKey(uid), on ? "1" : "0");
  }

  // ======================
  // Reels Render (15 cells)
  // ======================
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

  function isPngSymbol(sym) {
    const s = String(sym || "").toLowerCase();
    return /^pro\d+$/.test(s) || /^star\d+$/.test(s);
  }

  function setCellSymbol(cells, r, c, sym) {
    const idx = r * COLS + c;
    const cell = cells[idx];
    const box = cell?.querySelector?.(".sym");
    if (!box) return;

    const s = String(sym || "");
    box.innerHTML = "";
    if (!s) return;

    // 404 방지: pro/star만 png 요청
    if (isPngSymbol(s)) {
      const img = document.createElement("img");
      img.src = `${IMG_BASE}${s.toLowerCase()}.png`;
      img.alt = s;
      img.style.width = "88%";
      img.style.height = "88%";
      img.style.objectFit = "contain";
      img.onerror = () => {
        // 혹시 대소문자 혼합이면 한 번 더
        img.src = `${IMG_BASE}${s}.png`;
        img.onerror = () => img.remove();
      };
      box.appendChild(img);
    } else {
      box.textContent = s;
    }
  }

  function renderGrid(grid) {
    const cells = ensureCells();
    if (!cells.length) return;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        setCellSymbol(cells, r, c, grid?.[r]?.[c] ?? "");
      }
    }
  }

  function randSym() {
    return SYMBOLS[(Math.random() * SYMBOLS.length) | 0];
  }

  // ======================
  // Spin Visual (vertical + column stop)
  // ======================
  let colTimers = [];
  let spinningVisual = false;

  function startSpinVisual() {
    if (!ui.reels) return;
    spinningVisual = true;
    ui.reels.classList.add("isSpinning");

    const cells = ensureCells();
    colTimers.forEach(t => clearInterval(t));
    colTimers = [];

    // 각 컬럼별로 “위→아래”로 심볼이 밀려 내려오는 느낌
    for (let c = 0; c < COLS; c++) {
      // 초기 컬럼 상태
      let col = [randSym(), randSym(), randSym()];
      const timer = setInterval(() => {
        // 위에서 하나 들어오고, 아래로 밀림
        col = [randSym(), col[0], col[1]];
        for (let r = 0; r < ROWS; r++) setCellSymbol(cells, r, c, col[r]);
      }, 60 + c * 8); // 컬럼마다 약간 다른 속도(자연스러움)
      colTimers.push(timer);
    }
  }

  function stopSpinVisualWithFinal(finalGrid, onEachColStop) {
    // 컬럼별로 순차 멈추기
    const cells = ensureCells();
    colTimers.forEach(t => clearInterval(t));
    colTimers = [];

    const baseDelay = 120; // 컬럼 간 딜레이
    for (let c = 0; c < COLS; c++) {
      setTimeout(() => {
        for (let r = 0; r < ROWS; r++) setCellSymbol(cells, r, c, finalGrid?.[r]?.[c] ?? "");
        // 스냅 느낌
        for (let r = 0; r < ROWS; r++) {
          const idx = r * COLS + c;
          const cell = cells[idx];
          cell?.classList?.add("colSnap");
          setTimeout(() => cell?.classList?.remove("colSnap"), 180);
        }
        if (typeof onEachColStop === "function") onEachColStop(c);
        if (c === COLS - 1) {
          spinningVisual = false;
          ui.reels?.classList?.remove("isSpinning");
        }
      }, c * baseDelay);
    }
  }

  function forceStopVisual() {
    colTimers.forEach(t => clearInterval(t));
    colTimers = [];
    spinningVisual = false;
    ui.reels?.classList?.remove("isSpinning");
  }

  // ======================
  // Sounds (ON/OFF)
  // ======================
  const sounds = {
    start:   new Audio(`${SOUND_BASE}start-button-sound.MP3`),
    spin:    new Audio(`${SOUND_BASE}spining-sound.MP3`), // 파일명 그대로(spining)
    stop:    new Audio(`${SOUND_BASE}stop-stop-stop-sound.MP3`),
    win:     new Audio(`${SOUND_BASE}win-sound.MP3`),
    lose:    new Audio(`${SOUND_BASE}lose-sound.MP3`),
    jackpot: new Audio(`${SOUND_BASE}jackpot-sound.MP3`),
  };

  let audioUnlocked = false;
  let soundOn = true;

  function audioInit() {
    try {
      Object.values(sounds).forEach(a => {
        a.preload = "auto";
        a.volume = 0.7;
      });
      sounds.spin.loop = true;
      sounds.spin.volume = 0.45;
    } catch (_) {}
  }

  async function unlockAudioOnce() {
    if (audioUnlocked) return true;
    try {
      const a = sounds.start;
      a.currentTime = 0;
      await a.play();
      a.pause();
      audioUnlocked = true;
      return true;
    } catch {
      audioUnlocked = false;
      return false;
    }
  }

  function applySoundOnOff(on) {
    soundOn = !!on;
    if (!soundOn) {
      try { sounds.spin.pause(); sounds.spin.currentTime = 0; } catch(_) {}
    }
    // 음소거는 볼륨으로 처리
    try {
      Object.entries(sounds).forEach(([k, a]) => {
        if (!a) return;
        if (!soundOn) a.volume = 0;
        else {
          // 기본 볼륨 복구
          if (k === "spin") a.volume = 0.45;
          else a.volume = 0.7;
        }
      });
    } catch (_) {}
  }

  function playSound(key) {
    if (!soundOn) return;
    const a = sounds[key];
    if (!a) return;
    try {
      a.currentTime = 0;
      a.play().catch(() => {});
    } catch (_) {}
  }

  function startSpinSound() {
    if (!soundOn) return;
    try {
      sounds.spin.currentTime = 0;
      sounds.spin.play().catch(() => {});
    } catch (_) {}
  }

  function stopSpinSound() {
    try {
      sounds.spin.pause();
      sounds.spin.currentTime = 0;
    } catch (_) {}
  }

  // ======================
  // Controls: SOUND 버튼 + BET +/- 버튼
  // ======================
  function addControls(identity, state) {
    // SOUND 버튼: 기존 row(오토/스핀 버튼 라인)에 삽입
    const row = ui.btnSpin?.parentElement; // .row
    if (row && !document.getElementById("btnSound")) {
      const btn = document.createElement("button");
      btn.id = "btnSound";
      btn.className = ui.btnAuto ? ui.btnAuto.className : "slotMiniBtn";
      btn.style.width = "140px";
      btn.textContent = soundOn ? "SOUND ON" : "SOUND OFF";
      btn.addEventListener("click", async () => {
        await unlockAudioOnce();
        const next = !soundOn;
        applySoundOnOff(next);
        saveSoundOn(identity.id, next);
        btn.textContent = next ? "SOUND ON" : "SOUND OFF";
        if (next) playSound("start");
      });

      // AUTO 버튼 옆에 끼워넣기
      // [AUTO] [SOUND] [SPIN]
      if (ui.btnAuto && ui.btnAuto.nextSibling) {
        row.insertBefore(btn, ui.btnAuto.nextSibling);
      } else {
        row.insertBefore(btn, ui.btnSpin);
      }
    }

    // BET 컨트롤: BET 카드 아래쪽에 삽입
    const betEl = ui.bet;
    const betCard = betEl?.closest?.(".stat");
    if (betCard && !document.getElementById("betMinus")) {
      const ctl = document.createElement("div");
      ctl.className = "slotCtlRow";

      const minus = document.createElement("button");
      minus.id = "betMinus";
      minus.className = "slotMiniBtn";
      minus.textContent = "-5";
      minus.addEventListener("click", () => {
        state.bet = clampBet(state.bet - BET_STEP);
        setText(ui.bet, fmtInt(state.bet));
        saveBet(identity.id, state.bet);
        refreshBetButtons(state);
      });

      const pill = document.createElement("div");
      pill.id = "betHint";
      pill.className = "slotPill";
      pill.textContent = `BET: ${state.bet} UT (±${BET_STEP})`;

      const plus = document.createElement("button");
      plus.id = "betPlus";
      plus.className = "slotMiniBtn";
      plus.textContent = "+5";
      plus.addEventListener("click", () => {
        state.bet = clampBet(state.bet + BET_STEP);
        setText(ui.bet, fmtInt(state.bet));
        saveBet(identity.id, state.bet);
        refreshBetButtons(state);
      });

      ctl.appendChild(minus);
      ctl.appendChild(pill);
      ctl.appendChild(plus);

      betCard.appendChild(ctl);
      refreshBetButtons(state);
    }
  }

  function refreshBetButtons(state) {
    const minus = document.getElementById("betMinus");
    const plus = document.getElementById("betPlus");
    const pill = document.getElementById("betHint");
    if (pill) pill.textContent = `BET: ${state.bet} UT (±${BET_STEP})`;
    if (minus) minus.disabled = state.bet <= BET_MIN;
    if (plus) plus.disabled = state.bet >= BET_MAX;
  }

  // ======================
  // Paytable UI (안내용)
  // ======================
  function renderPaytable() {
    if (!ui.pay) return;

    ui.pay.innerHTML = `
      <div class="ptTitle">PAY TABLE (느낌: 자주 작은 승리 + 가끔 큰 승리)</div>
      <div class="ptGrid">
        <div class="ptRow">
          <div class="ptLeft"><div class="ptBadge">2x</div><div>전체 15칸 중 <b>같은 심볼 2개</b></div></div>
          <div class="ptHint">작은 보상 / 재미 유지</div>
        </div>
        <div class="ptRow">
          <div class="ptLeft"><div class="ptBadge">3x</div><div>전체 15칸 중 <b>같은 심볼 3개</b></div></div>
          <div class="ptHint">체감 승리 시작</div>
        </div>
        <div class="ptRow">
          <div class="ptLeft"><div class="ptBadge">4x</div><div>전체 15칸 중 <b>같은 심볼 4개</b></div></div>
          <div class="ptHint">큰 승리(흥분 구간)</div>
        </div>
        <div class="ptRow">
          <div class="ptLeft"><div class="ptBadge">5x</div><div>전체 15칸 중 <b>같은 심볼 5개</b></div></div>
          <div class="ptHint">강한 보상(고조)</div>
        </div>
        <div class="ptRow">
          <div class="ptLeft"><div class="ptBadge">JP</div><div><b>PRO10</b>이 <b>5개</b>면 JACKPOT</div></div>
          <div class="ptHint">“진짜 희귀” (연 2회 체감 목표)</div>
        </div>
        <div class="ptRow">
          <div class="ptLeft"><div class="ptBadge">S</div><div>심볼: STAR1~3 / PRO1~10</div></div>
          <div class="ptHint">슬라이드/잭팟PNG 없음</div>
        </div>
      </div>
    `;
  }

  // ======================
  // Game State
  // ======================
  let identity = null;
  const state = {
    bet: BET_DEFAULT,
    autoOn: false,
    spinning: false,
  };

  function setWalletNow(n) {
    if (n === null || n === undefined) return;
    setText(ui.wallet, fmtInt(n));
  }

  function stopAuto() {
    state.autoOn = false;
    if (ui.btnAuto) ui.btnAuto.textContent = "AUTO OFF";
    if (state._autoTimer) clearInterval(state._autoTimer);
    state._autoTimer = null;
  }

  function startAuto() {
    if (state.autoOn) return;
    state.autoOn = true;
    if (ui.btnAuto) ui.btnAuto.textContent = "AUTO ON";
    state._autoTimer = setInterval(() => {
      if (!state.spinning) spin();
    }, 1200);
  }

  function toggleAuto() {
    if (state.autoOn) stopAuto();
    else startAuto();
  }

  async function loadStateFromWorker() {
    const u = identity?.id;
    if (!u) return null;

    setNote("SYNC…");
    const url = `${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}&name=${encodeURIComponent(identity.name||"")}&nick=${encodeURIComponent(identity.nickname||"")}`;
    const js = await fetchJSON(url);

    if (!js?.ok) {
      setResult("STATE ERROR", true);
      // UT는 로컬이라도 유지
      setWalletNow(identity.balance ?? 0);
      setNote(`state fail: ${js?.error || "unknown"} (메인 등록/동기화 후 다시)`, true);
      return null;
    }

    // UT 동기화
    const ut = pickUT(js);
    if (ut !== null) {
      setWalletNow(ut);
      identity.balance = ut;
      try {
        const raw = localStorage.getItem("uniqueCurrentUser");
        if (raw) {
          const uu = JSON.parse(raw);
          uu.balance = ut;
          localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
        }
        localStorage.setItem("myUtPoints", String(ut));
      } catch (_) {}
    }

    // worker가 bet 주면 그걸 반영(없으면 로컬 bet 유지)
    const wb = toNum(js.bet ?? js.BET);
    if (wb !== null) {
      state.bet = clampBet(wb);
      saveBet(identity.id, state.bet);
      setText(ui.bet, fmtInt(state.bet));
      refreshBetButtons(state);
    }

    // jackpot 표시
    const jp = toNum(js.jackpot ?? js.JACKPOT);
    if (jp !== null) setText(ui.jackpot, fmtInt(jp));

    // 그리드 렌더
    if (js.grid) renderGrid(js.grid);

    setResult("READY");
    setNote("");
    return js;
  }

  // ======================
  // Spin
  // ======================
  async function spin() {
    if (state.spinning) return;

    state.spinning = true;
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      await unlockAudioOnce();
      playSound("start");

      // 연출 시작
      startSpinVisual();
      startSpinSound();
      setNote("SPINNING…");

      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      // ✅ bet 같이 보냄 (worker가 무시해도 OK / 지원하면 바로 반영됨)
      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          u,
          name: identity.name || "",
          nickname: identity.nickname || "",
          bet: state.bet,
        })
      });

      stopSpinSound();

      if (!js?.ok) {
        forceStopVisual();
        setResult("SPIN ERROR", true);

        const err = String(js?.error || "unknown");
        if (err.includes("user_not_found")) {
          setNote("유저가 슬롯 시트에 없음 → 메인에서 등록/동기화 후 다시 오세요.", true);
        } else {
          setNote(`spin fail: ${err}`, true);
        }

        if (err.includes("insufficient")) stopAuto();
        return;
      }

      // worker 응답 반영(UT/잭팟/베팅/그리드)
      const ut = pickUT(js);
      if (ut !== null) {
        setWalletNow(ut);
        identity.balance = ut;
        try {
          const raw = localStorage.getItem("uniqueCurrentUser");
          if (raw) {
            const uu = JSON.parse(raw);
            uu.balance = ut;
            localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
          }
          localStorage.setItem("myUtPoints", String(ut));
        } catch (_) {}
      }

      const jp = toNum(js.jackpot ?? js.JACKPOT);
      if (jp !== null) setText(ui.jackpot, fmtInt(jp));

      const wb = toNum(js.bet ?? js.BET);
      if (wb !== null) {
        state.bet = clampBet(wb);
        saveBet(identity.id, state.bet);
        setText(ui.bet, fmtInt(state.bet));
        refreshBetButtons(state);
      }

      const finalGrid = js.grid || null;
      if (!finalGrid) {
        // grid가 없으면 그냥 스톱
        forceStopVisual();
      } else {
        // ✅ 컬럼별 멈춤 연출 + 컬럼마다 “딸깍” 사운드
        stopSpinVisualWithFinal(finalGrid, (colIdx) => {
          // 컬럼마다 stop 사운드를 짧게 쳐주면 슬롯 맛 남
          playSound("stop");
        });
      }

      // 결과 문구
      const betCharged = toNum(js.betCharged) ?? state.bet;
      const win = toNum(js.win) ?? 0;
      const delta = (win ?? 0) - (betCharged ?? 0);

      // 조금 기다렸다가(컬럼 스톱 끝나고) 결과를 터트리는 느낌
      setTimeout(() => {
        if (delta > 0) {
          setResult(`WIN +${fmtInt(delta)} UT`);
          ui.reels?.classList?.add("winFlash");
          setTimeout(() => ui.reels?.classList?.remove("winFlash"), 650);
          playSound("win");
        } else if (delta < 0) {
          setResult(`LOSE ${fmtInt(delta)} UT`);
          playSound("lose");
        } else {
          setResult("EVEN 0 UT");
        }

        // 잭팟 플래그(서버가 주면 사용)
        if (toNum(js.jackpotHit) === 1 || toNum(js.isJackpot) === 1) {
          ui.reelWrap?.classList?.add("jackpotPulse");
          setTimeout(() => ui.reelWrap?.classList?.remove("jackpotPulse"), 1800);
          playSound("jackpot");
        }

        setNote("");
      }, 650);

    } catch (e) {
      forceStopVisual();
      stopSpinSound();
      setResult("SPIN ERROR", true);
      setNote(String(e?.message || e), true);
      stopAuto();
    } finally {
      // 컬럼 스톱 연출 중에도 스핀 버튼 연타 방지 위해 약간 늦게 해제
      setTimeout(() => {
        state.spinning = false;
        if (ui.btnSpin) ui.btnSpin.disabled = false;
      }, 900);
    }
  }

  // ======================
  // Boot
  // ======================
  async function boot() {
    injectStyleOnce();
    audioInit();
    renderPaytable();

    identity = getLocalUser();
    if (!identity) return redirectToGate();

    // nickname 보조
    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    // 로컬 UT 먼저 표시(즉시)
    setText(ui.player, identity.name || identity.id);
    setWalletNow(identity.balance ?? 0);

    // bet 로드(유저별 저장)
    state.bet = loadBet(identity.id);
    setText(ui.bet, fmtInt(state.bet));

    // sound 로드(유저별 저장)
    applySoundOnOff(loadSoundOn(identity.id));

    // 버튼 바인딩
    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    // UI 컨트롤 삽입
    addControls(identity, state);

    // 빈 화면 방지: 초기 랜덤
    renderGrid([
      [randSym(),randSym(),randSym(),randSym(),randSym()],
      [randSym(),randSym(),randSym(),randSym(),randSym()],
      [randSym(),randSym(),randSym(),randSym(),randSym()],
    ]);

    setResult("READY");
    setNote("");

    // worker 동기화
    await loadStateFromWorker();

    console.log("SLOT UI LOADED ✅", VERSION);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
