// games/slot/slot.app.js
(() => {
  const $ = (id) => document.getElementById(id);

  function setText(id, v){
    const el = $(id);
    if (el) el.textContent = String(v ?? "");
  }

  function setNote(msg){
    const el = $("uiNote");
    if (el) el.textContent = msg || "";
  }

  function updateLocalStorageBalance(newBal){
    try{
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (!raw) return;
      const u = JSON.parse(raw);
      u.balance = Number(newBal || 0);
      localStorage.setItem("uniqueCurrentUser", JSON.stringify(u));
      localStorage.setItem("myUtPoints", String(Number(newBal || 0)));
    }catch(e){}
  }

  async function boot(){
    // 세션 체크
    const u = window.SLOT_API?.getLocalUser?.();
    if (!u){
      location.href = "../the-unique-gate.html";
      return;
    }

    // 기본 표시(즉시)
    setText("uiPlayer", `${u.id} / ${u.name || "-"}`);
    setText("uiWallet", Number(u.balance||0));
    setText("uiJackpot", "…");
    setText("uiResult", "READY");
    setNote("");

    // 시트에서 최신값 로드
    try{
      const r = await window.SLOT_API.getSlotState();
      if (!r || !r.ok || !r.user){
        setNote("시트에서 유저 정보를 불러오지 못했습니다.");
        return;
      }

      setText("uiPlayer", `${r.user.id} / ${r.user.name || "-"}`);
      setText("uiWallet", Number(r.user.balance||0));
      setText("uiJackpot", Number(r.jackpotTotal || 0));

      updateLocalStorageBalance(Number(r.user.balance||0));

    }catch(e){
      setNote("네트워크 오류로 유저 정보를 불러오지 못했습니다.");
    }
  }

  // ✅ 게임(스핀) 끝난 직후 “딱 여기만” 호출하면 된다.
  // netDelta: 승리면 +, 패배면 -
  // lossAmount: 패배 금액(양수). 승리면 0
  window.SLOT_COMMIT_RESULT = async function({ netDelta = 0, lossAmount = 0, resultText = "" } = {}){
    try{
      const r = await window.SLOT_API.commitSlotSpin({ netDelta, lossAmount });
      if (!r || !r.ok || !r.user){
        setNote("시트 반영 실패. (잠시 후 다시)");
        return;
      }

      // UI 반영
      setText("uiWallet", Number(r.user.balance||0));
      setText("uiJackpot", Number(r.jackpotTotal||0));
      if (resultText) setText("uiResult", resultText);

      updateLocalStorageBalance(Number(r.user.balance||0));

    }catch(e){
      setNote("시트 반영 중 네트워크 오류.");
    }
  };

  // 외부에서 강제 새로고침용
  window.SLOT_REFRESH = boot;

  document.addEventListener("DOMContentLoaded", boot);
})();
