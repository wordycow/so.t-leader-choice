# 🔑 API 키 설정 가이드 (로컬 전용)

## 📋 전체 과정 (5분)

### 1️⃣ 업비트 API 키 발급 (2분)

1. **업비트 웹사이트 접속**
   - URL: https://upbit.com
   - 로그인 (본인인증 완료된 계정)

2. **API 관리 페이지 이동**
   - 우측 상단 **프로필 아이콘** 클릭
   - **Open API 관리** 클릭
   - 또는 직접: https://upbit.com/mypage/open_api_management

3. **API 키 발급**
   - **"Open API Key 발급"** 버튼 클릭
   - **권한 설정** (⚠️ 중요!):
     ```
     ✅ 자산 조회 (Assets: View)
     ✅ 주문 조회 (Orders: View)  
     ✅ 주문 하기 (Orders: Trade)
     ❌ 출금 하기 (Withdraws) ⛔ 절대 체크 금지!
     ```
   - OTP 인증
   - **API 키 발급 완료**

4. **API 키 복사**
   ```
   Access Key: abcd1234efgh5678...
   Secret Key: wxyz9876stuv5432...
   ```
   ⚠️ **Secret Key는 딱 한 번만 보여줍니다!** 즉시 복사하세요!

---

### 2️⃣ API 키 파일 생성 (1분)

봇이 있는 폴더에서:

```bash
cd /home/user/webapp
nano api_keys.json
```

다음 내용을 **복사해서 붙여넣고**, 실제 키로 변경:

```json
{
  "access_key": "abcd1234efgh5678ijklmnopqrstuvwx",
  "secret_key": "wxyz9876stuv5432qrstuvwxyzabcdef"
}
```

**저장**:
- `Ctrl + O` (저장)
- `Enter` (확인)
- `Ctrl + X` (종료)

---

### 3️⃣ 파일 권한 설정 (보안 강화)

```bash
# api_keys.json을 본인만 읽을 수 있도록
chmod 600 api_keys.json

# 확인
ls -la api_keys.json
# 출력: -rw------- (본인만 읽기/쓰기 가능)
```

---

### 4️⃣ 봇 실행

```bash
python3 upbit-smart-bot.py
```

---

## 🔒 보안 수칙

### ✅ 해야 할 것:
- API 키 파일(`api_keys.json`)은 **로컬에만 보관**
- 파일 권한을 `600`으로 설정 (본인만 접근)
- 정기적으로 API 키 재발급 (1-3개월마다)
- 출금 권한은 **절대 부여 금지**

### ❌ 하지 말아야 할 것:
- API 키를 GitHub/공개 저장소에 업로드
- 다른 사람과 API 키 공유
- 출금 권한 부여
- API 키를 코드에 직접 입력

---

## 📁 파일 구조

```
/home/user/webapp/
├── upbit-smart-bot.py       # 메인 봇 (이 파일이 api_keys.json 읽음)
├── api_keys.json             # API 키 저장 (Git에 올리지 않음!)
├── bot.log                   # 실행 로그
└── .gitignore                # api_keys.json 차단
```

---

## 🚨 문제 해결

### "api_keys.json 파일이 없습니다"
```bash
# 파일 존재 확인
ls -la api_keys.json

# 없으면 생성
nano api_keys.json
# (위 2️⃣ 단계 참고)
```

### "API 키 로드 실패"
```bash
# 파일 내용 확인
cat api_keys.json

# JSON 형식이 올바른지 확인
python3 -m json.tool api_keys.json
```

### "API 키가 비어있습니다"
- `api_keys.json` 파일에서 `"여기에_실제..."` 부분을 실제 키로 변경했는지 확인

### "권한 거부" 오류
```bash
# 파일 권한 확인
ls -la api_keys.json

# 권한 수정
chmod 600 api_keys.json
```

---

## 💡 참고

### API 키 테스트
```python
import pyupbit

access = "your_access_key"
secret = "your_secret_key"

upbit = pyupbit.Upbit(access, secret)
balance = upbit.get_balance("KRW")
print(f"보유 원화: {balance:,.0f}원")
```

### API 키 재발급
1. 업비트 → Open API 관리
2. 기존 키 **삭제**
3. 새로운 키 **발급**
4. `api_keys.json` 파일 **업데이트**

---

**✅ 설정 완료 후 봇 실행: `python3 upbit-smart-bot.py`**
