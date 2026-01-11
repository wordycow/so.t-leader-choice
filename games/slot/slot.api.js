// games/slot/slot.api.js
(() => {
  // ✅ 고정: 기존 프로젝트 동일
  const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";
  const WORKER_BASE_URL   = "https://the-unique-vault-api.wordycow0001.workers.dev";

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  function apiOnceJSONP(action, params = {}, timeoutMs = 25000) {
    return new Promise((resolve, reject) => {
      const cb = "cb_" + Date.now() + "_" + Math.random().toString(16).slice(2);

      params.action = action;
      params.callback = cb;
      params._t = Date.now();

      const qs = new URLSearchParams(params).toString();
      const s = document.createElement("script");
      const joiner = GOOGLE_SCRIPT_URL.includes("?") ? "&" : "?";
      s.src = GOOGLE_SCRIPT_URL + joiner + qs;

      const t = setTimeout(() => { cleanup(); reject(new Error("API timeout")); }, timeoutMs);

      window[cb] = (data) => { cleanup(); resolve(data); };
      s.onerror = () => { cleanup(); reject(new Error("API load failed")); };

      function cleanup() {
        clearTimeout(t);
        try { delete window[cb]; } catch(e){}
        try { s.remove(); } catch(e){}
      }
      document.body.appendChild(s);
    });
  }

  async function apiJSONP(action, params = {}) {
    let lastErr = null;
    for (let i = 1; i <= 3; i++){
      try{
        const timeoutMs = (i === 1) ? 20000 : 30000;
        return await apiOnceJSONP(action, params, timeoutMs);
      }catch(e){
        lastErr = e;
        await sleep(450 * i);
      }
    }
    throw lastErr || new Error("API failed");
  }

  async function apiWorker(action, params = {}, timeoutMs = 12000){
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), timeoutMs);

    try{
      const r = await fetch(`${WORKER_BASE_URL}/api/${encodeURIComponent(action)}`, {
        method: "POST",
        headers: { "content-type":"application/json" },
        body: JSON.stringify(params || {}),
        signal: controller.signal,
        cache: "no-store",
        credentials: "omit"
      });
      const js = await r.json().catch(()=>null);
      if (!js) throw new Error("worker_bad_json");
      return js;
    } finally {
      clearTimeout(t);
    }
  }

  async function api(action, params = {}) {
    const force = new URLSearchParams(location.search).get("api");
    if (force === "legacy") return apiJSONP(action, params);
    if (force === "worker") return apiWorker(action, params, 20000);

    try{
      return await apiWorker(action, params, 9000);
    } catch(e){
      // worker에 slot 액션 없으면 여기로 떨어짐
      return await apiJSONP(action, params);
    }
  }

  function getLocalUser(){
    try{
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return null;
      const u = JSON.parse(raw);
      if (!u || !u.id) return null;
      return {
        id: String(u.id||"").trim().toLowerCase(),
        name: String(u.name||"").trim(),
        balance: Number(u.balance||0)
      };
    }catch(e){
      return null;
    }
  }

  async function getSlotState(){
    const u = getLocalUser();
    if (!u) return { ok:false, error:"no_session" };
    // ✅ Apps Script 액션명
    return await api("getSlotState", { id: u.id });
  }

  async function commitSlotSpin({ netDelta = 0, lossAmount = 0 }){
    const u = getLocalUser();
    if (!u) return { ok:false, error:"no_session" };

    // ✅ Apps Script 액션명
    return await api("slotCommit", {
      id: u.id,
      netDelta: Number(netDelta || 0),
      lossAmount: Number(lossAmount || 0)
    });
  }

  window.SLOT_API = { getLocalUser, getSlotState, commitSlotSpin };
})();
