(function () {
  const S = (window.S = window.S || {});
  S.app = S.app || {};

  const state = {
    userId: "",
    userName: "-",
    balance: 0,
    jackpot: 0,
    casino: 0,
    bet: 10,
    auto: false,
    spinning: false,
    soundOn: true,
  };

  function qs(name) {
    return new URLSearchParams(location.search).get(name) || "";
  }

  function parseMaybeJson(v) {
    if (!v) return null;
    const s = String(v);
    if (!s) return null;
    try { return JSON.parse(s); } catch (_) { return null; }
  }

  function loadLogin() {
    // 1) querystring 우선
    const qid = (qs("id") || qs("uid") || "").trim().toLowerCase();
    if (qid) return { id: qid };

    // 2) localStorage 다 훑기
    const keys = S.CONFIG.LOGIN_KEYS || [];
    for (const k of keys) {
      let raw = "";
      try { raw = localStorage.getItem(k) || ""; } catch (_) {}
      if (!raw) continue;

      const obj = parseMaybeJson(raw);
      if (obj && typeof obj === "object") {
        const id = String(obj.id || obj.userId || obj.userid || obj.uid || "").trim().toLowerCase();
        const name = String(obj.name || obj.nickname || obj.nick || "").trim();
        if (id) return { id, name };
      }

      // plain string
      const plain = String(raw).trim().toLowerCase();
      if (plain && plain.length >= 3) return { id: plain };
    }
    return null;
  }

  function clampBet(v) {
    const min = S.CONFIG.BET_MIN ?? 10;
    const max = S.CONFIG.BET_MAX ?? 1000;
    let x = Math.floor(Number(v || 0));
    if (!Number.isFinite(x)) x = min;
    x = Math.max(min, Math.min(max, x));
    return x;
  }

  function setBet(v) {
    state.bet = clampBet(v);
    S.ui.setBet(state.bet);
    try { localStorage.setItem("slot_bet", String(state.bet)); } catch (_) {}
  }

  function loadBet() {
    try {
      const v = Number(localStorage.getItem("slot_bet") || S.CONFIG.BET_DEFAULT || 10);
      setBet(v);
    } catch (_) {
      setBet(S.CONFIG.BET_DEFAULT || 10);
    }
  }

  function renderPaytable() {
    const body = document.getElementById("paytableBody");
    if (!body) return;

    const list = S.game.paytable();
    const rows = list.map(s => {
      const p2 = s.pay[2] ? `2개: EVEN (x${s.pay[2]})` : "";
      const p3 = s.pay[3] ? `3개: x${s.pay[3]}` : "";
      const p4 = s.pay[4] ? `4개: x${s.pay[4]}` : "";
      const p5 = s.pay[5] ? `5개: x${s.pay[5]}` : "";
      return `
        <div class="pt-row">
          <div class="pt-left">
            <img class="pt-ico" src="${S.CONFIG.IMG_DIR}/${s.id}.png" alt="${s.name}" />
            <div class="pt-name">${s.name}</div>
          </div>
          <div class="pt-right">
            <div>${p2}</div>
            <div>${p3}</div>
            <div>${p4}</div>
            <div>${p5}</div>
          </div>
        </div>
      `;
    }).join("");

    body.innerHTML = `<div class="pt-list">${rows}</div>`;
  }

  async function syncStateFromServer() {
    const login = loadLogin();
    if (!login?.id) {
      state.userId = "";
      state.userName = "-";
      S.ui.setPlayer("-");
      S.ui.setWallet(0);
      S.ui.setJackpot(0);
      S.ui.setResult("LOGIN REQUIRED");
      S.ui.setSpinEnabled(false);
      return;
    }

    state.userId = login.id;
    try { localStorage.setItem("slot_user_id", login.id); } catch (_) {}

    // 서버에서 유저/잭팟/카지노 가져오기
    const r = await S.api.getSlotState(state.userId);
    const u = r.user || {};
    state.userName = (u.nickname || u.name || login.name || state.userId || "-");
    state.balance = Number(u.balance || 0);
    state.jackpot = Number(r.jackpotTotal || 0);
    state.casino = Number(r.casinoTotal || 0);

    S.ui.setPlayer(state.userName);
    S.ui.setWallet(state.balance);
    S.ui.setJackpot(state.jackpot);
    S.ui.setResult("READY");
    S.ui.setSpinEnabled(true);
  }

  function bindUI() {
    const btnSpin = document.getElementById("btnSpin");
    const btnAuto = document.getElementById("btnAuto");
    const btnSound = document.getElementById("btnSound");
    const btnMinus = document.getElementById("btnBetMinus");
    const btnPlus = document.getElementById("btnBetPlus");
    const btnPayToggle = document.getElementById("btnPayToggle");

    btnMinus.onclick = () => setBet(state.bet - (S.CONFIG.BET_STEP || 5));
    btnPlus.onclick = () => setBet(state.bet + (S.CONFIG.BET_STEP || 5));

    btnSound.onclick = () => {
      state.soundOn = !state.soundOn;
      S.audio.setEnabled(state.soundOn);
      S.ui.setSoundLabel(state.soundOn);
    };

    btnAuto.onclick = () => {
      state.auto = !state.auto;
      S.ui.setAutoLabel(state.auto);
      if (state.auto && !state.spinning) spinOnce(); // 즉시 1회
    };

    btnSpin.onclick = () => spinOnce();

    btnPayToggle.onclick = () => {
      const card = document.getElementById("paytableCard");
      card?.classList.toggle("collapsed");
    };
  }

  function randomizeAnim(ms = 900) {
    const rows = S.CONFIG.ROWS || 3;
    const cols = S.CONFIG.COLS || 5;
    const size = rows * cols;
    const ids = ["star1","star2","star3","pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"];

    return new Promise((resolve) => {
      const t0 = performance.now();
      const timer = setInterval(() => {
        const grid = new Array(size).fill(0).map(() => ids[(Math.random() * ids.length) | 0]);
        S.ui.renderGrid(grid);
        if (performance.now() - t0 > ms) {
          clearInterval(timer);
          resolve();
        }
      }, 70);
    });
  }

  function resultText(spin) {
    if (spin.type === "JACKPOT") return `JACKPOT +${spin.win.toFixed(2)} UT`;
    if (spin.type === "EVEN") return `EVEN`;
    if (spin.type === "WIN") return `WIN +${Math.max(0, spin.netDelta).toFixed(2)} UT`;
    return `MISS -${state.bet} UT`;
  }

  async function spinOnce() {
    if (state.spinning) return;
    if (!state.userId) return;

    state.spinning = true;
    S.ui.setSpinEnabled(false);

    try {
      S.audio.play("start");
      S.audio.play("spin");
      S.ui.startBgCycle();
      S.ui.setResult("SPINNING...");

      await randomizeAnim(950);

      // 최종 결과
      const spin = S.game.spin(state.bet, state.jackpot);

      // 결과 그리기
      S.ui.renderGrid(spin.grid);

      S.audio.stopSpin();
      S.audio.play("stop");
      S.ui.stopBgCycle();

      const txt = resultText(spin);
      S.ui.setResult(txt);

      // 서버 커밋(구글 Apps Script)
      const payload = {
        id: state.userId,
        netDelta: spin.netDelta,
        lossAmount: spin.lossAmount,
        bet: state.bet,
        win: spin.win,
        resultType: spin.type,
        jackpotPayout: spin.jackpotPayout,
        grid: JSON.stringify(spin.grid),
        name: state.userName
      };

      const beforeBal = state.balance;
      const beforeJack = state.jackpot;

      const r = await S.api.slotCommit(payload);

      // 서버값 반영
      const u = r.user || {};
      state.balance = Number(u.balance ?? state.balance);
      state.jackpot = Number(r.jackpotTotal ?? state.jackpot);

      // 숫자 카운트업(돈 올라가는 느낌)
      S.ui.animateWallet(beforeBal, state.balance, 900);
      S.ui.animateJackpot(beforeJack, state.jackpot, 900);

      // 사운드/연출
      if (spin.type === "JACKPOT") {
        S.audio.play("jackpot");
        S.ui.jackpotTickerFor(state.userName);
        S.ui.showCelebrate({
          title: "JACKPOT!",
          amount: spin.win,
          sub: `${state.userName}님 잭팟 축하드립니다.`,
          ms: 60000
        });
      } else if (spin.type === "WIN") {
        S.audio.play("win");
        // 빅윈이면 팝업(연출)
        if (spin.netDelta >= state.bet * 10) {
          S.ui.showCelebrate({
            title: "BIG WIN!",
            amount: spin.netDelta,
            sub: "축하드립니다.",
            ms: 12000
          });
        }
      } else if (spin.type === "MISS") {
        S.audio.play("lose");
      }

    } catch (e) {
      console.error(e);
      S.audio.stopSpin();
      S.ui.stopBgCycle();
      S.ui.setResult(`ERROR: ${e.message || e}`);
    } finally {
      state.spinning = false;
      S.ui.setSpinEnabled(true);

      // AUTO면 계속
      if (state.auto) {
        setTimeout(() => {
          if (!state.spinning) spinOnce();
        }, 900);
      }
    }
  }

  async function init() {
    S.ui.init();
    S.audio.init();

    state.soundOn = S.audio.loadEnabled();
    S.ui.setSoundLabel(state.soundOn);

    loadBet();
    renderPaytable();
    bindUI();

    await syncStateFromServer();

    // 초기 그리드(보기)
    const size = (S.CONFIG.ROWS || 3) * (S.CONFIG.COLS || 5);
    S.ui.renderGrid(new Array(size).fill("star1"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    init().catch((e) => {
      console.error(e);
      S.ui?.setResult?.(`INIT ERROR: ${e.message || e}`);
    });
  });
})();
