[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=2E9EF7&center=true&vCenter=true&width=800&lines=AI-MultiColony-Ecosystem;Platform+Koordinasi+Koloni+Multi-Agent;v8.0.0+oleh+Mulky+Malikul+Dhaher)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem)

<p align="center">
  <img src="https://img.shields.io/badge/versi-8.0.0-gold?style=for-the-badge&logo=semver" alt="Versi 8.0.0"/>
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/multi--agent-40%2B-FF6F00?style=for-the-badge&logo=robotframework&logoColor=white" alt="40+ Agen"/>
  <img src="https://img.shields.io/badge/lisensi-MIT-green?style=for-the-badge" alt="Lisensi MIT"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-Dashboard-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js"/>
</p>

<p align="center">
  <a href="./README.md">🇬🇧 English</a> |
  <a href="./README_id.md">🇮🇩 Bahasa Indonesia</a> |
  <a href="./README_zh.md">🇨🇳 中文</a>
</p>

---

## Ikhtisar

**AI-MultiColony-Ecosystem** adalah platform koordinasi koloni multi-agent terdepan yang dirancang untuk mengorkestrasi puluhan agen AI khusus dalam ekosistem terpadu dan kolaboratif. Dibangun oleh [Mulky Malikul Dhaher](https://github.com/mulkymalikuldhrs), platform ini menyediakan kerangka kerja yang kokoh untuk menyebarkan, mengelola, dan mengoordinasikan agen-agen cerdas di berbagai domain termasuk pengembangan perangkat lunak otonom, perdagangan keuangan, otomasi web, pemantauan keamanan, dan lainnya.

Pada intinya, ekosistem mengikuti **metafora koloni** — setiap agen beroperasi sebagai anggota khusus dari koloni yang lebih besar, berkomunikasi melalui bus memori bersama, dikoordinasikan oleh registri agen pusat, dan diorkestrasi melalui penjadwal dan manajer daemon. Platform ini terintegrasi dengan kerangka kerja AI terkemuka (CAMEL AI, AutoGen, CrewAI, LangGraph) dan menyediakan dasbor web modern yang dibangun dengan Next.js dan FastAPI untuk pemantauan dan kontrol secara real-time.

Arsitektur sistem mendukung pembuatan agen dinamis, loop otonom yang memperbaiki diri, akses LLM multi-provider melalui gateway terpadu, dan konektor yang dapat diperluas untuk alat Model Context Protocol (MCP). Baik Anda membangun sistem perdagangan otonom, pipeline pengembangan bertenaga AI, atau platform riset multi-agent, AI-MultiColony-Ecosystem menyediakan infrastruktur dasar untuk mewujudkannya.

> **Proyek Terkait**: [HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) — Sistem operasi perdagangan kuantitatif siap produksi yang dibangun dengan ekosistem ini.

---

## Arsitektur

AI-MultiColony-Ecosystem diorganisasikan menjadi lima lapisan utama, yang masing-masing bertanggung jawab atas aspek kritis dari operasi platform. Lapisan-lapisan ini bekerja sama untuk memberikan pengalaman yang mulus dari pembuatan agen hingga penerapan dan pemantauan.

### Inti Koloni (Colony Core)

Inti Koloni adalah sistem saraf pusat dari platform. Ia mengelola seluruh siklus hidup agen, dari registrasi dan penemuan hingga penjadwalan dan manajemen memori. Komponen-komponen kunci meliputi:

| Komponen | File | Deskripsi |
|----------|------|-----------|
| **Registri Agen** | `colony/core/agent_registry.py` | Sistem registrasi berbasis dekorator yang menemukan dan mengatalogkan semua kelas agen secara otomatis. Mendukung metadata, rute API, dan pelacakan dependensi. |
| **Agen Dasar** | `colony/core/base_agent.py` | Kelas dasar abstrak yang diwarisi semua agen. Menyediakan manajemen status, penanganan kesalahan, persistensi output, validasi tugas, dan kait siklus hidup (`run`, `process_task`, `stop`, `restart`). |
| **Manajer Agen** | `colony/core/agent_manager.py` | Mengorkestrasi eksekusi agen, mengelola instance agen, menangani komunikasi antar-agen, dan menyediakan kontrol agen terpusat. |
| **Registri Agen Terpadu** | `colony/core/unified_agent_registry.py` | Registri yang ditingkatkan dengan metode pabrik untuk pembuatan agen dinamis, manajemen instance, dan penemuan agen lintas-koloni. |
| **Penjadwal** | `colony/core/scheduler.py` | Mesin penjadwalan tugas yang mendukung pola cron-like, antrian prioritas, tugas berulang, dan urutan eksekusi berbasis dependensi. |
| **Bus Memori** | `colony/core/memory_bus.py` | Tulang punggung komunikasi bersama yang memungkinkan agen bertukar pesan, berbagi status, dan mengoordinasikan aktivitas secara real-time. |
| **Manajer Daemon** | `colony/core/daemon_manager.py` | Mengelola proses latar belakang yang berjalan lama (daemon), pemeriksaan kesehatan, restart otomatis, dan pemantauan sumber daya. |
| **Pemuat Konfigurasi** | `colony/core/config_loader.py` | Sistem konfigurasi berbasis YAML dengan interpolasi variabel lingkungan, validasi, dan dukungan hot-reload. |
| **Master Prompt** | `colony/core/prompt_master.py` | Sistem manajemen dan rekayasa prompt tingkat lanjut untuk interaksi LLM yang dioptimalkan di seluruh agen. |
| **Bootstrap Sistem** | `colony/core/system_bootstrap.py` | Urutan inisialisasi startup yang memuat konfigurasi, menginisialisasi database, mendaftarkan agen, dan memulai layanan sistem. |
| **Mesin Pelaporan** | `colony/core/reporting/` | Subsistem pengumpulan hasil, validasi, resolusi konflik, pembuatan laporan, dan penyimpanan output. |

### Agen Koloni (Colony Agents)

Platform ini dilengkapi dengan 40+ agen khusus, masing-masing dirancang untuk domain tertentu. Agen mewarisi dari `BaseAgent` dan ditemukan secara otomatis oleh registri. Agen-agen kunci meliputi:

| Kategori | Agen Kunci | Deskripsi |
|----------|-----------|-----------|
| **Komando & Kontrol** | `commander_agi` | Pemantauan keamanan, deteksi ancaman, pelacakan kesehatan sistem, dan koordinasi misi agen dengan kemampuan respons otonom. |
| **Perdagangan & Keuangan** | `smart_money_trading_agent`, `money_making_agent`, `money_making_orchestrator` | Perdagangan berbasis Smart Money Concepts (SMC) dan ICT dengan analisis order block, deteksi fair value gap, pemetaan likuiditas, dan pemindaian konfluensi multi-timeframe. |
| **Pengembangan** | `autonomous_fullstack_dev_agent`, `fullstack_dev`, `fullstack_agent`, `dev_engine` | Pembuatan kode otonom, analisis sistem, loop peningkatan berkelanjutan, dan pengembangan mandiri dengan kemampuan riset. |
| **Otomasi Web** | `web_automation_agent`, `cybershell` | Otomasi browser berbasis Selenium, manajemen kredensial, pengisian formulir, otomasi login/registrasi, dan interaksi web. |
| **Pembuatan Agen** | `dynamic_agent_factory`, `enhanced_agent_creator`, `meta_agent_creator`, `agent_maker` | Pembuatan agen runtime dari template, injeksi kapabilitas dinamis, dan manajemen cetak biru agen. |
| **Operasi** | `deployment_agent`, `deploy_manager`, `auto_deployment_system` | Pipeline penerapan otomatis, manajemen layanan, dan penyediaan infrastruktur. |
| **Keamanan** | `authentication_agent`, `credential_manager`, `auto_redactor_agent` | Penyimpanan kredensial, alur autentikasi, redaksi data sensitif, dan penegakan kebijakan keamanan. |
| **Riset & AI** | `ai_research_agent`, `knowledge_management_agent`, `camel_agent_integration` | Otomasi riset AI, pengelolaan basis pengetahuan, dan penalaran kolaboratif CAMEL AI. |
| **Desain & UI** | `ui_designer`, `agent_05_designer` | Pembuatan desain UI/UX, pembuatan komponen, dan pengembangan antarmuka visual. |
| **Sistem** | `system_supervisor`, `system_optimizer`, `autonomous_maintainer`, `bug_hunter_bot` | Pemantauan kesehatan sistem, optimasi kinerja, pemeliharaan otomatis, dan deteksi bug. |

### API Koloni (Colony API)

Lapisan API Koloni menyediakan endpoint RESTful dan WebSocket untuk berinteraksi dengan ekosistem:

- **Backend FastAPI / Flask** (`colony/api/app.py`) — Server API berkinerja tinggi dengan pembuatan endpoint dinamis dari registri agen
- **Server WebSocket** (`colony/api/websocket.py`) — Komunikasi bidireksional real-time untuk pembaruan langsung dan streaming
- **Launcher API** (`colony/api/launcher_api.py`) — Endpoint kontrol sistem untuk memulai, menghentikan, dan mengelola agen
- **Endpoint Agen** (`colony/api/endpoints/agents.py`, `tasks.py`, `agent_creator.py`) — Operasi CRUD untuk agen dan tugas
- **API Chat** — `/api/chat/message`, `/api/chat/history`, `/api/chat/clear` untuk interaksi AI percakapan
- **API Sistem** — `/api/system/status`, `/api/system/emergency-stop`, `/api/system/restart-all` untuk manajemen sistem
- **API Memori** — `/api/memory/stats` untuk statistik bus memori bersama

### Integrasi Koloni (Colony Integrations)

Platform ini terintegrasi dengan kerangka kerja AI dan cloud terkemuka:

| Integrasi | File | Deskripsi |
|-----------|------|-----------|
| **CAMEL AI** | `colony/integrations/camel_ai_integration.py` | Penalaran kolaboratif multi-agent, percakapan bermain peran, dan pemecahan tugas kooperatif |
| **AutoGen** | `colony/integrations/autogen_integration.py` | Kerangka kerja percakapan multi-agent Microsoft untuk tugas penalaran kompleks |
| **CrewAI** | `colony/integrations/crewai_integration.py` | Kru agen berbasis peran dengan eksekusi tugas sekuensial dan paralel |
| **LangGraph** | `colony/integrations/langgraph_integration.py` | Alur kerja agen berbasis graf dengan eksekusi stateful dan perutean kondisional |
| **Supabase** | `colony/integrations/supabase_integration.py` | Database cloud, autentikasi, dan langganan real-time |
| **Netlify** | `colony/integrations/netlify_integration.py` | Penerapan web otomatis dan integrasi hosting |

### Antarmuka Web

Dasbor Next.js menyediakan panel kontrol modern dan responsif:

- **Dasbor** — Pemantauan sistem real-time, status agen, dan metrik kinerja
- **Manajer Agen** — Jelajahi, buat, konfigurasi, dan kontrol semua agen terdaftar
- **Antarmuka Chat** — AI percakapan dengan perutean multi-agent dan manajemen konteks
- **Pembuat Agen** — Pembuatan agen dinamis dari template dengan kustomisasi kapabilitas
- **Panel Penerapan** — Penerapan satu klik dengan konfigurasi lingkungan
- **Pemantauan** — Kesehatan sistem, penggunaan sumber daya, dan manajemen peringatan
- **Brankas Kredensial** — Manajemen kredensial aman dengan penyimpanan terenkripsi
- **Integrasi Platform** — Konfigurasi CAMEL AI, AutoGen, CrewAI, LangGraph, dan penyedia cloud
- **Dukungan PWA** — Progressive Web App dengan kemampuan offline dan notifikasi push

### Konektor

| Konektor | File | Deskripsi |
|----------|------|-----------|
| **Konektor MCP** | `connectors/mcp_connector.py` | Klien Model Context Protocol untuk terhubung ke server MCP, mengakses alat/sumber/daya/prompt melalui WebSocket |
| **Gateway LLM** | `connectors/llm_gateway.py` | Akses LLM multi-provider dengan failover otomatis, penyeimbangan beban, dan pelacakan penggunaan. Mendukung LLM7, OpenRouter, dan provider kustom |

---

## Fitur Utama

- **Koordinasi Agen Gaya Koloni** — Agen beroperasi sebagai anggota khusus dari koloni, berkomunikasi melalui bus memori bersama dan dikoordinasikan oleh registri terpadu. Ini memungkinkan kecerdasan kolektif yang muncul di mana agen berkolaborasi pada tugas kompleks yang tidak dapat ditangani oleh satu agen pun.

- **Pabrik Agen Dinamis** — Buat agen baru saat runtime dari template atau dari awal menggunakan pembuat agen yang ditingkatkan. Sistem pabrik mendukung injeksi kapabilitas, pewarisan template, dan konfigurasi runtime, memungkinkan Anda untuk dengan cepat membuat prototipe dan menyebarkan tipe agen baru tanpa memodifikasi kode inti.

- **Integrasi Multi-Framework** — Integrasikan dengan mulus dengan CAMEL AI untuk penalaran kolaboratif, AutoGen untuk jaringan agen percakapan, CrewAI untuk kru berbasis peran, dan LangGraph untuk alur kerja graf stateful. Beralih antara kerangka kerja atau menggabungkannya berdasarkan persyaratan tugas Anda.

- **Mesin Perdagangan Smart Money** — Agen perdagangan Smart Money Concepts (SMC) dan ICT bawaan menyediakan analisis pasar tingkat institusi termasuk identifikasi order block, deteksi fair value gap, pemetaan pool likuiditas, dan pemindaian konfluensi multi-timeframe dengan manajemen risiko yang dapat dikonfigurasi.

- **Gateway LLM Terpadu** — Akses beberapa provider LLM (LLM7, OpenRouter, OpenAI, endpoint kustom) melalui antarmuka tunggal dengan failover otomatis, pembatasan tarif, pelacakan token, dan pemantauan kesehatan provider. Tidak perlu lagi khawatir tentang gangguan provider.

- **Konektor MCP** — Terhubung ke server Model Context Protocol untuk mengakses alat, sumber daya, dan prompt eksternal. Konektor menangani siklus hidup MCP lengkap termasuk inisialisasi, penemuan kapabilitas, dan pemanggilan alat.

- **Dasbor Web Real-Time** — Pantau seluruh koloni Anda dari dasbor Next.js modern dengan pembaruan status agen langsung melalui WebSocket, chat interaktif, metrik kesehatan sistem, dan kontrol penerapan satu klik. Berfungsi sebagai PWA untuk akses mobile.

- **Peningkatan Diri Otonom** — Agen pengembangan otonom secara terus-menerus menganalisis sistem, mengidentifikasi peluang peningkatan, melakukan riset, dan mengeksekusi peningkatan — menciptakan ekosistem yang berevolusi sendiri yang semakin baik seiring waktu.

- **Desain Utama Keamanan** — Commander AGI menyediakan pemantauan keamanan real-time, deteksi ancaman, dan respons otonom. Manajemen kredensial dengan penyimpanan terenkripsi, agen autentikasi, dan auto-redaksi melindungi data sensitif.

---

## Mulai Cepat

### Prasyarat

- Python 3.8 atau lebih tinggi
- Node.js 18+ (untuk antarmuka web)
- RAM 4GB+ direkomendasikan
- Koneksi internet untuk akses provider LLM

### Instalasi

```bash
# Klon repositori
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# Instal dependensi Python
pip install -r requirements.txt

# Instal dependensi antarmuka web (opsional)
cd web-interface && npm install && cd ..

# Salin konfigurasi lingkungan
cp .env.example .env
# Edit .env dengan kunci API dan konfigurasi Anda
```

### Menjalankan Ekosistem

```bash
# Mulai ekosistem lengkap dengan antarmuka web
python main.py --start-all

# Mulai dengan mode tertentu
python main.py --mode ultimate

# Mulai hanya antarmuka web
python main.py --web-ui --port 8080

# Periksa status sistem
python main.py --status --detailed

# Daftar semua agen terdaftar
python main.py --list-agents
```

### Akses Dasbor

Setelah berjalan, buka browser Anda ke:

```
http://localhost:8080
```

Dasbor menyediakan pemantauan real-time, manajemen agen, antarmuka chat, dan kontrol sistem.

### Penerapan Docker

```bash
# Bangun dan jalankan dengan Docker Compose
docker-compose up -d

# Atau bangun secara manual
docker build -t ai-multicolony .
docker run -p 8080:8080 -p 5000:5000 ai-multicolony
```

---

## Struktur Proyek

```
AI-MultiColony-Ecosystem/
├── main.py                          # Titik masuk terpadu / peluncur
├── colony/
│   ├── core/                        # Mesin inti koloni
│   │   ├── base_agent.py            # Kelas dasar agen abstrak
│   │   ├── agent_registry.py        # Penemuan & registrasi agen
│   │   ├── unified_agent_registry.py # Registri ditingkatkan dengan pabrik
│   │   ├── agent_manager.py         # Manajemen siklus hidup agen
│   │   ├── scheduler.py             # Mesin penjadwalan tugas
│   │   ├── memory_bus.py            # Bus komunikasi bersama
│   │   ├── daemon_manager.py        # Manajer proses latar belakang
│   │   ├── config_loader.py         # Sistem konfigurasi YAML
│   │   ├── prompt_master.py         # Sistem rekayasa prompt
│   │   ├── system_bootstrap.py      # Inisialisasi startup
│   │   └── reporting/               # Subsistem hasil & laporan
│   ├── agents/                      # 40+ agen khusus
│   │   ├── commander_agi.py         # Agen keamanan & komando
│   │   ├── smart_money_trading_agent.py  # Perdagangan SMC/ICT
│   │   ├── autonomous_fullstack_dev_agent.py  # Pengembangan otomatis
│   │   ├── web_automation_agent.py  # Otomasi browser
│   │   ├── dynamic_agent_factory.py # Pembuatan agen runtime
│   │   └── ...                      # 35+ agen lainnya
│   ├── api/                         # API REST & WebSocket
│   │   ├── app.py                   # Server Flask/FastAPI
│   │   ├── websocket.py             # Handler WebSocket
│   │   └── endpoints/               # Modul endpoint API
│   └── integrations/                # Integrasi kerangka kerja AI
│       ├── camel_ai_integration.py
│       ├── autogen_integration.py
│       ├── crewai_integration.py
│       ├── langgraph_integration.py
│       ├── supabase_integration.py
│       └── netlify_integration.py
├── connectors/                      # Konektor eksternal
│   ├── mcp_connector.py             # Model Context Protocol
│   └── llm_gateway.py               # Gateway LLM multi-provider
├── web-interface/                   # Dasbor Next.js
│   ├── src/                         # Sumber React/Next.js
│   ├── templates/                   # Template HTML Flask
│   ├── static/                      # CSS, JS, ikon
│   └── package.json
├── config/                          # File konfigurasi
│   ├── system_config.yaml
│   ├── agent_templates.yaml
│   └── prompts.yaml
├── data/                            # Data runtime (gitignored)
├── database/                        # Model database & init
├── docs/                            # Dokumentasi
├── examples/                        # Contoh penggunaan
├── scripts/                         # Skrip utilitas
├── sandbox/                         # Manajer sandbox
├── requirements.txt                 # Dependensi Python
├── docker-compose.yml               # Konfigurasi Docker
├── Dockerfile                       # Definisi kontainer
└── LICENSE                          # Lisensi MIT
```

---

## Katalog Agen

Berikut adalah katalog terperinci dari agen-agen kunci yang tersedia di ekosistem. Setiap agen ditemukan secara otomatis oleh registri dan dapat diakses melalui endpoint API atau dasbor web.

| Agen | ID | Kategori | Deskripsi |
|------|----|----------|-----------|
| Commander AGI | `commander_agi` | Komando & Kontrol | Pemantauan keamanan tingkat lanjut, deteksi ancaman, pelacakan kesehatan sistem, dan koordinasi misi otonom dengan analisis jaringan real-time dan respons insiden |
| Smart Money Trading | `smart_money_trading_agent` | Perdagangan & Keuangan | Perdagangan tingkat institusi menggunakan Smart Money Concepts (SMC) dan metodologi ICT — order block, fair value gap, pool likuiditas, analisis multi-timeframe |
| Autonomous Fullstack Dev | `autonomous_fullstack_dev_agent` | Pengembangan | Agen pengembangan mandiri yang secara terus-menerus menganalisis sistem, mengidentifikasi peningkatan, melakukan riset, dan mengeksekusi perubahan kode secara otonom |
| Web Automation | `web_automation_agent` | Otomasi Web | Otomasi browser berbasis Selenium dengan manajemen kredensial, login/registrasi otomatis, pengisian formulir, dan kemampuan interaksi web |
| Dynamic Agent Factory | `dynamic_agent_factory` | Pembuatan Agen | Pembuatan agen runtime dari template dengan injeksi kapabilitas, konfigurasi kustom, dan integrasi registri otomatis |
| Enhanced Agent Creator | `enhanced_agent_creator` | Pembuatan Agen | Pembangun agen tingkat lanjut dengan manajemen template, validasi, dan otomasi penerapan |
| Meta Agent Creator | `meta_agent_creator` | Pembuatan Agen | Membuat pembuat agen lainnya — pabrik tingkat meta untuk menghasilkan pabrik agen khusus |
| Chatbot Agent | `chatbot_agent` | Komunikasi | Agen AI percakapan dengan manajemen sesi, pelacakan konteks, dan dukungan dialog multi-giliran |
| Deployment Agent | `deployment_agent` | Operasi | Manajemen pipeline penerapan otomatis dengan konfigurasi lingkungan dan dukungan rollback |
| Deploy Manager | `deploy_manager` | Operasi | Orkestrasi penerapan terpusat di berbagai lingkungan dan platform |
| Auto Deployment System | `auto_deployment_system` | Operasi | Sistem penerapan sepenuhnya otonom dengan pemeriksaan kesehatan, canary release, dan rollback otomatis |
| Authentication Agent | `authentication_agent` | Keamanan | Alur autentikasi pengguna, manajemen token, dan penegakan kontrol akses |
| Credential Manager | `credential_manager` | Keamanan | Penyimpanan kredensial terenkripsi, pengambilan, dan manajemen siklus hidup dengan pelacakan penggunaan |
| Auto Redactor | `auto_redactor_agent` | Keamanan | Deteksi dan redaksi otomatis informasi sensitif dalam output dan log agen |
| AI Research Agent | `ai_research_agent` | Riset | Riset AI otonom dengan tinjauan literatur, pembuatan hipotesis, dan desain eksperimen |
| Knowledge Management | `knowledge_management_agent` | Riset | Kurasi basis pengetahuan, generasi yang diperkuat pengambilan, dan manajemen siklus hidup informasi |
| CAMEL Agent Integration | `camel_agent_integration` | Riset | Jembatan ke kerangka kerja penalaran kolaboratif CAMEL AI untuk dialog multi-agent |
| System Supervisor | `system_supervisor` | Sistem | Pemantauan sistem tingkat tinggi, pemeriksaan kesehatan, dan remediasi otomatis |
| System Optimizer | `system_optimizer` | Sistem | Profiling kinerja, optimasi sumber daya, dan penyetelan konfigurasi |
| Autonomous Maintainer | `autonomous_maintainer` | Sistem | Pemeliharaan sistem swa-perbaikan dengan rotasi log, pembersihan cache, dan pembaruan dependensi |
| Bug Hunter Bot | `bug_hunter_bot` | Sistem | Deteksi bug otomatis, reproduksi, dan pelaporan dengan klasifikasi tingkat keparahan |
| Quality Control Specialist | `quality_control_specialist` | Kualitas | Tinjauan kode, pengawasan pengujian, dan penegakan metrik kualitas |
| Marketing Agent | `marketing_agent` | Pemasaran | Pembuatan konten, manajemen kampanye, dan otomasi media sosial |
| UI Designer | `ui_designer` | Desain | Pembuatan desain antarmuka visual dengan integrasi perpustakaan komponen |
| CyberShell | `cybershell` | Keamanan | Otomasi shell dan terminal tingkat lanjut dengan audit keamanan |
| LLM Provider Manager | `llm_provider_manager` | Infrastruktur | Konfigurasi LLM multi-provider, pemantauan kesehatan, dan pelacakan biaya |

---

## Berkontribusi

Kontributor dipersilakan! AI-MultiColony-Ecosystem adalah proyek open-source dan kami aktif mendorong partisipasi komunitas. Baik Anda ingin menambahkan agen baru, meningkatkan yang sudah ada, menyempurnakan antarmuka web, atau memperbaiki bug, ada banyak cara untuk berkontribusi.

### Cara Berkontribusi

1. **Fork Repositori** — Buat fork Anda sendiri di [https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork)
2. **Buat Branch Fitur** — `git checkout -b feature/nama-fitur-anda`
3. **Kembangkan Fitur Anda** — Ikuti pola kode yang ada dan warisi dari `BaseAgent` untuk agen baru
4. **Uji Perubahan Anda** — Pastikan semua pengujian yang ada lulus dan tambahkan pengujian baru untuk fitur Anda
5. **Kirim Pull Request** — Jelaskan perubahan Anda dengan jelas dan referensikan masalah terkait

### Membuat Agen Baru

```python
from colony.core.base_agent import BaseAgent
from colony.core.agent_registry import register_agent

@register_agent(
    name="my_custom_agent",
    description="Agen kustom yang melakukan sesuatu yang luar biasa",
    route="/api/agents/my_custom_agent"
)
class MyCustomAgent(BaseAgent):
    def __init__(self, name="my_custom_agent", config=None, memory_manager=None):
        super().__init__(name=name, config=config, memory_manager=memory_manager)
    
    def run(self):
        """Eksekusi agen utama"""
        self.update_status("running")
        # Logika agen Anda di sini
        self.update_status("completed")
    
    async def process_task(self, task):
        """Memproses tugas masuk"""
        result = {"success": True, "data": "diproses"}
        return self.format_response(str(result))
```

### Pengaturan Pengembangan

```bash
# Instal dependensi pengembangan
pip install -r requirements-dev.txt

# Jalankan pengujian
python -m pytest tests/

# Format kode
black colony/ connectors/
```

### Kontak

Untuk pertanyaan, saran, atau peluang kolaborasi, hubungi:

- **Email**: [mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)
- **GitHub**: [https://github.com/mulkymalikuldhrs](https://github.com/mulkymalikuldhrs)

---

## Kontak

<p align="center">
  <a href="mailto:mulkymalikuldhaher@email.com">
    <img src="https://img.shields.io/badge/Email-mulkymalikuldhaher@email.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/>
  </a>
  <a href="https://github.com/mulkymalikuldhrs">
    <img src="https://img.shields.io/badge/GitHub-mulkymalikuldhrs-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
    <img src="https://img.shields.io/badge/Repositori-AI--MultiColony--Ecosystem-2E9EF7?style=for-the-badge&logo=github&logoColor=white" alt="Repositori"/>
  </a>
  <a href="https://github.com/mulkymalikuldhrs/HermesQuantOS">
    <img src="https://img.shields.io/badge/Terkait-HermesQuantOS-8B5CF6?style=for-the-badge&logo=github&logoColor=white" alt="HermesQuantOS"/>
  </a>
</p>

---

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file [LICENSE](./LICENSE) untuk detailnya.

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=80&section=footer" alt="Gelombang Footer"/>
</p>

<p align="center">
  Dibuat dengan ❤️ oleh <strong>Mulky Malikul Dhaher</strong> di Indonesia 🇮🇩
</p>
