import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
import json
import webbrowser
from datetime import datetime

class UpbitBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 업비트 스마트 봇 v5.0 - 설정 및 실행")
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        
        # 봇 프로세스
        self.bot_process = None
        self.bot_running = False
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.check_requirements()
    
    def setup_ui(self):
        """UI 구성"""
        
        # 헤더
        header_frame = tk.Frame(self.root, bg='#667eea', height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🤖 업비트 스마트 봇 v5.0", 
                        font=('맑은 고딕', 20, 'bold'), bg='#667eea', fg='white')
        title.pack(pady=10)
        
        subtitle = tk.Label(header_frame, text="웹 대시보드 + 수익 분산 투자 (SOL, XRP, BTC, HBAR)", 
                           font=('맑은 고딕', 10), bg='#667eea', fg='white')
        subtitle.pack()
        
        # 메인 컨테이너
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # === 1단계: 시스템 확인 ===
        step1_frame = tk.LabelFrame(main_frame, text="1️⃣ 시스템 확인", font=('맑은 고딕', 12, 'bold'), padx=10, pady=10)
        step1_frame.pack(fill='x', pady=10)
        
        self.status_label = tk.Label(step1_frame, text="확인 중...", font=('맑은 고딕', 10))
        self.status_label.pack(anchor='w')
        
        self.check_btn = ttk.Button(step1_frame, text="🔄 다시 확인", command=self.check_requirements)
        self.check_btn.pack(anchor='w', pady=5)
        
        # === 2단계: API 키 설정 ===
        step2_frame = tk.LabelFrame(main_frame, text="2️⃣ 업비트 API 키 설정", font=('맑은 고딕', 12, 'bold'), padx=10, pady=10)
        step2_frame.pack(fill='x', pady=10)
        
        # API 키 발급 안내
        guide_text = tk.Label(step2_frame, 
                             text="📋 API 키가 없으신가요? 아래 버튼을 클릭하세요!", 
                             font=('맑은 고딕', 9), fg='#666')
        guide_text.pack(anchor='w', pady=5)
        
        guide_btn = ttk.Button(step2_frame, text="📖 API 키 발급 방법 보기", command=self.show_api_guide)
        guide_btn.pack(anchor='w', pady=5)
        
        upbit_btn = ttk.Button(step2_frame, text="🌐 업비트 API 관리 페이지 열기", command=self.open_upbit)
        upbit_btn.pack(anchor='w', pady=5)
        
        tk.Label(step2_frame, text="").pack()  # 공백
        
        # Access Key
        tk.Label(step2_frame, text="Access Key:", font=('맑은 고딕', 10, 'bold')).pack(anchor='w')
        self.access_key_entry = tk.Entry(step2_frame, font=('맑은 고딕', 10), width=60)
        self.access_key_entry.pack(fill='x', pady=5)
        
        # Secret Key
        tk.Label(step2_frame, text="Secret Key:", font=('맑은 고딕', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        self.secret_key_entry = tk.Entry(step2_frame, font=('맑은 고딕', 10), width=60, show='*')
        self.secret_key_entry.pack(fill='x', pady=5)
        
        # 보기/숨기기 버튼
        show_btn = ttk.Button(step2_frame, text="👁 Secret Key 보기", command=self.toggle_secret_key)
        show_btn.pack(anchor='w', pady=5)
        
        # 저장 버튼
        save_btn = ttk.Button(step2_frame, text="💾 API 키 저장", command=self.save_api_keys)
        save_btn.pack(anchor='w', pady=10)
        
        self.api_status_label = tk.Label(step2_frame, text="", font=('맑은 고딕', 9))
        self.api_status_label.pack(anchor='w')
        
        # === 3단계: 봇 실행 ===
        step3_frame = tk.LabelFrame(main_frame, text="3️⃣ 봇 실행", font=('맑은 고딕', 12, 'bold'), padx=10, pady=10)
        step3_frame.pack(fill='x', pady=10)
        
        self.bot_status_label = tk.Label(step3_frame, text="⚪ 대기중", font=('맑은 고딕', 12, 'bold'))
        self.bot_status_label.pack(anchor='w', pady=10)
        
        btn_frame = tk.Frame(step3_frame)
        btn_frame.pack(fill='x')
        
        self.start_btn = ttk.Button(btn_frame, text="▶ 봇 시작", command=self.start_bot)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏸ 봇 중지", command=self.stop_bot, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.dashboard_btn = ttk.Button(btn_frame, text="🌐 대시보드 열기", command=self.open_dashboard, state='disabled')
        self.dashboard_btn.pack(side='left', padx=5)
        
        # === 로그 창 ===
        log_frame = tk.LabelFrame(main_frame, text="📜 실행 로그", font=('맑은 고딕', 12, 'bold'), padx=10, pady=10)
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=('Consolas', 9), bg='#f5f5f5')
        self.log_text.pack(fill='both', expand=True)
        
        # 하단 정보
        footer = tk.Label(self.root, text="v5.0.0 | © 2026 so.t Team | MIT License", 
                         font=('맑은 고딕', 8), fg='#999')
        footer.pack(pady=10)
        
        # API 키 로드 시도
        self.load_existing_api_keys()
    
    def log(self, message, level='INFO'):
        """로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        self.log_text.insert('end', log_message)
        self.log_text.see('end')
        self.root.update()
    
    def check_requirements(self):
        """시스템 요구사항 확인"""
        self.log("시스템 확인 시작...", "INFO")
        
        # Python 확인
        try:
            version = sys.version.split()[0]
            self.log(f"✅ Python {version} 감지됨", "SUCCESS")
            
            # 필수 패키지 확인
            required = ['pyupbit', 'pandas', 'numpy', 'flask', 'flask_cors']
            missing = []
            
            for package in required:
                try:
                    __import__(package)
                    self.log(f"✅ {package} 설치됨", "SUCCESS")
                except ImportError:
                    missing.append(package)
                    self.log(f"❌ {package} 없음", "WARNING")
            
            if missing:
                self.status_label.config(text=f"⚠️ 패키지 설치 필요: {', '.join(missing)}", fg='orange')
                if messagebox.askyesno("패키지 설치", 
                                      f"다음 패키지를 설치하시겠습니까?\n{', '.join(missing)}"):
                    self.install_packages(missing)
            else:
                self.status_label.config(text="✅ 모든 요구사항 충족!", fg='green')
                
        except Exception as e:
            self.log(f"❌ 오류: {e}", "ERROR")
            self.status_label.config(text="❌ 시스템 확인 실패", fg='red')
    
    def install_packages(self, packages):
        """패키지 설치"""
        self.log("패키지 설치 시작...", "INFO")
        
        for package in packages:
            try:
                self.log(f"📦 {package} 설치 중...", "INFO")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
                self.log(f"✅ {package} 설치 완료", "SUCCESS")
            except Exception as e:
                self.log(f"❌ {package} 설치 실패: {e}", "ERROR")
        
        self.log("패키지 설치 완료", "SUCCESS")
        self.check_requirements()
    
    def show_api_guide(self):
        """API 키 발급 가이드 표시"""
        guide = """
🔑 업비트 API 키 발급 방법

1️⃣ 업비트 로그인
   https://upbit.com

2️⃣ API 키 발급
   • 프로필 → Open API 관리
   • API 키 발급 클릭

3️⃣ 권한 설정 (매우 중요!)
   ✅ 자산조회 (필수)
   ✅ 주문조회 (필수)
   ✅ 주문하기 (필수)
   ❌ 출금하기 (절대 체크 금지!)

4️⃣ API 키 복사
   • Access Key: 복사 → 위에 붙여넣기
   • Secret Key: 복사 → 위에 붙여넣기
   (Secret Key는 한 번만 보임!)

5️⃣ 저장 버튼 클릭

⚠️ 보안 주의사항:
• API 키는 절대 다른 사람과 공유 금지
• 출금 권한은 절대 활성화 금지
• Secret Key는 안전하게 보관
"""
        messagebox.showinfo("API 키 발급 가이드", guide)
    
    def open_upbit(self):
        """업비트 API 관리 페이지 열기"""
        webbrowser.open("https://upbit.com/mypage/open_api_management")
        self.log("업비트 API 관리 페이지 열림", "INFO")
    
    def toggle_secret_key(self):
        """Secret Key 보기/숨기기"""
        if self.secret_key_entry.cget('show') == '*':
            self.secret_key_entry.config(show='')
        else:
            self.secret_key_entry.config(show='*')
    
    def load_existing_api_keys(self):
        """기존 API 키 로드"""
        try:
            if os.path.exists('api_keys.json'):
                with open('api_keys.json', 'r') as f:
                    keys = json.load(f)
                    self.access_key_entry.insert(0, keys.get('access_key', ''))
                    self.secret_key_entry.insert(0, keys.get('secret_key', ''))
                    self.api_status_label.config(text="✅ 기존 API 키 로드됨", fg='green')
                    self.log("기존 API 키 로드 완료", "SUCCESS")
        except Exception as e:
            self.log(f"API 키 로드 실패: {e}", "WARNING")
    
    def save_api_keys(self):
        """API 키 저장"""
        access_key = self.access_key_entry.get().strip()
        secret_key = self.secret_key_entry.get().strip()
        
        if not access_key or not secret_key:
            messagebox.showerror("오류", "Access Key와 Secret Key를 모두 입력하세요!")
            return
        
        if len(access_key) < 20 or len(secret_key) < 20:
            messagebox.showerror("오류", "API 키가 너무 짧습니다. 올바른 키를 입력하세요!")
            return
        
        try:
            with open('api_keys.json', 'w') as f:
                json.dump({
                    'access_key': access_key,
                    'secret_key': secret_key
                }, f, indent=2)
            
            self.api_status_label.config(text="✅ API 키 저장 완료!", fg='green')
            self.log("API 키 저장 완료", "SUCCESS")
            messagebox.showinfo("성공", "API 키가 저장되었습니다!\n이제 봇을 시작할 수 있습니다.")
        except Exception as e:
            self.api_status_label.config(text=f"❌ 저장 실패: {e}", fg='red')
            self.log(f"API 키 저장 실패: {e}", "ERROR")
            messagebox.showerror("오류", f"API 키 저장 실패:\n{e}")
    
    def start_bot(self):
        """봇 시작"""
        if not os.path.exists('api_keys.json'):
            messagebox.showerror("오류", "먼저 API 키를 설정하세요!")
            return
        
        if not os.path.exists('upbit-smart-bot-v5.py'):
            messagebox.showerror("오류", "upbit-smart-bot-v5.py 파일이 없습니다!")
            return
        
        try:
            self.log("봇 시작 중...", "INFO")
            
            # 봇 실행
            self.bot_process = subprocess.Popen(
                [sys.executable, 'upbit-smart-bot-v5.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.bot_running = True
            self.bot_status_label.config(text="🟢 실행중", fg='green')
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.dashboard_btn.config(state='normal')
            
            self.log("✅ 봇이 시작되었습니다!", "SUCCESS")
            self.log("🌐 웹 대시보드: http://localhost:5000", "INFO")
            
            # 5초 후 대시보드 자동 열기
            self.root.after(5000, self.open_dashboard)
            
            messagebox.showinfo("성공", 
                              "봇이 시작되었습니다!\n\n" +
                              "5초 후 웹 대시보드가 자동으로 열립니다.\n" +
                              "또는 '🌐 대시보드 열기' 버튼을 클릭하세요.")
            
        except Exception as e:
            self.log(f"❌ 봇 시작 실패: {e}", "ERROR")
            messagebox.showerror("오류", f"봇 시작 실패:\n{e}")
    
    def stop_bot(self):
        """봇 중지"""
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
                self.log("봇이 중지되었습니다", "INFO")
            except:
                self.bot_process.kill()
                self.log("봇이 강제 종료되었습니다", "WARNING")
            
            self.bot_running = False
            self.bot_status_label.config(text="⚪ 대기중", fg='gray')
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.dashboard_btn.config(state='disabled')
    
    def open_dashboard(self):
        """웹 대시보드 열기"""
        webbrowser.open("http://localhost:5000")
        self.log("웹 대시보드 열림", "INFO")
    
    def on_closing(self):
        """프로그램 종료 시"""
        if self.bot_running:
            if messagebox.askokcancel("종료", "봇이 실행 중입니다. 종료하시겠습니까?"):
                self.stop_bot()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UpbitBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
