// === 설정(Config) ===
const CONFIG = {
    // Apps Script 배포 URL (exec로 끝나는 주소)
    API_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",
    
    imgObj: {
        path: '../img/slot/', // 상대 경로 유지
        bg: ['bg1.png', 'bg2.png', 'bg3.png', 'bg4.png', 'bg5.png'],
        // 서버에서 내려오는 키값(star1)과 파일명(star1.png) 매핑
        symbols: [
            'star1.png', 'star2.png', 'star3.png',
            'pro1.png', 'pro2.png', 'pro3.png', 'pro4.png', 'pro5.png',
            'pro6.png', 'pro7.png', 'pro8.png', 'pro9.png', 'pro10.png'
        ]
    },
    soundObj: {
        path: '../sounds/',
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
    dummySymbolCount: 60 // 릴 애니메이션을 위한 더미 심볼 개수
};

// === 상태(State) ===
let state = {
    id: null,        // 접속 유저 ID
    wallet: 0,       // 현재 잔액
    bet: 10,         // 기본 베팅 (서버 설정 따름)
    isSpinning: false,
    audioEnabled: false,
    bgIntervalId: null,
    jackpotPool: 0   // 잭팟 누적금
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
    // URL에서 ID 파싱 (?id=wordycow)
    const urlParams = new URLSearchParams(window.location.search);
    state.id = urlParams.get('id');

    if (!state.id) {
        alert("접속 경로가 잘못되었습니다. ?id=아이디 형식으로 접속해주세요.");
        els.userId.innerText = "GUEST";
        els.spinBtn.disabled = true;
    } else {
        els.userId.innerText = state.id;
    }

    // 오디오 로드
    Object.keys(CONFIG.soundObj).forEach(key => {
        if (key !== 'path') {
            const audio = new Audio(CONFIG.soundObj.path + CONFIG.soundObj[key]);
            if(key === 'spin') audio.loop = true;
            audios[key] = audio;
        }
    });

    createReels(); // 릴 DOM 생성

    // 이벤트 리스너
    els.overlay.addEventListener('click', unlockAudio);
    els.spinBtn.addEventListener('click', onSpinClick);
    els.plus.addEventListener('click', () => changeBet(10));
    els.minus.addEventListener('click', () => changeBet(-10));

    // 서버에서 초기 데이터(잔액, 잭팟풀) 가져오기
    if (state.id) {
        els.msg.innerText = "CONNECTING...";
        try {
            const res = await jsonpRequest('getSlotState', { id: state.id });
            if (res.ok) {
                state.wallet = res.user.balance;
                state.jackpotPool = res.jackpotTotal;
                updateUI();
                updateTicker(res.jackpotTotal);
                els.msg.innerText = "READY";
            } else {
                els.msg.innerText = "ERROR: " + (res.error || "Login Failed");
            }
        } catch (e) {
            console.error(e);
            els.msg.innerText = "NETWORK ERROR";
        }
    }
}

// === 2. JSONP 통신 (Apps Script CORS 우회) ===
function jsonpRequest(action, params = {}) {
    return new Promise((resolve, reject) => {
        const callbackName = 'cb_' + Math.round(100000 * Math.random());
        const script = document.createElement('script');
        
        // 타임아웃 처리
        const timeout = setTimeout(() => {
            cleanup();
            reject(new Error("Timeout"));
        }, 15000); 

        // 콜백 함수 정의
        window[callbackName] = function(data) {
            cleanup();
            resolve(data);
        };

        function cleanup() {
            clearTimeout(timeout);
            document.body.removeChild(script);
            delete window[callbackName];
        }

        // 쿼리 스트링 조합
        params.action = action;
        params.callback = callbackName;
        const qs = new URLSearchParams(params).toString();
        
        script.src = `${CONFIG.API_URL}?${qs}`;
        document.body.appendChild(script);
    });
}

// === 3. 게임 로직 ===

// 릴 생성 (초기 상태)
function createReels() {
    els.reelsContainer.innerHTML = '';
    for (let i = 0; i < CONFIG.reels; i++) {
        const reelDiv = document.createElement('div');
        reelDiv.className = 'reel';
        
        const stripDiv = document.createElement('div');
        stripDiv.className = 'reel-strip';
        
        // 초기에는 랜덤 심볼을 채워넣음
        let html = '';
        for(let j=0; j < CONFIG.dummySymbolCount; j++) {
            const sym = getRandomSymbolName();
            html += `<div class="symbol" style="background-image: url('${CONFIG.imgObj.path}${sym}')"></div>`;
        }
        stripDiv.innerHTML = html;
        
        reelDiv.appendChild(stripDiv);
        els.reelsContainer.appendChild(reelDiv);
    }
    
    // 심볼 높이 측정 (반응형 대응)
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
        alert("잔액이 부족합니다 (UT 부족)");
        return;
    }

    // 1. 스핀 시작 처리
    state.isSpinning = true;
    els.spinBtn.disabled = true;
    els.msg.innerText = "SPINNING...";
    
    if(state.audioEnabled) {
        audios.btn.play();
        audios.spin.currentTime = 0;
        audios.spin.play();
    }
    
    startBgEffect(); // 배경 연출 시작

    // 2. 시각적 스핀 시작 (무한 스크롤 느낌)
    const strips = document.querySelectorAll('.reel-strip');
    // 심볼 높이 재계산 (창크기 변경 대응)
    const symbolDom = document.querySelector('.symbol');
    if(symbolDom) CONFIG.symbolHeight = symbolDom.offsetHeight;

    // 일단 릴을 움직이게 함 (결과 받기 전까지 계속 도는 느낌)
    strips.forEach((strip, i) => {
        strip.style.transition = `transform 4s linear`; 
        strip.style.transform = `translateY(-${CONFIG.symbolHeight * (CONFIG.dummySymbolCount - 5)}px)`; // 끝까지 내림
        strip.style.filter = 'blur(3px)';
    });

    // 3. 서버 요청 (비동기)
    try {
        const res = await jsonpRequest('slotSpin', {
            id: state.id,
            bet: state.bet
        });

        if (!res.ok) {
            throw new Error(res.error || "Spin Failed");
        }

        // 4. 결과 도착 -> 릴 멈춤 연출 실행
        stopReelsWithResult(res);

    } catch (err) {
        console.error(err);
        stopBgEffect();
        audios.spin.pause();
        state.isSpinning = false;
        els.spinBtn.disabled = false;
        els.msg.innerText = "ERROR: " + err.message;
        // 릴 원위치 (리셋)
        createReels();
    }
}

// 서버 결과(res)를 받아서 릴을 멈춤
function stopReelsWithResult(data) {
    const serverKeys = data.spin.keys; // 15개 배열 (row0..row2)
    // 서버 배열 구조: 0~4(Top), 5~9(Mid-WinLine), 10~14(Bot)
    // 릴별로 필요한 심볼:
    // Reel 0: keys[0], keys[5], keys[10]
    // Reel 1: keys[1], keys[6], keys[11]
    // ...

    const strips = document.querySelectorAll('.reel-strip');

    strips.forEach((strip, colIdx) => {
        // 이 릴이 멈춰야 할 최종 3개 심볼
        const topSym = serverKeys[colIdx] + ".png";       // keys[0..4]
        const midSym = serverKeys[colIdx + 5] + ".png";   // keys[5..9] (당첨라인)
        const botSym = serverKeys[colIdx + 10] + ".png";  // keys[10..14]

        // 릴 스트립의 맨 끝부분(보여질 부분)을 이 심볼들로 교체
        const symbols = strip.querySelectorAll('.symbol');
        const len = symbols.length;
        
        // 릴의 마지막 3개를 결과 심볼로 변경 (위에서부터 보여질 순서대로)
        symbols[len - 4].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbolName()}')`; // 여유분
        symbols[len - 3].style.backgroundImage = `url('${CONFIG.imgObj.path}${topSym}')`;
        symbols[len - 2].style.backgroundImage = `url('${CONFIG.imgObj.path}${midSym}')`; // 이게 중앙
        symbols[len - 1].style.backgroundImage = `url('${CONFIG.imgObj.path}${botSym}')`;

        // 멈추는 타이밍 (릴별 시차)
        const delay = colIdx * 300; 
        
        setTimeout(() => {
            strip.style.transition = 'transform 0.5s cubic-bezier(0.2, 1, 0.3, 1)'; // 쫀득한 멈춤
            strip.style.filter = 'none';
            
            // 정확히 len-3 위치가 맨 위에 오도록 계산
            // len-3 인덱스 요소의 top 위치로 이동해야 함
            // CSS translateY는 전체 이동거리.
            // (len - 3) * height 만큼 위로 올리면 됨.
            const targetY = -((len - 3) * CONFIG.symbolHeight);
            
            strip.style.transform = `translateY(${targetY}px)`;

            // 쿵! 소리
            if(state.audioEnabled) {
                const stopSound = audios.stop.cloneNode();
                stopSound.volume = 0.6;
                stopSound.play();
            }

        }, 500 + delay); // 서버 응답 후 0.5초 뒤부터 순차 정지
    });

    // 모든 릴이 멈춘 후 결과 처리
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

    // 메시지 및 사운드
    let msgText = "";
    let sound = audios.lose;

    if (spin.kind === "lose") {
        msgText = "TRY AGAIN";
    } else {
        const payout = spin.payout;
        if (spin.kind === "even") {
            msgText = `EVEN! (+${spin.netDelta + state.bet})`; // EVEN(+1) 같은 텍스트
            sound = audios.win;
        } else if (spin.kind === "jackpot") {
            msgText = `★ JACKPOT ★ (+${payout.toLocaleString()})`;
            sound = audios.jackpot;
        } else {
            // win3, win4, mega
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
    if(newBet >= 10 && newBet <= 1000) { // 서버 설정(SLOT_BET_MIN/MAX)에 맞춰 10단위
        state.bet = newBet;
        updateUI();
    }
}

// 시작
window.onload = init;
