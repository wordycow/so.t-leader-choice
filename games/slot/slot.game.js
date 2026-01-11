/* games/slot/slot.game.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const ROWS = 3;
  const COLS = 5;

  // ✅ 기본 심볼(네 폴더에 있는 이미지 전부 사용)
  const SYMBOL_IDS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // ✅ 기본 가중치(Apps Script config 있으면 그걸로 덮어씀)
  let WEIGHTS = {
    star1:22, star2:18, star3:14,
    pro1:12, pro2:9, pro3:7, pro4:5, pro5:4,
    pro6:3, pro7:2.5, pro8:2, pro9:1.5, pro10:1
  };

  // ✅ 족보(라인 3개: 가로 3줄만)
  // 2개는 “본전(배팅=지급)”부터 시작해서 최소한 ‘졌는데 -가 표시’ 느낌 없게
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
    pro10:{2:1,3:15,4:40,5:100} // 5개면 JACKPOT 처리
  };

  // ✅ 배경(유송이 말한 bg1~bg5)
  const BG_LIST_DEFAULT = [
    "img/slot/bg1.jpg",
    "img/slot/bg2.jpg",
    "img/slot/bg3.jpg",
    "img/slot/bg4.jpg",
    "img/slot/bg5.jpg"
  ];

  // ✅ 사운드 경로 (games/sounds)
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

  function findMount() {
    return (
      document.getElementById("reels") ||
      document.getElementById("reelMount") ||
      document.getElementById("slotStage") ||
      document.getElementById("stage") ||
      document.querySelector("[data-slot-stage]") ||
      document.querySelector(".slot-stage") ||
      document.querySelector(".stage") ||
      null
    );
  }

  function ensureMount() {
    let mount = findMount();
    if (mount) return mount;

    const candidate =
      document.getElementById("gameStage") ||
      document.querySelector(".right-panel") ||
      document.querySelector(".panel-right") ||
      document.querySelector(".stage-wrap") ||
      document.querySelector(".board") ||
      document.body;

    mount = document.createElement("div");
    mount.id = "reels";
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
      // ✅ 기존 CSS가 있으면 그걸 쓰고, 없으면 최소한만 보이게
      gridEl.style.display = "grid";
      gridEl.style.gridTemplateColumns = "repeat(5, 1fr)";
      gridEl.style.gridTemplateRows = "repeat(3, 1fr)";
      gridEl.style.gap = "12px";
      gridEl.style.width = "100%";
      gridEl.style.height = "100%";
      gridEl.style.padding = "18px";
      gridEl.style.boxSizing = "border-box";
      mount.innerHTML = "";
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

    // ✅ Apps Script Config 값이 있으면 가중치 덮어쓰기
    const m = {};
    const pick = (k, fallback) => {
      const v = Number(cfg?.[k]);
      return Number.isFinite(v) ? v : fallback;
    };

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

    // 기존 배경보다 뒤에 깔리도록 아주 뒤쪽
    state.bgA = mk("slotBgA", -5);
    state.bgB = mk("slotBgB", -4);
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

  function startBgCycle(intervalMs=200){
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
    // 멈출 때는 마지막 배경은 유지(현란함 유지)
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

    return { payout, netDelta, lossAmount, jackpot, lines };
  }

  // ✅ 10초 스핀: 빠르게 시작 → 점점 늦추며 릴별로 “탁탁탁” 멈춤
  async function spin({ bet=10 } = {}){
    if (state.spinning) return { ok:false, error:"busy" };
    state.spinning = true;

    ensureGridDOM();
    if (!state.grid) renderGrid(null);

    const totalMs = 10000;
    const startFast = 35;    // 초반 속도(빠르게)
    const endSlow   = 150;   // 멈추기 직전 느리게

    // reel stop 타이밍(총 10초 안에서 순차)
    const stopAt = [7200, 8000, 8600, 9200, 9800];

    playOne("start");
    playLoop("spin");
    startBgCycle(200);

    const running = Array(COLS).fill(true);
    const stopPromises = [];

    // 각 릴(열) 업데이트 루프 (setTimeout 기반 가변 딜레이)
    for (let c=0;c<COLS;c++){
      const col = c;
      const t0 = performance.now();
      const tStop = stopAt[col];

      const tick = () => {
        if (!running[col]) return;

        const elapsed = performance.now() - t0;
        const ratio = Math.min(1, elapsed / tStop);
        const delay = Math.floor(startFast + (endSlow - startFast) * (ratio * ratio)); // 감속 곡선

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

    // 전체 종료 대기
    await Promise.all(stopPromises);

    stopBgCycle();
    stopLoop("spin");

    const result = evaluate(state.grid, bet);
    let resultText = "LOSE";

    if (result.jackpot){
      playOne("jackpot");
      resultText = `JACKPOT +${Math.max(0, result.netDelta)} UT`;
    } else if (result.payout > 0){
      playOne("win");
      resultText = `WIN +${Math.max(0, result.netDelta)} UT`;
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

  // 초기 릴 생성(호환)
  function buildReels(){
    renderGrid(null);
  }

  // 노출
  S.game = S.game || {};
  S.game.buildReels = buildReels;
  S.game.renderGrid = renderGrid;
  S.game.spin = spin;
  S.game.setConfig = setConfig;
  S.game.setSoundEnabled = setSoundEnabled;
  S.game.getSoundEnabled = () => state.soundOn;

})(window.SLOT);
