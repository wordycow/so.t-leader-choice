// games/slot/slot.ui.js
window.SLOT = window.SLOT || {};
(function (S) {
  const betVal = document.getElementById("betVal");
  const jpVal  = document.getElementById("jpVal");
  const winVal = document.getElementById("winVal");
  const logEl  = document.getElementById("log");

  const apiDot  = document.getElementById("apiDot");
  const apiText = document.getElementById("apiText");

  const playerName = document.getElementById("playerName");
  const playerUid  = document.getElementById("playerUid");
  const playerUt   = document.getElementById("playerUt");

  function setOnline(ok){
    if(ok){
      apiDot.classList.add("ok");
      apiText.textContent = "Online";
    } else {
      apiDot.classList.remove("ok");
      apiText.textContent = "Offline";
    }
  }

  function setKpi({ bet, jackpot, win } = {}){
    if (bet !== undefined && bet !== null) betVal.textContent = bet;
    if (jackpot !== undefined && jackpot !== null) jpVal.textContent = jackpot;
    if (win !== undefined && win !== null) winVal.textContent = win;
  }

  function setLog(text){
    logEl.textContent = String(text || "");
  }

  function setPlayer({ u, uid, ut } = {}){
    playerName.textContent = u || "Guest";
    playerUid.textContent = uid || "-";
    if (ut !== undefined && ut !== null && ut !== "") playerUt.textContent = ut;
  }

  function buildPaytable(){
    const payGrid = document.getElementById("payGrid");
    payGrid.innerHTML = "";

    S.PAYTABLE.forEach(p => {
      const row = document.createElement("div");
      row.className = "pay-row";
      row.innerHTML = `
        <img src="${S.IMG_PATH(p.id)}" class="pay-img" alt="${p.id}">
        <div class="pay-data">
          <div class="pay-name">${p.name}</div>
          <div class="pay-muls">
            <div><span class="lbl">1x</span><span>${p.pays[0] || '-'}</span></div>
            <div><span class="lbl">2x</span><span>${p.pays[1] || '-'}</span></div>
            <div><span class="lbl">3x</span><span>${p.pays[2] || '-'}</span></div>
            <div><span class="lbl">4x</span><span>${p.pays[3] || '-'}</span></div>
            <div><span class="lbl">5x</span><span class="high">${p.pays[4] || '-'}</span></div>
          </div>
        </div>
      `;
      payGrid.appendChild(row);
    });
  }

  S.ui = { setOnline, setKpi, setLog, setPlayer, buildPaytable };
})(window.SLOT);
