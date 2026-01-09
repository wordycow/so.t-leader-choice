// games/slot/slot.api.js
window.SLOT = window.SLOT || {};
(function (S) {
  // ✅ 워커 룰로 통일 (구글시트/code.gs 호출 금지)
  const DEFAULT_API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  function getApiBase() {
    const ls = String(localStorage.getItem("unique_slot_api") || "").trim();
    const c  = String(S.API_BASE || "").trim();
    let base = (ls || c || DEFAULT_API_BASE).trim();
    base = base.replace(/\/+$/, "");
    return base;
  }

  function buildUrl(path, qs) {
    const base = getApiBase();
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

    if (ct.includes("application/json")) {
      const j = await res.json().catch(() => null);
      if (!j) throw new Error(`Invalid JSON response (${res.status})`);
      return j;
    }

    // 404 HTML / 기타 응답이면 원인 노출
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

    // uid/ut는 “표시용/캐시용” (없어도 게임 가능)
    const uid = String(localStorage.getItem("unique_userid") || "").trim();
    const ut  = String(localStorage.getItem("unique_ut") || "").trim();

    return { u, uid, ut };
  }

  // =========================
  // API
  // =========================
  async function state(ctx) {
    // 워커는 user 파라미터를 사용
    const url = buildUrl("/slot/state", { user: ctx.u });
    const out = await fetchJson(url);

    if (!out || out.ok !== true) throw new Error(out?.error || "slot/state failed");

    return {
      betUT: Number(out.betUT ?? 10),
      jackpotUT: Number(out.jackpotUT ?? 0),
      freeSpins: Number(out.freeSpins ?? 0),
      symbols: out.symbols || [],
      version: out.version || ""
    };
  }

  async function spin(ctx) {
    const url = buildUrl("/slot/spin");
    const out = await fetchJson(url, { method: "POST", body: { user: ctx.u } });

    if (!out || out.ok !== true) throw new Error(out?.error || "slot/spin failed");

    return {
      grid: out.grid,
      bet: Number(out.betUT ?? 0),
      jackpot: Number(out.jackpotUT ?? 0),
      win: Number(out.winUT ?? 0),
      usedFreeSpin: !!out.usedFreeSpin,
      freeSpins: Number(out.freeSpins ?? 0),
      awardedFreeSpin: Number(out.awardedFreeSpin ?? 0),
      version: out.version || "",
      raw: out
    };
  }

  async function checkApi(ctx) {
    return await state(ctx);
  }

  S.api = {
    getApiBase,
    getPlayerContext,
    checkApi,
    state,
    spin,
  };
})(window.SLOT);
