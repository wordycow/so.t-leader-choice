(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.api = {
    jsonp(action, params={}) {
      const { GOOGLE_SCRIPT_URL } = U.CONFIG;
      return new Promise((resolve, reject) => {
        const cb = "cb_" + Date.now() + "_" + Math.random().toString(16).slice(2);

        params.action = action;
        params.callback = cb;
        params._t = Date.now();

        const qs = new URLSearchParams(params).toString();
        const s = document.createElement("script");
        const joiner = GOOGLE_SCRIPT_URL.includes("?") ? "&" : "?";
        s.src = GOOGLE_SCRIPT_URL + joiner + qs;

        const t = setTimeout(() => {
          cleanup();
          reject(new Error("API timeout"));
        }, 12000);

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
  };
})();
