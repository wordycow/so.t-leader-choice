(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  function jsonp(url, params = {}, timeoutMs = 12000) {
    return new Promise((resolve, reject) => {
      const cb = `__slotcb_${Date.now()}_${Math.floor(Math.random()*1e9)}`;
      const q = new URLSearchParams({ ...params, callback: cb });
      const src = `${url}${url.includes("?") ? "&" : "?"}${q.toString()}`;

      let done = false;
      const script = document.createElement("script");
      const timer = setTimeout(() => {
        if (done) return;
        done = true;
        cleanup();
        reject(new Error("JSONP timeout"));
      }, timeoutMs);

      function cleanup() {
        clearTimeout(timer);
        try { delete window[cb]; } catch(_) { window[cb] = undefined; }
        if (script.parentNode) script.parentNode.removeChild(script);
      }

      window[cb] = (data) => {
        if (done) return;
        done = true;
        cleanup();
        resolve(data);
      };

      script.onerror = () => {
        if (done) return;
        done = true;
        cleanup();
        reject(new Error("JSONP load error"));
      };

      script.src = src;
      document.head.appendChild(script);
    });
  }

  async function call(action, params) {
    const url = String(CFG().SCRIPT_URL || "").trim();
    if (!url || url.includes("PASTE_YOUR")) {
      return { ok:false, error:"SCRIPT_URL_NOT_SET" };
    }
    return await jsonp(url, { action, ...params });
  }

  SLOT.api = {
    getSlotState: (id) => call("getSlotState", { id }),
    slotSpin: (id, bet) => call("slotSpin", { id, bet }),
  };
})();
