(function () {
  const S = (window.S = window.S || {});
  S.CONFIG = S.CONFIG || {};

  // ✅ 경로 (slot.html 기준: /games)
  S.CONFIG.IMG_DIR = "img/slot";
  S.CONFIG.SOUND_DIR = "sounds";

  // ✅ 배경 PNG OK
  S.CONFIG.BG_LIST = [
    "img/slot/bg1.png",
    "img/slot/bg2.png",
    "img/slot/bg3.png",
    "img/slot/bg4.png",
    "img/slot/bg5.png",
  ];

  // ✅ 베팅 (유송 요구: ±5 / 기본 10)
  S.CONFIG.BET_DEFAULT = 10;
  S.CONFIG.BET_MIN = 10;
  S.CONFIG.BET_MAX = 1000;
  S.CONFIG.BET_STEP = 5;

  // ✅ 5x3
  S.CONFIG.COLS = 5;
  S.CONFIG.ROWS = 3;

  // ✅ 사운드 파일명(대소문자 그대로)
  S.CONFIG.SOUNDS = {
    start: "sounds/start-button-sound.MP3",
    spin: "sounds/spining-sound.MP3",        // 철자 주의: spining
    stop: "sounds/stop-stop-stop-sound.MP3",
    win: "sounds/win-sound.MP3",
    lose: "sounds/lose-sound.MP3",
    jackpot: "sounds/jackpot-sound.MP3",
  };

  // ✅ 로그인 키(게이트/메인에서 저장된 값 최대한 다 잡아줌)
  S.CONFIG.LOGIN_KEYS = [
    "unique_user",
    "UNIQUE_USER",
    "uniqueUser",
    "unique.user",
    "user",
    "USER",
    "login",
    "auth",
    "unique_id",
    "UNIQUE_ID",
    "user_id",
    "uid",
    "id",
    "slot_user_id", // 슬롯이 마지막으로 기억해둔 값
  ];
})();
