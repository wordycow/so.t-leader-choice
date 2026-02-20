' Lee May Training Center - 스텔스 시작
' 모든 프로세스를 백그라운드(창 없음)로 실행

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 현재 스크립트 경로
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' ============================================================
' 1. Lee May API 서버 시작 (백그라운드)
' ============================================================
strAPICommand = "cmd /c cd /d """ & strScriptPath & """ && python api_server.py"
objShell.Run strAPICommand, 0, False

' 2초 대기
WScript.Sleep 2000

' ============================================================
' 2. Ollama Tunnel 시작 (백그라운드)
' ============================================================
strTunnelCommand = "cmd /c cloudflared tunnel run ollama-stable"
objShell.Run strTunnelCommand, 0, False

' 1초 대기
WScript.Sleep 1000

' ============================================================
' 완료 알림 (토스트 형태)
' ============================================================
objShell.Popup "Lee May Training Center 시작 완료!" & vbCrLf & vbCrLf & _
               "접속: http://localhost:5001" & vbCrLf & _
               "외부: https://leemay.더유니크.com" & vbCrLf & vbCrLf & _
               "종료: LeeMay_STOP.bat 실행", _
               5, "Lee May Training Center", 64

Set objShell = Nothing
Set objFSO = Nothing
