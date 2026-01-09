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
  function getPlayerContext(){
    const u   = clean(getParam("u"))   || clean(localStorage.getItem("slot_player")) || "Guest";
    const uid = clean(getParam("uid")) || clean(localStorage.getItem("unique_userid")) || clean(localStorage.getItem("uid")) || "";

    // 표시용 UT 캐시
    const ut  = clean(getParam("ut"))  || clean(localStorage.getItem("unique_ut")) || "";

    // ✅ 서버에서 user로 쓸 키 (우선 uid, 없으면 닉)
    const userKey = uid || u;

    localStorage.setItem("slot_player", u);
    if(uid) localStorage.setItem("unique_userid", uid);
    if(ut)  localStorage.setItem("unique_ut", ut);

    return { u, uid, ut, userKey };
  }

  async function checkApi(ctx){
    try{
      // ✅ Worker가 받는 파라미터는 user
      const url = new URL(`${S.API_BASE}/slot/state`);
      url.searchParams.set("user", ctx.userKey);
      // 참고용 (worker가 무시해도 됨)
      url.searchParams.set("u", ctx.u);
      if(ctx.uid) url.searchParams.set("uid", ctx.uid);

      const res = await fetch(url.toString(), { cache: "no-store" });
      const d = await res.json();

      if(d && d.ok){
        S.ui.setOnline(true);

        // ✅ Worker v3 키: betUT, jackpotUT, (ut 추가해줄 예정)
        const bet = d.betUT ?? d.bet ?? d.state?.bet ?? 10;
        const jackpot = d.jackpotUT ?? d.jackpot ?? d.state?.jackpot ?? 0;
        const ut = d.ut ?? d.userUT ?? d.balanceUT ?? d.user?.ut;

        S.ui.setKpi({ bet, jackpot });
        if(ut !== undefined) S.ui.setPlayer({ u: ctx.u, uid: ctx.uid, ut });

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
    // ✅ Worker는 body.user를 요구한다
    const url = new URL(`${S.API_BASE}/slot/spin`);
    url.searchParams.set("user", ctx.userKey);

    const res = await fetch(url.toString(), {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({
        user: ctx.userKey, // ✅ 핵심
        u: ctx.u,
        uid: ctx.uid
      })
    });

    const data = await res.json();

    if(!data || !data.ok) {
      const msg = (data && data.error) ? data.error : "Spin failed";
      throw new Error(msg);
    }

    // normalize
    const grid = data.grid || data.result?.grid || null;

    const win = data.winUT ?? data.win ?? (data.result?.win ?? 0);
    const bet = data.betUT ?? data.bet ?? (data.state?.bet ?? 10);
    const jackpot = data.jackpotUT ?? data.jackpot ?? (data.state?.jackpot ?? 0);

    // ✅ worker에서 ut 내려주면 표시/동기화
    const ut = data.ut ?? data.userUT ?? data.balanceUT ?? data.user?.ut;

    const winType =
      data.winType ||
      data.result?.winType ||
      (Number(win) > 0 ? "WIN" : "LOSE");

    return { raw:data, grid, win, winType, bet, jackpot, ut };
  }

  S.api = { getPlayerContext, checkApi, spin };
})(window.SLOT);
