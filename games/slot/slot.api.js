(function () {
  const S = (window.S = window.S || {});
  S.api = S.api || {};

  const DEFAULT_TIMEOUT = 12000;

  function getGoogleScriptUrl() {
    // ✅ unique.config.js에서 가져오기
    const U = window.U || window.UNIQUE || {};
    const fromUnique = U?.CONFIG?.GOOGLE_SCRIPT_URL ? String(U.CONFIG.GOOGLE_SCRIPT_URL).trim() : "";
    const fromLocal = S?.CONFIG?.GOOGLE_SCRIPT_URL ? String(S.CONFIG.GOOGLE_SCRIPT_URL).trim() : "";
    return fromUnique || fromLocal || "";
  }

  function buildUrl(base, params) {
    const hasQ = base.includes("?");
    const qs = Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join("&");
    return base + (hasQ ? "&" : "?") + qs;
  }

  function jsonp(base, params = {}, timeoutMs = DEFAULT_TIMEOUT) {
    return new Promise((resolve, reject) => {
      const cb = `__slotcb_${Date.now()}_${Math.random().toString(16).slice(2)}`;
      let done = false;

      const cleanup = (script, timer) => {
        if (done) return;
        done = true;
        try { delete window[cb]; } catch (_) {}
        if (script && script.parentNode) script.parentNode.removeChild(script);
        if (timer) clearTimeout(timer);
      };

      window[cb] = (data) => {
        cleanup(script, timer);
        resolve(data);
      };

      const url = buildUrl(base, { ...params, callback: cb, _ts: Date.now() });

      const script = document.createElement("script");
      script.src = url;
      script.async = true;
      script.onerror = () => {
        cleanup(script, timer);
        reject(new Error("jsonp load error"));
      };

      const timer = setTimeout(() => {
        cleanup(script, timer);
        reject(new Error("jsonp timeout"));
      }, timeoutMs);

      document.head.appendChild(script);
    });
  }

  async function call(action, params = {}) {
    const base = getGoogleScriptUrl();
    if (!base) throw new Error("GOOGLE_SCRIPT_URL not set (unique.config.js 확인)");

    const data = await jsonp(base, { action, ...params });
    if (!data || data.ok !== true) {
      const msg = data?.message || data?.error || "API error";
      const err = new Error(msg);
      err.payload = data;
      throw err;
    }
    return data;
  }

  S.api.call = call;
  S.api.getConfig = () => call("getConfig");
  S.api.getSlotState = (id) => call("getSlotState", { id });
  S.api.slotCommit = (payload) => call("slotCommit", payload);
})();
