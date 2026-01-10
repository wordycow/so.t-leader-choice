/* games/slot/slot.api.js */
(() => {
  const root = (window.SLOT = window.SLOT || {});
  const api = (root.api = root.api || {});

  const LS_API = "unique_slot_api";

  function stripSlash(s){ return String(s || "").replace(/\/+$/,""); }

  function getBase(){
    const fromWindow = (window.SLOT_API_BASE || "").trim();
    if(fromWindow) return stripSlash(fromWindow);

    const fromLS = (localStorage.getItem(LS_API) || "").trim();
    if(fromLS) return stripSlash(fromLS);

    return ""; // empty => 상대경로 호출(권장X)
  }

  function setBase(url){
    const v = String(url || "").trim();
    if(!v) localStorage.removeItem(LS_API);
    else localStorage.setItem(LS_API, v);
    return getBase();
  }

  function qp(name){
    try{
      const u = new URL(location.href);
      return (u.searchParams.get(name) || "").trim();
    }catch(_){ return ""; }
  }

  // ✅ 유저 식별: "이름" 우선, 동명이인일 때 "아이디" 추가
  // - name: 구글시트 '이름'
  // - id:   구글시트 '아이디'
  // - fallback: 기존 닉네임/유저키(u)
  function getUserIdentity(){
    const name =
      qp("name") ||
      (localStorage.getItem("unique_name") || "").trim() ||
      (localStorage.getItem("unique_realname") || "").trim() ||
      (localStorage.getItem("unique_display_name") || "").trim() ||
      (localStorage.getItem("unique_displayName") || "").trim() ||
      "";

    const id =
      qp("id") ||
      (localStorage.getItem("unique_id") || "").trim() ||
      (localStorage.getItem("unique_user_id") || "").trim() ||
      (localStorage.getItem("unique_userid") || "").trim() ||
      (localStorage.getItem("unique_login_id") || "").trim() ||
      "";

    const u =
      qp("u") ||
      qp("user") ||
      (localStorage.getItem("unique_nickname") || "").trim() ||
      (localStorage.getItem("unique_nick") || "").trim() ||
      (localStorage.getItem("unique_user") || "").trim() ||
      "";

    return { name, id, u };
  }

  function buildStateUrl(){
    const base = getBase();
    const { name, id, u } = getUserIdentity();
    const url = new URL((base ? base : location.origin) + "/slot/state");

    // ✅ name/id 방식 우선
    if(name) url.searchParams.set("name", name);
    if(id) url.searchParams.set("id", id);

    // ✅ worker가 아직 name/id를 안 받으면 u로도 같이 보내서 호환성 확보
    if(u) url.searchParams.set("u", u);

    // base가 비어있는 경우(상대경로)라면 origin 붙인 URL이 필요하니 그대로 반환
    return (base ? (base + "/slot/state" + "?" + url.searchParams.toString()) : ("/slot/state?" + url.searchParams.toString()));
  }

  function buildSpinUrl(){
    const base = getBase();
    return base ? (base + "/slot/spin") : "/slot/spin";
  }

  async function safeJson(res){
    const text = await res.text();
    try{
      return JSON.parse(text);
    }catch(e){
      const head = text.slice(0, 180);
      throw new Error(`non_json_response: ${res.status} ${head}`);
    }
  }

  function withTimeout(ms){
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), ms);
    return { ctrl, done: () => clearTimeout(t) };
  }

  async function state(){
    const url = buildStateUrl();
    const { ctrl, done } = withTimeout(12000);
    try{
      const res = await fetch(url, { method:"GET", signal: ctrl.signal });
      return await safeJson(res);
    } finally { done(); }
  }

  async function spin({ bet }){
    const url = buildSpinUrl();
    const { name, id, u } = getUserIdentity();

    const body = {
      bet: Number(bet || 0),
      // ✅ name/id 기반
      name: name || "",
      id: id || "",
      // ✅ 기존 호환
      u: u || "",
      user: u || ""
    };

    const { ctrl, done } = withTimeout(12000);
    try{
      const res = await fetch(url, {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify(body),
        signal: ctrl.signal
      });
      return await safeJson(res);
    } finally { done(); }
  }

  api.getBase = getBase;
  api.setBase = setBase;
  api.getUserIdentity = getUserIdentity;
  api.state = state;
  api.spin = spin;
})();
