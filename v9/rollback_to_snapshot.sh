#!/bin/bash
# 롤백 스크립트
if [ -z "$1" ]; then
  echo "❌ Usage: ./rollback_to_snapshot.sh <snapshot_timestamp>"
  echo "Available snapshots:"
  ls -1 runtime/backup/ | grep snapshot_
  exit 1
fi

SNAPSHOT="runtime/backup/snapshot_$1"
if [ ! -d "$SNAPSHOT" ]; then
  echo "❌ Snapshot not found: $SNAPSHOT"
  exit 1
fi

echo "🔄 Rolling back to snapshot: $1"

# 1. 런타임 데이터 복원
cp -f "${SNAPSHOT}"/*.json runtime/ 2>/dev/null || true
cp -f "${SNAPSHOT}/imei_memory.db" . 2>/dev/null || true

# 2. Git 상태 복원
if [ -f "${SNAPSHOT}/last_commit.txt" ]; then
  COMMIT=$(head -1 "${SNAPSHOT}/last_commit.txt" | awk '{print $1}')
  echo "📌 Git commit to restore: $COMMIT"
  git reset --hard "$COMMIT"
fi

# 3. 미커밋 변경 사항 적용
if [ -f "${SNAPSHOT}/uncommitted_changes.patch" ] && [ -s "${SNAPSHOT}/uncommitted_changes.patch" ]; then
  git apply "${SNAPSHOT}/uncommitted_changes.patch" || echo "⚠️ Could not apply uncommitted changes"
fi

echo "✅ Rollback completed"
echo "⚠️ Please restart services manually: cd v9 && ./시작.bat"
