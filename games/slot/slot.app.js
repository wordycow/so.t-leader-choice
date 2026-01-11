/* games/slot/slot.app.js */
(function () {
  "use strict";

  window.SLOT = window.SLOT || {};
  const S = window.SLOT;

  // =========================
  // Config / Storage (login 유지)
  // =========================
  const STORAGE_FIXED_KEY = "THE_UNIQUE_LOGIN"; // ✅ slot이 무조건 찾고/저장하는 고정 키
  const FALLBACK_SCAN_LIMIT = 80;

  function getUConfig_() {
    // unique.config.js가 어떤 형태든 최대한 잡는다
    const U = window.U || window.UNIQUE || {};
    const cfg =
      (U && U.CONFIG) ||
      window.UNIQUE_CONFIG ||
      window.CONFIG ||
      {};
    return cfg || {};
  }

  function getGoogleScriptUrl_() {
    const cfg = getUConfig_();
    const url = String(cfg.GOOGLE_SCRIPT_URL || cfg.GSCRIPT_URL || "").trim();
    return url;
  }

  function loadUserFromSomewhere_() {
    // 1) URL ?id=
    const url = new URL(location.href);
    const idQ = (url.searchParams.get("id") || "").trim();
    const nameQ = (url.searchParams.get("name") || "").trim();
    const nickQ = (url.searchParams.get("nickname") || url.searchParams.get("nick") || "").trim();
    if (idQ) {
      const u = { id: idQ.toLowerCase(), name: nameQ, nickname: nickQ };
      persistUser_(u);
      return u;
    }

    // 2) 고정키
    const fixed = safeParse_(localStorage.getItem(STORAGE_FIXED_KEY));
    if (fixed && fixed.id) return fixed;

    // 3) 흔한 키들
    const candidates = [
      "unique_user",
      "UNIQUE_USER",
      "UniqueUser",
      "the_unique_user",
      "THE_UNIQUE_USER",
      "auth_user",
      "AUTH_USER",
      "login",
      "LOGIN",
      "user",
      "USER",
      "U_USER",
      "U.AUTH",
      "U_AUTH",
    ];
    for (const k of candidates) {
      const v = safeParse_(localStorage.getItem(k)) || safeParse_(sessionStorage.getItem(k));
      if (v && v.id) {
        persistUser_(v);
        return v;
      }
    }

    // 4) 마지막 수단: localStorage 전체 스캔 (id/name/nickname 같은 형태를 찾아냄)
    let found = null;
    let scanned = 0;
    for (let i = localStorage.length - 1; i >= 0; i--) {
      if (scanned++ > FALLBACK_SCAN_LIMIT) break;
      const k = localStorage.key(i);
      if (!k) continue;
      const raw = localStorage.getItem(k);
      const obj = safeParse_(raw);
      if (obj && obj.id && (obj.name || obj.nickname || obj.nick)) {
        found = obj;
        break;
      }
    }
    if (found) {
      persistUser_(found);
      return found;
    }

    return null;
  }

  function persistUser_(u) {
    if (!u || !u.id) return;
    const obj = {
      id: String(u.id).trim().toLowerCase(),
      name: String(u.name || "").trim(),
      nickname: String(u.nickname || u.nick || "").trim(),
    };
    localStorage.setItem(STORAGE_FIXED_KEY, JSON.stringify(obj));
  }

  function safeParse_(s) {
    if (!s) return null;
    const str = String(s);
    try {
      const o = JSON.parse(str);
      if (o && typeof o === "object") return o;
    } catch (_) {}
    return null;
  }

  // =========================
  // JSONP (구글 Apps Script 전용)
  // =========================
  function jsonp_(baseUrl, params, opts) {
    const timeout = (opts && opts.timeout) || 12000;

    return new Promise((resolve, reject) => {
      const cb = "__slotcb_" + Math.random().toString(36).slice(2);
      const u = new URL(baseUrl, location.href);

      Object.entries(params || {}).forEach(([k, v]) => u.searchParams.set(k, String(v)));
      u.searchParams.set("callback", cb);
      u.searchParams.set("_", String(Date.now()));

      const script = document.createElement("script");
      script.async = true;
      script.src = u.toString();

      let done = false;
      const timer = setTimeout(() => {
        if (done) return;
        done = true;
        cleanup_();
        reject(new Error("jsonp timeout"));
      }, timeout);

      function cleanup_() {
        try { clearTimeout(timer); } catch (_) {}
        try { delete window[cb]; } catch (_) { window[cb] = undefined; }
        try { script.remove(); } catch (_) {}
      }

      window[cb] = (data) => {
        if (done) return;
        done = true;
        cleanup_();
        resolve(data);
      };

      script.onerror = () => {
        if (done) return;
        done = true;
        cleanup_();
        reject(new Error("jsonp network error"));
      };

      document.head.appendChild(script);
    });
  }

  // =========================
  // UI helpers (S.ui 같은 의존성 제거)
  // =========================
  function setText_(selectors, text) {
    const list = Array.isArray(selectors) ? selectors : [selectors];
    for (const sel of list) {
      const el = typeof sel === "string" ? document.querySelector(sel) : sel;
      if (el) {
        el.textContent = text;
        return true;
      }
    }
    return false;
  }

  function findEl_(selectors) {
    const list = Array.isArray(selectors) ? selectors : [selectors];
    for (const sel of list) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

  function animateNumber_(el, from, to, ms) {
    if (!el) return;
    const start = performance.now();
    const dur = Math.max(200, ms || 900);
    const a = Number(from) || 0;
    const b = Number(to) || 0;

    function step(now) {
      const t = Math.min(1, (now - start) / dur);
      const v = a + (b - a) * (1 - Math.pow(1 - t, 3));
      el.textContent = fmt2_(v);
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function toast_(msg) {
    console.log("[SLOT]", msg);
    const host = document.body;
    const t = document.createElement("div");
    t.textContent = msg;
    t.style.position = "fixed";
    t.style.left = "50%";
    t.style.bottom = "18px";
    t.style.transform = "translateX(-50%)";
    t.style.padding = "10px 14px";
    t.style.borderRadius = "14px";
    t.style.background = "rgba(2,6,23,0.86)";
    t.style.border = "1px solid rgba(255,255,255,0.12)";
    t.style.color = "#e5e7eb";
    t.style.zIndex = "99999";
    t.style.backdropFilter = "blur(10px)";
    host.appendChild(t);
    setTimeout(() => t.remove(), 2200);
  }

  // ✅ 잭팟 티커(자정까지 유지)
  function setJackpotTicker_(name) {
    const msg = `${name}님이 잭팟이 터지셨습니다. 축하드립니다.`;
    const exp = endOfTodayMs_();
    localStorage.setItem("SLOT_JACKPOT_TICKER", JSON.stringify({ msg, exp }));
    showJackpotTickerIfAny_();
  }

  function showJackpotTickerIfAny_() {
    const raw = localStorage.getItem("SLOT_JACKPOT_TICKER");
    const obj = safeParse_(raw);
    if (!obj || !obj.msg || !obj.exp) return;

    if (Date.now() > Number(obj.exp)) {
      localStorage.removeItem("SLOT_JACKPOT_TICKER");
      return;
    }

    let bar = document.getElementById("slotJackpotTicker");
    if (!bar) {
      bar = document.createElement("div");
      bar.id = "slotJackpotTicker";
      bar.style.position = "fixed";
      bar.style.top = "0";
      bar.style.left = "0";
      bar.style.right = "0";
      bar.style.height = "42px";
      bar.style.zIndex = "99998";
      bar.style.background = "rgba(2,6,23,0.75)";
      bar.style.borderBottom = "1px solid rgba(255,255,255,0.12)";
      bar.style.backdropFilter = "blur(10px)";
      bar.style.overflow = "hidden";
      bar.style.display = "flex";
      bar.style.alignItems = "center";

      const inner = document.createElement("div");
      inner.id = "slotJackpotTickerInner";
      inner.style.whiteSpace = "nowrap";
      inner.style.willChange = "transform";
      inner.style.color = "#fbbf24";
      inner.style.fontWeight = "800";
      inner.style.letterSpacing = "0.5px";
      inner.style.paddingLeft = "100%";
      inner.style.animation = "slotTicker 12s linear infinite";
      inner.textContent = obj.msg;

      const style = document.createElement("style");
      style.textContent = `
        @keyframes slotTicker {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-120%); }
        }
        body { padding-top: 42px; }
      `;
      bar.appendChild(style);
      bar.appendChild(inner);
      document.body.appendChild(bar);
    } else {
      const inner = document.getElementById("slotJackpotTickerInner");
      if (inner) inner.textContent = obj.msg;
    }
  }

  function endOfTodayMs_() {
    const d = new Date();
    d.setHours(23, 59, 59, 999);
    return d.getTime();
  }

  // =========================
  // App
  // =========================
  let cfg = null;
  let user = null;
  let balance = 0;
  let bet = 10;
  const BET_STEP = 5; // ✅ 유송: 5단위 고정
  let busy = false;

  async function init_() {
    showJackpotTickerIfAny_();

    user = loadUserFromSomewhere_();
    if (!user || !user.id) {
      toast_("로그인 정보(id)를 못 찾았어. gate에서 로그인 후 다시 들어와줘.");
      // 그래도 화면은 살아있게
    }

    // UI elements (여러 후보를 다 지원)
    const elPlayer = findEl_([
      "#playerName", "#slotPlayer", "[data-slot-player]", ".js-player", ".player-value"
    ]);
    const elWallet = findEl_([
      "#walletValue", "#slotWallet", "[data-slot-wallet]", ".js-wallet", ".wallet-value"
    ]);
    const elJackpot = findEl_([
      "#jackpotValue", "#slotJackpot", "[data-slot-jackpot]"
    ]);
    const elLast = findEl_([
      "#lastResult", "#slotLastResult", "[data-slot-last]"
    ]);
    const elBet = findEl_([
      "#betValue", "#slotBet", "[data-slot-bet]"
    ]);

    const btnSpin = findEl_([
      "#btnSpin", "#spinBtn", "[data-slot-spin]"
    ]);
    const btnAuto = findEl_([
      "#btnAuto", "#autoBtn", "[data-slot-auto]"
    ]);
    const btnMinus = findEl_([
      "#betMinus", "#btnBetMinus", "[data-slot-bet-minus]"
    ]);
    const btnPlus = findEl_([
      "#betPlus", "#btnBetPlus", "[data-slot-bet-plus]"
    ]);
    const btnSound = findEl_([
      "#btnSound", "#soundBtn", "[data-slot-sound]"
    ]);

    // initial UI
    if (elPlayer) elPlayer.textContent = displayName_(user);
    if (elLast) elLast.textContent = "READY";
    if (elBet) elBet.textContent = String(bet);

    // mount slot grid
    if (S.game && S.game.ensureMounted) S.game.ensureMounted();

    // load config from Apps Script
    const gs = getGoogleScriptUrl_();
    if (!gs) {
      toast_("GOOGLE_SCRIPT_URL이 비었어. unique.config.js에 Apps Script /exec URL 넣어줘.");
    } else {
      try {
        const res = await jsonp_(gs, { action: "getConfig" }, { timeout: 12000 });
        if (res && res.ok && res.config) {
          cfg = res.config;
          if (S.game && S.game.setConfig) S.game.setConfig(cfg);
        }
      } catch (e) {
        console.error(e);
        toast_("Config 불러오기 실패(구글 스크립트). 배포 URL / 권한 확인 필요.");
      }
    }

    // fetch slot state (user + totals)
    if (gs && user && user.id) {
      try {
        const st = await jsonp_(gs, { action: "getSlotState", id: user.id }, { timeout: 12000 });
        if (st && st.ok && st.user) {
          user = Object.assign({}, user, st.user);
          persistUser_(user);

          balance = Number(st.user.balance || 0);
          if (elWallet) elWallet.textContent = fmt2_(balance);

          if (elPlayer) elPlayer.textContent = displayName_(user);
          if (elJackpot && Number.isFinite(Number(st.jackpotTotal))) {
            elJackpot.textContent = fmt2_(st.jackpotTotal);
          }
        }
      } catch (e) {
        console.error(e);
        toast_("getSlotState 실패: Apps Script 응답/권한 확인");
      }
    }

    // bet min/max (cfg 있으면 반영, 없으면 기본)
    const betMin = cfg ? num_(cfg.SLOT_BET_MIN, 10) : 10;
    const betMax = cfg ? num_(cfg.SLOT_BET_MAX, 1000) : 1000;
    bet = clamp_(bet, betMin, betMax);
    if (elBet) elBet.textContent = String(bet);

    // bind buttons
    if (btnMinus) btnMinus.onclick = () => {
      if (busy) return;
      bet = clamp_(bet - BET_STEP, betMin, betMax);
      if (elBet) elBet.textContent = String(bet);
    };

    if (btnPlus) btnPlus.onclick = () => {
      if (busy) return;
      bet = clamp_(bet + BET_STEP, betMin, betMax);
      if (elBet) elBet.textContent = String(bet);
    };

    let autoOn = false;
    let autoTimer = null;

    function setAuto_(on) {
      autoOn = !!on;
      if (btnAuto) btnAuto.textContent = autoOn ? "AUTO ON" : "AUTO OFF";
      if (!autoOn && autoTimer) {
        clearTimeout(autoTimer);
        autoTimer = null;
      }
    }

    if (btnAuto) {
      btnAuto.onclick = () => {
        if (busy) return;
        setAuto_(!autoOn);
        if (autoOn) loopAuto_();
      };
    }

    if (btnSound) {
      let soundOn = true;
      btnSound.textContent = "SOUND ON";
      btnSound.onclick = () => {
        soundOn = !soundOn;
        btnSound.textContent = soundOn ? "SOUND ON" : "SOUND OFF";
        if (S.game && S.game.setSound) S.game.setSound(soundOn);
      };
    }

    async function loopAuto_() {
      if (!autoOn) return;
      await doSpin_();
      autoTimer = setTimeout(loopAuto_, 650);
    }

    async function doSpin_() {
      const gs2 = getGoogleScriptUrl_();

      if (busy) return;
      if (!user || !user.id) {
        toast_("로그인(id) 없음. gate에서 로그인 후 다시.");
        return;
      }
      if (balance < bet) {
        toast_("UT 잔액 부족");
        return;
      }
      if (!S.game || !S.game.spin) {
        toast_("slot.game이 로드되지 않았어(스크립트 순서 확인)");
        return;
      }

      busy = true;
      try {
        if (btnSpin) btnSpin.disabled = true;

        const before = balance;
        const res = await S.game.spin({ bet });

        // UI result (즉시)
        if (elLast) elLast.textContent = res.resultText || "READY";

        // ✅ 서버(구글시트) 커밋
        const netDelta = Number(res.netDelta || 0);
        const lossAmount = Number(res.lossAmount || 0);

        if (gs2) {
          const commit = await jsonp_(gs2, {
            action: "slotCommit",
            id: user.id,
            netDelta: String(netDelta),
            lossAmount: String(lossAmount),
          }, { timeout: 12000 });

          if (commit && commit.ok && commit.user) {
            balance = Number(commit.user.balance || 0);
            if (elWallet) animateNumber_(elWallet, before, balance, res.jackpot ? 2200 : 1100);

            // jackpot/casino totals
            if (elJackpot && Number.isFinite(Number(commit.jackpotTotal))) {
              elJackpot.textContent = fmt2_(commit.jackpotTotal);
            }

            // ✅ 잭팟 티커(자정까지)
            if (res.jackpot) {
              setJackpotTicker_(displayName_(user));
              showWinOverlay_("JACKPOT!", `+${fmt2_(Math.max(0, netDelta))} UT`, 3500);
            } else if (netDelta > 0) {
              showWinOverlay_("WIN!", `+${fmt2_(netDelta)} UT`, 1400);
            } else if (netDelta === 0) {
              showWinOverlay_("EVEN!", `+0 UT`, 900);
            }
          } else {
            toast_("slotCommit 실패(구글시트 반영 안 됨)");
          }
        } else {
          toast_("GOOGLE_SCRIPT_URL 없음(구글시트 반영 불가)");
        }
      } catch (e) {
        console.error(e);
        toast_("스핀 오류: 콘솔 확인");
      } finally {
        busy = false;
        if (btnSpin) btnSpin.disabled = false;
      }
    }

    if (btnSpin) btnSpin.onclick = doSpin_;
  }

  function showWinOverlay_(title, sub, ms) {
    const wrap = document.createElement("div");
    wrap.style.position = "fixed";
    wrap.style.inset = "0";
    wrap.style.display = "grid";
    wrap.style.placeItems = "center";
    wrap.style.zIndex = "99997";
    wrap.style.pointerEvents = "none";
    wrap.style.background = "radial-gradient(circle at center, rgba(0,0,0,0.20), rgba(0,0,0,0.55))";

    const box = document.createElement("div");
    box.style.padding = "22px 26px";
    box.style.borderRadius = "22px";
    box.style.background = "rgba(2,6,23,0.75)";
    box.style.border = "1px solid rgba(255,255,255,0.14)";
    box.style.backdropFilter = "blur(12px)";
    box.style.textAlign = "center";
    box.style.transform = "translateY(8px) scale(0.98)";
    box.style.animation = "slotPop 220ms ease-out forwards";

    const h = document.createElement("div");
    h.textContent = title;
    h.style.fontSize = "34px";
    h.style.fontWeight = "900";
    h.style.letterSpacing = "1px";
    h.style.color = "#fbbf24";

    const p = document.createElement("div");
    p.textContent = sub;
    p.style.marginTop = "6px";
    p.style.fontSize = "18px";
    p.style.fontWeight = "800";
    p.style.color = "#e5e7eb";

    const style = document.createElement("style");
    style.textContent = `
      @keyframes slotPop {
        from { opacity: 0; transform: translateY(10px) scale(0.96); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
      }
    `;
    box.appendChild(style);
    box.appendChild(h);
    box.appendChild(p);
    wrap.appendChild(box);
    document.body.appendChild(wrap);

    setTimeout(() => wrap.remove(), Math.max(600, ms || 1200));
  }

  function displayName_(u) {
    const nick = String((u && (u.nickname || u.nick)) || "").trim();
    const name = String((u && u.name) || "").trim();
    // ✅ “슬래시 느낌 제거” (표시용)
    const d = (nick || name || "-").replaceAll("/", " ").trim();
    return d || "-";
  }

  function fmt2_(n) {
    const x = Number(n) || 0;
    return x % 1 === 0 ? String(x) : x.toFixed(2);
  }

  function num_(v, d) {
    const n = Number(v);
    return Number.isFinite(n) ? n : d;
  }

  function clamp_(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  // =========================
  // Boot
  // =========================
  document.addEventListener("DOMContentLoaded", init_);
})();
