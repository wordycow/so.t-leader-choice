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
    const uid = clean(getParam("uid")) || clean(localStorage.getItem("unique_userid")) || "";

    const ut  = clean(getParam("ut"))  || clean(localStorage.getItem("unique_ut")) || "";

    localStorage.setItem("slot_player", u);
    if(uid) localStorage.setItem("unique_userid", uid);
    if(ut)  localStorage.setItem("unique_ut", ut);

    return { u, uid, ut };
  }

  function normState(d){
    if(!d) return null;

    // state keys (worker가 어떤 키를 주든 방어)
    const bet = d.bet ?? d.betUT ?? d.state?.bet ?? d.state?.betUT ?? d.config?.betUT;
    const jackpot = d.jackpot ?? d.jackpotUT ?? d.state?.jackpot ?? d.state?.jackpotUT;
    const ut = d.ut ?? d.balanceUT ?? d.user?.ut ?? d.player?.ut;

    const displayName = d.displayName ?? d.userName ?? d.name ?? d.player?.name;

    const totalIssuedUT = d.totalIssuedUT ?? d.econ?.totalIssuedUT;
    const utPrice = d.utPrice ?? d.econ?.utPrice;
    const winScale = d.winScale ?? d.econ?.winScale;

    return { bet, jackpot, ut, displayName, totalIssuedUT, utPrice, winScale };
  }

  async function checkApi(ctx){
    try{
      const url = new URL(`${S.API_BASE}/slot/state`);
      url.searchParams.set("u", ctx.u);
      if(ctx.uid) url.searchParams.set("uid", ctx.uid);

      const res = await fetch(url.toString(), { cache: "no-store" });
      const d = await res.json();

      if(d && d.ok){
        S.ui.setOnline(true);

        const st = normState(d);
        if(st){
          S.ui.setKpi({ bet: st.bet, jackpot: st.jackpot, win: 0 });
          if(st.ut !== undefined) S.ui.setPlayer({ u: ctx.u, displayName: st.displayName, ut: st.ut });
          S.ui.setEconomy({ totalIssuedUT: st.totalIssuedUT, utPrice: st.utPrice, winScale: st.winScale });
          if(st.ut !== undefined) localStorage.setItem("unique_ut", String(st.ut));
          if(st.displayName) localStorage.setItem("slot_display_name", String(st.displayName));
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
    const url = new URL(`${S.API_BASE}/slot/spin`);

    const res = await fetch(url.toString(), {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({
        u: ctx.u,
        uid: ctx.uid,
        // 서버 호환용(기존 worker가 user만 받는 경우 대비)
        user: ctx.uid || ctx.u
      })
    });

    const data = await res.json();

    if(!data || !data.ok){
      const msg = (data && data.error) ? data.error : "Spin failed";
      throw new Error(msg);
    }

    const grid = data.grid || data.result?.grid || null;

    const win = data.win ?? data.winUT ?? data.result?.win ?? 0;
    const winType = data.winType ?? data.result?.winType ?? (data.jackpotHit ? "JACKPOT" : "NORMAL");

    const bet = data.bet ?? data.betUT ?? data.state?.bet ?? data.state?.betUT ?? 10;
    const jackpot = data.jackpot ?? data.jackpotUT ?? data.state?.jackpot ?? data.state?.jackpotUT ?? 0;

    const ut = data.ut ?? data.balanceUT ?? data.user?.ut ?? data.player?.ut;
    const displayName = data.displayName ?? data.userName ?? data.name;

    const econ = {
      totalIssuedUT: data.totalIssuedUT ?? data.econ?.totalIssuedUT,
      utPrice: data.utPrice ?? data.econ?.utPrice,
      winScale: data.winScale ?? data.econ?.winScale
    };

    return { raw:data, grid, win, winType, bet, jackpot, ut, displayName, econ };
  }

  S.api = { getPlayerContext, checkApi, spin };
})(window.SLOT);
