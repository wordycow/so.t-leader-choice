/* games/slot/slot.game.js */
/* 릴(3x5) 렌더링 마운트가 없어서 죽는 문제 해결 + 기본 렌더 제공 */

window.SLOT = window.SLOT || {};
(function (S) {

  // ✅ 릴을 붙일 마운트 자동 탐색
  function findMount() {
    return (
      document.getElementById("reels") ||
      document.getElementById("reelMount") ||
      document.getElementById("slotStage") ||
      document.getElementById("stage") ||
      document.querySelector("[data-slot-stage]") ||
      document.querySelector(".slot-stage") ||
      document.querySelector(".stage") ||
      null
    );
  }

  // ✅ 없으면 “오른쪽 큰 패널”로 보이는 곳에 reels를 만들어 붙임
  function ensureMount() {
    let mount = findMount();
    if (mount) return mount;

    // 오른쪽 패널로 추정되는 후보들
    const candidate =
      document.getElementById("gameStage") ||
      document.querySelector(".right-panel") ||
      document.querySelector(".panel-right") ||
      document.querySelector(".stage-wrap") ||
      document.querySelector(".board") ||
      document.body;

    mount = document.createElement("div");
    mount.id = "reels";
    mount.style.width = "100%";
    mount.style.height = "100%";
    mount.style.display = "flex";
    mount.style.alignItems = "center";
    mount.style.justifyContent = "center";

    candidate.appendChild(mount);
    return mount;
  }

  // ✅ 심볼 이미지 경로 기본값 (없으면 자동 보정)
  function imgPath(id) {
    if (typeof S.IMG_PATH === "function") return S.IMG_PATH(id);
    // slot.html 위치가 /games/slot.html 이면 img/slot/... 이 맞음
    return `img/slot/${id}.png`;
  }

  // ✅ 3x5 기본 그리드 렌더
  function renderGrid(grid) {
    const mount = ensureMount();
    if (!mount) return;

    // grid 없으면 빈 그리드
    const g = Array.isArray(grid) ? grid : [
      ["star1","star2","star3","pro1","pro5"],
      ["star2","star3","pro1","pro5","pro10"],
      ["star1","star2","star3","pro1","pro5"]
    ];

    // (기존 CSS가 없어도 보이게 최소 스타일을 인라인로 같이 줌)
    mount.innerHTML = `
      <div class="slot-grid" style="
        width: 100%;
        height: 100%;
        max-width: 900px;
        aspect-ratio: 16/9;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        grid-template-rows: repeat(3, 1fr);
        gap: 12px;
        padding: 18px;
        box-sizing: border-box;
      ">
        ${g.flatMap((row, r) =>
          row.map((id, c) => `
            <div class="slot-cell" data-r="${r}" data-c="${c}" style="
              border-radius: 18px;
              background: rgba(0,0,0,0.18);
              border: 1px solid rgba(255,255,255,0.10);
              display:flex;
              align-items:center;
              justify-content:center;
              overflow:hidden;
            ">
              <img alt="${id}" src="${imgPath(id)}" style="
                width: 80%;
                height: 80%;
                object-fit: contain;
                filter: drop-shadow(0 10px 18px rgba(0,0,0,0.35));
              "/>
            </div>
          `)
        ).join("")}
      </div>
    `;
  }

  // ✅ 초기 릴 생성(기존 buildReels 호출부 호환)
  function buildReels() {
    // 여기서 null이면 죽던 문제를 제거
    renderGrid(null);
  }

  // 외부에서 쓰기 좋게 노출
  S.game = S.game || {};
  S.game.buildReels = buildReels;
  S.game.renderGrid = renderGrid;

})(window.SLOT);
