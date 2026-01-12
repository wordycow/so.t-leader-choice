(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  // ✅ Apps Script 웹앱(/exec) URL
  const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // ✅ 이미지 폴더: /games/img/slot
  // slot.html이 /games/slot.html 이니까 상대경로는 ./img/slot 이 맞다.
  const IMG_BASE = "./img/slot";

  const BG_FILES = ["bg1.png", "bg2.png", "bg3.png", "bg4.png", "bg5.png"];

  const SYMBOLS = [
    { key: "star1",  label: "STAR1",  file: "star1.png"  },
    { key: "star2",  label: "STAR2",  file: "star2.png"  },
    { key: "star3",  label: "STAR3",  file: "star3.png"  },
    { key: "pro1",   label: "PRO1",   file: "pro1.png"   },
    { key: "pro2",   label: "PRO2",   file: "pro2.png"   },
    { key: "pro3",   label: "PRO3",   file: "pro3.png"   },
    { key: "pro4",   label: "PRO4",   file: "pro4.png"   },
    { key: "pro5",   label: "PRO5",   file: "pro5.png"   },
    { key: "pro6",   label: "PRO6",   file: "pro6.png"   },
    { key: "pro7",   label: "PRO7",   file: "pro7.png"   },
    { key: "pro8",   label: "PRO8",   file: "pro8.png"   },
    { key: "pro9",   label: "PRO9",   file: "pro9.png"   },
    { key: "pro10",  label: "PRO10",  file: "pro10.png"  },
  ];

  const SYMBOL_MAP = Object.fromEntries(SYMBOLS.map(s => [s.key, s]));

  SLOT.config = {
    SCRIPT_URL,

    GRID: { rows: 3, cols: 5 },

    BET: { min: 10, max: 1000, step: 5, def: 10 },

    ASSET: {
      imgBase: IMG_BASE,
      bgFiles: BG_FILES
    },

    SYMBOLS,
    SYMBOL_MAP,

    PAYTABLE_TEXT: [
      "2연속: EVEN(±1)",
      "3연속: WIN(3x)",
      "4연속: WIN(10x)",
      "5연속: MEGA(25x)",
      "JACKPOT: 잭팟풀 지급"
    ],

    STORAGE_KEYS: {
      sound: "slot_sound_on",
      auto: "slot_auto_on",
      bet: "slot_bet_ut",
      banner: "slot_jackpot_banner_v1"
    }
  };
})();
