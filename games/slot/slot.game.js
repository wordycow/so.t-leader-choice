// === 설정(Config) ===
const CONFIG = {
    // Apps Script 배포 URL (건드리지 마세요 / 잘 작동중입니다)
    API_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",
    
    // [핵심 수정] 헷갈리지 않게 '절대 주소'를 입력했습니다. 이제 무조건 보입니다.
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
        // 사운드 경로도 절대 주소로 변경
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
    dummySymbolCount: 60 
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
    // 1) 로컬 스토리지에서 아이디 확인 (메인 페이지에서 로그인 후 넘어온 경우)
    // 일반적으로 사용하는 키 이름들을 순차적으로 검사하거나 'user_id'로 통일
    // 여기서는 'loginId' 또는 'user_id'를 찾는다고 가정.
    // ※ 중요: 메인 페이지에서 저장할 때 사용한 키값과 일치해야 합니다.
    const localId = localStorage.getItem('user_id') || localStorage.getItem('loginId') || localStorage.getItem('id');
    
    // 2) URL 파라미터 백업 확인
    const urlParams = new URLSearchParams(window.location.search);
    const paramId = urlParams.get('id');

    // 우선순위: 로컬스토리지 > URL파라미터
    state.id = localId || paramId;

    if (!state.id) {
        // 아이디가 없으면 GUEST 처리 (또는 로그인 페이지로 리다이렉트 가능)
        // alert("로그인 정보가 없습니다. 메인 화면으로 이동합니다.");
        // location.href = "../index.html"; // 필요시 주석 해제
        els.userId.innerText = "GUEST";
        els.spinBtn.disabled = true;
        els.msg.innerText = "PLEASE LOGIN";
    } else {
        els.userId.innerText = state.id;
        
        // [중요] 로그인된 상태라면 바로 서버와 통신해서 지갑 잔액 갱신
        await syncUserData();
    }

    // 오디오 로드 (경로 에러 방지용 try-catch 추가)
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

    // 이벤트 리스너
    els.overlay.addEventListener('click', unlockAudio);
    els.spinBtn.addEventListener('click', onSpinClick);
    els.plus.addEventListener('click', () => changeBet(10));
    els.minus.addEventListener('click', () => changeBet(-10));
}

// === 유저 데이터 동기화 (지갑/잭팟) ===
async function syncUserData() {
    if (!state.id) return;
    
    els.msg.innerText = "SYNCING...";
    try {
        // Apps Script의 getSlotState 호출
        const res = await jsonpRequest('getSlotState', { id: state.id });
        
        if (res.ok) {
            state.wallet = Number(res.user.balance);
            state.jackpotPool = Number(res.jackpotTotal);
            
            updateUI();
            updateTicker(state.jackpotPool);
            els.msg.innerText = "READY";
            els.spinBtn.disabled = false;
            
            // (선택) 최신 잔액 로컬스토리지 업데이트
            // localStorage.setItem('user_balance', state.wallet);
        } else {
            els.msg.innerText = "USER NOT FOUND"; // 구글 시트에 없는 아이디일 경우
            els.spinBtn.disabled = true;
        }
    } catch (e) {
        console.error(e);
        els.msg.innerText = "NETWORK ERROR";
    }
}

// === 2. JSONP 통신 ===
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
        
        // 에러 핸들링
        script.onerror = () => {
            cleanup();
            reject(new Error("Script Load Error"));
        };

        document.body.appendChild(script);
    });
}

// === 3. 게임 로직 ===
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
            // [중요] 이미지 경로 404 방지 확인
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
    const idx = Math.floor(Math.random() * CONFIG.imgObj.symbols.length);
    return CONFIG.imgObj.symbols[idx];
}

async function onSpinClick() {
    if (state.isSpinning) return;
    
    // 잔액 체크 (프론트단 1차 방어)
    if (state.wallet < state.bet) {
        // 혹시 잔액 동기화가 안되었을 수 있으니 한 번 더 체크 시도
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

    // 릴 돌리기 (시각적 효과)
    const strips = document.querySelectorAll('.reel-strip');
    const symbolDom = document.querySelector('.symbol');
    if(symbolDom) CONFIG.symbolHeight = symbolDom.offsetHeight;

    strips.forEach((strip) => {
        strip.style.transition = `transform 4s linear`; 
        strip.style.transform = `translateY(-${CONFIG.symbolHeight * (CONFIG.dummySymbolCount - 5)}px)`; 
        strip.style.filter = 'blur(3px)';
    });

    try {
        // 서버에 스핀 결과 요청
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
        createReels(); // 리셋
        syncUserData(); // 잔액 재동기화
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
        
        symbols[len - 4].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbolName()}')`; 
        symbols[len - 3].style.backgroundImage = `url('${CONFIG.imgObj.path}${topSym}')`;
        symbols[len - 2].style.backgroundImage = `url('${CONFIG.imgObj.path}${midSym}')`; 
        symbols[len - 1].style.backgroundImage = `url('${CONFIG.imgObj.path}${botSym}')`;

        const delay = colIdx * 300; 
        
        setTimeout(() => {
            strip.style.transition = 'transform 0.5s cubic-bezier(0.2, 1, 0.3, 1)'; 
            strip.style.filter = 'none';
            const targetY = -((len - 3) * CONFIG.symbolHeight);
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
    
    // 서버에서 받은 최종 잔액으로 업데이트 (중요: 정확성 보장)
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
