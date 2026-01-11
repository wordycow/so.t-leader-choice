/* games/slot/slot.app.js */
window.SLOT = window.SLOT || {};
(function(S){
  "use strict";

  // ✅ Apps Script URL 자동 탐색 (unique.config.js에 찍히는 GOOGLE_SCRIPT_URL 우선)
  function getApiBase_(){
    return (
      (window.U && U.CONFIG && (U.CONFIG.GOOGLE_SCRIPT_URL || U.CONFIG.SLOT_API_BASE)) ||
      window.GOOGLE_SCRIPT_URL ||
      window.SLOT_API_BASE ||
      ""
    );
  }

  // ✅ JSONP (Apps Script doGet이 callback 지원하니까 이걸로 가야 안 꼬임)
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

      window[cb] = (data)=>{
        cleanup();
        resolve(data);
      };

      script.onerror = ()=>{
        cleanup();
        reject(new Error("jsonp failed"));
      };

      script.src = url.toString();
      document.head.appendChild(script);

      // 타임아웃
      setTimeout(()=>{
        if(window[cb]){
          cleanup();
          reject(new Error("jsonp timeout"));
        }
      }, 12000);
    });
  }

  // --- UI safe setters (없어도 안 터지게) ---
  S.ui = S.ui || {};
  const ui = S.ui;

  function qsAny_(sels){
    for(const s of sels){
      const el = document.querySelector(s);
      if(el) return el;
    }
    return null;
  }

  const elPlayer = ()=> qsAny_([
    "#playerName", "[data-player-name]", ".player-name", ".js-player", ".player .value"
  ]);
  const elWallet = ()=> qsAny_([
    "#walletUt", "[data-wallet-ut]", ".wallet-ut", ".js-wallet", ".wallet .value"
  ]);
  const elJackpot= ()=> qsAny_([
    "#jackpotUt", "[data-jackpot-ut]", ".jackpot-ut", ".js-jackpot", ".jackpot .value"
  ]);
  const elResult = ()=> qsAny_([
    "#lastResult", "[data-last-result]", ".last-result", ".js-last-result"
  ]);
  const elBet    = ()=> qsAny_([
    "#betValue", "[data-bet]", ".bet-value", ".js-bet"
  ]);
  const btnSpin  = ()=> qsAny_([
    "#spinBtn", "[data-spin]", ".btn-spin", "button.spin", "button#spin"
  ]);
  const btnMinus = ()=> qsAny_([
    "#betMinus", "[data-bet-minus]", ".bet-minus", "button.minus"
  ]);
  const btnPlus  = ()=> qsAny_([
    "#betPlus", "[data-bet-plus]", ".bet-plus", "button.plus"
  ]);

  ui.setPlayer = ui.setPlayer || function(name){
    const el = elPlayer();
    if(el) el.textContent = name || "-";
  };
  ui.setWallet = ui.setWallet || function(ut){
    const el = elWallet();
    if(el) el.textContent = String(Math.floor(Number(ut||0)));
  };
  ui.setJackpot = ui.setJackpot || function(j){
    const el = elJackpot();
    if(el) el.textContent = String(Math.floor(Number(j||0)));
  };
  ui.setResult = ui.setResult || function(t){
    const el = elResult();
    if(el) el.textContent = t || "READY";
  };
  ui.setBet = ui.setBet || function(v){
    const el = elBet();
    if(el) el.textContent = String(Math.floor(Number(v||0)));
  };

  // --- state ---
  const state = {
    apiBase: "",
    cfg: null,
    user: null,     // {id,name,nickname,balance}
    bet: 10,
    betMin: 10,
    betMax: 1000,
    betStep: 5,     // ✅ 무조건 5단위
    inited: false,
  };

  function readIdentity_(){
    const sp = new URLSearchParams(location.search);

    // id 우선
    const id =
      sp.get("id") ||
      localStorage.getItem("unique_id") ||
      localStorage.getItem("uniqueUserId") ||
      localStorage.getItem("user_id") ||
      "";

    // nickname(로그인에 쓰는 값)
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
    // 5단위 스냅
    const step = state.betStep;
    v = Math.round(v / step) * step;
    if(v < state.betMin) v = state.betMin;
    if(v > state.betMax) v = state.betMax;
    return v;
  }

  function animateNumber_(from, to, ms, onTick, onDone){
    const t0 = performance.now();
    const dur = Math.max(180, ms|0);
    function raf(t){
      const p = Math.min(1, (t - t0) / dur);
      const v = Math.round(from + (to - from) * (p*p*(3-2*p))); // smoothstep
      onTick(v);
      if(p < 1) requestAnimationFrame(raf);
      else onDone && onDone();
    }
    requestAnimationFrame(raf);
  }

  async function loadConfig_(){
    const res = await jsonp_(state.apiBase, { action:"getConfig" });
    if(res && res.ok && res.config){
      state.cfg = res.config;

      // bet min/max만 반영(단위는 5 고정)
      const mn = Number(res.config.SLOT_BET_MIN);
      const mx = Number(res.config.SLOT_BET_MAX);
      state.betMin = Number.isFinite(mn) ? mn : 10;
      state.betMax = Number.isFinite(mx) ? mx : 1000;
      state.bet = clampBet_(state.bet);

      // 가중치 적용
      if (S.game && typeof S.game.setConfig === "function"){
        S.game.setConfig(res.config);
      }
    }
  }

  async function loadUser_(){
    const ident = readIdentity_();

    // 1) id가 있으면 getSlotState
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

    // 2) id 없고 nickname 있으면 getUserByNick → 그 id로 getSlotState
    if(ident.nickname){
      const u = await jsonp_(state.apiBase, { action:"getUserByNick", nickname: ident.nickname });
      if(u && u.ok && u.user && u.user.id){
        // 저장(다음부터 안정)
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
      // nickname은 있는데 못 찾으면 그래도 표시만
      ui.setPlayer(ident.nickname);
    }

    // 3) 아무것도 없으면 최소 표시
    ui.setPlayer("-");
    ui.setWallet(0);
    ui.setJackpot(0);
  }

  async function commitSpin_(result){
    if(!state.user || !state.user.id) return null;

    // Apps Script slotCommit 사용 (풀/총합 갱신)
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
      } else {
        // fallback: 프론트 계산
        state.user.balance = Math.max(0, Math.floor((state.user.balance||0) + result.netDelta));
        ui.setWallet(state.user.balance);
      }
      if(typeof res.jackpotTotal !== "undefined") ui.setJackpot(res.jackpotTotal);
    }

    return res;
  }

  function bindUI_(){
    // bet 표시 초기화
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

        const cur = Math.floor(Number(state.user.balance||0));
        if(cur < state.bet){
          ui.setResult("NO UT");
          return;
        }

        spin.disabled = true;
        ui.setResult("SPIN...");

        try{
          const before = cur;

          const result = await S.game.spin({ bet: state.bet });

          // 결과 텍스트: EVEN 표시
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

          // 프론트에서 먼저 애니메이션(체감)
          const afterPred = Math.max(0, before + result.netDelta);
          animateNumber_(before, afterPred, result.jackpot ? 1600 : 600, (v)=>ui.setWallet(v));

          // 서버 커밋(진짜 잔액/풀 확정)
          await commitSpin_(result);

        }catch(err){
          ui.setResult("ERROR");
          console.error(err);
        }finally{
          spin.disabled = false;
        }
      });
    }
  }

  function boot_(){
    if(state.inited) return;
    state.apiBase = getApiBase_();
    if(!state.apiBase){
      console.error("[SLOT] missing GOOGLE_SCRIPT_URL / SLOT_API_BASE");
      ui.setResult("NO API");
      return;
    }

    // ✅ bg png 리스트 강제(혹시 다른 코드가 덮어써도)
    S.BG_LIST = [
      "img/slot/bg1.png",
      "img/slot/bg2.png",
      "img/slot/bg3.png",
      "img/slot/bg4.png",
      "img/slot/bg5.png"
    ];

    state.inited = true;

    // game 준비
    if(S.game && typeof S.game.buildReels === "function"){
      S.game.buildReels();
    }

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

  // slot.game이 먼저 로드된 뒤 실행되도록 약간 기다림
  function wait_(){
    if(S.game && typeof S.game.spin === "function"){
      boot_();
    }else{
      setTimeout(wait_, 50);
    }
  }

  document.addEventListener("DOMContentLoaded", wait_);

})(window.SLOT);
