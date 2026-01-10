/* games/slot.page.js
 * THE UNIQUE SLOT (cyber + vertical rolling + sounds)
 *
 * ✅ SLIDE( slide1~8 ) 완전 제거
 * ✅ 위→아래 롤링 연출(진짜 슬롯 느낌: 컬럼별 스태거 멈춤)
 * ✅ 사운드: start / spinning(loop) / stop-per-reel / win / lose / jackpot
 * ✅ 이미지 경로: /games/img/slot/*.png (pro1~10, star1~3)
 * ✅ jackpot.png 없음 → img 로드 안 함(404 스팸 제거), SVG 네온으로만 표시
 * ✅ user_not_found_in_sheet 등 오류는 한글로 안내
 */

(() => {
  "use strict";

  // =========================
  // 0) CONFIG
  // =========================
  const DEFAULT_WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 버전 마커 (콘솔에서 적용 확인)
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_roll_v3";

  // URL 쿼리로 워커 바꾸기 가능: /games/slot.html?api=https://...
  const WORKER_BASE = (() => {
    try {
      const u = new URL(location.href);
      const api = u.searchParams.get("api");
      if (api && /^https?:\/\//i.test(api)) return api.replace(/\/+$/, "");
    } catch {}
    return DEFAULT_WORKER_BASE;
  })();

  // ✅ 심볼 풀: SLIDE 제거
  const SYMBOL_POOL = (() => {
    const arr = [];
    for (let i = 1; i <= 3; i++) arr.push(`star${i}`);
    for (let i = 1; i <= 10; i++) arr.push(`pro${i}`);
    arr.push("jackpot");
    return arr;
  })();

  // ✅ 사운드 파일 경로 (/games 기준)
  const SOUND = {
    start:   "sounds/start-button-sound.MP3",
    spin:    "sounds/spining-sound.MP3",
    stop:    "sounds/stop-stop-stop-sound.MP3",
    win:     "sounds/win-sound.MP3",
    lose:    "sounds/lose-sound.MP3",
    jackpot: "sounds/jackpot-sound.MP3",
  };

  // 롤링 속도/시간(감성 세팅)
  const ROLL_TICK_MS = 70;        // 굴러가는 프레임 간격 (작을수록 빠름)
  const ROLL_MIN_MS  = 900;       // 최소 스핀 연출 시간
  const ROLL_MAX_MS  = 1400;      // 최대 스핀 연출 시간
  const STOP_STAGGER = 160;       // 컬럼 멈추는 간격

  // =========================
  // 1) UTIL
  // =========================
  const $id = (id) => document.getElementById(id);

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return String(Math.floor(x));
  }

  function randPick(arr) {
    return arr[(Math.random() * arr.length) | 0];
  }

  function setText(el, v) {
    if (!el) return;
    el.textContent = String(v ?? "");
  }

  function humanizeError(err) {
    const e = String(err || "");
    if (!e) return "알 수 없는 오류";
    if (e.includes("user_not_found_in_sheet")) return "유저가 슬롯 시트에 없음 → 게이트에서 등록 후 다시 오세요.";
    if (e.includes("insufficient")) return "UT 잔액이 부족합니다.";
    if (e.includes("timeout")) return "요청 시간이 초과됐습니다(네트워크/워커 확인).";
    if (e.includes("bad_json")) return "서버 응답 형식이 깨졌습니다(JSON 오류).";
    if (e.includes("http_")) return `서버 HTTP 오류(${e.replace("http_", "")})`;
    return e;
  }

  async function fetchJSON(url, opt = {}, timeoutMs = 20000) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort("timeout"), timeoutMs);
    try {
      const res = await fetch(url, { ...opt, signal: ctrl.signal, cache: "no-store" });
      const text = await res.text();
      let js = null;
      try { js = JSON.parse(text); }
      catch { js = { ok: false, error: "bad_json", raw: text }; }

      if (!res.ok && js && typeof js === "object" && !js.error) {
        js.error = `http_${res.status}`;
      }
      return js;
    } finally {
      clearTimeout(t);
    }
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
    location.href = "../the-unique-gate.html";
  }

  // =========================
  // 2) DOM BIND
  // =========================
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

  // =========================
  // 3) PAYTABLE (SLIDE 제거)
  // =========================
  function buildPaytable() {
    if (!ui.pay) return;
    ui.pay.innerHTML = `
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">★</div><div>STAR</div></div>
        <div class="ptMul">x ?</div>
      </div>
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">P</div><div>PRO</div></div>
        <div class="ptMul">x ?</div>
      </div>
      <div class="ptItem">
        <div class="ptLeft"><div class="badge">JP</div><div>JACKPOT</div></div>
        <div class="ptMul">SPECIAL</div>
      </div>
    `;
  }

  // =========================
  // 4) SYMBOL RENDER (PNG + SVG NEON)
  // =========================
  function svgFor(sym) {
    const s = String(sym || "").toLowerCase();
    let g1 = "#21f6ff", g2 = "#ff2bd6";
    if (s.startsWith("star")) { g1 = "#21f6ff"; g2 = "#b7ff2a"; }
    if (s.startsWith("pro"))  { g1 = "#ff2bd6"; g2 = "#a98bff"; }
    if (s.includes("jack"))   { g1 = "#ffcc33"; g2 = "#ff2bd6"; }

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

  // ✅ png 파일명 결정 (slide 제거 + jackpot png 금지)
  function pickPngFile(sym) {
    const raw = String(sym || "");
    const s = raw.trim().toLowerCase();

    // ✅ slide 들어오면 강제 치환(서버가 혹시 보내도 화면 안 깨짐)
    if (s === "slide" || s.startsWith("slide")) return "pro1.png";

    const mPro  = s.match(/^pro(\d+)$/);
    const mStar = s.match(/^star(\d+)$/);

    if (mPro) {
      let n = Math.max(1, Math.min(10, Number(mPro[1] || 1)));
      return `pro${n}.png`;
    }
    if (mStar) {
      let n = Math.max(1, Math.min(3, Number(mStar[1] || 1)));
      return `star${n}.png`;
    }

    if (s === "pro") return "pro1.png";
    if (s === "star") return "star1.png";

    // ✅ jackpot은 png 없음 → null (이미지 로드 안 함)
    if (s.includes("jack")) return null;

    // 그 외는 파일이 있으면 로드, 없으면 onerror로 제거됨
    return `${s}.png`;
  }

  function renderSymbolInto(box, sym) {
    if (!box) return;
    box.innerHTML = sym ? svgFor(sym) : "";

    const png = pickPngFile(sym);
    if (!png) return; // jackpot 등

    const img = document.createElement("img");
    // ✅ slot.html 기준: /games/img/slot/...
    img.src = `img/slot/${png}`;
    img.alt = sym;
    img.onerror = () => img.remove();
    box.appendChild(img);
  }

  // =========================
  // 5) REELS (3x5 GRID + VERTICAL ROLLING)
  // =========================
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

  function cellAt(r, c, cells) {
    return cells[r * COLS + c];
  }

  function renderGrid(grid) {
    const cells = ensureCells();
    if (!cells.length) return;

    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const sym = grid?.[r]?.[c] ?? "";
        const cell = cellAt(r, c, cells);
        const box = cell?.querySelector(".sym");
        if (cell) cell.classList.remove("spinBlur");
        renderSymbolInto(box, sym);
      }
    }
  }

  // ✅ 롤링: 컬럼별로 "위→아래로" 계속 내려가는 느낌
  let rollTimers = new Array(COLS).fill(null);
  let rolling = false;

  function startRollingFX() {
    if (rolling) return;
    rolling = true;

    const cells = ensureCells();

    // 현재 화면을 기준으로 시작 심볼을 잡고(없으면 랜덤)
    const colSyms = Array.from({ length: COLS }, (_, c) => {
      const a = [];
      for (let r = 0; r < ROWS; r++) {
        const cell = cellAt(r, c, cells);
        const imgAlt = cell?.querySelector("img")?.alt;
        a.push(imgAlt || randPick(SYMBOL_POOL));
      }
      return a; // [top, mid, bot]
    });

    // 컬럼별 타이머: top에 랜덤 넣고 아래로 밀어내기
    for (let c = 0; c < COLS; c++) {
      if (rollTimers[c]) clearInterval(rollTimers[c]);

      rollTimers[c] = setInterval(() => {
        // [t,m,b] -> [new, t, m]
        const cur = colSyms[c];
        const nextTop = randPick(SYMBOL_POOL);
        colSyms[c] = [nextTop, cur[0], cur[1]];

        // 렌더 + 블러
        for (let r = 0; r < ROWS; r++) {
          const cell = cellAt(r, c, cells);
          const box = cell?.querySelector(".sym");
          if (cell) cell.classList.add("spinBlur");
          renderSymbolInto(box, colSyms[c][r]);
        }
      }, ROLL_TICK_MS);
    }
  }

  async function stopRollingToFinal(finalGrid) {
    // 컬럼별로 스태거 멈춤 (왼→오)
    const cells = ensureCells();

    for (let c = 0; c < COLS; c++) {
      await new Promise((r) => setTimeout(r, STOP_STAGGER));

      if (rollTimers[c]) {
        clearInterval(rollTimers[c]);
        rollTimers[c] = null;
      }

      // stop 사운드 (릴 멈출 때 “딱”)
      Sound.play("stop");

      // 최종 결과로 고정
      for (let r = 0; r < ROWS; r++) {
        const sym = finalGrid?.[r]?.[c] ?? "";
        const cell = cellAt(r, c, cells);
        const box = cell?.querySelector(".sym");
        if (cell) cell.classList.remove("spinBlur");
        renderSymbolInto(box, sym);
      }
    }

    rolling = false;
  }

  // spinBlur 효과를 JS로 주입 (slot.html 건드리기 싫어서)
  function injectFXCSS() {
    const css = `
      .cell.spinBlur .sym { filter: blur(1.2px) saturate(1.25); transform: translateY(1px); }
      .cell.spinBlur { box-shadow: 0 0 28px rgba(33,246,255,.14), 0 0 30px rgba(255,43,214,.10); }
    `;
    const tag = document.createElement("style");
    tag.textContent = css;
    document.head.appendChild(tag);
  }

  // =========================
  // 6) SOUND ENGINE
  // =========================
  const Sound = (() => {
    const aud = {};
    let unlocked = false;

    function get(name) {
      if (aud[name]) return aud[name];
      const src = SOUND[name];
      if (!src) return null;

      const a = new Audio(src);
      a.preload = "auto";
      a.crossOrigin = "anonymous";
      aud[name] = a;
      return a;
    }

    async function unlock() {
      if (unlocked) return;
      // 사용자 제스처에서만 성공 가능
      const a = get("start");
      if (!a) { unlocked = true; return; }
      try {
        a.volume = 0.0001;
        await a.play();
        a.pause();
        a.currentTime = 0;
        a.volume = 1.0;
        unlocked = true;
      } catch {
        // 실패해도 계속 진행(브라우저 정책)
        unlocked = false;
      }
    }

    function play(name, opt = {}) {
      const a = get(name);
      if (!a) return;

      try {
        a.pause();
        a.currentTime = 0;
      } catch {}

      if (typeof opt.loop === "boolean") a.loop = opt.loop;
      if (typeof opt.volume === "number") a.volume = opt.volume;

      a.play().catch(() => {});
    }

    function stop(name) {
      const a = aud[name];
      if (!a) return;
      try {
        a.loop = false;
        a.pause();
        a.currentTime = 0;
      } catch {}
    }

    return { get, play, stop, unlock };
  })();

  // =========================
  // 7) GAME FLOW
  // =========================
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
    }, 1400);
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
      setResult("STATE ERROR", true);
      setNote(humanizeError(js?.error || "unknown"), true);
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim()
      || identity.name
      || identity.nickname
      || identity.id;

    setText(ui.player, displayName);
    setText(ui.wallet, fmt(js.ut));
    setText(ui.jackpot, fmt(js.jackpot));
    setText(ui.bet, fmt(js.bet ?? 10));

    setResult("READY");
    setNote("");

    // grid 있으면 초기 표시
    if (js.grid) renderGrid(js.grid);
    else renderGrid(null);

    return js;
  }

  function updateLocalBalance(ut) {
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const uu = JSON.parse(raw);
        uu.balance = Number(ut || 0);
        localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
        localStorage.setItem("myUtPoints", String(Number(ut || 0)));
      }
    } catch {}
  }

  async function spin() {
    if (spinning) return;
    spinning = true;

    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      await Sound.unlock(); // 클릭에서만 가능
      Sound.play("start", { volume: 0.9 });

      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      // 1) 롤링 시작 + 스핀 사운드(루프)
      setResult("SPINNING…");
      setNote("");
      startRollingFX();
      Sound.play("spin", { loop: true, volume: 0.55 });

      // 최소 연출 시간 확보(너가 말한 “위에서 아래로 빠르게 돌기만” 먼저 보여주기)
      const rollWait = Math.floor(ROLL_MIN_MS + Math.random() * (ROLL_MAX_MS - ROLL_MIN_MS));

      // 2) 서버 요청(동시에 날리고, 최소 연출시간 끝나면 결과 적용)
      const p = fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u })
      }, 20000);

      const [js] = await Promise.all([
        p,
        new Promise((r) => setTimeout(r, rollWait))
      ]);

      if (!js?.ok) {
        // 스핀 사운드 stop
        Sound.stop("spin");
        setResult("SPIN ERROR", true);
        setNote(humanizeError(js?.error || "unknown"), true);

        // 롤링 멈추기(그냥 정지)
        for (let c = 0; c < COLS; c++) {
          if (rollTimers[c]) clearInterval(rollTimers[c]);
          rollTimers[c] = null;
        }
        rolling = false;

        if (String(js?.error || "").includes("insufficient")) stopAuto();
        return;
      }

      // 3) UI 수치 먼저 반영
      setText(ui.wallet, fmt(js.ut));
      setText(ui.jackpot, fmt(js.jackpot));
      setText(ui.bet, fmt(js.bet ?? 10));
      updateLocalBalance(js.ut);

      // 4) 롤링 → 최종 그리드로 컬럼별 멈춤(스태거)
      await stopRollingToFinal(js.grid);

      // 5) 결과 텍스트 + 사운드
      Sound.stop("spin");

      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);
      const delta = win - betCharged;

      const isJackpot = Array.isArray(js.grid)
        && js.grid.flat().some(v => String(v || "").toLowerCase().includes("jack"));

      if (isJackpot) {
        setResult("JACKPOT!!");
        Sound.play("jackpot", { volume: 0.9 });
        if (ui.reelWrap) ui.reelWrap.classList.add("jackpotPulse");
        setTimeout(() => ui.reelWrap && ui.reelWrap.classList.remove("jackpotPulse"), 900);
      } else if (delta > 0) {
        setResult(`WIN +${fmt(delta)} UT`);
        Sound.play("win", { volume: 0.8 });
      } else if (delta < 0) {
        setResult(`LOSE ${fmt(delta)} UT`);
        Sound.play("lose", { volume: 0.7 });
      } else {
        setResult("EVEN 0 UT");
        Sound.play("lose", { volume: 0.45 });
      }

    } catch (e) {
      Sound.stop("spin");
      setResult("SPIN ERROR", true);
      setNote(humanizeError(e?.message || e), true);
      stopAuto();
    } finally {
      spinning = false;
      if (ui.btnSpin) ui.btnSpin.disabled = false;
    }
  }

  // =========================
  // 8) BOOT
  // =========================
  async function boot() {
    injectFXCSS();
    buildPaytable();
    renderGrid(null);

    identity = getLocalUser();
    if (!identity) return redirectToGate();

    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    await loadState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__, "WORKER=", WORKER_BASE);
})();
