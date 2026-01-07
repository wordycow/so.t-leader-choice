(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.auth = {
    getUser() {
      return U.utils.safeJsonParse(localStorage.getItem("uniqueCurrentUser"), null);
    },
    setUser(u) {
      localStorage.setItem("uniqueCurrentUser", JSON.stringify(u));
    },
    requireLogin() {
      const u = this.getUser();
      if (!u || !u.id) {
        window.location.href = "the-unique-gate.html";
        return false;
      }
      U.STATE.user = u;
      return true;
    },
    isHQ() {
      const u = U.STATE.user || this.getUser() || {};
      const team = String(u.team || "").trim();
      const name = String(u.name || "").trim();
      return team === "HQ" || (name && team && name === team);
    }
  };

  function applyUserFromSheet(user) {
    const idLower = String(user.id || "").toLowerCase().trim();
    const payload = {
      id: idLower,
      name: user.name || "",
      nickname: user.nickname || "",
      team: user.team || "",
      joinedAt: user.joinedAt || "",
      balance: Number(user.balance || 0)
    };

    U.STATE.user = payload;
    U.auth.setUser(payload);
    localStorage.setItem("myUtPoints", String(payload.balance));

    const nickKey = "myNickname_" + idLower;
    if ((payload.nickname || "").trim()) localStorage.setItem(nickKey, payload.nickname.trim());
    else localStorage.removeItem(nickKey);
  }

  U.wallet = {
    async refreshUserFromSheet() {
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) return;

      const r = await U.api.jsonp("getUser", { id: String(u.id).toLowerCase().trim() });
      if (r && r.ok && r.user) {
        applyUserFromSheet(r.user);
      }
    },

    async refreshDonationUSDT() {
      const db = U.supabase.init(); // ✅ unique.supabase.js에 init()이 있어야 함
      try {
        const { data, error } = await db.from("profiles").select("donation_total");
        if (error) throw error;
        U.STATE.donationUSDT = (data || []).reduce((acc, r) => acc + (Number(r.donation_total) || 0), 0);
      } catch (e) {
        console.warn("donation_total sum fail:", e);
        U.STATE.donationUSDT = 0;
      }
    },

    async refreshStatsFromSheet() {
      try {
        const r = await U.api.jsonp("getStats", {});
        if (r && r.ok && r.stats) {
          const total = Number(r.stats.total_ut_supply ?? r.stats.total_ut ?? 0);
          const price = Number(r.stats.ut_price ?? 0);
          U.STATE.totalUT = Number.isFinite(total) ? total : 0;
          if (Number.isFinite(price) && pric
