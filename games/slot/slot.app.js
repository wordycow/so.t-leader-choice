// games/slot/slot.app.js
(() => {
  const $ = (id) => document.getElementById(id);

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, m => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[m]));

  function setText(id, v){
    const el = $(id);
    if (el) el.textContent = String(v ?? "");
  }

  function setHTML(id, html){
    const el = $(id);
    if (el) el.innerHTML = html;
  }

  function setNote(msg){
    const el = $("uiNote");
    if (el) el.textContent = msg || "";
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

  function setPlayerBox(id, name){
    // ✅ “id / name” 제거 → 2줄
    setHTML("uiPlayer", `
      <div style="font-weight:800; letter-spacing:0.2px;">${esc(id)}</div>
      <div style="opacity:0.9; margin-top:2px;">${esc(name || "")}</div>
    `);
  }

  // ✅ 베팅 로컬 상태
  const BET_KEY = "slotBetUt";
  function getBet(cfg){
    const saved = Number(localStorage.getItem(BET_KEY));
    const def = Math.floor(Number(cfg?.SLOT_BET_UT) || 10);
    const min = Math.floor(Number(cfg?.SLOT_BET_MIN) || 10);
    const max = Math.floor(Number(cfg?.SLOT_BET_MAX) || 1000);
    let bet = Number.isFinite(saved) ? saved : def;
    bet = Math.max(min, Math.min(max, bet));
    return bet;
  }
  function setBet(bet, cfg){
    const min = Math.floor(Number(cfg?.SLOT_BET_MIN) || 10);
    const max = Math.floor(Number(cfg?.SLOT_BET_MAX) || 1000);
    bet = Math.max(min, Math.min(max, Math.floor(bet)));
    localStorage.setItem(BET_KEY, String(bet));
    setText("uiBet", bet);
    return bet;
  }

  function ensureBetButtons(cfg){
    if ($("betMinus") || $("betPlus")) return;

    const betEl = $("uiBet");
    if (!betEl) return;

    const host =
      betEl.closest("[data-bet-host]") ||
      betEl.parentElement;

    if (!host) return;

    const step = 5; // ✅ 유송 요청: 5단위
    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.gap = "10px";
    row.style.marginTop = "10px";
    row.style.alignItems = "center";

    row.innerHTML = `
      <button id="betMinus" type="button"
        style="flex:1; padding:10px 12px; border-radius:14px;
               border:1px solid rgba(255,255,255,0.14);
               background:rgba(0,0,0,0.20); color:#e7ecff; font-weight:800;">
        -${step}
      </button>
      <button id="betPlus" type="button"
        style="flex:1; padding:10px 12px; border-radius:14px;
               border:1px solid rgba(255,255,255,0.14);
               background:rgba(0,0,0,0.20); color:#e7ecff; font-weight:800;">
        +${step}
      </button>
    `;

    host.appendChild(row);

    $("betMinus").addEventListener("click", () => {
      const cur = Number($("uiBet")?.textContent || 0);
      setBet(cur - step, cfg);
    });
    $("betPlus").addEventListener("click", () => {
      const cur = Number($("uiBet")?.textContent || 0);
      setBet(cur + step, cfg);
    });
  }

  function findButtonByText(txt){
    const buttons = Array.from(document.querySelectorAll("button"));
    const t = String(txt).toLowerCase();
    return buttons.find(b => String(b.textContent||"").trim().toLowerCase() === t)
        || buttons.find(b => String(b.textContent||"").toLowerCase().includes(t))
        || null;
  }

  // ✅ 자정까지 티커 유지(로컬 저장)
  const TICKER_KEY = "slotJackpotTickerV1";
  function nextMidnightMs(){
    const d = new Date();
    d.setHours(24,0,0,0); // 로컬이 서울이면 그대로 “자정”
    return d.getTime();
  }
  function setJackpotTicker(name){
    const text = `${name}님이 잭팟이 터지셨습니다. 축하드립니다.`;
    localStorage.setItem(TICKER_KEY, JSON.stringify({
      text,
      expiresAt: nextMidnightMs()
    }));
    showJackpotTicker();
  }
  function showJackpotTicker(){
    let payload = null;
    try{ payload = JSON.parse(localStorage.getItem(TICKER_KEY) || "null"); }catch(e){}
    if (!payload || !payload.text || !payload.expiresAt) return;

    if (Date.now() > Number(payload.expiresAt)){
      localStorage.removeItem(TICKER_KEY);
      return;
    }

    // 상단 타이틀 영역에 얹기 (없으면 body 상단)
    let bar = document.getElementById("jackpotTicker");
    if (!bar){
      bar = document.createElement("div");
      bar.id = "jackpotTicker";
      bar.style.position = "fixed";
      bar.style.left = "0";
      bar.style.right = "0";
      bar.style.top = "0";
      bar.style.zIndex = "9999";
      bar.style.pointerEvents = "none";
      bar.style.overflow = "hidden";
      bar.style.height = "34px";
      bar.style.background = "rgba(0,0,0,0.25)";
      bar.style.borderBottom = "1px solid rgba(255,255,255,0.10)";
      document.body.appendChild(bar);

      const inner = document.createElement("div");
      inner.id = "jackpotTickerInner";
      inner.style.whiteSpace = "nowrap";
      inner.style.display = "inline-block";
      inner.style.paddingLeft = "100%";
      inner.style.fontWeight = "900";
      inner.style.letterSpacing = "0.2px";
      inner.style.lineHeight = "34px";
      inner.style.color = "#fbbf24";
      inner.style.textShadow = "0 6px 18px rgba(0,0,0,0.6)";
      inner.style.animation = "tickerMove 12s linear infinite";
      inner.textContent = payload.text;
      bar.appendChild(inner);

      const style = document.createElement("style");
      style.textContent = `
        @keyframes tickerMove {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-120%); }
        }
        body { padding-top: 34px; } /* 티커가 덮지 않게 */
      `;
      document.head.appendChild(style);
    } else {
      const inner = document.getElementById("jackpotTickerInner");
      if (inner) inner.textContent = payload.text;
    }
  }

  async function boot(){
    // 세션 체크
    const u = window.SLOT_API?.getLocalUser?.();
    if (!u){
      location.href = "../the-unique-gate.html";
      return;
    }

    // 기본 표시(즉시)
    setPlayerBox(u.id, u.name || "-");
    setText("uiWallet", Number(u.balance||0));
    setText("uiJackpot", "…");
    setText("uiResult", "READY");
    setNote("");

    // 기본 그리드(즉시)
    window.SLOT?.game?.buildReels?.();

    // 티커 복원
    showJackpotTicker();

    // 시트에서 최신값 로드
    let cfg = null;
    try{
      const r = await window.SLOT_API.getSlotState();
      if (!r || !r.ok || !r.user){
        setNote("시트에서 유저 정보를 불러오지 못했습니다.");
        return;
      }

      cfg = r.config || null;
      window.SLOT_CONFIG = cfg;
      window.SLOT?.game?.setConfig?.(cfg);

      setPlayerBox(r.user.id, r.user.name || "-");
      setText("uiWallet", Number(r.user.balance||0));
      setText("uiJackpot", Number(r.jackpotTotal || 0));

      updateLocalStorageBalance(Number(r.user.balance||0));

      // 베팅 표시 + 버튼
      const bet = getBet(cfg);
      setText("uiBet", bet);
      ensureBetButtons(cfg);

    }catch(e){
      setNote("네트워크 오류로 유저 정보를 불러오지 못했습니다.");
      return;
    }

    // ✅ 버튼 연결
    const spinBtn = findButtonByText("SPIN");
    const autoBtn = findButtonByText("AUTO");

    let autoOn = false;
    let spinning = false;

    async function doSpin(){
      if (spinning) return;
      spinning = true;

      const bet = Number($("uiBet")?.textContent || 0);
      const walletNow = Number($("uiWallet")?.textContent || 0);
      if (walletNow < bet){
        setNote("잔액 부족");
        spinning = false;
        autoOn = false;
        return;
      }

      // ✅ “-10 UT” 같은 잔챙이 출력은 안 남김 (LOSE면 note 비움)
      setText("uiResult", "SPINNING");
      setNote("");

      // 체감용: 일단 UI에서만 선차감(서버 반영은 끝나고 commit)
      setText("uiWallet", walletNow - bet);

      const out = await window.SLOT?.game?.spin?.({ bet });
      if (!out || !out.ok){
        setNote("스핀 실패(리로드 후 재시도)");
        // 안전하게 새로고침
        try{ await window.SLOT_REFRESH?.(); }catch(e){}
        spinning = false;
        return;
      }

      // 결과 커밋(시트 반영)
      await window.SLOT_COMMIT_RESULT?.({
        netDelta: out.netDelta,
        lossAmount: out.lossAmount,
        resultText: out.resultText
      });

      // WIN/JACKPOT만 표시(LOSE는 조용히)
      if (out.jackpot){
        const name = (window.SLOT_API?.getLocalUser?.()?.name) || "";
        setJackpotTicker(name || "누군가");
        setNote("JACKPOT!");
      } else if (out.payout > 0){
        setNote(`WIN +${Math.max(0, out.netDelta)} UT`);
      } else {
        setNote("");
      }

      spinning = false;

      if (autoOn){
        setTimeout(doSpin, 450);
      }
    }

    if (spinBtn){
      spinBtn.addEventListener("click", () => {
        autoOn = false; // 수동 스핀 누르면 자동 끔
        doSpin();
      }, { passive:true });
    }

    if (autoBtn){
      autoBtn.addEventListener("click", () => {
        autoOn = !autoOn;
        if (autoOn) doSpin();
      }, { passive:true });
    }
  }

  // ✅ 스핀 끝난 직후 “딱 여기만” 호출하면 된다.
  window.SLOT_COMMIT_RESULT = async function({ netDelta = 0, lossAmount = 0, resultText = "" } = {}){
    const setTextSafe = (id, v) => { const el = $(id); if (el) el.textContent = String(v ?? ""); };

    try{
      const r = await window.SLOT_API.commitSlotSpin({ netDelta, lossAmount });
      if (!r || !r.ok || !r.user){
        setNote("시트 반영 실패. (잠시 후 다시)");
        return;
      }

      setTextSafe("uiWallet", Number(r.user.balance||0));
      setTextSafe("uiJackpot", Number(r.jackpotTotal||0));
      if (resultText) setTextSafe("uiResult", resultText);

      updateLocalStorageBalance(Number(r.user.balance||0));

    }catch(e){
      setNote("시트 반영 중 네트워크 오류.");
    }
  };

  window.SLOT_REFRESH = boot;
  document.addEventListener("DOMContentLoaded", boot);
})();
