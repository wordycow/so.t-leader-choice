/* games/slot/slot.game.js */
window.SLOT = window.SLOT || {};
(function (S) {
  "use strict";

  const ROWS = 3;
  const COLS = 5;

  // ✅ 심볼(네 폴더 이미지 전부)
  const SYMBOL_IDS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // ✅ 기본 가중치(Apps Script Config 있으면 덮어씀)
  let WEIGHTS = {
    star1:22, star2:18, star3:14,
    pro1:12, pro2:9, pro3:7, pro4:5, pro5:4,
    pro6:3, pro7:2.5, pro8:2, pro9:1.5, pro10:1
  };

  // ✅ 족보(가로 3줄만 평가 / 2개는 본전 1x)
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

  // ✅ 배경 (유송: png 확정)
  const BG_LIST_DEFAULT = [
  "img/slot/bg1.png",
  "img/slot/bg2.png",
  "img/slot/bg3.png",
  "img/slot/bg4.png",
  "img/slot/bg5.png"
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
    cells: null,      // [[{cellEl,imgEl}]]
    spinning: false,
    soundOn: (localStorage.getItem("slotSoundOn") ?? "1") !== "0",
    bgTimer: null,
    bgIdx: 0,
    bgA: null,
    bgB: null,
    bgLight: null,
    bgFlip: false,
    audio: {}
  };

  function imgPath(id) {
    if (typeof S.IMG_PATH === "function") return S.IMG_PATH(id);
    return `img/slot/${id}.png`;
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
      pro1 : pick("SLOT_W_PRO1",  WEIGHTS.pro1),
      pro2 : pick("SLOT_W_PRO2",  WEIGHTS.pro2),
      pro3 : pick("SLOT_W_PRO3",  WEIGHTS.pro3),
      pro4 : pick("SLOT_W_PRO4",  WEIGHTS.pro4),
      pro5 : pick("SLOT_W_PRO5",  WEIGHTS.pro5),
      pro6 : pick("SLOT_W_PRO6",  WEIGHTS.pro6),
      pro7 : pick("SLOT_W_PRO7",  WEIGHTS.pro7),
      pro8 : pick("SLOT_W_PRO8",  WEIGHTS.pro8),
      pro9 : pick("SLOT_W_PRO9",  WEIGHTS.pro9),
      pro10: pick("SLOT_W_PRO10", WEIGHTS.pro10),
    };
  }

  // ✅ slot.html 고정 타겟: uiReels
  function getReelsMount(){
    return (
      document.getElementById("uiReels") ||
      document.querySelector(".reels") ||
      document.getElementById("reels") ||
      document.getElementById("reelMount") ||
      document.getElementById("slotStage") ||
      null
    );
  }

  function ensureGridDOM(){
    const mount = getReelsMount();
    if (!mount) return null;

    // mount는 slot.html의 <div class="reels" id="uiReels"></div>
    mount.innerHTML = "";
    state.cells = Array.from({length: ROWS}, () => Array(COLS).fill(null));

    for (let r=0;r<ROWS;r++){
      for (let c=0;c<COLS;c++){
        const cell = document.createElement("div");
        cell.className = "cell";

        const sym = document.createElement("div");
        sym.className = "sym";

        const img = document.createElement("img");
        img.alt = "";
        img.decoding = "async";
        img.loading = "eager";
        img.style.width = "78%";
        img.style.height = "78%";
        img.style.objectFit = "contain";
        img.style.filter = "drop-shadow(0 10px 18px rgba(0,0,0,0.35))";

        sym.appendChild(img);
        cell.appendChild(sym);
        mount.appendChild(cell);

        state.cells[r][c] = { cellEl: cell, imgEl: img };
      }
    }
    return mount;
  }

  function setSymbol(r,c,id){
    const obj = state.cells?.[r]?.[c];
    if (!obj) return;

    obj.imgEl.alt = id;
    obj.imgEl.src = imgPath(id);

    // tick 애니메이션(슬롯 느낌)
    obj.cellEl.classList.remove("tick");
    // 강제로 reflow
    void obj.cellEl.offsetWidth;
    obj.cellEl.classList.add("tick");

    if (state.grid) state.grid[r][c] = id;
  }

  function defaultGrid(){
    return [
      ["star1","star2","star3","pro1","pro5"],
      ["star2","star3","pro1","pro5","pro10"],
      ["star1","star2","star3","pro1","pro5"]
    ];
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

  // ✅ 결과 타입 확률 (라스베가스 느낌: 잔잔한 히트는 자주, 잭팟은 극희귀)
  function rollOutcomeType_(cfg){
    // 잭팟: 20ppm = 1/50,000 (스핀이 월 5만이면 “대충 월1회” 체감)
    const ppm = Number(cfg?.SLOT_JACKPOT_PPM ?? 20);
    const pJackpot = Math.max(0, ppm) / 1_000_000;

    const r = Math.random();
    if (r < pJackpot) return "jackpot";
    if (r < pJackpot + 0.006) return "five";     // 0.6% (큰 승리)
    if (r < pJackpot + 0.006 + 0.030) return "four";   // 3%
    if (r < pJackpot + 0.006 + 0.030 + 0.150) return "three"; // 15%
    if (r < pJackpot + 0.006 + 0.030 + 0.150 + 0.350) return "two"; // 35% (자주 맞는 느낌/본전 포함)
    return "lose";
  }

  function forceOneLine_(grid, type){
    // 한 줄만 확정 히트 + 나머지는 랜덤(과당첨 방지)
    const lowSyms = ["star1","star2","star3","pro1","pro2","pro3"];
    const midSyms = ["pro3","pro4","pro5","pro6"];
    const highSyms= ["pro7","pro8","pro9"];
    const pick = (arr)=> arr[Math.floor(Math.random()*arr.length)];

    // 1) 랜덤 깔기
    for(let r=0;r<ROWS;r++){
      for(let c=0;c<COLS;c++){
        grid[r][c] = weightedPick();
      }
    }

    // 2) 한 줄 고르기
    const row = Math.floor(Math.random()*ROWS);

    let sym = pick(lowSyms);
    let count = 0;

    if (type === "two")    { sym = pick(lowSyms);  count = 2; }
    if (type === "three")  { sym = pick(lowSyms);  count = 3; }
    if (type === "four")   { sym = pick(midSyms);  count = 4; }
    if (type === "five")   { sym = pick(highSyms); count = 5; }
    if (type === "jackpot"){ sym = "pro10";        count = 5; }

    // 3) 강제 매치(왼쪽부터)
    for(let c=0;c<count;c++) grid[row][c] = sym;

    // 4) 다른 줄 우연 2연속 끊기
    for(let r=0;r<ROWS;r++){
      if (r === row) continue;
      const first = grid[r][0];
      if (grid[r][1] === first){
        let repl = weightedPick();
        while(repl === first) repl = weightedPick();
        grid[r][1] = repl;
      }
    }
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

  function preload(urls){
    urls.forEach(u => { try{ const im=new Image(); im.decoding="async"; im.src=u; }catch(e){} });
  }

  function ensureBgLayers(){
    if (state.bgA && state.bgB && state.bgLight) return;

    const ensureStyle = () => {
      if (document.getElementById("slotBgFxStyle")) return;
      const st = document.createElement("style");
      st.id = "slotBgFxStyle";
      st.textContent = `
        @keyframes slotLightSweep {
          0%   { transform: translateX(-8%) rotate(-8deg); opacity: .15; }
          50%  { transform: translateX(8%)  rotate(8deg);  opacity: .35; }
          100% { transform: translateX(-8%) rotate(-8deg); opacity: .15; }
        }
      `;
      document.head.appendChild(st);
    };
    ensureStyle();

    const mk = (id, z) => {
      const d = document.createElement("div");
      d.id = id;
      d.style.position = "fixed";
      d.style.inset = "0";
      d.style.zIndex = String(z);
      d.style.pointerEvents = "none";
      document.body.appendChild(d);
      return d;
    };

    state.bgA = mk("slotBgA", -50);
    state.bgB = mk("slotBgB", -49);

    [state.bgA, state.bgB].forEach(d => {
      d.style.backgroundSize = "cover";
      d.style.backgroundPosition = "center";
      d.style.opacity = "0";
      d.style.transition = "opacity 180ms linear";
      d.style.filter = "saturate(1.15) contrast(1.05)";
    });

    state.bgLight = mk("slotBgLight", -48);
    state.bgLight.style.background =
      "linear-gradient(120deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.14) 35%, rgba(255,255,255,0.00) 70%)";
    state.bgLight.style.mixBlendMode = "screen";
    state.bgLight.style.opacity = "0";
    state.bgLight.style.transformOrigin = "center";
  }

  function setBg(url){
    ensureBgLayers();
    const on  = state.bgFlip ? state.bgA : state.bgB;
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

    // 빛 방향 변화(현란 느낌) - 스핀 중만
    ensureBgLayers();
    state.bgLight.style.opacity = "0.28";
    state.bgLight.style.animation = "slotLightSweep 0.9s ease-in-out infinite";

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
    if (state.bgLight){
      state.bgLight.style.animation = "none";
      state.bgLight.style.opacity = "0";
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

  // ✅ 스핀(카지노 느낌: 4~5초, 릴별로 탁탁 멈춤)
  async function spin({ bet=10 } = {}){
    if (state.spinning) return { ok:false, error:"busy" };
    state.spinning = true;

    ensureGridDOM();
    if (!state.grid) renderGrid(null);

    const stopAt = [2600, 3100, 3600, 4100, 4600]; // ms
    const startFast = 26;   // 초반 빠름
    const endSlow   = 120;  // 멈추기 직전 느림

    playOne("start");
    playLoop("spin");
    startBgCycle(200);

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

    // ✅ 확률/연출 고정 결과 만들기
    const type = rollOutcomeType_(state.cfg);
    forceOneLine_(state.grid, type);
    renderGrid(state.grid);

    stopBgCycle();
    stopLoop("spin");

    const result = evaluate(state.grid, bet);

    // ✅ 표시 규칙: 2개 본전은 EVEN
    let label = "LOSE";
    if (result.jackpot) label = "JACKPOT";
    else if (result.payout > 0 && result.netDelta === 0) label = "EVEN";
    else if (result.payout > 0) label = "WIN";

    if (label === "JACKPOT") playOne("jackpot");
    else if (label === "WIN" || label === "EVEN") playOne("win");
    else playOne("lose");

    state.spinning = false;

    return {
      ok:true,
      grid: state.grid,
      ...result,
      resultText: label,
      outcomeType: label.toLowerCase()
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

  // ✅ app에서 족보 출력용
  S.game.getPaytable = () => ({ PAY, SYMBOL_IDS });

})(window.SLOT);
