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
   MAIN ← SLOT (query sync)
   - slot에서 돌아올 때 ?u= &uid= &ut=
   - localStorage에 즉시 반영 (UT 동기화 핵심)
========================= */
(function () {
  try {
    const qs = new URLSearchParams(location.search);
    const u   = (qs.get("u") || "").trim();
    const uid = (qs.get("uid") || "").trim();
    const ut  = (qs.get("ut") || "").trim();

    if (u)   localStorage.setItem("slot_player", u);
    if (u)   localStorage.setItem("unique_nickname", u);

    if (uid) localStorage.setItem("unique_userid", uid);
    if (uid) localStorage.setItem("uid", uid);

    if (ut)  localStorage.setItem("unique_ut", ut);
  } catch (e) {
    console.warn("query sync error:", e);
  }
})();

/* =========================
   SLOT 버튼 닉네임/UID/UT 연동 브릿지 (강화판)
   - PC: #slotBtnPc
   - M : #slotBtnM
   - CTA: #slotCta
   - 슬롯: games/slot.html?u=닉네임&uid=회원UID&ut=표시용UT
   - uid 없으면 이동 막고 안내 (missing_user 방지 핵심)
========================= */
(function () {
  const SLOT_PATH = "games/slot.html";

  function clean(v) {
    v = (v || "").trim();
    if (!v) return "";
    if (v === "User" || v === "회원 이름") return "";
    return v;
  }

  function textById(id) {
    const el = document.getElementById(id);
    return clean(el ? (el.textContent || el.value || "") : "");
  }

  function fromLS(keys) {
    for (const k of keys) {
      const v = clean(localStorage.getItem(k));
      if (v) return v;
    }
    return "";
  }

  function getNickname() {
    // 1) localStorage
    const v1 = fromLS(["slot_player", "unique_nickname", "nickname", "userNickname", "the_unique_nickname"]);
    if (v1) return v1;

    // 2) DOM
    const v2 = textById("tb-user-name") || textById("member-name") || textById("nickname");
    if (v2) return v2;

    // 3) window.UNIQUE 상태값(있으면)
    const U = window.UNIQUE || {};
    const v3 = clean(U.STATE?.nickname) || clean(U.STATE?.user?.nickname) || clean(U.user?.nickname);
    if (v3) return v3;

    return "";
  }

  function getUid() {
    // 1) localStorage (가장 확실)
    const v1 = fromLS(["unique_userid", "uid", "userId", "memberId"]);
    if (v1) return v1;

    // 2) DOM 후보 확장
    const v2 =
      textById("member-id") ||
      textById("tb-user-id") ||
      textById("user-id") ||
      textById("uid") ||
      textById("my-uid");
    if (v2) return v2;

    // 3) window.UNIQUE 상태값(있으면)
    const U = window.UNIQUE || {};
    const v3 =
      clean(U.STATE?.uid) ||
      clean(U.STATE?.userId) ||
      clean(U.STATE?.user?.uid) ||
      clean(U.STATE?.user?.id) ||
      clean(U.user?.uid);
    if (v3) return v3;

    return "";
  }

  function getUt() {
    // 1) localStorage
    const v1 = fromLS(["unique_ut", "ut", "balanceUT"]);
    if (v1) return v1;

    // 2) DOM 후보 확장
    const v2 =
      textById("my-ut-display") ||
      textById("tb-user-ut") ||
      textById("user-ut") ||
      textById("ut");
    if (v2) return v2;

    // 3) window.UNIQUE 상태값(있으면)
    const U = window.UNIQUE || {};
    const v3 =
      clean(U.STATE?.ut) ||
      clean(U.STATE?.balanceUT) ||
      clean(U.STATE?.user?.ut) ||
      clean(U.user?.ut);
    if (v3) return v3;

    return "";
  }

  function buildSlotUrl(nick, uid, ut) {
    const params = new URLSearchParams();
    if (nick) params.set("u", nick);
    if (uid)  params.set("uid", uid);
    if (ut)   params.set("ut", ut);
    return params.toString() ? `${SLOT_PATH}?${params.toString()}` : SLOT_PATH;
  }

  function applySlotLinks() {
    const nick = getNickname();
    const uid  = getUid();
    const ut   = getUt();

    // 저장 (다음 페이지에서도 유지)
    if (nick) localStorage.setItem("slot_player", nick);
    if (nick) localStorage.setItem("unique_nickname", nick);
    if (uid)  localStorage.setItem("unique_userid", uid);
    if (uid)  localStorage.setItem("uid", uid);
    if (ut)   localStorage.setItem("unique_ut", ut);

    const url = buildSlotUrl(nick, uid, ut);

    const pc  = document.getElementById("slotBtnPc");
    const m   = document.getElementById("slotBtnM");
    const cta = document.getElementById("slotCta");

    [pc, m, cta].forEach(a => {
      if (!a) return;
      a.href = url;

      // ✅ uid 없으면 안내 + 시각적 힌트(완전 비활성은 클릭에서 막음)
      if (!uid) {
        a.setAttribute("data-slot-disabled", "1");
        a.title = "슬롯은 로그인 후(회원 UID 필요) 이용 가능합니다.";
      } else {
        a.removeAttribute("data-slot-disabled");
        a.title = "";
      }
    });

    return { nick, uid, ut, url };
  }

  function boot() {
    applySlotLinks();

    // 닉네임/uid 렌더가 늦는 케이스 대비 (10초 재시도)
    let tries = 0;
    const t = setInterval(() => {
      applySlotLinks();
      tries++;
      if (tries >= 20) clearInterval(t);
    }, 500);

    // 클릭 순간에도 한번 더 보정 + uid 없으면 이동 막기
    document.addEventListener("click", (e) => {
      const a = e.target.closest("#slotBtnPc, #slotBtnM, #slotCta");
      if (!a) return;

      const { uid } = applySlotLinks();
      if (!uid) {
        e.preventDefault();
        alert("슬롯은 메인에서 로그인 후 이용 가능합니다. (회원 UID가 필요해요)");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
/* ===== slot 이동: 로그인 id를 붙여서 넘어가기 (main → slot) ===== */
(function () {
  function getLoginId() {
    // 1) gate가 저장한 uniqueCurrentUser 우선
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const u = JSON.parse(raw);
        if (u && u.id) return String(u.id).trim();
      }
    } catch (e) {}

    // 2) 호환 키들
    const keys = ["unique_user_id", "user_id", "uid", "id"];
    for (const k of keys) {
      const v = (localStorage.getItem(k) || "").trim();
      if (v) return v;
    }
    return "";
  }

  // 클릭용 (onclick에서 호출)
  window.goCasinoFromMain = function (e) {
    if (e) e.preventDefault();

    const id = getLoginId();
    if (!id) {
      alert("로그인 정보가 없습니다. 게이트에서 로그인 후 다시 시도하세요.");
      location.href = "the-unique-gate.html";
      return false;
    }
    location.href = "games/slot.html?id=" + encodeURIComponent(id);
    return false;
  };

  // 우클릭 새탭/새창 열기에서도 id가 붙도록 href도 갱신
  function refreshSlotHref() {
    const a = document.getElementById("slotBtn");
    if (!a) return;
    const id = getLoginId();
    if (id) a.href = "games/slot.html?id=" + encodeURIComponent(id);
  }

  // 지금 바로 + DOM 로드 후 한 번 더
  refreshSlotHref();
  document.addEventListener("DOMContentLoaded", refreshSlotHref);
})();
