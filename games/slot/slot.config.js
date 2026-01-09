// games/slot/slot.config.js
window.SLOT = window.SLOT || {};
(function (S) {
  S.API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // slot.html이 games/ 아래 → img/slot/...
  S.IMG_PATH = (id) => `img/slot/${id}.png`;

  // ✅ 낮은→높은 (pro10 = jackpot 최고)
  S.SYMBOLS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // ✅ UI 표시용 (실정산/승률은 서버 + sheet config)
  S.PAYTABLE = [
    { id:"star1",  name:"STAR I",   pays:[1, 2, 3, 5, 8] },
    { id:"star2",  name:"STAR II",  pays:[1, 2, 4, 6, 10] },
    { id:"star3",  name:"STAR III", pays:[1, 3, 5, 8, 15] },

    { id:"pro1",  name:"PRO I",  pays:[2, 4, 8, 12, 20] },
    { id:"pro2",  name:"PRO II", pays:[3, 6, 10, 16, 25] },
    { id:"pro3",  name:"PRO III",pays:[4, 8, 12, 20, 30] },
    { id:"pro4",  name:"PRO IV", pays:[5, 10, 15, 25, 40] },
    { id:"pro5",  name:"PRO V",  pays:[6, 12, 18, 30, 50] },
    { id:"pro6",  name:"PRO VI", pays:[8, 15, 22, 36, 60] },
    { id:"pro7",  name:"PRO VII",pays:[10, 18, 28, 45, 75] },
    { id:"pro8",  name:"PRO VIII",pays:[12, 22, 35, 55, 90] },
    { id:"pro9",  name:"PRO IX", pays:[15, 28, 45, 70, 120] },
    { id:"pro10", name:"PRO X(JP)",pays:[0, 0, 0, 0, 0] }
  ];

  S.NUM_REELS = 5;
  S.CELL_W = 150;
  S.CELL_H = 130;
})(window.SLOT);
