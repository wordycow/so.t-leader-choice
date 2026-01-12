(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config || {};

  function assertScriptUrl() {
    const url = String(CFG().SCRIPT_URL || "").trim();
    if (!url || url.includes("PASTE_YOUR")) throw new Error("SCRIPT_URL not set in slot.config.js");
    return url;
  }

  function jsonp(params, timeoutMs = 12000) {
    const base = assertScriptUrl();
    return new Promise((resolve, reject) => {
      const cbName = "__SLOTcb_" + Math.random().toString(16).slice(2);
      const q = new URLSearchParams(params);
      q.set("callback", cbName);

      const script = document.createElement("script");
      let done = false;

      const cleanup = () => {
        try { delete window[cbName]; } catch (_) {}
        if (script && script.parentNode) script.parentNode.removeChild(script);
      };

      const timer = setTimeout(() => {
        if (done) return;
        done = true;
        cleanup();
        reject(new Error("JSONP timeout"));
      }, timeoutMs);

      window[cbName] = (data) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        cleanup();
        resolve(data);
      };

      script.onerror = () => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        cleanup();
        reject(new Error("JSONP load error"));
      };

      script.src = `${base}?${q.toString()}`;
      document.head.appendChild(script);
    });
  }

  async function call(action, payload = {}) {
    const res = await jsonp({ action, ...payload });
    if (!res || res.ok !== true) {
      throw new Error((res && (res.message || res.error)) ? (res.message || res.error) : "API error");
    }
    return res;
  }

  SLOT.api = {
    getSlotState: (id) => call("getSlotState", { id }),
    slotSpin: (id, bet) => call("slotSpin", { id, bet })
  };
})();
