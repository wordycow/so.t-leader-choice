(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.ui = {
    openTab(evt, tabName) {
      const content = document.getElementsByClassName("tb-content");
      for (let i = 0; i < content.length; i++) content[i].classList.remove("active");

      const tablinks = document.getElementsByClassName("tb-tab-btn");
      for (let i = 0; i < tablinks.length; i++) tablinks[i].classList.remove("active");

      document.getElementById(tabName).classList.add("active");
      evt.currentTarget.classList.add("active");
    },

    updateHeaderUI() {
      const u = U.STATE.user || U.auth.getUser() || {};
      const id = String(u.id || "").trim();
      const name = String(u.name || "").trim();
      const team = String(u.team || "").trim();

      const hello = document.getElementById("member-hello");
      if (hello) hello.textContent = (name || id || "멤버") + "님, 오늘도 성장하러 오셨군요.";

      const memberName = document.getElementById("member-name");
      if (memberName) memberName.textContent = id || "Unknown";

      const teamEl = document.getElementById("member-team");
      if (teamEl) teamEl.textContent = U.auth.isHQ() ? "소속: HQ" : (team ? "소속: " + team : "소속: -");

      const tbUser = document.getElementById("tb-user-name");
      if (tbUser) tbUser.textContent = name || id || "User";

      const adminLink = document.getElementById("ebook-admin-link");
      if (adminLink && !U.auth.isHQ()) adminLink.style.display = "none";
    },

    updateNicknameButton() {
      const btn = document.getElementById("btn-nick-reg");
      if (!btn) return;

      const u = U.STATE.user || U.auth.getUser() || {};
      const id = String(u.id || "").toLowerCase().trim();
      const savedNick = (id ? localStorage.getItem("myNickname_" + id) : "") || "";

      if (savedNick) {
        btn.textContent = "닉네임: " + savedNick;
        btn.classList.add("done");
        btn.onclick = null;
      } else {
        btn.textContent = "닉네임 등록";
        btn.classList.remove("done");
        btn.onclick = window.registerNickname;
      }
    },

    updateWalletUI() {
      const myUtEl = document.getElementById("my-ut-display");
      const myUsdtEl = document.getElementById("my-usdt-display");
      const rateLine = document.getElementById("ut-rate-line");
      if (!myUtEl) return;

      const ut = parseFloat(localStorage.getItem("myUtPoints") || "0");
      myUtEl.textContent = ut.toFixed(2);

      const price = (Number.isFinite(U.STATE.utPrice) && U.STATE.utPrice > 0) ? U.STATE.utPrice : 0.02;

      if (myUsdtEl) myUsdtEl.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;
      if (rateLine) rateLine.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;
    },

    bindBasicButtons() {
      const travelBtn = document.getElementById("travel-btn");
      if (travelBtn) travelBtn.addEventListener("click", () => window.open("index.html", "_blank"));

      const sotBtn = document.getElementById("sot-btn");
      if (sotBtn) sotBtn.addEventListener("click", () => window.open("https://www.ssoti.com/", "_blank"));

      const linkonBtn = document.getElementById("ppt-form-btn");
      if (linkonBtn) linkonBtn.addEventListener("click", () => window.open("https://linkon.gift/", "_blank"));

      const logoutBtn = document.getElementById("logout-btn");
      if (logoutBtn) logoutBtn.addEventListener("click", () => {
        if (confirm("로그아웃 하시겠습니까?")) {
          localStorage.removeItem("uniqueCurrentUser");
          window.location.href = "the-unique-gate.html";
        }
      });
    }
  };

  // ✅ inline onclick들이 쓰니까 전역 노출
  window.openTab = U.ui.openTab;
})();
