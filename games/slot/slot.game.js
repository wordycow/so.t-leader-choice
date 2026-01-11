/* games/slot/slot.game.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const ROWS = 3;
  const COLS = 5;

  const SYMBOL_IDS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  let WEIGHTS = {
    star1:22, star2:18, star3:14,
    pro1:12, pro2:9, pro3:7, pro4:5, pro5:4,
    pro6:3, pro7:2.5, pro8:2, pro9:1.5, pro10:1
  };

  // ✅ 2개는 "EVEN(본전)" = 배팅*1
  const PAY = {
    star1:{2:1,3:2,4:5,5:12},
    star2:{2:1,3:2.5,4:6,5:15},
    star3:{2:1,3:3,4:7,5:18},
    pro1 :{2:1,3:3.5,4:8,5:22},
    pro2 :{2:1,3:4,4:10,5:26},
    pro3 :{2:1,3:4.5,4:12,5:30},
    pro4 :{2:1,3:5,4:14,5:35},
    pro5 :{2:1,3:6,4:16,5:40},
    pro6 :{2:1,3:7,4:18,5:45},
    pro7 :{2:1,3:8,4:20,5:55},
    pro8 :{2:1,3:10,4:25,5:65},
    pro9 :{2:1,3:12,4:30,5:80},
    pro10:{2:1,3:15,4:40,5:100}
  };

  // ✅ bg1~bg5 PNG로 고정
  const BG_LIST_DEFAULT = [
    "img/slot/bg1.png",
    "img/slot/bg2.png",
    "img/slot/bg3.png",
    "img/slot/bg4.png",
    "img/slot/bg5.png"
  ];

  const SOUND = {
    start:  "sounds/start-button-sound.MP3",
    spin:   "sounds/spining-sound.MP3",
    stop:   "sounds/stop-stop-stop-sound.MP3",
    win:    "sounds/win-sound.MP3",
    lose:   "sounds/lose-sound.MP3",
    jackpot:"sounds/jackpot-sound.MP3",
  };

  const state = {
    cfg: null,
    grid: null,
    cells: null,
    spinning: false,
    soundOn: (localStorage.getItem("slotSoundOn") ?? "1") !== "0",
    bgTimer: null,
    bgIdx: 0,
    bgA: null,
    bgB: null,
    bgFlip: false,
    audio: {}
  };

  // ✅ "큰 컨테이너(stage)" 절대 잡지 말기 (UI 지워지는 원인)
  function findMount() {
    return (
      document.getElementById("reels") ||
      document.getElementById("reelMount") ||
      document.querySelector("[data-slot-reels]") ||
      document.querySelector(".slot-reels") ||
      document.querySelector(".reels") ||
      null
    );
  }

  function ensureMount() {
    let mount = findMount();
    if (mount) return mount;

    // 마지막 수단: reels 전용 박스만 만들어서 넣음 (절대 body 통째로 지우지 않음)
    const candidate =
      document.querySelector(".right-panel") ||
      document.querySelector(".panel-right") ||
      document.querySelector(".stage-wrap") ||
      document.body;

    mount = document.createElement("div");
    mount.id = "reels";
    mount.setAttribute("data-slot-reels","1");
    candidate.appendChild(mount);
    return mount;
  }

  function imgPath(id) {
    if (typeof S.IMG_PATH === "function") return S.IMG_PATH(id);
    return `img/slot/${id}.png`;
  }

  function ensureGridDOM(){
    const mount = ensureMount();
    if (!mount) return null;

    let gridEl = mount.querySelector(".slot-grid");
    if (!gridEl){
      gridEl = document.createElement("div");
      gridEl.className = "slot-grid";

      gridEl.style.display = "grid";
      gridEl.style.gridTemplateColumns = "repeat(5, 1fr)";
      gridEl.style.gridTemplateRows = "repeat(3, 1fr)";
      gridEl.style.gap = "12px";
      gridEl.style.width = "100%";
      gridEl.style.height = "100%";
      gridEl.style.padding = "18px";
      gridEl.style.boxSizing = "border-box";

      // ✅ mount.innerHTML = "" 금지 (UI 전체 날아감)
      mount.appendChild(gridEl);

      state.cells = Array.from({length: ROWS}, () => Array(COLS).fill(null));

      for (let r=0;r<ROWS;r++){
        for (let c=0;c<COLS;c++){
          const cell = document.createElement("div");
          cell.className = "slot-cell";
          cell.dataset.r = String(r);
          cell.dataset.c = String(c);
          cell.style.borderRadius = "16px";
          cell.style.overflow = "hidden";
          cell.style.display = "flex";
          cell.style.alignItems = "center";
          cell.style.justifyContent = "center";
          cell.style.background = "rgba(0,0,0,0.14)";
          cell.style.border = "1px solid rgba(255,255,255,0.10)";

          const img = document.createElement("img");
          img.alt = "";
          img.decoding = "async";
          img.loading = "eager";
          img.style.width = "78%";
          img.style.height = "78%";
          img.style.objectFit = "contain";
          img.style.filter = "drop-shadow(0 10px 18px rgba(0,0,0,0.35))";

          cell.appendChild(img);
          gridEl.appendChild(cell);
          state.cells[r][c] = img;
        }
      }
    }
    return gridEl;
  }

  function setSymbol(r,c,id){
    const img = state.cells?.[r]?.[c];
    if (!img) return;
    img.alt = id;
    img.src = imgPath(id);
    if (state.grid) state.grid[r][c] = id;
  }

  function renderGrid(grid){
    ensureGridDOM();
    const g = Array.isArray(grid) ? grid : defaultGrid();
    state.grid = g.map(row => row.slice());
    for (let r=0;r<ROWS;r++){
      for (let c=0;c<COLS;c++){
        setSymbol(r,c,state.grid[r][c]);
      }
    }
  }

  function defaultGrid(){
    return [
      ["star1","star2","star3","pro1","pro5"],
      ["star2","star3","pro1","pro5","pro10"],
      ["star1","star2","star3","pro1","pro5"]
    ];
  }

  function setConfig(cfg){
    state.cfg = cfg || null;
    if (!cfg) return;

    const pick = (k, fallback) => {
      const v = Number(cfg?.[k]);
      return Number.isFinite(v) ? v : fallback;
    };

    const m = {};
    m.star1 = pick("SLOT_W_STAR1", WEIGHTS.star1);
    m.star2 = pick("SLOT_W_STAR2", WEIGHTS.star2);
    m.star3 = pick("SLOT_W_STAR3", WEIGHTS.star3);
    m.pro1  = pick("SLOT_W_PRO1",  WEIGHTS.pro1);
    m.pro2  = pick("SLOT_W_PRO2",  WEIGHTS.pro2);
    m.pro3  = pick("SLOT_W_PRO3",  WEIGHTS.pro3);
    m.pro4  = pick("SLOT_W_PRO4",  WEIGHTS.pro4);
    m.pro5  = pick("SLOT_W_PRO5",  WEIGHTS.pro5);
    m.pro6  = pick("SLOT_W_PRO6",  WEIGHTS.pro6);
    m.pro7  = pick("SLOT_W_PRO7",  WEIGHTS.pro7);
    m.pro8  = pick("SLOT_W_PRO8",  WEIGHTS.pro8);
    m.pro9  = pick("SLOT_W_PRO9",  WEIGHTS.pro9);
    m.pro10 = pick("SLOT_W_PRO10", WEIGHTS.pro10);
    WEIGHTS = m;
  }

  function weightedPick(){
    let total = 0;
    for (const id of SYMBOL_IDS) total += (Number(WEIGHTS[id]) || 0);
    const t = Math.random() * total;
    let acc = 0;
    for (const id of SYMBOL_IDS){
      acc += (Number(WEIGHTS[id]) || 0);
      if (t <= acc) return id;
    }
    return "star1";
  }

  function preload(urls){
    urls.forEach(u => {
      const im = new Image();
      im.decoding = "async";
      im.src = u;
    });
  }

  function ensureBgLayers(){
    if (state.bgA && state.bgB) return;

    // ✅ 배경이 "안 보이는" 케이스 대비: 게임 루트는 위로 올려줌
    const gameRoot =
      document.querySelector(".slot-app") ||
      document.querySelector(".page-wrap") ||
      document.querySelector(".container") ||
      document.querySelector("#app");

    if (gameRoot){
      gameRoot.style.position = gameRoot.style.position || "relative";
      gameRoot.style.zIndex = "5";
    }

    const mk = (id, z) => {
      const d = document.createElement("div");
      d.id = id;
      d.style.position = "fixed";
      d.style.inset = "0";
      d.style.zIndex = String(z);
      d.style.pointerEvents = "none";
      d.style.backgroundSize = "cover";
      d.style.backgroundPosition = "center";
      d.style.opacity = "0";
      d.style.transition = "opacity 180ms linear";
      d.style.filter = "saturate(1.15) contrast(1.05)";
      document.body.appendChild(d);
      return d;
    };

    // ✅ 음수 zIndex 쓰지 말자(바디 배경 뒤로 숨어버림)
    state.bgA = mk("slotBgA", 1);
    state.bgB = mk("slotBgB", 2);
  }

  function setBg(url){
    ensureBgLayers();
    const on = state.bgFlip ? state.bgA : state.bgB;
    const off = state.bgFlip ? state.bgB : state.bgA;
    on.style.backgroundImage = `url("${url}")`;
    on.style.opacity = "0.95";
    off.style.opacity = "0";
    state.bgFlip = !state.bgFlip;
  }

  function startBgCycle(intervalMs=220){
    const list = (S.BG_LIST && Array.isArray(S.BG_LIST) && S.BG_LIST.length>=2)
      ? S.BG_LIST
      : BG_LIST_DEFAULT;

    preload(list);
    stopBgCycle();

    state.bgIdx = 0;
    setBg(list[state.bgIdx % list.length]);

    state.bgTimer = setInterval(() => {
      state.bgIdx++;
      setBg(list[state.bgIdx % list.length]);
    }, intervalMs);
  }

  function stopBgCycle(){
    if (state.bgTimer){
      clearInterval(state.bgTimer);
      state.bgTimer = null;
    }
  }

  function getAudio(key){
    if (state.audio[key]) return state.audio[key];
    const a = new Audio(SOUND[key]);
    a.preload = "auto";
    a.volume = 0.85;
    state.audio[key] = a;
    return a;
  }

  function playOne(key){
    if (!state.soundOn) return;
    try{
      const a = getAudio(key);
      a.pause();
      a.currentTime = 0;
      a.loop = false;
      a.play().catch(()=>{});
    }catch(e){}
  }

  function playLoop(key){
    if (!state.soundOn) return;
    try{
      const a = getAudio(key);
      a.loop = true;
      if (a.paused) a.play().catch(()=>{});
    }catch(e){}
  }

  function stopLoop(key){
    try{
      const a = getAudio(key);
      a.loop = false;
      a.pause();
      a.currentTime = 0;
    }catch(e){}
  }

  function setSoundEnabled(on){
    state.soundOn = !!on;
    localStorage.setItem("slotSoundOn", state.soundOn ? "1" : "0");
    if (!state.soundOn) stopLoop("spin");
  }

  function evaluate(grid, bet){
    let payout = 0;
    let jackpot = false;
    const lines = [];

    for (let r=0;r<ROWS;r++){
      const first = grid[r][0];
      let cnt = 1;
      for (let c=1;c<COLS;c++){
        if (grid[r][c] === first) cnt++;
        else break;
      }
      if (cnt >= 2){
        const mult = (PAY[first] && PAY[first][cnt]) ? PAY[first][cnt] : 0;
        const linePay = Math.floor(bet * mult);
        if (linePay > 0){
          payout += linePay;
          lines.push({ row:r, sym:first, count:cnt, pay:linePay });
        }
        if (first === "pro10" && cnt === 5) jackpot = true;
      }
    }

    const netDelta = payout - bet;
    const lossAmount = (payout <= 0) ? bet : 0;
    const hadHit = lines.length > 0;

    return { payout, netDelta, lossAmount, jackpot, lines, hadHit };
  }

  function rollOutcomeType_(cfg){
    // 잭팟: 기본 20ppm = 1/50,000
    const ppm = Number(cfg?.SLOT_JACKPOT_PPM ?? 20);
    const pJackpot = Math.max(0, ppm) / 1_000_000;

    const pFive  = Number(cfg?.SLOT_P_FIVE  ?? 0.004);
    const pFour  = Number(cfg?.SLOT_P_FOUR  ?? 0.020);
    const pThree = Number(cfg?.SLOT_P_THREE ?? 0.120);
    const pTwo   = Number(cfg?.SLOT_P_TWO   ?? 0.250);

    const r = Math.random();
    if (r < pJackpot) return "jackpot";
    if (r < pJackpot + pFive) return "five";
    if (r < pJackpot + pFive + pFour) return "four";
    if (r < pJackpot + pFive + pFour + pThree) return "three";
    if (r < pJackpot + pFive + pFour + pThree + pTwo) return "two";
    return "lose";
  }

  function forceOneLine_(grid, type){
    const lowSyms = ["star1","star2","star3","pro1","pro2","pro3"];
    const midSyms = ["pro3","pro4","pro5","pro6"];
    const highSyms= ["pro7","pro8","pro9"];
    const pick = (arr)=> arr[Math.floor(Math.random()*arr.length)];

    const row = Math.floor(Math.random()*3);

    // 기본 랜덤
    for(let r=0;r<3;r++){
      for(let c=0;c<5;c++){
        grid[r][c] = weightedPick();
      }
    }

    let sym = pick(lowSyms);
    let count = 0;

    if (type === "two")      { sym = pick(lowSyms);  count = 2; }
    else if (type === "three"){ sym = pick(lowSyms);  count = 3; }
    else if (type === "four") { sym = pick(midSyms);  count = 4; }
    else if (type === "five") { sym = pick(highSyms); count = 5; }
    else if (type === "jackpot"){ sym = "pro10";      count = 5; }

    if (count > 0){
      for(let c=0;c<count;c++) grid[row][c] = sym;
    }

    // 다른 줄 우연 2연속 방지
    for(let r=0;r<3;r++){
      if (r === row) continue;
      const first = grid[r][0];
      if (grid[r][1] === first){
        let repl = weightedPick();
        while(repl === first) repl = weightedPick();
        grid[r][1] = repl;
      }
    }

    return { row, sym, count };
  }

  async function spin({ bet=10 } = {}){
    if (state.spinning) return { ok:false, error:"busy" };
    state.spinning = true;

    ensureGridDOM();
    if (!state.grid) renderGrid(null);

    const totalMs = 10000;
    const startFast = 35;
    const endSlow   = 150;
    const stopAt = [7200, 8000, 8600, 9200, 9800];

    playOne("start");
    playLoop("spin");
    startBgCycle(220);

    const running = Array(COLS).fill(true);
    const stopPromises = [];

    for (let c=0;c<COLS;c++){
      const col = c;
      const t0 = performance.now();
      const tStop = stopAt[col];

      const tick = () => {
        if (!running[col]) return;

        const elapsed = performance.now() - t0;
        const ratio = Math.min(1, elapsed / tStop);
        const delay = Math.floor(startFast + (endSlow - startFast) * (ratio * ratio));

        for (let r=0;r<ROWS;r++){
          setSymbol(r, col, weightedPick());
        }
        setTimeout(tick, delay);
      };

      tick();

      stopPromises.push(new Promise(res => {
        setTimeout(() => {
          running[col] = false;
          playOne("stop");
          res(true);
        }, tStop);
      }));
    }

    await Promise.all(stopPromises);

    // ✅ 결과 강제(승률/체감 컨트롤)
    const type = rollOutcomeType_(state.cfg);
    forceOneLine_(state.grid, type);
    renderGrid(state.grid);

    stopBgCycle();
    stopLoop("spin");

    const result = evaluate(state.grid, bet);

    let resultText = "LOSE";
    if (result.jackpot){
      playOne("jackpot");
      resultText = `JACKPOT +${Math.max(0, result.netDelta)} UT`;
    } else if (result.netDelta > 0){
      playOne("win");
      resultText = `WIN +${result.netDelta} UT`;
    } else if (result.netDelta === 0 && result.hadHit){
      playOne("win");
      resultText = `EVEN (0 UT)`;
    } else {
      playOne("lose");
      resultText = "LOSE";
    }

    state.spinning = false;

    return {
      ok:true,
      grid: state.grid,
      ...result,
      resultText
    };
  }

  function buildReels(){
    renderGrid(null);
  }

  S.game = S.game || {};
  S.game.buildReels = buildReels;
  S.game.renderGrid = renderGrid;
  S.game.spin = spin;
  S.game.setConfig = setConfig;
  S.game.setSoundEnabled = setSoundEnabled;
  S.game.getSoundEnabled = () => state.soundOn;

})(window.SLOT);
