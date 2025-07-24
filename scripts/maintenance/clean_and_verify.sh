#!/bin/bash
set -e

# 1. Hapus file duplikat/sampah
echo "[CLEAN] Menghapus file *.swp dan *.copy.py ..."
find . -type f \( -name '*.swp' -o -name '*.copy.py' \) -delete

echo "[VERIFY] Memverifikasi agent registry ..."
python3 -c 'from colony.core.agent_registry import list_all_agents; print("[AGENTS]", list_all_agents())'

echo "[TEST] Menjalankan API endpoint test ..."
if command -v curl >/dev/null 2>&1; then
  curl -sSf http://localhost:8080/api/agents/list || echo "[WARN] API tidak merespon"
else
  echo "[SKIP] curl tidak ditemukan, lewati tes API"
fi

echo "[VALIDATE] Memvalidasi .env dan config ..."
if [ -f .env ]; then
  echo "[OK] .env ditemukan"
else
  echo "[WARN] .env tidak ditemukan"
fi
if [ -f config/system_config.yaml ]; then
  echo "[OK] config/system_config.yaml ditemukan"
else
  echo "[WARN] config/system_config.yaml tidak ditemukan"
fi

echo "[DONE] Maintenance selesai."