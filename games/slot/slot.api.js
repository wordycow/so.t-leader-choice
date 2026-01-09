// games/slot/slot.api.js
window.SLOT = window.SLOT || {};
(function (S) {
  // =========================
  // API BASE (Workers only)
  // =========================
  // ✅ 여기에 워커 주소를 넣거나,
  // ✅ localStorage에 아래 키로 저장해두면 자동으로 씀:
  // localStorage.setItem("unique_slot_api", "https://YOUR-WORKER.yourdomain.workers.dev");
  const DEFAULT_API_BASE = ""; // 비워두는 게 안전(상대경로로 GitHub Pages를 치면 또 터짐)

  function getApiBase() {
    const ls = String(localStorage.getItem("unique_slot_api") || "").trim();
    const w = String(window.SLOT_API_BASE || "").trim();
    const c = String(S.API_BASE || "").trim(); // 혹시 다른 모듈에서 주입했을 때
    let base = ls || w || c || DEFAULT_API_BASE;

    base = String(base || "").trim();
    if (!base) return "";
    // 끝 슬래시 제거
    base = base.replace(/\/+$/, "");
    return base;
  }

  function buildUrl(path, qs) {
    const base = getApiBase();
    if (!base) throw new Error("SLOT API BASE missing. Set localStorage.unique_slot_api to your Worker URL.");
    const u = new URL(base + path);
    if (qs && typeof qs === "object") {
      Object.entries(qs).forEach(([k, v]) => {
        if (v === undefined || v === null) return;
        u.searchParams.set(k, String(v));
      });
    }
    return u.toString();
  }

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      method: options.method || "GET",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const ct = String(res.headers.get("content-type") || "");
    // JSON이면 바로 파싱
    if (ct.includes("application/json")) {
      const j = await res.json().catch(() => null);
      if (!j) throw new Error(`Invalid JSON response (${res.status})`);
      return j;
    }

    // JSON이 아니면(404 html 등) 텍스트로 이유 보여주기
    const text = await res.text().catch(() => "");
    const snippet = String(text || "").slice(0, 180).replace(/\s+/g, " ");
    throw new Error(`Non-JSON response (${res.status}): ${snippet}`);
  }

  // =========================
  // Player Context
  // =========================
  function getPlayerContext() {
    // 닉네임 키 후보들(프로젝트마다 다를 수 있어서 넓게 잡음)
    const nick =
      String(localStorage.getItem("unique_nick") || "").trim() ||
      String(localStorage.getItem("unique_nickname") || "").trim() ||
      String(localStorage.getItem("unique_user") || "").trim() ||
      String(localStorage.getItem("nickname") || "").trim() ||
      String(localStorage.getItem("user") || "").trim() ||
      "Guest";

    const uid =
      String(localStorage.getItem("unique_uid") || "").trim() ||
      String(localStorage.getItem("unique_id") || "").trim() ||
      String(localStorage.getItem("uid") || "").trim() ||
      "";

    return { u: nick, uid };
  }

  // =========================
  // API Calls
  // =========================
  async function checkApi(ctx) {
    // 워커는 u 또는 user 둘 다 받을 수 있게 해둔 상태라,
    // 여기선 u로 통일
    const url = buildUrl("/slot/state", { u: ctx.u });
    const out = await fetchJson(url);

    if (!out || out.ok !== true) {
      throw new Error(out?.error || "slot/state failed");
    }

    // slot.app.js가 기대하는 형태로 normalize
    return {
      ok: true,
      bet: Number(out.bet || out.betUT || out.betUt || 10),
      jackpot: Number(out.jackpot || out.jackpotUT || 0),
      ut: Number(out.ut ?? out.balance ?? null),
      freeSpins: Number(out.freeSpins || 0),
      symbols: out.symbols || null,
      version: out.version || "",
    };
  }

  async function spin(ctx) {
    const url = buildUrl("/slot/spin");
    const out = await fetchJson(url, {
      method: "POST",
      body: { u: ctx.u }, // ✅ 워커 룰 통일
    });

    if (!out || out.ok !== true) {
      throw new Error(out?.error || "slot/spin failed");
    }

    // slot.app.js가 쓰는 키로 맞춰서 반환
    return {
      ok: true,
      grid: out.grid,
      bet: Number(out.betCharged ?? out.bet ?? 0),
      jackpot: Number(out.jackpot ?? out.jackpotUT ?? 0),
      win: Number(out.win ?? out.winUT ?? 0),
      winType: String(out.winType || (Number(out.win || 0) > 0 ? "WIN" : "LOSE")),
      ut: (out.ut !== undefined && out.ut !== null) ? Number(out.ut) : undefined,
      freeSpins: Number(out.freeSpins || 0),
      awardedFreeSpin: Number(out.awardedFreeSpin || 0),
      version: out.version || "",
      raw: out,
    };
  }

  // =========================
  // Public API
  // =========================
  S.api = {
    getApiBase,
    getPlayerContext,
    checkApi,
    spin,

    // 디버그 편의
    _debug: {
      buildUrl,
      fetchJson
    }
  };
})(window.SLOT);
