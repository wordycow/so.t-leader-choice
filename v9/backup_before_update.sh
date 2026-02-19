#!/bin/bash
# 업데이트 전 자동 백업 스크립트
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="runtime/backup/snapshot_${TIMESTAMP}"

echo "🔄 Creating backup snapshot: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

# 1. 핵심 런타임 데이터 백업
cp -r runtime/*.json "${BACKUP_DIR}/" 2>/dev/null || true
cp imei_memory.db "${BACKUP_DIR}/" 2>/dev/null || true

# 2. 현재 코드 상태 저장
git diff HEAD > "${BACKUP_DIR}/uncommitted_changes.patch"
git log -1 --format="%H %s" > "${BACKUP_DIR}/last_commit.txt"

# 3. 실행 중인 프로세스 정보
ps aux | grep -E "(signal_engine|execution_engine|dashboard|imei_system)" | grep -v grep > "${BACKUP_DIR}/running_processes.txt"

# 4. 백업 메타데이터
cat > "${BACKUP_DIR}/backup_info.json" << INNER_EOF
{
  "timestamp": "${TIMESTAMP}",
  "git_commit": "$(git rev-parse HEAD)",
  "git_branch": "$(git branch --show-current)",
  "backup_reason": "pre_update_snapshot"
}
INNER_EOF

echo "✅ Backup completed: ${BACKUP_DIR}"
ls -lh "${BACKUP_DIR}"
