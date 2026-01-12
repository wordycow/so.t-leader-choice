/* games/slot/slot.api.js */
(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config || {};

  function qs(obj = {}) {
    const u = new URLSearchParams();
    Object.entries(obj).forEach(([k, v]) => {
      if (v === undefined || v === null) return;
      u.set(k, String(v));
    });
    return u.toString();
  }

  async function call(action, params = {}) {
    if (!cfg.SCRIPT_URL || cfg.SCRIPT_URL.includes("PASTE_YOUR")) {
      throw new Error("SCRIPT_URL not set in slot.config.js");
    }

    const url = `${cfg.SCRIPT_URL}?${qs({ action, ...params, _ts: Date.now() })}`;

    const r = await fetch(url, { method: "GET" });
    const j = await r.json().catch(() => null);
    if (!j) throw new Error("API response not JSON");
    if (!j.ok) throw new Error(j.error || j.message || "API error");
    return j;
  }

  SLOT.api = { call };
})();
