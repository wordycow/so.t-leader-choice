// games/slot/slot.api.js
(() => {
  const S = (window.SLOT = window.SLOT || {});

  function normalizeBase(v) {
    const s = String(v || "").trim();
    return s ? s.replace(/\/+$/, "") : "";
  }

  function getBase() {
    // 1) window.SLOT_API_BASE (slot.html에서 박는 값)
    const w = normalizeBase(window.SLOT_API_BASE);

    // 2) localStorage (필요하면 수동 세팅 가능)
    const ls = normalizeBase(localStorage.getItem("unique_slot_api"));

    return w || ls || "";
  }

  function setBase(url) {
    const b = normalizeBase(url);
    localStorage.setItem("unique_slot_api", b);
    return b;
  }

  function url(path) {
    const base = getBase();
    if (!base) return path; // (원래는 권장X) 상대경로 fallback
    return base + path;
  }

  async function fetchJson(input, init) {
    const res = await fetch(input, init);
    const text = await res.text();

    // JSON 파싱 시도
    try {
      const data = JSON.parse(text);
      if (!res.ok) {
        const msg = data?.error || data?.message || `${res.status} ${res.statusText}`;
        throw new Error(msg);
      }
      return data;
    } catch (e) {
      // JSON이 아니라 HTML/텍스트로 온 경우
      if (!res.ok) throw new Error(`${res.status} ${res.statusText} :: ${text.slice(0, 140)}`);
      throw new Error(`NOT_JSON :: ${text.slice(0, 140)}`);
    }
  }

  async function state(nickname) {
    const u = (nickname || "").trim();
    if (!u) return { ok: false, error: "missing_nickname" };
    return fetchJson(url(`/slot/state?u=${encodeURIComponent(u)}`), { method: "GET" });
  }

  async function spin(nickname, bet) {
    const u = (nickname || "").trim();
    if (!u) return { ok: false, error: "missing_nickname" };
    return fetchJson(url(`/slot/spin`), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ u, bet })
    });
  }

  S.api = { getBase, setBase, state, spin };
})();
