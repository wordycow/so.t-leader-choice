// games/slot/slot.config.js
window.SLOT = window.SLOT || {};
(function (S) {
  // ✅ Worker (슬롯 API)
  S.API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // (추후: 확률/룰/페이 시트 연동용으로 보관)
  S.GS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // slot.html이 games/ 아래 있으므로 상대경로는 그대로 유지
  S.IMG_PATH = (id) => `img/slot/${id}.png`;

  /**
   * ✅ 서열(낮음 → 높음)
   * star1 < star2 < star3 < pro1 ... < pro9 < pro10(잭팟)
   */
  S.SYMBOLS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  /**
   * ✅ 연출/설명용 페이테이블 (실제 정산은 서버에서 결정)
   * - 값은 "서열"에 맞게 오름차순으로만 잡아둠
   * - 나중에 진짜 배당은 worker가 시트(slot_config)에서 읽어서 계산하게 만들면 됨
   */
  S.PAYTABLE = [
    { id:"star1",  name:"STAR I",          pays: [0.1, 0.3, 1,  3,   8] },
    { id:"star2",  name:"STAR II",         pays: [0.2, 0.6, 2,  6,  15] },
    { id:"star3",  name:"STAR III",        pays: [0.3, 1.0, 3, 10,  25] },

    { id:"pro1",   name:"PRO I",           pays: [0.4, 1.2, 4, 12,  30] },
    { id:"pro2",   name:"PRO II",          pays: [0.5, 1.5, 5, 15,  40] },
    { id:"pro3",   name:"PRO III",         pays: [0.6, 2.0, 6, 18,  50] },
    { id:"pro4",   name:"PRO IV",          pays: [0.8, 2.5, 8, 25,  70] },
    { id:"pro5",   name:"PRO V",           pays: [1.0, 3.0,10, 30,  90] },
    { id:"pro6",   name:"PRO VI",          pays: [1.2, 3.8,12, 38, 110] },
    { id:"pro7",   name:"PRO VII",         pays: [1.5, 4.8,15, 48, 140] },
    { id:"pro8",   name:"PRO VIII",        pays: [2.0, 6.0,20, 60, 180] },
    { id:"pro9",   name:"PRO IX",          pays: [3.0, 9.0,30, 90, 260] },

    // ✅ 최상위 = 잭팟
    { id:"pro10",  name:"PRO X (JACKPOT)", pays: [5.0,15.0,50,150, 500] }
  ];

  S.NUM_REELS = 5;

  // ✅ UI 크게 보이게 (심볼 더 큼)
  S.CELL_W = 150;
  S.CELL_H = 130;

})(window.SLOT);
