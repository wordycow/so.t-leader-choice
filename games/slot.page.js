/* games/slot.page.js
 * THE UNIQUE SLOT (final-ish)
 * - localStorage(uniqueCurrentUser / myUtPoints)로 즉시 UT 표시
 * - WORKER_BASE /slot/state, /slot/spin 동기화
 * - 세로 슬롯 롤링(컬럼별 빠른 랜덤 스왑) 연출
 * - 사운드 로딩(경로/파일명 불일치 대비 fallback) + 실패해도 게임 진행
 * - jackpot.png 없으면 자동으로 SVG만 표시
 */

(() => {
  "use strict";

  // ✅ 워커 주소 (여기만 바꾸면 됨)
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 캐시 확인용 버전
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_final_vertical_fx_v1";

  // ✅ games/slot.html 기준 상대 경로
  const IMG_BASE = "./img/slot/";
  const SOUND_BASE = "./sounds/";

  // ---------- utils ----------
  const $id = (id) => document.getElementById(id);

  function fmt(n) {
    const x = Number(n);
    if (!Number.isFinite(x)) return "0";
    return String(Math.floor(x));
  }

  function setText(el, v) {
    if (!el) return;
    el.textContent = String(v ?? "");
  }

  // neon 글자가 "□"처럼 보이거나 안 보일 때 강제 가시성 확보
  function forceVisibleNumber(el) {
    if (!el) return;
    el.style.webkitTextFillColor = "rgba(215,228,255,.95)";
    el.style.color = "rgba(215,228,255,.95)";
    el.style.background = "none";
    el.style.textShadow = "0 0 18px rgba(33,246,255,.18)";
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

  function getLocalUtFallback() {
    // main에서 쓰는 값들 최대한 주워오기
    const a = localStorage.getItem("myUtPoints");
    if (a != null && a !== "") return Number(a) || 0;

    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const u = JSON.parse(raw);
        const b = Number(u?.balance);
        if (Number.isFinite(b)) return b;
      }
    } catch {}
    return 0;
  }

  function setLocalUt(ut) {
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const uu = JSON.parse(raw);
        uu.balance = Number(ut || 0);
        localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
      }
      localStorage.setItem("myUtPoints", String(Number(ut || 0)));
    } catch {}
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
      if (!res.ok && js && typeof js === "object" && !js.error) {
        js.error = `http_${res.status}`;
      }
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  // ---------- DOM ----------
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

  // ---------- symbols ----------
  // slide1~8은 빼자: 목록에서 아예 제외
  const SYMBOL_POOL = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10",
    "jackpot"
  ];

  // 서버에서 오는 심볼값 normalize
  function normSym(sym) {
    const s = String(sym || "").trim();
    if (!s) return "";
    const u = s.toUpperCase();

    if (u === "SPECIAL" || u === "JACKPOT" || u === "JP" || u === "J") return "jackpot";
    if (u.startsWith("STAR")) {
      const n = u.replace("STAR", "").replace(/[^0-9]/g, "");
      return n ? `star${n}` : "star1";
    }
    if (u.startsWith("PRO")) {
      const n = u.replace("PRO", "").replace(/[^0-9]/g, "");
      return n ? `pro${n}` : "pro1";
    }

    // 이미 star1/pro2 같은 케이스면 소문자로
    const low = s.toLowerCase();
    if (SYMBOL_POOL.includes(low)) return low;

    // 모르면 그냥 빈칸
    return "";
  }

  // ---------- reels rendering ----------
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

  // SVG 네온 기본 렌더 (PNG 없을 때도 멋있게)
  function svgFor(sym) {
    const s = String(sym || "").toUpperCase();
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

  function renderCell(box, sym) {
    const n = normSym(sym);
    box.innerHTML = n ? svgFor(n) : "";

    if (!n) return;

    // PNG overlay (있으면 얹기, 없으면 자동 삭제)
    const img = document.createElement("img");
    img.src = `${IMG_BASE}${n}.png`; // ✅ games/img/slot/
    img.alt = n;
    img.onerror = () => img.remove(); // jackpot.png 없으면 그냥 SVG만 남음
    box.appendChild(img);
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
      const box = cell?.querySelector(".sym");
      if (!box) return;
      renderCell(box, sym);
    });
  }

  // ---------- vertical spin FX (컬럼별 빠른 롤링) ----------
  function getCellIndex(r, c) {
    return r * COLS + c;
  }

  function randSym() {
    return SYMBOL_POOL[Math.floor(Math.random() * SYMBOL_POOL.length)];
  }

  function startSpinFX(durationMs = 850) {
    const cells = ensureCells();
    if (!cells.length) return { stop: () => {} };

    // 컬럼별로 약간씩 스톱 시간 다르게(슬롯 느낌)
    const colTimers = [];
    const colIntervals = [];

    // 흔들림
    ui.reelWrap?.classList?.add("shake");

    for (let c = 0; c < COLS; c++) {
      const interval = setInterval(() => {
        for (let r = 0; r < ROWS; r++) {
          const idx = getCellIndex(r, c);
          const box = cells[idx]?.querySelector(".sym");
          if (!box) continue;
          renderCell(box, randSym());
        }
      }, 60);
      colIntervals.push(interval);

      const stopAt = durationMs + c * 110; // 뒤로 갈수록 조금 더 길게
      const timer = setTimeout(() => {
        clearInterval(interval);
      }, stopAt);
      colTimers.push(timer);
    }

    const stop = () => {
      colIntervals.forEach((x) => clearInterval(x));
      colTimers.forEach((t) => clearTimeout(t));
      ui.reelWrap?.classList?.remove("shake");
    };

    return { stop };
  }

  // ---------- sounds ----------
  // 파일명/대소문자 조금만 달라도 404 나서, “후보들”로 자동 탐색
  const SOUND_CANDIDATES = {
    click:   ["start-button-sound.MP3", "start_button_sound.MP3", "start.mp3"],
    spin:    ["spining-sound.MP3", "spinning-sound.MP3", "spin.mp3"],
    stop:    ["stop-stop-stop-sound.MP3", "stop.mp3"],
    win:     ["win_sound.MP3", "win-sound.MP3", "win.mp3"],
    lose:    ["lose_sound.MP3", "lose-sound.MP3", "lose.mp3"],
    jackpot: ["jackpot-sound.MP3", "jackpot.mp3"],
  };

  const S = { click:null, spin:null, stop:null, win:null, lose:null, jackpot:null };

  async function probeAudio(url) {
    // HEAD가 막힐 수 있어서 실제로 Audio 로드 시도
    return new Promise((resolve) => {
      const a = new Audio();
      a.preload = "auto";
      a.src = url;
      a.addEventListener("canplaythrough", () => resolve(a), { once:true });
      a.addEventListener("error", () => resolve(null), { once:true });
      // iOS 대응: load 호출
      try { a.load(); } catch {}
    });
  }

  async function loadSound(key) {
    const list = SOUND_CANDIDATES[key] || [];
    for (const name of list) {
      const url = `${SOUND_BASE}${name}`; // ✅ games/sounds/
      const a = await probeAudio(url);
      if (a) return a;
    }
    return null;
  }

  async function initSounds() {
    // 실패해도 게임 진행
    try {
      const keys = Object.keys(SOUND_CANDIDATES);
      for (const k of keys) {
        S[k] = await loadSound(k);
      }
    } catch {}
  }

  function playSound(aud, { loop=false, volume=0.9, restart=true } = {}) {
    if (!aud) return;
    try {
      aud.loop = !!loop;
      aud.volume = volume;
      if (restart) aud.currentTime = 0;
      // 사용자 제스처 없이 재생 차단될 수 있음(정상)
      aud.play().catch(() => {});
    } catch {}
  }

  function stopSound(aud) {
    if (!aud) return;
    try {
      aud.pause();
      aud.currentTime = 0;
      aud.loop = false;
    } catch {}
  }

  // ---------- state / actions ----------
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

  function showLocalUtNow() {
    const ut = getLocalUtFallback();
    setText(ui.wallet, fmt(ut));
    forceVisibleNumber(ui.wallet);
  }

  async function loadState() {
    const u = identity?.id;
    if (!u) return null;

    setNote("SYNC…");
    const js = await fetchJSON(`${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}`, {}, 20000);

    if (!js?.ok) {
      // 서버 state 실패해도 로컬 UT는 유지해서 “안 보이는 병신짓” 방지
      showLocalUtNow();
      setResult("STATE ERROR", true);
      setNote(`state fail: ${js?.error || "unknown"}`, true);

      // 유저가 시트에 없으면 스핀을 막는게 맞음(계속 에러 찍힘)
      if (String(js?.error || "").includes("user_not_found")) {
        if (ui.btnSpin) ui.btnSpin.disabled = true;
      }
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim() || identity.name || identity.id;
    setText(ui.player, displayName);

    // ✅ UT 표시
    setText(ui.wallet, fmt(js.ut));
    forceVisibleNumber(ui.wallet);

    setText(ui.jackpot, fmt(js.jackpot));
    setText(ui.bet, fmt(js.bet ?? 10));

    // 로컬도 동기화
    setLocalUt(js.ut);

    setResult("READY");
    setNote("");

    if (js.grid) renderGrid(js.grid);

    if (ui.btnSpin) ui.btnSpin.disabled = false;
    return js;
  }

  async function spin() {
    if (spinning) return;
    spinning = true;
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    // 클릭 사운드
    playSound(S.click, { volume: 0.8 });

    // 스핀 연출 시작
    const fx = startSpinFX(780);
    playSound(S.spin, { loop:true, volume: 0.55, restart:true });

    try {
      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      setNote("SPINNING…");
      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u })
      }, 20000);

      // 스핀 사운드 정지 + 스톱 사운드
      stopSound(S.spin);
      playSound(S.stop, { volume: 0.7 });

      if (!js?.ok) {
        fx.stop();
        setResult("SPIN ERROR", true);
        setNote(`spin fail: ${js?.error || "unknown"}`, true);

        // 유저가 슬롯 시트에 없으면: 게이트에서 등록 유도 + 스핀 잠그기
        if (String(js?.error || "").includes("user_not_found_in_sheet")) {
          setNote("유저가 슬롯 시트에 없음 → 메인/게이트에서 등록 후 다시 오세요.", true);
          if (ui.btnSpin) ui.btnSpin.disabled = true;
        }

        if (String(js?.error || "").includes("insufficient")) stopAuto();
        return;
      }

      // 연출 멈추고 최종 그리드 렌더
      fx.stop();
      renderGrid(js.grid);

      // 숫자 업데이트
      setText(ui.wallet, fmt(js.ut));
      forceVisibleNumber(ui.wallet);
      setText(ui.jackpot, fmt(js.jackpot));
      setText(ui.bet, fmt(js.bet ?? 10));

      setLocalUt(js.ut);

      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);
      const delta = win - betCharged;

      if (delta > 0) {
        setResult(`WIN +${fmt(delta)} UT`);
        // 잭팟이면 jackpot 사운드 우선
        if (String(js?.winType || "").toLowerCase().includes("jack") || normSym("jackpot") === "jackpot" && win >= 1000) {
          playSound(S.jackpot, { volume: 0.95 });
        } else {
          playSound(S.win, { volume: 0.9 });
        }
      } else if (delta < 0) {
        setResult(`LOSE ${fmt(delta)} UT`);
        playSound(S.lose, { volume: 0.75 });
      } else {
        setResult(`EVEN 0 UT`);
      }

      setNote("");

    } catch (e) {
      fx.stop();
      stopSound(S.spin);
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

    // player 먼저 표시
    setText(ui.player, identity.name || identity.nickname || identity.id);

    // ✅ 로컬 UT 즉시 표시 (main에서 보이는데 slot에서 안 보이는 문제 해결)
    showLocalUtNow();

    // 잭팟/베트 기본
    if (ui.jackpot) setText(ui.jackpot, "0");
    if (ui.bet) setText(ui.bet, "10");

    // 버튼
    if (ui.btnSpin) ui.btnSpin.addEventListener("click", () => spin());
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", () => toggleAuto());

    // 빈 그리드라도 생성
    renderGrid(null);

    // 사운드 로딩 (백그라운드처럼 돌지만 await로 안전)
    await initSounds();

    // 서버 상태 로드
    await loadState();

    console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__ || "no_version");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
