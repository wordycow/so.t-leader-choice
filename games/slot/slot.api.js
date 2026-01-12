(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const cfg = SLOT.config || {};

  function isValidScriptUrl(u) {
    return typeof u === "string" && u.startsWith("https://") && u.includes("/exec");
  }

  function jsonp(url, params = {}) {
    return new Promise((resolve, reject) => {
      const cb = "__slotcb_" + Date.now() + "_" + Math.random().toString(16).slice(2);
      const qs = new URLSearchParams({ ...params, callback: cb }).toString();
      const src = url + (url.includes("?") ? "&" : "?") + qs;

      const s = document.createElement("script");
      s.async = true;
      s.src = src;

      let done = false;
      function cleanup() {
        if (done) return;
        done = true;
        try { delete window[cb]; } catch (_) { window[cb] = undefined; }
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }

      window[cb] = (data) => {
        cleanup();
        resolve(data);
      };

      s.onerror = () => {
        cleanup();
        reject(new Error("JSONP network error"));
      };

      document.head.appendChild(s);

      // 타임아웃(10초)
      setTimeout(() => {
        if (done) return;
        cleanup();
        reject(new Error("JSONP timeout"));
      }, 10000);
    });
  }

  SLOT.api = {
    async call(action, params = {}) {
      if (!isValidScriptUrl(cfg.SCRIPT_URL)) {
        // UI에 에러문구 박지 말고, 콘솔로만 남김
        console.error("[SLOT] SCRIPT_URL not set/invalid in slot.config.js");
        return { ok: false, error: "script_url_not_set" };
      }
      return jsonp(cfg.SCRIPT_URL, { action, ...params });
    },

    getSlotState(id) {
      return this.call("getSlotState", { id });
    },

    slotSpin(id, bet) {
      return this.call("slotSpin", { id, bet });
    },

    adminInfo() {
      return this.call("adminInfo", {});
    },

    adminSave(payload) {
      return this.call("adminSave", payload || {});
    }
  };
})();
