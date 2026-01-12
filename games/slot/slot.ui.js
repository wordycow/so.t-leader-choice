(function () {
  window.SLOT = window.SLOT || {};
  const { ASSET, SYMBOLS } = window.SLOT.config;

  function clamp(n,min,max){ return Math.max(min, Math.min(max, n)); }
  function round2(n){ return Math.round(n*100)/100; }
  function fmt(n){
    const x = Number(n||0);
    if (!Number.isFinite(x)) return "0";
    if (Math.abs(x) >= 1000) return x.toLocaleString("en-US");
    return (Math.round(x*100)/100).toString();
  }

  const UI = {
    el: null,
    cells: [],
    gridKeys: [],
    init() {
      this.el = {
        bgA: document.getElementById("bgA"),
        bgB: document.getElementById("bgB"),
        bgFlash: document.getElementById("bgFlash"),

        payCard: document.getElementById("payCard"),
        payToggle: document.getElementById("payToggle"),
        payList: document.getElementById("payList"),
        slotGrid: document.getElementById("slotGrid"),

        dotLogin: document.getElementById("dotLogin"),
        playerName: document.getElementById("playerName"),
        wallet: document.getElementById("wallet"),
        jackpot: document.getElementById("jackpot"),
        lastResult: document.getElementById("lastResult"),

        bet: document.getElementById("bet"),
        betDown: document.getElementById("betDown"),
        betUp: document.getElementById("betUp"),

        autoBtn: document.getElementById("autoBtn"),
        soundBtn: document.getElementById("soundBtn"),
        spinBtn: document.getElementById("spinBtn"),

        banner: document.getElementById("jackpotBanner"),
        bannerText: document.getElementById("jackpotText"),

        floatWin: document.getElementById("floatWin"),
        overlay: document.getElementById("overlay"),
      };
    },

    setLast(msg){ this.el.lastResult.textContent = msg; },
    showOverlay(on){ this.el.overlay.classList.toggle("on", !!on); },

    toast(text){
      const el = this.el.floatWin;
      el.textContent = text;
      el.classList.remove("on");
      void el.offsetWidth;
      el.classList.add("on");
    },

    animateNumber(node, from, to, ms=650){
      from = Number(from||0); to = Number(to||0);
      const t0 = performance.now();
      const self = this;
      function step(t){
        const p = clamp((t - t0) / ms, 0, 1);
        const e = 1 - Math.pow(1-p, 3);
        const v = from + (to-from) * e;
        node.textContent = fmt(round2(v));
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    },

    renderPaytable(){
      this.el.payList.innerHTML = "";
      for (const s of SYMBOLS){
        const row = document.createElement("div");
        row.className = "pay-item";
        row.innerHTML = `
          <img src="${ASSET.imgBase + s.img}" alt="${s.key}" onerror="this.style.display='none'">
          <div class="meta">
            <div class="name">${s.label}</div>
            <div class="rule">2연속: EVEN(±0) / 3연속: x${s.pay[3]} / 4연속: x${s.pay[4]} / 5연속: x${s.pay[5]} (JACKPOT)</div>
          </div>
        `;
        this.el.payList.appendChild(row);
      }
    },

    makeGrid(){
      this.el.slotGrid.innerHTML = "";
      this.cells = [];
      for (let i=0;i<15;i++){
        const c = document.createElement("div");
        c.className = "cell";
        c.innerHTML = `<img alt="slot" />`;
        this.el.slotGrid.appendChild(c);
        this.cells.push(c);
      }
    },

    setGrid(keys){
      this.gridKeys = keys.slice();
      for (let i=0;i<15;i++){
        const k = keys[i];
        const sym = SYMBOLS.find(x=>x.key===k) || SYMBOLS[0];
        const img = this.cells[i].querySelector("img");
        img.src = ASSET.imgBase + sym.img;
        img.onerror = ()=>{ img.style.display="none"; };
        img.style.display="block";
      }
    },

    flashCells(on){
      this.cells.forEach(c => c.classList.toggle("flash", !!on));
    },

    // ✅ 배경 교체(두 레이어 크로스페이드)
    bg: {
      side: "A",
      set(url){
        const ui = UI;
        const a = ui.el.bgA, b = ui.el.bgB;
        if (!a || !b) return;

        if (this.side === "A") {
          b.style.backgroundImage = `url("${url}")`;
          b.classList.add("on");
          a.classList.remove("on");
          this.side = "B";
        } else {
          a.style.backgroundImage = `url("${url}")`;
          a.classList.add("on");
          b.classList.remove("on");
          this.side = "A";
        }
      },
      flash(on){
        const ui = UI;
        if (!ui.el.bgFlash) return;
        ui.el.bgFlash.classList.toggle("on", !!on);
      }
    },

    setBanner(msg){
      this.el.bannerText.textContent = msg;
      this.el.banner.classList.add("on");
    },
    hideBanner(){
      this.el.banner.classList.remove("on");
    },
  };

  window.SLOT.ui = UI;
})();
