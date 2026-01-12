(() => {
  const SLOT = (window.SLOT = window.SLOT || {});
  const CFG = () => SLOT.config;

  const el = {};
  let state = {
    id: "",
    name: "",
    balance: 0,
    jackpot: 0,
    bet: CFG().BET.def,
    spinning: false,
    auto: false,
  };

  function $(id){ return document.getElementById(id); }

  function readBet(){
    const v = Number(localStorage.getItem(CFG().STORAGE_KEYS.bet));
    if (!Number.isFinite(v)) return CFG().BET.def;
    return Math.max(CFG().BET.min, Math.min(CFG().BET.max, v));
  }

  function writeBet(v){
    localStorage.setItem(CFG().STORAGE_KEYS.bet, String(v));
  }

  function readAuto(){
    return localStorage.getItem(CFG().STORAGE_KEYS.auto) === "1";
  }
  function writeAuto(on){
    localStorage.setItem(CFG().STORAGE_KEYS.auto, on ? "1" : "0");
  }

  function setAuto(on){
    state.auto = !!on;
    writeAuto(state.auto);
    el.autoBtn.textContent = state.auto ? "AUTO ON" : "AUTO OFF";
  }

  function syncSoundBtn(){
    el.soundBtn.textContent = SLOT.audio.enabled ? "SOUND ON" : "SOUND OFF";
  }

  function clampBet(v){
    v = Math.round(v);
    v = Math.max(CFG().BET.min, Math.min(CFG().BET.max, v));
    return v;
  }

  function setBet(v){
    state.bet = clampBet(v);
    writeBet(state.bet);
    SLOT.UI.setBet(state.bet);
  }

  function lockUi(lock){
    state.spinning = !!lock;
    el.spinBtn.disabled = lock;
    el.betUp.disabled = lock;
    el.betDown.disabled = lock;
    el.autoBtn.disabled = lock;
  }

  async function doSpin(){
    if (state.spinning) return;

    lockUi(true);
    try {
      const res = await SLOT.game.spin({
        id: state.id,
        bet: state.bet,
        onUpdateUser: ({ balance }) => {
          state.balance = Number(balance || 0);
          SLOT.UI.setWallet(state.balance);
        }
      });

      if (res && res.ok && res.user && typeof res.user.balance !== "undefined") {
        state.balance = Number(res.user.balance || 0);
        SLOT.UI.setWallet(state.balance);
      }

    } finally {
      lockUi(false);
      if (state.auto) {
        // auto는 템포 살짝 쉬고 재스핀
        setTimeout(() => { if (state.auto) doSpin(); }, 300);
      }
    }
  }

  async function boot({ id }){
    state.id = String(id || "").trim().toLowerCase();
    state.bet = readBet();
    setAuto(readAuto());

    // 사운드 버튼
    syncSoundBtn();

    // 초기 UI
    SLOT.UI.setBet(state.bet);
    SLOT.UI.setLast("READY");

    // 서버 상태
    const st = await SLOT.api.getSlotState(state.id).catch(err => ({ ok:false, error:String(err?.message||err) }));
    if (!st || !st.ok) {
      SLOT.UI.setLast("READY");
      return;
    }

    const user = st.user || {};
    state.name = user.nickname || user.name || state.id;
    state.balance = Number(user.balance || 0);
    state.jackpot = Number(st.jackpotTotal || 0);

    SLOT.UI.setPlayer(state.name);
    SLOT.UI.setWallet(state.balance);
    SLOT.UI.setJackpot(state.jackpot);

    // 초기 그리드
    const initKeys = Array.from({length: 15}, () => CFG().SYMBOLS[Math.floor(Math.random()*CFG().SYMBOLS.length)].key);
    SLOT.UI.setGrid(initKeys);

    // 이벤트
    el.spinBtn.addEventListener("click", async () => {
      await SLOT.audio.unlock();
      doSpin();
    });

    el.betUp.addEventListener("click", () => setBet(state.bet + CFG().BET.step));
    el.betDown.addEventListener("click", () => setBet(state.bet - CFG().BET.step));

    el.autoBtn.addEventListener("click", () => setAuto(!state.auto));

    el.soundBtn.addEventListener("click", async () => {
      await SLOT.audio.unlock();
      SLOT.audio.setEnabled(!SLOT.audio.enabled);
      syncSoundBtn();
    });
  }

  function initDom(){
    el.spinBtn = $("spinBtn");
    el.betUp = $("betUp");
    el.betDown = $("betDown");
    el.autoBtn = $("autoBtn");
    el.soundBtn = $("soundBtn");
  }

  SLOT.app = { initDom, boot };
})();
