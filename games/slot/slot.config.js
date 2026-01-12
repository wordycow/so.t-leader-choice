(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  // ✅ 여기에 Apps Script 웹앱(/exec) URL 넣어라
  const SCRIPT_URL = "PASTE_YOUR_APPS_SCRIPT_WEBAPP_EXEC_URL";

  // ✅ 이미지 기본 경로 (slot.html 기준 상대경로)
  // 폴더 구조: /games/slot.html, /games/slot/ (여기 안에 img)
  const IMG_BASE = "./slot/img";

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
      // 배경 이미지를 쓰면 여기에 넣어 (없으면 빈값)
      bg: ""
    },

    SYMBOLS,
    SYMBOL_MAP,

    PAYTABLE_TEXT: [
      "2연속: EVEN(±0)",
      "3연속: WIN(3x)",
      "4연속: WIN(10x)",
      "5연속: MEGA(25x)",
      "JACKPOT: 운영자 지정(잭팟풀 지급)"
    ],

    STORAGE_KEYS: {
      sound: "slot_sound_on",
      auto: "slot_auto_on",
      bet: "slot_bet_ut",
      banner: "slot_jackpot_banner_v1"
    }
  };
})();
