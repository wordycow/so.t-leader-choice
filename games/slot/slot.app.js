/* games/slot/slot.app.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const LS = {
    WALLET: "slotWalletUT",
    BET: "slotBetUT",
    AUTO: "slotAutoOn",
    PLAYER_ID: "slotPlayerId",
    PLAYER_NAME: "slotPlayerName",
  };

  const state = {
    wallet: 0,
    bet: 10,
    auto: false,
    spinning: false,
    els: {},
  };

  const $ = (sel, root = document) => root.querySelector(sel);

  function num(v, d = 0) {
    const n = Number(v);
    return Number.isFinite(n) ? n : d;
  }

  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }

  function setText(el, t) {
    if (el) el.textContent = String(t);
  }

  function injectStyleOnce(id, cssText) {
    if (document.getElementById(id)) return;
    const st = document.createElement("style");
    st.id = id;
    st.textContent = cssText;
    document.head.appendChild(st);
  }

  // ---------------------------
  // UI API (slot.app.js가 쓰던 것들)
  // ---------------------------
  S.ui = S.ui || {};
  S.ui.setWallet = (v) => {
    state.wallet = num(v, state.wallet);
    setText(state.els.walletValue, state.wallet);
  };
  S.ui.setBet = (v) => {
    state.bet = clamp(num(v, state.bet), 5, 5000);
    setText(state.els.betValue, state.bet);
  };
  S.ui.setJackpot = (v) => setText(state.els.jackpotValue, v);
  S.ui.setLastResult = (v) => setText(state.els.lastResultValue, v);

  // ---------------------------
  // 요소 찾기 (있으면 쓰고, 없으면 넘어감)
  // ---------------------------
  function grabEls() {
    state.els = {
      // 값 표시
      walletValue: $("#walletValue") || $("#walletUt") || $("[data-wallet]"),
      betValue: $("#betValue") || $("[data-bet]"),
      jackpotValue: $("#jackpotValue") || $("[data-jackpot]"),
      lastResultValue: $("#lastResultValue") || $("[data-last-result]"),

      // 버튼
      btnSpin: $("#btnSpin") || $("#spinBtn") || $("button[data-spin]") || $("button"),
      btnAuto: $("#btnAuto") || $("#autoBtn") || $("[data-auto]"),
      btnMinus: $("#btnBetMinus") || $("[data-bet-minus]"),
      btnPlus: $("#btnBetPlus") || $("[data-bet-plus]"),

      // 블럭
      paytableBlock:
        $("#payTable") ||
        $(".paytable") ||
        $("[data-paytable]") ||
        $(".slot-paytable") ||
        null,
      stageMount:
        $("#reels") ||
        $("#reelMount") ||
        $("#slotStage") ||
        $("#stage") ||
        $("[data-slot-stage]") ||
        $(".slot-stage") ||
        null,
      assetPanel:
        $("#assetPanel") ||
        $("#leftPanel") ||
        $(".left-panel") ||
        $("[data-slot-panel]") ||
        null,

      // 플레이어 표시 (슬래시 제거용)
      playerIdEl: $("#playerId") || $("[data-player-id]"),
      playerNameEl: $("#playerName") || $("[data-player-name]"),
      playerComboEl: $("#playerLabel") || $("[data-player]"),
    };
  }

  // ---------------------------
  // 모바일/데스크탑 레이아웃 재배치
  // PayTable -> Slot -> AssetPanel
  // ---------------------------
  function relaxScrollLocks() {
    // "밑으로 내리면 내려가야" = overflow hidden / 100vh 락 풀기
    [document.documentElement, document.body].forEach((el) => {
      el.style.overflowY = "auto";
      el.style.height = "auto";
      el.style.minHeight = "100vh";
    });
  }

  function setupFlowLayout() {
    const pay = state.els.paytableBlock;
    const stage = state.els.stageMount;
    const panel = state.els.assetPanel;

    // 블럭 3개 중 하나라도 못 찾으면 레이아웃 강제 재배치 안 함
    if (!pay || !stage || !panel) return;

    // stage는 mount 자체 말고 “카드/패널” 단위로 잡는 게 안전
    const stageBlock =
      stage.closest(".slot-stage-card") ||
      stage.closest(".panel-right") ||
      stage.closest(".right-panel") ||
      stage.closest(".card") ||
      stage;

    const payBlock =
      pay.closest(".slot-paytable-card") ||
      pay.closest(".card") ||
      pay;

    const panelBlock =
      panel.closest(".slot-panel-card") ||
      panel.closest(".card") ||
      panel;

    // 공통 부모(최대한 바깥)
    const host =
      stageBlock.closest(".page-wrap") ||
      stageBlock.closest("main") ||
      stageBlock.parentElement ||
      document.body;

    let flow = document.getElementById("slotFlow");
    if (!flow) {
      flow = document.createElement("div");
      flow.id = "slotFlow";
      host.insertBefore(flow, host.firstChild);
    }

    // 블럭들을 flow 안으로 이동 (순서 강제)
    flow.appendChild(payBlock);
    flow.appendChild(stageBlock);
    flow.appendChild(panelBlock);

    // z-index: 배경 레이어는 뒤(0), UI는 위(2)
    flow.style.position = "relative";
    flow.style.zIndex = "2";

    injectStyleOnce(
      "slot-flow-style",
      `
      /* 데스크탑: 패널은 왼쪽, 오른쪽 위에 paytable / 아래에 슬롯 */
      #slotFlow{
        width: min(1100px, calc(100% - 24px));
        margin: 0 auto;
        padding: 12px;
        display: grid;
        gap: 14px;
        align-items: start;
        grid-template-columns: 360px 1fr;
        grid-template-areas:
          "panel pay"
          "panel stage";
      }
      /* 블럭에 영역 지정 (가능한 경우만) */
      #slotFlow > :nth-child(1){ grid-area: pay; }
      #slotFlow > :nth-child(2){ grid-area: stage; }
      #slotFlow > :nth-child(3){ grid-area: panel; }

      /* 모바일: 위에서 아래로 PayTable -> Slot -> Panel */
      @media (max-width: 900px){
        #slotFlow{
          display:flex;
          flex-direction:column;
        }
        #slotFlow > :nth-child(1){ order: 1; }
        #slotFlow > :nth-child(2){ order: 2; }
        #slotFlow > :nth-child(3){ order: 3; }
      }
    `
    );

    // 배경 레이어가 보이도록 z-index 정리 (game.js가 만든 div가 있어도 잡아줌)
    const bgA = document.getElementById("slotBgA");
    const bgB = document.getElementById("slotBgB");
    if (bgA) bgA.style.zIndex = "0";
    if (bgB) bgB.style.zIndex = "1";
  }

  // ---------------------------
  // 플레이어 표시: "아이디 / 이름" 슬래시 제거
  // ---------------------------
  function fixPlayerSlash() {
    const combo = state.els.playerComboEl;
    const idEl = state.els.playerIdEl;
    const nameEl = state.els.playerNameEl;

    // 1) 분리된 엘리먼트가 있으면 거기에 넣고 끝
    if (idEl && nameEl) {
      const pid = (localStorage.getItem(LS.PLAYER_ID) || "").trim();
      const pname = (localStorage.getItem(LS.PLAYER_NAME) || "").trim();
      if (pid) setText(idEl, pid);
      if (pname) setText(nameEl, pname);
      return;
    }

    // 2) 한 줄 텍스트 안에 "/"가 있으면 제거해서 줄바꿈 느낌으로 정리
    if (combo) {
      const t = combo.textContent || "";
      if (t.includes("/")) {
        const [a, b] = t.split("/").map((s) => s.trim());
        combo.innerHTML = "";
        const top = document.createElement("div");
        const bottom = document.createElement("div");
        top.textContent = a || "";
        bottom.textContent = b || "";
        combo.appendChild(top);
        combo.appendChild(bottom);
      }
    }
  }

  // ---------------------------
  // 저장/로드
  // ---------------------------
  function loadState() {
    state.wallet = num(localStorage.getItem(LS.WALLET), num(state.els.walletValue?.textContent, 0));
    state.bet = clamp(num(localStorage.getItem(LS.BET), 10), 5, 5000);
    state.auto = (localStorage.getItem(LS.AUTO) ?? "0") === "1";
    S.ui.setWallet(state.wallet);
    S.ui.setBet(state.bet);
    if (state.els.btnAuto) state.els.btnAuto.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
  }

  function saveState() {
    localStorage.setItem(LS.WALLET, String(Math.max(0, Math.floor(state.wallet))));
    localStorage.setItem(LS.BET, String(Math.max(5, Math.floor(state.bet))));
    localStorage.setItem(LS.AUTO, state.auto ? "1" : "0");
  }

  // ---------------------------
  // 숫자 카운트업(이긴 느낌 연출)
  // ---------------------------
  function animateCount(el, from, to, ms = 900) {
    if (!el) return;
    const a = Math.floor(from);
    const b = Math.floor(to);
    if (a === b) {
      el.textContent = String(b);
      return;
    }
    const t0 = performance.now();
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / ms);
      const eased = 1 - Math.pow(1 - p, 3);
      const v = Math.floor(a + (b - a) * eased);
      el.textContent = String(v);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // ---------------------------
  // 스핀 동작
  // ---------------------------
  async function doSpinOnce() {
    if (state.spinning) return;
    if (!S.game || typeof S.game.spin !== "function") return;

    if (state.wallet < state.bet) {
      S.ui.setLastResult("UT 부족");
      return;
    }

    state.spinning = true;

    const before = state.wallet;
    state.wallet = before - state.bet;
    animateCount(state.els.walletValue, before, state.wallet, 250);
    saveState();

    // 게임 스핀(배경 현란은 game.js가 스핀 동안만 돌림)
    const result = await S.game.spin({ bet: state.bet });

    // payout 반영
    const after = state.wallet + (result?.payout || 0);
    animateCount(state.els.walletValue, state.wallet, after, result?.jackpot ? 3500 : 900);
    state.wallet = after;
    saveState();

    // 결과 텍스트: EVEN / WIN / LOSE
    if (result?.jackpot) {
      S.ui.setLastResult("JACKPOT");
    } else if ((result?.netDelta || 0) > 0) {
      S.ui.setLastResult("WIN");
    } else if ((result?.netDelta || 0) === 0 && (result?.payout || 0) > 0) {
      S.ui.setLastResult("EVEN");
    } else {
      S.ui.setLastResult("LOSE");
    }

    state.spinning = false;

    // AUTO
    if (state.auto) {
      setTimeout(() => doSpinOnce(), 350);
    }
  }

  // ---------------------------
  // 바인딩
  // ---------------------------
  function bindUi() {
    const { btnSpin, btnAuto, btnMinus, btnPlus } = state.els;

    if (btnSpin) {
      btnSpin.addEventListener("click", (e) => {
        e.preventDefault();
        doSpinOnce();
      });
    }

    if (btnAuto) {
      btnAuto.addEventListener("click", (e) => {
        e.preventDefault();
        state.auto = !state.auto;
        btnAuto.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
        saveState();
        if (state.auto && !state.spinning) doSpinOnce();
      });
    }

    const step = 5;
    if (btnMinus) {
      btnMinus.addEventListener("click", (e) => {
        e.preventDefault();
        state.bet = clamp(state.bet - step, 5, 5000);
        S.ui.setBet(state.bet);
        saveState();
      });
    }

    if (btnPlus) {
      btnPlus.addEventListener("click", (e) => {
        e.preventDefault();
        state.bet = clamp(state.bet + step, 5, 5000);
        S.ui.setBet(state.bet);
        saveState();
      });
    }
  }

  function init() {
    grabEls();
    relaxScrollLocks();
    setupFlowLayout();
    fixPlayerSlash();

    // 릴 생성
    try {
      S.game?.buildReels?.();
    } catch (_) {}

    loadState();
    bindUi();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // 외부에서 호출 가능하게
  S.app = S.app || {};
  S.app.spin = doSpinOnce;

})(window.SLOT);
