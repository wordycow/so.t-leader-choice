(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  const UI = {
    el: null,
    cells: [],

    init() {
      this.el = {
        playerName: document.getElementById("playerName"),
        walletUt: document.getElementById("walletUt"),
        jackpotPool: document.getElementById("jackpotPool"),
        lastResult: document.getElementById("lastResult"),
        bet: document.getElementById("betUt"),

        betUp: document.getElementById("betUp"),
        betDown: document.getElementById("betDown"),
        spinBtn: document.getElementById("spinBtn"),
        autoBtn: document.getElementById("autoBtn"),
        soundBtn: document.getElementById("soundBtn"),

        stage: document.getElementById("slotStage"),
        grid: document.getElementById("slotGrid"),
        bg: document.getElementById("slotBgImg"),

        payWrap: document.getElementById("payWrap"),
        payToggle: document.getElementById("payToggle"),

        overlay: document.getElementById("loginOverlay"),

        banner: document.getElementById("jackpotBanner"),
        bannerText: document.getElementById("jackpotBannerText"),
      };

      // 엘리먼트가 없으면(파일 꼬임) 최소한 크래시는 막는다
      return this.el;
    },

    makeGrid() {
      if (!this.el?.grid) return;
      this.el.grid.innerHTML = "";
      this.cells = [];

      for (let i = 0; i < 15; i++) {
        const c = document.createElement("div");
        c.className = "cell";
        c.innerHTML = `<img alt="" />`;
        this.el.grid.appendChild(c);
        this.cells.push(c);
      }
    },

    setGrid(keys) {
      const cfg = CFG();
      if (!this.cells?.length) return;

      for (let i = 0; i < 15; i++) {
        const k = keys[i];
        const sym = cfg.SYMBOLS.find(s => s.key === k) || cfg.SYMBOLS[0];
        const img = this.cells[i].querySelector("img");
        if (img) img.src = cfg.ASSETS.imgBase + sym.img;
      }
    },

    clearHit() {
      if (!this.cells?.length) return;
      this.cells.forEach(c => c.classList.remove("hit"));
    },

    setHit(indices) {
      if (!this.cells?.length) return;
      indices.forEach(i => {
        const c = this.cells[i];
        if (c) c.classList.add("hit");
      });
    },

    setBackground(bgFile) {
      if (!this.el?.bg) return;
      this.el.bg.src = `img/slot/${bgFile}`;
    },

    setPlayer(user) {
      if (!this.el?.playerName) return;
      const name = user?.nickname || user?.name || user?.id || "-";
      this.el.playerName.textContent = name;
    },

    setWallet(n) {
      if (!this.el?.walletUt) return;
      this.el.walletUt.textContent = String(Math.floor(Number(n || 0)));
    },

    setJackpotPool(n) {
      if (!this.el?.jackpotPool) return;
      this.el.jackpotPool.textContent = String(Math.floor(Number(n || 0)));
    },

    setLast(text) {
      if (!this.el?.lastResult) return;
      this.el.lastResult.textContent = String(text || "");
    },

    setBet(n) {
      if (!this.el?.bet) return;
      this.el.bet.textContent = String(Math.floor(Number(n || 0)));
    },

    setButtonsDisabled(disabled) {
      if (!this.el) return;
      ["betUp","betDown","spinBtn","autoBtn","soundBtn"].forEach(k=>{
        if (this.el[k]) this.el[k].disabled = !!disabled;
      });
    },

    setAuto(on) {
      if (!this.el?.autoBtn) return;
      this.el.autoBtn.textContent = on ? "AUTO ON" : "AUTO OFF";
    },

    setSound(on) {
      if (!this.el?.soundBtn) return;
      this.el.soundBtn.textContent = on ? "SOUND ON" : "SOUND OFF";
    },

    showOverlay() {
      if (!this.el?.overlay) return;
      this.el.overlay.classList.remove("hidden");
    },

    hideOverlay() {
      if (!this.el?.overlay) return;
      this.el.overlay.classList.add("hidden");
    },

    showBanner(text) {
      if (!this.el?.banner || !this.el?.bannerText) return;
      this.el.bannerText.textContent = text;
      this.el.banner.classList.remove("hidden");
      // 애니메이션 리셋
      this.el.bannerText.style.animation = "none";
      void this.el.bannerText.offsetHeight;
      this.el.bannerText.style.animation = "";
    },

    hideBanner() {
      if (!this.el?.banner) return;
      this.el.banner.classList.add("hidden");
    },

    renderPaytable() {
      const cfg = CFG();
      if (!this.el?.payWrap) return;

      const rows = cfg.SYMBOLS.map(s => {
        const p3 = s.pay?.[3] ?? "-";
        const p4 = s.pay?.[4] ?? "-";
        const p5 = s.pay?.[5] ?? "-";
        return `
          <tr>
            <td>
              <div class="paySym">
                <img src="${cfg.ASSETS.imgBase + s.img}" alt="">
                <b>${s.label}</b>
              </div>
            </td>
            <td>${p3}x</td>
            <td>${p4}x</td>
            <td>${p5}x</td>
          </tr>
        `;
      }).join("");

      this.el.payWrap.innerHTML = `
        <table class="payTable">
          <thead>
            <tr><th>SYMBOL</th><th>3</th><th>4</th><th>5</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }
  };

  SLOT.ui = UI;
})();
