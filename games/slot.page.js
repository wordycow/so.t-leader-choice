/* games/slot.page.js
 * THE UNIQUE SLOT (cyber + vertical spin + sounds)
 * - main/gate에서 저장한 localStorage(uniqueCurrentUser)로 자동 로그인
 * - WORKER_BASE /slot/state, /slot/spin 호출
 * - UT 숫자 안 보이는 이슈(네온 텍스트 투명) -> JS fallback으로 강제 표시
 * - user_not_found_in_sheet 등 에러를 UI에 확실히 표시 + AUTO 중단
 * - 이미지: ./img/slot/  (games/img/slot)
 * - 사운드: ./sounds/   (games/sounds)
 */

(() => {
  "use strict";

  // ✅ 워커 주소
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ✅ 버전 마커 (콘솔로 적용 확인)
  window.__UNIQUE_SLOT_PAGE__ = "slot.page.js@2026-01-10_vertical_spin_sound_v2";

  // ✅ 리소스 베이스 (slot.html이 /games/ 안에 있으므로 상대경로는 ./)
  const IMG_BASE = "./img/slot/";
  const SND_BASE = "./sounds/";

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

  function redirectToGate() {
    location.href = "../the-unique-gate.html";
  }

  function goMain() {
    location.href = "../the-unique-main.html";
  }

  function getLocalUser() {
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return null;
      const u = JSON.parse(raw);

      const id = String(u?.id || "").trim().toLowerCase();
      if (!id) return null;

      // main에서 myUtPoints만 쓰는 경우도 있어서 fallback
      const myUt = Number(localStorage.getItem("myUtPoints") || 0);

      return {
        id,
        name: String(u?.name || "").trim(),
        nickname: String(u?.nickname || "").trim(),
        balance: Number(u?.balance || myUt || 0),
      };
    } catch {
      return null;
    }
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

  // ---------- CSS fallback (UT 안 보이는 문제 강제 해결) ----------
  function forceNeonVisible(el, fallbackColor = "#21f6ff") {
    if (!el) return;
    const c = getComputedStyle(el).color;
    // transparent면 computed가 rgba(0,0,0,0)로 나오는 경우가 많음
    if (c.includes("rgba(0, 0, 0, 0)") || c === "transparent") {
      el.style.color = fallbackColor;        // 숫자 무조건 보이게
      el.style.webkitTextFillColor = "";     // 사파리/크롬 꼬임 방지
    }
  }

  // ---------- assets ----------
  // 404 스팸 방지용: 한 번 실패한 파일은 다시 안 부름
  const missingAsset = new Set();

  // worker가 어떤 심볼명을 주든 파일명으로 “정규화”
  // ✅ slide1~8은 제외
  function symbolToFile(symRaw) {
    const s = String(symRaw || "").trim().toLowerCase();
    if (!s) return null;

    // 금지: slide*
    if (s.startsWith("slide")) return null;

    // jackpot
    if (s === "jackpot" || s.includes("jack")) return "jackpot.png";

    // star1~3
    const mStar = s.match(/^star\s*([1-3])$/);
    if (mStar) return `star${mStar[1]}.png`;

    // pro1~10
    const mPro = s.match(/^pro\s*([1-9]|10)$/);
    if (mPro) return `pro${mPro[1]}.png`;

    // worker가 STAR_1 같은 형태면 보정
    const mStar2 = s.match(/^star[_-]?([1-3])$/);
    if (mStar2) return `star${mStar2[1]}.png`;

    const mPro2 = s.match(/^pro[_-]?([1-9]|10)$/);
    if (mPro2) return `pro${mPro2[1]}.png`;

    return null;
  }

  function imgUrlFor(symRaw) {
    const file = symbolToFile(symRaw);
    if (!file) return null;

    const key = file;
    if (missingAsset.has(key)) return null;

    return IMG_BASE + file;
  }

  // ---------- sounds ----------
  const SND = {
    start:  new Audio(SND_BASE + "start-button-sound.MP3"),
    spin:   new Audio(SND_BASE + "spining-sound.MP3"),
    win:    new Audio(SND_BASE + "win_sound.MP3"),
    lose:   new Audio(SND_BASE + "lose_sound.MP3"),
    jackpot:new Audio(SND_BASE + "jackpot-sound.MP3"),
    stop:   new Audio(SND_BASE + "stop-stop-stop-sound.MP3"),
  };

  // loop 설정 (스핀 도는 동안)
  SND.spin.loop = true;

  // 브라우저 정책상 “첫 사용자 제스처” 이후에만 재생 가능
  let audioUnlocked = false;
  function unlockAudioOnce() {
    if (audioUnlocked) return;
    audioUnlocked = true;
    // 아주 짧게 재생/정지로 unlock
    try {
      SND.start.volume = 0.001;
      SND.start.play().then(() => {
        SND.start.pause();
        SND.start.currentTime = 0;
        SND.start.volume = 1;
      }).catch(() => {});
    } catch {}
  }

  function sfxPlay(a, vol = 1) {
    if (!audioUnlocked) return;
    try {
      a.pause();
      a.currentTime = 0;
      a.volume = vol;
      a.play().catch(() => {});
    } catch {}
  }

  function spinLoopOn() {
    if (!audioUnlocked) return;
    try {
      SND.spin.volume = 0.65;
      SND.spin.play().catch(() => {});
    } catch {}
  }

  function spinLoopOff() {
    try {
      SND.spin.pause();
      SND.spin.currentTime = 0;
    } catch {}
  }

  // ---------- reels (vertical spin animation) ----------
  const ROWS = 3;
  const COLS = 5;

  // 랜덤 후보(슬라이드 제거)
  const RANDOM_POOL = (() => {
    const arr = [];
    for (let i = 1; i <= 10; i++) arr.push(`pro${i}`);
    for (let i = 1; i <= 3; i++) arr.push(`star${i}`);
    arr.push("jackpot");
    return arr;
  })();

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

  // 네온 SVG(이미지 없어도 “광기” 유지)
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
        <circle cx="100" cy="100" r="72" fill="rgba(0,0,0,.12)" stroke="url(#g)" stroke-width="10" filter="url(#glow)"/>
        <path d="M100 48 L120 92 L168 92 L130 120 L146 168 L100 140 L54 168 L70 120 L32 92 L80 92 Z"
              fill="url(#g)" filter="url(#glow)" opacity="0.95"/>
      </svg>
    `;
  }

  function renderSymbolInto(box, symRaw) {
    if (!box) return;
    const sym = String(symRaw || "");
    box.innerHTML = sym ? svgFor(sym) : "";

    const url = imgUrlFor(sym);
    if (!url) return;

    const img = document.createElement("img");
    img.src = url;
    img.alt = sym;

    img.onerror = () => {
      // 한 번 실패하면 기억해두고 이후 렌더에서 재요청 안 함
      const file = symbolToFile(sym);
      if (file) missingAsset.add(file);
      img.remove();
    };

    box.appendChild(img);
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
      renderSymbolInto(box, sym);
    });
  }

  // “위에서 아래로 쏟아지는” 세로 스핀 연출
  // - 컬럼별로 빠르게 랜덤 교체하다가 왼쪽부터 순차적으로 멈춤
  function startVerticalSpinFX(msPerCol = 850, tickMs = 55, stagger = 120) {
    const cells = ensureCells();
    if (!cells.length) return { stopAll: () => {} };

    const intervals = [];
    for (let c = 0; c < COLS; c++) {
      const startDelay = c * stagger;

      const handle = setTimeout(() => {
        // 컬럼에 해당하는 3개 셀 index: r*COLS + c
        const idxs = [0 * COLS + c, 1 * COLS + c, 2 * COLS + c];

        const interval = setInterval(() => {
          // 위->아래로 “흘러내리는 느낌”을 주기 위해
          // (아래칸 <- 위칸, 위칸 <- 새 랜덤)
          const b0 = cells[idxs[0]]?.querySelector(".sym");
          const b1 = cells[idxs[1]]?.querySelector(".sym");
          const b2 = cells[idxs[2]]?.querySelector(".sym");

          const pick = RANDOM_POOL[(Math.random() * RANDOM_POOL.length) | 0];

          // 아래로 밀기
          if (b2 && b1) b2.innerHTML = b1.innerHTML;
          if (b1 && b0) b1.innerHTML = b0.innerHTML;
          if (b0) renderSymbolInto(b0, pick);

          // 살짝 블러/잔상
          for (const idx of idxs) {
            const el = cells[idx];
            if (!el) continue;
            el.style.filter = "blur(0.8px) saturate(1.4)";
          }
        }, tickMs);

        intervals.push(interval);

        // 컬럼 시간 지나면 멈추기(필터 제거)
        setTimeout(() => {
          clearInterval(interval);
          for (let r = 0; r < ROWS; r++) {
            const el = cells[r * COLS + c];
            if (el) el.style.filter = "";
          }
        }, msPerCol);

      }, startDelay);

      intervals.push(handle);
    }

    return {
      stopAll: () => {
        for (const it of intervals) {
          try { clearInterval(it); clearTimeout(it); } catch {}
        }
        // 필터 제거
        const all = ensureCells();
        for (const el of all) el.style.filter = "";
      }
    };
  }

  // ---------- paytable UI (슬라이드 제거) ----------
  function renderPaytableUI() {
    if (!ui.pay) return;
    const items = [
      { key: "STAR",  desc: "star1~3", tag: "x ?" },
      { key: "PRO",   desc: "pro1~10", tag: "x ?" },
      { key: "JACKPOT", desc: "special", tag: "SPECIAL" },
    ];

    ui.pay.innerHTML = items.map(it => `
      <div class="ptItem">
        <div class="ptLeft">
          <div class="badge">${it.key[0]}</div>
          <div>
            <div style="font-weight:900; letter-spacing:.08em;">${it.key}</div>
            <div style="opacity:.75; font-size:11px; margin-top:2px;">${it.desc}</div>
          </div>
        </div>
        <div class="ptMul">${it.tag}</div>
      </div>
    `).join("");
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
      setResult(`STATE ERROR`, true);
      setNote(`state fail: ${js?.error || "unknown"}`, true);
      return null;
    }

    const displayName = String(js?.userName || js?.name || "").trim() || identity.name || identity.id;

    setText(ui.player, displayName);
    setText(ui.wallet, fmt(js.ut));
    setText(ui.jackpot, fmt(js.jackpot));
    setText(ui.bet, fmt(js.bet ?? 10));

    console.log("[SLOT] STATE OK", { ut: js.ut, jackpot: js.jackpot, bet: js.bet });

    setResult("READY");
    setNote("");

    if (js.grid) renderGrid(js.grid);
    return js;
  }

  async function spin() {
    if (spinning) return;
    spinning = true;

    unlockAudioOnce();

    if (ui.btnSpin) ui.btnSpin.disabled = true;

    // 스핀 시작 SFX
    sfxPlay(SND.start, 0.9);
    spinLoopOn();

    // “세로로 도는” 연출 시작
    const fx = startVerticalSpinFX(850, 55, 120);

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
        spinLoopOff();
        fx.stopAll();

        setResult("SPIN ERROR", true);

        // 핵심 에러 메시지 보기 좋게
        if (js?.error === "user_not_found_in_sheet") {
          setNote("유저가 슬롯 시트에 없음 → 메인에서 등록/동기화 후 다시 오세요.", true);
          stopAuto();
          // 바로 메인으로 가게 유도(원하면 자동 이동도 가능)
          // goMain();
        } else if (String(js?.error || "").includes("insufficient")) {
          setNote("잔액 부족(UT) → AUTO 중단", true);
          stopAuto();
        } else {
          setNote(`spin fail: ${js?.error || "unknown"}`, true);
        }

        return;
      }

      // 최종 결과 렌더
      fx.stopAll();
      spinLoopOff();

      setText(ui.wallet, fmt(js.ut));
      setText(ui.jackpot, fmt(js.jackpot));
      setText(ui.bet, fmt(js.bet ?? 10));

      renderGrid(js.grid);

      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);
      const delta = win - betCharged;

      if (delta > 0) {
        setResult(`WIN +${fmt(delta)} UT`);
        sfxPlay(SND.win, 0.95);
      } else if (delta < 0) {
        setResult(`LOSE ${fmt(delta)} UT`);
        sfxPlay(SND.lose, 0.85);
      } else {
        setResult(`EVEN 0 UT`);
        sfxPlay(SND.stop, 0.7);
      }

      // 잭팟이면 잭팟 SFX 추가
      if (String(js?.winType || "").toLowerCase().includes("jackpot") || String(js?.hit || "").toLowerCase().includes("jackpot")) {
        sfxPlay(SND.jackpot, 1);
      }

      // localStorage 잔액 동기화(메인/게이트와 동일)
      try {
        const raw = localStorage.getItem("uniqueCurrentUser");
        if (raw) {
          const uu = JSON.parse(raw);
          uu.balance = Number(js.ut || 0);
          localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
          localStorage.setItem("myUtPoints", String(Number(js.ut || 0)));
        }
      } catch (_) {}

      console.log("[SLOT] SPIN OK", { ut: js.ut, win: js.win, betCharged: js.betCharged });

      setNote("");

    } catch (e) {
      spinLoopOff();
      fx.stopAll();

      setResult("SPIN ERROR", true);
      setNote(String(e?.message || e), true);
      stopAuto();
    } finally {
      spinning = false;
      if (ui.btnSpin) ui.btnSpin.disabled = false;
    }
  }

  // ---------- boot ----------
  function bindAudioUnlockToFirstGesture() {
    // 클릭/터치 첫 순간에만 unlock
    const fn = () => {
      unlockAudioOnce();
      window.removeEventListener("pointerdown", fn);
      window.removeEventListener("keydown", fn);
    };
    window.addEventListener("pointerdown", fn, { once: true });
    window.addEventListener("keydown", fn, { once: true });
  }

  async function boot() {
    identity = getLocalUser();
    if (!identity) return redirectToGate();

    // nickname 보조 저장값
    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    // UI 즉시 표시(서버 응답 전에 “메인 UT라도” 먼저 보여주기)
    setText(ui.player, identity.nickname || identity.name || identity.id);
    setText(ui.wallet, fmt(identity.balance || 0));
    forceNeonVisible(ui.wallet); // ✅ UT 안 보이는 문제 해결
    forceNeonVisible(ui.bet);

    renderPaytableUI();
    renderGrid(null);

    bindAudioUnlockToFirstGesture();

    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", toggleAuto);

    // 서버 상태 동기화
    await loadState();

    console.log("SLOT UI LOADED ✅", window.__UNIQUE_SLOT_PAGE__);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
