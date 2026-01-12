// === 설정(Config) ===
const CONFIG = {
    API_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",
    imgObj: {
        path: 'https://wordycow.github.io/so.t-leader-choice/games/img/slot/', 
        bg: ['bg1.png', 'bg2.png', 'bg3.png', 'bg4.png', 'bg5.png'],
        symbols: [
            'star1.png', 'star2.png', 'star3.png',
            'pro1.png', 'pro2.png', 'pro3.png', 'pro4.png', 'pro5.png',
            'pro6.png', 'pro7.png', 'pro8.png', 'pro9.png', 'pro10.png'
        ]
    },
    soundObj: {
        path: 'https://wordycow.github.io/so.t-leader-choice/games/sounds/',
        spin: 'spinning-sound.MP3',
        stop: 'stop-stop-stop-sound.MP3',
        win: 'win-sound.MP3',
        lose: 'lose-sound.MP3',
        jackpot: 'jackpot-sound.MP3',
        btn: 'start-button-sound.MP3'
    },
    reels: 5, rows: 3, symbolHeight: 0, bgIntervalTime: 200, dummySymbolCount: 150 
};

// === 상태(State) ===
let state = {
    id: null, wallet: 0, bet: 10, isSpinning: false, audioEnabled: false, bgIntervalId: null, jackpotPool: 0   
};

// === DOM 요소 ===
const els = {
    bg: document.getElementById('game-bg'),
    overlay: document.getElementById('start-overlay'),
    reelsContainer: document.getElementById('reels-container'),
    spinBtn: document.getElementById('btn-spin'),
    walletSpan: document.getElementById('wallet-balance'),
    betSpan: document.getElementById('current-bet'),
    // [변경] 새 당첨 정보 패널 요소
    winPanel: document.querySelector('.win-info-panel'),
    winLabel: document.getElementById('win-label'),
    winAmount: document.getElementById('win-amount'),
    plus: document.getElementById('btn-bet-plus'),
    minus: document.getElementById('btn-bet-minus'),
    userId: document.getElementById('user-id'),
    ticker: document.querySelector('.ticker-item'),
    gameContainer: document.getElementById('game-container')
};

const audios = {};

// === 초기화 ===
async function init() {
    console.log("SLOT GAME LOADED: VERSION ULTRA 3D");

    const localId = localStorage.getItem('user_id') || localStorage.getItem('loginId') || localStorage.getItem('id');
    state.id = localId || new URLSearchParams(window.location.search).get('id');

    if (!state.id) {
        els.userId.innerText = "GUEST";
        els.spinBtn.disabled = true;
        setWinDisplay("PLEASE LOGIN", "---");
    } else {
        els.userId.innerText = state.id;
        await syncUserData();
    }

    Object.keys(CONFIG.soundObj).forEach(key => {
        if (key !== 'path') {
            try {
                const audio = new Audio(CONFIG.soundObj.path + CONFIG.soundObj[key]);
                if(key === 'spin') audio.loop = true;
                audios[key] = audio;
            } catch(e) { console.warn("Audio error", key); }
        }
    });

    createReels(); 

    els.overlay.addEventListener('click', unlockAudio);
    els.spinBtn.addEventListener('click', onSpinClick);
    els.plus.addEventListener('click', () => changeBet(10));
    els.minus.addEventListener('click', () => changeBet(-10));
}

// === [추가] 숫자 애니메이션 함수 (지갑용) ===
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // 정수로 변환하여 표시 (toLocaleString으로 콤마 추가)
        obj.innerText = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerText = end.toLocaleString(); // 최종값 보정
        }
    };
    window.requestAnimationFrame(step);
}

// === 유저 동기화 ===
async function syncUserData(animate = false) {
    if (!state.id) return;
    if(!animate) setWinDisplay("SYNCING...", "...");
    try {
        const res = await jsonpRequest('getSlotState', { id: state.id });
        if (res.ok) {
            const newWallet = Number(res.user.balance);
            state.jackpotPool = Number(res.jackpotTotal);
            
            // [변경] 지갑 숫자 애니메이션 적용
            if (animate && state.wallet !== newWallet) {
                animateValue(els.walletSpan, state.wallet, newWallet, 1000);
            } else {
                els.walletSpan.innerText = newWallet.toLocaleString();
            }
            state.wallet = newWallet; // 상태 업데이트

            updateUI();
            updateTicker(state.jackpotPool);
            if(!animate) setWinDisplay("READY", "GOOD LUCK!");
            els.spinBtn.disabled = false;
        } else {
            setWinDisplay("ERROR", "USER NOT FOUND");
            els.spinBtn.disabled = true;
        }
    } catch (e) {
        setWinDisplay("ERROR", "NETWORK FAIL");
    }
}

function jsonpRequest(action, params = {}) {
    return new Promise((resolve, reject) => {
        const callbackName = 'cb_' + Math.round(100000 * Math.random());
        const script = document.createElement('script');
        const timeout = setTimeout(() => { cleanup(); reject(new Error("Timeout")); }, 15000); 
        window[callbackName] = function(data) { cleanup(); resolve(data); };
        function cleanup() {
            clearTimeout(timeout);
            if(document.body.contains(script)) document.body.removeChild(script);
            delete window[callbackName];
        }
        params.action = action; params.callback = callbackName;
        script.src = `${CONFIG.API_URL}?${new URLSearchParams(params).toString()}`;
        script.onerror = () => { cleanup(); reject(new Error("Script Error")); };
        document.body.appendChild(script);
    });
}

// === 게임 로직 ===
function createReels() {
    els.reelsContainer.innerHTML = '';
    for (let i = 0; i < CONFIG.reels; i++) {
        const reelDiv = document.createElement('div');
        reelDiv.className = 'reel';
        const stripDiv = document.createElement('div');
        stripDiv.className = 'reel-strip';
        
        let html = '';
        for(let j=0; j < CONFIG.dummySymbolCount; j++) {
            const sym = getRandomSymbolName();
            html += `<div class="symbol" style="background-image: url('${CONFIG.imgObj.path}${sym}')"></div>`;
        }
        stripDiv.innerHTML = html;
        reelDiv.appendChild(stripDiv);
        els.reelsContainer.appendChild(reelDiv);
    }
    setTimeout(() => {
        const firstSymbol = document.querySelector('.symbol');
        if(firstSymbol) CONFIG.symbolHeight = firstSymbol.offsetHeight;
    }, 100);
}

function getRandomSymbolName() {
    return CONFIG.imgObj.symbols[Math.floor(Math.random() * CONFIG.imgObj.symbols.length)];
}

async function onSpinClick() {
    if (state.isSpinning) return;
    if (state.wallet < state.bet) {
        await syncUserData(); 
        if(state.wallet < state.bet) { alert("잔액 부족 (UT)"); return; }
    }

    state.isSpinning = true;
    els.spinBtn.disabled = true;
    setWinDisplay("SPINNING...", `BET: ${state.bet}`);
    els.winPanel.classList.remove('jackpot-hit'); // 잭팟 효과 초기화
    
    // [변경] 베팅 차감 애니메이션 (현재 잔액 -> 베팅 후 잔액)
    animateValue(els.walletSpan, state.wallet, state.wallet - state.bet, 500);
    state.wallet -= state.bet; // 즉시 차감 반영

    if(state.audioEnabled) {
        audios.btn.play();
        audios.spin.currentTime = 0;
        audios.spin.play();
    }
    startBgEffect(); 

    const strips = document.querySelectorAll('.reel-strip');
    const symbolDom = document.querySelector('.symbol');
    if(symbolDom) CONFIG.symbolHeight = symbolDom.offsetHeight;

    strips.forEach((strip) => {
        strip.style.transition = `transform 2.5s linear`; 
        const targetY = -(CONFIG.symbolHeight * (CONFIG.dummySymbolCount - 20));
        strip.style.transform = `translateY(${targetY}px)`; 
        // [변경] 블러를 8px에서 4px로 줄여서 덜 흐릿하게
        strip.style.filter = 'blur(4px)'; 
    });

    try {
        const res = await jsonpRequest('slotSpin', { id: state.id, bet: state.bet });
        if (!res.ok) throw new Error(res.error || "Spin Failed");
        stopReelsWithResult(res);
    } catch (err) {
        console.error(err);
        stopBgEffect();
        audios.spin.pause();
        state.isSpinning = false;
        els.spinBtn.disabled = false;
        setWinDisplay("ERROR", "TRY AGAIN");
        strips.forEach(strip => {
             strip.style.transition = 'none';
             strip.style.transform = 'translateY(0)';
             strip.style.filter = 'none';
        });
        syncUserData(true); // 에러 시 잔액 복구 애니메이션
    }
}

function stopReelsWithResult(data) {
    const serverKeys = data.spin.keys;
    const strips = document.querySelectorAll('.reel-strip');
    const STOP_INDEX = CONFIG.dummySymbolCount - 30;

    strips.forEach((strip, colIdx) => {
        const topSym = serverKeys[colIdx] + ".png";       
        const midSym = serverKeys[colIdx + 5] + ".png";   
        const botSym = serverKeys[colIdx + 10] + ".png";  

        const symbols = strip.querySelectorAll('.symbol');
        if(symbols[STOP_INDEX]) symbols[STOP_INDEX].style.backgroundImage = `url('${CONFIG.imgObj.path}${topSym}')`;
        if(symbols[STOP_INDEX + 1]) symbols[STOP_INDEX + 1].style.backgroundImage = `url('${CONFIG.imgObj.path}${midSym}')`;
        if(symbols[STOP_INDEX + 2]) symbols[STOP_INDEX + 2].style.backgroundImage = `url('${CONFIG.imgObj.path}${botSym}')`;

        const delay = colIdx * 300; 
        
        setTimeout(() => {
            strip.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)'; 
            strip.style.filter = 'none'; 
            const finalY = -(STOP_INDEX * CONFIG.symbolHeight);
            strip.style.transform = `translateY(${finalY}px)`;

            if(state.audioEnabled) {
                const stopSound = audios.stop.cloneNode();
                stopSound.volume = 0.6;
                stopSound.play();
            }

            // 마지막 릴 멈출 때 타격감
            if (colIdx === CONFIG.reels - 1) {
                els.gameContainer.classList.add('shake-hard');
                setTimeout(() => els.gameContainer.classList.remove('shake-hard'), 500);
            }
        }, 500 + delay); 
    });

    const totalTime = 500 + (CONFIG.reels * 300) + 700;
    setTimeout(() => {
        handleSpinEnd(data);
    }, totalTime);
}

function handleSpinEnd(data) {
    state.isSpinning = false;
    stopBgEffect();
    els.spinBtn.disabled = false;
    audios.spin.pause();

    const spin = data.spin;
    const oldWallet = state.wallet;
    const newWallet = data.user.balance;
    state.jackpotPool = data.jackpotTotal;

    // [변경] 지갑 잔액 증가 애니메이션 (당첨금 수령)
    if (newWallet > oldWallet) {
        animateValue(els.walletSpan, oldWallet, newWallet, 1500); // 1.5초 동안 증가
    } else {
        els.walletSpan.innerText = newWallet.toLocaleString();
    }
    state.wallet = newWallet;

    let sound = audios.lose;
    let labelText = "NO WIN";
    let amountText = "TRY AGAIN";

    if (spin.kind === "lose") {
        labelText = "RESULT";
        amountText = "NO WIN";
    } else {
        const payout = spin.payout;
        const netWin = spin.netDelta + state.bet; // 순수익 + 베팅원금

        if (spin.kind === "even") {
            labelText = "EVEN! (+1 BONUS)";
            amountText = `+${payout.toLocaleString()} UT`;
            sound = audios.win;
        } else if (spin.kind === "jackpot") {
            // [요청 반영] 잭팟 시 "얼마 터졌다" 명확히 표시
            labelText = "★ JACKPOT HIT! ★";
            amountText = `+${payout.toLocaleString()} UT`;
            sound = audios.jackpot;
            els.winPanel.classList.add('jackpot-hit'); // 잭팟 전용 스타일 추가
        } else {
            // win3, win4, mega
            const multiplier = spin.kind === 'win3' ? '3X' : spin.kind === 'win4' ? '10X' : '25X';
            labelText = `${multiplier} BIG WIN!`;
            amountText = `+${payout.toLocaleString()} UT`;
            sound = audios.win;
        }
    }

    setWinDisplay(labelText, amountText); // 하단 패널 업데이트

    if (spin.payout > 0 && state.audioEnabled) {
        sound.currentTime = 0;
        sound.play();
    }

    updateUI();
    updateTicker(data.jackpotTotal);

    setTimeout(() => {
        const strips = document.querySelectorAll('.reel-strip');
        strips.forEach(strip => {
            strip.style.transition = 'none';
            strip.style.transform = 'translateY(0px)';
        });
        createReels(); 
    }, 2500); 
}

// === 유틸리티 ===
// [추가] 하단 당첨 정보 패널 업데이트 함수
function setWinDisplay(label, amount) {
    els.winLabel.innerText = label;
    els.winAmount.innerText = amount;
}

function startBgEffect() {
    let idx = 0;
    state.bgIntervalId = setInterval(() => {
        idx = (idx + 1) % CONFIG.imgObj.bg.length;
        els.bg.style.backgroundImage = `url('${CONFIG.imgObj.path}${CONFIG.imgObj.bg[idx]}')`;
    }, CONFIG.bgIntervalTime);
}

function stopBgEffect() {
    clearInterval(state.bgIntervalId);
    els.bg.style.backgroundImage = `url('${CONFIG.imgObj.path}bg1.png')`;
}

function unlockAudio() {
    els.overlay.style.display = 'none';
    state.audioEnabled = true;
    audios.btn.play().catch(()=>{}); 
}

function updateUI() {
    // els.walletSpan.innerText는 animateValue가 처리하므로 여기선 제외
    els.betSpan.innerText = state.bet.toLocaleString();
}

function updateTicker(jackpotAmount) {
    if(els.ticker) els.ticker.innerText = `★ JACKPOT POOL: ${jackpotAmount.toLocaleString()} UT ★ [NOTICE] 5연속 MEGA WIN 25배 지급! ★ THE UNIQUE SLOT OPEN ★`;
}

function changeBet(delta) {
    if(state.isSpinning) return;
    const newBet = state.bet + delta;
    if(newBet >= 10 && newBet <= 1000) {
        state.bet = newBet;
        updateUI();
    }
}

window.onload = init;
