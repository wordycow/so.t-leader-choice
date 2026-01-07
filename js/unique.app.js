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
})();
