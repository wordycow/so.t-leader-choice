(function () {
  window.UNIQUE = window.UNIQUE || {};
  window.UNIQUE.CONFIG = {
    // Supabase
    SUPABASE_URL: "https://lrpscubricemcgfssjgg.supabase.co",
    SUPABASE_KEY: "sb_publishable_8mMA4oEsuB9j0rc6KsLmtQ_UkJo0Zaq",

    // Apps Script(JSONP)
    GOOGLE_SCRIPT_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",

    // UT 가격 계산 비율 (총기부USDT의 30% / 총UT)
    UT_PRICE_FACTOR: 0.30,

    // Rank
    RANK_JSON: "rank-hall.json",
    RANK_PAGE: "rank-hall.html",
    PROMO_PAGE: "the-unique-promo.html",

    // eBook
    EBOOK_JSON: "ebook-config.json",
    EBOOK_FALLBACK: [
      { id:"unique-basic", title:"협력을 배우고 협력을 만들어낸다.", description:"THE UNIQUE 기본 매뉴얼", cover:"img/ebook-the-unique-system-book.jpg", link:"ebook.html", visible:true, order:1, posY:50 },
      { id:"unique-sot", title:"현대 사회에 맞는 여행도구 so.t", description:"so.t 안에서 서로를 챙겨주며 함께 여행을 그린다.", cover:"img/ebook-network-marketing-cover.jpg", link:"ebook1.html", visible:true, order:2, posY:50 }
    ],

    // Schedule (gviz)
    SCHEDULE_GVIZ_URL: "https://docs.google.com/spreadsheets/d/1C4fyJtyBHSaBIWyN_lM75Zp7myvtz3cKfHYUbAmoVQY/gviz/tq?gid=0&tqx=responseHandler:handleScheduleSheet",

    // ✅ 유튜브 지식채굴 영상 ID (요청 반영)
    YT_VIDEO_ID: "DBcSLPRz0HI",

    // 주기 동기화
    REFRESH_MS: 30000
  };
})();
