const API_BASE = "https://the-unique.yourworker.workers.dev";

// games/slot/slot.page.js
(() => {
  const S = window.SLOT = window.SLOT || {};

  // ✅ 네 Worker URL로 바꿔라 (예: https://xxx.workers.dev)
  // 지금 이미 슬롯이 돌아가고 있는 워커 도메인 쓰면 됨
  const API_BASE = (localStorage.getItem("unique_slot_api") || "").trim() || ""; 
  // API_BASE가 비어있으면 "상대경로"로 호출 (같은 도메인에 워커 프록시가 있을 때만)
  // 보통은 아래처럼 강제로 박아두는 걸 추천:
  // const API_BASE = "https://YOUR-WORKER.yourname.workers.dev";

  const els = {
    bg: document.getElementById("bg"),
    hint: document.getElementById("hintText"),
    player: document.getElementById("playerName"),
    wallet: document.getElementById("walletUt"),
    jackpot: document.getElementById("jackpotVal"),
    win: document.getElementById("winVal"),

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

  function imgOf(id){
    // games/slot.html 기준: img/slot/<id>.png
    return `img/slot/${id}.png`;
  }

  const state = {
    spinning: false,
    auto: false,

    // 서버에서 갱신됨
    ut: 0,
    jackpot: 0,
    bet: 10,

    betMin: 10,
    betMax: 1000,
    betStep: 10,

    // 유저 식별(닉네임 기준)
    nickname: (localStorage.getItem("unique_nickname") || "").trim(), // 내부 키
    displayName: "",

    // 마지막 결과
    lastWin: 0
  };

  // ---------- UI helpers ----------
  function flashBg(){
    if(!els.bg) return;
    els.bg.classList.add("flash");
    setTimeout(()=>els.bg.classList.remove("flash"), 280);
  }
  function hint(t){ els.hint.textContent = t; }

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

  function updateUI(){
    els.player.textContent = state.displayName || state.nickname || "Guest";
    els.wallet.textContent = Number(state.ut || 0).toFixed(2);
    els.jackpot.textContent = String(Math.floor(Number(state.jackpot || 0)));
    els.win.textContent = String(Math.floor(Number(state.lastWin || 0)));
    els.betAmount.textContent = String(state.bet);
  }

  function buildPayTable(){
    els.payTable.innerHTML = "";
    // 위에서부터 고급이 보이게 역순
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
  function randomSymbolId(){
    return SYMBOLS[Math.floor(Math.random()*SYMBOLS.length)].id;
  }

  function stripHtml(count, loop=false){
    // 3 visible + extra for loop 느낌
    const n = loop ? Math.max(count, 22) : count;
    let html = "";
    for(let i=0;i<n;i++){
      const id = randomSymbolId();
      html += `<div class="symbol"><img src="${imgOf(id)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>`;
    }
    if(loop){
      // 루프용 복제(절반 이동)
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
    // final3: [top, mid, bot]
    const strip = els.reels[i];
    strip.classList.remove("spinning");

    const top = final3[0] || randomSymbolId();
    const mid = final3[1] || randomSymbolId();
    const bot = final3[2] || randomSymbolId();

    strip.innerHTML = `
      <div class="symbol"><img src="${imgOf(top)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
      <div class="symbol"><img src="${imgOf(mid)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
      <div class="symbol"><img src="${imgOf(bot)}" onerror="this.src='https://via.placeholder.com/120?text=?'"></div>
    `;
    strip.style.transform = "translateY(0)";
  }

  // ---------- API ----------
  function apiUrl(path){
    if(API_BASE) return API_BASE.replace(/\/+$/,"") + path;
    return path; // fallback
  }

  async function apiState(){
    if(!state.nickname){
      // 닉네임이 없으면 최소한 "이유송"으로 임시 설정해도 되지만,
      // 시트에서 닉네임 매칭이 안 될 수 있으니 안내
      return { ok:false, error:"missing_nickname" };
    }
    const url = apiUrl(`/slot/state?u=${encodeURIComponent(state.nickname)}`);
    const res = await fetch(url, { method:"GET" });
    return await res.json();
  }

  async function apiSpin(){
    const url = apiUrl(`/slot/spin`);
    const body = { u: state.nickname, bet: state.bet };
    const res = await fetch(url, {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(body)
    });
    return await res.json();
  }

  // ---------- Controls ----------
  function changeBet(delta){
    if(state.spinning) return;
    const next = Math.max(state.betMin, Math.min(state.betMax, state.bet + delta));
    // step 정렬
    const step = Math.max(1, state.betStep);
    const aligned = Math.round(next / step) * step;
    state.bet = Math.max(state.betMin, Math.min(state.betMax, aligned));
    S.audio?.playOne("start");
    updateUI();
  }

  async function spinOnce(){
    if(state.spinning) return;
    state.spinning = true;

    els.spinBtn.disabled = true;
    els.payline.classList.remove("show");
    state.lastWin = 0;
    updateUI();

    // 오디오 언락 & 시작
    S.audio?.unlockAudio();
    S.audio?.playOne("start");

    hint("Spinning... 숨참기 😈");
    startSpinVisual();
    S.audio?.startSpinSound();

    let out;
    try{
      out = await apiSpin();
      if(!out || !out.ok) throw new Error(out?.error || "spin_failed");
    }catch(e){
      S.audio?.stopSpinSound();
      initReels();
      state.spinning = false;
      els.spinBtn.disabled = false;
      hint("에러났음. 닉네임/워커/시트 연결 확인 ㄱㄱ");
      alert("Spin Error: " + (e?.message || e));
      if(state.auto) setAuto(false);
      return;
    }

    // 서버에서 UT/표시명/잭팟 갱신
    if(out.displayName) state.displayName = out.displayName;
    if(out.ut != null) state.ut = Number(out.ut);
    if(out.jackpot != null) state.jackpot = Number(out.jackpot);

    const grid = out.grid;
    const win = Number(out.win || 0);
    state.lastWin = Math.floor(win);

    // 최소 연출 시간
    await new Promise(r => setTimeout(r, 850));

    // 릴 순차 정지 + 멈춤 틱
    for(let i=0;i<5;i++){
      await new Promise(r => setTimeout(r, 230 + i*160));

      // grid는 3x5
      const col3 = [
        grid?.[0]?.[i],
        grid?.[1]?.[i],
        grid?.[2]?.[i],
      ];
      stopReel(i, col3);

      // ✅ 릴 멈춤 소리 = 틱
      S.audio?.playStopTick();
    }

    // 스핀 사운드 종료
    S.audio?.stopSpinSound();

    // 결과 처리
    updateUI();

    const wt = String(out.winType || "").toLowerCase();
    if(win > 0){
      flashBg();
      els.payline.classList.add("show");

      if(wt.includes("jackpot")){
        hint("잭팟! PRO10 터졌다 👑");
        S.audio?.playOne("jackpot");
      } else {
        hint("승리! UT 쌓이는 맛 🔥");
        S.audio?.playOne("win");
      }
    } else {
      hint("다음 판이 진짜다 😅");
      S.audio?.playOne("lose");
    }

    state.spinning = false;
    els.spinBtn.disabled = false;

    // AUTO
    if(state.auto){
      // 잔액 부족 대비: 다음 state에서 ut 확인
      setTimeout(async () => {
        if(!state.auto) return;
        // 잔액 부족이면 auto off
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

    // 버튼 바인딩
    els.betMinus.addEventListener("click", () => changeBet(-state.betStep));
    els.betPlus.addEventListener("click", () => changeBet(+state.betStep));

    els.autoBtn.addEventListener("click", () => {
      S.audio?.unlockAudio();
      S.audio?.playOne("start");
      setAuto(!state.auto);
      if(state.auto && !state.spinning) spinOnce();
    });

    els.spinBtn.addEventListener("click", () => spinOnce());

    // 상태 로드
    hint("서버 상태 불러오는 중...");
    const st = await apiState();
    if(!st || !st.ok){
      hint(state.nickname ? "유저 상태를 못 불러옴(닉네임/시트 매칭 확인)" : "닉네임이 없음. MAIN에서 닉네임 등록 후 다시 들어와.");
      // 그래도 UI는 기본값
      updateUI();
      return;
    }

    // state 반영
    state.displayName = st.displayName || "";
    state.ut = (st.ut != null) ? Number(st.ut) : 0;
    state.jackpot = Number(st.jackpot || 0);

    // bet 범위(워커가 안 주면 기본값)
    const cfg = st.slot_config || {};
    state.bet = Number(st.bet || cfg.BET_UT || state.bet);
    state.betMin = Number(cfg.BET_MIN || state.betMin);
    state.betMax = Number(cfg.BET_MAX || state.betMax);
    state.betStep = Number(cfg.BET_STEP || state.betStep);

    // bet을 범위에 맞게 정렬
    state.bet = Math.max(state.betMin, Math.min(state.betMax, state.bet));
    updateUI();
    hint("준비 완료. SPIN 눌러라 😈");
  }

  window.addEventListener("load", boot);
})();
