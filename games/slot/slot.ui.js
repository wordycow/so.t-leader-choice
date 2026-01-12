(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  const el = {};
  const cells = []; // 15개

  function $(id){ return document.getElementById(id); }

  function setPageBg(file) {
    const url = `url("${CFG().ASSET.imgBase}/${file}")`;
    document.documentElement.style.setProperty("--slot-bg", url);
  }

  function preloadImages() {
    const base = CFG().ASSET.imgBase;
    const imgs = [
      ...CFG().ASSET.bgFiles.map(f => `${base}/${f}`),
      ...CFG().SYMBOLS.map(s => `${base}/${s.file}`)
    ];
    imgs.forEach(src => { const i = new Image(); i.src = src; });
  }

  function buildGrid() {
    const grid = el.slotGrid;
    grid.innerHTML = "";
    cells.length = 0;

    const { rows, cols } = CFG().GRID;
    for (let r=0; r<rows; r++){
      for (let c=0; c<cols; c++){
        const cell = document.createElement("div");
        cell.className = "cell";
        const img = document.createElement("img");
        img.alt = "";
        img.draggable = false;
        cell.appendChild(img);
        grid.appendChild(cell);
        cells.push({ cell, img, key: null, r, c });
      }
    }
  }

  function keyToSrc(key){
    const m = CFG().SYMBOL_MAP[key];
    if (!m) return "";
    return `${CFG().ASSET.imgBase}/${m.file}`;
  }

  function setGrid(keys){
    if (!Array.isArray(keys) || keys.length !== cells.length) return;
    for (let i=0;i<cells.length;i++){
      const k = keys[i];
      cells[i].key = k;
      cells[i].img.src = keyToSrc(k);
    }
  }

  function setLast(text){ el.lastResult.textContent = text; }
  function setPlayer(name){ el.playerName.textContent = name || "-"; }
  function setWallet(n){ el.walletUt.textContent = String(n ?? 0); }
  function setJackpot(n){ el.jackpotPool.textContent = String(n ?? 0); }
  function setBet(n){ el.betUt.textContent = String(n ?? 0); }

  function renderPaytable(){
    const wrap = el.payWrap;
    wrap.innerHTML = "";
    const ul = document.createElement("ul");
    ul.className = "payList";
    CFG().PAYTABLE_TEXT.forEach(t => {
      const li = document.createElement("li");
      li.textContent = t;
      ul.appendChild(li);
    });
    wrap.appendChild(ul);
  }

  function setPayCollapsed(collapsed){
    const card = el.paytableCard;
    card.classList.toggle("collapsed", !!collapsed);
    el.payToggle.textContent = collapsed ? "펼치기" : "접기";
    localStorage.setItem(CFG().STORAGE_KEYS.payCollapsed, collapsed ? "1" : "0");
  }

  function togglePay(){
    const collapsed = el.paytableCard.classList.contains("collapsed");
    setPayCollapsed(!collapsed);
  }

  function showLoginOverlay(show){
    el.loginOverlay.classList.toggle("hidden", !show);
  }

  function showSetupOverlay(show){
    el.setupOverlay.classList.toggle("hidden", !show);
  }

  function flashWinLine(runLen){
    // 가운데 줄(인덱스 5~9)에서 연속되는 구간을 하이라이트
    const midStart = 5;
    const mid = cells.slice(midStart, midStart+5);
    mid.forEach(x => x.cell.classList.remove("hit"));

    if (runLen < 2) return;

    // 연속 최대 구간 찾기
    let best = {len:1, s:0, key: mid[0].key};
    for (let s=0;s<5;s++){
      let k = mid[s].key;
      let len=1;
      for (let j=s+1;j<5;j++){
        if (mid[j].key === k) len++;
        else break;
      }
      if (len > best.len) best = {len, s, key:k};
    }

    for (let i=best.s;i<best.s+best.len;i++){
      mid[i].cell.classList.add("hit");
    }
  }

  function initDom(){
    el.slotGrid = $("slotGrid");
    el.playerName = $("playerName");
    el.walletUt = $("walletUt");
    el.jackpotPool = $("jackpotPool");
    el.lastResult = $("lastResult");
    el.betUt = $("betUt");

    el.paytableCard = $("paytableCard");
    el.payWrap = $("payWrap");
    el.payToggle = $("payToggle");

    el.loginOverlay = $("loginOverlay");
    el.setupOverlay = $("setupOverlay");

    el.payToggle.addEventListener("click", togglePay);

    const saved = localStorage.getItem(CFG().STORAGE_KEYS.payCollapsed);
    setPayCollapsed(saved === "1");
  }

  SLOT.UI = {
    init(){
      initDom();
      preloadImages();
      buildGrid();
      renderPaytable();
      // 초기 배경
      setPageBg(CFG().ASSET.bgFiles[0]);
    },
    setPageBg,
    setGrid,
    setLast,
    setPlayer,
    setWallet,
    setJackpot,
    setBet,
    flashWinLine,
    showLoginOverlay,
    showSetupOverlay,
    setPayCollapsed
  };
})();
