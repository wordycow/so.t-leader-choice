(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const getScriptUrl = () => SLOT?.config?.SCRIPT_URL;

  async function call(action, params = {}) {
    const base = getScriptUrl();
    if (!base) throw new Error("SCRIPT_URL missing");

    const url = new URL(base);
    url.searchParams.set("action", action);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));

    const res = await fetch(url.toString(), { method: "GET", mode: "cors" });
    const json = await res.json();

    if (!json || json.ok !== true) {
      const msg = json?.error || json?.message || "API error";
      throw new Error(msg);
    }
    return json;
  }

  SLOT.api = {
    call,
    getSlotState: (id) => call("getSlotState", { id }),
    slotSpin: (id, bet) => call("slotSpin", { id, bet }),
    adminInfo: () => call("adminInfo", {}),
    adminSave: (payload) => call("adminSave", payload || {}),
  };
})();
