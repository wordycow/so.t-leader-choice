(function () {
  window.SLOT = window.SLOT || {};

  const ROOT = "https://wordycow.github.io/so.t-leader-choice/";
  const CFG = {
    ROOT,
    MAIN_URL: ROOT + "the-unique-main.html",
    GATE_URL: ROOT + "the-unique-gate.html",

    SCRIPT_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",

    ASSET: {
      imgBase: "img/slot/",
      sndBase: "sounds/",
      bg: ["bg1.png","bg2.png","bg3.png","bg4.png","bg5.png"],
      sound: {
        start: "start-button-sound.MP3",
        spin:  "spining-sound.MP3",       // 파일명 그대로
        stop:  "stop-stop-stop-sound.MP3",
        win:   "win-sound.MP3",
        lose:  "lose-sound.MP3",
        jackpot:"jackpot-sound.MP3"
      }
    },

    BET: { min: 10, max: 1000, step: 5, def: 10 },

    // ✅ 스핀 연출(요구사항): 10초 + 하나씩 멈춤
    SPIN: {
      totalMs: 10000,
      tickMs: 90,
      stopCascadeMs: 950,   // 컬럼 멈춤 간격(거의 1초)
      bgFastMs: 420,        // 초반 배경 전환(빠름)
      bgSlowMs: 1100,       // 후반 배경 전환(느림)
    },

    // ✅ 승률(LOW/MID/HIGH) : jackpot은 기본 0 (운영자 수동)
    ODDS_PROFILES: {
      LOW:  { lose:0.80, even:0.17, win3:0.028, win4:0.002, jackpot:0.0 },
      MID:  { lose:0.70, even:0.20, win3:0.085, win4:0.015, jackpot:0.0 },
      HIGH: { lose:0.55, even:0.23, win3:0.17,  win4:0.05,  jackpot:0.0 },
    },

    // ✅ 잭팟: 이번달 “없음” 기본값
    JACKPOT: {
      enabled: false, // 나중에 casino-admin 연결되면 서버값으로 true/false 제어
    },

    SYMBOLS: [
      { key:"star1", label:"STAR 1", w:22, img:"star1.png",  pay:{3:2,   4:5,  5:12} },
      { key:"star2", label:"STAR 2", w:18, img:"star2.png",  pay:{3:2.5, 4:6,  5:15} },
      { key:"star3", label:"STAR 3", w:14, img:"star3.png",  pay:{3:3,   4:7,  5:18} },

      { key:"pro1",  label:"PRO 1",  w:12, img:"pro1.png",   pay:{3:4,   4:10, 5:25} },
      { key:"pro2",  label:"PRO 2",  w:9,  img:"pro2.png",   pay:{3:4.5, 4:11, 5:28} },
      { key:"pro3",  label:"PRO 3",  w:7,  img:"pro3.png",   pay:{3:5,   4:12, 5:30} },
      { key:"pro4",  label:"PRO 4",  w:5,  img:"pro4.png",   pay:{3:5.5, 4:13, 5:33} },
      { key:"pro5",  label:"PRO 5",  w:4,  img:"pro5.png",   pay:{3:6,   4:14, 5:36} },
      { key:"pro6",  label:"PRO 6",  w:3,  img:"pro6.png",   pay:{3:6.5, 4:15, 5:40} },
      { key:"pro7",  label:"PRO 7",  w:2.5,img:"pro7.png",   pay:{3:7,   4:16, 5:44} },
      { key:"pro8",  label:"PRO 8",  w:2,  img:"pro8.png",   pay:{3:7.5, 4:18, 5:48} },
      { key:"pro9",  label:"PRO 9",  w:1.5,img:"pro9.png",   pay:{3:8,   4:20, 5:55} },
      { key:"pro10", label:"PRO 10", w:1,  img:"pro10.png",  pay:{3:9,   4:24, 5:70} },
    ],
  };

  window.SLOT.config = CFG;
})();
