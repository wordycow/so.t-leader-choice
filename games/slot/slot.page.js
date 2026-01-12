(() => {
  document.addEventListener("DOMContentLoaded", () => {
    try {
      window.SLOT?.app?.boot?.();
    } catch (e) {
      console.error("[SLOT] boot error:", e);
    }
  });
})();
