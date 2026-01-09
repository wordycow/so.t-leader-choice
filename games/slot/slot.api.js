// games/slot/slot.api.js
window.SLOT = window.SLOT || {};
(function (S) {
  // ✅ 기본 워커 주소를 "진짜"로 박아둠 (플레이스홀더 금지)
  const DEFAULT_API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  function getApiBase() {
    const ls = String(localStorage.getItem("unique_slot_api") || "").trim();
    const w  = String(window.SLOT_API_BASE || "").trim();
    const c  = String(S.API_BASE || "").trim();
    let base = (ls || w || c || DEFAULT_API_BASE).trim();
    base = base.replace(/\/+$/, "");
    return base;
  }

  function buildUrl(path, qs) {
    const base = getApiBase();
    if (!base) throw new Error("SLOT API BASE missing");
    const u = new URL(base + path);
    if (qs && typeof qs === "object") {
      Object.entries(qs).forEach(([k, v]) => {
        if (v === undefined || v === null || v === "") return;
        u.searchParams.set(k, String(v));
      });
    }
    return u.toString();
  }

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      method: options.method || "GET",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const ct = String(res.headers.get("content-type") || "");

    // JSON이면 파싱
    if (ct.includes("application/json")) {
      const j = await res.json().catch(() => null);
      if (!j) throw new Error(`Invalid JSON response (${res.status})`);
      return j;
    }

    // JSON 아니면(404 HTML 등) 텍스트로 원인 보여주기
    const text = await res.text().catch(() => "");
    const snippet = String(text || "").slice(0, 220).replace(/\s+/g, " ");
    throw new Error(`Non-JSON response (${res.status}): ${snippet}`);
  }

  function cleanName(v) {
    v = String(v || "").trim();
    if (!v) return "";
    if (v === "User" || v === "회원 이름") return "";
    return v;
  }

  function getPlayerContext() {
    const u =
      cleanName(localStorage.getItem("slot_player")) ||
      cleanName(localStorage.getItem("unique_nickname")) ||
      cleanName(localStorage.getItem("nickname")) ||
      "Guest";

    const uid =
      String(localStorage.getItem("unique_userid") || "").trim() ||
      String(localStorage.getItem("uid") || "").trim() ||
      "";

    const ut =
      String(localStorage.getItem("unique_ut") || "").trim() ||
      "";

    return { u, uid, ut };
  }

  // =========================
  // API Calls
  // =========================
  async function checkApi(ctx) {
    // ✅ 워커 구현이 user 파라미터를 쓰고 있으니 user로 기본 호출
    // (혹시 u로 바뀌어도 대비해서 둘 다 넣음)
    const url = buildUrl("/slot/state", { user: ctx.u, u: ctx.u });

    const out = await fetchJson(url);
    if (!out || out.ok !== true) throw new Error(out?.error || "slot/state failed");

    return {
      ok: true,
      bet: Number(out.bet || out.betUT || out.betUt || 10),
      jackpot: Number(out.jackpot || out.jackpotUT || 0),
      ut: (out.ut !== undefined && out.ut !== null) ? Number(out.ut) : undefined,
      freeSpins: Number(out.freeSpins || 0),
      symbols: out.symbols || null,
      version: out.version || "",
      raw: out
    };
  }

  async function spin(ctx) {
    const url = buildUrl("/slot/spin");

    // ✅ 워커 body가 {user}든 {u}든 둘 다 받게 보내줌
    const out = await fetchJson(url, {
      method: "POST",
      body: { user: ctx.u, u: ctx.u },
    });

    if (!out || out.ok !== true) throw new Error(out?.error || "slot/spin failed");

    return {
      ok: true,
      grid: out.grid,
      bet: Number(out.bet ?? out.betUT ?? 0),
      jackpot: Number(out.jackpot ?? out.jackpotUT ?? 0),
      win: Number(out.win ?? out.winUT ?? 0),
      winType: String(out.winType || (Number(out.win || out.winUT || 0) > 0 ? "WIN" : "LOSE")),
      ut: (out.ut !== undefined && out.ut !== null) ? Number(out.ut) : undefined,
      freeSpins: Number(out.freeSpins || 0),
      awardedFreeSpin: Number(out.awardedFreeSpin || 0),
      version: out.version || "",
      raw: out,
    };
  }

  S.api = {
    getApiBase,
    getPlayerContext,
    checkApi,
    spin,
    _debug: { buildUrl, fetchJson }
  };
})(window.SLOT);
