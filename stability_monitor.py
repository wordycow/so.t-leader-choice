#!/usr/bin/env python3
"""
안정성 모니터링 시스템
- 5분마다 시스템 상태 체크
- 이상 감지 시 알림
- 로그 기록
"""
import sqlite3
import json
import time
from datetime import datetime

class StabilityMonitor:
    def __init__(self):
        self.db_path = 'upbit_bot.db'
        self.log_file = 'stability_monitor.log'
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(self.log_file, 'a') as f:
            f.write(log_line + '\n')
    
    def check_data_integrity(self):
        """데이터 무결성 검사"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        issues = []
        
        # 1. bot_states 체크
        cursor.execute("SELECT simulation_krw, simulation_holdings, seed_amount FROM bot_states WHERE user_id = 'wordycow'")
        result = cursor.fetchone()
        
        if result:
            krw, holdings_json, seed = result
            holdings = json.loads(holdings_json)
            
            # 보유 코인이 없는데 KRW가 seed와 다르면 이상
            if len(holdings) == 0 and krw != seed:
                issues.append(f"❌ 보유 코인 없는데 현금 변동: {krw:,}원 (시드: {seed:,}원)")
        
        # 2. 거래 내역 체크
        cursor.execute("SELECT COUNT(*) FROM trades WHERE user_id = 'wordycow'")
        trade_count = cursor.fetchone()[0]
        
        if len(holdings) > 0 and trade_count == 0:
            issues.append(f"❌ 거래 내역 없는데 코인 보유")
        
        conn.close()
        
        return issues
    
    def check_bot_status(self):
        """봇 실행 상태 체크"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT running, last_update FROM bot_states WHERE user_id = 'wordycow'")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return ["❌ bot_states 데이터 없음"]
        
        running, last_update = result
        
        issues = []
        if not running:
            issues.append("⚠️ 봇 중지됨")
        
        # last_update가 10분 이상 오래되면 이상
        if last_update:
            try:
                update_time = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S.%f')
                diff = (datetime.now() - update_time).total_seconds()
                if diff > 600:  # 10분
                    issues.append(f"⚠️ 마지막 업데이트 {int(diff/60)}분 전")
            except:
                pass
        
        return issues
    
    def run_check(self):
        """전체 검사 실행"""
        self.log("=" * 50)
        self.log("🔍 안정성 검사 시작")
        
        # 데이터 무결성
        data_issues = self.check_data_integrity()
        if data_issues:
            self.log("❌ 데이터 무결성 문제:")
            for issue in data_issues:
                self.log(f"  {issue}")
        else:
            self.log("✅ 데이터 무결성 정상")
        
        # 봇 상태
        bot_issues = self.check_bot_status()
        if bot_issues:
            self.log("⚠️ 봇 상태 문제:")
            for issue in bot_issues:
                self.log(f"  {issue}")
        else:
            self.log("✅ 봇 상태 정상")
        
        return len(data_issues) == 0 and len(bot_issues) == 0
    
    def monitor_loop(self, interval=300):
        """모니터링 루프 (기본 5분)"""
        self.log(f"🚀 안정성 모니터 시작 (체크 간격: {interval}초)")
        
        while True:
            try:
                is_stable = self.run_check()
                if is_stable:
                    self.log("✅ 시스템 안정")
                else:
                    self.log("🚨 시스템 불안정!")
                
                time.sleep(interval)
            except KeyboardInterrupt:
                self.log("⏹️ 모니터 중지")
                break
            except Exception as e:
                self.log(f"❌ 오류: {e}")
                time.sleep(interval)

if __name__ == '__main__':
    monitor = StabilityMonitor()
    
    # 즉시 체크
    monitor.run_check()
    
    print("\n계속 모니터링하려면 'python3 stability_monitor.py monitor'")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        monitor.monitor_loop()
