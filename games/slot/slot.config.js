(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  // ✅ Apps Script 웹앱(/exec) URL
  const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // ✅ slot.html 기준 상대경로: /games/slot.html, /games/slot/img/*
  const IMG_BASE = "./slot/img";

  // ✅ 배경 5개
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

    // ✅ 버튼이 -5/+5니까 step=5로 맞춤
    BET: { min: 10, max: 1000, step: 5, def: 10 },

    // ✅ 스핀 애니메이션(슬로우 기준 0.2초 = 200ms)
    SPIN: {
      durationMs: 2200,     // "천천히" 도는 느낌
      tickMinMs: 80,        // 빠를 때 최소 틱
      tickMaxMs: 200        // 느릴 때(최소 속도) 0.2초
    },

    ASSET: {
      imgBase: IMG_BASE,
      bgList: BG_FILES,
      bg: BG_FILES[0] // 기본 배경
    },

    SYMBOLS,
    SYMBOL_MAP,

    // ✅ 여기 주석은 JS 주석으로 밖으로 빼야 함
    // "2연속: EVEN(±0)"보다 "±1"이 좋다고 했으니 표기 반영
    PAYTABLE_TEXT: [
      "2연속: EVEN(+1)",
      "3연속: WIN(3x)",
      "4연속: WIN(10x)",
      "5연속: MEGA(25x)",
      "JACKPOT: 운영자 지정(잭팟풀 지급)"
    ],

    STORAGE_KEYS: {
      sound: "slot_sound_on",
      auto: "slot_auto_on",
      bet: "slot_bet_ut",
      payCollapsed: "slot_pay_collapsed_v1",
      banner: "slot_jackpot_banner_v1"
    }
  };
})();
