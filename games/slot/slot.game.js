/* games/slot/slot.game.js */
/* ✅ uiReels에 3x5 렌더 + 10초 스핀 + 사운드 + 결과 커밋(SLOT_COMMIT_RESULT) */

window.SLOT = window.SLOT || {};
(function (S) {
  const $ = (id) => document.getElementById(id);

  // ✅ 심볼(이미지 파일명 = games/img/slot/*.png)
  const SYMBOLS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // ✅ (임시) 페이테이블: 3/4/5 연속(왼쪽부터) 배수
  // netDelta = bet * (mult - 1)
  const PAY = {
    star1:{3:2,4:3,5:5},
    star2:{3:3,4:5,5:8},
    star3:{3:5,4:8,5:15},
    pro1 :{3:6,4:10,5:20},
    pro2 :{3:7,4:12,5:24},
    pro3 :{3:8,4:14,5:28},
    pro4 :{3:9,4:16,5:32},
    pro5 :{3:10,4:18,5:36},
    pro6 :{3:12,4:22,5:45},
    pro7 :{3:14,4:26,5:55},
    pro8 :{3:16,4:32,5:70},
    pro9 :{3:20,4:40,5:90},
    pro10:{3:25,4:60,5:150} // ✅ 여기서 5연속이면 JACKPOT 연출만 (풀 지급은 다음 단계)
  };

  const state = {
    inited: false,
    spinning: false,
    auto: false,
    cells: [], // {cell, img}
  };

  function randSym(){
    return SYMBOLS[(Math.random() * SYMBOLS.length) | 0];
  }

  function imgSrc(sym){
    // slot.html이 /games/slot.html 이므로 "img/slot/..." 가 정답
    return `img/slot/${sym}.png`;
  }

  function setText(id, v){
    const el = $(id);
    if (el) el.textContent = String(v ?? "");
  }

  function setNote(msg){
    const el = $("uiNote");
    if (el) el.textContent = msg || "";
  }

  function getBet(){
    const v = Number(($("uiBet")?.textContent || "").trim());
    return Number.isFinite(v) && v > 0 ? v : 10;
  }

  function getWallet(){
    const v = Number(($("uiWallet")?.textContent || "").trim());
    return Number.isFinite(v) ? v : 0;
  }

  function mount(){
    return $("uiReels");
  }

  function buildCells(){
    const m = mount();
    if (!m) return false;

    m.innerHTML = "";
    state.cells = [];

    // 3 x 5 = 15
    for (let i = 0; i < 15; i++){
      const cell = document.createElement("div");
      cell.className = "cell";

      const sym = document.createElement("div");
      sym.className = "sym";

      const img = document.createElement("img");
      img.alt = "";
      img.draggable = false;

      sym.appendChild(img);
      cell.appendChild(sym);
      m.appendChild(cell);

      state.cells.push({ cell, img });
    }
    return true;
  }

  function tickCell(cell){
    if (!cell) return;
    cell.classList.remove("tick");
    // reflow
    void cell.offsetWidth;
    cell.classList.add("tick");
    setTimeout(() => cell.classList.remove("tick"), 90);
  }

  function setCell(index, sym, doTick){
    const o = state.cells[index];
    if (!o) return;
    o.img.src = imgSrc(sym);
    o.img.alt = sym;
    if (doTick) tickCell(o.cell);
  }

  function renderGrid(grid, doTick){
    // grid: [ [..5], [..5], [..5] ]
    for (let r = 0; r < 3; r++){
      for (let c = 0; c < 5; c++){
        setCell(r * 5 + c, grid[r][c], !!doTick);
      }
    }
  }

  function randomGrid(){
    return Array.from({ length: 3 }, () =>
      Array.from({ length: 5 }, () => randSym())
    );
  }

  function evaluate(grid, bet){
    let best = { mult: 0, row: -1, count: 0, sym: null };

    for (let r = 0; r < 3; r++){
      const line = grid[r];
      const sym = line[0];
      let count = 1;
      for (let c = 1; c < 5; c++){
        if (line[c] === sym) count++;
        else break;
      }

      if (count >= 3){
        const mult = (PAY[sym] && PAY[sym][count]) ? PAY[sym][count] : 0;
        if (mult > best.mult){
          best = { mult, row: r, count, sym };
        }
      }
    }

    if (best.mult > 0){
      const netDelta = Math.round(bet * (best.mult - 1));
      const winCells = [];
      for (let c = 0; c < best.count; c++){
        winCells.push(best.row * 5 + c);
      }

      const isJackpot = (best.sym === "pro10" && best.count === 5);
      const resultText = isJackpot ? "JACKPOT" : `WIN x${best.mult}`;
      return { isWin:true, isJackpot, netDelta, lossAmount:0, resultText, winCells };
    }

    return { isWin:false, isJackpot:false, netDelta:-bet, lossAmount:bet, resultText:"LOSE", winCells:[] };
  }

  // ======================
  // ✅ SOUND (games/sounds/)
  // ======================
  const sound = (() => {
    const base = "sounds/";
    const map = {
      start:  base + "start-button-sound.MP3",
      spin:   base + "spining-sound.MP3",
      stop:   base + "stop-stop-stop-sound.MP3",
      win:    base + "win-sound.MP3",
      lose:   base + "lose-sound.MP3",
      jackpot:base + "jackpot-sound.MP3",
    };

    const a = {};
    function get(name){
      if (a[name]) return a[name];
      const src = map[name];
      if (!src) return null;
      const audio = new Audio(src);
      audio.preload = "auto";
      a[name] = audio;
      return audio;
    }

    function play(name, opt={}){
      const audio = get(name);
      if (!audio) return;
      try{
        audio.loop = !!opt.loop;
        audio.currentTime = 0;
        audio.play().catch(()=>{});
      }catch(e){}
    }

    function stop(name){
      const audio = get(name);
      if (!audio) return;
      try{
        audio.loop = false;
        audio.pause();
        audio.currentTime = 0;
      }catch(e){}
    }

    return { play, stop };
  })();

  function flashWinCells(indexes){
    indexes.forEach(i => {
      const cell = state.cells[i]?.cell;
      if (!cell) return;
      cell.classList.add("winFlash");
      setTimeout(() => cell.classList.remove("winFlash"), 650);
    });
  }

  function pulseJackpot(){
    const wrap = $("uiReelWrap");
    if (!wrap) return;
    wrap.classList.add("jackpotPulse");
    setTimeout(() => wrap.classList.remove("jackpotPulse"), 1800);
  }

  async function commitResult(outcome){
    if (typeof window.SLOT_COMMIT_RESULT !== "function"){
      setNote("정산 함수가 없습니다 (SLOT_COMMIT_RESULT).");
      return;
    }

    setNote("정산 중...");
    await window.SLOT_COMMIT_RESULT({
      netDelta: outcome.netDelta,
      lossAmount: outcome.lossAmount,
      resultText: outcome.resultText
    });

    if (outcome.isWin) setNote(`+${outcome.netDelta} UT`);
    else setNote(`${outcome.netDelta} UT`);
  }

  async function spinOnce(){
    if (state.spinning) return;

    const bet = getBet();
    const wallet = getWallet();
    if (wallet < bet){
      setNote("잔액 부족");
      return;
    }

    state.spinning = true;
    $("btnSpin") && ($("btnSpin").disabled = true);
    setText("uiResult", "SPINNING");
    setNote("");

    // ✅ 최종 그리드 미리 결정
    const finalGrid = randomGrid();

    // ✅ 10초 스핀(릴 순차 스톱)
    const startTs = performance.now();
    const stopAt = [7000, 7800, 8600, 9400, 10000]; // ms
    const stopped = [false,false,false,false,false];

    sound.play("start");
    sound.play("spin", { loop:true });

    await new Promise((resolve) => {
      const timer = setInterval(() => {
        const t = performance.now() - startTs;

        for (let c = 0; c < 5; c++){
          if (!stopped[c]){
            if (t >= stopAt[c]){
              stopped[c] = true;

              // ✅ 이 릴(열) 확정
              for (let r = 0; r < 3; r++){
                setCell(r * 5 + c, finalGrid[r][c], true);
              }
              sound.play("stop");
            } else {
              // ✅ 도는 동안 랜덤으로 흔들기
              for (let r = 0; r < 3; r++){
                setCell(r * 5 + c, randSym(), true);
              }
            }
          }
        }

        // 마지막 릴 멈춘 뒤 조금 텀
        if (t >= stopAt[4] + 220){
          clearInterval(timer);
          resolve();
        }
      }, 80);
    });

    sound.stop("spin");

    // ✅ 최종 그리드 확정 렌더
    renderGrid(finalGrid, false);

    // ✅ 승/패 판정
    const outcome = evaluate(finalGrid, bet);
    setText("uiResult", outcome.resultText);

    if (outcome.isWin){
      flashWinCells(outcome.winCells);
      if (outcome.isJackpot){
        pulseJackpot();
        sound.play("jackpot");
      } else {
        sound.play("win");
      }
    } else {
      sound.play("lose");
    }

    // ✅ 시트 반영
    await commitResult(outcome);

    $("btnSpin") && ($("btnSpin").disabled = false);
    state.spinning = false;

    // ✅ AUTO면 다음 스핀
    if (state.auto){
      setTimeout(() => spinOnce(), 650);
    }
  }

  function bind(){
    const btnSpin = $("btnSpin");
    const btnAuto = $("btnAuto");

    if (btnSpin && !btnSpin.dataset.bound){
      btnSpin.dataset.bound = "1";
      btnSpin.addEventListener("click", spinOnce);
    }

    if (btnAuto && !btnAuto.dataset.bound){
      btnAuto.dataset.bound = "1";
      btnAuto.addEventListener("click", () => {
        state.auto = !state.auto;
        btnAuto.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
        if (state.auto && !state.spinning) spinOnce();
      });
    }
  }

  function init(){
    if (state.inited) return;
    state.inited = true;

    const ok = buildCells();
    if (!ok) return;

    // ✅ 진입 즉시 “빈 화면” 제거: 랜덤 그리드 1회 깔기
    renderGrid(randomGrid(), false);
    bind();
  }

  document.addEventListener("DOMContentLoaded", init);

  // 외부에서 쓰기 좋게 노출
  S.game = S.game || {};
  S.game.init = init;
  S.game.spinOnce = spinOnce;
  S.game.renderGrid = renderGrid;

})(window.SLOT);
