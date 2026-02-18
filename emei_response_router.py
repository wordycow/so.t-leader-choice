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
    DB 기반 Q/A + Ollama 폴백 + 대화 로그 저장
    - 의존성 추가 없음 (stdlib만 사용)
    - "모르면 모른다" + 반복사과 금지
    """
    def __init__(self, db_path: str, ollama_url: str, ollama_model: str):
        self.db_path = db_path
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model
        self._last_error_signature = None
        self._last_user_msg = None
        self._last_assistant_msg = None

    # ---------- DB helpers ----------
    def _conn(self):
        return sqlite3.connect(self.db_path)

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
    def _emei_system_prompt(self, user_pattern):
        # 유송이 원하는 방향: 사람같이 + 모르면 모른다 + 반복사과 금지
        formality = user_pattern.get("formality_level", "formal")
        # 말투는 서버 기본 페르소나(존댓말+가끔 반말)에 맞추되, 안전하게 존댓말 기본
        base = [
            "너는 '이메이(Emei)'다. 밝고 친근하지만, 과장하지 않는다.",
            "원칙: 확실하지 않으면 단정하지 말고 '지금 정보로는 확실히 모르겠어요'라고 말한 뒤, 확인 질문 1~2개를 한다.",
            "같은 사과/회피 문장을 연속으로 반복하지 않는다. 오류가 나면 원인(추정) 1개 + 해결 시도 1개를 제시한다.",
            "트레이딩은 조언이 아니라 정보 정리/지표 설명/시나리오로 답한다. 실행(매수/매도)은 별도 엔진이 한다.",
        ]
        if formality == "casual":
            base.append("말투는 너무 딱딱하지 않게, 필요하면 짧게 반말 섞어도 된다.")
        else:
            base.append("말투는 존댓말을 기본으로 한다.")
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

    def chat(self, user_id: str, message: str):
        t0 = time.time()
        user_id = user_id or "anonymous"
        message = _norm(message)

        # 사용자 패턴 업데이트
        self._update_user_pattern(user_id, message)
        pattern = self._get_user_pattern(user_id)

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

        system = self._emei_system_prompt(pattern)

        try:
            # temperature 상향 조정으로 캐시 응답 방지 (0.25 → 0.4)
            llm = self._ollama_chat(system=system, user=message, context_blocks=context_blocks, temperature=0.4)
            llm = self._style_postprocess(llm, pattern)

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
            # 에러가 반복되면 사과만 하지 말고 해결 가이드
            if sig == self._last_error_signature:
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
                    resp = (
                        f"🔧 로컬 AI 연결 문제가 있어요.\n\n"
                        f"오류: {sig[:100]}\n\n"
                        "**해결:** 노트북 터널 URL 확인 → `./update_ollama_url.sh` 실행\n"
                        "**지금:** DB 기반 답변만 가능 (기본 대화는 OK!) 💜"
                    )
            self._last_error_signature = sig
            self._log_conversation(user_id, message, resp, learned=0)
            return {"response": resp, "learned": False, "response_time": round(time.time() - t0, 4)}
