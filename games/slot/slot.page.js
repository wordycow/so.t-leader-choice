(() => {
  // ✅ 네 워커 베이스 URL (필요하면 여기만 바꾸면 됨)
  const DEFAULT_API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  const $ = (id) => document.getElementById(id);

  const ui = {
    player: $("uiPlayer"),
    wallet: $("uiWallet"),
    jackpot: $("uiJackpot"),
    result: $("uiResult"),
    bet: $("uiBet"),
    note: $("uiNote"),
    paytable: $("uiPaytable"),
    reels: $("uiReels"),
    btnSpin: $("btnSpin"),
    btnAuto: $("btnAuto"),
  };

  let apiBase = DEFAULT_API_BASE;
  let identity = null;
  let state = null;

  let spinning = false;
  let auto = false;
  let autoTimer = null;

  function readIdentity() {
    const raw = localStorage.getItem("uniqueCurrentUser");
    if (!raw) return null;
    try {
      const u = JSON.parse(raw);
      const id = String(u.id || "").trim().toLowerCase();
      const name = String(u.name || "").trim();
      const nickname = String(u.nickname || "").trim();
      if (!id) return null;

      // 표시용: 기본은 이름, 없으면 id
      const display = name || nickname || id;

      return { id, name, nickname, display };
    } catch {
      return null;
    }
  }

  function saveBalanceToLocal(newBal) {
    const raw = localStorage.getItem("uniqueCurrentUser");
    if (!raw) return;
    try {
      const u = JSON.parse(raw);
      u.balance = Number(newBal || 0);
      localStorage.setItem("uniqueCurrentUser", JSON.stringify(u));
      localStorage.setItem("myUtPoints", String(Number(newBal || 0)));
    } catch {}
  }

  function setNote(msg) {
    if (ui.note) ui.note.textContent = msg || "";
  }

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return String(Math.round(x * 100) / 100);
  }

  function symbolImgPath(id) {
    // ✅ 네 리포에 심볼 PNG가 있으면 여기 경로로 맞추면 됨
    // 일단 없으면 텍스트로 fallback
    return `../img/slot/${id}.png`;
  }

  function renderPaytable(symbols) {
    if (!ui.paytable) return;
    ui.paytable.innerHTML = "";
    if (!Array.isArray(symbols) || !symbols.length) return;

    symbols.forEach((s) => {
      const row = document.createElement("div");
      row.className = "ptItem";
      row.innerHTML = `
        <div class="ptLeft">
          <div class="badge">${String(s.id).toUpperCase().replace("STAR","S").replace("PRO","P")}</div>
          <div>${s.id}</div>
        </div>
        <div>x${s.payout}</div>
      `;
      ui.paytable.appendChild(row);
    });
  }

  function renderGrid(grid) {
    if (!ui.reels) return;
    ui.reels.innerHTML = "";
    if (!Array.isArray(grid) || grid.length !== 3) {
      // 기본 빈칸 15개
      for (let i = 0; i < 15; i++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        cell.innerHTML = `<div class="fallback">-</div>`;
        ui.reels.appendChild(cell);
      }
      return;
    }

    // grid: [ [..5], [..5], [..5] ]
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 5; c++) {
        const sym = String(grid[r][c] || "-");
        const cell = document.createElement("div");
        cell.className = "cell";

        const img = document.createElement("img");
        img.src = symbolImgPath(sym);
        img.alt = sym;
        img.onerror = () => {
          cell.innerHTML = `<div class="fallback">${sym}</div>`;
        };

        cell.appendChild(img);
        ui.reels.appendChild(cell);
      }
    }
  }

  async function fetchState() {
    const res = await fetch(`${apiBase}/slot/state?id=${encodeURIComponent(identity.id)}`, {
      cache: "no-store",
    });
    const js = await res.json().catch(() => null);
    if (!js?.ok) throw new Error(js?.error || "state_failed");
    state = js;

    // UI 반영
    if (ui.player) ui.player.textContent = identity.display;
    if (ui.wallet) ui.wallet.textContent = fmt(js.ut);
    if (ui.jackpot) ui.jackpot.textContent = fmt(js.jackpot);
    if (ui.bet) ui.bet.textContent = fmt(js.bet);

    renderPaytable(js.symbols);
    renderGrid(null);

    saveBalanceToLocal(js.ut);
    setNote("준비 완료. SPIN 눌러라.");
  }

  async function spinOnce() {
    if (spinning) return;
    spinning = true;

    try {
      setNote("스핀 중...");
      if (ui.btnSpin) ui.btnSpin.disabled = true;

      const res = await fetch(`${apiBase}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ id: identity.id }),
      });

      const js = await res.json().catch(() => null);
      if (!js?.ok) throw new Error(js?.error || "spin_failed");

      // grid
      renderGrid(js.grid);

      // 잔액/잭팟
      if (ui.wallet) ui.wallet.textContent = fmt(js.ut);
      if (ui.jackpot) ui.jackpot.textContent = fmt(js.jackpot);

      // ✅ LAST RESULT: net(딴/잃은 값)
      const net = Number(js.net || 0);
      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);

      if (ui.result) {
        if (net > 0) ui.result.textContent = `+${fmt(net)} (WIN ${fmt(win)})`;
        else if (net < 0) ui.result.textContent = `${fmt(net)} (BET ${fmt(betCharged)})`;
        else ui.result.textContent = `0`;
      }

      saveBalanceToLocal(js.ut);

      if (js.winType === "JACKPOT") setNote("잭팟이다.");
      else if (net > 0) setNote("따먹었다.");
      else if (net < 0) setNote("잃었다. 다음.");
      else setNote("변동 없음.");

    } finally {
      spinning = false;
      if (ui.btnSpin) ui.btnSpin.disabled = false;
    }
  }

  function setAuto(on) {
    auto = !!on;
    if (ui.btnAuto) ui.btnAuto.textContent = auto ? "AUTO ON" : "AUTO OFF";

    if (autoTimer) {
      clearInterval(autoTimer);
      autoTimer = null;
    }
    if (auto) {
      autoTimer = setInterval(() => {
        if (!spinning) spinOnce().catch(e => setNote(String(e.message || e)));
      }, 1200);
    }
  }

  async function boot() {
    identity = readIdentity();
    if (!identity) {
      alert("로그인이 필요합니다. 게이트로 이동합니다.");
      location.href = "../the-unique-gate.html";
      return;
    }

    // 버튼 바인딩
    ui.btnSpin?.addEventListener("click", () => spinOnce().catch(e => setNote(String(e.message || e))));
    ui.btnAuto?.addEventListener("click", () => setAuto(!auto));

    // 초기 상태
    await fetchState();

    // ✅ sheet에서 바뀐 UT가 사이트에도 반영되게 주기적 sync
    setInterval(() => {
      fetchState().catch(() => {});
    }, 8000);

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") fetchState().catch(() => {});
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    boot().catch(e => {
      console.error(e);
      setNote(String(e.message || e));
    });
  });
})();
