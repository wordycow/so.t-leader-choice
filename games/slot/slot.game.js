// === 설정(Config) ===
const CONFIG = {
    // Apps Script 배포 URL (건드리지 마세요)
    API_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",
    
    // [중요] 404 에러 방지를 위한 절대 경로 유지
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
    // [수정] 빈 공간 방지를 위해 심볼 개수를 넉넉하게 늘림 (60 -> 120)
    dummySymbolCount: 120 
};

// === 상태(State) ===
let state = {
    id: null,        
    wallet: 0,       
    bet: 10,         
    isSpinning: false,
    audioEnabled: false,
    bgIntervalId: null,
    jackpotPool: 0   
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

// === 1. 초기화 (Init) ===
async function init() {
    const localId = localStorage.getItem('user_id') || localStorage.getItem('loginId') || localStorage.getItem('id');
    const urlParams = new URLSearchParams(window.location.search);
    const paramId = urlParams.get('id');

    state.id = localId || paramId;

    if (!state.id) {
        els.userId.innerText = "GUEST";
        els.spinBtn.disabled = true;
        els.msg.innerText = "PLEASE LOGIN";
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
            } catch(e) {
                console.warn("Audio load fail:", key);
            }
        }
    });

    createReels(); 

    els.overlay.addEventListener('click', unlockAudio);
    els.spinBtn.addEventListener('click', onSpinClick);
    els.plus.addEventListener('click', () => changeBet(10));
    els.minus.addEventListener('click', () => changeBet(-10));
}

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
        console.error(e);
        els.msg.innerText = "NETWORK ERROR";
    }
}

function jsonpRequest(action, params = {}) {
    return new Promise((resolve, reject) => {
        const callbackName = 'cb_' + Math.round(100000 * Math.random());
        const script = document.createElement('script');
        
        const timeout = setTimeout(() => {
            cleanup();
            reject(new Error("Timeout"));
        }, 15000); 

        window[callbackName] = function(data) {
            cleanup();
            resolve(data);
        };

        function cleanup() {
            clearTimeout(timeout);
            if(document.body.contains(script)) document.body.removeChild(script);
            delete window[callbackName];
        }

        params.action = action;
        params.callback = callbackName;
        const qs = new URLSearchParams(params).toString();
        
        script.src = `${CONFIG.API_URL}?${qs}`;
        
        script.onerror = () => {
            cleanup();
            reject(new Error("Script Load Error"));
        };

        document.body.appendChild(script);
    });
}

// === 3. 게임 로직 (수정됨) ===
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
    
    // 심볼 높이 측정
    setTimeout(() => {
        const firstSymbol = document.querySelector('.symbol');
        if(firstSymbol) CONFIG.symbolHeight = firstSymbol.offsetHeight;
    }, 100);
}

function getRandomSymbolName() {
    const idx = Math.floor(Math.random() * CONFIG.imgObj.symbols.length);
    return CONFIG.imgObj.symbols[idx];
}

async function onSpinClick() {
    if (state.isSpinning) return;
    
    if (state.wallet < state.bet) {
        await syncUserData(); 
        if(state.wallet < state.bet) {
            alert("잔액이 부족합니다 (UT 부족)");
            return;
        }
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

    const strips = document.querySelectorAll('.reel-strip');
    const symbolDom = document.querySelector('.symbol');
    if(symbolDom) CONFIG.symbolHeight = symbolDom.offsetHeight;

    // [연출 수정] 강렬한 블러 + 빠른 이동
    strips.forEach((strip) => {
        // 이미지를 맨 끝부분보다 훨씬 더 아래로 이동시켜서 속도감을 냄
        strip.style.transition = `transform 3s linear`; 
        // 끝보다 10칸 정도 덜 가서 계속 도는 느낌 유지
        const targetY = -(CONFIG.symbolHeight * (CONFIG.dummySymbolCount - 20));
        strip.style.transform = `translateY(${targetY}px)`; 
        // [중요] 세로 모션 블러 효과 (8px)
        strip.style.filter = 'blur(8px)';
    });

    try {
        const res = await jsonpRequest('slotSpin', {
            id: state.id,
            bet: state.bet
        });

        if (!res.ok) {
            throw new Error(res.error || "Spin Failed");
        }

        stopReelsWithResult(res);

    } catch (err) {
        console.error(err);
        stopBgEffect();
        audios.spin.pause();
        state.isSpinning = false;
        els.spinBtn.disabled = false;
        els.msg.innerText = "ERROR: " + err.message;
        
        // 에러 시 릴 리셋
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

    strips.forEach((strip, colIdx) => {
        const topSym = serverKeys[colIdx] + ".png";       
        const midSym = serverKeys[colIdx + 5] + ".png";   
        const botSym = serverKeys[colIdx + 10] + ".png";  

        const symbols = strip.querySelectorAll('.symbol');
        const len = symbols.length;
        
        // [수정] 멈추는 위치 심볼 교체
        // 맨 끝에서부터 역순으로 채움. 
        // len-5 위치부터 채워서 여유 공간(buffer)을 확보 -> 빈 공간 방지
        symbols[len - 6].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbolName()}')`; 
        symbols[len - 5].style.backgroundImage = `url('${CONFIG.imgObj.path}${topSym}')`;
        symbols[len - 4].style.backgroundImage = `url('${CONFIG.imgObj.path}${midSym}')`; // 중앙 (결과)
        symbols[len - 3].style.backgroundImage = `url('${CONFIG.imgObj.path}${botSym}')`;
        symbols[len - 2].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbolName()}')`; // 아래 여유분
        symbols[len - 1].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbolName()}')`; // 맨 끝 여유분

        const delay = colIdx * 300; 
        
        setTimeout(() => {
            // [연출 수정] 멈출 때 블러 제거 및 탄성 효과
            strip.style.transition = 'transform 0.5s cubic-bezier(0.2, 1, 0.3, 1)'; 
            strip.style.filter = 'none'; // 블러 해제
            
            // 정확한 위치 계산: (len - 5)번째 심볼이 맨 위에 오도록
            const targetY = -((len - 5) * CONFIG.symbolHeight);
            strip.style.transform = `translateY(${targetY}px)`;

            if(state.audioEnabled) {
                const stopSound = audios.stop.cloneNode();
                stopSound.volume = 0.6;
                stopSound.play();
            }

        }, 500 + delay); 
    });

    const totalTime = 500 + (CONFIG.reels * 300) + 600;
    
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
    
    // [추가] 다음 스핀을 위해 릴 위치 조용히 리셋? 
    // 여기서는 하지 않음 (연속성을 위해). 
    // 다음 스핀 누르면 createReels()를 호출하는 방식이 아니므로,
    // DOM이 계속 길어지지 않게 하려면 리셋이 필요할 수 있음.
    // 하지만 현재 로직은 매번 createReels() 하지 않고 기존 strip을 재활용하므로
    // 다음 스핀 시 '순간이동' 리셋이 필요함.
    
    setTimeout(() => {
        // 다음 판을 위해 릴을 몰래 초기 위치로 되돌림 (사용자 눈속임)
        const strips = document.querySelectorAll('.reel-strip');
        strips.forEach(strip => {
            strip.style.transition = 'none';
            strip.style.transform = 'translateY(0px)';
            // 현재 보이는 결과 심볼을 맨 위(0,1,2)로 복사해서 자연스럽게 이어지게 하면 좋지만
            // 코드가 복잡해지므로, 그냥 0으로 리셋하고 심볼들을 랜덤으로 다시 채워둠
            // (사용자는 다음 스핀 누르기 전까지 눈치 못 챔)
        });
        // 릴 내용물 리필 (다음 스핀 준비)
        createReels(); 
    }, 2000); // 결과 확인 후 2초 뒤 리셋
}

// === 4. 유틸리티 ===
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
    if(els.ticker) {
        els.ticker.innerText = `★ JACKPOT POOL: ${jackpotAmount.toLocaleString()} UT ★ [NOTICE] 5연속 MEGA WIN 25배 지급! ★ THE UNIQUE SLOT OPEN ★`;
    }
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
