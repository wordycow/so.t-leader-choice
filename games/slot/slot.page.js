/* games/slot/slot.page.js */
(() => {
  const S = (window.SLOT = window.SLOT || {});
  if(!S.api){
    console.error("[slot.page] SLOT.api missing. slot.api.js 로드 순서/경로 확인");
    return;
  }

  const els = {
    bg: document.getElementById("bg"),
    hint: document.getElementById("hintText"),
    player: document.getElementById("playerName"),
    wallet: document.getElementById("walletUt"),
    jackpot: document.getElementById("jackpotVal"),
    delta: document.getElementById("deltaUt"),

    betMinus: document.getElementById("betMinus"),
    betPlus: document.getElementById("betPlus"),
    betAmount: document.getElementById("betAmount"),

    payTable: document.getElementById("payTable"),
    payline: document.getElementById("payline"),

    spinBtn: document.getElementById("spinBtn"),
    autoBtn: document.getElementById("autoBtn"),
    autoText: document.getElementById("autoText"),

    reels: [
      document.getElementById("reel0"),
      document.getElementById("reel1"),
      document.getElementById("reel2"),
      document.getElementById("reel3"),
      document.getElementById("reel4"),
    ],
  };

  // ✅ HTML이 구형이면 여기서 바로 잡아주고 종료 (하얀화면 방지)
  const required = ["hint","player","wallet","jackpot","delta","payTable","spinBtn","autoBtn","autoText","payline"];
  const missing = required.filter(k => !els[k]);
  if(missing.length){
    console.error("[slot.page] required DOM missing:", missing);
    alert("slot.html이 구형/깨짐 상태야. 내가 준 games/slot.html로 덮어써야 함.\nmissing: " + missing.join(", "));
    return;
  }
  if(els.reels.some(x => !x)){
    console.error("[slot.page] reels DOM missing");
    alert("릴 DOM(reel0~4)이 없어. games/slot.html을 완전체로 덮어써야 함.");
    return;
  }

  const SYMBOLS = [
    { id:"star1", name:"STAR 1", payout:2 },
    { id:"star2", name:"STAR 2", payout:3 },
    { id:"star3", name:"STAR 3", payout:5 },
    { id:"pro1", name:"PRO 1", payout:8 },
    { id:"pro2", name:"PRO 2", payout:12 },
    { id:"pro3", name:"PRO 3", payout:16 },
    { id:"pro4", name:"PRO 4", payout:24 },
    { id:"pro5", name:"PRO 5", payout:32 },
    { id:"pro6", name:"PRO 6", payout:48 },
    { id:"pro7", name:"PRO 7", payout:64 },
    { id:"pro8", name:"PRO 8", payout:96 },
    { id:"pro9", name:"PRO 9", payout:128 },
    { id:"pro10", name:"PRO 10", payout:200 },
  ];

  function imgOf(id){ return `img/slot/${id}.png`; }

  const state = {
    spinning:false,
    auto:false,

    name:"",
    ut:0,
    jackpot:0,

    bet:10,
    betMin:10,
    betMax:1000,
    betStep:10,

    lastDelta:0
  };

  function hint(t){ els.hint.textContent = t; }

  function flashBg(){
    els.bg.classList.add("flash");
    setTimeout(()=>els.bg.classList.remove("flash"), 280);
  }

  function setAuto(on){
    state.auto = !!on;
    if(state.auto){
      els.autoBtn.classList.add("active");
      els.autoText.textContent = "AUTO ON";
    } else {
      els.autoBtn.classList.remove("active");
      els.autoText.textContent = "AUTO OFF";
    }
  }

  function fmtDelta(n){
    const v = Math.floor(Number(n || 0));
    if(v > 0) return `+${v}`;
    if(v < 0) return `${v}`;
    return "0";
  }

  function updateUI(){
    els.player.textContent = state.name || "Guest";
    els.wallet.textContent = Number(state.ut || 0).toFixed(2);
    els.jackpot.textContent = String(Math.floor(Number(state.jackpot || 0)));
    els.delta.textContent = fmtDelta(state.lastDelta);
    els.betAmount.textContent = String(state.bet);
  }

  function buildPayTable(){
    els.payTable.innerHTML = "";
    [...SYMBOLS].reverse().forEach(s => {
      const div = document.createElement("div");
      div.className = "pay-item";
      div.innerHTML = `
        <img class="pay-img" src="${imgOf(s.id)}" onerror="this.src='https://via.placeholder.com/26?text=?'">
        <div class="pay-name">${s.name}</div>
        <div class="pay-mul">x${s.payout}</div>
      `;
      els.payTable.appendChild(div);
    });
  }

  // ---------- Reel visuals ----------
  function randomSymbolId(){ return SYMBOLS[Math.floor(Math.random()*SYMBOLS.length)].id; }

  function stripHtml(count, loop=false){
    const n = loop ? Math.max(count, 22) : count;
    let html = "";
    for(let i=0;i<n;i++){
      const id = randomSymbolId();
      html += `<div class="symbol"><img src="${imgOf(id)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>`;
    }
    if(loop){
      for(let i=0;i<n;i++){
        const id = randomSymbolId();
        html += `<div class="symbol"><img src="${imgOf(id)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>`;
      }
    }
    return html;
  }

  function initReels(){
    for(let i=0;i<5;i++){
      const strip = els.reels[i];
      strip.innerHTML = stripHtml(3,false);
      strip.style.transform = "translateY(0)";
      strip.classList.remove("spinning");
      strip.style.animationDelay = "0s";
    }
  }

  function startSpinVisual(){
    for(let i=0;i<5;i++){
      const strip = els.reels[i];
      strip.innerHTML = stripHtml(22,true);
      strip.classList.add("spinning");
      strip.style.animationDelay = `${i*0.08}s`;
      strip.style.transform = "translateY(0)";
    }
  }

  function stopReel(i, final3){
    const strip = els.reels[i];
    strip.classList.remove("spinning");

    const top = final3?.[0] || randomSymbolId();
    const mid = final3?.[1] || randomSymbolId();
    const bot = final3?.[2] || randomSymbolId();

    strip.innerHTML = `
      <div class="symbol"><img src="${imgOf(top)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
      <div class="symbol"><img src="${imgOf(mid)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
      <div class="symbol"><img src="${imgOf(bot)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
    `;
    strip.style.transform = "translateY(0)";
  }

  // ---------- Controls ----------
  function changeBet(delta){
    if(state.spinning) return;

    const next = Math.max(state.betMin, Math.min(state.betMax, state.bet + delta));
    const step = Math.max(1, state.betStep);
    const aligned = Math.round(next / step) * step;

    state.bet = Math.max(state.betMin, Math.min(state.betMax, aligned));
    S.audio?.unlockAudio?.();
    S.audio?.playOne?.("start");
    updateUI();
  }

  async function spinOnce(){
    if(state.spinning) return;
    state.spinning = true;

    els.spinBtn.disabled = true;
    els.payline.classList.remove("show");
    state.lastDelta = 0;
    updateUI();

    S.audio?.unlockAudio?.();
    S.audio?.playOne?.("start");
    hint("Spinning... 숨참기 😈");
    startSpinVisual();
    S.audio?.startSpinSound?.();

    // UT 변화 계산용(베팅 포함 반영하려면 worker가 delta를 내려주는 게 베스트)
    const before = Number(state.ut || 0);

    let out;
    try{
      out = await S.api.spin({ bet: state.bet });
      if(!out || !out.ok) throw new Error(out?.error || "spin_failed");
    }catch(e){
      S.audio?.stopSpinSound?.();
      initReels();
      state.spinning = false;
      els.spinBtn.disabled = false;
      hint("에러. 유저 매칭/워커 응답 확인 ㄱㄱ");
      alert("Spin Error: " + (e?.message || e));
      if(state.auto) setAuto(false);
      return;
    }

    // 서버 갱신값 반영
    if(out.displayName) state.name = out.displayName;
    if(out.name) state.name = out.name;
    if(out.ut != null) state.ut = Number(out.ut);
    if(out.jackpot != null) state.jackpot = Number(out.jackpot);

    const after = Number(state.ut || 0);

    // ✅ worker가 delta를 주면 그걸 신뢰, 없으면 before/after로 계산
    const delta = (out.delta != null) ? Number(out.delta) : (after - before);
    state.lastDelta = delta;

    const grid = out.grid;

    await new Promise(r => setTimeout(r, 850));

    for(let i=0;i<5;i++){
      await new Promise(r => setTimeout(r, 230 + i*160));
      const col3 = [ grid?.[0]?.[i], grid?.[1]?.[i], grid?.[2]?.[i] ];
      stopReel(i, col3);
      S.audio?.playStopTick?.();
    }

    S.audio?.stopSpinSound?.();
    updateUI();

    if(delta > 0){
      flashBg();
      els.payline.classList.add("show");
      const wt = String(out.winType || "").toLowerCase();
      if(wt.includes("jackpot")){
        hint("잭팟! 👑");
        S.audio?.playOne?.("jackpot");
      } else {
        hint("승리! 🔥");
        S.audio?.playOne?.("win");
      }
    } else if(delta < 0){
      hint("잃었음. 다음 판이 진짜다 😅");
      S.audio?.playOne?.("lose");
    } else {
      hint("본전. 다시 😈");
      S.audio?.playOne?.("start");
    }

    state.spinning = false;
    els.spinBtn.disabled = false;

    if(state.auto){
      setTimeout(() => {
        if(!state.auto) return;
        if(Number(state.ut || 0) < Number(state.bet || 0)){
          setAuto(false);
          hint("UT 부족. AUTO OFF");
          return;
        }
        spinOnce();
      }, 1200);
    }
  }

  async function boot(){
    buildPayTable();
    initReels();

    els.betMinus.addEventListener("click", () => changeBet(-state.betStep));
    els.betPlus.addEventListener("click", () => changeBet(+state.betStep));

    els.autoBtn.addEventListener("click", () => {
      S.audio?.unlockAudio?.();
      S.audio?.playOne?.("start");
      setAuto(!state.auto);
      if(state.auto && !state.spinning) spinOnce();
    });

    els.spinBtn.addEventListener("click", () => spinOnce());

    hint("서버 상태 불러오는 중...");
    let st;
    try{
      st = await S.api.state();
    }catch(e){
      console.error(e);
      hint("서버 응답이 JSON이 아님. API_BASE/워커 URL부터 확인.");
      updateUI();
      return;
    }

    if(!st || !st.ok){
      hint("유저 상태를 못 불러옴 (이름/아이디 매칭 또는 워커 로직 확인)");
      updateUI();
      return;
    }

    state.name = st.displayName || st.name || state.name;
    state.ut = (st.ut != null) ? Number(st.ut) : 0;
    state.jackpot = Number(st.jackpot || 0);

    const cfg = st.slot_config || {};
    state.bet = Number(st.bet || cfg.BET_UT || state.bet);
    state.betMin = Number(cfg.BET_MIN || state.betMin);
    state.betMax = Number(cfg.BET_MAX || state.betMax);
    state.betStep = Number(cfg.BET_STEP || state.betStep);

    state.bet = Math.max(state.betMin, Math.min(state.betMax, state.bet));
    updateUI();
    hint("준비 완료. SPIN 눌러라 😈");
  }

  window.addEventListener("DOMContentLoaded", boot);
})();
