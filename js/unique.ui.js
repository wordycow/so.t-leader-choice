(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.ui = {
    // ✅ 경고(aria-hidden + focus) 방지 버전
    openTab(evt, tabName) {
      const tabs = Array.from(document.getElementsByClassName("tb-content"));
      const activeEl = document.activeElement;

      // 1) 숨길 탭 안에 포커스가 있으면 먼저 blur (유튜브/버튼 포커스 경고 방지)
      if (activeEl) {
        for (const t of tabs) {
          const willHide = (t.id !== tabName) && t.classList.contains("active");
          if (willHide && t.contains(activeEl) && typeof activeEl.blur === "function") {
            activeEl.blur();
            break;
          }
        }
      }

      // 2) 탭 show/hide + aria-hidden/inert 정리
      for (const t of tabs) {
        const isOn = (t.id === tabName);

        t.classList.toggle("active", isOn);

        // 접근성 속성 정리
        t.setAttribute("aria-hidden", isOn ? "false" : "true");
        if (isOn) t.removeAttribute("inert");
        else t.setAttribute("inert", "");
      }

      // 3) 탭 버튼 active 처리
      const tablinks = Array.from(document.getElementsByClassName("tb-tab-btn"));
      tablinks.forEach((b) => b.classList.remove("active"));
      if (evt && evt.currentTarget) evt.currentTarget.classList.add("active");

      try { U.ui.updateWalletUI(); } catch (_) {}
    },

    updateHeaderUI() {
      const u = U.STATE.user || (U.auth && U.auth.getUser ? U.auth.getUser() : {}) || {};
      const id = String(u.id || "").trim();
      const name = String(u.name || "").trim();
      const team = String(u.team || "").trim();

      const hello = document.getElementById("member-hello");
      if (hello) hello.textContent = (name || id || "멤버") + "님, 오늘도 성장하러 오셨군요.";

      const memberName = document.getElementById("member-name");
      if (memberName) memberName.textContent = id || "Unknown";

      const teamEl = document.getElementById("member-team");
      if (teamEl) {
        const isHQ = (U.auth && U.auth.isHQ) ? U.auth.isHQ() : false;
        teamEl.textContent = isHQ ? "소속: HQ" : (team ? "소속: " + team : "소속: -");
      }

      const tbUser = document.getElementById("tb-user-name");
      if (tbUser) tbUser.textContent = name || id || "User";

      const adminLink = document.getElementById("ebook-admin-link");
      if (adminLink) {
        const isHQ = (U.auth && U.auth.isHQ) ? U.auth.isHQ() : false;
        if (!isHQ) adminLink.style.display = "none";
      }
    },

    updateNicknameButton() {
      const btn = document.getElementById("btn-nick-reg");
      if (!btn) return;

      const u = U.STATE.user || (U.auth && U.auth.getUser ? U.auth.getUser() : {}) || {};
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
      const price =
        (Number.isFinite(U.STATE && U.STATE.utPrice) && U.STATE.utPrice > 0)
          ? U.STATE.utPrice
          : 0.02;

      // tab-main
      const myUtEl = document.getElementById("my-ut-display");
      if (myUtEl) myUtEl.textContent = ut.toFixed(2);

      const myUsdtEl = document.getElementById("my-usdt-display");
      if (myUsdtEl) myUsdtEl.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;

      const rateLine = document.getElementById("ut-rate-line");
      if (rateLine) rateLine.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;

      // tab-transfer (좌측 자산)
      const myUtTransfer = document.getElementById("my-ut-display-transfer");
      if (myUtTransfer) myUtTransfer.textContent = ut.toFixed(2);

      const myUsdtTransfer = document.getElementById("my-usdt-display-transfer");
      if (myUsdtTransfer) myUsdtTransfer.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;

      const rateTransfer = document.getElementById("ut-rate-line-transfer");
      if (rateTransfer) rateTransfer.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;

      // tab-transfer (우측 뱃지)
      const badge = document.getElementById("my-ut-transfer-badge");
      if (badge) badge.textContent = `보유: ${Math.floor(ut).toLocaleString()} UT`;
    },

    bindBasicButtons() {
      const bindOnce = (el, key, fn) => {
        if (!el) return;
        if (el.dataset.bound === "1") return;
        el.dataset.bound = "1";
        el.addEventListener("click", fn);
      };

      bindOnce(document.getElementById("work-btn"), "work", () =>
        window.open("the-unique-work-tool.html", "_blank")
      );

      bindOnce(document.getElementById("sot-btn"), "sot", () =>
        window.open("https://www.ssoti.com/", "_blank")
      );

      bindOnce(document.getElementById("travel-btn"), "travel", () =>
        window.open("index.html", "_blank")
      );

      bindOnce(document.getElementById("ppt-form-btn"), "linkon", () =>
        window.open("https://linkon.gift/", "_blank")
      );

      bindOnce(document.getElementById("market-btn"), "market", () =>
        window.open("market.html", "_blank")
      );

      bindOnce(document.getElementById("logout-btn"), "logout", () => {
        if (confirm("로그아웃 하시겠습니까?")) {
          localStorage.removeItem("uniqueCurrentUser");
          window.location.href = "the-unique-gate.html";
        }
      });
    }
  };

  // ✅ 초기 상태에서도 aria-hidden/inert 정리(첫 로딩 안정화)
  try {
    const tabs = Array.from(document.getElementsByClassName("tb-content"));
    tabs.forEach((t) => {
      const isOn = t.classList.contains("active");
      t.setAttribute("aria-hidden", isOn ? "false" : "true");
      if (isOn) t.removeAttribute("inert");
      else t.setAttribute("inert", "");
    });
  } catch (_) {}

  window.openTab = U.ui.openTab;
})();
