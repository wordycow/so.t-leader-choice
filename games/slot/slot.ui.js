// games/slot/slot.ui.js
window.SLOT = window.SLOT || {};
(function (S) {
  const $ = (id) => document.getElementById(id);

  const els = {
    apiDot: $("apiDot"),
    apiText: $("apiText"),
    soundBtn: $("soundBtn"),
    soundText: $("soundText"),

    playerName: $("playerName"),
    playerUt: $("playerUt"),

    betVal: $("betVal"),
    jpVal: $("jpVal"),
    winVal: $("winVal"),

    log: $("log"),
    ecoBox: $("ecoBox"),
    payGrid: $("payGrid"),
  };

  function fmtNum(v, digits = 0){
    const n = Number(v);
    if (!Number.isFinite(n)) return digits ? (0).toFixed(digits) : "0";
    return digits ? n.toFixed(digits) : String(Math.trunc(n));
  }

  function setOnline(on){
    if(!els.apiDot || !els.apiText) return;
    els.apiDot.style.background = on ? "#22c55e" : "#ef4444";
    els.apiText.textContent = on ? "Online" : "Offline";
  }

  function setLog(text){
    if(els.log) els.log.textContent = text;
  }

  function setPlayer(p){
    if(!p) return;
    // ✅ displayName 우선, 없으면 u, 없으면 Guest
    const name = (p.displayName || p.u || "Guest").toString();
    if(els.playerName) els.playerName.textContent = name;

    // ✅ UT
    if(els.playerUt && p.ut !== undefined && p.ut !== null){
      els.playerUt.textContent = fmtNum(p.ut, 2);
    }
  }

  function setKpi({ bet, jackpot, win }){
    if(els.betVal && bet !== undefined) els.betVal.textContent = fmtNum(bet, 0);
    if(els.jpVal && jackpot !== undefined) els.jpVal.textContent = fmtNum(jackpot, 0);
    if(els.winVal && win !== undefined) els.winVal.textContent = fmtNum(win, 0);
  }

  function setEconomy(info){
    if(!els.ecoBox) return;
    if(!info){
      els.ecoBox.textContent = "ECON: -";
      return;
    }
    const lines = [
      `TOTAL ISSUED UT: ${fmtNum(info.totalIssuedUT ?? 0, 0)}`,
      `UT PRICE: ${fmtNum(info.utPrice ?? 0, 4)}`,
      `WIN SCALE: ${fmtNum(info.winScale ?? 1, 3)}`
    ];
    els.ecoBox.textContent = lines.join("\n");
  }

  function buildPaytable(){
    if(!els.payGrid) return;
    els.payGrid.innerHTML = "";

    (S.PAYTABLE || []).forEach(row => {
      const wrap = document.createElement("div");
      wrap.className = "pay-row";

      const left = document.createElement("div");
      left.className = "pay-left";

      const img = document.createElement("img");
      img.className = "pay-icon";
      img.alt = row.id;
      img.src = S.IMG_PATH(row.id);

      const nm = document.createElement("div");
      nm.className = "pay-name";
      nm.textContent = row.name;

      left.appendChild(img);
      left.appendChild(nm);

      const right = document.createElement("div");
      right.className = "pay-right";
      // 표시용 숫자만
      right.textContent = (row.pays || []).join("  ");

      wrap.appendChild(left);
      wrap.appendChild(right);
      els.payGrid.appendChild(wrap);
    });
  }

  // sound toggle UI
  function bindSound(){
    if(!els.soundBtn) return;
    els.soundBtn.addEventListener("click", () => {
      const on = S.audio.toggle();
      if(els.soundText) els.soundText.textContent = on ? "SOUND: ON" : "SOUND: OFF";
    });
  }

  bindSound();

  S.ui = {
    setOnline,
    setLog,
    setPlayer,
    setKpi,
    setEconomy,
    buildPaytable
  };
})(window.SLOT);
