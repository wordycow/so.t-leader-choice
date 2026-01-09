// games/slot/slot.api.js
window.SLOT = window.SLOT || {};
(function (S) {

  function getParam(name){
    return new URLSearchParams(location.search).get(name);
  }

  function clean(v){
    v = (v || "").trim();
    if(!v) return "";
    if(v === "User" || v === "회원 이름") return "";
    return v;
  }

  // ✅ prompt 없음. 있으면 쓰고 없으면 Guest.
  // ✅ 중요: uid는 "MAIN에서 전달된 값"을 써야 함. 여기서 임의 생성 금지.
  function getPlayerContext(){
    const u   = clean(getParam("u"))   || clean(localStorage.getItem("slot_player")) || "Guest";
    const uid = clean(getParam("uid")) || clean(localStorage.getItem("unique_userid")) || clean(localStorage.getItem("uid")) || "";
    const ut  = clean(getParam("ut"))  || clean(localStorage.getItem("unique_ut")) || "";

    localStorage.setItem("slot_player", u);
    if(uid) localStorage.setItem("unique_userid", uid);
    if(uid) localStorage.setItem("uid", uid);
    if(ut)  localStorage.setItem("unique_ut", ut);

    return { u, uid, ut };
  }

  async function checkApi(ctx){
    try{
      if(!S.API_BASE) throw new Error("API_BASE missing");

      // uid 없으면 online false로 표시만 하고 끝
      if(!ctx.uid){
        S.ui.setOnline(false);
        S.ui.setLog("MAIN에서 들어와야 플레이 가능합니다 (uid 필요)");
        return null;
      }

      const url = new URL(`${S.API_BASE}/slot/state`);
      url.searchParams.set("u", ctx.u);
      url.searchParams.set("uid", ctx.uid);

      const res = await fetch(url.toString(), { cache: "no-store" });
      const d = await res.json();

      if(d && d.ok){
        S.ui.setOnline(true);

        // 방어적으로 여러 키 지원
        const bet = d.bet ?? d.state?.bet;
        const jackpot = d.jackpot ?? d.state?.jackpot;
        const ut = d.ut ?? d.balanceUT ?? d.user?.ut ?? d.state?.ut;

        S.ui.setKpi({ bet, jackpot });
        if(ut !== undefined) {
          S.ui.setPlayer({ u: ctx.u, uid: ctx.uid, ut });
          localStorage.setItem("unique_ut", String(ut));
        } else {
          S.ui.setPlayer({ u: ctx.u, uid: ctx.uid, ut: ctx.ut || "" });
        }

        return d;
      }
      S.ui.setOnline(false);
      return null;
    }catch(e){
      S.ui.setOnline(false);
      return null;
    }
  }

  async function spin(ctx){
    if(!S.API_BASE) throw new Error("API_BASE missing");
    if(!ctx.uid) throw new Error("uid 없음: MAIN에서 들어와야 합니다");

    const url = new URL(`${S.API_BASE}/slot/spin`);
    url.searchParams.set("u", ctx.u);
    url.searchParams.set("uid", ctx.uid);

    const res = await fetch(url.toString(), {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({ u: ctx.u, uid: ctx.uid })
    });

    const data = await res.json();

    if(!data || !data.ok) {
      const msg = (data && (data.error || data.message)) ? (data.error || data.message) : "Spin failed";
      throw new Error(msg);
    }

    // normalize
    const grid = data.grid || data.result?.grid || null;
    const win = (data.result && data.result.win !== undefined) ? data.result.win : (data.win ?? 0);
    const winType = (data.result && data.result.winType) ? data.result.winType : (data.winType ?? "");

    const bet = data.bet ?? data.state?.bet;
    const jackpot = data.jackpot ?? data.state?.jackpot;
    const ut = data.ut ?? data.balanceUT ?? data.user?.ut ?? data.state?.ut;

    if(ut !== undefined && ut !== null){
      localStorage.setItem("unique_ut", String(ut));
    }

    return { raw:data, grid, win, winType, bet, jackpot, ut };
  }

  S.api = { getPlayerContext, checkApi, spin };
})(window.SLOT);
