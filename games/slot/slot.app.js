// games/slot/slot.app.js
window.SLOT = window.SLOT || {};
(function (S) {

  const spinBtn = document.getElementById("spinBtn");
  const hintText = document.getElementById("hintText");
  const bg = document.getElementById("bg");
  const backMainBtn = document.getElementById("backMainBtn");

  function flashBg(){
    bg.classList.add("flash");
    setTimeout(()=>bg.classList.remove("flash"), 280);
  }

  function setHint(text){
    hintText.textContent = text;
  }

  // ✅ MAIN 돌아가기 링크에 u/uid/ut 붙여서 동기화
  function setBackLink(ctx, utOverride){
    if(!backMainBtn) return;

    const ut = (utOverride !== undefined && utOverride !== null)
      ? String(utOverride)
      : (localStorage.getItem("unique_ut") || ctx.ut || "");

    const params = new URLSearchParams();
    if(ctx.u) params.set("u", ctx.u);
    if(ctx.uid) params.set("uid", ctx.uid);
    if(ut) params.set("ut", ut);

    const base = "../the-unique-main.html";
    backMainBtn.href = params.toString() ? `${base}?${params.toString()}` : base;
  }

  async function boot(){
    S.ui.buildPaytable();

    const ctx = S.api.getPlayerContext();
    S.ui.setPlayer(ctx);

    // ✅ 최초 MAIN 링크 세팅
    setBackLink(ctx);

    // API 상태 확인(가능하면 bet/jp/ut 갱신)
    await S.api.checkApi(ctx);

    // 버튼 바인딩
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

        setTimeout(() => {
          S.audio.stopSpinSound();

          const grid = out.grid;
          if(!grid || !Array.isArray(grid) || grid.length < 3){
            throw new Error("Invalid grid");
          }

          for(let i=0; i<S.NUM_REELS; i++){
            setTimeout(() => {
              S.game.stopReel(i, [ grid[0][i], grid[1][i], grid[2][i] ]);
              S.audio.playOne("stop");

              if(i === S.NUM_REELS - 1){
                S.game.reelsEl.classList.remove("spinning");
                spinBtn.disabled = false;

                S.ui.setKpi({ bet: out.bet, jackpot: out.jackpot, win: out.win });

                // ✅ UT 업데이트(서버가 주면 표시 + MAIN 동기화용 캐시 + MAIN 링크도 갱신)
                if(out.ut !== undefined && out.ut !== null){
                  S.ui.setPlayer({ u: ctx.u, uid: ctx.uid, ut: out.ut });
                  localStorage.setItem("unique_ut", String(out.ut));
                  setBackLink(ctx, out.ut);
                } else {
                  // ut가 안 오더라도 링크는 최신 localStorage 기준으로 유지
                  setBackLink(ctx);
                }

                const wt = String(out.winType || "").trim();
                S.ui.setLog(`RESULT: ${wt || "NORMAL"}\nWIN: ${out.win}`);

                if(wt.toLowerCase().includes("jackpot") || (grid[1]?.slice(1,4).every(x=>x==="pro10"))){
                  flashBg();
                  setHint("잭팟! PRO10 터졌다 👑");
                  S.audio.playOne("jackpot");
                } else if(Number(out.win) > 0){
                  flashBg();
                  setHint("승리! UT 쌓이는 맛 🔥");
                  S.audio.playOne("win");
                } else {
                  setHint("다음 판이 진짜다 😅");
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
