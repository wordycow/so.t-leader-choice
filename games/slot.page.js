/* games/slot.page.js
 * THE UNIQUE SLOT - page controller
 * - gate/main에서 저장한 localStorage(uniqueCurrentUser)로 자동 로그인
 * - worker의 /slot/state, /slot/spin 호출로 UT/잭팟/로그 동기화
 */

(() => {
  "use strict";

  // ✅ 네 워커 주소(스크린샷에 찍히던 도메인으로 우선 넣음)
  // 필요하면 여기만 바꾸면 됨.
  const WORKER_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // ------- utils -------
  const $ = (sel) => document.querySelector(sel);
  const byId = (...ids) => {
    for (const id of ids) {
      const el = document.getElementById(id);
      if (el) return el;
    }
    return null;
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function fetchJSON(url, opt) {
    const res = await fetch(url, opt);
    const text = await res.text();
    let js;
    try { js = JSON.parse(text); } catch { js = { ok:false, error:"bad_json", raw:text }; }
    return js;
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
    // slot.html이 /games/ 아래니까 한 단계 위로
    location.href = "../the-unique-gate.html";
  }

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    // UT는 정수처럼 쓰는 분위기라 일단 정수표시
    return String(Math.floor(x));
  }

  function setText(el, v) {
    if (!el) return;
    el.textContent = v;
  }

  // ------- DOM binding (여러 id에 대응: 안 깨지게) -------
  const elPlayer   = byId("playerVal", "player", "slotPlayer", "playerName");
  const elWallet   = byId("walletVal", "wallet", "slotWallet", "walletUt");
  const elJackpot  = byId("jackpotVal", "jackpot", "slotJackpot");
  const elBet      = byId("betVal", "bet", "slotBet");
  const elLast     = byId("lastResultVal", "lastResult", "slotLast", "lastWin");

  const btnSpin    = byId("btnSpin", "spinBtn", "spin");
  const btnAuto    = byId("btnAuto", "autoBtn", "auto");

  const btnPlus    = byId("betPlus", "btnBetPlus", "plus");
  const btnMinus   = byId("betMinus", "btnBetMinus", "minus");

  const gridWrap   = byId("slotGrid", "grid", "reels", "slotReels") || $(".slot-grid") || $(".reels");

  // ------- state -------
  let identity = null;
  let serverBet = 10;
  let autoOn = false;
  let autoTimer = null;
  let spinning = false;

  // 심볼 이미지 매핑(기존 png 그대로 쓰되, 나중에 네온/사이버로 바꾸면 여기만 바꿔도 됨)
  const SYMBOL_IMG = (id) => `../img/slot/${id}.png`; // 폴더 구조에 맞게 조정 가능

  function renderGrid(grid) {
    if (!gridWrap) return;

    // grid가 [ [..5], [..5], [..5] ] 형태라고 가정
    // 컨테이너가 비어있으면 3x5를 만들어주고, 있으면 업데이트
    const rows = Array.isArray(grid) ? grid : [];
    const needCells = 15;

    // 셀 수집/생성
    let cells = gridWrap.querySelectorAll?.("[data-cell='1']");
    if (!cells || cells.length !== needCells) {
      gridWrap.innerHTML = "";
      const frag = document.createDocumentFragment();
      for (let i = 0; i < needCells; i++) {
        const d = document.createElement("div");
        d.dataset.cell = "1";
        d.style.width = "100%";
        d.style.height = "100%";
        d.style.display = "flex";
        d.style.alignItems = "center";
        d.style.justifyContent = "center";
        d.style.borderRadius = "14px";
        d.style.background = "rgba(2,6,23,0.35)";
        d.style.border = "1px solid rgba(250,204,21,0.12)";
        d.style.boxShadow = "inset 0 0 22px rgba(0,0,0,0.6)";
        frag.appendChild(d);
      }
      gridWrap.appendChild(frag);
      cells = gridWrap.querySelectorAll("[data-cell='1']");
    }

    // 값 넣기
    const flat = [];
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 5; c++) {
        flat.push(rows?.[r]?.[c] || "");
      }
    }

    flat.forEach((sym, i) => {
      const cell = cells[i];
      if (!cell) return;
      // 이미지가 없으면 텍스트로라도 보여줌
      cell.innerHTML = "";
      if (sym) {
        const img = document.createElement("img");
        img.src = SYMBOL_IMG(sym);
        img.alt = sym;
        img.style.maxWidth = "86%";
        img.style.maxHeight = "86%";
        img.style.filter = "drop-shadow(0 0 8px rgba(250,204,21,0.25))";
        img.onerror = () => { cell.textContent = sym; };
        cell.appendChild(img);
      }
    });
  }

  function setLastResult({ betCharged, win, utAfter }) {
    const b = Number(betCharged || 0);
    const w = Number(win || 0);
    const delta = w - b;

    let msg = "";
    if (delta > 0) msg = `WIN +${fmt(delta)} UT (bet ${fmt(b)} / win ${fmt(w)})`;
    else if (delta < 0) msg = `LOSE ${fmt(delta)} UT (bet ${fmt(b)} / win ${fmt(w)})`;
    else msg = `EVEN 0 UT (bet ${fmt(b)} / win ${fmt(w)})`;

    setText(elLast, msg);
    if (typeof utAfter !== "undefined") setText(elWallet, fmt(utAfter));
  }

  async function loadState() {
    // ✅ identity.id를 canonical로 사용 (게이트/메인과 동일)
    const u = identity?.id;
    const js = await fetchJSON(`${WORKER_BASE}/slot/state?u=${encodeURIComponent(u)}`, { cache: "no-store" });

    if (!js?.ok) {
      setText(elLast, `STATE ERROR: ${js?.error || "unknown"}`);
      return null;
    }

    serverBet = Number(js.bet || serverBet) || serverBet;

    // PLAYER는 “이름”이 있으면 이름, 없으면 id
    const displayName = String(js?.userName || js?.name || "").trim() || identity.name || identity.id;
    setText(elPlayer, displayName);

    setText(elWallet, fmt(js.ut));
    setText(elJackpot, fmt(js.jackpot));
    setText(elBet, fmt(serverBet));

    // 첫 진입 메시지
    if (elLast && !elLast.textContent) setText(elLast, "READY");

    return js;
  }

  async function doSpin() {
    if (spinning) return;
    spinning = true;

    try {
      const u = identity?.id;
      const js = await fetchJSON(`${WORKER_BASE}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ u })
      });

      if (!js?.ok) {
        setText(elLast, `SPIN ERROR: ${js?.error || "unknown"}`);
        // 잔액 부족이면 자동중단
        if (String(js?.error || "").includes("insufficient")) stopAuto();
        return;
      }

      // UI 반영
      setText(elWallet, fmt(js.ut));
      setText(elJackpot, fmt(js.jackpot));
      setText(elBet, fmt(js.bet));

      renderGrid(js.grid);
      setLastResult({ betCharged: js.betCharged, win: js.win, utAfter: js.ut });

      // localStorage도 최신 잔액으로 업데이트(메인이랑 일치)
      try {
        const raw = localStorage.getItem("uniqueCurrentUser");
        if (raw) {
          const uu = JSON.parse(raw);
          uu.balance = Number(js.ut || 0);
          localStorage.setItem("uniqueCurrentUser", JSON.stringify(uu));
          localStorage.setItem("myUtPoints", String(Number(js.ut || 0)));
        }
      } catch (_) {}

    } finally {
      spinning = false;
    }
  }

  function startAuto() {
    if (autoOn) return;
    autoOn = true;
    if (btnAuto) btnAuto.textContent = "AUTO ON";
    autoTimer = setInterval(() => {
      if (!spinning) doSpin();
    }, 1200);
  }

  function stopAuto() {
    autoOn = false;
    if (btnAuto) btnAuto.textContent = "AUTO OFF";
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = null;
  }

  function toggleAuto() {
    if (autoOn) stopAuto();
    else startAuto();
  }

  // bet +/-는 서버 bet이 config 기반이면(고정) 사실상 UI만 바꾸는 꼴이라
  // 지금은 “표시만” 조절하고, 실제 정산은 서버 bet을 따르게 둠.
  // (원하면 다음 단계에서 서버도 bet 선택 허용으로 확장)
  function bumpBet(dir) {
    serverBet = Math.max(1, serverBet + dir);
    setText(elBet, fmt(serverBet));
    setText(elLast, "BET CHANGE (UI only)");
  }

  // ------- boot -------
  async function boot() {
    identity = getLocalUser();
    if (!identity) return redirectToGate();

    // 메인에서 nickname을 따로 저장해둔 경우도 읽어서 identity에 반영
    const savedNick = localStorage.getItem("myNickname_" + identity.id);
    if (savedNick && !identity.nickname) identity.nickname = String(savedNick).trim();

    // 버튼 바인딩
    if (btnSpin) btnSpin.addEventListener("click", doSpin);
    if (btnAuto) btnAuto.addEventListener("click", toggleAuto);
    if (btnPlus) btnPlus.addEventListener("click", () => bumpBet(+1));
    if (btnMinus) btnMinus.addEventListener("click", () => bumpBet(-1));

    // MAIN 버튼(있다면)
    const mainBtn = byId("btnMain", "mainBtn") || $(".to-main");
    if (mainBtn) mainBtn.addEventListener("click", () => location.href = "../the-unique-main.html");

    await loadState();
  }

  // DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
