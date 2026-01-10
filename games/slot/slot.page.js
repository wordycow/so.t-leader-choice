(() => {
  const DEFAULT_API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  const $ = (id) => document.getElementById(id);

  const ui = {
    title: $("uiTitle"),
    player: $("uiPlayer"),
    wallet: $("uiWallet"),
    jackpot: $("uiJackpot"),
    result: $("uiResult"),
    bet: $("uiBet"),
    note: $("uiNote"),
    paytable: $("uiPaytable"),
    reels: $("uiReels"),
    reelWrap: $("uiReelWrap"),
    btnSpin: $("btnSpin"),
    btnAuto: $("btnAuto"),
  };

  let apiBase = DEFAULT_API_BASE;
  let identity = null;
  let state = null;

  let spinning = false;
  let auto = false;
  let autoTimer = null;

  // ---- Identity ----
  function readIdentity() {
    const raw = localStorage.getItem("uniqueCurrentUser");
    if (!raw) return null;
    try {
      const u = JSON.parse(raw);
      const id = String(u.id || "").trim().toLowerCase();
      const name = String(u.name || "").trim();
      const nickname = String(u.nickname || "").trim();
      if (!id) return null;
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

  // ---- UI helpers ----
  function setNote(msg) {
    if (ui.note) ui.note.textContent = msg || "";
  }

  function fmt(n) {
    const x = Number(n || 0);
    if (!Number.isFinite(x)) return "0";
    return String(Math.round(x * 100) / 100);
  }

  function flashFX(kind) {
    // kind: "WIN" | "JACKPOT" | "LOSE"
    if (!ui.reelWrap) return;
    ui.reelWrap.classList.remove("winFlash", "jackpotPulse", "shake");
    void ui.reelWrap.offsetWidth; // reflow to retrigger animations

    if (kind === "JACKPOT") {
      ui.reelWrap.classList.add("jackpotPulse", "winFlash");
      ui.reelWrap.classList.add("shake");
      if (ui.title) {
        ui.title.classList.add("glitch");
        ui.title.setAttribute("data-glitch", "THE UNIQUE SLOT");
        setTimeout(() => ui.title.classList.remove("glitch"), 1400);
      }
    } else if (kind === "WIN") {
      ui.reelWrap.classList.add("winFlash");
    } else {
      ui.reelWrap.classList.add("shake");
    }
  }

  // ---- Symbol styling (SVG) ----
  const SYMBOL_META = {
    star1: { hue: 35,  label: "STAR 1",  tier: "STAR", power: 1 },
    star2: { hue: 55,  label: "STAR 2",  tier: "STAR", power: 2 },
    star3: { hue: 75,  label: "STAR 3",  tier: "STAR", power: 3 },

    pro1:  { hue: 190, label: "PRO 1",   tier: "PRO",  power: 1 },
    pro2:  { hue: 205, label: "PRO 2",   tier: "PRO",  power: 2 },
    pro3:  { hue: 220, label: "PRO 3",   tier: "PRO",  power: 3 },
    pro4:  { hue: 235, label: "PRO 4",   tier: "PRO",  power: 4 },
    pro5:  { hue: 250, label: "PRO 5",   tier: "PRO",  power: 5 },
    pro6:  { hue: 265, label: "PRO 6",   tier: "PRO",  power: 6 },
    pro7:  { hue: 280, label: "PRO 7",   tier: "PRO",  power: 7 },
    pro8:  { hue: 295, label: "PRO 8",   tier: "PRO",  power: 8 },
    pro9:  { hue: 310, label: "PRO 9",   tier: "PRO",  power: 9 },
    pro10: { hue: 330, label: "PRO 10",  tier: "PRO",  power: 10 },
  };

  function hsl(h, s, l, a=1) {
    return `hsla(${h}, ${s}%, ${l}%, ${a})`;
  }

  function svgSymbol(id) {
    const m = SYMBOL_META[id] || { hue: 200, label: String(id||"-").toUpperCase(), tier:"", power: 1 };
    const H = m.hue;

    // STAR: spiky star glyph / PRO: shield glyph
    const isStar = String(m.tier).toUpperCase() === "STAR";

    // NOTE: We intentionally make this “neon” via filter+stroke gradients
    return `
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${hsl(H, 100, 62, 1)}"/>
      <stop offset="0.55" stop-color="${hsl((H+55)%360, 100, 58, 1)}"/>
      <stop offset="1" stop-color="${hsl((H+120)%360, 100, 55, 1)}"/>
    </linearGradient>
    <linearGradient id="g2" x1="1" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${hsl(H, 100, 75, .95)}"/>
      <stop offset="1" stop-color="${hsl((H+80)%360, 100, 65, .95)}"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feColorMatrix in="b" type="matrix"
        values="
          1 0 0 0 0
          0 1 0 0 0
          0 0 1 0 0
          0 0 0 18 -7" result="c"/>
      <feMerge>
        <feMergeNode in="c"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Outer ring -->
  <circle cx="100" cy="100" r="78"
    fill="none"
    stroke="${hsl(H, 100, 62, .45)}"
    stroke-width="8"
    opacity=".75"
    filter="url(#glow)"/>

  <circle cx="100" cy="100" r="70"
    fill="none"
    stroke="${hsl((H+70)%360, 100, 62, .28)}"
    stroke-width="2"
    opacity=".9"/>

  <!-- Main glyph -->
  ${
    isStar
      ? `
      <path d="M100 34
               L114 76
               L158 76
               L122 102
               L136 146
               L100 120
               L64 146
               L78 102
               L42 76
               L86 76 Z"
            fill="url(#g)"
            stroke="url(#g2)"
            stroke-width="4"
            filter="url(#glow)"/>
      `
      : `
      <path d="M100 34
               C132 34 152 48 152 70
               V106
               C152 132 128 156 100 168
               C72 156 48 132 48 106
               V70
               C48 48 68 34 100 34 Z"
            fill="url(#g)"
            stroke="url(#g2)"
            stroke-width="4"
            filter="url(#glow)"/>
      <path d="M66 78 H134" stroke="${hsl(H, 100, 80, .55)}" stroke-width="3" opacity=".8"/>
      `
  }

  <!-- Label -->
  <text x="100" y="186" text-anchor="middle"
        font-family="Share Tech Mono, ui-monospace, monospace"
        font-size="14"
        fill="${hsl(H, 100, 75, .92)}"
        opacity=".92"
        style="letter-spacing:.18em">
    ${m.label}
  </text>

  <!-- Power dots -->
  ${
    Array.from({length: Math.min(10, Math.max(1, m.power))})
      .map((_, i) => {
        const x = 52 + i * 10;
        return `<circle cx="${x}" cy="24" r="2.2" fill="${hsl(H, 100, 70, .9)}" opacity="${i < m.power ? .9 : .15}"/>`;
      }).join("")
  }
</svg>`;
  }

  function symbolImgPath(id) {
    // PNG는 "있으면 덤" (없어도 SVG로 완성)
    return `../img/slot/${id}.png`;
  }

  function renderPaytable(symbols) {
    if (!ui.paytable) return;
    ui.paytable.innerHTML = "";
    if (!Array.isArray(symbols) || !symbols.length) return;

    symbols.forEach((s) => {
      const id = String(s.id || "");
      const m = SYMBOL_META[id] || { hue: 200 };
      const badgeText = id.toUpperCase().replace("STAR","S").replace("PRO","P");

      const row = document.createElement("div");
      row.className = "ptItem";
      row.innerHTML = `
        <div class="ptLeft">
          <div class="badge" style="border-color: hsla(${m.hue},100%,60%,.28); box-shadow: 0 0 18px hsla(${m.hue},100%,60%,.16)">${badgeText}</div>
          <div style="opacity:.9">${id}</div>
        </div>
        <div class="ptMul">x${Number(s.payout || 0)}</div>
      `;
      ui.paytable.appendChild(row);
    });
  }

  function renderGrid(grid) {
    if (!ui.reels) return;
    ui.reels.innerHTML = "";

    const putCell = (symId) => {
      const cell = document.createElement("div");
      cell.className = "cell";
      const sym = document.createElement("div");
      sym.className = "sym";

      // SVG is primary
      sym.insertAdjacentHTML("beforeend", svgSymbol(symId));

      // PNG is optional overlay
      const img = document.createElement("img");
      img.src = symbolImgPath(symId);
      img.alt = symId;
      img.onerror = () => { img.remove(); }; // 없으면 그냥 제거
      sym.appendChild(img);

      cell.appendChild(sym);
      ui.reels.appendChild(cell);
    };

    if (!Array.isArray(grid) || grid.length !== 3) {
      for (let i = 0; i < 15; i++) putCell("star1");
      return;
    }

    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 5; c++) {
        putCell(String(grid[r][c] || "star1"));
      }
    }
  }

  // ---- API ----
  async function fetchState() {
    const res = await fetch(`${apiBase}/slot/state?id=${encodeURIComponent(identity.id)}`, {
      cache: "no-store",
    });
    const js = await res.json().catch(() => null);
    if (!js?.ok) throw new Error(js?.error || "state_failed");
    state = js;

    if (ui.player) ui.player.textContent = identity.display;
    if (ui.wallet) ui.wallet.textContent = fmt(js.ut);
    if (ui.jackpot) ui.jackpot.textContent = fmt(js.jackpot);
    if (ui.bet) ui.bet.textContent = fmt(js.bet);

    renderPaytable(js.symbols);
    renderGrid(null);

    saveBalanceToLocal(js.ut);
    setNote("READY. SPIN.");
  }

  async function spinOnce() {
    if (spinning) return;
    spinning = true;

    try {
      setNote("SPINNING...");
      if (ui.btnSpin) ui.btnSpin.disabled = true;

      const res = await fetch(`${apiBase}/slot/spin`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ id: identity.id }),
      });

      const js = await res.json().catch(() => null);
      if (!js?.ok) throw new Error(js?.error || "spin_failed");

      renderGrid(js.grid);

      if (ui.wallet) ui.wallet.textContent = fmt(js.ut);
      if (ui.jackpot) ui.jackpot.textContent = fmt(js.jackpot);

      const net = Number(js.net || 0);
      const betCharged = Number(js.betCharged || 0);
      const win = Number(js.win || 0);

      if (ui.result) {
        if (net > 0) ui.result.textContent = `+${fmt(net)}  (WIN ${fmt(win)})`;
        else if (net < 0) ui.result.textContent = `${fmt(net)}  (BET ${fmt(betCharged)})`;
        else ui.result.textContent = `0`;
      }

      saveBalanceToLocal(js.ut);

      if (js.winType === "JACKPOT") {
        setNote("JACKPOT. NO MERCY.");
        flashFX("JACKPOT");
      } else if (net > 0) {
        setNote("WIN CONFIRMED.");
        flashFX("WIN");
      } else if (net < 0) {
        setNote("DRAINED. AGAIN.");
        flashFX("LOSE");
      } else {
        setNote("STATIC. AGAIN.");
        flashFX("LOSE");
      }

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
      }, 1100);
    }
  }

  async function boot() {
    identity = readIdentity();
    if (!identity) {
      alert("로그인이 필요합니다. 게이트로 이동합니다.");
      location.href = "../the-unique-gate.html";
      return;
    }

    ui.btnSpin?.addEventListener("click", () => spinOnce().catch(e => setNote(String(e.message || e))));
    ui.btnAuto?.addEventListener("click", () => setAuto(!auto));

    await fetchState();

    setInterval(() => { fetchState().catch(() => {}); }, 8000);

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
