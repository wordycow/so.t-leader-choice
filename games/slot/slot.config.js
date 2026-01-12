:root{
  --bg0:#050814;
  --panel: rgba(10,16,32,.62);
  --panel2: rgba(6,10,22,.55);
  --line: rgba(110,170,255,.22);
  --line2: rgba(220,120,255,.18);
  --text:#eaf0ff;
  --muted: rgba(234,240,255,.65);
  --aqua:#62e6ff;
  --pink:#ff6bf2;
  --gold:#ffd54a;

  --r: 18px;
  --r2: 26px;

  --shadow: 0 20px 60px rgba(0,0,0,.45);
}

*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;
  color:var(--text);
  font-family: system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
  background:
    radial-gradient(1200px 700px at 20% 10%, rgba(98,230,255,.18), transparent 55%),
    radial-gradient(900px 600px at 80% 20%, rgba(255,107,242,.16), transparent 60%),
    radial-gradient(900px 600px at 50% 90%, rgba(255,213,74,.10), transparent 60%),
    linear-gradient(180deg, #020318, #020318 40%, #050814);
  overflow-x:hidden;
}

/* ✅ 배경 항상 유지 + 스핀때 천천히 전환 */
.bg-stage{
  position:fixed;
  inset:0;
  pointer-events:none;
  z-index:-1;
}
.bg-img{
  position:absolute;
  inset:0;
  background-size:cover;
  background-position:center;
  opacity:0;
  transition: opacity 900ms ease;
  filter: saturate(1.08) contrast(1.05);
}
.bg-img.on{ opacity:.38; }

/* 스핀 중 강조(살짝만) */
.bg-flash{
  position:absolute;
  inset:0;
  opacity:0;
  transition: opacity .6s ease;
  background-size: cover;
  background-position: center;
  mix-blend-mode: screen;
  filter: saturate(1.2) contrast(1.05);
}
.bg-flash.on{ opacity:.20; }

.wrap{
  width:min(1180px, calc(100% - 28px));
  margin: 12px auto 46px;
  padding: 0;
}

.banner{
  display:none;
  margin: 10px 0 14px;
  border:1px solid rgba(255,213,74,.35);
  background: linear-gradient(90deg, rgba(255,213,74,.15), rgba(98,230,255,.10), rgba(255,107,242,.10));
  border-radius: 14px;
  overflow:hidden;
  box-shadow: var(--shadow);
}
.banner.on{ display:block; }
.ticker{
  white-space: nowrap;
  overflow:hidden;
  position:relative;
  padding: 10px 12px;
  font-weight:800;
  color: rgba(255,245,210,.95);
  text-shadow: 0 2px 14px rgba(0,0,0,.6);
}
.ticker span{
  display:inline-block;
  padding-left: 100%;
  animation: ticker 18s linear infinite;
}
@keyframes ticker{
  0%{ transform: translateX(0); }
  100%{ transform: translateX(-100%); }
}

.card{
  border-radius: var(--r2);
  border: 1px solid rgba(120,190,255,.18);
  background: linear-gradient(180deg, rgba(18,28,58,.55), rgba(6,10,22,.45));
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}

.topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 12px 14px;
  border-bottom:1px solid rgba(110,170,255,.14);
}
.title{
  letter-spacing:.22em;
  font-weight:900;
  font-size: 14px;
  color: rgba(98,230,255,.9);
}
.title b{ color: rgba(255,107,242,.92); }

.btn{
  border:1px solid rgba(98,230,255,.28);
  background: rgba(7,10,20,.45);
  color: rgba(234,240,255,.9);
  padding: 9px 12px;
  border-radius: 999px;
  cursor:pointer;
  font-weight:800;
  letter-spacing:.06em;
  transition: transform .12s ease, border-color .12s ease, background .12s ease;
  user-select:none;
  text-decoration:none;
  display:inline-flex;
  align-items:center;
  justify-content:center;
}
.btn:hover{ transform: translateY(-1px); border-color: rgba(255,107,242,.35); background: rgba(12,16,30,.55); }
.btn:active{ transform: translateY(0); }

.grid{
  display:grid;
  grid-template-columns: 1.1fr 1.4fr;
  gap: 14px;
  padding: 14px;
}
@media (max-width: 980px){
  .grid{ grid-template-columns: 1fr; }
}

/* Paytable */
.pay{ padding: 14px; }
.pay-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin-bottom: 10px;
}
.pay-head h3{
  margin:0;
  font-size: 13px;
  letter-spacing:.18em;
  color: rgba(234,240,255,.78);
}
.pay-body{
  display:none;
  border-top: 1px solid rgba(110,170,255,.12);
  padding-top: 10px;
}
.pay.open .pay-body{ display:block; }
.pay-note{
  font-size: 12px;
  color: rgba(234,240,255,.65);
  margin: 0 0 10px;
}
.pay-list{
  display:grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 10px;
}
@media (max-width: 720px){
  .pay-list{ grid-template-columns: 1fr; }
}
.pay-item{
  display:flex;
  gap: 10px;
  align-items:center;
  border: 1px solid rgba(110,170,255,.12);
  background: rgba(4,6,18,.35);
  border-radius: 14px;
  padding: 10px;
}
.pay-item img{
  width: 44px; height: 44px; object-fit: contain;
  filter: drop-shadow(0 8px 16px rgba(0,0,0,.55));
}
.pay-item .meta{ display:flex; flex-direction:column; gap:4px; min-width:0; }
.pay-item .meta .name{
  font-weight:900;
  font-size: 13px;
  letter-spacing:.08em;
  color: rgba(234,240,255,.92);
}
.pay-item .meta .rule{
  font-size: 12px;
  color: rgba(234,240,255,.68);
  line-height: 1.35;
}

/* Left status */
.status{
  padding: 14px;
  display:flex;
  flex-direction:column;
  gap: 12px;
}
.pill{
  border:1px solid rgba(110,170,255,.14);
  background: rgba(4,6,18,.32);
  border-radius: 16px;
  padding: 12px;
}
.pill .k{
  font-size: 11px;
  letter-spacing:.22em;
  color: rgba(234,240,255,.55);
  margin-bottom: 8px;
}
.pill .v{
  font-size: 16px;
  font-weight:900;
  letter-spacing:.04em;
  color: rgba(234,240,255,.92);
  display:flex;
  align-items:center;
  gap:10px;
  min-height: 22px;
}
.pill .v .dot{
  width:10px;height:10px;border-radius:999px;background: rgba(98,230,255,.9);
  box-shadow: 0 0 20px rgba(98,230,255,.55);
}
.pill .v .dot.warn{ background: rgba(255,107,242,.9); box-shadow: 0 0 20px rgba(255,107,242,.55); }
.pill .v .dot.gold{ background: rgba(255,213,74,.95); box-shadow: 0 0 22px rgba(255,213,74,.55); }

.bet-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin-top: 8px;
}
.bet{
  font-size: 24px;
  font-weight: 1000;
  color: rgba(98,230,255,.95);
  text-shadow: 0 0 22px rgba(98,230,255,.18);
  letter-spacing:.04em;
  min-width: 70px;
}
.mini{
  width: 44px;
  height: 34px;
  border-radius: 999px;
  border:1px solid rgba(110,170,255,.16);
  background: rgba(4,6,18,.35);
  color: rgba(234,240,255,.92);
  font-weight: 1000;
  cursor:pointer;
}
.mini:hover{ border-color: rgba(255,107,242,.30); }

.toggle-row{
  display:flex;
  gap:10px;
  margin-top: 10px;
}
.toggle{
  flex: 1;
  padding: 10px 12px;
  border-radius: 999px;
  border:1px solid rgba(110,170,255,.16);
  background: rgba(4,6,18,.35);
  font-weight: 1000;
  cursor:pointer;
  text-align:center;
  user-select:none;
}
.toggle.on{
  border-color: rgba(98,230,255,.35);
  background: rgba(98,230,255,.12);
  color: rgba(234,240,255,.96);
}

.spin{
  margin-top: 10px;
  width: 100%;
  padding: 12px 14px;
  border-radius: 16px;
  border: 0;
  cursor:pointer;
  font-weight: 1100;
  letter-spacing:.18em;
  color: rgba(4,6,18,.95);
  background: linear-gradient(90deg, rgba(98,230,255,.95), rgba(255,107,242,.92), rgba(255,213,74,.92));
  box-shadow: 0 18px 40px rgba(0,0,0,.35);
  transition: transform .12s ease, filter .12s ease;
}
.spin:hover{ transform: translateY(-1px); filter: saturate(1.1); }
.spin:active{ transform: translateY(0); }
.spin:disabled{ opacity:.55; cursor:not-allowed; }

/* Slot area (✅ 높이 낮춤) */
.slot-area{
  padding: 14px;
  display:flex;
  flex-direction:column;
  gap: 10px;
}
.slot-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
}
.slot-head h3{
  margin:0;
  font-size: 13px;
  letter-spacing:.18em;
  color: rgba(234,240,255,.78);
}
.slot-sub{
  font-size: 12px;
  color: rgba(234,240,255,.62);
  white-space:nowrap;
}

.slot-grid{
  display:grid;
  grid-template-columns: repeat(5, minmax(0,1fr));
  gap: 8px;
  padding: 10px;
  border-radius: 18px;
  border: 1px solid rgba(110,170,255,.12);
  background: rgba(4,6,18,.28);
  min-height: 210px; /* ✅ 기존 240 → 210 */
}

.cell{
  aspect-ratio: 1/1;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.08);
  background: radial-gradient(120px 120px at 30% 20%, rgba(98,230,255,.10), transparent 55%),
              radial-gradient(120px 120px at 70% 30%, rgba(255,107,242,.10), transparent 60%),
              rgba(2,3,10,.55);
  display:flex;
  align-items:center;
  justify-content:center;
  position:relative;
  overflow:hidden;
}
.cell img{
  width: 72%;
  height: 72%;
  object-fit: contain;
  filter: drop-shadow(0 10px 18px rgba(0,0,0,.55));
  transform: translateZ(0);
}
.cell.flash::after{
  content:"";
  position:absolute; inset:-20%;
  background: conic-gradient(from 0deg, rgba(98,230,255,.0), rgba(98,230,255,.22), rgba(255,107,242,.22), rgba(255,213,74,.22), rgba(98,230,255,.0));
  filter: blur(6px);
  animation: spinflash .55s linear infinite;
}
@keyframes spinflash{ to{ transform: rotate(360deg); } }

.float-win{
  position: fixed;
  left: 50%;
  top: 18%;
  transform: translateX(-50%);
  z-index: 50;
  pointer-events:none;
  font-weight: 1100;
  letter-spacing:.08em;
  padding: 12px 16px;
  border-radius: 999px;
  border: 1px solid rgba(255,213,74,.35);
  background: rgba(6,10,22,.65);
  box-shadow: 0 24px 70px rgba(0,0,0,.55);
  opacity:0;
}
.float-win.on{
  opacity:1;
  animation: floatpop 1.1s ease forwards;
}
@keyframes floatpop{
  0%{ transform: translateX(-50%) translateY(10px) scale(.95); opacity:0; }
  20%{ opacity:1; }
  60%{ transform: translateX(-50%) translateY(-6px) scale(1.02); }
  100%{ transform: translateX(-50%) translateY(-20px) scale(1.02); opacity:0; }
}

/* overlay */
.overlay{
  position:fixed;
  inset:0;
  display:none;
  align-items:center;
  justify-content:center;
  padding: 18px;
  background: rgba(0,0,0,.58);
  backdrop-filter: blur(10px);
  z-index: 80;
}
.overlay.on{ display:flex; }
.modal{
  width:min(520px, 100%);
  border-radius: 20px;
  border:1px solid rgba(110,170,255,.22);
  background: rgba(8,12,26,.85);
  box-shadow: 0 30px 90px rgba(0,0,0,.65);
  padding: 16px;
}
.modal h2{
  margin: 0 0 10px;
  font-size: 16px;
  letter-spacing:.08em;
}
.modal p{
  margin: 0 0 12px;
  color: rgba(234,240,255,.70);
  line-height:1.45;
  font-size: 13px;
}
.modal .row{
  display:flex;
  gap:10px;
  justify-content:flex-end;
}
