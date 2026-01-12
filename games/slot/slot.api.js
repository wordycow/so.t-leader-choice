(function () {
  window.SLOT = window.SLOT || {};
  const { SCRIPT_URL } = window.SLOT.config;

  function jsonp(url, params, timeoutMs = 12000) {
    return new Promise((resolve, reject) => {
      const cb = "__slot_cb_" + Math.random().toString(36).slice(2);
      const p = Object.assign({}, params, { callback: cb });
      const qs = new URLSearchParams(p);
      const src = url + (url.includes("?") ? "&" : "?") + qs.toString();

      const script = document.createElement("script");
      let done = false;

      const t = setTimeout(() => {
        if (done) return;
        done = true;
        cleanup();
        reject(new Error("timeout"));
      }, timeoutMs);

      function cleanup() {
        clearTimeout(t);
        try { delete window[cb]; } catch(_){}
        try { script.remove(); } catch(_){}
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
        reject(new Error("jsonp_failed"));
      };

      script.src = src;
      document.head.appendChild(script);
    });
  }

  async function call(action, params = {}) {
    const res = await jsonp(SCRIPT_URL, Object.assign({ action }, params));
    if (!res || res.ok !== true) {
      const msg = (res && (res.message || res.error)) ? (res.message || res.error) : "api_error";
      throw new Error(msg);
    }
    return res;
  }

  window.SLOT.api = {
    call,
    getSlotState: (id) => call("getSlotState", { id }),
    slotCommit: (id, netDelta, lossAmount) =>
      call("slotCommit", { id, netDelta: String(netDelta), lossAmount: String(lossAmount) }),
  };
})();
