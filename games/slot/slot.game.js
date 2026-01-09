// games/slot/slot.game.js
window.SLOT = window.SLOT || {};
(function (S) {

  const reelsEl = document.getElementById("reels");
  const reels = [];

  function createSymbol(sym){
    const d = document.createElement("div");
    d.className = "symbol";
    const img = document.createElement("img");
    img.src = S.IMG_PATH(sym);
    img.alt = sym;
    d.appendChild(img);
    return d;
  }

  function buildReels(){
    reelsEl.innerHTML = "";
    reels.length = 0;

    for(let i=0; i<S.NUM_REELS; i++){
      const col = document.createElement("div");
      col.className = "reel-col";

      const strip = document.createElement("div");
      strip.className = "reel-strip";

      for(let k=0; k<12; k++){
        strip.appendChild(createSymbol(S.SYMBOLS[Math.floor(Math.random()*S.SYMBOLS.length)]));
      }

      col.appendChild(strip);
      reelsEl.appendChild(col);

      reels.push({ el: strip, offset:0, speed:0, running:false, h:0 });
    }
  }

  function measure(){
    const sample = reelsEl.querySelector(".symbol");
    if(!sample) return;

    const h = sample.getBoundingClientRect().height;
    const stripStyle = getComputedStyle(reelsEl.querySelector(".reel-strip"));
    const gap = parseFloat(stripStyle.gap || "0");

    reels.forEach(r => {
      r.h = h + gap;
      r.offset = 0;
      r.el.style.transform = `translateY(0px)`;
    });
  }

  function animate(){
    reels.forEach(r => {
      if(!r.running) return;
      r.offset += r.speed;
      r.el.style.transform = `translateY(${r.offset}px)`;

      if(r.offset >= r.h){
        r.offset -= r.h;
        const last = r.el.lastElementChild;
        if(last) r.el.removeChild(last);
        r.el.prepend(createSymbol(S.SYMBOLS[Math.floor(Math.random()*S.SYMBOLS.length)]));
      }
    });
    requestAnimationFrame(animate);
  }

  function startSpinVisual(){
    reelsEl.classList.add("spinning");
    reels.forEach((r, i) => {
      r.running = true;
      r.speed = 26 + i * 2;
      r.el.style.transition = "none";
    });
  }

  function stopSpinVisual(){
    reelsEl.classList.remove("spinning");
    reels.forEach(r => r.running = false);
  }

  function stopReel(i, resultSyms){
    const r = reels[i];
    r.running = false;

    r.el.innerHTML = "";

    // buffer
    for(let k=0; k<3; k++) r.el.appendChild(createSymbol(S.SYMBOLS[Math.floor(Math.random()*S.SYMBOLS.length)]));

    // result (top/mid/bot)
    r.el.appendChild(createSymbol(resultSyms[0]));
    r.el.appendChild(createSymbol(resultSyms[1]));
    r.el.appendChild(createSymbol(resultSyms[2]));

    // buffer
    for(let k=0; k<3; k++) r.el.appendChild(createSymbol(S.SYMBOLS[Math.floor(Math.random()*S.SYMBOLS.length)]));

    // snap to show result rows (index 3,4,5)
    const target = -(r.h * 3);
    r.el.style.transition = "none";
    r.el.style.transform = `translateY(${target + 18}px)`;

    requestAnimationFrame(() => {
      r.el.style.transition = "transform 0.2s ease-out";
      r.el.style.transform = `translateY(${target}px)`;
    });
  }

  // init
  buildReels();
  setTimeout(measure, 120);
  window.addEventListener("resize", () => setTimeout(measure, 200));
  requestAnimationFrame(animate);

  S.game = { reelsEl, buildReels, measure, startSpinVisual, stopSpinVisual, stopReel, reels };
})(window.SLOT);
