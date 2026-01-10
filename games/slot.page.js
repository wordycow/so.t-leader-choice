/* games/slot.page.js
 * THE UNIQUE SLOT - FINAL (UT fix + vertical spin + 404 cleanup + sounds)
 * - main/gate에서 저장한 localStorage(uniqueCurrentUser, myUtPoints) 기반으로 UT 즉시 표시
 * - worker /slot/state, /slot/spin 응답 키가 달라도 최대한 유연하게 UT 잡아오기
 * - 이미지: games/img/slot/(pro1~10, star1~3)만 로드 → jackpot.png/slide*.png 같은 404 제거
 * - 사운드: games/sounds/*.MP3 파일명(하이픈/대소문자) 기준으로 정확히 로드
 * - 스핀 연출: 위→아래 “슬롯처럼” 랜덤 그리드가 빠르게 내려가는 느낌(클라 연출)
 */

(() => {
  "use strict";

  // ======================
  // ✅ CONFIG
  // ======================
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // GitHub Pages 캐시 확인용
  const VERSION = "slot.page.js@2026-01-10_final_v3";
  window.__UNIQUE_SLOT_PAGE__ = VERSION;

  // 이 페이지(/games/slot.html) 기준 상대경로
  const IMG_BASE = "./img/slot/";
  const SOUND_BASE = "./sounds/";

  // 네 폴더에 실제로 존재하는 심볼만 (slide1~8 제거 완료 전제)
  const SYMBOLS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // ======================
  // ✅ DOM
  // ======================
  const $id = (id) => document.getElementById(id);

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

  // ======================
  // ✅ STYLE INJECT (spin FX)
  // ======================
  function injectStyleOnce() {
    if (document.getElementById("unique-slot-style")) return;
    const s = document.createElement("style");
    s.id = "unique-slot-style";
    s.textContent = `
      /* spin 느낌: 위→아래로 흐르는 모션 + 블러 */
      #uiReels.isSpinning { filter: blur(.55px) saturate(1.18) contrast(1.08); }
      #uiReels.isSpinning .cell { overflow:hidden; }
      #uiReels.isSpinning .sym { animation: symDrop .12s linear infinite; }
      @keyframes symDrop {
        0%   { transform: translateY(-8px); opacity:.78; }
        100% { transform: translateY(8px);  opacity:.95; }
      }
      #uiReels.winFlash { animation: winFlash .55s ease-out 1; }
      @keyframes winFlash{
        0%{ box-shadow: 0 0 0 rgba(0,0,0,0); }
        45%{ box-shadow: 0 0 28px rgba(33,246,255,.22), 0 0 34px rgba(255,43,214,.16); }
        100%{ box-shadow: 0 0 0 rgba(0,0,0,0); }
      }
      #uiReelWrap.jackpotPulse { animation: jackpotPulse .85s ease-in-out 2; }
      @keyframes jackpotPulse{
        0%{ transform: scale(1); }
        50%{ transform: scale(1.012); }
        100%{ transform: scale(1); }
      }
    `;
    document.head.appendChild(s);
  }

  // ======================
  // ✅ UT/NUMBER utils
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

  // 응답에서 UT를 최대한 잡아오기 (키가 바뀌어도 대응)
  function pickUT(js) {
    if (!js || typeof js !== "object") return null;

    const candidates = [
      js.ut,
      js.UT,
      js.balance,
      js.wallet,
      js.points,
      js.utPoints,
      js.myUtPoints,
      js.user?.ut,
      js.user?.balance,
      js.data?.ut,
      js.data?.balance,
      js.state?.ut,
    ];

    for (const c of candidates) {
      const n = toNum(c);
      if (n !== null) return n;
    }
    return null;
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

  // ======================
  // ✅ LOCAL USER (main에서 저장된 값)
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

  // ======================
  // ✅ HTTP
  // ======================
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
  // ✅ REELS RENDER
  // ======================
  const ROWS = 3;
  const COLS = 5;

  function ensureCells() {
    if (!ui.reels) return [];
    const need = ROWS * COLS;

    // 네 slot.html에서 .cell 구조가 이미 있을 수도 있으니 둘 다 대응
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

  function randomSym() {
    return SYMBOLS[(Math.random() * SYMBOLS.length) | 0];
  }

  function randomGrid() {
    const g = [];
    for (let r = 0; r < ROWS; r++) {
      const row = [];
      for (let c = 0; c < COLS; c++) row.push(randomSym());
      g.push(row);
    }
    return g;
  }

  function isPngSymbol(sym) {
    const s = String(sym || "").toLowerCase();
    return /^pro\d+$/.test(s) || /^star\d+$/.test(s);
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
      const box = cell?.querySelector?.(".sym");
      if (!box) return;

      const s = String(sym || "");
      box.innerHTML = "";

      // 심볼이 비어있으면 빈칸
      if (!s) return;

      // PNG가 “존재하는 심볼(pro/star)”만 로드 → jackpot.png 같은 404 자체 차단
      if (isPngSymbol(s)) {
        const img = document.createElement("img");
        img.src = `${IMG_BASE}${s.toLowerCase()}.png`; // 파일명이 소문자일 때 가장 안전
        img.alt = s;
        img.style.width = "88%";
        img.style.height = "88%";
        img.style.objectFit = "contain";
        img.onerror = () => {
          // 혹시 파일이 대소문자 섞였으면 원본 심볼로 한 번 더 시도
          img.src = `${IMG_BASE}${s}.png`;
          img.onerror = () => img.remove();
        };
        box.appendChild(img);
      } else {
        // 예외 심볼은 그냥 텍스트(혹은 나중에 SVG)
        box.textContent = s;
      }
    });
  }

  // ======================
  // ✅ SPIN VISUAL (vertical 느낌)
  // ======================
  let spinFxTimer = null;

  function startSpinVisual() {
    if (!ui.reels) return;
    ui.reels.classList.add("isSpinning");

    // “위→아래로 빠르게 돌아가는 느낌” = 랜덤 그리드 고속 갱신
    // (서버 응답 기다리는 동안 연출)
    if (spinFxTimer) clearInterval(spinFxTimer);
    spinFxTimer = setInterval(() => {
      renderGrid(randomGrid());
    }, 70);
  }

  function stopSpinVisual() {
    if (!ui.reels) return;
    ui.reels.classList.remove("isSpinning");
    if (spinFxTimer) clearInterval(spinFxTimer);
    spinFxTimer = null;
  }

  // ======================
  // ✅ SOUNDS (파일명 정확히)
  // ======================
  const sounds = {
    start:   new Audio(`${SOUND_BASE}start-button-sound.MP3`),
    spin:    new Audio(`${SOUND_BASE}spining-sound.MP3`),   // 네 폴더 파일명이 spining 임(중요)
    stop:    new Audio(`${SOUND_BASE}stop-stop-stop-sound.MP3`),
    win:     new Audio(`${SOUND_BASE}win-sound.MP3`),
    lose:    new Audio(`${SOUND_BASE}lose-sound.MP3`),
    jackpot: new Audio(`${SOUND_BASE}jackpot-sound.MP3`),
  };

  let audioUnlocked = false;

  function audioInit() {
    // preload / 기본 설정
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
      // 사용자 제스처 안에서 호출되면 unlock 됨
      const a = sounds.start;
      a.currentTime = 0;
      await a.play();
      a.pause();
      audioUnlocked = true;
      return true;
    } catch {
      // autoplay 정책으로 실패해도 게임은 진행
      audioUnlocked = false;
      return false;
    }
  }

  function playSound(key) {
    const a = sounds[key];
    if (!a) return;
    try {
      a.currentTime = 0;
      a.play().catch(() => {});
    } catch (_) {}
  }

  function startSpinSound() {
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
  // ✅ GAME STATE / ACTIONS
  // ======================
  let identity = null;
  let autoOn = false;
  let spinning = false;
  let autoTimer = null;

  function setWalletNow(n, sourceLabel) {
    if (n === null || n === undefined) return;
    setText(ui.wallet, fmtInt(n));
    if (sourceLabel) {
      // 디버그 필요하면 잠깐 확인 가능
      // console.log("[WALLET]", n, sourceLabel);
    }
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
    const url = `${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}&name=${encodeURIComponent(identity.name || "")}&nick=${encodeURIComponent(identity.nickname || "")}`;
    const js = await fetchJSON(url);

    if (!js?.ok) {
      setResult("STATE ERROR", true);

      // ✅ UT라도 로컬에 있으면 보여줘야 함
      setWalletNow(identity.balance ?? 0, "local_fallback");

      setNote(`state fail: ${js?.error || "unknown"} (메인에서 등록/로그인 후 다시)`, true);
      return null;
    }

    // 표시명
    const displayName = String(js?.userName || js?.name || "").trim() || identity.name || identity.id;
    setText(ui.player, displayName);

    // ✅ UT 우선: worker → 없으면 localStorage → 없으면 0
    const ut = pickUT(js);
    if (ut !== null) setWalletNow(ut, "worker_state");
    else setWalletNow(identity.balance ?? 0, "local_balance");

    // 잭팟/베팅
    const jackpot = toNum(js.jackpot ?? js.JACKPOT);
    if (jackpot !== null) setText(ui.jackpot, fmtInt(jackpot));

    const bet = toNum(js.bet ?? js.BET);
    if (bet !== null) setText(ui.bet, fmtInt(bet));

    // grid가 있으면 렌더
    if (js.grid) renderGrid(js.grid);
    else renderGrid(randomGrid()); // 빈 화면 방지용

    setResult("READY");
    setNote("");

    return js;
  }

  async function spin() {
    if (spinning) return;

    spinning = true;
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      await unlockAudioOnce();
      playSound("start");

      // ✅ 스핀 연출 시작
      startSpinVisual();
      startSpinSound();

      const u = identity?.id;
      if (!u) throw new Error("missing_user");

      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        // worker가 u 말고 name/nick을 키로 쓰는 경우도 있어서 같이 보냄(무해)
        body: JSON.stringify({
          u,
          name: identity.name || "",
          nickname: identity.nickname || "",
        })
      });

      // ✅ 스핀 연출 종료
      stopSpinVisual();
      stopSpinSound();
      playSound("stop");

      if (!js?.ok) {
        setResult("SPIN ERROR", true);

        // 유저 미등록이면 이 메시지가 뜸
        const err = String(js?.error || "unknown");
        if (err.includes("user_not_found")) {
          setNote("유저가 슬롯 시트에 없음 → 메인에서 등록/동기화 후 다시 오세요.", true);
        } else {
          setNote(`spin fail: ${err}`, true);
        }

        // UT는 로컬값이라도 유지
        setWalletNow(identity.balance ?? 0, "local_keep");
        if (err.includes("insufficient")) stopAuto();
        return;
      }

      // ✅ 응답 반영
      // UT
      const ut = pickUT(js);
      if (ut !== null) setWalletNow(ut, "worker_spin");

      // 잭팟/베팅
      const jackpot = toNum(js.jackpot ?? js.JACKPOT);
      if (jackpot !== null) setText(ui.jackpot, fmtInt(jackpot));
      const bet = toNum(js.bet ?? js.BET);
      if (bet !== null) setText(ui.bet, fmtInt(bet));

      // 그리드
      if (js.grid) renderGrid(js.grid);

      // 결과 문구
      const betCharged = toNum(js.betCharged) ?? (bet ?? 0);
      const win = toNum(js.win) ?? 0;
      const delta = (win ?? 0) - (betCharged ?? 0);

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

      // 잭팟 연출 (서버가 jackpotHit 같은 플래그를 주면 그걸 쓰는 게 베스트인데, 없으면 win이 큰 경우로 추정)
      if (toNum(js.jackpotHit) === 1 || toNum(js.isJackpot) === 1) {
        ui.reelWrap?.classList?.add("jackpotPulse");
        setTimeout(() => ui.reelWrap?.classList?.remove("jackpotPulse"), 1800);
        playSound("jackpot");
      }

      setNote("");

      // ✅ localStorage 잔액 동기화 (다음 진입에서도 UT 뜨게)
      if (ut !== null) {
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

    } catch (e) {
      stopSpinVisual();
      stopSpinSound();
      playSound("stop");

      setResult("SPIN ERROR", true);
      setNote(String(e?.message || e), true);
      stopAuto();
    } finally {
      spinning = false;
      if (ui.btnSpin) ui.btnSpin.disabled = false;
    }
  }

  // ======================
  // ✅ PAYTABLE (간단 표시: 404 없이)
  // ======================
  function renderPaytable() {
    if (!ui.pay) return;
    ui.pay.innerHTML = `
      <div class="ptItem"><div class="ptLeft"><div class="badge">S</div>STAR</div><div class="ptMul">star1~3</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">P</div>PRO</div><div class="ptMul">pro1~10</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">JP</div>JACKPOT</div><div class="ptMul">SPECIAL</div></div>
    `;
  }

  // ======================
  // ✅ BOOT
  // ======================
  async function boot() {
    injectStyleOnce();
    audioInit();
    renderPaytable();

    identity = getLocalUser();
    if (!identity) return redirectToGate();

    // 이름/닉네임 보조
    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    // ✅ 들어오자마자 “메인에서 저장된 UT”를 먼저 찍어준다 (가장 중요)
    setText(ui.player, identity.name || identity.id);
    setWalletNow(identity.balance ?? 0, "local_on_boot");

    // 버튼 바인딩
    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    // 빈 화면 방지
    renderGrid(randomGrid());
    setResult("READY");
    setNote("");

    // worker 상태 동기화
    await loadState();

    console.log("SLOT UI LOADED ✅", VERSION);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
