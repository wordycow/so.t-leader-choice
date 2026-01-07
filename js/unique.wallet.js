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

  function applyUserFromSheet(user){
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
    async refreshUserFromSheet(){
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) return;

      const r = await U.api.jsonp("getUser", { id: String(u.id).toLowerCase().trim() });
      if (r && r.ok && r.user) {
        applyUserFromSheet(r.user);
      }
    },

    async refreshDonationUSDT(){
      const db = U.supabase.init();
      try{
        const { data, error } = await db.from("profiles").select("donation_total");
        if (error) throw error;
        U.STATE.donationUSDT = (data || []).reduce((acc, r) => acc + (Number(r.donation_total) || 0), 0);
      } catch(e){
        console.warn("donation_total sum fail:", e);
        U.STATE.donationUSDT = 0;
      }
    },

    async refreshStatsFromSheet(){
      try{
        const r = await U.api.jsonp("getStats", {});
        if (r && r.ok && r.stats) {
          const total = Number(r.stats.total_ut_supply ?? r.stats.total_ut ?? 0);
          const price = Number(r.stats.ut_price ?? 0);
          U.STATE.totalUT = Number.isFinite(total) ? total : 0;
          if (Number.isFinite(price) && price > 0) U.STATE.utPrice = price;
        }
      } catch(e){
        console.warn("getStats fail:", e);
        U.STATE.totalUT = 0;
      }
    },

    async refreshRewardConfig(){
      try{
        const r = await U.api.jsonp("getConfig", {});
        if (r && r.ok && r.config) {
          const cfg = r.config;
          const vr = Number(cfg.VIDEO_REWARD);
          const er = Number(cfg.EBOOK_REWARD);
          const lm = Number(cfg.LUCKY_MIN);
          const lx = Number(cfg.LUCKY_MAX);
          if (Number.isFinite(vr)) U.STATE.videoReward = Math.floor(vr);
          if (Number.isFinite(er)) U.STATE.ebookReward = Math.floor(er);
          if (Number.isFinite(lm)) U.STATE.luckyMin = Math.floor(lm);
          if (Number.isFinite(lx)) U.STATE.luckyMax = Math.floor(lx);
          if (U.STATE.luckyMax < U.STATE.luckyMin) U.STATE.luckyMax = U.STATE.luckyMin;
        }
      } catch(_){}
    },

    async refreshPricing(){
      await this.refreshDonationUSDT();
      await this.refreshStatsFromSheet();

      if (!(Number.isFinite(U.STATE.utPrice) && U.STATE.utPrice > 0)) {
        if (U.STATE.totalUT > 0) U.STATE.utPrice = (U.STATE.donationUSDT * U.CONFIG.UT_PRICE_FACTOR) / U.STATE.totalUT;
        else U.STATE.utPrice = 0.02;
      }
      if (!Number.isFinite(U.STATE.utPrice) || U.STATE.utPrice <= 0) U.STATE.utPrice = 0.02;
    },

    async addUt(delta){
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) throw new Error("로그인 정보가 없습니다.");
      const r = await U.api.jsonp("addBalance", { id: String(u.id).toLowerCase().trim(), delta });
      if (!r || !r.ok || !r.user) throw new Error(r?.error || "UT update failed");
      applyUserFromSheet(r.user);
      await this.refreshPricing();
    },

    async sendP2P(receiver, amount){
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) throw new Error("로그인 정보가 없습니다.");
      const r = await U.api.jsonp("transfer", {
        fromId: String(u.id).toLowerCase().trim(),
        toNickname: receiver,
        amount
      });
      if (!r || !r.ok) throw new Error(r?.error || "송금 실패");
      if (r.fromUser) applyUserFromSheet(r.fromUser);
      await this.refreshUserFromSheet();
      await this.refreshPricing();
    }
  };

  // ✅ 전역: 닉네임 등록, 송금
  window.registerNickname = async function(){
    const u = U.STATE.user || U.auth.getUser();
    if (!u || !u.id) return alert("로그인 정보가 없습니다.");

    const idLower = String(u.id).toLowerCase().trim();
    const already = localStorage.getItem("myNickname_" + idLower);
    if (already) return alert("이미 등록된 닉네임입니다.");

    const rawNick = prompt("송금에 사용할 닉네임을 입력하세요.\n(변경 불가, 신중히 입력)");
    if (!rawNick) return;
    const nickname = U.utils.normNick(rawNick);
    if (!nickname) return;
    if (!confirm(`'${nickname}' (으)로 설정하시겠습니까?`)) return;

    const btn = document.getElementById("btn-nick-reg");
    const prev = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "처리 중..."; }

    try{
      const r = await U.api.jsonp("setNickname", { id: idLower, nickname });
      if (!r || !r.ok || !r.user) throw new Error(r?.error || "닉네임 저장 실패");
      applyUserFromSheet(r.user);
      U.ui.updateHeaderUI();
      U.ui.updateNicknameButton();
      alert("닉네임이 저장되었습니다.");
    } catch(e){
      console.error(e);
      alert("저장 실패: " + (e.message || e));
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = prev; }
      U.ui.updateNicknameButton();
    }
  };

  window.sendP2P = async function(){
    const receiver = U.utils.normNick(document.getElementById("p2p-receiver")?.value || "");
    const amount = Number(document.getElementById("p2p-amount")?.value);

    if (!receiver) return alert("받는 분 닉네임을 입력하세요.");
    if (!Number.isFinite(amount) || amount <= 0) return alert("보낼 수량(UT)을 올바르게 입력하세요.");

    const myBal = Number(localStorage.getItem("myUtPoints") || 0);
    if (amount > myBal) return alert("잔액 부족");
    if (!confirm(`${receiver}님에게 ${amount} UT를 송금하시겠습니까?`)) return;

    const btn = document.querySelector(".transfer-btn");
    const prev = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "처리 중..."; }

    try{
      await U.wallet.sendP2P(receiver, amount);
      alert("송금 완료");
      document.getElementById("p2p-amount").value = "";
      U.ui.updateWalletUI();
    } catch(e){
      console.error(e);
      alert("송금 오류: " + (e.message || e));
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = prev || "송금하기"; }
    }
  };
})();
