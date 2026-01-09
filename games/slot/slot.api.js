// games/slot/slot.api.js
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  // ✅ 여기 1순위: slot.html에서 window.SLOT_API_BASE 로 주입해라
  // 예) <script>window.SLOT_API_BASE="https://xxxx.xxxxx.workers.dev";</script>
  function getApiBase() {
    const fromWindow = String(window.SLOT_API_BASE || "").trim();
    if (fromWindow) return stripSlash(fromWindow);

    const fromLS = String(localStorage.getItem("unique_api_base") || "").trim();
    if (fromLS) return stripSlash(fromLS);

    const meta = document.querySelector('meta[name="unique-api-base"]');
    const fromMeta = String(meta?.content || "").trim();
    if (fromMeta) return stripSlash(fromMeta);

    return ""; // 없으면 에러로 처리
  }

  function setApiBase(base) {
    const b = stripSlash(String(base || "").trim());
    if (b) localStorage.setItem("unique_api_base", b);
  }

  function stripSlash(s) {
    return String(s || "").replace(/\/+$/, "");
  }

  function assertBase() {
    const base = getApiBase();
    if (!base) {
      throw new Error(
        "API_BASE undefined. slot.html에 window.SLOT_API_BASE=\"https://<your-worker>.workers.dev\" 를 먼저 설정해줘."
      );
    }
    return base;
  }

  async function fetchJson(url, opts = {}) {
    const res = await fetch(url, {
      ...opts,
      headers: {
        "Accept": "application/json",
        ...(opts.headers || {}),
      },
    });

    const text = await res.text();

    // ✅ Cloudflare 404/에러는 HTML일 수 있음 → 여기서 친절하게 터뜨림
    const ct = String(res.headers.get("content-type") || "");
    const looksLikeHtml =
      ct.includes("text/html") ||
      text.trim().startsWith("<!DOCTYPE") ||
      text.trim().startsWith("<html");

    if (looksLikeHtml) {
      throw new Error(
        `Server returned HTML (not JSON). API_BASE/경로가 틀렸거나 워커가 아닌 곳을 호출중.\nURL: ${url}\nHTTP: ${res.status}`
      );
    }

    let data;
    try {
      data = JSON.parse(text || "{}");
    } catch (e) {
      throw new Error(`Invalid JSON from server.\nURL: ${url}\nHTTP: ${res.status}\nBODY: ${text.slice(0, 160)}`);
    }

    if (!res.ok) {
      throw new Error(data?.error || `http_${res.status}`);
    }
    return data;
  }

  function getPlayerContext() {
    // ✅ 현재 프로젝트에선 "닉네임(user)" 기준으로 워커가 동작함
    // - localStorage 키는 네가 이미 쓰는 값들 최대한 존중
    const u =
      String(localStorage.getItem("unique_user") || "").trim() ||
      String(localStorage.getItem("unique_nickname") || "").trim() ||
      String(localStorage.getItem("unique_nick") || "").trim() ||
      String(new URL(location.href).searchParams.get("user") || "").trim() ||
      String(new URL(location.href).searchParams.get("u") || "").trim() ||
      "Guest";

    // uid는 화면에 안 보여도 내부적으로 남겨둠(필요하면 나중에 시트 연동에 씀)
    const uid =
      String(localStorage.getItem("unique_uid") || "").trim() ||
      String(new URL(location.href).searchParams.get("uid") || "").trim() ||
      "";

    // UT는 당장은 로컬 캐시(나중에 시트/서버 연동 가능)
    const ut = Number(localStorage.getItem("unique_ut") || "0") || 0;

    return { u, uid, ut };
  }

  async function state(ctx) {
    const base = assertBase();
    const user = encodeURIComponent(String(ctx?.u || "").trim());
    const url = `${base}/slot/state?user=${user}`;
    const out = await fetchJson(url, { method: "GET" });

    if (!out?.ok) throw new Error(out?.error || "state_failed");

    return {
      bet: Number(out.betUT || 0),
      jackpot: Number(out.jackpotUT || 0),
      freeSpins: Number(out.freeSpins || 0),
      symbols: out.symbols || [],
      version: out.version || "",
      // owner면 houseProfitUT가 내려올 수 있음
      houseProfitUT: out.houseProfitUT,
    };
  }

  async function checkApi(ctx) {
    // 부팅 시 한 번 상태 확인용
    const st = await state(ctx);
    return st;
  }

  async function spin(ctx) {
    const base = assertBase();
    const user = String(ctx?.u || "").trim();
    if (!user) throw new Error("missing_user");

    const url = `${base}/slot/spin`;
    const out = await fetchJson(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ user }),
    });

    if (!out?.ok) throw new Error(out?.error || "spin_failed");

    const grid = out.grid;
    const bet = Number(out.betUT || 0);
    const win = Number(out.winUT || 0);
    const jackpot = Number(out.jackpotUT || 0);

    // winType 프론트 연출용으로 만들어줌
    let winType = "NORMAL";
    const mid = (grid && grid[1]) ? grid[1].slice(1, 4) : [];
    const isPro10Mid3 = mid.length === 3 && mid.every(x => x === "pro10");
    if (win > 0 && isPro10Mid3) winType = "JACKPOT";
    else if (win > 0) winType = "WIN";
    else winType = "LOSE";

    // ✅ 프론트(slot.app.js)가 기대하는 키로 맞춰서 반환
    return {
      ok: true,
      grid,
      bet,
      jackpot,
      win,
      winType,

      // 부가정보(필요하면 UI에 표시 가능)
      usedFreeSpin: !!out.usedFreeSpin,
      freeSpins: Number(out.freeSpins || 0),
      awardedFreeSpin: Number(out.awardedFreeSpin || 0),
      version: out.version || "",
      houseProfitUT: out.houseProfitUT,

      // ut는 아직 서버에서 관리 안하면 로컬 유지(연동은 다음 단계에서)
      ut: Number(ctx?.ut || 0),
    };
  }

  S.api = {
    getApiBase,
    setApiBase,
    getPlayerContext,
    checkApi,
    state,
    spin,
  };
})(window.SLOT);
