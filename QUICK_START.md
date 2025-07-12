# 🚀 Quick Start Guide - AI-MultiColony-Ecosystem

## Prerequisites
- Python 3.8+ installed
- Git installed

## 1. Clone Repository (if not already done)
```bash
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem
```

## 2. Install Core Dependencies
```bash
pip install flask flask-socketio flask-cors pyyaml requests aiofiles
```

## 3. Launch Web Interface
```bash
python main.py --web-ui
```

The web interface will be available at:
- **Local**: http://localhost:8080
- **Network**: http://YOUR_IP:8080

## 4. Available Launch Options

### Show Help
```bash
python main.py --help
```

### Launch Specific Agent
```bash
python main.py --agent agent_base
```

### Launch All Agents
```bash
python main.py --all
```

### Enable Monitoring
```bash
python main.py --monitor
```

### Launch with Specific Mode
```bash
python main.py --mode 1  # Modes 1-5 available
```

## 5. Web Interface Features

Once the web UI is running, you can:
- 📊 Monitor system status
- 🤖 View registered agents (12 currently active)
- 📝 Submit tasks to agents
- 💬 Send prompts for processing
- 🔄 Start/stop system components
- 📈 View real-time metrics

## 6. API Endpoints

The system provides REST API endpoints:
- `GET /api/system/status` - System health
- `GET /api/agents/list` - List all agents
- `POST /api/task/submit` - Submit tasks
- `POST /api/prompt/submit` - Submit prompts

## 7. Install Optional Dependencies (Recommended)

For full functionality, install optional dependencies:
```bash
pip install netifaces dnspython arxiv opencv-python qrcode[pil] nltk asyncpg paramiko
```

This will enable additional agents and features.

## 8. Configuration

Configuration files are located in the `config/` directory:
- `agents.yaml` - Agent configurations
- `system.yaml` - System settings
- `llm.yaml` - LLM provider settings

## 9. Troubleshooting

### Common Issues:
1. **Port 8080 already in use**: Change port in config or use different port
2. **Import errors**: Install missing dependencies
3. **Permission errors**: Check file permissions

### Check System Status:
```bash
python -c "
import sys
sys.path.append('.')
from colony.core.agent_registry import agent_registry
print(f'Registered agents: {len(agent_registry.get_all_agents())}')
"
```

## 10. Next Steps

1. Explore the web interface
2. Try submitting tasks to different agents
3. Install optional dependencies for more features
4. Read the comprehensive analysis report
5. Customize configurations as needed

## Support

For issues or questions:
1. Check the `COMPREHENSIVE_ANALYSIS_REPORT.md`
2. Review the `INSTALL_DEPENDENCIES.md`
3. Check the `docs/` directory for additional documentation

---

**System Status**: ✅ Operational  
**Core Agents**: 12 registered  
**Web Interface**: ✅ Working  
**API**: ✅ Functional