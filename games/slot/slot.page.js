(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  window.addEventListener("DOMContentLoaded", () => {
    try { SLOT.app.boot(); } catch (e) { console.error(e); }
  });
})();
