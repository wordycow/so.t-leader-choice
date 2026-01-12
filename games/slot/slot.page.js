(() => {
  function getIdFromQuery() {
    const u = new URL(location.href);
    return u.searchParams.get("id") || "";
  }

  document.addEventListener("DOMContentLoaded", async () => {
    try {
      window.SLOT.ui.init();
      const id = getIdFromQuery();
      await window.SLOT.app.boot(id);
      console.log("Lily's page content initialized");
    } catch (e) {
      console.error(e);
      alert(String(e.message || e));
    }
  });
})();
