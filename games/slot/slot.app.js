/* games/slot/slot.app.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  // ✅ 기존 데이터 덮어쓰기 방지용: init때는 절대 wallet 저장 안 함
  const LS_KEYS = {
    WALLET: "slotWalletUT",      // (기존에 쓰던 키 유지)
    BET: "slotBetUT",
    AUTO: "slotAutoOn",
    PLAYER_ID: "slotPlayerId",
    PLAYER_NAME: "slotPlayerName",
  };

  const state = {
    wallet: null,   // null = 아직 모름(0으로 덮지 않음)
    bet: 10,
    auto: false,
    spinning: false,
    els: {},
  };

  const $ = (sel, root = document) => root.querySelector(sel);

  const num = (v) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  };

  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

  const setText = (el, t) => { if (el) el.textContent = String(t); };

  function injectStyleOnce(id, cssText) {
    if (document.getElementById(id)) return;
    const st = document.createElement("style");
    st.id = id;
    st.textContent = cssText;
    document.head.appendChild(st);
  }

  // -------------------------
  // ✅ “키 자동 탐색” (닉네임/UT 못잡는 문제 해결용)
  // -------------------------
  function getLocalStorageAny(keys) {
    for (const k of keys) {
      const v = localStorage.getItem(k);
      if (v !== null && String(v).trim() !== "") return v;
    }
    return null;
  }

  function scanLocalStorageSmart() {
    // 키 이름에서 추정 (유송 프로젝트에서 흔히 쓰는 패턴들)
    const all = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k) continue;
      all.push([k, localStorage.getItem(k)]);
    }

    const lower = (s) => String(s || "").toLowerCase();

    // nickname 후보
    const nickKeys = all
      .filter(([k, v]) => v && /[가-힣a-zA-Z0-9]/.test(v) && (
        lower(k).includes("nick") || lower(k).includes("name") || lower(k).includes("player")
      ))
      .map(([k]) => k);

    // ut 후보 (숫자인 값 + 키에 ut/wallet/balance 포함)
    const utKeys = all
      .filter(([k, v]) => {
        const n = num(v);
        if (n === null) return false;
        const lk = lower(k);
        return lk.includes("ut") || lk.includes("wallet") || lk.includes("balance");
      })
      .map(([k]) => k);

    return { nickKeys, utKeys };
  }

  function hydratePlayerAndWalletFromAnySource() {
    // 1) “확정 키” 먼저
    let pid = getLocalStorageAny([LS_KEYS.PLAYER_ID, "playerId", "uniquePlayerId", "uniqueId", "loginId", "username"]);
    let pname = getLocalStorageAny([LS_KEYS.PLAYER_NAME, "nickname", "uniqueNickname", "displayName", "userName", "name"]);

    // 2) 못 찾으면 “스마트 스캔”
    if (!pname) {
      const { nickKeys } = scanLocalStorageSmart();
      pname = getLocalStorageAny(nickKeys);
    }

    // 3) UT
    let w = getLocalStorageAny([LS_KEYS.WALLET, "walletUT", "walletUt", "ut", "UT", "uniqueUT", "uniqueUt"]);
    if (w === null) {
      const { utKeys } = scanLocalStorageSmart();
      w = getLocalStorageAny(utKeys);
    }

    const walletNum = num(w);

    // 화면 반영 (placeholder '-' / 0이면 덮어씀)
    if (pname) setPlayerUI(pid, pname);
    if (walletNum !== null && walletNum >= 0) S.ui.setWallet(walletNum, { persist: false }); // ✅ init에선 저장 금지
  }

  // -------------------------
  // ✅ UI 엘리먼트 잡기
  // -------------------------
  function grabEls() {
    state.els = {
      // 값 표시
      walletValue: $("#walletValue") || $("#walletUt") || $("[data-wallet]"),
      betValue: $("#betValue") || $("[data-bet]"),
      jackpotValue: $("#jackpotValue") || $("[data-jackpot]"),
      lastResultValue: $("#lastResultValue") || $("[data-last-result]"),

      // 버튼
      btnSpin: $("#btnSpin") || $("#spinBtn") || $("button[data-spin]") || $("button#spin") || $("button"),
      btnAuto: $("#btnAuto") || $("#autoBtn") || $("[data-auto]"),

      // 플레이어 표시
      playerBox: $("#playerBox") || $("[data-player]") || $(".player-box") || null,
      playerIdEl: $("#playerId") || $("[data-player-id]"),
      playerNameEl: $("#playerName") || $("[data-player-name]"),

      // 블럭 (paytable / slot / panel)
      payBlock: $("#payTable") || $("[data-paytable]") || $(".paytable") || $(".slot-paytable"),
      stageMount:
        $("#reels") ||
        $("#reelMount") ||
        $("#slotStage") ||
        $("#stage") ||
        document.querySelector("[data-slot-stage]") ||
        document.querySelector(".slot-stage") ||
        null,
      panelBlock: null, // spin 버튼으로 역추적
    };

    // panelBlock은 spin 버튼이 있는 카드/패널을 기준으로 잡는 게 가장 확실
    if (state.els.btnSpin) {
      state.els.panelBlock =
        state.els.btnSpin.closest(".panel, .card, .left-panel, .slot-panel, .slot-card") ||
        state.els.btnSpin.closest("section, article, div") ||
        null;
    }
  }

  // -------------------------
  // ✅ 플레이어 UI (슬래시 없음, 2줄)
  // -------------------------
  function setPlayerUI(pid, pname) {
    // 분리 엘리먼트가 있으면 거기에
    if (state.els.playerIdEl || state.els.playerNameEl) {
      if (state.els.playerIdEl) setText(state.els.playerIdEl, pid || "");
      if (state.els.playerNameEl) setText(state.els.playerNameEl, pname || "");
      return;
    }

    // 없으면 playerBox 안에 2줄로 강제 구성
    const box = state.els.playerBox;
    if (!box) return;
    box.innerHTML = "";
    const top = document.createElement("div");
    const bottom = document.createElement("div");
    top.textContent = (pid || "").trim();
    bottom.textContent = (pname || "").trim();
    box.appendChild(top);
    box.appendChild(bottom);
  }

  // -------------------------
  // ✅ 결과/지갑/베팅 UI API (다른 스크립트가 호출해도 안 죽게)
  // -------------------------
  S.ui = S.ui || {};

  S.ui.setWallet = (v, opt = {}) => {
    const n = num(v);
    if (n === null) return;
    state.wallet = Math.floor(n);
    setText(state.els.walletValue, state.wallet);

    // ✅ init에서는 저장 금지 (persist:false)
    const persist = opt.persist !== false;
    if (persist) localStorage.setItem(LS_KEYS.WALLET, String(state.wallet));
  };

  S.ui.setBet = (v) => {
    const n = num(v);
    if (n === null) return;
    state.bet = clamp(Math.floor(n), 5, 5000);
    setText(state.els.betValue, state.bet);
    localStorage.setItem(LS_KEYS.BET, String(state.bet));
  };

  S.ui.setLastResult = (t) => setText(state.els.lastResultValue, t);
  S.ui.setJackpot = (t) => setText(state.els.jackpotValue, t);

  // 닉네임/아이디를 외부 모듈이 넘겨도 반영되게
  S.ui.setPlayer = (pid, pname) => {
    if (pid) localStorage.setItem(LS_KEYS.PLAYER_ID, String(pid));
    if (pname) localStorage.setItem(LS_KEYS.PLAYER_NAME, String(pname));
    setPlayerUI(pid, pname);
  };

  // -------------------------
  // ✅ 레이아웃: PayTable → Slot → Panel
  // (DOM을 “계속 흔드는” 방식 금지 / 딱 한번만 정리)
  // -------------------------
  function setupFlowOnce() {
    const pay = state.els.payBlock;
    const stage = state.els.stageMount;
    const panel = state.els.panelBlock;

    // paytable이 없으면 억지로 재배치하지 않음
    if (!stage || !panel) return;

    // 각 블럭의 "카드" 단위를 최대한 보존
    const stageBlock =
      stage.closest(".panel, .card, .slot-card, .right-panel") || stage;

    const payBlock =
      pay ? (pay.closest(".panel, .card, .slot-card") || pay) : null;

    const panelBlock =
      panel.closest(".panel, .card, .slot-card, .left-panel") || panel;

    const host =
      stageBlock.closest(".page-wrap") ||
      stageBlock.closest("main") ||
      stageBlock.parentElement ||
      document.body;

    // 이미 만든 flow면 또 건드리지 않음
    let flow = document.getElementById("slotFlow");
    if (!flow) {
      flow = document.createElement("div");
      flow.id = "slotFlow";
      host.insertBefore(flow, host.firstChild);
    } else {
      // 이미 정리되어 있으면 종료
      if (flow.contains(stageBlock) && flow.contains(panelBlock)) return;
    }

    // ✅ 순서 고정: pay → stage → panel
    flow.innerHTML = "";
    if (payBlock) flow.appendChild(payBlock);
    flow.appendChild(stageBlock);
    flow.appendChild(panelBlock);

    injectStyleOnce(
      "slot-flow-style",
      `
      #slotFlow{
        width: min(760px, calc(100% - 16px));
        margin: 0 auto;
        padding: 10px 8px 18px;
        display:flex;
        flex-direction:column;
        gap: 14px;
        position: relative;
        z-index: 2; /* 배경 레이어보다 위 */
      }
      html,body{height:auto; min-height:100vh; overflow-y:auto;}
    `
    );
  }

  // -------------------------
  // ✅ 베팅 5단위 +/- 버튼이 없으면 자동 생성
  // -------------------------
  function ensureBetStepButtons() {
    // 이미 있으면 끝
    if (document.getElementById("btnBetMinus") && document.getElementById("btnBetPlus")) return;

    // betValue 주변에 붙이기
    const betValue = state.els.betValue;
    if (!betValue) return;

    const holder =
      betValue.closest(".panel, .card, .stat, .box, .tile, .row") ||
      betValue.parentElement ||
      betValue;

    const wrap = document.createElement("div");
    wrap.style.display = "flex";
    wrap.style.gap = "10px";
    wrap.style.marginTop = "10px";

    const mkBtn = (id, text) => {
      const b = document.createElement("button");
      b.id = id;
      b.type = "button";
      b.textContent = text;
      b.style.flex = "1";
      b.style.height = "40px";
      b.style.borderRadius = "12px";
      b.style.border = "1px solid rgba(255,255,255,0.12)";
      b.style.background = "rgba(0,0,0,0.18)";
      b.style.color = "#e7ecff";
      b.style.fontWeight = "700";
      b.style.letterSpacing = "0.5px";
      return b;
    };

    const minus = mkBtn("btnBetMinus", "-5");
    const plus = mkBtn("btnBetPlus", "+5");

    wrap.appendChild(minus);
    wrap.appendChild(plus);

    holder.appendChild(wrap);

    minus.addEventListener("click", () => {
      S.ui.setBet((state.bet || 10) - 5);
    });
    plus.addEventListener("click", () => {
      S.ui.setBet((state.bet || 10) + 5);
    });
  }

  // -------------------------
  // ✅ 저장은 “베팅/오토”만 init에서, 지갑은 절대 저장 금지
  // -------------------------
  function loadStateSafe() {
    const bet = num(localStorage.getItem(LS_KEYS.BET));
    const auto = (localStorage.getItem(LS_KEYSளம்        Keys.AUTO) ?? "0") === "1";

    state.bet = bet !== null ? clamp(Math.floor(bet), 5, 5000) : 10;
    state.auto = auto;

    setText(state.els.betValue, state.bet);
    if (state.els.btnAuto) state.els.btnAuto.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
  }

  function saveAuto() {
    localStorage.setItem(LS_KEYS.AUTO, state.auto ? "1" : "0");
  }

  // -------------------------
  // ✅ 숫자 카운트업 연출
  // -------------------------
  function animateCount(el, from, to, ms = 800) {
    if (!el) return;
    const a = Math.floor(from);
    const b = Math.floor(to);
    if (a === b) { el.textContent = String(b); return; }

    const t0 = performance.now();
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / ms);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.floor(a + (b - a) * eased));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // -------------------------
  // ✅ 스핀
  // -------------------------
  async function doSpinOnce() {
    if (state.spinning) return;
    if (!S.game || typeof S.game.spin !== "function") return;

    // wallet 모르면 “표시값”에서 읽어보되, 저장은 안 함
    if (state.wallet === null) {
      const displayed = num(state.els.walletValue?.textContent);
      if (displayed !== null) state.wallet = displayed;
    }

    if (state.wallet === null) {
      S.ui.setLastResult("UT 로딩중");
      return;
    }

    if (state.wallet < state.bet) {
      S.ui.setLastResult("UT 부족");
      return;
    }

    state.spinning = true;

    const before = state.wallet;
    const afterPayBet = before - state.bet;

    // ✅ 여기서만 wallet 변화 저장(덮어쓰기 방지)
    animateCount(state.els.walletValue, before, afterPayBet, 220);
    state.wallet = afterPayBet;
    localStorage.setItem(LS_KEYS.WALLET, String(state.wallet));

    const result = await S.game.spin({ bet: state.bet });

    const payout = Number(result?.payout || 0);
    const final = state.wallet + payout;

    animateCount(state.els.walletValue, state.wallet, final, result?.jackpot ? 3500 : 900);
    state.wallet = final;
    localStorage.setItem(LS_KEYS.WALLET, String(state.wallet));

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

    if (state.auto) setTimeout(doSpinOnce, 350);
  }

  function bindUi() {
    if (state.els.btnSpin) {
      state.els.btnSpin.addEventListener("click", (e) => {
        e.preventDefault();
        doSpinOnce();
      });
    }

    if (state.els.btnAuto) {
      state.els.btnAuto.addEventListener("click", (e) => {
        e.preventDefault();
        state.auto = !state.auto;
        state.els.btnAuto.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
        saveAuto();
        if (state.auto && !state.spinning) doSpinOnce();
      });
    }
  }

  function init() {
    grabEls();
    setupFlowOnce();           // ✅ 순서: paytable → slot → panel
    loadStateSafe();           // ✅ wallet 저장 금지
    ensureBetStepButtons();    // ✅ -5 +5 없으면 생성
    bindUi();

    // 릴 생성
    try { S.game?.buildReels?.(); } catch (_) {}

    // ✅ 이름/UT 자동 주입(가능한 모든 키에서 찾아서)
    hydratePlayerAndWalletFromAnySource();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  S.app = S.app || {};
  S.app.spin = doSpinOnce;

})(window.SLOT);
