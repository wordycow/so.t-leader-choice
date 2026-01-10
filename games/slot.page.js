/* games/slot.page.js
 * THE UNIQUE SLOT (cyberpunk master)
 * - localStorage(uniqueCurrentUser) 자동 로그인
 * - WORKER_BASE /slot/state, /slot/spin 호출
 * - 네온 SVG 심볼 + PNG 오버레이(있으면) + 사운드 + 스핀 애니메이션 + 잭팟 FX
 */
(() => {
  "use strict";

  // ✅ 워커 주소(필요하면 여기만)
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 적용 확인용 버전 마커
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_cyber_master_v1";

  // ✅ assets 경로 (중요!!)
  // 현재 구조: /games/slot.html, /games/img/slot, /games/sounds
  const IMG_BASE = "./img/slot/";
  const SND_BASE = "./sounds/";

  // ---------- DOM ----------
  const $id = (id) => document.getElementById(id);

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

  // ---------- utils ----------
  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return String(Math.floor(x));
  }
  function setText(el, v) { if (el) el.textContent = String(v ?? ""); }
  function setNote(msg, isErr=false) {
    if (!ui.note) return;
    ui.note.textContent = msg || "";
    ui.note.style.opacity = msg ? "1" : "0.8";
    ui.note.style.color = isErr ? "rgba(255,120,160,.95)" : "rgba(215,228,255,.82)";
  }
  function setResult(msg, isErr=false) {
    if (!ui.result) return;
    ui.result.textContent = msg || "";
    ui.result.style.color = isErr ? "rgba(255,120,160,.95)" : "";
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
    } catch { return null; }
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
      let js;
      try { js = JSON.parse(text); }
      catch { js = { ok:false, error:"bad_json", raw:text }; }

      if (!res.ok && js && typeof js === "object" && !js.error) js.error = `http_${res.status}`;
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  // ---------- audio ----------
  // 브라우저 정책상 “사용자 클릭 이후”에만 소리 재생 가능 → 첫 클릭에서만 언락
  const audio = {
    unlocked: false,
    startBtn: null,
    spinLoop: null,
    win: null,
    lose: null,
    jackpot: null,
    stop: null,
  };

  function mkAudio(file, { loop=false, volume=0.6 } = {}) {
    const a = new Audio(SND_BASE + file);
    a.loop = loop;
    a.volume = volume;
    a.preload = "auto";
    return a;
  }

  function unlockAudioOnce() {
    if (audio.unlocked) return;
    audio.unlocked = true;

    // 네 폴더명 그대로 사용
    audio.startBtn = mkAudio("start-button-sound.MP3", { volume: 0.75 });
    audio.spinLoop = mkAudio("spining-sound.MP3", { loop: true, volume: 0.35 });
    audio.win      = mkAudio("win-sound.MP3", { volume: 0.70 });
    audio.lose     = mkAudio("lose-sound.MP3", { volume: 0.70 });
    audio.jackpot  = mkAudio("jackpot-sound.MP3", { volume: 0.90 });
    audio.stop     = mkAudio("stop-stop-stop-sound.MP3", { volume: 0.75 });

    // 언락용 더미 재생(즉시 정지)
    try {
      audio.startBtn.play().then(() => {
        audio.startBtn.pause();
        audio.startBtn.currentTime = 0;
      }).catch(()=>{});
    } catch {}
  }

  function sfxPlay(aud) {
    if (!audio.unlocked || !aud) return;
    try {
      aud.currentTime = 0;
      aud.play().catch(()=>{});
    } catch {}
  }

  function spinLoopOn() {
    if (!audio.unlocked || !audio.spinLoop) return;
    try { audio.spinLoop.currentTime = 0; audio.spinLoop.play().catch(()=>{}); } catch {}
  }
  function spinLoopOff() {
    if (!audio.unlocked || !audio.spinLoop) return;
    try { audio.spinLoop.pause(); audio.spinLoop.currentTime = 0; } catch {}
  }

  // ---------- reels render ----------
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

  // “광기” 네온 SVG 기본 심볼
  function svgFor(sym) {
    const s = String(sym || "").toUpperCase();
    let g1 = "#21f6ff", g2 = "#ff2bd6";
    if (s.includes("STAR")) { g1 = "#21f6ff"; g2 = "#b7ff2a"; }
    if (s.includes("PRO"))  { g1 = "#ff2bd6"; g2 = "#a98bff"; }
    if (s.includes("SLIDE")){ g1 = "#21f6ff"; g2 = "#ffcc33"; }
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
        <circle cx="100" cy="100" r="72" fill="rgba(0,0,0,.12)" stroke="url(#g)" stroke-width="10" filter="url(#glow)"/>
        <path d="M100 46 L120 90 L168 92 L132 120 L146 168 L100 140 L54 168 L68 120 L32 92 L80 90 Z"
              fill="url(#g)" filter="url(#glow)" opacity="0.95"/>
      </svg>
    `;
  }

  function pngPath(sym) {
    // 워커가 "pro1" 같은 소문자 줄 가능성 높음 → 그대로 시도
    // 네 폴더는 pro1.png / star1.png / slide1.png (소문자)라서 이게 정답
    return IMG_BASE + String(sym || "") + ".png";
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

      box.innerHTML = sym ? svgFor(sym) : "";

      if (sym) {
        const img = document.createElement("img");
        img.src = pngPath(sym);
        img.alt = sym;
        img.onerror = () => img.remove(); // PNG 없으면 SVG만 남김(그게 “광기”)
        box.appendChild(img);
      }
    });
  }

  // ---------- spin animation (fake reel blur) ----------
  // 실제 결과 오기 전까지 “랜덤 심볼”로 돌려서 체감이 살아남
  const SYMBOL_POOL = [
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10",
    "star1","star2","star3",
    "slide1","slide2","slide3","slide4","slide5","slide6","slide7","slide8"
  ];

  function randSym() {
    return SYMBOL_POOL[(Math.random() * SYMBOL_POOL.length) | 0];
  }

  function makeRandomGrid() {
    const g = [];
    for (let r=0;r<ROWS;r++){
      const row = [];
      for (let c=0;c<COLS;c++) row.push(randSym());
      g.push(row);
    }
    return g;
  }

  let animTimer = null;
  function animStart() {
    if (animTimer) clearInterval(animTimer);
    if (ui.reelWrap) ui.reelWrap.classList.add("shake");
    const cells = ensureCells();
    cells.forEach(c => c.classList.add("shake"));

    animTimer = setInterval(() => {
      renderGrid(makeRandomGrid());
    }, 70);
  }
  function animStop() {
    if (animTimer) clearInterval(animTimer);
    animTimer = null;
    const cells = ensureCells();
    cells.forEach(c => c.classList.remove("shake"));
    if (ui.reelWrap) ui.reelWrap.classList.remove("shake");
  }

  // ---------- paytable (간단 버전) ----------
  function renderPaytable() {
    if (!ui.pay) return;
    ui.pay.innerHTML = `
      <div class="ptItem"><div class="ptLeft"><div class="badge">★</div><div>STAR</div></div><div class="ptMul">x ?</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">P</div><div>PRO</div></div><div class="ptMul">x ?</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">S</div><div>SLIDE</div></div><div class="ptMul">x ?</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">JP</div><div>JACKPOT</div></div><div class="ptMul">SPECIAL</div></div>
    `;
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
    if (audio.unlocked) sfxPlay(audio.stop);
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
    unlockAudioOnce();
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
      setNote(`state fail: ${js?.error || "unknown"}`, true);
      return null;
    }

    const displayName =
      String(js?.userName || js?.name || "").trim() ||
      identity.name ||
      identity.nickname ||
      identity.id;

    setText(ui.player, displayName);
    setText(ui.wallet, fmt(js.ut));
    setText(ui.jackpot, fmt(js.jackpot));
    setText(ui.bet, fmt(js.bet ?? 10));

    setResult("READY");
    setNote("");

    if (js.grid) renderGrid(js.grid);

    // localStorage 잔액 동기화
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const uu = JSON.parse(raw);
        uu.balance = Number(js.ut || 0);
        localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
        localStorage.setItem("myUtPoints", String(Number(js.ut || 0)));
      }
    } catch {}

    return js;
  }

  function winFX(type) {
    // type: "win" | "lose" | "jackpot"
    if (ui.reelWrap) {
      ui.reelWrap.classList.remove("winFlash","jackpotPulse");
      // reflow
      void ui.reelWrap.offsetWidth;
      ui.reelWrap.classList.add("winFlash");
      if (type === "jackpot") ui.reelWrap.classList.add("jackpotPulse");
    }
  }

  async function spin() {
    if (spinning) return;
    spinning = true;

    unlockAudioOnce();
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      sfxPlay(audio.startBtn);
      spinLoopOn();

      setNote("SPINNING…");
      animStart();

      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u })
      }, 20000);

      animStop();
      spinLoopOff();

      if (!js?.ok) {
        setResult("SPIN ERROR", true);
        setNote(`spin fail: ${js?.error || "unknown"}`, true);
        if (String(js?.error || "").includes("insufficient")) stopAuto();
        sfxPlay(audio.lose);
        return;
      }

      setText(ui.wallet, fmt(js.ut));
      setText(ui.jackpot, fmt(js.jackpot));
      setText(ui.bet, fmt(js.bet ?? 10));
      renderGrid(js.grid);

      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);
      const delta = win - betCharged;

      if (delta > 0) {
        setResult(`WIN +${fmt(delta)} UT`);
        winFX("win");
        sfxPlay(audio.win);
      } else if (delta < 0) {
        setResult(`LOSE ${fmt(delta)} UT`);
        winFX("lose");
        sfxPlay(audio.lose);
      } else {
        setResult("EVEN 0 UT");
        sfxPlay(audio.lose);
      }

      // 잭팟 특수 처리(워커가 flag를 주거나 win이 큰 경우)
      if (js.jackpotHit || String(js?.result || "").toLowerCase().includes("jack")) {
        winFX("jackpot");
        sfxPlay(audio.jackpot);
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
      } catch {}

      setNote("");

    } catch (e) {
      animStop();
      spinLoopOff();
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

    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    renderPaytable();
    renderGrid(null);

    await loadState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__ || "no_version");
})();
