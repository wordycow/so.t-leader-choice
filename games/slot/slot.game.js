// === 설정(Config) ===
const CONFIG = {
    imgObj: {
        path: '../img/slot/',
        bg: ['bg1.png', 'bg2.png', 'bg3.png', 'bg4.png', 'bg5.png'],
        // pro1~pro10, star1~star3 (총 13개 심볼)
        symbols: [
            'star1.png', 'star2.png', 'star3.png',
            'pro1.png', 'pro2.png', 'pro3.png', 'pro4.png', 'pro5.png',
            'pro6.png', 'pro7.png', 'pro8.png', 'pro9.png', 'pro10.png'
        ]
    },
    soundObj: {
        path: '../sounds/',
        // 대소문자 중요 (.MP3)
        spin: 'spinning-sound.MP3',
        stop: 'stop-stop-stop-sound.MP3',
        win: 'win-sound.MP3',
        lose: 'lose-sound.MP3',
        jackpot: 'jackpot-sound.MP3',
        btn: 'start-button-sound.MP3'
    },
    reels: 5,
    rows: 3,
    symbolHeight: 0, // 로딩 후 계산
    spinDuration: 2000, // 기본 스핀 시간 (ms) - 10초는 너무 길어서 2~3초 권장하지만 원하시면 늘려드림
    bgIntervalTime: 200 // 배경 교체 간격 (ms)
};

// === 상태(State) ===
let state = {
    wallet: 100, // 테스트용 초기 자금
    bet: 5,
    isSpinning: false,
    audioEnabled: false,
    bgIntervalId: null
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
    minus: document.getElementById('btn-bet-minus')
};

// === 오디오 객체 ===
const audios = {};

// 1. 초기화 (Init)
function init() {
    // 오디오 프리로드
    Object.keys(CONFIG.soundObj).forEach(key => {
        if (key !== 'path') {
            const audio = new Audio(CONFIG.soundObj.path + CONFIG.soundObj[key]);
            if(key === 'spin') audio.loop = true; // 스핀 소리는 반복
            audios[key] = audio;
        }
    });

    // 릴 생성
    createReels();

    // 이벤트 리스너
    els.overlay.addEventListener('click', unlockAudio);
    els.spinBtn.addEventListener('click', spin);
    els.plus.addEventListener('click', () => changeBet(1));
    els.minus.addEventListener('click', () => changeBet(-1));
    
    updateUI();
}

// 2. 오디오 언락 (브라우저 정책 대응)
function unlockAudio() {
    els.overlay.style.display = 'none';
    state.audioEnabled = true;
    // 빈 소리 재생으로 모바일 언락
    audios.btn.play().catch(()=>{}); 
}

// 3. 릴(Reel) HTML 생성
// 구조: .reel > .reel-strip > .symbol 이미지들
function createReels() {
    els.reelsContainer.innerHTML = '';
    for (let i = 0; i < CONFIG.reels; i++) {
        const reelDiv = document.createElement('div');
        reelDiv.className = 'reel';
        
        const stripDiv = document.createElement('div');
        stripDiv.className = 'reel-strip';
        // 초기 3개 심볼 + 애니메이션용 더미 심볼 추가
        // 50개의 랜덤 심볼을 미리 깔아둡니다.
        let html = '';
        for(let j=0; j<50; j++) {
            const sym = getRandomSymbol();
            html += `<div class="symbol" style="background-image: url('${CONFIG.imgObj.path}${sym}')"></div>`;
        }
        stripDiv.innerHTML = html;
        
        reelDiv.appendChild(stripDiv);
        els.reelsContainer.appendChild(reelDiv);
    }
    
    // 심볼 높이 계산 (반응형 대응)
    setTimeout(() => {
        const firstSymbol = document.querySelector('.symbol');
        if(firstSymbol) CONFIG.symbolHeight = firstSymbol.offsetHeight;
    }, 100);
}

function getRandomSymbol() {
    const idx = Math.floor(Math.random() * CONFIG.imgObj.symbols.length);
    return CONFIG.imgObj.symbols[idx];
}

// 4. 스핀 로직 (핵심)
function spin() {
    if (state.isSpinning) return;
    if (state.wallet < state.bet) {
        alert("잔액이 부족합니다!");
        return;
    }

    // 상태 업데이트
    state.isSpinning = true;
    state.wallet -= state.bet; // 베팅 차감
    els.spinBtn.disabled = true;
    els.msg.innerText = "SPINNING...";
    updateUI();

    // 오디오 시작
    if(state.audioEnabled) {
        audios.btn.play();
        audios.spin.currentTime = 0;
        audios.spin.play();
    }

    // 배경 연출 시작
    startBgEffect();

    // 결과 미리 결정 (프론트엔드 랜덤)
    // 실제로는 여기서 Apps Script (/exec)에 fetch 요청을 보내서 결과를 받아와야 함.
    // 지금은 순수 JS 랜덤으로 처리.
    const resultSymbols = []; // 5개 릴의 '가운데' 심볼
    for(let i=0; i<CONFIG.reels; i++) {
        resultSymbols.push(getRandomSymbol());
    }

    // 애니메이션 실행
    const strips = document.querySelectorAll('.reel-strip');
    const symbolHeight = document.querySelector('.symbol').offsetHeight; // 높이 재계산

    strips.forEach((strip, index) => {
        // 각 릴마다 조금씩 늦게 멈추기 (0.5초 차이)
        const delay = index * 500; 
        const duration = 2000 + delay; // 전체 도는 시간

        // CSS Transition으로 이동
        // 현재 위치에서 매우 아래쪽(-2000px 등)으로 이동시켜서 도는 느낌 줌
        // 최종적으로 보여줄 심볼을 DOM의 적절한 위치에 꽂아넣거나, 
        // 단순히 strip을 이동시킴.
        
        // 간단 구현: strip을 css transition으로 쭉 내림.
        // 그리고 transitionend 이벤트에서 위치를 초기화(loop)하는 게 정석이지만,
        // 여기서는 '내려가서 멈추는' 타격감을 위해 translate 사용.
        
        // 1. 블러 효과 추가
        strip.style.transition = `transform ${duration/1000}s cubic-bezier(0.25, 1, 0.5, 1)`;
        strip.style.filter = 'blur(2px)';
        
        // 2. 목표 위치 계산 (현재보다 훨씬 아래로)
        // 랜덤성을 위해 단순히 많이 이동. 
        // *중요*: 결과 심볼을 시각적으로 맞추려면 strip 내부 이미지를 수정해야 함.
        // 여기서는 약식으로 '멈췄을 때 보이는 이미지가 결과'라고 가정하지 않고,
        // 멈추는 시점에 DOM의 해당 위치 이미지를 결과 이미지로 바꿔치기합니다.
        
        const moveDistance = -( (Math.floor(Math.random() * 20) + 20) * symbolHeight ); 
        strip.style.transform = `translateY(${moveDistance}px)`;

        // 3. 멈춤 로직
        setTimeout(() => {
            // 소리 (탁!)
            if(state.audioEnabled) {
                const stopSound = audios.stop.cloneNode();
                stopSound.play();
            }
            
            strip.style.transition = 'none';
            strip.style.filter = 'none';
            
            // 멈춘 위치 보정 (정확히 칸에 맞게)
            // 그리고 가운데 줄(2번째 칸) 이미지를 결과 이미지로 교체
            // 현재 strip의 구조: 0~49 인덱스. 
            // 뷰포트에는 대략 20번째 쯤이 보일 것임.
            
            // 간단하게: 애니메이션 끝난 후 리셋하고 결과 보여주기
            // "진짜" 느낌을 위해: 멈추는 순간 결과 심볼이 딱 보이게.
            
            // 여기서는 코드를 단순화하여, 애니메이션이 끝나면 
            // strip 위치를 0으로 되돌리고, 
            // strip의 1번째, 2번째, 3번째 이미지를 결과 세팅에 맞게 바꿉니다.
            
            strip.style.transform = `translateY(0px)`;
            
            // 2번째 줄(인덱스 1)이 결과 심볼이어야 함
            const symbols = strip.querySelectorAll('.symbol');
            // 위, 중간(결과), 아래
            symbols[0].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbol()}')`;
            symbols[1].style.backgroundImage = `url('${CONFIG.imgObj.path}${resultSymbols[index]}')`; // 결과!
            symbols[2].style.backgroundImage = `url('${CONFIG.imgObj.path}${getRandomSymbol()}')`;
            
        }, duration);
    });

    // 모든 릴이 멈춘 후 결과 판정 (마지막 릴 시간 + 여유분)
    setTimeout(() => {
        finishSpin(resultSymbols);
    }, 2000 + (CONFIG.reels - 1) * 500 + 500);
}

// 5. 배경 연출 함수
function startBgEffect() {
    let idx = 0;
    state.bgIntervalId = setInterval(() => {
        idx = (idx + 1) % CONFIG.imgObj.bg.length;
        els.bg.style.backgroundImage = `url('${CONFIG.imgObj.path}${CONFIG.imgObj.bg[idx]}')`;
    }, CONFIG.bgIntervalTime);
}

function stopBgEffect() {
    clearInterval(state.bgIntervalId);
    els.bg.style.backgroundImage = `url('${CONFIG.imgObj.path}bg1.png')`; // 기본 배경 복귀
}

// 6. 결과 판정 및 보상
function finishSpin(resultArray) {
    state.isSpinning = false;
    stopBgEffect();
    els.spinBtn.disabled = false;
    audios.spin.pause();

    // 판정 로직 (가운데 줄 연속)
    // resultArray 예: ['star1.png', 'star1.png', 'pro1.png', ...]
    
    let consecutive = 1;
    const firstSym = resultArray[0];
    
    for(let i=1; i<resultArray.length; i++) {
        if(resultArray[i] === firstSym) {
            consecutive++;
        } else {
            break; // 연속 끊김
        }
    }

    let payout = 0;
    let msg = "TRY AGAIN";
    let soundToPlay = audios.lose;

    // A안 계산: EVEN(+1) -> 베팅액(5) + 1 = 6 지급
    if(consecutive === 2) {
        msg = "EVEN! (+1)";
        payout = state.bet + 1;
        soundToPlay = audios.win;
    } else if (consecutive === 3) {
        msg = "WIN! (3x)";
        payout = state.bet * 3;
        soundToPlay = audios.win;
    } else if (consecutive === 4) {
        msg = "BIG WIN! (10x)";
        payout = state.bet * 10;
        soundToPlay = audios.win;
    } else if (consecutive === 5) {
        msg = "MEGA WIN! (25x)";
        payout = state.bet * 25;
        soundToPlay = audios.win; // jackpot 사운드는 운영자 수동 시 사용
    }

    if(payout > 0) {
        state.wallet += payout;
        els.msg.style.color = "#00ffff";
        // 승리 효과
    } else {
        els.msg.style.color = "gray";
    }

    els.msg.innerText = msg;
    updateUI();

    if(state.audioEnabled) {
        soundToPlay.currentTime = 0;
        soundToPlay.play();
    }
}

function updateUI() {
    els.walletSpan.innerText = state.wallet.toLocaleString();
    els.betSpan.innerText = state.bet;
}

function changeBet(delta) {
    if(state.isSpinning) return;
    const newBet = state.bet + delta;
    if(newBet >= 5 && newBet <= 100) { // 최소 5, 최대 100 제한
        state.bet = newBet;
        updateUI();
    }
}

// 게임 시작
window.onload = init;
