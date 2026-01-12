(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const C = () => SLOT.config;

  function isValidScriptUrl(url) {
    return typeof url === "string" && url.startsWith("https://script.google.com/macros/s/");
  }

  function jsonp(action, params = {}) {
    return new Promise((resolve, reject) => {
      const scriptUrl = C()?.SCRIPT_URL;
      if (!isValidScriptUrl(scriptUrl)) {
        reject(new Error("SCRIPT_URL not set in slot.config.js"));
        return;
      }

      const cbName = `__slot_cb_${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const qs = new URLSearchParams({
        action,
        callback: cbName,
        t: String(Date.now()),
        ...Object.fromEntries(
          Object.entries(params).map(([k, v]) => [k, v == null ? "" : String(v)])
        ),
      });

      const s = document.createElement("script");
      s.src = `${scriptUrl}?${qs.toString()}`;
      s.async = true;

      function cleanup() {
        try { delete window[cbName]; } catch (_) { window[cbName] = undefined; }
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }

      window[cbName] = (data) => {
        cleanup();
        resolve(data);
      };

      s.onerror = () => {
        cleanup();
        reject(new Error("network_error"));
      };

      document.head.appendChild(s);
    });
  }

  SLOT.api = {
    async getSlotState(id) {
      return jsonp("getSlotState", { id });
    },
    async slotSpin(id, bet) {
      return jsonp("slotSpin", { id, bet });
    },
  };
})();
