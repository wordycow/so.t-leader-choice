// games/slot/slot.audio.js
window.SLOT = window.SLOT || {};
(function (S) {
  const soundBtn = document.getElementById("soundBtn");
  const soundText = document.getElementById("soundText");

  let SOUND_ON = true;
  let audioUnlocked = false;

  // ✅ 후보 리스트 제거: mp3 소문자만 사용
  function makeAudio(src, { loop=false, volume=1 } = {}) {
    const a = new Audio(src);
    a.loop = loop;
    a.volume = volume;
    return a;
  }

  S.SFX = {
    start: makeAudio("sounds/start-button-sound.mp3", { volume: 0.9 }),
    spin:  makeAudio("sounds/spining-sound.mp3",      { loop: true, volume: 0.9 }),
    stop:  makeAudio("sounds/stop-stop-stop-sound.mp3",{ volume: 0.9 }),
    win:   makeAudio("sounds/win-sound.mp3",          { volume: 1.0 }),
    lose:  makeAudio("sounds/lose-sound.mp3",         { volume: 1.0 }),
    jackpot: makeAudio("sounds/jackpot-sound.mp3",    { volume: 1.0 }),
  };

  function unlockAudio(){
    if (audioUnlocked) return;
    audioUnlocked = true;

    Object.values(S.SFX).forEach(a => {
      try {
        const v = a.volume;
        a.volume = 0.001;
        a.play().then(() => {
          a.pause(); a.currentTime = 0; a.volume = v;
        }).catch(() => {});
      } catch(e){}
    });
  }

  function stopSpinSound(){
    try { S.SFX.spin.pause(); } catch(e){}
  }

  function startSpinSound(){
    if (!SOUND_ON) return;
    try { S.SFX.spin.currentTime = 0; S.SFX.spin.play().catch(()=>{}); } catch(e){}
  }

  function playOne(key){
    if (!SOUND_ON) return;
    try {
      const a = S.SFX[key];
      a.currentTime = 0;
      a.play().catch(()=>{});
    } catch(e){}
  }

  function toggleSound(){
    SOUND_ON = !SOUND_ON;
    soundBtn.classList.toggle("off", !SOUND_ON);
    soundText.textContent = SOUND_ON ? "SOUND: ON" : "SOUND: OFF";
    if(!SOUND_ON) stopSpinSound();
  }

  soundBtn.addEventListener("click", toggleSound);

  // export
  S.audio = {
    unlockAudio,
    playOne,
    startSpinSound,
    stopSpinSound,
    get on(){ return SOUND_ON; }
  };
})(window.SLOT);
