// games/slot/slot_api.js
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

  function genUid(){
    // 안정적으로 하나 만들고 로컬에 고정
    try {
      if (crypto && crypto.randomUUID) return crypto.randomUUID();
    } catch(_) {}
    return "uid_" + Math.random().toString(16).slice(2) + Date.now().toString(16);
  }

  // ✅ prompt 없음. 있으면 쓰고 없으면 Guest.
  function getPlayerContext(){
    const u = clean(getParam("u")) || clean(localStorage.getItem("slot_player")) || "Guest";

    // uid: main에서 넘기면 그걸 최우선. 없으면 로컬 고정값을 만든다.
    let uid =
      clean(getParam("uid")) ||
      clean(localStorage.getItem("unique_userid")) ||
      clean(localStorage.getItem("uid")) ||
      "";

    if(!uid){
      uid = genUid();
      localStorage.setItem("unique_userid", uid);
      localStorage.setItem("uid", uid);
    }

    // ut는 main에서 넘겨주거나(ut=), localStorage에 있으면 표시용 캐시
    const ut = clean(getParam("ut")) || clean(localStorage.getItem("unique_ut")) || "";

    localStorage.setItem("slot_player", u);
    localStorage.setItem("unique_userid", uid);
    if(ut) localStorage.setItem("unique_ut", ut);

    return { u, uid, ut };
  }

  async function checkApi(ctx){
    try{
      if(!S.API_BASE){
        S.ui.setOnline(false);
        S.ui.setLog("API_BASE missing");
        return null;
      }

      const url = new URL(`${S.API_BASE}/slot/state`);
      url.searchParams.set("u", ctx.u);
      url.searchParams.set("uid", ctx.uid);

      const res = await fetch(url.toString(), { cache: "no-store" });
      const d = await res.json().catch(()=>null);

      if(d && d.ok){
        S.ui.setOnline(true);

        // 방어적 키
        const bet = d.bet ?? d.state?.bet ?? null;
        const jackpot = d.jackpot ?? d.state?.jackpot ?? null;
        const ut = d.ut ?? d.balanceUT ?? d.user?.ut ?? d.state?.ut ?? null;

        // 서버가 uid를 되돌려주면 그걸 신뢰(없어도 됨)
        const serverUid = d.uid ?? d.user?.uid ?? d.state?.uid ?? "";
        if(serverUid){
          ctx.uid = String(serverUid);
          localStorage.setItem("unique_userid", ctx.uid);
          localStorage.setItem("uid", ctx.uid);
        }

        if(bet !== null || jackpot !== null) S.ui.setKpi({ bet, jackpot });
        if(ut !== null && ut !== undefined){
          ctx.ut = String(ut);
          localStorage.setItem("unique_ut", String(ut));
          S.ui.setPlayer({ u: ctx.u, uid: ctx.uid, ut });
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

    const url = new URL(`${S.API_BASE}/slot/spin`);
    url.searchParams.set("u", ctx.u);
    url.searchParams.set("uid", ctx.uid);

    const res = await fetch(url.toString(), {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({ u: ctx.u, uid: ctx.uid })
    });

    const data = await res.json().catch(()=>null);

    if(!data || !data.ok) {
      const msg = (data && (data.error || data.message)) ? (data.error || data.message) : "Spin failed";

      // ✅ 유송 스샷의 missing_user를 여기서 더 친절하게
      if(String(msg).includes("missing_user")){
        throw new Error("missing_user (uid 연동 필요) - MAIN에서 들어오거나 uid가 전달돼야 함");
      }
      throw new Error(msg);
    }

    // normalize
    const grid = data.grid || data.result?.grid || null;
    const win = (data.result && data.result.win !== undefined) ? data.result.win : (data.win ?? 0);
    const winType = (data.result && data.result.winType) ? data.result.winType : (data.winType ?? "");

    const bet = data.bet ?? data.state?.bet ?? null;
    const jackpot = data.jackpot ?? data.state?.jackpot ?? null;
    const ut = data.ut ?? data.balanceUT ?? data.user?.ut ?? null;

    // ✅ 서버가 ut를 주면 ctx/localStorage도 갱신
    if(ut !== null && ut !== undefined){
      ctx.ut = String(ut);
      localStorage.setItem("unique_ut", String(ut));
    }

    return { raw:data, grid, win, winType, bet, jackpot, ut };
  }

  S.api = { getPlayerContext, checkApi, spin };
})(window.SLOT);
