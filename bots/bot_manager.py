# -*- coding: utf-8 -*-
"""
Lee May Training Center - Bot Manager
모든 봇을 제어하는 중앙 관리 시스템
"""

import psutil
import subprocess
import json
import time
import os
from pathlib import Path

class BotManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.pids_file = self.base_dir / "data" / "pids.json"
        self.pids = self.load_pids()
    
    def start_bot(self, bot_name):
        """봇 시작"""
        # 이미 실행 중인지 체크
        if self.is_running(bot_name):
            return {
                "success": False,
                "error": f"{bot_name}이(가) 이미 실행 중입니다"
            }
        
        try:
            # 봇 경로 찾기
            bot_paths = {
                "leemay_api": self.base_dir / "bots/leemay/leemay_api.py",
                "trading_bot": self.base_dir / "bots/trading/trading_bot.py",
                "youtube_learner": self.base_dir / "bots/leemay/youtube_learner.py"
            }
            
            if bot_name not in bot_paths:
                return {"success": False, "error": "알 수 없는 봇"}
            
            bot_path = bot_paths[bot_name]
            
            # 봇 실행
            process = subprocess.Popen(
                ["python3", str(bot_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # PID 저장
            self.pids[bot_name] = {
                "pid": process.pid,
                "started": time.time(),
                "path": str(bot_path)
            }
            self.save_pids()
            
            return {
                "success": True,
                "pid": process.pid,
                "message": f"{bot_name} 시작됨"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_bot(self, bot_name):
        """봇 중지"""
        if not self.is_running(bot_name):
            return {
                "success": False,
                "error": f"{bot_name}이(가) 실행 중이 아닙니다"
            }
        
        try:
            pid = self.pids[bot_name]["pid"]
            process = psutil.Process(pid)
            
            # 정상 종료 시도
            process.terminate()
            time.sleep(1)
            
            # 강제 종료 (안 죽으면)
            if psutil.pid_exists(pid):
                process.kill()
            
            # PID 삭제
            del self.pids[bot_name]
            self.save_pids()
            
            return {
                "success": True,
                "message": f"{bot_name} 종료됨"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def restart_bot(self, bot_name):
        """봇 재시작"""
        self.stop_bot(bot_name)
        time.sleep(1)
        return self.start_bot(bot_name)
    
    def is_running(self, bot_name):
        """봇 실행 여부 확인"""
        if bot_name not in self.pids:
            return False
        
        pid = self.pids[bot_name]["pid"]
        return psutil.pid_exists(pid)
    
    def get_status(self):
        """모든 봇 상태 확인"""
        status = {}
        
        for bot_name in ["leemay_api", "trading_bot", "youtube_learner"]:
            if bot_name in self.pids and self.is_running(bot_name):
                pid = self.pids[bot_name]["pid"]
                try:
                    process = psutil.Process(pid)
                    status[bot_name] = {
                        "running": True,
                        "pid": pid,
                        "cpu": round(process.cpu_percent(), 1),
                        "memory": round(process.memory_percent(), 1),
                        "uptime": int(time.time() - self.pids[bot_name]["started"])
                    }
                except:
                    status[bot_name] = {"running": False}
            else:
                status[bot_name] = {"running": False}
        
        return status
    
    def load_pids(self):
        """PID 파일 로드"""
        try:
            if self.pids_file.exists():
                with open(self.pids_file) as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_pids(self):
        """PID 파일 저장"""
        self.pids_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pids_file, "w") as f:
            json.dump(self.pids, f, indent=2)

# 테스트
if __name__ == "__main__":
    manager = BotManager()
    print("Bot Manager 테스트")
    print("현재 상태:", manager.get_status())
