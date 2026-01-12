(function () {
  window.SLOT = window.SLOT || {};
  document.addEventListener("DOMContentLoaded", () => {
    if (window.SLOT.app && window.SLOT.app.boot) window.SLOT.app.boot();
  });
})();
