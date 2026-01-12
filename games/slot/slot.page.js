(() => {
  const $ = (id) => document.getElementById(id);

  function setPayCollapsed(collapsed) {
    const wrap = $("payWrap");
    const rule = document.querySelector("#paytableCard .ruleLine");
    if (!wrap) return;

    wrap.style.display = collapsed ? "none" : "";
    if (rule) rule.style.display = collapsed ? "none" : "";

    const k = window.SLOT?.config?.STORAGE_KEYS?.payCollapsed || "slot_pay_collapsed_v1";
    localStorage.setItem(k, collapsed ? "1" : "0");
  }

  function getPayCollapsed() {
    const k = window.SLOT?.config?.STORAGE_KEYS?.payCollapsed || "slot_pay_collapsed_v1";
    return localStorage.getItem(k) === "1";
  }

  function wirePayToggle() {
    const btn = $("payToggle");
    if (!btn) return;

    btn.addEventListener("click", () => {
      setPayCollapsed(!getPayCollapsed());
    });

    // 초기 상태 적용
    setPayCollapsed(getPayCollapsed());
  }

  function hideConfigErrorTextIfAny() {
    // LAST RESULT에 "ERROR: ..." 같은 문구를 남기는 코드가 있어도, 여기서 덮어씀
    const last = $("lastResult");
    if (!last) return;
    const t = (last.textContent || "").trim();
    if (t.startsWith("ERROR:")) last.textContent = "READY";
  }

  document.addEventListener("DOMContentLoaded", () => {
    wirePayToggle();
    hideConfigErrorTextIfAny();

    // 기존 앱 부팅이 있으면 그대로 실행
    try {
      if (window.SLOT?.page?.boot) window.SLOT.page.boot();
      else if (window.SLOT?.app?.boot) window.SLOT.app.boot();
      else if (window.SLOT?.app?.init) window.SLOT.app.init();
    } catch (e) {
      console.error(e);
    }
  });
})();
