# 📚 AI-MultiColony-Ecosystem Documentation

## Status Sistem
- Production-ready, modular, scalable, self-healing
- Semua agent, registry, CLI, dan Web UI terintegrasi

## Cara Install & Menjalankan
```bash
pip install -r requirements.txt
python main.py
# atau jalankan web-ui (lihat web-ui/README.md)
```

## Struktur Folder
```
AI-MultiColony-Ecosystem/
├── main.py
├── colony/
│   ├── agents/
│   ├── core/
│   ├── services/
│   └── api/
├── web-ui/
├── config/
├── tests/
├── docs/
├── archive/
├── requirements.txt
├── .env.example
└── README.md
```

## CLI & Web UI
- **main.py**: CLI all-in-one (run agent, chat, deploy, registry, dsb)
- **web-ui/**: Dashboard React+Vite real-time (agents, chat, deploy, settings, logs)

## Daftar Agent
- Semua agent otomatis terdaftar di registry global
- Tambah agent baru cukup dengan dekorator `@register_agent_class`
- Lihat `docs/AGENT_REGISTRY.md` untuk daftar lengkap

## Endpoint API
- `/api/agents` - List agent
- `/api/registry` - Registry info
- `/api/chat` - Chat WebSocket
- `/api/deploy` - Deploy
- `/api/settings` - Config

## Kontribusi
- Fork, buat branch, pull request ke main
- Jalankan lint/test sebelum push
- Semua perubahan terdokumentasi di `docs/CHANGELOG.md`

## Badge CI
![CI](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/actions/workflows/ci.yml/badge.svg)

## Kontak
- Email: support@ultimate-autonomous-ai.com
- Dashboard: http://localhost:8000

## Blueprint & Changelog
- [Blueprint Arsitektur](docs/BLUEPRINT.md)
- [Changelog](docs/CHANGELOG.md)