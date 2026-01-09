(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  async function boot() {
    // 1) 로그인 체크
    if (!U.auth || !U.auth.requireLogin || !U.auth.requireLogin()) return;

    // 2) 스케줄 로드
    if (U.schedule && U.schedule.init) U.schedule.init();

    // 3) 기본 UI
    if (U.ui) {
      U.ui.updateHeaderUI && U.ui.updateHeaderUI();
      U.ui.updateNicknameButton && U.ui.updateNicknameButton();
      U.ui.updateWalletUI && U.ui.updateWalletUI();
      U.ui.bindBasicButtons && U.ui.bindBasicButtons();
    }

    // 4) 시트 최신화 + 직급 + 설정 + 가격 + ebook
    if (U.wallet && U.wallet.refreshUserFromSheet) {
      await U.wallet.refreshUserFromSheet();
      U.ui && U.ui.updateHeaderUI && U.ui.updateHeaderUI();
      U.ui && U.ui.updateNicknameButton && U.ui.updateNicknameButton();
    }

    if (U.rank && U.rank.loadAndApply) {
      await U.rank.loadAndApply();
      U.rank.bindCaptureClicks && U.rank.bindCaptureClicks();
    }

    if (U.wallet) {
      U.wallet.refreshRewardConfig && (await U.wallet.refreshRewardConfig());
      U.wallet.refreshPricing && (await U.wallet.refreshPricing());
      U.ui && U.ui.updateWalletUI && U.ui.updateWalletUI();
    }

    if (U.ebooks && U.ebooks.load) {
      await U.ebooks.load();
    }

    // 5) 유튜브/보상 버튼 바인딩
    if (U.youtube) {
      U.youtube.init && U.youtube.init();
      U.youtube.bindRewardButton && U.youtube.bindRewardButton();
      U.youtube.bindLuckyBox && U.youtube.bindLuckyBox();
    }

    // 6) 주기 동기화
    const refreshMs =
      (U.CONFIG && U.CONFIG.REFRESH_MS) ? U.CONFIG.REFRESH_MS : 15000;

    setInterval(async () => {
      try {
        if (U.wallet && U.wallet.refreshUserFromSheet) await U.wallet.refreshUserFromSheet();
        if (U.rank && U.rank.loadAndApply) await U.rank.loadAndApply();
        if (U.wallet && U.wallet.refreshRewardConfig) await U.wallet.refreshRewardConfig();
        if (U.wallet && U.wallet.refreshPricing) await U.wallet.refreshPricing();

        if (U.ui) {
          U.ui.updateHeaderUI && U.ui.updateHeaderUI();
          U.ui.updateNicknameButton && U.ui.updateNicknameButton();
          U.ui.updateWalletUI && U.ui.updateWalletUI();
        }
      } catch (e) {
        console.warn("periodic refresh error:", e);
      }
    }, refreshMs);
  }

  document.addEventListener("DOMContentLoaded", boot);
})(); // ✅ 이게 빠져서 전체가 죽었던 거야


/* =========================
   SLOT 버튼 닉네임 연동 브릿지
   - PC: #slotBtnPc
   - M : #slotBtnM
   - (추가) 단일 CTA: #slotCta
   - 슬롯: games/slot.html?u=닉네임
   - localStorage.slot_player 저장
========================= */
(function () {
  const SLOT_PATH = "games/slot.html";

  function cleanName(v) {
    v = (v || "").trim();
    if (!v) return "";
    if (v === "User" || v === "회원 이름") return "";
    return v;
  }

  function getNickname() {
    // 1) localStorage 후보 키들
    const keys = ["slot_player", "unique_nickname", "nickname", "userNickname", "the_unique_nickname"];
    for (const k of keys) {
      const v = cleanName(localStorage.getItem(k));
      if (v) return v;
    }

    // 2) DOM에서 추출
    const ids = ["tb-user-name", "member-name"];
    for (const id of ids) {
      const el = document.getElementById(id);
      const v = cleanName(el ? el.textContent : "");
      if (v) return v;
    }

    return "";
  }

  function applySlotLinks(){
  const nick = getNickname();

  // uid 후보: DOM 또는 localStorage
  const uid =
    (document.getElementById("member-id")?.textContent || "").trim() ||
    (localStorage.getItem("unique_userid") || "").trim();

  // ut 후보: 화면 표시값
  const ut =
    (document.getElementById("my-ut-display")?.textContent || "").trim() ||
    (localStorage.getItem("unique_ut") || "").trim();

  const params = new URLSearchParams();
  if(nick) params.set("u", nick);
  if(uid)  params.set("uid", uid);
  if(ut)   params.set("ut", ut);

  const url = params.toString() ? `${SLOT_PATH}?${params.toString()}` : SLOT_PATH;

  const pc = document.getElementById("slotBtnPc");
  const m  = document.getElementById("slotBtnM");

  if(pc) pc.href = url;
  if(m)  m.href  = url;

  if(nick) localStorage.setItem("slot_player", nick);
  if(uid)  localStorage.setItem("unique_userid", uid);
  if(ut)   localStorage.setItem("unique_ut", ut);
}


  function boot() {
    applySlotLinks();

    // 닉네임이 늦게 렌더되는 케이스 대비 (약 10초만 재시도)
    let tries = 0;
    const t = setInterval(() => {
      applySlotLinks();
      tries++;
      if (tries >= 20) clearInterval(t);
    }, 500);

    // 클릭 순간에도 한번 더 보정
    document.addEventListener("click", (e) => {
      const a = e.target.closest("#slotBtnPc, #slotBtnM, #slotCta");
      if (!a) return;
      applySlotLinks();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
