/* games/slot/slot.config.js */
(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  // ✅ 너의 Apps Script 웹앱 exec URL로 교체
  // 예) https://script.google.com/macros/s/AKfycbxxxxx/exec
  const SCRIPT_URL = SLOT?.config?.SCRIPT_URL || "PASTE_YOUR_APPS_SCRIPT_EXEC_URL";

  // ✅ slot.html 위치(/games/slot.html) 기준으로 이미지 폴더는 보통 ../img/slot/
  // 네 프로젝트에 맞게 폴더만 조정하면 됨.
  const ASSET = Object.assign(
    {
      imgBase: "../img/slot/", // ✅ 여기 때문에 imgBase 에러가 났던 거다
    },
    (SLOT.config && SLOT.config.ASSET) || {}
  );

  // ✅ 심볼 키는 서버가 내려주는 keys[] (star1~pro10) 와 동일해야 함
  const SYMBOLS = [
    { key: "star1",  label: "STAR1",  file: "star1.png" },
    { key: "star2",  label: "STAR2",  file: "star2.png" },
    { key: "star3",  label: "STAR3",  file: "star3.png" },
    { key: "pro1",   label: "PRO1",   file: "pro1.png" },
    { key: "pro2",   label: "PRO2",   file: "pro2.png" },
    { key: "pro3",   label: "PRO3",   file: "pro3.png" },
    { key: "pro4",   label: "PRO4",   file: "pro4.png" },
    { key: "pro5",   label: "PRO5",   file: "pro5.png" },
    { key: "pro6",   label: "PRO6",   file: "pro6.png" },
    { key: "pro7",   label: "PRO7",   file: "pro7.png" },
    { key: "pro8",   label: "PRO8",   file: "pro8.png" },
    { key: "pro9",   label: "PRO9",   file: "pro9.png" },
    { key: "pro10",  label: "PRO10",  file: "pro10.png" },
  ];

  const PAY = { even: 0, win3: 3, win4: 10, mega: 25 };

  const SPIN = {
    betDefault: 10,
    betMin: 10,
    betMax: 1000,
    betStep: 5,
  };

  const STORAGE = {
    userId: "slot.userId",
    bet: "slot.bet",
    payCollapsed: "slot.pay.collapsed",
    banner: "slot.banner.untilMidnight",
  };

  SLOT.config = Object.assign({}, SLOT.config || {}, {
    SCRIPT_URL,
    ASSET,
    SYMBOLS,
    PAY,
    SPIN,
    STORAGE,
  });
})();
