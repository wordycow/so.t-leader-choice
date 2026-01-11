/* games/slot/slot.app.js */
(() => {
  window.SLOT = window.SLOT || {};
  const S = window.SLOT;

  const $ = (id) => document.getElementById(id);

  // 버튼/표시 요소 (있으면 자동 연결)
  const el = {
    spinBtn:
      $("spinBtn") ||
      $("spinButton") ||
      $("btnSpin") ||
      $("spin"),

    autoBtn:
      $("autoBtn") ||
      $("autoButton") ||
      $("btnAuto"),

    autoText:
      $("autoText") ||
      $("autoLabel"),

    betMinus:
      $("betMinus") ||
      $("btnBetMinus") ||
      $("minus5"),

    betPlus:
      $("betPlus") ||
      $("btnBetPlus") ||
      $("plus5"),

    betVal:
      $("betVal") || $("betValue"),
  };

  let booted = false;
  let autoOn = false;
  let spinning = false;

  // UI에서 조절되는 베팅값(서버가 아직 고정 bet이면 표시만 바뀜)
  let betUi = 10;
  let betMin = 10;
  let betMax = 1000;
  let betStep = 5;

  function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }
  function asInt(v, def = 0) {
    const n = Math.floor(Number(v));
    return Number.isFinite(n) ? n : def;
  }

  function setAuto(on) {
    autoOn = !!on;
    if (el.autoText) el.autoText.textContent = autoOn ? "AUTO ON" : "AUTO OFF";
  }

  function setBetUi(v) {
    betUi = clamp(asInt(v, betUi), betMin, betMax);
    if (el.betVal) el.betVal.textContent = String(betUi);
    // slot.ui.js의 KPI bet도 같이 갱신(있으면)
    if (S.ui?.setKpi) S.ui.setKpi({ bet: betUi });
  }

  function derivePaytableFromSymbols(symbols) {
    // ui.buildPaytable()가 기대하는 형태:
    // [{ id, name, pays: ["2x ...", "3x ..."] }]
    // 기존 slot.config.js에 PAYTABLE이 있으면 그걸 쓰고, 없을 때만 대체 생성
    const nameMap = {
      star1: "STAR1",
      star2: "STAR2",
      star3: "STAR3",
      pro1: "PRO1",
      pro2: "PRO2",
      pro3: "PRO3",
      pro4: "PRO4",
      pro5: "PRO5",
      pro6: "PRO6",
      pro7: "PRO7",
      pro8: "PRO8",
      pro9: "PRO9",
      pro10: "PRO10",
    };

    if (!Array.isArray(symbols) || !symbols.length) return [];

    return symbols.map(s => {
      const id = String(s.id || "");
      const payout = Number(s.payout || 0);
      // 지금 워커 로직은 "3개 맞으면 payout * bet" 구조라서 간단히 표기
      return {
        id,
        name: nameMap[id] || id,
        pays: payout ? [`3매치: x${payout}`] : ["-"],
      };
    });
  }

  async function syncState() {
    if (!S.api?.state) throw new Error("SLOT.api.state missing");
    if (!S.ui?.setOnline || !S.ui?.setPlayer) throw new Error("SLOT.ui missing");

    S.ui.setLog?.("SYNC…");

    const st = await S.api.state(); // ✅ /slot/state

    // 온라인 표시
    S.ui.setOnline(true);

    // ✅ 이름/UT 매핑 핵심
    const displayName =
      st?.identity?.name ||
      st?.identity?.nickname ||
      st?.identity?.id ||
      st?.identity?.u ||
      st?.u ||
      "Guest";

    const nickname =
      st?.identity?.nickname ||
      st?.identity?.u ||
      st?.u ||
      "";

    S.ui.setPlayer({
      displayName,
      u: nickname,
      ut: st?.ut ?? 0,
    });

    // 잭팟/베팅 KPI
    // 서버 bet이 있으면 그걸 기본으로 UI bet를 맞춰주되,
    // 유송이 원하는 "±5" UX를 위해 betStep은 5로 유지
    const serverBet = asInt(st?.bet, betUi);
    setBetUi(serverBet);

    if (S.ui?.setKpi) {
      S.ui.setKpi({
        bet: betUi,
        jackpot: st?.jackpot ?? 0,
        win: 0,
      });
    }

    // 페이테이블 (없으면 symbols로 생성)
    if (!Array.isArray(S.PAYTABLE) || S.PAYTABLE.length === 0) {
      S.PAYTABLE = derivePaytableFromSymbols(st?.symbols || []);
    }
    S.ui.buildPaytable?.();

    S.ui.setLog?.("READY");

    return st;
  }

  async function doSpinOnce() {
    if (spinning) return;
    spinning = true;

    try {
      S.ui.setLog?.("SPIN…");

      // ✅ /slot/spin
      // (현재 vault worker는 bet을 고정값으로 쓰고 있어서,
      //  다음 단계에서 worker가 bet을 받도록 바꾸면 UI bet이 실제 반영됨)
      const res = await S.api.spin({ bet: betUi });

      // 온라인 표시
      S.ui.setOnline(true);

      if (!res?.ok) {
        S.ui.setLog?.(res?.error ? `ERROR: ${res.error}` : "ERROR");
        // 잔액은 응답에 있을 수도 있음
        if (res?.ut !== undefined) {
          S.ui.setPlayer({ displayName: "", u: "", ut: res.ut });
        }
        return;
      }

      // ✅ 스핀 결과 반영 (이름/UT)
      const displayName =
        res?.identity?.name ||
        res?.identity?.nickname ||
        res?.identity?.id ||
        "Guest";

      const nickname =
        res?.identity?.nickname ||
        "";

      S.ui.setPlayer({
        displayName,
        u: nickname,
        ut: res?.ut ?? 0,
      });

      S.ui.setKpi?.({
        bet: betUi,
        jackpot: res?.jackpot ?? 0,
        win: res?.win ?? 0,
      });

      // 간단 로그
      const wt = res?.winType || "";
      const net = res?.net ?? 0;
      S.ui.setLog?.(`${wt}  (NET: ${net})`);

      // TODO(다음 단계): 잭팟/대승 애니메이션 + 숫자 카운트업(1분30초)
      // 여기서 winType === "JACKPOT" 일 때 연출 길게 타면 됨.

    } catch (e) {
      S.ui.setOnline(false);
      S.ui.setLog?.(`SYNC FAILED: ${String(e?.message || e)}`);
    } finally {
      spinning = false;
    }
  }

  function bind() {
    // 베팅 -/+
    if (el.betMinus) {
      el.betMinus.addEventListener("click", () => setBetUi(betUi - betStep));
    }
    if (el.betPlus) {
      el.betPlus.addEventListener("click", () => setBetUi(betUi + betStep));
    }

    // 스핀
    if (el.spinBtn) {
      el.spinBtn.addEventListener("click", async () => {
        setAuto(false);
        await doSpinOnce();
      });
    }

    // 오토
    if (el.autoBtn) {
      el.autoBtn.addEventListener("click", () => setAuto(!autoOn));
    }

    // 오토 루프(가볍게)
    setInterval(async () => {
      if (!autoOn) return;
      if (spinning) return;
      await doSpinOnce();
    }, 1200);
  }

  async function boot() {
    if (booted) return;
    booted = true;

    // 기본값
    setAuto(false);
    setBetUi(betUi);

    bind();

    // 첫 동기화
    try {
      await syncState();
    } catch (e) {
      S.ui?.setOnline?.(false);
      S.ui?.setLog?.(`SYNC FAILED: ${String(e?.message || e)}`);
    }

    // 주기적 동기화(UT/잭팟 갱신)
    const refreshMs = Number(window.UNIQUE?.CONFIG?.REFRESH_MS || 30000);
    setInterval(async () => {
      try { await syncState(); } catch (_) {}
    }, refreshMs);
  }

  // DOM 준비 후 시작
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
