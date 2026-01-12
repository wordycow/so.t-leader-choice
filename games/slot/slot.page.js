(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  function getParam(name){
    const u = new URL(location.href);
    return u.searchParams.get(name);
  }

  window.addEventListener("DOMContentLoaded", async () => {
    SLOT.UI.init();
    SLOT.app.initDom();

    const id = (getParam("id") || "").trim();
    if (!id) {
      SLOT.UI.showLoginOverlay(true);
      return;
    }

    // SCRIPT_URL 체크: 에러를 LAST RESULT에 글씨로 박지 말고 오버레이로만 안내
    const url = String(SLOT.config.SCRIPT_URL || "").trim();
    if (!url) {
      SLOT.UI.showSetupOverlay(true);
      return;
    }

    await SLOT.app.boot({ id });
  });
})();
