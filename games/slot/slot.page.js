// games/slot/slot.page.js
(() => {
  const API_BASE = String(window.SLOT_API_BASE || "").trim().replace(/\/+$/, "");
  const S = window.SLOT = window.SLOT || {};

  const els = {
    bg: document.getElementById("bg"),
    hint: document.getElementById("hintText"),
    player: document.getElementById("playerName"),
    wallet: document.getElementById("walletUt"),
    jackpot: document.getElementById("jackpotVal"),
    round: document.getElementById("roundVal"),

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

  function assertDom() {
    // 핵심 엘리먼트 없으면 “하얀페이지 + 콘솔에러” 나니까 여기서 딱 끊는다
    const must = ["hint","player","wallet","jackpot","round","betMinus","betPlus","betAmount","payTable","payline","spinBtn","autoBtn","autoText"];
    for (const k of must) {
      if (!els[k]) {
        alert(`DOM 누락: #${k} (slot.html이 다른 버전으로 바뀐 상태임)`);
        throw new Error("dom_missing_" + k);
      }
    }
    for (let i=0;i<5;i++){
      if (!els.reels[i]) {
        alert(`DOM 누락: #reel${i}`);
        throw new Error("dom_missing_reel" + i);
      }
    }
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
    spinning: false,
    auto: false,

    // identity: 이름 우선 + 동명이인 시 id로 분기
    name: (localStorage.getItem("unique_name") || "").trim(),      // ✅ 메인에서 저장해주면 최고
    id: (localStorage.getItem("unique_id") || "").trim(),          // ✅ 동명이인일 때만 필요
    nickname: (localStorage.getItem("unique_nickname") || "").trim(), // 있으면 같이 보내줌(보조키)

    displayName: "",
    ut: 0,
    jackpot: 0,

    bet: 10,
    betMin: 10,
    betMax: 1000,
    betStep: 10,

    roundDelta: 0,
  };

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

  function setRoundDelta(n){
    state.roundDelta = Number(n || 0);
    const v = Math.round(state.roundDelta);
    els.round.textContent = (v > 0 ? `+${v}` : `${v}`);
    els.round.classList.remove("gold","red");
    if (v > 0) els.round.classList.add("gold");
    else if (v < 0) els.round.classList.add("red");
    else els.round.classList.add("gold");
  }

  function updateUI(){
    const name = state.displayName || state.name || state.nickname || "Guest";
    els.player.textContent = name;
    els.wallet.textContent = Number(state.ut || 0).toFixed(2);
    els.jackpot.textContent = String(Math.floor(Number(state.jackpot || 0)));
    els.betAmount.textContent = String(state.bet);
    setRoundDelta(state.roundDelta);
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
  function randomSymbolId(){ return SYMBOLS[(Math.random()*SYMBOLS.length)|0].id; }

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

  // ---------- Identity ----------
  function identityQuery(){
    // ✅ 이름 우선. 동명이인일 때만 id가 필요.
    const q = new URLSearchParams();
    if (state.name) q.set("name", state.name);
    if (state.id) q.set("id", state.id);
    if (state.nickname) q.set("nickname", state.nickname);
    return q.toString();
  }

  function requireIdentityOrGuide(){
    // name이 없으면 메인에서 저장하도록 유도
    if (state.name) return true;
    hint("이름 정보가 없음. MAIN에서 회원가입/접속 후 들어와.");
    alert("이름(name) 정보가 없습니다.\nMAIN에서 로그인/회원정보(이름) 저장 후 다시 들어오세요.");
    return false;
  }

  function setChosenId(id){
    const v = String(id || "").trim();
    if (!v) return;
    state.id = v;
    localStorage.setItem("unique_id", v);
  }

  // ---------- API ----------
  function apiUrl(path){
    if(!API_BASE) return path;
    return API_BASE + path;
  }

  async function apiState(){
    if(!requireIdentityOrGuide()) return { ok:false, error:"missing_name" };
    const qs = identityQuery();
    const url = apiUrl(`/slot/state?${qs}`);
    const res = await fetch(url, { method:"GET" });
    return await res.json();
  }

  async function apiSpin(){
    if(!requireIdentityOrGuide()) return { ok:false, error:"missing_name" };
    const url = apiUrl(`/slot/spin`);
    const body = {
      name: state.name,
      id: state.id,
      nickname: state.nickname,
      bet: state.bet
    };
    const res = await fetch(url, {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(body)
    });
    return await res.json();
  }

  // ---------- Controls ----------
  function alignBet(n){
    const step = Math.max(1, state.betStep|0);
    let v = Math.round(Number(n||0) / step) * step;
    v = Math.max(state.betMin, Math.min(state.betMax, v));
    return v;
  }

  function changeBet(delta){
    if(state.spinning) return;
    state.bet = alignBet(state.bet + delta);
    S.audio?.playOne?.("start");
    updateUI();
  }

  function handleDuplicateName(out){
    const list = out?.candidates || [];
    if(!list.length){
      alert("동명이인인데 후보를 못 받음. 시트 확인 필요");
      return false;
    }

    const msg = [
      "동명이인이 있습니다. 아래 후보 중 본인 id를 입력하세요.",
      "",
      ...list.map((c, i) => `${i+1}) id=${c.id} / name=${c.name} / nick=${c.nickname || "-"} / team=${c.team || "-"}`),
      "",
      "id를 정확히 복사해서 붙여넣기.",
    ].join("\n");

    const picked = prompt(msg, list[0]?.id || "");
    if(!picked) return false;
    setChosenId(picked);
    return true;
  }

  async function spinOnce(){
    if(state.spinning) return;

    state.spinning = true;
    els.spinBtn.disabled = true;
    els.payline.classList.remove("show");
    state.roundDelta = 0;
    updateUI();

    S.audio?.unlockAudio?.();
    S.audio?.playOne?.("start");

    hint("Spinning... 숨참기 😈");
    startSpinVisual();
    S.audio?.startSpinSound?.();

    let out;
    try{
      out = await apiSpin();

      // ✅ 동명이인
      if(out && out.ok === false && out.error === "duplicate_name"){
        S.audio?.stopSpinSound?.();
        initReels();
        state.spinning = false;
        els.spinBtn.disabled = false;

        const ok = handleDuplicateName(out);
        if(ok) {
          hint("id 저장됨. 다시 SPIN 눌러.");
        } else {
          hint("id 선택이 필요함.");
        }
        if(state.auto) setAuto(false);
        return;
      }

      if(!out || !out.ok) throw new Error(out?.error || "spin_failed");
    }catch(e){
      S.audio?.stopSpinSound?.();
      initReels();
      state.spinning = false;
      els.spinBtn.disabled = false;
      hint("에러. 워커/시트/이름(id) 매칭 확인");
      alert("Spin Error: " + (e?.message || e));
      if(state.auto) setAuto(false);
      return;
    }

    // 서버 반영
    state.displayName = out.displayName || out.name || "";
    if(out.ut != null) state.ut = Number(out.ut);
    if(out.jackpot != null) state.jackpot = Number(out.jackpot);

    // 이번 판 손익(±)
    state.roundDelta = Number(out.delta || 0);

    const grid = out.grid;
    const win = Number(out.win || 0);

    await new Promise(r => setTimeout(r, 850));

    for(let i=0;i<5;i++){
      await new Promise(r => setTimeout(r, 230 + i*160));
      const col3 = [ grid?.[0]?.[i], grid?.[1]?.[i], grid?.[2]?.[i] ];
      stopReel(i, col3);
      S.audio?.playStopTick?.();
    }

    S.audio?.stopSpinSound?.();
    updateUI();

    if(win > 0){
      flashBg();
      els.payline.classList.add("show");
      hint(out.winType === "JACKPOT" ? "잭팟! 👑" : "승리! 🔥");
      S.audio?.playOne?.(out.winType === "JACKPOT" ? "jackpot" : "win");
    } else {
      hint("다음 판이 진짜다 😅");
      S.audio?.playOne?.("lose");
    }

    state.spinning = false;
    els.spinBtn.disabled = false;

    if(state.auto){
      setTimeout(async () => {
        if(!state.auto) return;
        if(Number(state.ut||0) < Number(state.bet||0)){
          setAuto(false);
          hint("UT 부족. AUTO OFF");
          return;
        }
        spinOnce();
      }, 1200);
    }
  }

  async function refreshStateSilent(){
    if(!state.name) return;
    try{
      const st = await apiState();
      if(st && st.ok){
        state.displayName = st.displayName || st.name || "";
        state.ut = Number(st.ut || 0);
        state.jackpot = Number(st.jackpot || 0);

        const cfg = st.slot_config || {};
        state.betMin = Number(cfg.BET_MIN || state.betMin);
        state.betMax = Number(cfg.BET_MAX || state.betMax);
        state.betStep = Number(cfg.BET_STEP || state.betStep);

        // bet은 현재값 유지하되 범위 보정
        state.bet = alignBet(state.bet);
        updateUI();
      } else if(st && st.ok === false && st.error === "duplicate_name") {
        // 조용히 후보만 표시하지 말고 힌트만
        hint("동명이인: id 설정 필요(자동갱신 멈춤)");
      }
    }catch(_){}
  }

  async function boot(){
    assertDom();
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
    const st = await apiState();

    // ✅ 동명이인 처리: state에서도 터질 수 있음
    if(st && st.ok === false && st.error === "duplicate_name"){
      const ok = handleDuplicateName(st);
      if(ok){
        // id 저장 후 다시 state 불러오기
        const st2 = await apiState();
        if(st2?.ok){
          state.displayName = st2.displayName || st2.name || "";
          state.ut = Number(st2.ut || 0);
          state.jackpot = Number(st2.jackpot || 0);
          const cfg = st2.slot_config || {};
          state.betMin = Number(cfg.BET_MIN || state.betMin);
          state.betMax = Number(cfg.BET_MAX || state.betMax);
          state.betStep = Number(cfg.BET_STEP || state.betStep);
          state.bet = alignBet(Number(st2.bet || state.bet));
          updateUI();
          hint("준비 완료. SPIN 눌러라 😈");
        } else {
          hint("id 저장했는데 상태를 못 불러옴. 워커/시트 확인");
        }
      } else {
        hint("동명이인: id 선택 필요");
      }
      return;
    }

    if(!st || !st.ok){
      hint("유저 상태를 못 불러옴(이름/id/시트/워커 확인)");
      updateUI();
      return;
    }

    state.displayName = st.displayName || st.name || "";
    state.ut = Number(st.ut || 0);
    state.jackpot = Number(st.jackpot || 0);

    const cfg = st.slot_config || {};
    state.betMin = Number(cfg.BET_MIN || state.betMin);
    state.betMax = Number(cfg.BET_MAX || state.betMax);
    state.betStep = Number(cfg.BET_STEP || state.betStep);

    state.bet = alignBet(Number(st.bet || state.bet));
    updateUI();
    hint("준비 완료. SPIN 눌러라 😈");

    // ✅ 시트↔사이트 양방향 반영: 10초마다 상태 갱신
    setInterval(refreshStateSilent, 10000);
  }

  window.addEventListener("load", boot);
})();
