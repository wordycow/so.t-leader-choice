(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

  function jsonpOnce(action, params = {}, timeoutMs = 20000) {
    const { GOOGLE_SCRIPT_URL } = U.CONFIG;

    return new Promise((resolve, reject) => {
      const cb = "cb_" + Date.now() + "_" + Math.random().toString(16).slice(2);

      params.action = action;
      params.callback = cb;
      params._t = Date.now(); // cache bust

      const qs = new URLSearchParams(params).toString();
      const s = document.createElement("script");
      const joiner = GOOGLE_SCRIPT_URL.includes("?") ? "&" : "?";
      s.src = GOOGLE_SCRIPT_URL + joiner + qs;

      const t = setTimeout(() => {
        cleanup();
        reject(new Error("API timeout"));
      }, timeoutMs);

      window[cb] = (data) => { cleanup(); resolve(data); };
      s.onerror = () => { cleanup(); reject(new Error("API load failed")); };

      function cleanup(){
        clearTimeout(t);
        try { delete window[cb]; } catch(_){}
        try { s.remove(); } catch(_){}
      }

      document.body.appendChild(s);
    });
  }

  U.api = {
    // ✅ 모바일 대비: 재시도 + 타임아웃 증가
    async jsonp(action, params = {}) {
      const maxTry = 3;
      let lastErr = null;

      for (let i = 1; i <= maxTry; i++) {
        try {
          // 1차 20초, 2~3차는 조금 더 여유
          const timeoutMs = (i === 1) ? 20000 : 25000;
          return await jsonpOnce(action, params, timeoutMs);
        } catch (e) {
          lastErr = e;
          // 지수 백오프 느낌으로 쉬었다가 재시도
          await sleep(350 * i);
        }
      }
      throw lastErr || new Error("API failed");
    }
  };
})();
