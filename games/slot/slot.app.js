// games/slot/slot.app.js
(() => {
  const $ = (id) => document.getElementById(id);

  function setText(id, v){
    const el = $(id);
    if (el) el.textContent = String(v ?? "");
  }

  function setNote(msg){
    const el = $("uiNote");
    if (el) el.textContent = msg || "";
  }

  function parseNum(x){
    const s = String(x ?? "").replace(/[^\d.-]/g, "");
    const n = Number(s);
    return Number.isFinite(n) ? n : 0;
  }

  function formatInt(n){
    const v = Math.floor(Number(n||0));
    return String(v);
  }

  function updateLocalStorageBalance(newBal){
    try{
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return;
      const u = JSON.parse(raw);
      u.balance = Number(newBal || 0);
      localStorage.setItem("uniqueCurrentUser", JSON.stringify(u));
      localStorage.setItem("myUtPoints", String(Number(newBal || 0)));
    }catch(e){}
  }

  // ✅ favicon.ico 404 같은 찌꺼기 제거(데이터URI로 박아버림)
  function ensureFavicon(){
    try{
      let link = document.querySelector('link[rel="icon"]');
      if (!link){
        link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
      }
      // 간단한 네온 원형 svg
      link.href =
        'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="64" height="64"%3E%3Cdefs%3E%3CradialGradient id="g"%3E%3Cstop offset="0" stop-color="%23ff4bd8"/%3E%3Cstop offset="1" stop-color="%2300f0ff"/%3E%3C/radialGradient%3E%3C/defs%3E%3Ccircle cx="32" cy="32" r="22" fill="url(%23g)"/%3E%3C/svg%3E';
    }catch(e){}
  }

  // ✅ PLAYER: "id" 윗줄 / "이름" 아랫줄. "/" 삭제.
  function setPlayer(id, name){
    const el = $("uiPlayer");
    if (!el) return;
    el.style.whiteSpace = "pre-line";
    el.textContent = `${String(id||"").trim()}\n${String(name||"-").trim()}`;
  }

  // ✅ BET: 5단위 증감 + 버튼 자동 삽입
  const BET_MIN = 10;
  const BET_MAX = 1000;
  const BET_STEP = 5;

  function getBet(){
    const n = parseNum(localStorage.getItem("slotBet"));
    return Math.min(BET_MAX, Math.max(BET_MIN, n || 10));
  }
  function setBet(v){
    const next = Math.min(BET_MAX, Math.max(BET_MIN, Math.round(Number(v||0) / BET_STEP) * BET_STEP));
    localStorage.setItem("slotBet", String(next));
    if ($("uiBet")) setText("uiBet", next);
    return next;
  }
  function incBet(){ return setBet(getBet() + BET_STEP); }
  function decBet(){ return setBet(getBet() - BET_STEP); }

  function ensureBetButtons(){
    // bet 숫자 엘리먼트 찾기
    const betEl = $("uiBet") || document.querySelector("[data-ui-bet]");
    if (!betEl) return;

    // 이미 있으면 패스
    if ($("btnBetMinus") || $("btnBetPlus")) return;

    // betEl 주변에 버튼 넣기
    const wrap = betEl.closest(".card, .panel, .bet, .box") || betEl.parentElement;
    if (!wrap) return;

    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.gap = "8px";
    row.style.marginTop = "8px";

    const mkBtn = (id, label) => {
      const b = document.createElement("button");
      b.id = id;
      b.type = "button";
      b.textContent = label;
      b.style.flex = "1";
      b.style.padding = "8px 10px";
      b.style.borderRadius = "12px";
      b.style.border = "1px solid rgba(255,255,255,0.14)";
      b.style.background = "rgba(0,0,0,0.18)";
      b.style.color = "rgba(255,255,255,0.9)";
      b.style.cursor = "pointer";
      b.style.backdropFilter = "blur(8px)";
      return b;
    };

    const minus = mkBtn("btnBetMinus", "−5");
    const plus  = mkBtn("btnBetPlus",  "+5");

    minus.addEventListener("click", () => decBet());
    plus.addEventListener("click",  () => incBet());

    row.appendChild(minus);
    row.appendChild(plus);
    wrap.appendChild(row);

    // 초기 표시
    setBet(getBet());
  }

  // ✅ 잭팟 티커(자정까지 유지) 뼈대: 나중에 잭팟 터질 때 이 함수만 호출하면 됨
  function seoulDayKey(){
    try{
      return new Intl.DateTimeFormat("sv-SE", { timeZone:"Asia/Seoul", year:"numeric", month:"2-digit", day:"2-digit" })
        .format(new Date()); // YYYY-MM-DD
    }catch(e){
      const d = new Date();
      const y = d.getFullYear();
      const m = String(d.getMonth()+1).padStart(2,"0");
      const dd= String(d.getDate()).padStart(2,"0");
      return `${y}-${m}-${dd}`;
    }
  }

  function ensureTickerHost(){
    if ($("jackpotTickerHost")) return $("jackpotTickerHost");

    const host = document.createElement("div");
    host.id = "jackpotTickerHost";
    host.style.position = "absolute";
    host.style.left = "16px";
    host.style.right = "16px";
    host.style.top = "10px";
    host.style.height = "28px";
    host.style.overflow = "hidden";
    host.style.pointerEvents = "none";
    host.style.zIndex = "50";

    const keyframes = document.createElement("style");
    keyframes.textContent = `
      @keyframes slotTickerMove {
        0%   { transform: translateX(100%); }
        100% { transform: translateX(-120%); }
      }
    `;
    document.head.appendChild(keyframes);

    // 페이지의 큰 컨테이너로 추정되는 곳에 붙임
    const container =
      document.querySelector(".page-wrap") ||
      document.querySelector(".app") ||
      document.querySelector(".container") ||
      document.body;

    // 컨테이너가 position:static이면 티커 absolute가 먹게 relative로 올림
    const cs = getComputedStyle(container);
    if (cs.position === "static") container.style.position = "relative";

    container.appendChild(host);
    return host;
  }

  function showTicker(message){
    const host = ensureTickerHost();
    host.innerHTML = "";

    const line = document.createElement("div");
    line.style.whiteSpace = "nowrap";
    line.style.display = "inline-block";
    line.style.padding = "4px 10px";
    line.style.borderRadius = "999px";
    line.style.background = "rgba(0,0,0,0.35)";
    line.style.border = "1px solid rgba(255,255,255,0.14)";
    line.style.color = "rgba(255,255,255,0.95)";
    line.style.backdropFilter = "blur(10px)";
    line.style.animation = "slotTickerMove 14s linear infinite";
    line.textContent = message;

    host.appendChild(line);
  }

  // ✅ 외부에서 호출: window.SLOT_JACKPOT_TICKER("이유송")
  window.SLOT_JACKPOT_TICKER = function(name){
    const nm = String(name||"").trim() || "누군가";
    const msg = `${nm}님이 잭팟이 터지셨습니다. 축하드립니다.`;
    const payload = { day: seoulDayKey(), msg };
    localStorage.setItem("slotJackpotTicker", JSON.stringify(payload));
    showTicker(msg);
  };

  function restoreTickerIfAny(){
    try{
      const raw = localStorage.getItem("slotJackpotTicker");
      if (!raw) return;
      const p = JSON.parse(raw);
      if (!p || p.day !== seoulDayKey() || !p.msg) return;
      showTicker(p.msg);
    }catch(e){}
  }

  async function boot(){
    ensureFavicon();
    restoreTickerIfAny();

    // 세션 체크
    const u = window.SLOT_API?.getLocalUser?.();
    if (!u){
      location.href = "../the-unique-gate.html";
      return;
    }

    // 기본 표시(즉시)
    setPlayer(u.id, u.name || "-");
    setText("uiWallet", formatInt(u.balance||0));
    setText("uiJackpot", "…");
    setText("uiResult", "READY");
    setNote("");

    // bet 표시 + 버튼 주입
    ensureBetButtons();

    // 시트에서 최신값 로드
    try{
      const r = await window.SLOT_API.getSlotState();
      if (!r || !r.ok || !r.user){
        setNote("시트에서 유저 정보를 불러오지 못했습니다.");
        return;
      }

      setPlayer(r.user.id, r.user.name || "-");
      setText("uiWallet", formatInt(r.user.balance||0));
      setText("uiJackpot", formatInt(r.jackpotTotal || 0));

      // (선택) casinoTotal 표시할 자리 있으면 넣고, 없으면 무시
      if ($("uiCasino")) setText("uiCasino", formatInt(r.casinoTotal || 0));

      updateLocalStorageBalance(Number(r.user.balance||0));

    }catch(e){
      setNote("네트워크 오류로 유저 정보를 불러오지 못했습니다.");
    }
  }

  // ✅ 게임(스핀) 끝난 직후 “딱 여기만” 호출하면 된다.
  // netDelta: 승리면 +, 패배면 - (최종)
  // lossAmount: 최종 손실(양수). 이기면 0
  window.SLOT_COMMIT_RESULT = async function({ netDelta = 0, lossAmount = 0, resultText = "" } = {}){
    try{
      const r = await window.SLOT_API.commitSlotSpin({ netDelta, lossAmount });
      if (!r || !r.ok || !r.user){
        setNote("시트 반영 실패. (잠시 후 다시)");
        return;
      }

      setText("uiWallet", formatInt(r.user.balance||0));
      setText("uiJackpot", formatInt(r.jackpotTotal||0));
      if (resultText) setText("uiResult", resultText);

      updateLocalStorageBalance(Number(r.user.balance||0));
    }catch(e){
      setNote("시트 반영 중 네트워크 오류.");
    }
  };

  // 외부에서 강제 새로고침용
  window.SLOT_REFRESH = boot;

  // bet 외부 접근용
  window.SLOT_BET = { get:getBet, set:setBet, inc:incBet, dec:decBet };

  document.addEventListener("DOMContentLoaded", boot);
})();
