# -*- coding: utf-8 -*-
"""
🤖 Lee May Training Center - API Server (Full Version)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
유송(wordycow) 시스템 방향에 맞춘 "운영 가능한" 풀버전:

✅ (1) 관리자 인증/권한
    - 헤더 토큰(X-ADMIN-TOKEN) + 세션 로그인(/api/auth/login) 둘 다 지원
    - 위험 API(트레이딩 실행/봇 제어/감사로그 열람)는 관리자만

✅ (2) 감사(Audit) 로그
    - 관리자 페이지 버튼 클릭 기록 저장
    - 관리자 페이지에서 "기록을 열어봤는지"(history/audit 열람) 자동 기록

✅ (3) RealSimTrading (실전형 시뮬)
    - 수수료 0.05% 적용
    - 잔고/포지션 DB 영구 저장(재시작해도 유지)
    - upbit_bot.db와 분리된 sim_trading.db 사용(기본)

✅ (4) Emotion + Image
    - C:\leemay_project\leemay\images (JPG) 제공

✅ (5) Live Telemetry
    - psutil 기반 실제 CPU/RAM/Disk

✅ (6) Learning Jobs (유튜브 학습) - 운영 뼈대
    - start/status/logs/stats 제공
    - 실제 학습은 외부 스크립트 연결 가능(YT_LEARNER_CMD 환경변수)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
환경변수(권장):
- ADMIN_ID=wordycow
- ADMIN_TOKEN=임의의_긴_문자열(필수 권장)
- SECRET_KEY=임의의_긴_문자열(세션 쿠키 서명용, 필수 권장)
- CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5500 (필요한 프론트만)
- IMAGES_DIR=C:\\leemay_project\\leemay\\images  (기본값 동일)
- YT_LEARNER_CMD=python C:\\leemay_project\\leemay\\learning\\youtube_learner.py
"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
import json
import uuid
import time
import sqlite3
import threading
import subprocess
from datetime import datetime
from pathlib import Path

import psutil


# ============================================================
# 0) 기본 경로/환경
# ============================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(DATA_DIR, "logs")
LEARNING_LOG_DIR = os.path.join(DATA_DIR, "learning_logs")

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
Path(LEARNING_LOG_DIR).mkdir(parents=True, exist_ok=True)

# 이미지 폴더(유송 PC 고정 경로 기본)
IMAGES_DIR = os.environ.get("IMAGES_DIR", r"C:\leemay_project\leemay\images")

# 서버용 DB(감사로그/러닝잡/채팅로그)
SERVER_DB_PATH = os.path.join(DATA_DIR, "server.db")

# 시뮬 트레이딩 DB(실전봇 DB와 반드시 분리 권장)
SIM_DB_PATH = os.environ.get("SIM_DB_PATH", os.path.join(DATA_DIR, "sim_trading.db"))

ADMIN_ID = os.environ.get("ADMIN_ID", "wordycow").strip()
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "").strip()
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()

# CORS 제한(운영은 반드시 특정 origin만 허용)
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5000,http://127.0.0.1:5500,http://localhost:5173"
).split(",")

# 유튜브 학습 외부 실행 커맨드(있으면 연결, 없으면 stub)
YT_LEARNER_CMD = os.environ.get("YT_LEARNER_CMD", "").strip()

# 봇 레지스트리(프로세스 감시/제어 목록)
BOT_REGISTRY_PATH = os.path.join(DATA_DIR, "bot_registry.json")


# ============================================================
# 1) 유틸
# ============================================================
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_json(obj) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"


def get_client_ip() -> str:
    xf = request.headers.get("X-Forwarded-For", "")
    if xf:
        return xf.split(",")[0].strip()
    return request.remote_addr or ""


def get_user_id() -> str:
    # 우선순위: 헤더 > body > query > session
    uid = (request.headers.get("X-USER-ID") or "").strip()
    if not uid:
        if request.is_json:
            body = request.get_json(silent=True) or {}
            uid = (body.get("user_id") or body.get("user") or "").strip()
    if not uid:
        uid = (request.args.get("user_id") or "").strip()
    if not uid:
        uid = (session.get("user_id") or "").strip()
    return uid or "guest"


def is_admin() -> bool:
    uid = get_user_id()
    # 1) 헤더 토큰 방식
    token = (request.headers.get("X-ADMIN-TOKEN") or "").strip()
    if uid == ADMIN_ID and ADMIN_TOKEN and token == ADMIN_TOKEN:
        return True
    # 2) 세션 로그인 방식
    if uid == ADMIN_ID and session.get("is_admin") is True:
        return True
    return False


def require_admin():
    if not is_admin():
        return jsonify({"success": False, "error": "관리자 권한이 필요합니다."}), 403
    return None


# ============================================================
# 2) 서버 DB 초기화 (감사로그/러닝잡/채팅로그)
# ============================================================
def db_server_conn():
    conn = sqlite3.connect(SERVER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_server_db():
    conn = db_server_conn()
    cur = conn.cursor()

    # 감사로그: "누가/언제/어떤 화면/어떤 버튼/어떤 API를 봤는지" 남김
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        user_id TEXT,
        is_admin INTEGER,
        ip TEXT,
        user_agent TEXT,
        event_type TEXT,       -- API_CALL / UI_CLICK / VIEW / AUTH / BOT_CONTROL 등
        event_name TEXT,       -- e.g. "OPEN_ADMIN_PAGE", "CLICK_STOP_BOT", "GET_TRADE_HISTORY"
        path TEXT,
        method TEXT,
        status_code INTEGER,
        payload_json TEXT
    )
    """)

    # 채팅 히스토리(원하면 UI에서 불러오기 가능)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        user_id TEXT,
        message TEXT,
        response TEXT,
        emotion TEXT
    )
    """)

    # 러닝 잡(유튜브 학습 등) 상태 관리
    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_jobs (
        id TEXT PRIMARY KEY,
        ts_created TEXT,
        ts_started TEXT,
        ts_finished TEXT,
        created_by TEXT,
        job_type TEXT,          -- "youtube"
        payload_json TEXT,      -- {"url": "..."}
        status TEXT,            -- created/running/done/error/stubbed
        log_path TEXT,
        result_json TEXT
    )
    """)

    conn.commit()
    conn.close()


def audit(event_type: str, event_name: str, status_code: int = 200, payload=None):
    # 이미지/헬스체크는 스킵
    path = request.path or ""
    if path.startswith("/image/") or path == "/health":
        return

    conn = db_server_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO audit_log
        (ts, user_id, is_admin, ip, user_agent, event_type, event_name, path, method, status_code, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_iso(),
        get_user_id(),
        1 if is_admin() else 0,
        get_client_ip(),
        (request.headers.get("User-Agent") or "")[:300],
        event_type,
        event_name,
        path,
        request.method,
        int(status_code),
        safe_json(payload or {})
    ))
    conn.commit()
    conn.close()


# ============================================================
# 3) RealSimTrading (DB 영구 저장형)
# ============================================================
class RealSimTrading:
    def __init__(self, initial_krw=1000000, fee_rate=0.0005):
        self.fee_rate = float(fee_rate)
        self.initial_krw = float(initial_krw)
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(SIM_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._conn()
        cur = conn.cursor()

        # 계정(원화 잔고)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sim_account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            krw_balance REAL,
            updated_at TEXT
        )
        """)
        # 포지션(코인별 보유/평단)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sim_positions (
            coin TEXT PRIMARY KEY,
            amount REAL,
            avg_price REAL,
            updated_at TEXT
        )
        """)
        # 거래 히스토리
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sim_trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            coin TEXT,
            side TEXT,
            price REAL,
            amount REAL,
            trade_value REAL,
            fee REAL,
            strategy TEXT,
            reason TEXT,
            krw_balance_after REAL,
            realized_pnl REAL
        )
        """)
        # 계정 row 보장
        cur.execute("SELECT krw_balance FROM sim_account WHERE id=1")
        row = cur.fetchone()
        if row is None:
            cur.execute(
                "INSERT INTO sim_account (id, krw_balance, updated_at) VALUES (1, ?, ?)",
                (self.initial_krw, now_iso())
            )
        conn.commit()
        conn.close()

    def _get_balance(self) -> float:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT krw_balance FROM sim_account WHERE id=1")
        bal = float(cur.fetchone()[0])
        conn.close()
        return bal

    def _set_balance(self, new_balance: float):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE sim_account SET krw_balance=?, updated_at=? WHERE id=1",
            (float(new_balance), now_iso())
        )
        conn.commit()
        conn.close()

    def _get_position(self, coin: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT coin, amount, avg_price FROM sim_positions WHERE coin=?", (coin,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"coin": coin, "amount": 0.0, "avg_price": 0.0}
        return {"coin": row[0], "amount": float(row[1]), "avg_price": float(row[2])}

    def _upsert_position(self, coin: str, amount: float, avg_price: float):
        conn = self._conn()
        cur = conn.cursor()
        if amount <= 0:
            cur.execute("DELETE FROM sim_positions WHERE coin=?", (coin,))
        else:
            cur.execute("""
                INSERT INTO sim_positions (coin, amount, avg_price, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(coin) DO UPDATE SET
                    amount=excluded.amount,
                    avg_price=excluded.avg_price,
                    updated_at=excluded.updated_at
            """, (coin, float(amount), float(avg_price), now_iso()))
        conn.commit()
        conn.close()

    def get_snapshot(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT krw_balance FROM sim_account WHERE id=1")
        bal = float(cur.fetchone()[0])
        cur.execute("SELECT coin, amount, avg_price, updated_at FROM sim_positions ORDER BY coin ASC")
        positions = [dict(row) for row in cur.fetchall()]
        conn.close()
        return {"krw_balance": round(bal, 2), "positions": positions}

    def execute_trade(self, coin: str, price: float, amount: float, side: str, strategy: str, reason: str):
        coin = (coin or "").strip().upper()
        side = (side or "").strip().upper()
        if side not in ("BUY", "SELL"):
            return {"success": False, "error": "side는 BUY 또는 SELL 이어야 합니다."}

        try:
            price = float(price)
            amount = float(amount)
        except Exception:
            return {"success": False, "error": "price/amount 숫자 형식이 올바르지 않습니다."}

        if price <= 0 or amount <= 0:
            return {"success": False, "error": "price/amount는 0보다 커야 합니다."}

        trade_value = price * amount
        fee = trade_value * self.fee_rate

        balance = self._get_balance()
        pos = self._get_position(coin)
        realized_pnl = 0.0

        if side == "BUY":
            total_cost = trade_value + fee
            if balance < total_cost:
                return {"success": False, "error": "잔고가 부족합니다, 유송님!"}

            # 신규 평단 계산
            old_amt = pos["amount"]
            old_avg = pos["avg_price"]
            new_amt = old_amt + amount
            new_avg = ((old_amt * old_avg) + trade_value) / new_amt if new_amt > 0 else 0.0

            balance = balance - total_cost
            self._set_balance(balance)
            self._upsert_position(coin, new_amt, new_avg)

        else:  # SELL
            if pos["amount"] < amount:
                return {"success": False, "error": "보유 수량이 부족합니다!"}

            # 실현손익(평단 기준)
            realized_pnl = (price - pos["avg_price"]) * amount - fee
            proceeds = trade_value - fee

            new_amt = pos["amount"] - amount
            new_avg = pos["avg_price"]  # 남은 물량 평단 유지(단순 평균법)
            balance = balance + proceeds

            self._set_balance(balance)
            self._upsert_position(coin, new_amt, new_avg)

        # 히스토리 저장
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sim_trade_history
            (ts, coin, side, price, amount, trade_value, fee, strategy, reason, krw_balance_after, realized_pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso(), coin, side, price, amount, trade_value, fee,
            (strategy or "")[:80], (reason or "")[:400],
            float(balance), float(realized_pnl)
        ))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "msg": f"{coin} {side} 완료 (전략: {strategy} / 사유: {reason})",
            "krw_balance": round(balance, 2),
            "fee": round(fee, 2),
            "realized_pnl": round(realized_pnl, 2),
            "position": self._get_position(coin)
        }

    def history(self, limit=10):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM sim_trade_history
            ORDER BY id DESC
            LIMIT ?
        """, (int(limit),))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows


# ============================================================
# 4) Emotion Engine (1차: 키워드 기반 + 확장 포인트)
# ============================================================
def get_real_emotion(message: str) -> str:
    message = message or ""
    joy_keys = ['행복', '좋아', '수익', '나이스', '와우', '기뻐', '대박', '승리']
    sad_keys = ['손해', '슬퍼', '힘들어', '망함', '우울', '짜증', '불안']
    angry_keys = ['화나', '지워', '에러', '병신', '똑바로', '열받', '빡']
    for k in joy_keys:
        if k in message:
            return "happy"
    for k in sad_keys:
        if k in message:
            return "sad"
    for k in angry_keys:
        if k in message:
            return "angry"
    return "neutral"


# ============================================================
# 5) 봇 레지스트리(프로세스 감시/제어) - 관리자 전용
# ============================================================
def ensure_bot_registry():
    if os.path.exists(BOT_REGISTRY_PATH):
        return
    sample = {
        "bots": [
            {
                "name": "signal_engine",
                "match": "signal_engine",
                "start": "python signal_engine.py",
                "cwd": BASE_DIR
            },
            {
                "name": "execution_engine",
                "match": "execution_engine",
                "start": "python execution_engine.py",
                "cwd": BASE_DIR
            }
        ]
    }
    with open(BOT_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)


def load_bot_registry():
    ensure_bot_registry()
    with open(BOT_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_processes_by_match(match: str):
    match = (match or "").lower()
    found = []
    for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            name = (p.info.get("name") or "").lower()
            cmd = " ".join(p.info.get("cmdline") or []).lower()
            if match and (match in name or match in cmd):
                found.append({
                    "pid": p.info["pid"],
                    "name": p.info.get("name"),
                    "cmdline": p.info.get("cmdline"),
                    "create_time": p.info.get("create_time")
                })
        except Exception:
            continue
    return found


def start_bot(bot):
    cmd = bot.get("start")
    cwd = bot.get("cwd") or BASE_DIR
    if not cmd:
        return {"success": False, "error": "start 커맨드가 없습니다."}
    # Windows에서도 동작하도록 shell=True
    p = subprocess.Popen(cmd, cwd=cwd, shell=True)
    return {"success": True, "pid": p.pid, "cmd": cmd}


def stop_bot(pid: int):
    try:
        proc = psutil.Process(int(pid))
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 6) Learning Jobs (유튜브 학습) - 외부 스크립트 연결형
# ============================================================
def learning_create_job(job_type: str, payload: dict, created_by: str) -> dict:
    job_id = uuid.uuid4().hex
    log_path = os.path.join(LEARNING_LOG_DIR, f"{job_id}.log")

    conn = db_server_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO learning_jobs
        (id, ts_created, ts_started, ts_finished, created_by, job_type, payload_json, status, log_path, result_json)
        VALUES (?, ?, NULL, NULL, ?, ?, ?, ?, ?, NULL)
    """, (
        job_id, now_iso(), created_by, job_type, safe_json(payload), "created", log_path
    ))
    conn.commit()
    conn.close()

    # 즉시 실행(백그라운드)
    t = threading.Thread(target=learning_run_job, args=(job_id,), daemon=True)
    t.start()

    return {"job_id": job_id, "status": "created", "log_path": log_path}


def learning_update(job_id: str, **fields):
    conn = db_server_conn()
    cur = conn.cursor()
    keys = []
    vals = []
    for k, v in fields.items():
        keys.append(f"{k}=?")
        vals.append(v)
    vals.append(job_id)
    cur.execute(f"UPDATE learning_jobs SET {', '.join(keys)} WHERE id=?", tuple(vals))
    conn.commit()
    conn.close()


def learning_append_log(log_path: str, line: str):
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] {line}\n")
    except Exception:
        pass


def learning_get(job_id: str):
    conn = db_server_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM learning_jobs WHERE id=?", (job_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def learning_run_job(job_id: str):
    job = learning_get(job_id)
    if not job:
        return

    learning_update(job_id, status="running", ts_started=now_iso())
    learning_append_log(job["log_path"], f"JOB START: {job_id}")

    payload = json.loads(job.get("payload_json") or "{}")
    url = payload.get("url", "")

    # 외부 learner 연결이 있으면 실행
    if YT_LEARNER_CMD:
        try:
            learning_append_log(job["log_path"], f"RUN learner: {YT_LEARNER_CMD} --url {url}")
            # stdout/stderr를 로그 파일에 붙임
            with open(job["log_path"], "a", encoding="utf-8") as lf:
                p = subprocess.Popen(
                    f'{YT_LEARNER_CMD} "{url}" "{job_id}"',
                    shell=True,
                    stdout=lf,
                    stderr=lf,
                    cwd=BASE_DIR
                )
                code = p.wait()
            if code == 0:
                learning_update(job_id, status="done", ts_finished=now_iso(), result_json=safe_json({"ok": True}))
                learning_append_log(job["log_path"], "JOB DONE (code=0)")
            else:
                learning_update(job_id, status="error", ts_finished=now_iso(), result_json=safe_json({"ok": False, "code": code}))
                learning_append_log(job["log_path"], f"JOB ERROR (code={code})")
        except Exception as e:
            learning_update(job_id, status="error", ts_finished=now_iso(), result_json=safe_json({"ok": False, "error": str(e)}))
            learning_append_log(job["log_path"], f"EXCEPTION: {e}")
    else:
        # learner 미연결이면 stub으로 끝냄(중앙 UI 붙이는 데는 충분)
        learning_append_log(job["log_path"], "YT_LEARNER_CMD가 없어서 STUB 처리합니다.")
        learning_append_log(job["log_path"], f"요청 URL: {url}")
        time.sleep(1)
        learning_update(job_id, status="stubbed", ts_finished=now_iso(), result_json=safe_json({"ok": True, "stubbed": True}))
        learning_append_log(job["log_path"], "JOB STUBBED DONE")


def learning_stats():
    # 실제 값(가짜 금지): server.db + sim_trading.db + learning_logs 크기
    def fsize(p):
        try:
            return os.path.getsize(p)
        except Exception:
            return 0

    total_logs = 0
    for fn in os.listdir(LEARNING_LOG_DIR):
        total_logs += fsize(os.path.join(LEARNING_LOG_DIR, fn))

    return {
        "server_db_size": fsize(SERVER_DB_PATH),
        "sim_db_size": fsize(SIM_DB_PATH),
        "learning_logs_size": total_logs,
        "timestamp": now_iso()
    }


# ============================================================
# 7) Flask 앱
# ============================================================
app = Flask(__name__)
# 세션 쿠키 서명키(반드시 고정)
app.secret_key = SECRET_KEY or "CHANGE_ME_SECRET_KEY"

# CORS 제한
CORS(app, resources={r"/*": {"origins": [o.strip() for o in CORS_ORIGINS if o.strip()]}})

# DB 초기화
init_server_db()
ensure_bot_registry()

# 시뮬 인스턴스
sim_trading = RealSimTrading(initial_krw=1000000, fee_rate=0.0005)

SERVER_START_TS = time.time()


# ============================================================
# 8) 공통 훅: 중요한 API 호출 자동 기록
# ============================================================
@app.after_request
def after(resp):
    try:
        path = request.path or ""
        # 너무 자주 찍히는 건 제외
        if path.startswith("/image/") or path == "/health":
            return resp

        # 관리자 페이지에서 "기록 조회했는지"는 자동으로 남겨야 함
        # - trading/history, admin/audit/list 같은 엔드포인트 접근 자체가 "봤다" 증거
        event_name = "API_CALL"
        if path.startswith("/api/trading/history"):
            event_name = "VIEW_TRADE_HISTORY"
        elif path.startswith("/api/admin/audit/list"):
            event_name = "VIEW_AUDIT_LOG"
        elif path.startswith("/api/learning/"):
            event_name = "LEARNING_API"
        elif path.startswith("/api/bots/"):
            event_name = "BOT_API"

        audit("API_CALL", event_name, status_code=resp.status_code, payload={"q": request.query_string.decode("utf-8", "ignore")})
    except Exception:
        pass
    return resp


# ============================================================
# 9) 기본/헬스
# ============================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "ts": now_iso()})


# ============================================================
# 10) 인증/권한
# ============================================================
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or data.get("user") or "").strip() or "guest"
    token = (data.get("admin_token") or "").strip()

    session["user_id"] = user_id

    # 관리자 로그인 조건: ADMIN_ID + (헤더 토큰 또는 body token 일치)
    if user_id == ADMIN_ID and ADMIN_TOKEN and token == ADMIN_TOKEN:
        session["is_admin"] = True
        audit("AUTH", "ADMIN_LOGIN", payload={"user_id": user_id})
        return jsonify({"success": True, "user_id": user_id, "is_admin": True})

    session["is_admin"] = False
    audit("AUTH", "LOGIN", payload={"user_id": user_id})
    return jsonify({"success": True, "user_id": user_id, "is_admin": False})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    uid = get_user_id()
    session.clear()
    audit("AUTH", "LOGOUT", payload={"user_id": uid})
    return jsonify({"success": True})


@app.route("/api/auth/whoami", methods=["GET"])
def whoami():
    return jsonify({"user_id": get_user_id(), "is_admin": is_admin(), "admin_id": ADMIN_ID})


# ============================================================
# 11) 채팅/이메이
# ============================================================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    uid = get_user_id()

    emotion = get_real_emotion(message)
    image_name = f"{emotion}.jpg"

    response_text = f"유송님, 말씀하신 '{message}' 내용을 잘 들었어요. 분석 중입니다!"

    # 채팅 저장
    conn = db_server_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_history (ts, user_id, message, response, emotion)
        VALUES (?, ?, ?, ?, ?)
    """, (now_iso(), uid, message[:2000], response_text[:2000], emotion))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "text": response_text,
        "emotion": emotion,
        "emotion_score": 0.6,   # (확장 포인트) 향후 감정 점수화
        "image_url": f"/image/{image_name}",
        "user_id": uid,
        "timestamp": now_iso()
    })


@app.route("/image/<filename>", methods=["GET"])
def serve_image(filename):
    # 보안: 파일명만 허용(경로탐색 방지)
    filename = os.path.basename(filename)
    return send_from_directory(IMAGES_DIR, filename)


# ============================================================
# 12) 시스템 상태/텔레메트리
# ============================================================
@app.route("/api/system/status", methods=["GET"])
def system_status():
    uptime_sec = int(time.time() - SERVER_START_TS)

    # 디스크는 BASE_DIR 기준
    disk = psutil.disk_usage(BASE_DIR)

    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.1),
        "memory": psutil.virtual_memory().percent,
        "disk_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "uptime_sec": uptime_sec,
        "server_db_size": os.path.getsize(SERVER_DB_PATH) if os.path.exists(SERVER_DB_PATH) else 0,
        "sim_db_size": os.path.getsize(SIM_DB_PATH) if os.path.exists(SIM_DB_PATH) else 0,
        "timestamp": now_iso()
    })


# ============================================================
# 13) 시뮬 트레이딩(관리자 전용)
# ============================================================
@app.route("/api/trading/snapshot", methods=["GET"])
def trading_snapshot():
    guard = require_admin()
    if guard:
        return guard
    return jsonify({"success": True, "data": sim_trading.get_snapshot()})


@app.route("/api/trading/execute", methods=["POST"])
def trade_execute():
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    res = sim_trading.execute_trade(
        coin=data.get("coin"),
        price=data.get("price"),
        amount=data.get("amount"),
        side=data.get("side"),
        strategy=data.get("strategy", ""),
        reason=data.get("reason", "")
    )
    audit("TRADE", "EXECUTE_SIM_TRADE", payload={"req": data, "res": res})
    return jsonify(res)


@app.route("/api/trading/history", methods=["GET"])
def trade_history():
    guard = require_admin()
    if guard:
        return guard

    limit = int(request.args.get("limit", "10"))
    rows = sim_trading.history(limit=limit)
    return jsonify({"success": True, "items": rows})


# ============================================================
# 14) 봇 관제/제어(관리자 전용)
# ============================================================
@app.route("/api/bots/list", methods=["GET"])
def bots_list():
    guard = require_admin()
    if guard:
        return guard

    reg = load_bot_registry()
    bots = reg.get("bots", [])
    result = []
    for b in bots:
        match = b.get("match", "")
        procs = find_processes_by_match(match)
        result.append({
            "name": b.get("name"),
            "match": match,
            "running": len(procs) > 0,
            "processes": procs
        })
    return jsonify({"success": True, "bots": result})


@app.route("/api/bots/start", methods=["POST"])
def bots_start():
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    reg = load_bot_registry()
    bots = reg.get("bots", [])
    bot = next((x for x in bots if x.get("name") == name), None)
    if not bot:
        return jsonify({"success": False, "error": "등록되지 않은 봇입니다."}), 400

    res = start_bot(bot)
    audit("BOT_CONTROL", "START_BOT", payload={"name": name, "res": res})
    return jsonify(res)


@app.route("/api/bots/stop", methods=["POST"])
def bots_stop():
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    pid = data.get("pid")
    if pid is None:
        return jsonify({"success": False, "error": "pid가 필요합니다."}), 400

    res = stop_bot(int(pid))
    audit("BOT_CONTROL", "STOP_BOT", payload={"pid": pid, "res": res})
    return jsonify(res)


# ============================================================
# 15) 러닝(유튜브 학습) - 중앙 패널용
# ============================================================
@app.route("/api/learning/youtube/start", methods=["POST"])
def learning_youtube_start():
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"success": False, "error": "url이 필요합니다."}), 400

    job = learning_create_job("youtube", {"url": url}, created_by=get_user_id())
    audit("LEARNING", "START_YOUTUBE_LEARNING", payload=job)
    return jsonify({"success": True, "job": job})


@app.route("/api/learning/job/<job_id>/status", methods=["GET"])
def learning_job_status(job_id):
    guard = require_admin()
    if guard:
        return guard

    job = learning_get(job_id)
    if not job:
        return jsonify({"success": False, "error": "job이 없습니다."}), 404

    return jsonify({"success": True, "job": job})


@app.route("/api/learning/job/<job_id>/logs", methods=["GET"])
def learning_job_logs(job_id):
    guard = require_admin()
    if guard:
        return guard

    job = learning_get(job_id)
    if not job:
        return jsonify({"success": False, "error": "job이 없습니다."}), 404

    log_path = job.get("log_path") or ""
    if not log_path or not os.path.exists(log_path):
        return jsonify({"success": True, "lines": []})

    # 최근 N줄만 반환
    n = int(request.args.get("lines", "200"))
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return jsonify({"success": True, "lines": lines[-n:]})


@app.route("/api/learning/stats", methods=["GET"])
def learning_stats_api():
    guard = require_admin()
    if guard:
        return guard
    return jsonify({"success": True, "stats": learning_stats()})


# ============================================================
# 16) 관리자 UI 이벤트/감사로그 조회
# ============================================================
@app.route("/api/admin/ui_event", methods=["POST"])
def admin_ui_event():
    guard = require_admin()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    event_name = (data.get("event_name") or "").strip() or "UI_EVENT"
    detail = data.get("detail") or {}
    # 버튼 클릭/페이지 이동 등 기록
    audit("UI_CLICK", event_name, payload={"detail": detail})
    return jsonify({"success": True})


@app.route("/api/admin/audit/list", methods=["GET"])
def admin_audit_list():
    guard = require_admin()
    if guard:
        return guard

    limit = int(request.args.get("limit", "100"))
    event_type = (request.args.get("event_type") or "").strip()

    conn = db_server_conn()
    cur = conn.cursor()

    if event_type:
        cur.execute("""
            SELECT * FROM audit_log
            WHERE event_type=?
            ORDER BY id DESC
            LIMIT ?
        """, (event_type, limit))
    else:
        cur.execute("""
            SELECT * FROM audit_log
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    return jsonify({"success": True, "items": rows})


# ============================================================
# 17) 엔트리포인트
# ============================================================
if __name__ == "__main__":
    print("🚀 Lee May 통합 관제 서버 가동 (Port 5001)")
    print(f"📁 이미지 경로: {IMAGES_DIR} (JPG 모드)")
    if not ADMIN_TOKEN:
        print("⚠️  ADMIN_TOKEN 환경변수가 비어있음: 운영/외부접속이면 반드시 설정하세요!")
    app.run(host="0.0.0.0", port=5001, debug=False)
