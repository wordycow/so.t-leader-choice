/* games/slot/slot.app.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const LS = {
    playerNick: "slotPlayerNick",
    playerName: "slotPlayerName",
    walletUT:   "slotWalletUT",
    bet:        "slotBet",
    auto:       "slotAuto",
    jackpotTicker: "slotJackpotTicker" // JSON { text, untilTs }
  };

  const state = {
    playerNick: "",
    playerName: "",
    walletUT: 0,
    bet: 10,
    auto: false,
    spinning: false,
    autoTimer: null
  };

  // ---------- helpers ----------
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

  function $try(...sels){
    for (const s of sels){
      const el = document.querySelector(s);
      if (el) return el;
    }
    return null;
  }

  function findButtonByText(txt){
    const up = String(txt).toUpperCase();
    const btns = Array.from(document.querySelectorAll("button, a"));
    return btns.find(b => (b.textContent||"").trim().toUpperCase() === up) || null;
  }

  function findValueElForLabel(label){
    const up = String(label).trim().toUpperCase();
    const nodes = Array.from(document.querySelectorAll("small, div, span, p, b, strong"));
    const lab = nodes.find(el => el.childElementCount === 0 && (el.textContent||"").trim().toUpperCase() === up);
    if (!lab) return null;

    const box = lab.closest(".card, .stat, .kv, .cell, .box, .panel, div") || lab.parentElement;
    if (!box) return null;

    // value 후보
    return (
      box.querySelector(".value") ||
      box.querySelector(".val") ||
      box.querySelector("strong") ||
      box.querySelector("b") ||
      Array.from(box.querySelectorAll("div,span,p")).reverse().find(e => e !== lab && e.childElementCount === 0) ||
      null
    );
  }

  function readNumberLS(keys, fallback=0){
    for (const k of keys){
      const v = Number(localStorage.getItem(k));
      if (Number.isFinite(v)) return v;
    }
    return fallback;
  }

  function readTextLS(keys, fallback=""){
    for (const k of keys){
      const v = localStorage.getItem(k);
      if (v && String(v).trim()) return String(v).trim();
    }
    return fallback;
  }

  function loadIdentityFromEverywhere(){
    // 1) unique쪽 전역 state가 있으면 사용
    const U = window.U || window.UNIQUE || window.UNIQUE_STATE || null;

    const nickFromGlobal =
      (window.U?.STATE?.nickname) ||
      (window.UNIQUE?.STATE?.nickname) ||
      (window.U?.state?.nickname) ||
      (window.UNIQUE?.state?.nickname) ||
      "";

    const nameFromGlobal =
      (window.U?.STATE?.name) ||
      (window.UNIQUE?.STATE?.name) ||
      (window.U?.state?.name) ||
      (window.UNIQUE?.state?.name) ||
      "";

    const utFromGlobal =
      Number(window.U?.STATE?.walletUT) ||
      Number(window.UNIQUE?.STATE?.walletUT) ||
      Number(window.U?.state?.walletUT) ||
      Number(window.UNIQUE?.state?.walletUT) ||
      NaN;

    // 2) 로컬스토리지(여러 키를 다 훑어서 “- / 0” 방지)
    const nickLS = readTextLS(
      [LS.playerNick, "uniqueNick", "uniqueNickname", "nickname", "playerNick", "USER_NICK"],
      ""
    );
    const nameLS = readTextLS(
      [LS.playerName, "uniqueName", "name", "displayName", "playerName", "USER_NAME"],
      ""
    );
    const utLS = readNumberLS(
      [LS.walletUT, "uniqueWalletUT", "walletUT", "UT", "userUT"],
      NaN
    );

    state.playerNick = (nickFromGlobal || nickLS || state.playerNick || "").trim();
    state.playerName = (nameFromGlobal || nameLS || state.playerName || "").trim();

    const utPick = Number.isFinite(utFromGlobal) ? utFromGlobal : utLS;
    state.walletUT = Number.isFinite(utPick) ? Math.floor(utPick) : (Number(state.walletUT)||0);

    // 저장(안정화)
    if (state.playerNick) localStorage.setItem(LS.playerNick, state.playerNick);
    if (state.playerName) localStorage.setItem(LS.playerName, state.playerName);
    localStorage.setItem(LS.walletUT, String(state.walletUT));
  }

  function loadBetAuto(){
    const b = Number(localStorage.getItem(LS.bet));
    state.bet = Number.isFinite(b) && b > 0 ? b : state.bet;

    state.auto = (localStorage.getItem(LS.auto) ?? "0") === "1";
  }

  function saveBetAuto(){
    localStorage.setItem(LS.bet, String(state.bet));
    localStorage.setItem(LS.auto, state.auto ? "1" : "0");
  }

  // ---------- UI refs ----------
  const ui = {
    elPlayer: null,
    elWallet: null,
    elJackpot: null,
    elLast: null,
    elBet: null,
    btnSpin: null,
    btnAuto: null,
    btnMinus: null,
    btnPlus: null,
    payTable: null,
    reelsMount: null,
    leftPanel: null,
    ticker: null
  };

  function bindUI(){
    // label 기반(안전)
    ui.elPlayer  = $try("#playerValue",".player-value",".player .value") || findValueElForLabel("PLAYER");
    ui.elWallet  = $try("#walletValue","#walletUT",".wallet-value",".wallet .value") || findValueElForLabel("WALLET (UT)");
    ui.elJackpot = $try("#jackpotValue",".jackpot-value",".jackpot .value") || findValueElForLabel("JACKPOT");
    ui.elLast    = $try("#lastResultValue",".last-value",".last .value") || findValueElForLabel("LAST RESULT");
    ui.elBet     = $try("#betValue",".bet-value",".bet .value") || findValueElForLabel("BET");

    ui.btnSpin = $try("#spinBtn","button[data-spin]",".btn-spin") || findButtonByText("SPIN");
    ui.btnAuto = $try("#autoBtn","button[data-auto]",".btn-auto") || findButtonByText("AUTO OFF") || findButtonByText("AUTO ON") || findButtonByText("AUTO");

    // reels mount
    ui.reelsMount =
      document.getElementById("reels") ||
      document.getElementById("reelMount") ||
      document.getElementById("slotStage") ||
      document.querySelector("[data-slot-stage]") ||
      document.querySelector(".slot-stage") ||
      null;

    // left panel(스핀 버튼 기준)
    if (ui.btnSpin) ui.leftPanel = ui.btnSpin.closest(".left-panel, .panel-left, .panel, .card, .box, div") || null;

    // paytable(없으면 생성)
    ui.payTable = document.getElementById("slotPayTable") || document.querySelector(".slot-paytable") || null;
  }

  // ---------- render ----------
  function renderPlayer(){
    if (!ui.elPlayer) return;

    // ✅ 슬래시 제거: "nick / name" 형태면 split해서 정리
    const nick = (state.playerNick || "-").trim();
    const name = (state.playerName || "").trim();

    const safeNick = nick.replaceAll("/", "").trim();
    const safeName = name.replaceAll("/", "").trim();

    // 두 줄 표현(닉 / 이름)
    ui.elPlayer.innerHTML = `
      <div style="line-height:1.1">
        <div style="font-weight:700; font-size:16px">${escapeHtml(safeNick || "-")}</div>
        <div style="margin-top:4px; opacity:.9; font-size:13px">${escapeHtml(safeName)}</div>
      </div>
    `;
  }

  function renderWallet(animate=false, from=null){
    if (!ui.elWallet) return;
    const to = Math.max(0, Math.floor(state.walletUT||0));

    // 숫자만 찍히는 UI면 innerText로
    if (!animate || from === null){
      ui.elWallet.textContent = String(to);
      return;
    }
    animateNumber(ui.elWallet, from, to, 900);
  }

  function renderBet(){
    if (ui.elBet) ui.elBet.textContent = String(state.bet);
    saveBetAuto();
  }

  function renderAuto(){
    if (!ui.btnAuto) return;
    ui.btnAuto.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
    ui.btnAuto.setAttribute("aria-pressed", state.auto ? "true" : "false");
    saveBetAuto();
  }

  function renderLast(text){
    if (!ui.elLast) return;
    ui.elLast.textContent = text || "READY";
  }

  function ensureBetButtons(){
    // ✅ -5 / +5 버튼이 없으면 BET 아래에 자동 생성
    if (ui.btnMinus && ui.btnPlus) return;

    // 버튼 이미 있으면 연결
    ui.btnMinus = $try("#betMinus",".bet-minus","button[data-bet='-']") || findButtonByText("-5");
    ui.btnPlus  = $try("#betPlus",".bet-plus","button[data-bet='+']") || findButtonByText("+5");
    if (ui.btnMinus && ui.btnPlus) return;

    // 만들어서 꽂기
    const host = ui.elBet?.closest(".card,.stat,.kv,.panel,div") || ui.leftPanel;
    if (!host) return;

    const row = document.createElement("div");
    row.style.display = "grid";
    row.style.gridTemplateColumns = "1fr 1fr";
    row.style.gap = "10px";
    row.style.marginTop = "10px";

    const mkBtn = (txt) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = txt;
      b.style.height = "42px";
      b.style.borderRadius = "14px";
      b.style.border = "1px solid rgba(255,255,255,0.12)";
      b.style.background = "rgba(0,0,0,0.18)";
      b.style.color = "rgba(255,255,255,0.9)";
      b.style.fontWeight = "700";
      b.style.cursor = "pointer";
      return b;
    };

    ui.btnMinus = mkBtn("-5");
    ui.btnPlus  = mkBtn("+5");

    row.appendChild(ui.btnMinus);
    row.appendChild(ui.btnPlus);
    host.appendChild(row);
  }

  function renderPayTable(){
    // ✅ paytable은 모바일에서 최상단 블럭으로
    if (!ui.payTable){
      ui.payTable = document.createElement("div");
      ui.payTable.id = "slotPayTable";
      ui.payTable.className = "slot-paytable";
      ui.payTable.style.margin = "14px 0";
      ui.payTable.style.padding = "14px";
      ui.payTable.style.borderRadius = "18px";
      ui.payTable.style.border = "1px solid rgba(255,255,255,0.10)";
      ui.payTable.style.background = "rgba(0,0,0,0.18)";
      ui.payTable.style.backdropFilter = "blur(10px)";
    }

    const PAY = S.game?.getPayTable ? S.game.getPayTable() : null;
    const IDS = S.game?.getSymbolIds ? S.game.getSymbolIds() : [];

    if (!PAY || IDS.length === 0){
      ui.payTable.innerHTML = `<div style="opacity:.8; font-size:13px">PAYTABLE 로딩중...</div>`;
      return;
    }

    const rows = IDS.map(id => {
      const p = PAY[id] || {};
      const t2 = (p[2] ? `2개: EVEN (x${p[2]})` : "");
      const t3 = (p[3] ? `3개: x${p[3]}` : "");
      const t4 = (p[4] ? `4개: x${p[4]}` : "");
      const t5 = (p[5] ? `5개: x${p[5]}` : "");
      return `
        <div style="display:grid; grid-template-columns:74px 1fr; gap:12px; align-items:center; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.06)">
          <div style="display:flex; align-items:center; gap:8px">
            <img src="img/slot/${id}.png" alt="${id}" style="width:54px;height:54px;object-fit:contain;filter:drop-shadow(0 8px 14px rgba(0,0,0,.35))">
          </div>
          <div style="font-size:13px; opacity:.92; line-height:1.45">
            ${t2 ? `<div>${t2}</div>` : ``}
            ${t3 ? `<div>${t3}</div>` : ``}
            ${t4 ? `<div>${t4}</div>` : ``}
            ${t5 ? `<div>${t5}</div>` : ``}
            ${id==="pro10" ? `<div style="margin-top:4px; font-weight:800; letter-spacing:.3px">5개 = JACKPOT</div>` : ``}
          </div>
        </div>
      `;
    }).join("");

    ui.payTable.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
        <div style="font-weight:900; letter-spacing:.6px">PAYTABLE</div>
        <div style="opacity:.75; font-size:12px">라인은 가로 3줄</div>
      </div>
      <div>${rows}</div>
    `;
  }

  function ensureTicker(){
    if (ui.ticker) return;
    ui.ticker = document.createElement("div");
    ui.ticker.id = "slotJackpotTicker";
    ui.ticker.style.position = "sticky";
    ui.ticker.style.top = "0";
    ui.ticker.style.zIndex = "50";
    ui.ticker.style.height = "40px";
    ui.ticker.style.display = "none";
    ui.ticker.style.alignItems = "center";
    ui.ticker.style.overflow = "hidden";
    ui.ticker.style.borderRadius = "14px";
    ui.ticker.style.border = "1px solid rgba(255,255,255,0.12)";
    ui.ticker.style.background = "rgba(0,0,0,0.20)";
    ui.ticker.style.backdropFilter = "blur(10px)";
    ui.ticker.style.margin = "10px 0";

    const inner = document.createElement("div");
    inner.id = "slotJackpotTickerInner";
    inner.style.whiteSpace = "nowrap";
    inner.style.willChange = "transform";
    inner.style.fontWeight = "900";
    inner.style.letterSpacing = ".4px";
    inner.style.paddingLeft = "100%";
    inner.style.animation = "slotTickerMove 10s linear infinite";
    ui.ticker.appendChild(inner);

    if (!document.getElementById("slotTickerStyle")){
      const st = document.createElement("style");
      st.id = "slotTickerStyle";
      st.textContent = `
@keyframes slotTickerMove {
  0%   { transform: translate3d(0,0,0); }
  100% { transform: translate3d(-120%,0,0); }
}`;
      document.head.appendChild(st);
    }

    // paytable 위에 붙이기(모바일 최상단 느낌)
    const insertTarget =
      document.querySelector(".page-wrap, .shell, .container, main, body") || document.body;
    insertTarget.insertBefore(ui.ticker, insertTarget.firstChild);
  }

  function setTicker(text){
    ensureTicker();
    const inner = document.getElementById("slotJackpotTickerInner");
    if (!inner) return;
    inner.textContent = ` ${text}  —  ${text}  —  ${text} `;
    ui.ticker.style.display = "flex";
  }

  function hideTicker(){
    if (!ui.ticker) return;
    ui.ticker.style.display = "none";
  }

  function persistJackpotTicker(){
    const who = (state.playerName || state.playerNick || "누군가");
    const text = `${who}님이 잭팟이 터지셨습니다. 축하드립니다.`;

    // 자정까지 유지(로컬 시간)
    const now = new Date();
    const midnight = new Date(now);
    midnight.setHours(24,0,0,0);
    const untilTs = midnight.getTime();

    localStorage.setItem(LS.jackpotTicker, JSON.stringify({ text, untilTs }));
    setTicker(text);
  }

  function restoreJackpotTicker(){
    try{
      const raw = localStorage.getItem(LS.jackpotTicker);
      if (!raw) return;
      const obj = JSON.parse(raw);
      if (!obj?.text || !obj?.untilTs) return;
      if (Date.now() >= Number(obj.untilTs)){
        localStorage.removeItem(LS.jackpotTicker);
        hideTicker();
        return;
      }
      setTicker(String(obj.text));
    }catch(e){}
  }

  // ---------- layout (mobile order) ----------
  const originalPos = new WeakMap();

  function rememberPos(node){
    if (!node || originalPos.has(node)) return;
    originalPos.set(node, { parent: node.parentNode, next: node.nextSibling });
  }
  function restorePos(node){
    const pos = originalPos.get(node);
    if (!pos || !pos.parent) return;
    if (pos.next && pos.next.parentNode === pos.parent) pos.parent.insertBefore(node, pos.next);
    else pos.parent.appendChild(node);
  }

  function ensureMobileOrder(){
    const isMobile = window.matchMedia("(max-width: 860px)").matches;

    if (!ui.leftPanel){
      // leftPanel 못찾으면 스핀 버튼 기준으로 다시
      if (!ui.btnSpin) ui.btnSpin = findButtonByText("SPIN");
      if (ui.btnSpin) ui.leftPanel = ui.btnSpin.closest(".left-panel, .panel-left, .panel, .card, .box, div") || null;
    }
    if (!ui.reelsMount) ui.reelsMount = document.getElementById("reels") || document.querySelector(".slot-stage") || null;
    if (!ui.payTable) ui.payTable = document.getElementById("slotPayTable") || null;

    if (!ui.leftPanel || !ui.reelsMount || !ui.payTable) return;

    const stackId = "slotMobileStack";
    let stack = document.getElementById(stackId);

    if (isMobile){
      if (!stack){
        stack = document.createElement("div");
        stack.id = stackId;
        stack.style.display = "flex";
        stack.style.flexDirection = "column";
        stack.style.gap = "14px";

        const host = document.querySelector(".page-wrap, .shell, .container, main") || document.body;
        // 헤더 다음에 들어가게
        host.insertBefore(stack, host.children[1] || null);
      }

      rememberPos(ui.payTable);
      rememberPos(ui.reelsMount);
      rememberPos(ui.leftPanel);

      // ✅ 순서: PAYTABLE → SLOT → ASSET/SPIN
      stack.appendChild(ui.payTable);
      stack.appendChild(ui.reelsMount);
      stack.appendChild(ui.leftPanel);
    } else {
      // 데스크탑 복구
      if (stack){
        restorePos(ui.payTable);
        restorePos(ui.reelsMount);
        restorePos(ui.leftPanel);
        stack.remove();
      }
    }
  }

  // ---------- spin flow ----------
  function setBusy(on){
    state.spinning = !!on;
    if (ui.btnSpin) ui.btnSpin.disabled = state.spinning;
  }

  function betChange(delta){
    // ✅ 5단위
    const next = clamp((Number(state.bet)||10) + delta, 5, 5000);
    state.bet = Math.round(next / 5) * 5;
    renderBet();
  }

  function applyWalletDelta(delta){
    const from = state.walletUT;
    state.walletUT = Math.max(0, Math.floor((state.walletUT||0) + delta));
    localStorage.setItem(LS.walletUT, String(state.walletUT));
    renderWallet(true, from);
  }

  function showWinOverlay(title, delta, durationMs=60000){
    // 1분 축하(잭팟/승리 공통)
    const old = document.getElementById("slotWinOverlay");
    if (old) old.remove();

    const ov = document.createElement("div");
    ov.id = "slotWinOverlay";
    ov.style.position = "fixed";
    ov.style.inset = "0";
    ov.style.zIndex = "9999";
    ov.style.display = "flex";
    ov.style.alignItems = "center";
    ov.style.justifyContent = "center";
    ov.style.background = "rgba(0,0,0,0.55)";
    ov.style.backdropFilter = "blur(6px)";

    const card = document.createElement("div");
    card.style.width = "min(560px, 92vw)";
    card.style.borderRadius = "26px";
    card.style.border = "1px solid rgba(255,255,255,0.16)";
    card.style.background = "rgba(8,10,20,0.72)";
    card.style.padding = "22px";
    card.style.textAlign = "center";
    card.style.boxShadow = "0 20px 70px rgba(0,0,0,0.55)";

    card.innerHTML = `
      <div style="font-weight:1000; letter-spacing:1px; font-size:28px">${escapeHtml(title)}</div>
      <div id="slotOverlayDelta" style="margin-top:10px; font-size:44px; font-weight:1000; letter-spacing:1px">+0 UT</div>
      <div style="margin-top:10px; opacity:.85; font-size:13px">계속 스핀해도 되고, 그냥 즐기게 연출만 해둠</div>
    `;

    ov.appendChild(card);
    document.body.appendChild(ov);

    // 숫자 카운트업
    const el = document.getElementById("slotOverlayDelta");
    if (el){
      animateNumber(el, 0, Math.max(0, Math.floor(delta)), 1600, (v)=>`+${v} UT`);
      // 반짝 효과
      el.style.textShadow = "0 0 18px rgba(255,255,255,0.35)";
    }

    // 클릭하면 즉시 닫기
    ov.addEventListener("click", () => ov.remove());
    setTimeout(() => {
      if (document.getElementById("slotWinOverlay")) ov.remove();
    }, durationMs);
  }

  async function doSpin(){
    if (!S.game?.spin) return;
    if (state.spinning) return;

    loadIdentityFromEverywhere(); // ✅ 스핀 전에 다시 한번 잡아두기
    renderPlayer();
    renderWallet(false);

    // 베팅 차감(시작할 때)
    if ((state.walletUT||0) < state.bet){
      renderLast("NO MONEY");
      return;
    }

    setBusy(true);
    renderLast("SPIN...");

    // 시작 차감(진짜 카지노 느낌)
    applyWalletDelta(-state.bet);

    const res = await S.game.spin({ bet: state.bet }).catch(err => ({ ok:false, error:String(err) }));
    setBusy(false);

    if (!res || !res.ok){
      // 실패하면 베팅 복구
      applyWalletDelta(+state.bet);
      renderLast("ERROR");
      return;
    }

    // 결과 적용(지급)
    if (res.payout > 0){
      applyWalletDelta(+res.payout);
    }

    // 결과 텍스트: EVEN / WIN / LOSE / JACKPOT
    if (res.jackpot){
      renderLast("JACKPOT");
      persistJackpotTicker();
      showWinOverlay("JACKPOT!", Math.max(0, res.payout), 60000);
    } else if (res.even){
      renderLast("EVEN");
      // EVEN은 정신없게 숫자 튀기진 말고 가볍게
    } else if (res.payout > 0){
      renderLast(`WIN +${Math.max(0, res.netDelta)} UT`);
      showWinOverlay("WIN!", Math.max(0, res.netDelta), 12000);
    } else {
      renderLast("LOSE");
    }
  }

  function toggleAuto(){
    state.auto = !state.auto;
    renderAuto();

    if (state.auto){
      // 즉시 1회 실행 후, 이후 반복
      if (!state.autoTimer){
        state.autoTimer = setInterval(() => {
          if (!state.auto) return;
          if (state.spinning) return;
          doSpin();
        }, 700);
      }
      doSpin();
    } else {
      if (state.autoTimer){
        clearInterval(state.autoTimer);
        state.autoTimer = null;
      }
    }
  }

  // ---------- misc ----------
  function escapeHtml(s){
    return String(s || "")
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll('"',"&quot;")
      .replaceAll("'","&#039;");
  }

  function animateNumber(el, from, to, durMs=900, fmt=null){
    const start = performance.now();
    const a = Number(from)||0;
    const b = Number(to)||0;
    const d = Math.max(200, durMs|0);

    const tick = (t) => {
      const p = Math.min(1, (t - start)/d);
      const ease = 1 - Math.pow(1 - p, 3);
      const v = Math.floor(a + (b - a) * ease);
      el.textContent = fmt ? fmt(v) : String(v);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // ---------- wire ----------
  function wire(){
    if (ui.btnSpin){
      ui.btnSpin.addEventListener("click", () => doSpin());
    }
    if (ui.btnAuto){
      ui.btnAuto.addEventListener("click", () => toggleAuto());
    }
    if (ui.btnMinus){
      ui.btnMinus.addEventListener("click", () => betChange(-5));
    }
    if (ui.btnPlus){
      ui.btnPlus.addEventListener("click", () => betChange(+5));
    }
  }

  function init(){
    // game 준비
    try{ S.game?.buildReels?.(); }catch(e){}

    bindUI();

    loadBetAuto();
    loadIdentityFromEverywhere();

    // paytable
    renderPayTable();
    ensureTicker();
    restoreJackpotTicker();

    // bet buttons
    ensureBetButtons();

    // 다시 bind(버튼 생성했을 수 있음)
    bindUI();

    renderPlayer();
    renderWallet(false);
    renderBet();
    renderAuto();
    renderLast("READY");

    wire();

    // 모바일 블럭 순서
    ensureMobileOrder();
    window.addEventListener("resize", () => ensureMobileOrder(), { passive:true });

    // 2초 후 한번 더(늦게 로드되는 unique state 대응)
    setTimeout(() => {
      loadIdentityFromEverywhere();
      renderPlayer();
      renderWallet(false);
      restoreJackpotTicker();
    }, 2000);
  }

  // 외부에서 강제 주입 가능(혹시 unique에서 호출할 때)
  S.setPlayer = (nick, name) => {
    state.playerNick = String(nick||"").trim();
    state.playerName = String(name||"").trim();
    if (state.playerNick) localStorage.setItem(LS.playerNick, state.playerNick);
    if (state.playerName) localStorage.setItem(LS.playerName, state.playerName);
    renderPlayer();
  };
  S.setWalletUT = (ut) => {
    const n = Number(ut);
    if (!Number.isFinite(n)) return;
    state.walletUT = Math.max(0, Math.floor(n));
    localStorage.setItem(LS.walletUT, String(state.walletUT));
    renderWallet(false);
  };

  // boot
  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(window.SLOT);
