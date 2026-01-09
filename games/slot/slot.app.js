// games/slot/slot_app.js
window.SLOT = window.SLOT || {};
(function (S) {

  const spinBtn = document.getElementById("spinBtn");
  const hintText = document.getElementById("hintText");
  const bg = document.getElementById("bg");

  function flashBg(){
    if(!bg) return;
    bg.classList.add("flash");
    setTimeout(()=>bg.classList.remove("flash"), 280);
  }

  function setHint(text){
    if(hintText) hintText.textContent = text;
  }

  async function boot(){
    S.audio?.preload?.();

    S.ui.buildPaytable();

    const ctx = S.api.getPlayerContext();
    S.ui.setPlayer(ctx);

    // API 상태 확인(가능하면 bet/jp/ut 갱신)
    await S.api.checkApi(ctx);

    spinBtn.addEventListener("click", async () => {
      S.audio.unlockAudio();

      spinBtn.disabled = true;
      S.ui.setKpi({ win: 0 });
      S.ui.setLog("Spinning...");
      setHint("릴이 멈출 때까지 숨참기 😈");

      S.audio.playOne("start");
      S.audio.startSpinSound();
      S.game.startSpinVisual();

      try {
        const out = await S.api.spin(ctx);

        // ✅ 여기서 먼저 grid 검증(중요: setTimeout 안에서 throw하면 catch에 안 잡힘)
        const grid = out.grid;
        if(!grid || !Array.isArray(grid) || grid.length < 3){
          throw new Error("Invalid grid");
        }

        // stop sequence
        setTimeout(() => {
          S.audio.stopSpinSound();

          for(let i=0; i<S.NUM_REELS; i++){
            setTimeout(() => {
              S.game.stopReel(i, [ grid[0][i], grid[1][i], grid[2][i] ]);
              S.audio.playOne("stop");

              if(i === S.NUM_REELS - 1){
                // finish
                S.game.reelsEl.classList.remove("spinning");
                spinBtn.disabled = false;

                S.ui.setKpi({ bet: out.bet, jackpot: out.jackpot, win: out.win });

                // ✅ UT 업데이트(서버가 주면 표시 + localStorage 저장)
                if(out.ut !== undefined && out.ut !== null){
                  S.ui.setPlayer({ u: ctx.u, uid: ctx.uid, ut: out.ut });
                  localStorage.setItem("unique_ut", String(out.ut));
                }

                const wt = String(out.winType || "").trim();
                S.ui.setLog(`RESULT: ${wt || "NORMAL"}\nWIN: ${out.win}`);

                if(wt.toLowerCase().includes("jackpot")){
                  flashBg();
                  setHint("잭팟! 오늘 운 다 씀 👑");
                  S.audio.playOne("jackpot");
                } else if(Number(out.win) > 0){
                  flashBg();
                  setHint("승리! UT 쌓이는 맛이 이거지 🔥");
                  S.audio.playOne("win");
                } else {
                  setHint("다음 판이 진짜다. (근데 무지성 연타 금지) 😅");
                  S.audio.playOne("lose");
                }
              }
            }, 500 + i * 380);
          }
        }, 1200);

      } catch(e) {
        S.audio.stopSpinSound();
        S.game.stopSpinVisual();
        spinBtn.disabled = false;
        S.ui.setLog("Error. Try again.");
        setHint("에러났음. 콘솔 확인 ㄱㄱ");
        alert("Spin Error: " + e.message);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", boot);
})(window.SLOT);
