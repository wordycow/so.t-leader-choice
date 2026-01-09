(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  async function boot(){
    // 1) 로그인 체크
    if (!U.auth.requireLogin()) return;

    // 2) 스케줄 로드
    U.schedule.init();

    // 3) 기본 UI
    U.ui.updateHeaderUI();
    U.ui.updateNicknameButton();
    U.ui.updateWalletUI();
    U.ui.bindBasicButtons();

    // 4) 시트 최신화 + 직급 + 설정 + 가격 + ebook
    await U.wallet.refreshUserFromSheet();
    U.ui.updateHeaderUI();
    U.ui.updateNicknameButton();

    await U.rank.loadAndApply();
    U.rank.bindCaptureClicks();

    await U.wallet.refreshRewardConfig();
    await U.wallet.refreshPricing();
    U.ui.updateWalletUI();

    await U.ebooks.load();

    // 5) 유튜브/보상 버튼 바인딩
    U.youtube.init();
    U.youtube.bindRewardButton();
    U.youtube.bindLuckyBox();

    // 6) 주기 동기화
    setInterval(async () => {
      try{
        await U.wallet.refreshUserFromSheet();
        await U.rank.loadAndApply();
        await U.wallet.refreshRewardConfig();
        await U.wallet.refreshPricing();
        U.ui.updateHeaderUI();
        U.ui.updateNicknameButton();
        U.ui.updateWalletUI();
      } catch(e){
        console.warn("periodic refresh error:", e);
      }
    }, U.CONFIG.REFRESH_MS);
  }

  document.addEventListener("DOMContentLoaded", boot);
}
/* =========================
   SLOT 버튼 닉네임 연동 브릿지
   - PC: #slotBtnPc
   - M : #slotBtnM
   - 슬롯: games/slot.html?u=닉네임
   - localStorage.slot_player 저장
========================= */
(function(){
  const SLOT_PATH = "games/slot.html";

  function cleanName(v){
    v = (v || "").trim();
    if(!v) return "";
    if(v === "User" || v === "회원 이름") return "";
    return v;
  }

  function getNickname(){
    // 1) localStorage 후보 키들 (프로젝트마다 키명이 달라도 대응)
    const keys = ["slot_player","unique_nickname","nickname","userNickname","the_unique_nickname"];
    for (const k of keys){
      const v = cleanName(localStorage.getItem(k));
      if(v) return v;
    }

    // 2) DOM에서 추출 (이미 화면에 찍힌 이름)
    const ids = ["tb-user-name","member-name"];
    for (const id of ids){
      const el = document.getElementById(id);
      const v = cleanName(el ? el.textContent : "");
      if(v) return v;
    }

    return "";
  }

  function applySlotLinks(){
    const nick = getNickname();
    const url = nick ? `${SLOT_PATH}?u=${encodeURIComponent(nick)}` : SLOT_PATH;

    const pc = document.getElementById("slotBtnPc");
    const m  = document.getElementById("slotBtnM");

    if(pc) pc.href = url;
    if(m)  m.href  = url;

    if(nick) localStorage.setItem("slot_player", nick);
  }

  function boot(){
    applySlotLinks();

    // 닉네임이 늦게 렌더되는 케이스 대비 (약 10초만 재시도)
    let tries = 0;
    const t = setInterval(()=>{
      applySlotLinks();
      tries++;
      if(tries >= 20) clearInterval(t);
    }, 500);

    // 클릭 순간에도 한번 더 보정
    document.addEventListener("click", (e)=>{
      const a = e.target.closest("#slotBtnPc, #slotBtnM");
      if(!a) return;
      applySlotLinks();
    });
  }

  if(document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();


