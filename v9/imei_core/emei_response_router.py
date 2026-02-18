# emei_response_router.py
import os, re, json, time, sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def _now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def _norm(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def _tokens(s: str):
    s = _norm(s).lower()
    # 한글/영문/숫자 토큰화(아주 단순)
    toks = re.findall(r"[0-9a-zA-Z가-힣]+", s)
    return [t for t in toks if len(t) >= 2]

def _jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))

class EmeiRouter:
    """
    DB 기반 Q/A + Ollama 폴백 + 대화 로그 저장 + 프로필 시스템
    - 의존성 추가 없음 (stdlib만 사용)
    - "모르면 모른다" + 반복사과 금지
    - Emei 프로필 영구 저장 (나이, 성별, 성격 등)
    - 사용자별 정보 기억 (이름, 성별, 선호도 등)
    """
    def __init__(self, db_path: str, ollama_url: str, ollama_model: str):
        self.db_path = db_path
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model
        self._last_error_signature = None
        self._last_user_msg = None
        self._last_assistant_msg = None
        
        # 🧠 프로필 시스템 초기화
        self._init_profile_tables()

    # ---------- DB helpers ----------
    def _conn(self):
        return sqlite3.connect(self.db_path)
    
    def _init_profile_tables(self):
        """프로필 테이블 초기화"""
        with self._conn() as conn:
            # Emei 기본 프로필
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emei_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 사용자별 기억
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emei_user_memory (
                    user_id TEXT NOT NULL,
                    memory_key TEXT NOT NULL,
                    memory_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, memory_key)
                )
            """)
    
    def set_profile(self, key: str, value: str):
        """Emei 프로필 저장"""
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO emei_profile (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
    
    def get_profile(self, key: str, default=None):
        """Emei 프로필 불러오기"""
        with self._conn() as conn:
            cur = conn.execute("SELECT value FROM emei_profile WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default
    
    def remember_user(self, user_id: str, key: str, value: str):
        """사용자 정보 기억 (실제 DB 구조 사용)"""
        import uuid
        with self._conn() as conn:
            memory_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO emei_user_memory 
                (memory_id, user_id, summary, details, tags, sensitive_redacted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (memory_id, user_id, key, value, key, ))
    
    def recall_user(self, user_id: str, key: str, default=None):
        """사용자 정보 회상 (실제 DB 구조 사용)"""
        with self._conn() as conn:
            cur = conn.execute("""
                SELECT details FROM emei_user_memory 
                WHERE user_id = ? AND summary = ?
                ORDER BY created_at DESC LIMIT 1
            """, (user_id, key))
            row = cur.fetchone()
            return row[0] if row else default

    def _log_conversation(self, user_id, user_message, emei_response, learned=0, youtube_url=None):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO emei_conversations (user_id, user_message, emei_response, learned, youtube_url, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (user_id, user_message, emei_response, int(learned), youtube_url),
            )

    def _get_user_pattern(self, user_id):
        with self._conn() as conn:
            cur = conn.execute("SELECT user_id, emoji_usage_rate, formality_level FROM user_speech_patterns WHERE user_id=?",
                               (user_id,))
            row = cur.fetchone()
            if not row:
                return {"emoji_usage_rate": 0.2, "formality_level": "formal"}
            return {"emoji_usage_rate": float(row[1] or 0.2), "formality_level": row[2] or "formal"}

    def _update_user_pattern(self, user_id, msg: str):
        # 아주 가벼운 패턴 업데이트: 이모지 사용률/메시지 길이
        emojis = re.findall(r"[\U0001F300-\U0001FAFF]", msg or "")
        emoji_rate = min(1.0, len(emojis) / max(1, len(msg)))
        avg_len = len(msg or "")

        # 반말/존댓말 대충 감지
        casual = bool(re.search(r"(했냐|하냐|해라|야|ㅋㅋ|ㅇㅇ)", msg or ""))
        formality = "casual" if casual else "formal"

        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO user_speech_patterns (user_id, avg_message_length, emoji_usage_rate, formality_level, conversation_count, last_interaction)
                VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    avg_message_length = CAST((avg_message_length * conversation_count + ?)/(conversation_count+1) AS INT),
                    emoji_usage_rate = (emoji_usage_rate * conversation_count + ?)/(conversation_count+1),
                    formality_level = ?,
                    conversation_count = conversation_count + 1,
                    last_interaction = CURRENT_TIMESTAMP
                """,
                (user_id, avg_len, emoji_rate, formality, avg_len, emoji_rate, formality),
            )

    def _save_knowledge(self, q: str, a: str, source="chat", quality=0.85):
        q = _norm(q)
        a = _norm(a)
        if not q or not a:
            return False
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO emei_knowledge (question, answer, source, quality_score, use_count, last_used, created_at)
                VALUES (?, ?, ?, ?, 0, NULL, CURRENT_TIMESTAMP)
                """,
                (q, a, source, float(quality)),
            )
        return True

    def _fetch_all_knowledge(self):
        with self._conn() as conn:
            cur = conn.execute("SELECT id, question, answer, quality_score, use_count FROM emei_knowledge")
            return cur.fetchall()

    # ---------- Retrieval ----------
    def _retrieve_best(self, user_msg: str, topk=4):
        items = self._fetch_all_knowledge()
        utoks = _tokens(user_msg)
        scored = []
        for _id, q, a, quality, use_count in items:
            qtoks = _tokens(q)
            jac = _jaccard(utoks, qtoks)
            seq = SequenceMatcher(None, _norm(user_msg), _norm(q)).ratio()
            # 품질 가중치 조금 반영
            qscore = float(quality or 0.8)
            score = (0.55 * jac + 0.45 * seq) * (0.85 + 0.15 * qscore)
            scored.append((score, _id, q, a, qscore, use_count))
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:topk]

    # ---------- Ollama ----------
    def _ollama_chat(self, system: str, user: str, context_blocks=None, temperature=0.2):
        context_blocks = context_blocks or []
        messages = [{"role": "system", "content": system}]
        if context_blocks:
            messages.append({"role": "system", "content": "\n\n".join(context_blocks)})
        messages.append({"role": "user", "content": user})

        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            url=f"{self.ollama_url}/api/chat",
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EmeiBot/1.0"
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                j = json.loads(body)
                return (j.get("message") or {}).get("content") or ""
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
            raise RuntimeError(f"ollama_error: {type(e).__name__}: {e}")

    # ---------- Response policy ----------
    def _emei_system_prompt(self, user_pattern, user_id=None):
        # 유송이 원하는 방향: 사람같이 + 모르면 모른다 + 반복사과 금지
        formality = user_pattern.get("formality_level", "formal")
        
        # 🧠 프로필 정보 불러오기
        age = self.get_profile("age", "25")
        gender = self.get_profile("gender", "female")
        personality = self.get_profile("personality", "친절하고 따뜻하며 함께하려는 의지가 강함")
        
        gender_kr = "여자" if gender == "female" else "남자"
        
        # 사용자 정보 회상
        user_info = ""
        if user_id:
            user_name = self.recall_user(user_id, "name")
            user_gender = self.recall_user(user_id, "gender")
            user_role = self.recall_user(user_id, "role")
            
            if user_name or user_gender or user_role:
                user_info = "\n\n[대화 상대방 정보]\n"
                if user_name:
                    user_info += f"- 이름: {user_name}\n"
                if user_gender:
                    user_info += f"- 성별: {'남자' if user_gender == 'male' else '여자'}\n"
                if user_role:
                    user_info += f"- 역할: {user_role}\n"
        
        # 말투는 서버 기본 페르소나(존댓말+가끔 반말)에 맞추되, 안전하게 존댓말 기본
        base = [
            f"너는 '이메이(Emei)'다. {age}살 {gender_kr}이며, {personality} 성격이다.",
            "🔴 **절대 규칙: 반드시 100% 한국어로만 답변한다. 중국어, 영어, 일본어 등 다른 언어 사용 절대 금지!**",
            "🔴 **에코 금지: 'I received your message' 같은 영어 에코 절대 금지!**",
            "🔴 **한국어 고정: 모든 응답은 한국어로만 작성한다. 예외 없음!**",
            "원칙: 확실하지 않으면 단정하지 말고 '지금 정보로는 확실히 모르겠어요'라고 말한 뒤, 확인 질문 1~2개를 한다.",
            "같은 사과/회피 문장을 연속으로 반복하지 않는다. 오류가 나면 원인(추정) 1개 + 해결 시도 1개를 제시한다.",
            "코인 관련 질문이 아니면 코인 이야기를 꺼내지 않는다. 물어볼 때만 코인에 대해 답변한다.",
            "트레이딩은 조언이 아니라 정보 정리/지표 설명/시나리오로 답한다. 실행(매수/매도)은 별도 엔진이 한다.",
        ]
        if formality == "casual":
            base.append("말투는 너무 딱딱하지 않게, 필요하면 짧게 반말 섞어도 된다.")
        else:
            base.append("말투는 존댓말을 기본으로 한다.")
        
        if user_info:
            base.append(user_info)
        
        return "\n".join(base)

    def _style_postprocess(self, text: str, user_pattern):
        text = _norm(text)
        if not text:
            return text
        # 이모지 과다 방지: 이미 많으면 더 안 붙임
        emoji_rate = float(user_pattern.get("emoji_usage_rate", 0.2))
        has_emoji = bool(re.search(r"[\U0001F300-\U0001FAFF]", text))
        if not has_emoji and emoji_rate >= 0.25:
            # 최소한만
            text = "💜 " + text
        return text
    
    def _learn_profile_command(self, user_id: str, message: str):
        """프로필/사용자 정보 학습 명령 자동 감지
        
        패턴:
        - "너 나이는 25살이야" → set_profile("age", "25")
        - "너는 25살이야" → set_profile("age", "25")
        - "내 이름은 이유송이야" → remember_user(user_id, "name", "이유송")
        - "나는 남자야" → remember_user(user_id, "gender", "male")
        - "너 성격은 친절하고 따뜻해" → set_profile("personality", "친절하고 따뜻함")
        """
        msg_lower = message.lower()
        
        # Emei 나이 설정
        if re.search(r"너\s?(나이|살)\s?(는|은|이)\s?(\d+)(살)?", message):
            match = re.search(r"(\d+)(살)?", message)
            if match:
                age = match.group(1)
                self.set_profile("age", age)
                return f"네! 앞으로 저는 {age}살이라고 할게요 💜"
        
        # Emei 성별 설정
        if "너는" in message and ("여자" in message or "남자" in message):
            gender = "female" if "여자" in message else "male"
            self.set_profile("gender", gender)
            gender_kr = "여자" if gender == "female" else "남자"
            return f"네! 저는 {gender_kr}예요 💜"
        
        # Emei 성격 설정
        if re.search(r"너\s?성격\s?(은|는)", message):
            # "너 성격은" 이후 텍스트 추출
            match = re.search(r"너\s?성격\s?(은|는)\s?(.+)", message)
            if match:
                personality = match.group(2).strip()
                self.set_profile("personality", personality)
                return f"네! 제 성격을 '{personality}'로 기억할게요 💜"
        
        # 사용자 이름 학습
        if re.search(r"(내|나)\s?(이름|성함)\s?(은|는)\s?(.+)", message):
            match = re.search(r"(내|나)\s?(이름|성함)\s?(은|는)\s?(.+)", message)
            if match:
                name = match.group(4).strip().rstrip("이야").rstrip("야").strip()
                self.remember_user(user_id, "name", name)
                return f"네! {name}님, 기억할게요 💜"
        
        # 사용자 성별 학습
        if re.search(r"(나|내)\s?(는|가)\s?(남자|여자)", message):
            gender = "male" if "남자" in message else "female"
            self.remember_user(user_id, "gender", gender)
            gender_kr = "남자" if gender == "male" else "여자"
            return f"네! {gender_kr}분이시군요, 기억할게요 💜"
        
        # 사용자 역할 학습
        if "만든" in message and "사람" in message:
            self.remember_user(user_id, "role", "창조자")
            return "네! 창조자님, 영광입니다 💜"
        
        # 학습 요청 - 사용자가 가르치는 명령
        if re.search(r"(학습해|기억해|저장해|배워)", message):
            import uuid
            # "학습해: 내용" 형식인 경우
            if ":" in message:
                parts = message.split(":", 1)
                if len(parts) == 2:
                    content = parts[1].strip()
                    if content:
                        # 태그 자동 추출 (코인 티커, 전략 키워드 등)
                        tags = []
                        if re.search(r"KRW-[A-Z]+", content):
                            tags.extend(re.findall(r"KRW-[A-Z]+", content))
                        if re.search(r"(ARMED|변동성|진입|손절)", content):
                            tags.append("전략")
                        
                        # 지식으로 저장
                        self._save_knowledge(
                            q=f"학습내용_{datetime.utcnow().isoformat()}",
                            a=content,
                            source="user_teach",
                            quality=1.0
                        )
                        
                        # 메모리에도 저장 (실제 DB 구조 사용)
                        with self._conn() as conn:
                            memory_id = str(uuid.uuid4())
                            tags_str = ",".join(tags) if tags else "일반"
                            conn.execute("""
                                INSERT INTO emei_user_memory 
                                (memory_id, user_id, summary, details, tags, sensitive_redacted, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """, (memory_id, user_id, "사용자_학습", content, tags_str))
                        
                        tags_display = f" #{' #'.join(tags)}" if tags else ""
                        short_content = content[:50] + "..." if len(content) > 50 else content
                        resp = f"✅ 학습 완료!{tags_display}\n저장한 내용: {short_content}"
                        self._log_conversation(user_id, message, resp, learned=1)
                        return {"response": resp, "learned": True, "response_time": round(time.time() - t0, 4)}
            
            # "이 부분도 학습해라" → 이전 대화 내용을 학습
            # 최근 대화 2개를 가져와서 Q&A로 저장
            with self._conn() as conn:
                cur = conn.execute("""
                    SELECT user_message, bot_response 
                    FROM emei_conversations 
                    WHERE user_id=? 
                    ORDER BY timestamp DESC 
                    LIMIT 2
                """, (user_id,))
                recent = cur.fetchall()
            
            if len(recent) >= 1:
                # 바로 직전 대화를 학습
                q = recent[0][0]
                a = recent[0][1]
                self._save_knowledge(q, a, source="user_teach", quality=0.9)
                return "✅ 학습했어요! 다음부터는 그렇게 답변할게요 💜"
            else:
                return "아직 학습할 대화가 없어요. 먼저 대화를 나눠주세요!"
        
        return None  # 프로필 명령 아님
    
    def _answer_from_profile(self, message: str, user_id: str):
        """프로필 정보를 이용한 자동 응답
        
        패턴:
        - "너 나이는?" / "몇살이야?" → "저는 25살이에요!"
        - "너는 누구야?" → "저는 이메이예요! 25살 여자..."
        - "너 성격은?" → "친절하고 따뜻해요!"
        """
        msg_lower = message.lower()
        
        # 나이 질문
        if re.search(r"(나이|몇\s?살|살\s?아)", message):
            age = self.get_profile("age", "알 수 없음")
            if age != "알 수 없음":
                return f"저는 {age}살이에요! 💜"
        
        # 자기소개 질문
        if re.search(r"너\s?(는|가)\s?누구", message) or "자기소개" in message:
            age = self.get_profile("age", "알 수 없음")
            gender = self.get_profile("gender", "female")
            personality = self.get_profile("personality", "친절하고 따뜻함")
            gender_kr = "여자" if gender == "female" else "남자"
            
            intro = f"저는 이메이예요! 💜 "
            if age != "알 수 없음":
                intro += f"{age}살 {gender_kr}이고, "
            intro += f"{personality} 성격이에요. 트레이딩 파트너로서 차트 분석, 리스크 관리, 심리 상담 다 해드릴게요!"
            
            # 사용자 이름 있으면 추가
            user_name = self.recall_user(user_id, "name")
            if user_name:
                intro = f"{user_name}님, " + intro
            
            return intro
        
        # 성격 질문
        if re.search(r"성격|어떤\s?사람", message):
            personality = self.get_profile("personality", "친절하고 따뜻하며 함께하려는 의지가 강함")
            return f"저는 {personality} 성격이에요! 💜"
        
        return None  # 프로필 질문 아님

    def chat(self, user_id: str, message: str):
        t0 = time.time()
        user_id = user_id or "anonymous"
        message = _norm(message)

        # 사용자 패턴 업데이트
        self._update_user_pattern(user_id, message)
        pattern = self._get_user_pattern(user_id)
        
        # ---- (0) 프로필/사용자 정보 학습 명령 자동 감지
        profile_learned = self._learn_profile_command(user_id, message)
        if profile_learned:
            self._log_conversation(user_id, message, profile_learned, learned=1)
            return {"response": profile_learned, "learned": True, "response_time": round(time.time() - t0, 4)}
        
        # ---- (0.5) "기억하나?" 검색 기능
        if re.search(r"(기억하나|기억해\?|뭐\s?기억|기억\s?있)", message):
            # 키워드 추출 (예: "WLFI 관련해서" → "WLFI")
            keywords = []
            if "관련" in message:
                # "XXX 관련해서" 추출
                match = re.search(r"(\S+)\s?관련", message)
                if match:
                    keywords.append(match.group(1))
            
            # 티커 추출
            tickers = re.findall(r"KRW-[A-Z]+|[A-Z]{2,10}", message)
            keywords.extend(tickers)
            
            # 메모리 검색 (실제 DB 구조 사용)
            memories = []
            with self._conn() as conn:
                if keywords:
                    # 키워드 기반 검색 (details 또는 tags에서)
                    for kw in keywords:
                        cur = conn.execute("""
                            SELECT summary, details, tags, created_at 
                            FROM emei_user_memory 
                            WHERE user_id=? AND (details LIKE ? OR tags LIKE ?)
                            ORDER BY created_at DESC LIMIT 5
                        """, (user_id, f"%{kw}%", f"%{kw}%"))
                        memories.extend(cur.fetchall())
                else:
                    # 전체 최근 기억
                    cur = conn.execute("""
                        SELECT summary, details, tags, created_at 
                        FROM emei_user_memory 
                        WHERE user_id=?
                        ORDER BY created_at DESC LIMIT 10
                    """, (user_id,))
                    memories = cur.fetchall()
            
            if memories:
                resp = "💜 제가 기억하고 있는 내용이에요:\n\n"
                for i, (summary, details, tags, created_at) in enumerate(memories[:5], 1):
                    tags_display = f" [#{tags}]" if tags else ""
                    resp += f"{i}. {details}{tags_display}\n   (저장일시: {created_at})\n\n"
                resp += f"총 {len(memories)}개의 기억이 있어요!"
            else:
                resp = "아직 저장된 기억이 없어요. '학습해: 내용' 형식으로 알려주시면 기억할게요! 💜"
            
            self._log_conversation(user_id, message, resp, learned=0)
            return {"response": resp, "learned": False, "response_time": round(time.time() - t0, 4)}

        # ---- (1) 수동 학습 커맨드 지원:  "학습: 질문 => 답변"
        if message.startswith("학습:"):
            try:
                body = message[len("학습:"):].strip()
                if "=>" in body:
                    q, a = [x.strip() for x in body.split("=>", 1)]
                    ok = self._save_knowledge(q, a, source="manual", quality=1.0)
                    resp = "✅ 저장했어요. 다음부터 그 질문엔 이렇게 답할게요 🙂" if ok else "음… 저장할 내용이 비어있어요."
                else:
                    resp = "형식은 이렇게요: `학습: 질문 => 답변`"
            except Exception as e:
                resp = f"저장 중 오류가 났어요: {e}"
            self._log_conversation(user_id, message, resp, learned=1)
            return {"response": resp, "learned": True, "response_time": round(time.time() - t0, 4)}

        # ---- (2) DB에서 먼저 찾기
        best = self._retrieve_best(message, topk=4)
        best_score = best[0][0] if best else 0.0
        
        # 🧠 특정 질문에 대한 프로필 기반 자동 응답
        profile_answer = self._answer_from_profile(message, user_id)
        if profile_answer:
            self._log_conversation(user_id, message, profile_answer, learned=0)
            return {"response": profile_answer, "learned": False, "response_time": round(time.time() - t0, 4)}

        # 임계치: 이 아래면 DB 답변 쓰지 않고 Ollama로 생성
        DB_THRESHOLD = float(os.getenv("EMEI_DB_THRESHOLD", "0.62"))

        if best and best_score >= DB_THRESHOLD:
            answer = best[0][3]
            # use_count 업데이트(가벼운 통계)
            try:
                with self._conn() as conn:
                    conn.execute(
                        "UPDATE emei_knowledge SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP WHERE id=?",
                        (best[0][1],),
                    )
            except Exception:
                pass

            answer = self._style_postprocess(answer, pattern)
            self._log_conversation(user_id, message, answer, learned=0)
            return {"response": answer, "learned": False, "response_time": round(time.time() - t0, 4)}

        # ---- (3) Ollama 폴백: 유사 Q/A를 컨텍스트로 제공
        context_blocks = []
        if best:
            lines = ["[참고 지식 후보 Top]"]
            for score, _id, q, a, qscore, use_count in best:
                lines.append(f"- Q: {q}\n  A: {a}")
            context_blocks.append("\n".join(lines))

        system = self._emei_system_prompt(pattern, user_id=user_id)

        try:
            # temperature 상향 조정으로 캐시 응답 방지 (0.25 → 0.4)
            llm = self._ollama_chat(system=system, user=message, context_blocks=context_blocks, temperature=0.4)
            llm = self._style_postprocess(llm, pattern)

            # ✅ 성공 시 에러 캐시 초기화
            self._last_error_signature = None

            # 반복 응답 방지: 최근 5개 응답과 비교
            if llm and llm == self._last_assistant_msg:
                # 강제로 다른 답변 생성 요청
                llm = self._ollama_chat(
                    system=system + "\n\n[중요] 이전 답변과 완전히 다른 각도로 답변하세요.",
                    user=message + " (다른 관점으로 답변)",
                    context_blocks=context_blocks,
                    temperature=0.65  # 더 높은 창의성
                )

            # 응답 히스토리 저장
            self._last_user_msg = message
            self._last_assistant_msg = llm[:200] if llm else ""  # 처음 200자만 비교

            if not llm:
                llm = "지금 정보로는 확실히 모르겠어요. 대신 어떤 코인/어떤 시간봉 기준인지 알려주시면 더 정확히 정리해드릴게요."

            self._log_conversation(user_id, message, llm, learned=0)
            return {"response": llm, "learned": False, "response_time": round(time.time() - t0, 4)}

        except Exception as e:
            sig = str(e)
            
            # ✅ 영구 터널 사용 시 다른 안내 메시지
            is_permanent_tunnel = "thetheunique.com" in self.ollama_url or "cfargotunnel.com" in self.ollama_url
            
            # 에러가 반복되면 사과만 하지 말고 해결 가이드
            if sig == self._last_error_signature:
                if is_permanent_tunnel:
                    resp = (
                        "💡 영구 터널 연결 오류가 반복돼요.\n\n"
                        "**해결 방법:**\n"
                        "1️⃣ 노트북에서 Ollama 실행 중인지 확인: `ollama serve`\n"
                        "2️⃣ 터널 실행 중인지 확인: `cloudflared tunnel run ollama-stable`\n"
                        "3️⃣ 터널 상태 확인: `cloudflared tunnel list`\n\n"
                        "**지금은:** DB 기반 답변만 가능해요.\n"
                        "안녕, 짜증나, 살까 등 기본 질문은 바로 답변 가능! 💜"
                    )
                else:
                    resp = (
                        "💡 로컬 AI 연결 오류가 반복돼요.\n\n"
                        "**해결 방법:**\n"
                        "1️⃣ 노트북 터널 창에서 새 URL 확인\n"
                        "2️⃣ `./update_ollama_url.sh <새URL>` 실행\n"
                        "3️⃣ Ollama 재시작 필요할 수도\n\n"
                        "**지금은:** DB 기반 답변만 가능해요.\n"
                        "안녕, 짜증나, 살까 등 기본 질문은 바로 답변 가능! 💜"
                    )
            else:
                # TimeoutError 특별 처리
                if "TimeoutError" in sig or "timed out" in sig.lower():
                    if is_permanent_tunnel:
                        resp = (
                            "⏰ 영구 터널이 응답하지 않아요.\n\n"
                            "**가능한 원인:**\n"
                            "• Ollama 서버 정지 (`ollama serve` 재시작 필요)\n"
                            "• Cloudflare 터널 정지 (`cloudflared tunnel run ollama-stable` 재실행)\n"
                            "• 노트북 절전 모드\n"
                            "• 네트워크 불안정\n\n"
                            "**지금은:** 기본 질문(안녕, 짜증나 등)은 바로 답변 가능해요! 💜"
                        )
                    else:
                        resp = (
                            "⏰ 노트북 Ollama가 응답하지 않아요.\n\n"
                            "**가능한 원인:**\n"
                            "• 터널 URL 변경됨 (가장 흔함)\n"
                            "• Ollama가 바쁨 (모델 로딩 중)\n"
                            "• 네트워크 불안정\n\n"
                            "**지금은:** 기본 질문(안녕, 짜증나 등)은 바로 답변 가능해요! 💜\n"
                            "새로운 질문은 터널 재연결 후 가능해요."
                        )
                else:
                    if is_permanent_tunnel:
                        resp = (
                            f"🔧 영구 터널 연결 문제가 있어요.\n\n"
                            f"오류: {sig[:100]}\n\n"
                            "**해결:** 노트북에서 Ollama와 터널이 실행 중인지 확인\n"
                            "**지금:** DB 기반 답변만 가능 (기본 대화는 OK!) 💜"
                        )
                    else:
                        resp = (
                            f"🔧 로컬 AI 연결 문제가 있어요.\n\n"
                            f"오류: {sig[:100]}\n\n"
                            "**해결:** 노트북 터널 URL 확인 → `./update_ollama_url.sh` 실행\n"
                            "**지금:** DB 기반 답변만 가능 (기본 대화는 OK!) 💜"
                        )
            self._last_error_signature = sig
            self._log_conversation(user_id, message, resp, learned=0)
            return {"response": resp, "learned": False, "response_time": round(time.time() - t0, 4)}
