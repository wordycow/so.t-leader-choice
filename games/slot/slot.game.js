/* games/slot/slot.game.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const ROWS = 3;
  const COLS = 5;

  // ✅ 심볼(네 폴더에 있는 이미지 전부 사용)
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
  // 2개는 “본전(배팅=지급)” 느낌으로 유지
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

  // ✅ /games/slot.html 기준 경로 자동 보정
  function isGamesPath_(){
    return /\/games\//.test(location.pathname);
  }
  const IMG_BASE = (S.IMG_BASE) ? String(S.IMG_BASE) : (isGamesPath_() ? "../img/slot" : "img/slot");
  const SOUND_BASE = (S.SOUND_BASE) ? String(S.SOUND_BASE) : (isGamesPath_() ? "../sounds" : "sounds");

  // ✅ 배경(유송 bg1~bg5) — PNG 확정
  const BG_LIST_DEFAULT = [
    `${IMG_BASE}/bg1.png`,
    `${IMG_BASE}/bg2.png`,
    `${IMG_BASE}/bg3.png`,
    `${IMG_BASE}/bg4.png`,
    `${IMG_BASE}/bg5.png`
  ];

  // ✅ 사운드 경로 (games/sounds)
  const SOUND = {
    start:  `${SOUND_BASE}/start-button-sound.MP3`,
    spin:   `${SOUND_BASE}/spining-sound.MP3`,
    stop:   `${SOUND_BASE}/stop-stop-stop-sound.MP3`,
    win:    `${SOUND_BASE}/win-sound.MP3`,
    lose:   `${SOUND_BASE}/lose-sound.MP3`,
    jackpot:`${SOUND_BASE}/jackpot-sound.MP3`,
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
    return `${IMG_BASE}/${id}.png`;
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

    const pick = (k, fallback) => {
      const v = Number(cfg?.[k]);
      return Number.isFinite(v) ? v : fallback;
    };

    WEIGHTS = {
      star1: pick("SLOT_W_STAR1", WEIGHTS.star1),
      star2: pick("SLOT_W_STAR2", WEIGHTS.star2),
      star3: pick("SLOT_W_STAR3", WEIGHTS.star3),
      pro1:  pick("SLOT_W_PRO1",  WEIGHTS.pro1),
      pro2:  pick("SLOT_W_PRO2",  WEIGHTS.pro2),
      pro3:  pick("SLOT_W_PRO3",  WEIGHTS.pro3),
      pro4:  pick("SLOT_W_PRO4",  WEIGHTS.pro4),
      pro5:  pick("SLOT_W_PRO5",  WEIGHTS.pro5),
      pro6:  pick("SLOT_W_PRO6",  WEIGHTS.pro6),
      pro7:  pick("SLOT_W_PRO7",  WEIGHTS.pro7),
      pro8:  pick("SLOT_W_PRO8",  WEIGHTS.pro8),
      pro9:  pick("SLOT_W_PRO9",  WEIGHTS.pro9),
      pro10: pick("SLOT_W_PRO10", WEIGHTS.pro10),
    };
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

    // 기존 배경보다 뒤쪽
    state.bgA = mk("slotBgA", -10);
    state.bgB = mk("slotBgB", -9);
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

  // ✅ “라스베가스 느낌” 결과 타입 롤
  function rollOutcomeType_(cfg){
    const ppm = Number(cfg?.SLOT_JACKPOT_PPM ?? 20); // 20ppm = 1/50,000
    const pJackpot = Math.max(0, ppm) / 1_000_000;

    // 기본 확률(필요하면 Config로 조정 가능하게 열어둠)
    const pFive  = Number(cfg?.SLOT_P_FIVE  ?? 0.006); // 0.6%
    const pFour  = Number(cfg?.SLOT_P_FOUR  ?? 0.030); // 3.0%
    const pThree = Number(cfg?.SLOT_P_THREE ?? 0.150); // 15%
    const pTwo   = Number(cfg?.SLOT_P_TWO   ?? 0.350); // 35% (자주 “본전/잔승” 느낌)

    const r = Math.random();
    if (r < pJackpot) return "jackpot";
    if (r < pJackpot + pFive) return "five";
    if (r < pJackpot + pFive + pFour) return "four";
    if (r < pJackpot + pFive + pFour + pThree) return "three";
    if (r < pJackpot + pFive + pFour + pThree + pTwo) return "two";
    return "lose";
  }

  function forceOneLine_(grid, type){
    const lowSyms  = ["star1","star2","star3","pro1","pro2","pro3"];
    const midSyms  = ["pro3","pro4","pro5","pro6"];
    const highSyms = ["pro7","pro8","pro9"];
    const pick = (arr)=> arr[Math.floor(Math.random()*arr.length)];

    const hitRow = Math.floor(Math.random()*3);

    // 1) 우선 전체 랜덤
    for(let r=0;r<3;r++){
      for(let c=0;c<5;c++){
        grid[r][c] = weightedPick();
      }
    }

    // 2) 히트 심볼/갯수 결정
    let sym = pick(lowSyms);
    let count = 0;

    if (type === "two")      { sym = pick(lowSyms);  count = 2; }
    else if (type === "three"){ sym = pick(lowSyms); count = 3; }
    else if (type === "four"){ sym = pick(midSyms);  count = 4; }
    else if (type === "five"){ sym = pick(highSyms); count = 5; }
    else if (type === "jackpot"){ sym = "pro10";     count = 5; }

    if (count > 0){
      for(let c=0;c<count;c++) grid[hitRow][c] = sym;
    }

    // 3) 과당첨 방지: 다른 줄 2연속 끊기(0-1칸)
    for(let r=0;r<3;r++){
      if (r === hitRow) continue;
      const a = grid[r][0];
      if (grid[r][1] === a){
        let repl = weightedPick();
        while(repl === a) repl = weightedPick();
        grid[r][1] = repl;
      }
    }

    return { row: hitRow, sym, count };
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

    // reel stop 타이밍(총 10초 안에서 순차)
    const startFast = 35;
    const endSlow   = 150;
    const stopAt = [7200, 8000, 8600, 9200, 9800];

    playOne("start");
    playLoop("spin");
    startBgCycle(200); // 0.2초

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

    // ✅ “라스베가스 확률”로 결과 강제
    const type = rollOutcomeType_(state.cfg);
    forceOneLine_(state.grid, type);
    renderGrid(state.grid);

    stopBgCycle();
    stopLoop("spin");

    const result = evaluate(state.grid, bet);

    // ✅ 결과 텍스트: 2개 본전(net=0)은 EVEN으로 표시
    let resultText = "LOSE";
    if (result.jackpot){
      playOne("jackpot");
      resultText = "JACKPOT";
    } else if (result.payout > 0){
      playOne("win");
      if (result.netDelta === 0) resultText = "WIN (EVEN)";
      else resultText = "WIN";
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

  // 노출
  S.game = S.game || {};
  S.game.buildReels = buildReels;
  S.game.renderGrid = renderGrid;
  S.game.spin = spin;
  S.game.setConfig = setConfig;
  S.game.setSoundEnabled = setSoundEnabled;
  S.game.getSoundEnabled = () => state.soundOn;

})(window.SLOT);
