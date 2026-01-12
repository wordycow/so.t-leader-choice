(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  function randKey(){
    const arr = CFG().SYMBOLS;
    return arr[Math.floor(Math.random()*arr.length)].key;
  }

  function makeRandomKeys(){
    const n = CFG().GRID.rows * CFG().GRID.cols;
    const a = new Array(n);
    for (let i=0;i<n;i++) a[i] = randKey();
    return a;
  }

  function shiftDownByColumn(keys){
    // keys: row-major 3x5
    const { rows, cols } = CFG().GRID;
    const out = keys.slice();
    for (let c=0;c<cols;c++){
      for (let r=rows-1; r>=1; r--){
        out[r*cols + c] = out[(r-1)*cols + c];
      }
      out[0*cols + c] = randKey(); // 맨 위 새 심볼
    }
    return out;
  }

  function lerp(a,b,t){ return a + (b-a)*t; }
  function easeOutCubic(t){ return 1 - Math.pow(1-t, 3); }

  async function spin({ id, bet, onUpdateUser }){
    const dur = CFG().SPIN.durationMs;
    const tickMin = CFG().SPIN.tickMinMs;
    const tickMax = CFG().SPIN.tickMaxMs;
    const bgMin = CFG().SPIN.bgMinMs;

    SLOT.UI.setLast("SPINNING...");
    SLOT.UI.flashWinLine(0);

    // 서버 결과 먼저 받아두고(네트워크 지연 대비) 애니메이션은 그대로 10초
    const serverPromise = SLOT.api.slotSpin(id, bet);

    // 사운드
    await SLOT.audio.unlock();
    SLOT.audio.play("start");
    SLOT.audio.play("spin", { loop:true, volume: 0.9 });

    // 애니메이션 루프
    let keys = makeRandomKeys();
    SLOT.UI.setGrid(keys);

    const bgFiles = CFG().ASSET.bgFiles;
    let bgIdx = 0;
    let lastBgTs = 0;

    const t0 = performance.now();

    return new Promise(async (resolve) => {
      async function step(){
        const now = performance.now();
        const t = Math.min(1, (now - t0) / dur);
        const e = easeOutCubic(t);
        const tick = Math.round(lerp(tickMin, tickMax, e));

        // 위→아래 느낌: 컬럼별로 내려오게 shift
        keys = shiftDownByColumn(keys);
        SLOT.UI.setGrid(keys);

        // 배경도 스핀 틱과 동기화 (최소 200ms)
        if (now - lastBgTs >= Math.max(bgMin, tick)) {
          bgIdx = (bgIdx + 1) % bgFiles.length;
          SLOT.UI.setPageBg(bgFiles[bgIdx]);
          lastBgTs = now;
        }

        if (t < 1){
          setTimeout(step, tick);
          return;
        }

        // 10초 끝: 서버 결과 반영
        const res = await serverPromise.catch(err => ({ ok:false, error:String(err?.message||err) }));

        SLOT.audio.stop("spin");
        SLOT.audio.play("stop");

        if (!res || !res.ok){
          SLOT.UI.setLast("ERROR");
          // 실패해도 화면은 유지
          resolve({ ok:false, error: res?.error || "spin_failed" });
          return;
        }

        const spin = res.spin || {};
        const finalKeys = Array.isArray(spin.keys) ? spin.keys : makeRandomKeys();
        SLOT.UI.setGrid(finalKeys);

        // 결과 표시
        const kind = String(spin.kind || "").toUpperCase();
        const label =
          kind === "LOSE" ? "LOSE" :
          kind === "EVEN" ? "EVEN" :
          kind === "WIN3" ? "WIN" :
          kind === "WIN4" ? "WIN" :
          kind === "MEGA" ? "MEGA" :
          kind === "JACKPOT" ? "JACKPOT" : kind || "READY";

        SLOT.UI.setLast(label);

        // 하이라이트(가운데줄)
        const runLen =
          spin.kind === "even" ? 2 :
          spin.kind === "win3" ? 3 :
          spin.kind === "win4" ? 4 :
          (spin.kind === "mega" || spin.kind === "jackpot") ? 5 : 1;
        SLOT.UI.flashWinLine(runLen);

        // 사운드 결과
        if (spin.kind === "jackpot") SLOT.audio.play("jackpot");
        else if (spin.kind === "lose") SLOT.audio.play("lose");
        else SLOT.audio.play("win");

        // 유저/풀 업데이트
        if (res.user && typeof res.user.balance !== "undefined") {
          onUpdateUser?.({ balance: res.user.balance });
        }
        if (typeof res.jackpotTotal !== "undefined") SLOT.UI.setJackpot(res.jackpotTotal);

        resolve(res);
      }

      step();
    });
  }

  SLOT.game = { spin };
})();
