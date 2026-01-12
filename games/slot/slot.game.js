(function () {
  window.SLOT = window.SLOT || {};
  const { SYMBOLS, ASSET, SPIN, ODDS_PROFILES, JACKPOT } = window.SLOT.config;

  function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
  function clamp(n,min,max){ return Math.max(min, Math.min(max, n)); }

  function weightedPickSymbolKey(){
    const total = SYMBOLS.reduce((a,s)=>a + s.w, 0);
    let r = Math.random() * total;
    for (const s of SYMBOLS){
      r -= s.w;
      if (r <= 0) return s.key;
    }
    return SYMBOLS[SYMBOLS.length-1].key;
  }

  function pickOutcome(profileKey){
    const p = ODDS_PROFILES[profileKey] || ODDS_PROFILES.LOW;
    const r = Math.random();
    let acc = 0;

    acc += p.lose;   if (r < acc) return "lose";
    acc += p.even;   if (r < acc) return "even";
    acc += p.win3;   if (r < acc) return "win3";
    acc += p.win4;   if (r < acc) return "win4";
    acc += (p.jackpot || 0);
    return "lose";
  }

  // ✅ 3x5(15칸) 그리드 생성
  // 가운데 줄(row=1)에서 왼쪽부터 연속 매칭으로 결과를 만들고,
  // 나머지 줄은 그냥 랜덤으로 채운다.
  function buildFinalGrid(outcome, forcedKey){
    const keys = new Array(15);
    const payKey = forcedKey || weightedPickSymbolKey();

    // 우선 랜덤으로 전체 채움
    for (let i=0;i<15;i++) keys[i] = weightedPickSymbolKey();

    // 가운데 줄 인덱스: 5..9
    const base = 5;
    const setMid = (c, k) => { keys[base + c] = k; };

    const k = payKey;
    const k2 = (function(){
      let t = weightedPickSymbolKey();
      let guard = 0;
      while (t === k && guard++ < 30) t = weightedPickSymbolKey();
      return t;
    })();

    if (outcome === "lose"){
      // 첫 2개부터 다르게
      setMid(0, k);
      setMid(1, k2);
    } else if (outcome === "even"){
      setMid(0, k);
      setMid(1, k);
      setMid(2, k2);
    } else if (outcome === "win3"){
      setMid(0, k);
      setMid(1, k);
      setMid(2, k);
      setMid(3, k2);
    } else if (outcome === "win4"){
      setMid(0, k);
      setMid(1, k);
      setMid(2, k);
      setMid(3, k);
      setMid(4, k2);
    } else if (outcome === "jackpot"){
      setMid(0, k);
      setMid(1, k);
      setMid(2, k);
      setMid(3, k);
      setMid(4, k);
    }

    return { keys, payKey };
  }

  // ✅ 결과 평가: 가운데 줄(5칸)에서 왼쪽부터 연속
  function evaluate(keys){
    const mid = keys.slice(5, 10); // 5개
    const first = mid[0];
    let count = 1;
    for (let i=1;i<5;i++){
      if (mid[i] === first) count++;
      else break;
    }
    return { bestKey: first, bestCount: count };
  }

  // ✅ 배경 전환(스핀 중은 빠르고, 멈출수록 느리게)
  function makeBgSpinner(ui){
    let t = null;
    let idx = 0;
    let currentMs = SPIN.bgFastMs;

    function setIntervalMs(ms){
      currentMs = ms;
      stop();
      t = setInterval(() => {
        idx = (idx + 1) % ASSET.bg.length;
        ui.bg.set(ASSET.imgBase + ASSET.bg[idx]);
      }, currentMs);
    }

    function start(){
      idx = Math.floor(Math.random() * ASSET.bg.length);
      ui.bg.set(ASSET.imgBase + ASSET.bg[idx]);
      ui.bg.flash(true);
      setIntervalMs(SPIN.bgFastMs);
    }
    function slow(){
      setIntervalMs(SPIN.bgSlowMs);
    }
    function stop(){
      if (t){ clearInterval(t); t = null; }
      ui.bg.flash(false);
    }
    return { start, slow, stop };
  }

  // ✅ 10초 스핀 + 컬럼(5개) 하나씩 멈춤
  // finalKeys는 “최종 고정값”
  async function animateSpin(ui, finalKeys){
    const cols = 5;
    const rows = 3;

    const totalMs = SPIN.totalMs;
    const tickMs = SPIN.tickMs;

    const cascade = SPIN.stopCascadeMs;            // ~1초
    const stopStartAt = totalMs - (cascade * cols); // 마지막 5초쯤부터 1초 간격으로 멈춤

    const stopped = new Array(cols).fill(false);
    const working = ui.gridKeys && ui.gridKeys.length === 15 ? ui.gridKeys.slice() : new Array(15).fill(SYMBOLS[0].key);

    let elapsed = 0;

    while (elapsed < totalMs){
      // 멈출 시점 판단
      for (let c=0;c<cols;c++){
        const stopAt = stopStartAt + (cascade * c);
        if (!stopped[c] && elapsed >= stopAt){
          // 이 컬럼을 final로 고정
          for (let r=0;r<rows;r++){
            working[r*cols + c] = finalKeys[r*cols + c];
          }
          stopped[c] = true;
        }
      }

      // 아직 안 멈춘 컬럼만 랜덤 스핀
      for (let c=0;c<cols;c++){
        if (stopped[c]) continue;
        for (let r=0;r<rows;r++){
          working[r*cols + c] = weightedPickSymbolKey();
        }
      }

      ui.setGrid(working);
      await sleep(tickMs);

      elapsed += tickMs;
      // 후반부로 갈수록 배경 느리게 바꾸는 느낌은 app에서 slow() 호출로 처리
    }

    ui.setGrid(finalKeys);
  }

  window.SLOT.game = {
    pickOutcome,
    buildFinalGrid,
    evaluate,
    makeBgSpinner,
    animateSpin
  };
})();
