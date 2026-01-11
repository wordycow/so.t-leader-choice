/* games/slot/slot.app.js
 * THE UNIQUE SLOT - App Entrypoint (no-approval, clean wiring)
 * - Depends on: slot.config.js, slot.api.js, slot.audio.js, slot.game.js, slot.ui.js
 * - Works with BOTH UI id sets:
 *   (A) cyberpunk slot.html ids: uiPlayer/uiWallet/uiBet/uiJackpot/uiResult/uiNote/uiPaytable/uiReels + btnSpin/btnAuto
 *   (B) module ui ids: playerName/playerUt/betVal/jpVal/winVal/log/payGrid + soundBtn/soundText
 */

(() => {
  "use strict";

  window.SLOT = window.SLOT || {};
  const S = window.SLOT;

  // ---- version stamp
  window.__SLOT_BUILD__ = "slot.app@2026-01-11";
  console.log("RUNNING:", window.__SLOT_BUILD__);

  // ---- helpers
  const $ = (id) => document.getElementById(id);
  const pickEl = (...ids) => ids.map($).find(Boolean) || null;
  const setText = (el, v) => { if (el) el.textContent = String(v ?? ""); };
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const fmtInt = (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return "0";
    return String(Math.trunc(n));
  };

  // ---- bind UI (supports both html styles)
  const ui = {
    // cyberpunk
    uiPlayer: $("uiPlayer"),
    uiWallet: $("uiWallet"),
    uiBet: $("uiBet"),
    uiJackpot: $("uiJackpot"),
    uiResult: $("uiResult"),
    uiNote: $("uiNote"),
    uiPaytable: $("uiPaytable"),
    uiReels: $("uiReels"),
    uiReelWrap: $("uiReelWrap"),
    btnSpin: $("btnSpin"),
    btnAuto: $("btnAuto"),

    // module ui (optional)
    apiDot: $("apiDot"),
    apiText: $("apiText"),
    soundBtn: $("soundBtn") || $("btnSound"),
    soundText: $("soundText"),
    playerName: $("playerName"),
    playerUt: $("playerUt"),
    betVal: $("betVal"),
    jpVal: $("jpVal"),
    winVal: $("winVal"),
    log: $("log"),
    payGrid: $("payGrid"),
  };

  // ---- ensure API base (this fixes your Not found / 404)
  function ensureApiBase() {
    // 1) unique.config.js에서 내려오는 값 우선
    const fromUnique =
      window.UNIQUE?.CONFIG?.SLOT_WORKER_BASE ||
      window.UNIQUE?.CONFIG?.SLOT_API_BASE ||
      "";

    // 2) 이미 세팅되어 있으면 유지
    if (window.SLOT_API_BASE && String(window.SLOT_API_BASE).trim()) return;

    // 3) unique.config 값이 있으면 SLOT_API_BASE로 주입
    if (fromUnique && String(fromUnique).trim()) {
      window.SLOT_API_BASE = String(fromUnique).trim().replace(/\/+$/,"");
      return;
    }

    // 4) 마지막 fallback(너가 쓰던 워커)
    window.SLOT_API_BASE = "https://the-unique-slot-api.wordycow0001.workers.dev";
  }

  // ---- local identity bridge (no approval)
  // main/gate에서 쓰던 uniqueCurrentUser가 있으면 slot.api.js가 보는 localStorage 키들도 채워준다.
  function bridgeIdentityFromUniqueCurrentUser() {
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return;
      const u = JSON.parse(raw);

      const id = String(u?.id || "").trim();
      const name = String(u?.name || "").trim();
      const nick = String(u?.nickname || "").trim();

      if (id) localStorage.setItem("unique_id", id);
      if (name) localStorage.setItem("unique_name", name);
      if (nick) localStorage.setItem("unique_nickname", nick);

      // UI 표시용
      if (name) localStorage.setItem("unique_display_name", name);
      else if (nick) localStorage.setItem("unique_display_name", nick);
    } catch {}
  }

  // ---- bet (step=5, min=10)
  const LS_BET = "uniqueSlotBet";
  let bet = 10;

  function loadBet() {
    const v = Number(localStorage.getItem(LS_BET) || 10);
    if (Number.isFinite(v)) bet = clamp(Math.round(v / 5) * 5, 10, 1000);
  }
  function saveBet() {
    localStorage.setItem(LS_BET, String(bet));
  }

  // ---- inject bet controls (cyberpunk html has only uiBet text)
  function ensureBetControls() {
    if (!ui.uiBet) return;
    const box = ui.uiBet.closest(".stat") || ui.uiBet.parentElement;
    if (!box) return;

    if (document.getElementById("btnBetMinus")) return;

    const bar = document.createElement("div");
    bar.style.display = "flex";
    bar.style.alignItems = "center";
    bar.style.gap = "10px";
    bar.style.marginTop = "10px";

    const mkBtn = (id, txt) => {
      const b = document.createElement("button");
      b.id = id;
      b.textContent = txt;
      b.style.width = "44px";
      b.style.height = "40px";
      b.style.borderRadius = "14px";
      b.style.border = "1px solid rgba(33,246,255,.22)";
      b.style.background = "rgba(4,6,16,.40)";
      b.style.color = "rgba(215,228,255,.92)";
      b.style.fontWeight = "900";
      b.style.cursor = "pointer";
      return b;
    };

    const minus = mkBtn("btnBetMinus", "-5");
    const plus  = mkBtn("btnBetPlus", "+5");

    const meta = document.createElement("div");
    meta.id = "uiBetHint";
    meta.style.fontFamily = '"Share Tech Mono", ui-monospace, Menlo, monospace';
    meta.style.fontSize = "12px";
    meta.style.color = "rgba(215,228,255,.82)";
    meta.style.letterSpacing = ".06em";

    const refresh = () => {
      setText(ui.uiBet, fmtInt(bet));
      meta.textContent = `BET: ${bet} UT (±5)`;
      // module ui도 같이 갱신
      if (ui.betVal) setText(ui.betVal, fmtInt(bet));
      if (S.ui?.setKpi) S.ui.setKpi({ bet });
    };

    minus.addEventListener("click", () => {
      bet = clamp(bet - 5, 10, 1000);
      saveBet();
      refresh();
      S.audio?.sfx?.("start");
    });

    plus.addEventListener("click", () => {
      bet = clamp(bet + 5, 10, 1000);
      saveBet();
      refresh();
      S.audio?.sfx?.("start");
    });

    bar.appendChild(minus);
    bar.appendChild(meta);
    bar.appendChild(plus);
    box.appendChild(bar);

    refresh();
  }

  // ---- ensure sound button for cyberpunk layout (if slot.ui.js style ids not present)
  function ensureSoundButton() {
    if (ui.soundBtn) return; // already exists

    const row = ui.btnSpin?.closest(".row") || ui.btnSpin?.parentElement;
    if (!row) return;

    const btn = document.createElement("button");
    btn.id = "btnSound";
    btn.className = "btn btnAuto"; // reuse cyberpunk styles
    btn.style.width = "140px";
    btn.textContent = (S.audio?.isOn?.() ?? true) ? "SOUND ON" : "SOUND OFF";

    btn.addEventListener("click", async () => {
      const on = S.audio?.toggle ? S.audio.toggle() : true;
      btn.textContent = on ? "SOUND ON" : "SOUND OFF";
    });

    // AUTO 옆에 끼워넣기
    if (ui.btnAuto && row.contains(ui.btnAuto)) ui.btnAuto.insertAdjacentElement("afterend", btn);
    else row.insertBefore(btn, ui.btnSpin);

    ui.soundBtn = btn;
  }

  // ---- paytable (cyberpunk paytable area)
  function buildCyberPaytable() {
    if (!ui.uiPaytable) return;
    ui.uiPaytable.innerHTML = `
      <div class="ptItem"><div class="ptLeft"><div class="badge">2×</div><div>같은 심볼 2개</div></div><div class="ptMul">WIN</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">3×</div><div>같은 심볼 3개</div></div><div class="ptMul">WIN</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">4×</div><div>같은 심볼 4개</div></div><div class="ptMul">BIG WIN</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">5×</div><div>같은 심볼 5개</div></div><div class="ptMul">MEGA</div></div>
      <div class="ptItem"><div class="ptLeft"><div class="badge">JP</div><div><b>PRO10</b> 5개 = JACKPOT</div></div><div class="ptMul">SPECIAL</div></div>
    `;
  }

  function movePaytableUnderReels() {
    if (!ui.uiReelWrap || !ui.uiPaytable) return;
    if (ui.uiReelWrap.querySelector(".tu-paywrap")) return;

    const wrap = document.createElement("div");
    wrap.className = "tu-paywrap";
    wrap.style.marginTop = "12px";

    const title = document.createElement("div");
    title.textContent = "PAY TABLE";
    title.style.fontFamily = '"Orbitron", system-ui, sans-serif';
    title.style.fontWeight = "900";
    title.style.letterSpacing = ".14em";
    title.style.fontSize = "12px";
    title.style.color = "rgba(215,228,255,.88)";
    title.style.margin = "4px 0 8px";
    title.style.textTransform = "uppercase";

    wrap.appendChild(title);
    wrap.appendChild(ui.uiPaytable);
    ui.uiReelWrap.appendChild(wrap);
  }

  // ---- status / log helpers (works for both UI types)
  function setOnline(on) {
    // module ui
    if (S.ui?.setOnline) S.ui.setOnline(on);
    if (ui.apiDot) ui.apiDot.style.background = on ? "#22c55e" : "#ef4444";
    if (ui.apiText) setText(ui.apiText, on ? "Online" : "Offline");
  }

  function setNote(msg, isErr = false) {
    if (ui.uiNote) {
      setText(ui.uiNote, msg || "");
      ui.uiNote.style.color = isErr ? "rgba(255,120,160,.95)" : "rgba(215,228,255,.82)";
    }
    if (ui.log) setText(ui.log, msg || "");
    if (S.ui?.setLog) S.ui.setLog(msg || "");
  }

  function setResult(msg, isErr = false) {
    if (ui.uiResult) {
      setText(ui.uiResult, msg || "");
      ui.uiResult.style.color = isErr ? "rgba(255,120,160,.95)" : "";
    }
    // module ui에서는 winVal를 결과표시로 쓰는 경우가 많아 같이 넣어줌
    if (ui.winVal) setText(ui.winVal, msg || "");
  }

  function setPlayerAndWallet({ displayName, ut }) {
    // cyberpunk
    if (ui.uiPlayer) setText(ui.uiPlayer, displayName || "-");
    if (ui.uiWallet && ut !== undefined) setText(ui.uiWallet, fmtInt(ut));

    // module ui
    if (S.ui?.setPlayer) S.ui.setPlayer({ displayName, ut });
    if (ui.playerName) setText(ui.playerName, displayName || "-");
    if (ui.playerUt && ut !== undefined) setText(ui.playerUt, String(ut));
  }

  function setJackpot(v) {
    if (ui.uiJackpot) setText(ui.uiJackpot, fmtInt(v));
    if (ui.jpVal) setText(ui.jpVal, fmtInt(v));
    if (S.ui?.setKpi) S.ui.setKpi({ jackpot: v });
  }

  // ---- main flow
  let spinning = false;
  let autoOn = false;
  let autoTimer = null;

  function stopAuto() {
    autoOn = false;
    if (ui.btnAuto) setText(ui.btnAuto, "AUTO OFF");
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = null;
  }
  function startAuto() {
    if (autoOn) return;
    autoOn = true;
    if (ui.btnAuto) setText(ui.btnAuto, "AUTO ON");
    autoTimer = setInterval(() => { if (!spinning) spin(); }, 1250);
  }

  async function loadState() {
    setNote("SYNC…");
    try {
      const js = await S.api.state();
      // worker가 살아있으면 ok 유무와 상관 없이 Online은 켬(네트워크 OK)
      setOnline(true);

      if (!js || js.ok === false) {
        setResult("STATE ERROR", true);
        setNote(`state fail: ${js?.error || "unknown"}`, true);
        return;
      }

      const name = String(js.userName || js.name || js.displayName || "").trim();
      const idt = S.api.getUserIdentity?.() || {};
      const displayName = name || idt.name || idt.id || idt.u || "Guest";

      const ut = (js.ut ?? js.UT ?? js.totalUT ?? js.wallet ?? js.balance);
      setPlayerAndWallet({ displayName, ut: ut ?? 0 });

      setJackpot(js.jackpot ?? js.jackpotUT ?? js.jackpot_ut ?? 0);

      // 서버가 bet을 내려주면 맞춰주기(없으면 로컬 bet 유지)
      const srvBet = Number(js.bet);
      if (Number.isFinite(srvBet) && srvBet > 0) {
        bet = clamp(Math.round(srvBet / 5) * 5, 10, 1000);
        saveBet();
      }
      if (ui.uiBet) setText(ui.uiBet, fmtInt(bet));
      if (ui.betVal) setText(ui.betVal, fmtInt(bet));
      if (S.ui?.setKpi) S.ui.setKpi({ bet });

      // grid 렌더는 slot.game.js에 있으면 위임
      if (js.grid && S.game?.renderGrid) S.game.renderGrid(js.grid);

      setResult("READY");
      setNote("");

    } catch (e) {
      setOnline(false);
      setResult("STATE ERROR", true);
      setNote(String(e?.message || e), true);
    }
  }

  async function spin() {
    if (spinning) return;
    spinning = true;
    if (ui.btnSpin) ui.btnSpin.disabled = true;

    try {
      S.audio?.unlock?.();
      S.audio?.sfx?.("start");

      setNote("SPINNING…");
      S.audio?.loop?.(true);

      // 비주얼은 game쪽 있으면 위임(없어도 상관없게)
      const visual = S.game?.spinVisual ? S.game.spinVisual(750) : Promise.resolve();

      const js = await S.api.spin({ bet });
      await visual;

      S.audio?.loop?.(false);
      S.audio?.sfx?.("stop");

      if (!js || js.ok === false) {
        setResult("SPIN ERROR", true);
        setNote(`spin fail: ${js?.error || "unknown"}`, true);
        // 돈 부족/오류면 자동 끔
        stopAuto();
        return;
      }

      // 업데이트
      const name = String(js.userName || js.name || js.displayName || "").trim();
      const idt = S.api.getUserIdentity?.() || {};
      const displayName = name || idt.name || idt.id || idt.u || "Guest";

      const ut = (js.ut ?? js.UT ?? js.totalUT ?? js.wallet ?? js.balance);
      setPlayerAndWallet({ displayName, ut: ut ?? 0 });

      setJackpot(js.jackpot ?? js.jackpotUT ?? js.jackpot_ut ?? 0);

      const srvBet = Number(js.bet);
      if (Number.isFinite(srvBet) && srvBet > 0) {
        bet = clamp(Math.round(srvBet / 5) * 5, 10, 1000);
        saveBet();
      }
      if (ui.uiBet) setText(ui.uiBet, fmtInt(bet));
      if (ui.betVal) setText(ui.betVal, fmtInt(bet));
      if (S.ui?.setKpi) S.ui.setKpi({ bet });

      if (js.grid && S.game?.renderGrid) S.game.renderGrid(js.grid);

      // 결과 메시지
      const betCharged = Number(js.betCharged ?? js.bet_cost ?? bet);
      const win = Number(js.win ?? js.payout ?? 0);
      const delta = win - betCharged;

      if (js.jackpotHit || js.isJackpot) {
        setResult(`JACKPOT!!! +${fmtInt(js.jackpotWin ?? win)} UT`);
        S.audio?.sfx?.("jackpot");
      } else if (delta > 0) {
        setResult(`WIN +${fmtInt(delta)} UT`);
        S.audio?.sfx?.("win");
      } else if (delta < 0) {
        setResult(`LOSE ${fmtInt(delta)} UT`);
        S.audio?.sfx?.("lose");
      } else {
        setResult("EVEN 0 UT");
      }

      setNote("");

    } catch (e) {
      S.audio?.loop?.(false);
      setResult("SPIN ERROR", true);
      setNote(String(e?.message || e), true);
      stopAuto();
    } finally {
      spinning = false;
      if (ui.btnSpin) ui.btnSpin.disabled = false;
    }
  }

  async function boot() {
    ensureApiBase();
    bridgeIdentityFromUniqueCurrentUser();
    loadBet();

    // UI 초기
    if (ui.uiBet) setText(ui.uiBet, fmtInt(bet));
    if (ui.betVal) setText(ui.betVal, fmtInt(bet));
    setResult("READY");
    setOnline(false);

    // paytable
    // module ui paytable이 있으면 그걸 쓰고, 없으면 cyberpunk paytable 생성
    if (S.ui?.buildPaytable) S.ui.buildPaytable();
    buildCyberPaytable();
    movePaytableUnderReels();

    ensureBetControls();
    ensureSoundButton();

    // bind buttons
    if (ui.btnSpin) ui.btnSpin.addEventListener("click", spin);
    if (ui.btnAuto) ui.btnAuto.addEventListener("click", () => {
      S.audio?.unlock?.();
      S.audio?.sfx?.("start");
      if (autoOn) stopAuto();
      else startAuto();
    });

    await loadState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
