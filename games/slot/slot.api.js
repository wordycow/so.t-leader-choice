/* /games/slot/slot.api.js */
(function () {
  "use strict";

  function normBase(input) {
    const raw = (input || "").trim();
    if (!raw) return "";
    return raw.replace(/\/+$/,qTH/, "");
  }

  function slotRoot() {
    const base = normBase(window.SLOT_API_BASE || "");
    if (!base) return "";
    // base가 .../slot 로 끝나면 그대로, 아니면 /slot 붙임
    return /\/slot$/i.test(base) ? base : (base + "/slot");
  }

  async function readJsonOrText(res) {
    const ct = (res.headers.get("content-type") || "").toLowerCase();
    if (ct.includes("application/json")) return await res.json();
    const text = await res.text();
    try { return JSON.parse(text); } catch { return { ok: false, error: text || `HTTP_${res.status}` }; }
  }

  async function request(path, { method = "GET", qs = null, body = null } = {}) {
    const root = slotRoot();
    if (!root) throw new Error("SLOT_API_BASE_missing");

    let url = root + path;
    if (qs && typeof qs === "object") {
      const sp = new URLSearchParams();
      Object.keys(qs).forEach(k => {
        if (qs[k] !== undefined && qs[k] !== null) sp.set(k, String(qs[k]));
      });
      const q = sp.toString();
      if (q) url += (url.includes("?") ? "&" : "?") + q;
    }

    const headers = { "Accept": "application/json" };
    const init = { method, headers, mode: "cors" };

    if (body !== null) {
      headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(body);
    }

    const res = await fetch(url, init);
    const data = await readJsonOrText(res);

    // 서버가 ok:false를 줘도 그대로 반환 (throw 하지 않음)
    // 단, 네트워크/HTTP 자체 실패만 throw
    if (!res.ok && !(data && typeof data === "object" && "ok" in data)) {
      throw new Error(`HTTP_${res.status}`);
    }
    return data;
  }

  const api = {
    getBase() {
      return slotRoot();
    },

    // ✅ 유저 상태 읽기
    async state(user) {
      return await request("/state", { method: "GET", qs: { u: user } });
    },

    // ✅ 스핀 요청
    async spin(user, bet) {
      return await request("/spin", { method: "POST", body: { u: user, bet } });
    },

    // ✅ 유저 등록(서버에 /slot/register 가 있어야 함)
    async register(user) {
      return await request("/register", { method: "POST", body: { u: user } });
    },

    // ✅ user_not_found_in_sheet면 자동 등록 시도
    async ensureUser(user) {
      const st = await api.state(user);
      if (st && st.ok) return st;

      const err = (st && st.error) ? String(st.error) : "";
      if (err === "user_not_found_in_sheet") {
        const reg = await api.register(user);
        if (reg && reg.ok) {
          return await api.state(user);
        }
        return reg; // 등록 실패면 등록 응답 그대로
      }
      return st;
    }
  };

  window.SLOT = window.SLOT || {};
  window.SLOT.api = api;
})();
