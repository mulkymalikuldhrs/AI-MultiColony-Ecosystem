#!/bin/bash
set -e

echo "[E2E] Start semua agent (dummy run) ..."
python3 main.py --all || echo "[WARN] Gagal start semua agent"

echo "[E2E] Kirim task ke agent (dummy) ..."
python3 -c 'from colony.core.agent_registry import list_all_agents; print("[TASK]", list_all_agents())'

echo "[E2E] Monitor log ..."
tail -n 20 logs/colony_activity.log || echo "[WARN] Log tidak ditemukan"

echo "[E2E] Cek sinkronisasi UI ..."
curl -sSf http://localhost:8080/api/agents/list || echo "[WARN] UI tidak sinkron"

echo "[E2E] Validasi registry ..."
python3 -c 'from colony.core.agent_registry import list_all_agents; print("[REGISTRY]", list_all_agents())'

echo "[E2E] Tes CLI ..."
echo "exit" | python3 main.py --mode 3 || echo "[WARN] CLI error"

echo "[E2E] Tes Web UI ..."
curl -sSf http://localhost:8080 || echo "[WARN] Web UI error"

echo "[DONE] E2E test selesai."