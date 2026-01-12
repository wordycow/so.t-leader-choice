/* games/slot/slot.page.js */
(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config;

  function getParam(name) {
    const u = new URL(location.href);
    return u.searchParams.get(name);
  }

  function $(sel) { return document.querySelector(sel); }

  async function boot() {
    // ✅ URL ?id= 가 최우선, 없으면 localStorage
    const idFromUrl = (getParam("id") || "").trim().toLowerCase();
    const idSaved = (localStorage.getItem(cfg.STORAGE.userId) || "").trim().toLowerCase();
    const id = idFromUrl || idSaved;

    // paytable toggle 바인딩 + 잭팟배너 복원
    SLOT.ui.bindPayTableToggle();
    SLOT.ui.restoreJackpotBanner();

    // 버튼 바인딩
    const btnSpin = $("#btnSpin") || $("#spinBtn") || $('[data-action="spin"]');
    const btnMinus = $("#btnBetMinus") || $("#betMinus") || $('[data-action="bet-minus"]');
    const btnPlus = $("#btnBetPlus") || $("#betPlus") || $('[data-action="bet-plus"]');

    if (btnMinus) btnMinus.addEventListener("click", () => SLOT.app.changeBet(-1));
    if (btnPlus) btnPlus.addEventListener("click", () => SLOT.app.changeBet(+1));
    if (btnSpin) btnSpin.addEventListener("click", () => SLOT.app.spin());

    // 아이디가 없으면 안내만 띄움(페이지는 죽지 않게)
    if (!id) {
      const msg = $("#loginMsg") || $("#loginWarning") || $("#needLogin");
      if (msg) msg.style.display = "";
      SLOT.ui.setLastResult("LOGIN REQUIRED");
      return;
    }

    // URL id가 있으면 저장해두기
    localStorage.setItem(cfg.STORAGE.userId, id);

    // init
    await SLOT.app.init(id);

    // URL에 id가 있으면 로그인 경고 숨김
    const msg = $("#loginMsg") || $("#loginWarning") || $("#needLogin");
    if (msg) msg.style.display = "none";
  }

  document.addEventListener("DOMContentLoaded", () => {
    boot().catch((e) => {
      console.error(e);
      SLOT?.ui?.setLastResult?.("ERROR: " + (e?.message || e));
    });
  });
})();
