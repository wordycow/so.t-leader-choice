(function () {
  window.SLOT = window.SLOT || {};
  const CFG = window.SLOT.config;
  const API = window.SLOT.api;
  const UI  = window.SLOT.ui;
  const AUD = window.SLOT.audio;
  const GAME= window.SLOT.game;

  function round2(n){ return Math.round(n*100)/100; }
  function safeName(s){
    return String(s||"")
      .replace(/[\/\\<>]/g,"")
      .replace(/\s+/g," ")
      .trim();
  }
  function fmt(n){
    const x = Number(n||0);
    if (!Number.isFinite(x)) return "0";
    if (Math.abs(x) >= 1000) return x.toLocaleString("en-US");
    return (Math.round(x*100)/100).toString();
  }
  function clamp(n,min,max){ return Math.max(min, Math.min(max, n)); }

  // ✅ 로그인 id 복구: gate에서 저장한 uniqueCurrentUser 포함해서 전부 찾음
  function readLoginId(){
    const q = new URLSearchParams(location.search);
    const qid = (q.get("id") || q.get("uid") || q.get("user_id") || "").trim();
    if (qid){
      localStorage.setItem("unique_user_id", qid);
      return qid;
    }

    // gate 저장
    const cur = localStorage.getItem("uniqueCurrentUser");
    if (cur){
      try{
        const obj = JSON.parse(cur);
        if (obj && obj.id){
          localStorage.setItem("unique_user_id", String(obj.id));
          if (obj.name) localStorage.setItem("unique_user_name", safeName(obj.name));
          if (obj.nickname) localStorage.setItem("unique_user_nick", safeName(obj.nickname));
          return String(obj.id);
        }
      }catch(_){}
    }

    const keys = [
      "unique_user_id","uniqueUserId","unique_id","the_unique_id",
      "USER_ID","user_id","uid","id","loginId",
      "unique.login.id","unique_login_id"
    ];
    for (const k of keys){
      const v = (localStorage.getItem(k) || sessionStorage.getItem(k) || "").trim();
      if (v) { localStorage.setItem("unique_user_id", v); return v; }
    }
    return "";
  }

  // ✅ 잭팟 배너: 자정까지 유지(기존 요구사항)
  function msUntilMidnightLocal(){
    const d = new Date();
    const m = new Date(d);
    m.setHours(24,0,0,0);
    return m.getTime() - d.getTime();
  }
  function setJackpotBanner(msg){
    const until = Date.now() + msUntilMidnightLocal();
    localStorage.setItem("slot_jackpot_banner", JSON.stringify({ msg, until }));
    renderJackpotBanner();
  }
  function renderJackpotBanner(){
    const raw = localStorage.getItem("slot_jackpot_banner");
    if (!raw){ UI.hideBanner(); return; }
    try{
      const obj = JSON.parse(raw);
      if (!obj || !obj.msg || !obj.until || Date.now() > obj.until){
        localStorage.removeItem("slot_jackpot_banner");
        UI.hideBanner();
        return;
      }
      UI.setBanner(obj.msg);
    }catch(_){
      localStorage.removeItem("slot_jackpot_banner");
      UI.hideBanner();
    }
  }

  const S = {
    id: "",
    name: "",
    nickname: "",
    balance: 0,
    jackpotTotal: 0,

    bet: CFG.BET.def,
    spinning: false,
    auto: false,
    sound: true,

    oddsProfile: "LOW", // 기본 LOW
  };

  function setBet(next){
    next = Math.round(next / CFG.BET.step) * CFG.BET.step;
    next = clamp(next, CFG.BET.min, CFG.BET.max);
    S.bet = next;
    UI.el.bet.textContent = String(next);
  }

  async function syncState(){
    const data = await API.getSlotState(S.id);

    const u = data.user || {};
    S.name = safeName(u.name || localStorage.getItem("unique_user_name") || "");
    S.nickname = safeName(u.nickname || localStorage.getItem("unique_user_nick") || "");
    S.balance = Number(u.balance || 0);
    S.jackpotTotal = Number(data.jackpotTotal || 0);

    const display = S.nickname || S.name || S.id;
    UI.el.playerName.textContent = display || "-";
    UI.el.dotLogin.classList.toggle("warn", !display);

    UI.animateNumber(UI.el.wallet, Number(UI.el.wallet.textContent||0), S.balance, 550);
    UI.el.jackpot.textContent = fmt(S.jackpotTotal);

    localStorage.setItem("unique_user_id", S.id);
    if (S.name) localStorage.setItem("unique_user_name", S.name);
    if (S.nickname) localStorage.setItem("unique_user_nick", S.nickname);
  }

  async function commitSpin(netDelta, lossAmount){
    const res = await API.slotCommit(S.id, netDelta, lossAmount);
    const u = res.user || {};
    const newBal = Number(u.balance || S.balance);
    const newJack = Number(res.jackpotTotal || S.jackpotTotal);

    S.balance = newBal;
    S.jackpotTotal = newJack;

    UI.animateNumber(UI.el.wallet, Number(UI.el.wallet.textContent||0), newBal, 650);
    UI.el.jackpot.textContent = fmt(newJack);
  }

  async function doSpin(){
    if (S.spinning) return;

    const bet = S.bet;
    if (!Number.isFinite(bet) || bet < CFG.BET.min) return;

    if (S.balance < bet){
      UI.setLast("잔액 부족");
      AUD.play("lose");
      return;
    }

    S.spinning = true;
    UI.el.spinBtn.disabled = true;
    UI.setLast("SPINNING...");
    AUD.play("start");

    // 배경/사운드/플래시
    const bg = GAME.makeBgSpinner(UI);
    bg.start();
    AUD.spinLoop(true);
    UI.flashCells(true);

    // ✅ 이번달 잭팟 “없음” 기본: jackpot outcome 자체를 막는다
    let outcome = GAME.pickOutcome(S.oddsProfile);
    if (!CFG.JACKPOT.enabled) {
      if (outcome === "jackpot") outcome = "win4";
    }

    const built = GAME.buildFinalGrid(outcome);
    const finalKeys = built.keys;

    // 후반부 배경 천천히(연출)
    setTimeout(() => bg.slow(), Math.max(0, CFG.SPIN.totalMs - (CFG.SPIN.stopCascadeMs * 5) - 800));

    // ✅ 10초 + 컬럼 하나씩 멈춤 애니메이션
    await GAME.animateSpin(UI, finalKeys);

    // 정지
    AUD.spinLoop(false);
    AUD.play("stop");
    bg.stop();
    UI.flashCells(false);

    // 결과 계산(가운데 줄 연속)
    const { bestKey, bestCount } = GAME.evaluate(finalKeys);
    const sym = CFG.SYMBOLS.find(x=>x.key===bestKey) || CFG.SYMBOLS[0];

    let kind = "lose";
    let win = 0;

    if (bestCount >= 5){
      kind = "jackpot";
      win = bet * sym.pay[5];
    } else if (bestCount === 4){
      kind = "win";
      win = bet * sym.pay[4];
    } else if (bestCount === 3){
      kind = "win";
      win = bet * sym.pay[3];
    } else if (bestCount === 2){
      kind = "even";
      win = bet; // EVEN = ±0
    } else {
      kind = "lose";
      win = 0;
    }

    win = round2(win);
    const netDelta = round2(win - bet);
    const lossAmount = (netDelta < 0) ? Math.abs(netDelta) : 0;

    // UI 먼저 튀게
    const before = S.balance;
    const after = round2(S.balance + netDelta);
    UI.animateNumber(UI.el.wallet, before, after, 720);

    if (kind === "even"){
      UI.setLast("HIT +0 UT");
      UI.toast("HIT +0 UT");
      AUD.play("win");
    } else if (kind === "win"){
      UI.setLast(`WIN +${fmt(netDelta)} UT`);
      UI.toast(`WIN +${fmt(netDelta)} UT`);
      AUD.play("win");
    } else if (kind === "jackpot"){
      UI.setLast(`JACKPOT +${fmt(netDelta)} UT`);
      UI.toast(`JACKPOT +${fmt(netDelta)} UT`);
      AUD.play("jackpot");

      const who = safeName(S.nickname || S.name || S.id || "누군가");
      setJackpotBanner(`${who}님이 잭팟이 터지셨습니다. 축하드립니다.`);
    } else {
      UI.setLast(`LOSE -${fmt(bet)} UT`);
      UI.toast(`LOSE -${fmt(bet)} UT`);
      AUD.play("lose");
    }

    // 서버 반영
    try{
      await commitSpin(netDelta, lossAmount);
    }catch(err){
      UI.setLast("SERVER ERROR: 재동기화");
      try{ await syncState(); }catch(_){}
    }

    S.spinning = false;
    UI.el.spinBtn.disabled = false;

    if (S.auto){
      setTimeout(() => doSpin(), 600);
    }
  }

  function bindEvents(){
    UI.el.payToggle.addEventListener("click", ()=> UI.el.payCard.classList.toggle("open"));

    UI.el.betDown.addEventListener("click", ()=> setBet(S.bet - CFG.BET.step));
    UI.el.betUp.addEventListener("click", ()=> setBet(S.bet + CFG.BET.step));

    UI.el.autoBtn.addEventListener("click", ()=>{
      S.auto = !S.auto;
      UI.el.autoBtn.classList.toggle("on", S.auto);
      UI.el.autoBtn.textContent = S.auto ? "AUTO ON" : "AUTO OFF";
      if (S.auto && !S.spinning) doSpin();
    });

    UI.el.soundBtn.addEventListener("click", ()=>{
      S.sound = !S.sound;
      UI.el.soundBtn.classList.toggle("on", S.sound);
      UI.el.soundBtn.textContent = S.sound ? "SOUND ON" : "SOUND OFF";
      AUD.setEnabled(S.sound);
    });

    UI.el.spinBtn.addEventListener("click", doSpin);
  }

  async function boot(){
    renderJackpotBanner();

    // 기본 배경 1장 고정(항상 보임)
    UI.bg.set(CFG.ASSET.imgBase + CFG.ASSET.bg[0]);

    UI.renderPaytable();
    UI.makeGrid();
    AUD.init();

    // odds profile 로컬저장(나중에 admin에서 이 값을 바꾸게 만들면 됨)
    const savedProfile = (localStorage.getItem("slot_odds_profile") || "").toUpperCase().trim();
    if (savedProfile && CFG.ODDS_PROFILES[savedProfile]) S.oddsProfile = savedProfile;

    setBet(CFG.BET.def);

    const id = readLoginId();
    if (!id){
      UI.el.dotLogin.classList.add("warn");
      UI.showOverlay(true);
      return;
    }
    S.id = String(id).trim().toLowerCase();

    bindEvents();

    try{
      await syncState();
      UI.showOverlay(false);
      UI.setLast("READY");
    }catch(err){
      UI.setLast("INIT ERROR: " + (err && err.message ? err.message : "init_failed"));
    }
  }

  window.SLOT.app = { boot };
})();
