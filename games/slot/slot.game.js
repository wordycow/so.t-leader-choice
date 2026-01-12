// === 설정(Config) ===
const CONFIG = {
    // Apps Script 배포 URL (유지)
    API_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",
    
    // [절대 경로] 404 방지
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
    reels: 5,
    rows: 3,
    symbolHeight: 0, 
    bgIntervalTime: 200,
    // [수정] 심볼을 150개로 대폭 늘려 위아래 여유 확보
    dummySymbolCount: 150 
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
    msg: document.getElementById('message-area'),
    plus: document.getElementById('btn-bet-plus'),
    minus: document.getElementById('btn-bet-minus'),
    userId: document.getElementById('user-id'),
    ticker: document.querySelector('.ticker-item')
};

const audios = {};

// === 초기화 ===
async function init() {
    console.log("SLOT GAME LOADED: VERSION FINAL"); // 콘솔에서 로드 확인용

    const localId = localStorage.getItem('user_id') || localStorage.getItem('loginId') || localStorage.getItem('id');
    const urlParams = new URLSearchParams(window.location.search);
    state.id = localId || urlParams.get('id');

    if (!state.id) {
        els.userId.innerText = "GUEST";
        els.spinBtn.disabled = true;
        els.msg.innerText = "PLEASE LOGIN";
    } else {
        els.userId.innerText = state.id;
        await syncUserData();
    }

    // 오디오 로드
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

// === 유저 동기화 ===
async function syncUserData() {
    if (!state.id) return;
    els.msg.innerText = "SYNCING...";
    try {
        const res = await jsonpRequest('getSlotState', { id: state.id });
        if (res.ok) {
            state.wallet = Number(res.user.balance);
            state.jackpotPool = Number(res.jackpotTotal);
            updateUI();
            updateTicker(state.jackpotPool);
            els.msg.innerText = "READY";
            els.spinBtn.disabled = false;
        } else {
            els.msg.innerText = "USER NOT FOUND";
            els.spinBtn.disabled = true;
        }
    } catch (e) {
        els.msg.innerText = "NETWORK ERROR";
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
        // 150개의 심볼 생성
        for(let j=0; j < CONFIG.dummySymbolCount; j++) {
            const sym = getRandomSymbolName();
            html += `<div class="symbol" style="background-image: url('${CONFIG.imgObj.path}${sym}')"></div>`;
        }
        stripDiv.innerHTML = html;
        reelDiv.appendChild(stripDiv);
        els.reelsContainer.appendChild(reelDiv);
    }
    
    // 높이 측정
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
    els.msg.innerText = "SPINNING...";
    
    if(state.audioEnabled) {
        audios.btn.play();
        audios.spin.currentTime = 0;
        audios.spin.play();
    }
    startBgEffect(); 

    // 1. 스핀 애니메이션 (엄청 빠르게, 멀리 이동)
    const strips = document.querySelectorAll('.reel-strip');
    const symbolDom = document.querySelector('.symbol');
    if(symbolDom) CONFIG.symbolHeight = symbolDom.offsetHeight;

    strips.forEach((strip) => {
        // 현재 위치에서 -100칸 정도 더 내려감 (매우 빠름)
        strip.style.transition = `transform 2.5s linear`; 
        // 130번째 심볼 근처까지 이동 (끝이 아님!)
        const targetY = -(CONFIG.symbolHeight * (CONFIG.dummySymbolCount - 20));
        strip.style.transform = `translateY(${targetY}px)`; 
        strip.style.filter = 'blur(8px)'; // 강한 블러
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
        els.msg.innerText = "ERROR";
        // 에러 시 릴 초기화
        strips.forEach(strip => {
             strip.style.transition = 'none';
             strip.style.transform = 'translateY(0)';
             strip.style.filter = 'none';
        });
        syncUserData();
    }
}

function stopReelsWithResult(data) {
    const serverKeys = data.spin.keys;
    const strips = document.querySelectorAll('.reel-strip');

    // [핵심] 멈출 위치: 전체 150개 중 120번째(뒤쪽)에서 멈춤.
    // 이렇게 하면 멈춘 뒤에도 아래에 30개 정도의 심볼이 더 남아있어서, 
    // 반동(Bounce)이 생겨도 절대 빈 공간이 보이지 않음.
    const STOP_INDEX = CONFIG.dummySymbolCount - 30; // 120번째

    strips.forEach((strip, colIdx) => {
        const topSym = serverKeys[colIdx] + ".png";       
        const midSym = serverKeys[colIdx + 5] + ".png";   
        const botSym = serverKeys[colIdx + 10] + ".png";  

        const symbols = strip.querySelectorAll('.symbol');
        
        // 120번째 위치에 결과 심볼 심기
        // STOP_INDEX = 화면 맨 위
        // STOP_INDEX + 1 = 화면 중간 (결과)
        // STOP_INDEX + 2 = 화면 아래
        if(symbols[STOP_INDEX]) symbols[STOP_INDEX].style.backgroundImage = `url('${CONFIG.imgObj.path}${topSym}')`;
        if(symbols[STOP_INDEX + 1]) symbols[STOP_INDEX + 1].style.backgroundImage = `url('${CONFIG.imgObj.path}${midSym}')`; // 결과!
        if(symbols[STOP_INDEX + 2]) symbols[STOP_INDEX + 2].style.backgroundImage = `url('${CONFIG.imgObj.path}${botSym}')`;

        const delay = colIdx * 300; // 릴 별 시간차
        
        setTimeout(() => {
            strip.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)'; // 부드러운 정지
            strip.style.filter = 'none'; 
            
            // 정확히 STOP_INDEX가 맨 위에 오도록 이동
            const finalY = -(STOP_INDEX * CONFIG.symbolHeight);
            strip.style.transform = `translateY(${finalY}px)`;

            if(state.audioEnabled) {
                const stopSound = audios.stop.cloneNode();
                stopSound.volume = 0.6;
                stopSound.play();
            }
        }, 500 + delay); 
    });

    // 종료 처리
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
    state.wallet = data.user.balance; 
    state.jackpotPool = data.jackpotTotal;

    let msgText = "";
    let sound = audios.lose;

    if (spin.kind === "lose") {
        msgText = "TRY AGAIN";
    } else {
        const payout = spin.payout;
        if (spin.kind === "even") {
            msgText = `EVEN! (+${spin.netDelta + state.bet})`;
            sound = audios.win;
        } else if (spin.kind === "jackpot") {
            msgText = `★ JACKPOT ★ (+${payout.toLocaleString()})`;
            sound = audios.jackpot;
        } else {
            msgText = `WIN! (+${payout.toLocaleString()})`;
            sound = audios.win;
        }
    }

    if (spin.payout > 0 && state.audioEnabled) {
        sound.currentTime = 0;
        sound.play();
    }

    els.msg.innerText = msgText;
    if(spin.payout > 0) els.msg.style.color = "#00ffff";
    else els.msg.style.color = "gray";

    updateUI();
    updateTicker(data.jackpotTotal);

    // [무한 스핀 트릭]
    // 사용자가 다음 스핀을 누르기 전, 아주 조용히 릴을 0번 위치로 초기화하고
    // 심볼을 랜덤으로 섞어놓으면 무한히 돌릴 수 있습니다.
    setTimeout(() => {
        const strips = document.querySelectorAll('.reel-strip');
        strips.forEach(strip => {
            strip.style.transition = 'none'; // 애니메이션 없이
            strip.style.transform = 'translateY(0px)'; // 0번 위치로 순간이동
        });
        createReels(); // 심볼 내용물 랜덤 리셋
    }, 2500); 
}

// === 유틸리티 ===
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
    els.walletSpan.innerText = state.wallet.toLocaleString();
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
