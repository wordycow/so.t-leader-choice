/* games/slot/slot.app.js */
window.SLOT = window.SLOT || {};
(function(S){
  "use strict";

  // -------------------------
  // API BASE (Apps Script)
  // -------------------------
  function getApiBase_(){
    return (
      (window.U && U.CONFIG && (U.CONFIG.GOOGLE_SCRIPT_URL || U.CONFIG.SLOT_API_BASE)) ||
      window.GOOGLE_SCRIPT_URL ||
      window.SLOT_API_BASE ||
      ""
    );
  }

  function jsonp_(base, params){
    return new Promise((resolve, reject)=>{
      if(!base) return reject(new Error("missing api base"));
      const cb = "__slotcb_" + Math.random().toString(36).slice(2);
      const url = new URL(base);
      Object.entries(params||{}).forEach(([k,v])=> url.searchParams.set(k, String(v)));
      url.searchParams.set("callback", cb);

      const script = document.createElement("script");
      const cleanup = ()=>{
        try{ delete window[cb]; }catch(_){}
        if(script && script.parentNode) script.parentNode.removeChild(script);
      };

      window[cb] = (data)=>{ cleanup(); resolve(data); };
      script.onerror = ()=>{ cleanup(); reject(new Error("jsonp failed")); };

      script.src = url.toString();
      document.head.appendChild(script);

      setTimeout(()=>{
        if(window[cb]){
          cleanup();
          reject(new Error("jsonp timeout"));
        }
      }, 12000);
    });
  }

  // -------------------------
  // UI: 무조건 함수 주입 (에러 방지)
  // -------------------------
  S.ui = (S.ui && typeof S.ui === "object") ? S.ui : {};
  const ui = S.ui;

  function qsAny_(sels){
    for(const s of sels){
      const el = document.querySelector(s);
      if(el) return el;
    }
    return null;
  }

  const elPlayer = ()=> qsAny_(["#playerName","[data-player-name]",".player-name",".js-player",".player .value"]);
  const elWallet = ()=> qsAny_(["#walletUt","[data-wallet-ut]",".wallet-ut",".js-wallet",".wallet .value"]);
  const elJackpot= ()=> qsAny_(["#jackpotUt","[data-jackpot-ut]",".jackpot-ut",".js-jackpot",".jackpot .value"]);
  const elResult = ()=> qsAny_(["#lastResult","[data-last-result]",".last-result",".js-last-result"]);
  const elBet    = ()=> qsAny_(["#betValue","[data-bet]",".bet-value",".js-bet"]);
  const btnSpin  = ()=> qsAny_(["#spinBtn","[data-spin]",".btn-spin","button.spin","button#spin"]);
  const btnMinus = ()=> qsAny_(["#betMinus","[data-bet-minus]",".bet-minus","button.minus",".bet-step-minus"]);
  const btnPlus  = ()=> qsAny_(["#betPlus","[data-bet-plus]",".bet-plus","button.plus",".bet-step-plus"]);

  ui.setPlayer = function(name){ const el = elPlayer(); if(el) el.textContent = name || "-"; };
  ui.setWallet = function(ut){ const el = elWallet(); if(el) el.textContent = String(Math.floor(Number(ut||0))); };
  ui.setJackpot= function(v){ const el = elJackpot(); if(el) el.textContent = String(Math.floor(Number(v||0))); };
  ui.setResult = function(t){ const el = elResult(); if(el) el.textContent = t || "READY"; };
  ui.setBet    = function(v){ const el = elBet(); if(el) el.textContent = String(Math.floor(Number(v||0))); };

  // -------------------------
  // Mobile stack 재배치(가능하면)
  // paytable -> reels -> panel(내자산/버튼)
  // -------------------------
  function applyMobileStack_(){
    const w = window.innerWidth || 9999;
    if (w > 780) return;

    const pay = qsAny_(["#payTable","[data-paytable]",".paytable",".pay-table"]);
    const reels = qsAny_(["#reels","[data-slot-reels]",".slot-reels",".reels"]);
    const panel = qsAny_(["#leftPanel",".left-panel",".slot-panel","[data-panel]"]);

    if(!pay || !reels || !panel) return;

    const wrap = document.getElementById("slotMobileStack") || document.createElement("div");
    wrap.id = "slotMobileStack";
    wrap.style.display = "flex";
    wrap.style.flexDirection = "column";
    wrap.style.gap = "14px";
    wrap.style.width = "100%";

    // 공통 부모를 최대한 안전하게
    const host = panel.parentElement || document.body;
    if(!wrap.parentNode) host.insertBefore(wrap, host.firstChild);

    // 원하는 순서로 꽂기
    if (pay.parentNode !== wrap) wrap.appendChild(pay);
    if (reels.parentNode !== wrap) wrap.appendChild(reels);
    if (panel.parentNode !== wrap) wrap.appendChild(panel);

    // 스크롤 자연스럽게
    document.documentElement.style.height = "auto";
    document.body.style.height = "auto";
    document.body.style.overflow = "auto";
  }

  // -------------------------
  // 잭팟 티커 (자정까지 유지)
  // -------------------------
  function ensureTicker_(){
    let bar = document.getElementById("jackpotTicker");
    if(bar) return bar;

    bar = document.createElement("div");
    bar.id = "jackpotTicker";
    bar.style.position = "fixed";
    bar.style.left = "0";
    bar.style.right = "0";
    bar.style.top = "0";
    bar.style.zIndex = "9999";
    bar.style.padding = "10px 0";
    bar.style.background = "rgba(0,0,0,0.55)";
    bar.style.backdropFilter = "blur(8px)";
    bar.style.color = "#fff";
    bar.style.fontWeight = "800";
    bar.style.letterSpacing = "0.2px";
    bar.style.display = "none";
    bar.style.overflow = "hidden";

    const inner = document.createElement("div");
    inner.id = "jackpotTickerInner";
    inner.style.whiteSpace = "nowrap";
    inner.style.display = "inline-block";
    inner.style.paddingLeft = "100%";
    inner.style.animation = "slotTicker 10s linear infinite";

    const style = document.createElement("style");
    style.textContent = `
      @keyframes slotTicker {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
      }
    `;
    document.head.appendChild(style);

    bar.appendChild(inner);
    document.body.appendChild(bar);
    return bar;
  }

  function setTickerUntilMidnight_(text){
    const now = new Date();
    const midnight = new Date(now);
    midnight.setHours(24,0,0,0);

    localStorage.setItem("slot_jackpot_ticker_text", text);
    localStorage.setItem("slot_jackpot_ticker_exp", String(midnight.getTime()));

    showTickerIfValid_();
  }

  function showTickerIfValid_(){
    const text = localStorage.getItem("slot_jackpot_ticker_text") || "";
    const exp = Number(localStorage.getItem("slot_jackpot_ticker_exp") || 0);
    const now = Date.now();

    const bar = ensureTicker_();
    const inner = document.getElementById("jackpotTickerInner");

    if(text && exp && now < exp){
      if(inner) inner.textContent = text;
      bar.style.display = "block";
      // 상단 바 때문에 내용이 가려지지 않게
      document.body.style.paddingTop = "52px";
    }else{
      bar.style.display = "none";
      document.body.style.paddingTop = "";
      localStorage.removeItem("slot_jackpot_ticker_text");
      localStorage.removeItem("slot_jackpot_ticker_exp");
    }
  }

  // -------------------------
  // state
  // -------------------------
  const state = {
    apiBase: "",
    cfg: null,
    user: null, // {id,name,nickname,balance}
    bet: 10,
    betMin: 10,
    betMax: 1000,
    betStep: 5, // ✅ 무조건 5단위
    inited: false,
  };

  function readIdentity_(){
    const sp = new URLSearchParams(location.search);
    const id =
      sp.get("id") ||
      localStorage.getItem("unique_id") ||
      localStorage.getItem("uniqueUserId") ||
      localStorage.getItem("user_id") ||
      "";
    const nickname =
      sp.get("nick") ||
      sp.get("nickname") ||
      localStorage.getItem("unique_nick") ||
      localStorage.getItem("uniqueNickname") ||
      localStorage.getItem("nickname") ||
      "";
    return { id: String(id||"").trim().toLowerCase(), nickname: String(nickname||"").trim() };
  }

  function clampBet_(v){
    v = Math.floor(Number(v||0));
    if(!Number.isFinite(v)) v = state.betMin;
    if(v < state.betMin) v = state.betMin;
    if(v > state.betMax) v = state.betMax;
    const step = state.betStep;
    v = Math.round(v / step) * step;
    if(v < state.betMin) v = state.betMin;
    if(v > state.betMax) v = state.betMax;
    return v;
  }

  function animateNumber_(from, to, ms, onTick){
    const t0 = performance.now();
    const dur = Math.max(180, ms|0);
    function raf(t){
      const p = Math.min(1, (t - t0) / dur);
      const v = Math.round(from + (to - from) * (p*p*(3-2*p)));
      onTick(v);
      if(p < 1) requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  }

  async function loadConfig_(){
    const res = await jsonp_(state.apiBase, { action:"getConfig" });
    if(res && res.ok && res.config){
      state.cfg = res.config;

      const mn = Number(res.config.SLOT_BET_MIN);
      const mx = Number(res.config.SLOT_BET_MAX);
      state.betMin = Number.isFinite(mn) ? mn : 10;
      state.betMax = Number.isFinite(mx) ? mx : 1000;
      state.bet = clampBet_(state.bet);

      if (S.game && typeof S.game.setConfig === "function"){
        S.game.setConfig(res.config);
      }
    }
  }

  async function loadUser_(){
    const ident = readIdentity_();

    if(ident.id){
      const r = await jsonp_(state.apiBase, { action:"getSlotState", id: ident.id });
      if(r && r.ok && r.user){
        state.user = r.user;
        ui.setPlayer(state.user.nickname || state.user.name || "-");
        ui.setWallet(state.user.balance || 0);
        ui.setJackpot(r.jackpotTotal || 0);
        return;
      }
    }

    if(ident.nickname){
      const u = await jsonp_(state.apiBase, { action:"getUserByNick", nickname: ident.nickname });
      if(u && u.ok && u.user && u.user.id){
        localStorage.setItem("unique_id", u.user.id);
        localStorage.setItem("unique_nick", u.user.nickname || ident.nickname);

        const r2 = await jsonp_(state.apiBase, { action:"getSlotState", id: u.user.id });
        if(r2 && r2.ok && r2.user){
          state.user = r2.user;
          ui.setPlayer(state.user.nickname || state.user.name || ident.nickname);
          ui.setWallet(state.user.balance || 0);
          ui.setJackpot(r2.jackpotTotal || 0);
          return;
        }
      }
      ui.setPlayer(ident.nickname);
    }

    ui.setPlayer("-");
    ui.setWallet(0);
    ui.setJackpot(0);
  }

  async function commitSpin_(result){
    if(!state.user || !state.user.id) return null;

    const res = await jsonp_(state.apiBase, {
      action:"slotCommit",
      id: state.user.id,
      netDelta: result.netDelta,
      lossAmount: result.lossAmount
    });

    if(res && res.ok){
      if(res.user && typeof res.user.balance !== "undefined"){
        state.user.balance = Number(res.user.balance||0);
        ui.setWallet(state.user.balance);
      }
      if(typeof res.jackpotTotal !== "undefined") ui.setJackpot(res.jackpotTotal);
    }
    return res;
  }

  function bindUI_(){
    ui.setBet(state.bet);

    const minus = btnMinus();
    const plus  = btnPlus();
    const spin  = btnSpin();

    if(minus){
      minus.addEventListener("click", ()=>{
        state.bet = clampBet_(state.bet - state.betStep);
        ui.setBet(state.bet);
      });
    }
    if(plus){
      plus.addEventListener("click", ()=>{
        state.bet = clampBet_(state.bet + state.betStep);
        ui.setBet(state.bet);
      });
    }

    if(spin){
      spin.addEventListener("click", async ()=>{
        if(!S.game || typeof S.game.spin !== "function") return;

        if(!state.user){
          ui.setResult("NO USER");
          return;
        }

        const before = Math.floor(Number(state.user.balance||0));
        if(before < state.bet){
          ui.setResult("NO UT");
          return;
        }

        spin.disabled = true;
        ui.setResult("SPIN...");

        try{
          const result = await S.game.spin({ bet: state.bet });

          // 결과 텍스트 (EVEN 표시)
          let label = "LOSE";
          if(result.jackpot){
            label = `JACKPOT +${Math.max(0,result.netDelta)} UT`;
          }else if(result.netDelta > 0){
            label = `WIN +${result.netDelta} UT`;
          }else if(result.netDelta === 0 && result.hadHit){
            label = `EVEN (0 UT)`;
          }else{
            label = "LOSE";
          }
          ui.setResult(label);

          // 돈 올라가는 느낌 (빠르게)
          const afterPred = Math.max(0, before + result.netDelta);
          animateNumber_(before, afterPred, result.jackpot ? 1600 : 650, (v)=>ui.setWallet(v));

          // 잭팟이면 티커 자정까지
          if(result.jackpot){
            const name = state.user.nickname || state.user.name || "누군가";
            setTickerUntilMidnight_(`${name}님이 잭팟이 터지셨습니다. 축하드립니다.`);
          }

          await commitSpin_(result);

        }catch(err){
          console.error(err);
          ui.setResult("ERROR");
        }finally{
          spin.disabled = false;
        }
      });
    }
  }

  function boot_(){
    if(state.inited) return;
    state.inited = true;

    // bg 목록 강제 (png)
    S.BG_LIST = [
      "img/slot/bg1.png",
      "img/slot/bg2.png",
      "img/slot/bg3.png",
      "img/slot/bg4.png",
      "img/slot/bg5.png"
    ];

    showTickerIfValid_();
    applyMobileStack_();

    state.apiBase = getApiBase_();
    if(!state.apiBase){
      ui.setResult("NO API");
      // 그래도 UI는 깨지면 안 됨
      if(S.game && typeof S.game.buildReels === "function") S.game.buildReels();
      bindUI_();
      return;
    }

    if(S.game && typeof S.game.buildReels === "function") S.game.buildReels();

    Promise.resolve()
      .then(loadConfig_)
      .then(loadUser_)
      .then(bindUI_)
      .then(()=> ui.setResult("READY"))
      .catch(err=>{
        console.error(err);
        ui.setResult("ERROR");
      });
  }

  function wait_(){
    if(S.game && typeof S.game.spin === "function"){
      boot_();
    }else{
      setTimeout(wait_, 50);
    }
  }

  window.addEventListener("resize", ()=>{ try{ applyMobileStack_(); }catch(_){} });
  document.addEventListener("DOMContentLoaded", wait_);

})(window.SLOT);
