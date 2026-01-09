// games/slot/slot.audio.js
window.SLOT = window.SLOT || {};
(function (S) {
  const sounds = {};
  let unlocked = false;
  let spinLoop = null;
  let enabled = true;

  // ✅ 파일명/확장자 정확히: GitHub Pages는 대소문자 구분
  const MAP = {
    start:   "start-button-sound.MP3",
    spin:    "spining-sound.MP3",
    stop:    "stop-stop-stop-sound.MP3",
    win:     "win-sound.MP3",
    lose:    "lose-sound.MP3",
    jackpot: "jackpot-sound.MP3",
  };

  function urlOf(key){
    return `sounds/${MAP[key]}`;
  }

  function loadOne(key){
    const a = new Audio(urlOf(key));
    a.preload = "auto";
    sounds[key] = a;
  }

  function init(){
    Object.keys(MAP).forEach(loadOne);

    const btn = document.getElementById("soundBtn");
    if(btn){
      btn.addEventListener("click", () => {
        enabled = !enabled;
        const t = document.getElementById("soundText");
        if(t) t.textContent = enabled ? "SOUND: ON" : "SOUND: OFF";
      });
    }
  }

  function unlockAudio(){
    if(unlocked) return;
    unlocked = true;

    // 모바일 정책: 최초 제스처에서 한 번 재생/정지로 unlock
    try{
      const a = sounds.start;
      a.muted = true;
      a.play().then(()=>{
        a.pause();
        a.currentTime = 0;
        a.muted = false;
      }).catch(()=>{});
    }catch(e){}
  }

  function playOne(key){
    if(!enabled) return;
    const a = sounds[key];
    if(!a) return;
    try{
      a.pause();
      a.currentTime = 0;
      a.play().catch(()=>{});
    }catch(e){}
  }

  function startSpinSound(){
    if(!enabled) return;
    const a = sounds.spin;
    if(!a) return;
    try{
      a.loop = true;
      a.currentTime = 0;
      a.play().catch(()=>{});
      spinLoop = a;
    }catch(e){}
  }

  function stopSpinSound(){
    if(spinLoop){
      try{
        spinLoop.pause();
        spinLoop.currentTime = 0;
      }catch(e){}
    }
    spinLoop = null;
  }

  init();

  S.audio = { unlockAudio, playOne, startSpinSound, stopSpinSound };
})(window.SLOT);
