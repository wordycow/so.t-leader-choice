/* games/slot/slot.api.js */
(() => {
  const root = (window.SLOT = window.SLOT || {});
  const api = (root.api = root.api || {});

  // -----------------------------
  // Base URL (Worker)
  // 우선순위:
  // 1) window.SLOT_API_BASE (slot.html에서 주입)
  // 2) localStorage unique_slot_api
  // 3) "" (상대경로 - 보통 안씀)
  // -----------------------------
  function getBase() {
    const w = (window.SLOT_API_BASE || "").trim();
    if (w) return w.replace(/\/+$/, "");
    const ls = (localStorage.getItem("unique_slot_api") || "").trim();
    if (ls) return ls.replace(/\/+$/, "");
    return "";
  }

  // -----------------------------
  // User identity
  // 너 요구사항: "회원가입 시트의 '이름' 기준"
  // 동명이인일 때 '아이디'로 구분
  //
  // 그래서:
  // - nameKeys에서 먼저 이름을 찾고
  // - idKeys에서 아이디를 찾음
  // - URL 파라미터로 들어오면(localStorage에 저장)
  // -----------------------------
  const nameKeys = [
    "unique_user_name",
    "unique_name",
    "unique_realname",
    "unique_display_name",
    "unique_member_name",
    "unique_player_name",
    "unique_join_name",
    "unique_form_name",
    "unique_nickname", // 마지막 fallback (예전값 호환)
  ];
  const idKeys = [
    "unique_user_id",
    "unique_id",
    "unique_member_id",
    "unique_join_id",
    "unique_form_id",
    "unique_login_id",
  ];

  function readUrlParamsOnce() {
    try {
      const qs = new URLSearchParams(location.search);
      const nm = (qs.get("name") || qs.get("user") || "").trim();
      const id = (qs.get("id") || qs.get("uid") || "").trim();
      if (nm) localStorage.setItem("unique_user_name", nm);
      if (id) localStorage.setItem("unique_user_id", id);
    } catch (_) {}
  }

  function pickFirst(keys) {
    for (const k of keys) {
      const v = (localStorage.getItem(k) || "").trim();
      if (v) return v;
    }
    return "";
  }

  function getUserIdentity() {
    readUrlParamsOnce();

    const name = pickFirst(nameKeys);
    const id = pickFirst(idKeys);

    // display는 UI에 보여줄 기본값
    const display = name || id || "Guest";

    return { name, id, display };
  }

  // -----------------------------
  // helpers
  // -----------------------------
  function apiUrl(path) {
    const base = getBase();
    return base ? base + path : path;
  }

  async function fetchJson(url, opts) {
    const res = await fetch(url, opts);
    const ct = (res.headers.get("content-type") || "").toLowerCase();

    // 서버가 에러로 HTML을 뱉으면 여기서 잡아주기(예전 "Unexpected token <" 방지)
    if (!ct.includes("application/json")) {
      const text = await res.text().catch(() => "");
      throw new Error(`non_json_response (${res.status}): ${text.slice(0, 140)}`);
    }

    const data = await res.json();
    return data;
  }

  // -----------------------------
  // public API
  // -----------------------------
  api.getBase = getBase;
  api.getUserIdentity = getUserIdentity;

  // GET /slot/state?user=이름&id=아이디  (워커가 u도 받는다며 → 호환용으로 u도 같이 보냄)
  api.getState = async () => {
    const { name, id } = getUserIdentity();

    // 이름이 없으면(=회원가입 기반 추적 불가) 즉시 에러
    if (!name) return { ok: false, error: "missing_name" };

    const url =
      apiUrl(`/slot/state?user=${encodeURIComponent(name)}`) +
      (id ? `&id=${encodeURIComponent(id)}` : "") +
      `&u=${encodeURIComponent(name)}`; // 호환

    return await fetchJson(url, { method: "GET" });
  };

  // POST /slot/spin  body: { user, id, u, bet }
  api.spin = async (bet) => {
    const { name, id } = getUserIdentity();
    if (!name) return { ok: false, error: "missing_name" };

    const url = apiUrl(`/slot/spin`);
    const body = { user: name, id: id || "", u: name, bet: Number(bet || 0) };

    return await fetchJson(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  };
})();
