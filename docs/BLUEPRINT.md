# BLUEPRINT ARSITEKTUR

## Struktur Folder

```
AI-MultiColony-Ecosystem/
├── main.py                # Entrypoint CLI
├── colony/
│   ├── agents/            # Semua agent
│   ├── core/              # BaseAgent, registry, memory, scheduler
│   ├── services/          # Backend logic
│   └── api/               # Endpoint API (Flask/FastAPI)
├── web-ui/                # Frontend React+Vite
├── config/                # .env, config yaml
├── tests/                 # Testing
├── docs/                  # Dokumentasi
├── archive/               # Backup
├── requirements.txt
├── .env.example
└── README.md
```

## Alur Sistem

```
[CLI (main.py)]
    |
    v
[Agent Registry] <----> [Orchestrator]
    |                        |
    v                        v
[API Backend] <--------> [Agents]
    |
    v
[Web UI (web-ui/)] <---(WebSocket/API)---> [User]
```

- **main.py**: Entrypoint CLI, semua perintah agent, deploy, registry.
- **Agent Registry**: Semua agent auto-register, bisa diakses CLI & Web UI.
- **Orchestrator**: Mengelola lifecycle agent, workflow, self-healing.
- **API Backend**: Endpoint REST/WebSocket untuk Web UI & integrasi eksternal.
- **Web UI**: Dashboard real-time, kontrol agent, chat, deploy, settings, log.

## Modularitas
- Semua agent, core, dan service terpisah, mudah dikembangkan.
- Web UI dan backend terhubung via API, bisa diskalakan terpisah.
- Dokumentasi, changelog, dan blueprint auto-update.

> Sistem siap untuk ekspansi, self-healing, dan deployment production.