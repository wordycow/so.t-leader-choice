// games/slot/slot.config.js
window.SLOT = window.SLOT || {};
(function (S) {
  S.API_BASE = "https://the-unique-vault-api.wordycow0001.workers.dev";

  // slot.html이 games/ 아래 있으므로 상대경로는 그대로 유지
  S.IMG_PATH = (id) => `img/slot/${id}.png`;

  S.SYMBOLS = [
    "star1","star2","star3",
    "pro1","pro2","pro3","pro4","pro5","pro6","pro7","pro8","pro9","pro10"
  ];

  // 연출/설명용 페이테이블 (실제 정산은 서버)
  S.PAYTABLE = [
    { id:"star1", name:"STAR I",  pays: [0.5, 2, 10, 50, 500] },
    { id:"star2", name:"STAR II", pays: [0.5, 2, 8, 40, 400] },
    { id:"star3", name:"STAR III",pays: [0.5, 2, 5, 25, 250] },
    { id:"pro1",  name:"PRO I",   pays: [0, 1, 4, 15, 100] },
    { id:"pro2",  name:"PRO II",  pays: [0, 1, 4, 12, 80] },
    { id:"pro3",  name:"PRO III", pays: [0, 1, 3, 10, 60] },
    { id:"pro4",  name:"PRO IV",  pays: [0, 0, 3, 8, 50] },
    { id:"pro5",  name:"PRO V",   pays: [0, 0, 2, 6, 40] },
    { id:"pro6",  name:"PRO VI",  pays: [0, 0, 2, 5, 30] },
    { id:"pro7",  name:"PRO VII", pays: [0, 0, 1, 4, 20] },
    { id:"pro8",  name:"PRO VIII",pays: [0, 0, 1, 3, 15] },
    { id:"pro9",  name:"PRO IX",  pays: [0, 0, 1, 2, 10] },
    { id:"pro10", name:"PRO X",   pays: [0, 0, 1, 1, 5] }
  ];

  S.NUM_REELS = 5;

  // ✅ UI 크게 보이게 (심볼 더 큼)
  S.CELL_W = 150;
  S.CELL_H = 130;

})(window.SLOT);
