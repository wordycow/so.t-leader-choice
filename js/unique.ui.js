(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.ui = {
    openTab(evt, tabName) {
      // content toggle
      const content = document.getElementsByClassName("tb-content");
      for (let i = 0; i < content.length; i++) content[i].classList.remove("active");

      // tab button toggle
      const tablinks = document.getElementsByClassName("tb-tab-btn");
      for (let i = 0; i < tablinks.length; i++) tablinks[i].classList.remove("active");

      const target = document.getElementById(tabName);
      if (target) target.classList.add("active");
      if (evt && evt.currentTarget) evt.currentTarget.classList.add("active");

      // ✅ 탭 바뀔 때도 송금 탭 뱃지/표시 갱신 (안전)
      try { U.ui.updateWalletUI(); } catch (_) {}
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
        btn.onclick = window.registerNickname || null;
      }
    },

    updateWalletUI() {
      const ut = parseFloat(localStorage.getItem("myUtPoints") || "0");

      // 정산가
      const price = (Number.isFinite(U.STATE.utPrice) && U.STATE.utPrice > 0) ? U.STATE.utPrice : 0.02;

      // ===== tab-main 좌측 자산 =====
      const myUtEl = document.getElementById("my-ut-display");
      if (myUtEl) myUtEl.textContent = ut.toFixed(2);

      const myUsdtEl = document.getElementById("my-usdt-display");
      if (myUsdtEl) myUsdtEl.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;

      const rateLine = document.getElementById("ut-rate-line");
      if (rateLine) rateLine.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;

      // ===== tab-transfer 좌측 자산(새 레이아웃) =====
      const myUtTransfer = document.getElementById("my-ut-display-transfer");
      if (myUtTransfer) myUtTransfer.textContent = ut.toFixed(2);

      const myUsdtTransfer = document.getElementById("my-usdt-display-transfer");
      if (myUsdtTransfer) myUsdtTransfer.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;

      const rateTransfer = document.getElementById("ut-rate-line-transfer");
      if (rateTransfer) rateTransfer.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;

      // ===== tab-transfer 우측 뱃지 =====
      const badge = document.getElementById("my-ut-transfer-badge");
      if (badge) badge.textContent = `보유: ${Math.floor(ut).toLocaleString()} UT`;
    },

    bindBasicButtons() {
      // ✅ work-btn
      const workBtn = document.getElementById("work-btn");
      if (workBtn && workBtn.dataset.bound !== "1") {
        workBtn.dataset.bound = "1";
        workBtn.addEventListener("click", () => window.open("the-unique-work-tool.html", "_blank"));
      }

      // ✅ So.T
      const sotBtn = document.getElementById("sot-btn");
      if (sotBtn && sotBtn.dataset.bound !== "1") {
        sotBtn.dataset.bound = "1";
        sotBtn.addEventListener("click", () => window.open("https://www.ssoti.com/", "_blank"));
      }

      // ✅ 여행신청/광고 문의 (현재 index.html로 열고 있음)
      const travelBtn = document.getElementById("travel-btn");
      if (travelBtn && travelBtn.dataset.bound !== "1") {
        travelBtn.dataset.bound = "1";
        travelBtn.addEventListener("click", () => window.open("index.html", "_blank"));
      }

      // ✅ Linkon
      const linkonBtn = document.getElementById("ppt-form-btn");
      if (linkonBtn && linkonBtn.dataset.bound !== "1") {
        linkonBtn.dataset.bound = "1";
        linkonBtn.addEventListener("click", () => window.open("https://linkon.gift/", "_blank"));
      }

      // ✅ Market
      const marketBtn = document.getElementById("market-btn");
      if (marketBtn && marketBtn.dataset.bound !== "1") {
        marketBtn.dataset.bound = "1";
        marketBtn.addEventListener("click", () => window.open("market.html", "_blank"));
      }

      // ✅ Logout
      const logoutBtn = document.getElementById("logout-btn");
      if (logoutBtn && logoutBtn.dataset.bound !== "1") {
        logoutBtn.dataset.bound = "1";
        logoutBtn.addEventListener("click", () => {
          if (confirm("로그아웃 하시겠습니까?")) {
            localStorage.removeItem("uniqueCurrentUser");
            window.location.href = "the-unique-gate.html";
          }
        });
      }
    }
  };

  // inline onclick 지원
  window.openTab = U.ui.openTab;
})();
