/* games/slot/slot.config.js */
(function () {
  // 전역 네임스페이스
  window.SLOT = window.SLOT || {};

  // Apps Script (너가 쓰는 그대로)
  const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // ✅ slot.html이 games/slot.html 이라서 상대경로는 이게 맞다
  const ASSET = {
    imgBase: "img/slot/",
    sndBase: "sounds/",
    bg: ["bg1.png", "bg2.png", "bg3.png", "bg4.png", "bg5.png"],
    sound: {
      start: "start-button-sound.MP3",
      spin: "spining-sound.MP3", // 파일명 오타 그대로
      stop: "stop-stop-stop-sound.MP3",
      win: "win-sound.MP3",
      lose: "lose-sound.MP3",
      jackpot: "jackpot-sound.MP3"
    }
  };

  // ✅ 베팅: 5 단위 (유송 요청)
  const BET = { min: 10, max: 1000, step: 5, def: 10 };

  // 심볼/배당 (원형 유지)
  const SYMBOLS = [
    { key: "star1", label: "STAR 1", w: 22, img: "star1.png", pay: { 3: 2, 4: 5, 5: 12 } },
    { key: "star2", label: "STAR 2", w: 18, img: "star2.png", pay: { 3: 2.5, 4: 6, 5: 15 } },
    { key: "star3", label: "STAR 3", w: 14, img: "star3.png", pay: { 3: 3, 4: 7, 5: 18 } },

    { key: "pro1", label: "PRO 1", w: 12, img: "pro1.png", pay: { 3: 4, 4: 10, 5: 25 } },
    { key: "pro2", label: "PRO 2", w: 9, img: "pro2.png", pay: { 3: 4.5, 4: 11, 5: 28 } },
    { key: "pro3", label: "PRO 3", w: 7, img: "pro3.png", pay: { 3: 5, 4: 12, 5: 30 } },
    { key: "pro4", label: "PRO 4", w: 5, img: "pro4.png", pay: { 3: 5.5, 4: 13, 5: 33 } },
    { key: "pro5", label: "PRO 5", w: 4, img: "pro5.png", pay: { 3: 6, 4: 14, 5: 36 } },
    { key: "pro6", label: "PRO 6", w: 3, img: "pro6.png", pay: { 3: 6.5, 4: 15, 5: 40 } },
    { key: "pro7", label: "PRO 7", w: 2.5, img: "pro7.png", pay: { 3: 7, 4: 16, 5: 44 } },
    { key: "pro8", label: "PRO 8", w: 2, img: "pro8.png", pay: { 3: 7.5, 4: 18, 5: 48 } },
    { key: "pro9", label: "PRO 9", w: 1.5, img: "pro9.png", pay: { 3: 8, 4: 20, 5: 55 } },
    { key: "pro10", label: "PRO 10", w: 1, img: "pro10.png", pay: { 3: 9, 4: 24, 5: 70 } }
  ];

  // ✅ 스핀 연출 기본값 (요청: 10초, 하나씩 멈춤)
  const SPIN = {
    totalMs: 10000,
    tickMs: 90,
    stopStepMs: 1200, // 컬럼별 멈추는 간격(대충 1.2초씩)
    bgFastMs: 180,
    bgSlowMs: 900
  };

  // ✅ 잭팟은 “운영자 수동”으로 가는 중이니까, 슬롯 자체는 당장 JACKPOT을 터뜨리지 않게 막아둔다
  const JACKPOT = {
    enabled: false // false면 5연속도 MEGA로만 처리(배너/잭팟사운드 X)
  };

  window.SLOT.config = { SCRIPT_URL, ASSET, BET, SYMBOLS, SPIN, JACKPOT };
})();
