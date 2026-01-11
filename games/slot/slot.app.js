/* games/slot/slot.app.js */
window.SLOT = window.SLOT || {};
(function(S){
  "use strict";

  const $ = (id)=> document.getElementById(id);

  const state = {
    ut: 500,
    jackpot: 20,
    bet: 10,
    auto: false,
    busy: false,
    playerId: "wordycow",
    playerName: "이유송"
  };

  function fmt(n){
    const x = Number(n)||0;
    return x.toLocaleString("en-US");
  }

  function clampBet(n){
    n = Math.max(5, Math.min(5000, Math.floor((Number(n)||10)/5)*5));
    if (n % 5 !== 0) n = Math.round(n/5)*5;
    return n;
  }

  function setNote(text){
    if (S.ui && S.ui.setNote) S.ui.setNote(text);
    else { const el = $("uiNote"); if (el) el.textContent = text; }
  }

  function setBet(n){
    state.bet = clampBet(n);
    if (S.ui && S.ui.setBet) S.ui.setBet(fmt(state.bet));
    else { const el = $("uiBet"); if (el) el.textContent = fmt(state.bet); }
  }

  function hardSetWalletText(v){
    const el = $("uiWallet");
    if (el) el.textContent = fmt(v);
  }

  function animateNumber(el, from, to, ms){
    if (!el) return;
    const a = Number(from)||0;
    const b = Number(to)||0;
    const t0 = performance.now();
    const d = b - a;

    const ease = (p)=> 1 - Math.pow(1-p, 3);

    function tick(t){
      const p = Math.min(1, (t - t0) / ms);
      const v = Math.round(a + d * ease(p));
      el.textContent = fmt(v);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // ✅ 족보 UI 채우기 (slot.html의 #uiPaytable)
  function renderPaytable(){
    const wrap = $("uiPaytable");
    if (!wrap || !S.game || !S.game.getPaytable) return;

    const { PAY, SYMBOL_IDS } = S.game.getPaytable();
    const rows = [];

    for (const sym of SYMBOL_IDS){
      const p = PAY[sym] || {};
      const isJack = (sym === "pro10");
      const line = `
        <div class="ptItem">
          <div class="ptLeft">
            <span class="badge">${sym.toUpperCase()}</span>
            <img src="${(S.IMG_PATH ? S.IMG_PATH(sym) : `img/slot/${sym}.png`)}" alt="" style="width:28px;height:28px;object-fit:contain;filter:drop-shadow(0 8px 14px rgba(0,0,0,.35));">
          </div>
          <div class="ptRight">
            <div class="ptLine">2개: <b>EVEN</b> (x${p[2] ?? 1})</div>
            <div class="ptLine">3개: x${p[3] ?? 0}</div>
            <div class="ptLine">4개: x${p[4] ?? 0}</div>
            <div class="ptLine">${isJack ? "5개: <b>JACKPOT</b>" : `5개: x${p[5] ?? 0}`}</div>
          </div>
        </div>
      `;
      rows.push(line);
    }

    wrap.innerHTML = `<div class="paytable">${rows.join("")}</div>`;
  }

  // ✅ 잭팟 티커(자정까지 유지)
  function ensureJackpotTicker(){
    if ($("jackpotTicker")) return;

    const bar = document.createElement("div");
    bar.id = "jackpotTicker";
    bar.style.position = "fixed";
    bar.style.top = "0";
    bar.style.left = "0";
    bar.style.right = "0";
    bar.style.zIndex = "9999";
    bar.style.pointerEvents = "none";
    bar.style.padding = "10px 0";
    bar.style.background = "rgba(0,0,0,0.45)";
    bar.style.backdropFilter = "blur(10px)";
    bar.style.borderBottom = "1px solid rgba(255,255,255,0.12)";
    bar.style.display = "none";
    bar.style.overflow = "hidden";

    const inner = document.createElement("div");
    inner.style.whiteSpace = "nowrap";
    inner.style.display = "inline-block";
    inner.style.willChange = "transform";
    inner.style.paddingLeft = "100%";
    inner.style.animation = "tickerMove 18s linear infinite";
    inner.style.color = "#fff";
    inner.style.fontWeight = "800";
    inner.style.textShadow = "0 10px 30px rgba(0,0,0,.6)";
    inner.id = "jackpotTickerText";

    const st = document.createElement("style");
    st.textContent = `
      @keyframes tickerMove { 0%{ transform:translateX(0);} 100%{ transform:translateX(-100%);} }
    `;
    document.head.appendChild(st);

    bar.appendChild(inner);
    document.body.appendChild(bar);
  }

  function showJackpotTicker(name){
    ensureJackpotTicker();
    const bar = $("jackpotTicker");
    const text = $("jackpotTickerText");
    if (!bar || !text) return;

    text.textContent = `${name}님이 잭팟이 터지셨습니다. 축하드립니다.  🎉🎉🎉`;
    bar.style.display = "block";

    // 자정까지 유지
    const now = new Date();
    const midnight = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0, 0);
    const ttl = midnight.getTime() - now.getTime();

    localStorage.setItem("slotJackpotTicker", JSON.stringify({
      name,
      until: midnight.getTime()
    }));

    setTimeout(() => {
      const saved = JSON.parse(localStorage.getItem("slotJackpotTicker") || "null");
      if (!saved || Date.now() > saved.until){
        bar.style.display = "none";
        localStorage.removeItem("slotJackpotTicker");
      }
    }, Math.min(ttl, 60*1000)); // 1분마다 한번씩만 체크
  }

  function restoreJackpotTicker(){
    ensureJackpotTicker();
    const saved = JSON.parse(localStorage.getItem("slotJackpotTicker") || "null");
    if (!saved) return;
    if (Date.now() > saved.until){
      localStorage.removeItem("slotJackpotTicker");
      return;
    }
    showJackpotTicker(saved.name);
  }

  // ✅ 승리/잭팟 오버레이(잭팟 60초)
  function ensureOverlay(){
    if ($("slotCelebrate")) return;

    const st = document.createElement("style");
    st.textContent = `
      #slotCelebrate{
        position:fixed; inset:0; z-index:10000;
        display:none; align-items:center; justify-content:center;
        background:rgba(0,0,0,.55);
        backdrop-filter: blur(10px);
      }
      #slotCelebrate .card{
        width:min(720px, 92vw);
        border-radius:24px;
        border:1px solid rgba(255,255,255,.16);
        background: radial-gradient(circle at top, rgba(255,255,255,.12), rgba(0,0,0,.35));
        box-shadow: 0 40px 120px rgba(0,0,0,.55);
        padding:22px;
        position:relative;
        overflow:hidden;
        transform: translateY(8px) scale(.98);
        animation: popIn .22s ease forwards;
      }
      #slotCelebrate .title{
        font-weight:900; letter-spacing:.06em;
        font-size:40px;
      }
      #slotCelebrate .amt{
        margin-top:10px;
        font-weight:900;
        font-size:46px;
      }
      #slotCelebrate .sub{
        margin-top:8px;
        opacity:.9;
        font-weight:700;
      }
      #slotCelebrate .close{
        position:absolute; right:14px; top:14px;
        border-radius:14px; padding:10px 12px;
        border:1px solid rgba(255,255,255,.18);
        background:rgba(0,0,0,.25);
        color:#fff; font-weight:800;
        cursor:pointer;
      }
      #slotCelebrate.jackpot .card{
        background: radial-gradient(circle at top, rgba(255,215,0,.18), rgba(0,0,0,.35));
      }
      #slotCelebrate.jackpot .title{
        text-shadow: 0 0 24px rgba(255,215,0,.45);
      }
      #slotCelebrate .spark{
        position:absolute; inset:-40%;
        background:
          radial-gradient(circle, rgba(255,255,255,.18) 0 2px, transparent 3px) 0 0 / 22px 22px;
        opacity:.18;
        animation: sparkMove 1.2s linear infinite;
        pointer-events:none;
      }
      @keyframes sparkMove { from{ transform:translate3d(0,0,0) rotate(0deg);} to{ transform:translate3d(40px,40px,0) rotate(8deg);} }
      @keyframes popIn { to{ transform: translateY(0) scale(1);} }
    `;
    document.head.appendChild(st);

    const ov = document.createElement("div");
    ov.id = "slotCelebrate";
    ov.innerHTML = `
      <div class="spark"></div>
      <div class="card">
        <button class="close">닫기</button>
        <div class="title" id="slotCeleTitle">WIN</div>
        <div class="amt" id="slotCeleAmt">+0 UT</div>
        <div class="sub" id="slotCeleSub"></div>
      </div>
    `;
    document.body.appendChild(ov);

    ov.querySelector(".close").addEventListener("click", () => hideOverlay());
    ov.addEventListener("click", (e)=>{ if (e.target === ov) hideOverlay(); });
  }

  let overlayTimer = null;
  function showOverlay({ title, amountText, subText, jackpot=false, ms=2500 }){
    ensureOverlay();
    const ov = $("slotCelebrate");
    if (!ov) return;

    ov.classList.toggle("jackpot", !!jackpot);
    $("slotCeleTitle").textContent = title;
    $("slotCeleAmt").textContent = amountText;
    $("slotCeleSub").textContent = subText || "";

    ov.style.display = "flex";

    if (overlayTimer) clearTimeout(overlayTimer);
    overlayTimer = setTimeout(() => {
      // 잭팟은 기본 60초지만, 원하면 클릭으로 닫을 수 있게 둠
      hideOverlay();
    }, ms);
  }

  function hideOverlay(){
    const ov = $("slotCelebrate");
    if (ov) ov.style.display = "none";
    if (overlayTimer) clearTimeout(overlayTimer);
    overlayTimer = null;
  }

  async function onSpin(){
    if (state.busy) return;
    state.busy = true;
    setNote("SPINNING...");

    const bet = state.bet;
    if (state.ut < bet){
      setNote("NOT ENOUGH UT");
      state.busy = false;
      return;
    }

    // 잭팟 풀 누적(가볍게)
    state.jackpot = Math.round((state.jackpot + bet * 0.1) * 10) / 10;

    // 실제 스핀
    const res = await S.game.spin({ bet });

    // UT 반영(로컬)
    const prevUt = state.ut;
    const newUt = state.ut - bet + (res.payout || 0);
    state.ut = newUt;

    // UI 반영
    const walletEl = $("uiWallet");
    if (walletEl){
      // 승리/잭팟 때만 카운트업(감성)
      if (newUt >= prevUt) animateNumber(walletEl, prevUt, newUt, res.jackpot ? 2400 : 900);
      else walletEl.textContent = fmt(newUt);
    } else if (S.ui && S.ui.setWallet){
      S.ui.setWallet(fmt(newUt));
    }

    if (S.ui && S.ui.setJackpot) S.ui.setJackpot(fmt(state.jackpot));
    else { const je = $("uiJackpot"); if (je) je.textContent = fmt(state.jackpot); }

    // ✅ 결과 텍스트 규칙
    if (res.jackpot){
      setNote("JACKPOT !!!");
      // 잭팟 터지면 풀 리셋(연출용)
      state.jackpot = 20;
      if (S.ui && S.ui.setJackpot) S.ui.setJackpot(fmt(state.jackpot));

      showJackpotTicker(state.playerName);
      showOverlay({
        title: "JACKPOT",
        amountText: `+${fmt(Math.max(0, res.netDelta||0))} UT`,
        subText: "축하 60초 연출 (클릭하면 닫힘)",
        jackpot: true,
        ms: 60_000
      });
    } else if ((res.payout||0) > 0 && (res.netDelta||0) === 0){
      // 2개 본전: EVEN
      setNote("EVEN");
      showOverlay({
        title: "EVEN",
        amountText: "+0 UT",
        subText: "본전 HIT",
        jackpot: false,
        ms: 1400
      });
    } else if ((res.payout||0) > 0){
      setNote(`WIN +${fmt(Math.max(0, res.netDelta||0))} UT`);
      showOverlay({
        title: "WIN",
        amountText: `+${fmt(Math.max(0, res.netDelta||0))} UT`,
        subText: "좋아. 계속 간다.",
        jackpot: false,
        ms: 2200
      });
    } else {
      setNote("LOSE");
      // LOSE는 오버레이 안 띄움(짜증 덜 나게)
    }

    // 서버 기록(있으면)
    try{
      if (S.api && S.api.commitSlotSpin){
        await S.api.commitSlotSpin({
          bet,
          payout: res.payout||0,
          net: res.netDelta||0,
          jackpot: !!res.jackpot
        });
      }
    }catch(e){}

    state.busy = false;
  }

  function bindUI(){
    // player 표시: slash 절대 안 씀(두 줄)
    const p = $("uiPlayer");
    if (p) p.innerHTML = `<div>${state.playerId}</div><div style="opacity:.85;font-weight:700">${state.playerName}</div>`;

    if (S.ui){
      S.ui.setWallet(fmt(state.ut));
      S.ui.setJackpot(fmt(state.jackpot));
      S.ui.setBet(fmt(state.bet));
      S.ui.setAuto(false);
      S.ui.setSound(S.game.getSoundEnabled());
      S.ui.setNote("READY");
    } else {
      hardSetWalletText(state.ut);
      const je = $("uiJackpot"); if (je) je.textContent = fmt(state.jackpot);
      const be = $("uiBet"); if (be) be.textContent = fmt(state.bet);
      setNote("READY");
    }

    // 버튼
    const btnSpin = $("btnSpin");
    const btnAuto = $("btnAuto");
    const btnSound= $("btnSound");
    const btnBetDown = $("btnBetDown");
    const btnBetUp   = $("btnBetUp");
    const btnMain = $("btnMain");

    if (btnSpin) btnSpin.addEventListener("click", onSpin);

    if (btnAuto) btnAuto.addEventListener("click", async ()=>{
      state.auto = !state.auto;
      if (S.ui && S.ui.setAuto) S.ui.setAuto(state.auto);

      // auto loop
      while(state.auto){
        await onSpin();
        await new Promise(r=>setTimeout(r, 450));
      }
    });

    if (btnSound) btnSound.addEventListener("click", ()=>{
      const on = !S.game.getSoundEnabled();
      S.game.setSoundEnabled(on);
      if (S.ui && S.ui.setSound) S.ui.setSound(on);
    });

    if (btnBetDown) btnBetDown.addEventListener("click", ()=> setBet(state.bet - 5));
    if (btnBetUp)   btnBetUp.addEventListener("click", ()=> setBet(state.bet + 5));

    if (btnMain) btnMain.addEventListener("click", ()=>{
      location.href = "../index.html";
    });
  }

  async function init(){
    // 릴 만들기
    if (S.game && S.game.buildReels) S.game.buildReels();

    // 족보 그리기
    renderPaytable();

    // 잭팟 티커 복구
    restoreJackpotTicker();

    // UI 연결
    bindUI();
  }

  // 시작
  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})(window.SLOT);
