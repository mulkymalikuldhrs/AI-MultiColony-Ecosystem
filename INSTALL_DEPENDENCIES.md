# 📦 Dependencies Installation Guide

## Core Dependencies (✅ Already Installed)
```bash
pip install flask flask-socketio flask-cors pyyaml requests aiofiles
```

## Optional Dependencies (⚠️ Missing - Install for Full Functionality)

### Network & System
```bash
pip install netifaces  # Network interface detection
pip install dnspython  # DNS resolution
```

### Research & Academic
```bash
pip install arxiv  # Academic paper access
```

### Computer Vision & Media
```bash
pip install opencv-python  # Computer vision (cv2)
pip install qrcode[pil]  # QR code generation
```

### Natural Language Processing
```bash
pip install nltk  # Natural language processing
```

### Database & Async
```bash
pip install asyncpg  # PostgreSQL async driver
pip install paramiko  # SSH client
```

### Web3 & Blockchain (if needed)
```bash
pip install web3  # Ethereum blockchain interaction
```

## Install All Optional Dependencies at Once
```bash
pip install netifaces dnspython arxiv opencv-python qrcode[pil] nltk asyncpg paramiko web3
```

## Create Requirements File
```bash
pip freeze > requirements.txt
```

## Install from Requirements (for future deployments)
```bash
pip install -r requirements.txt
```

## Verification
After installing dependencies, run:
```bash
python main.py --help
```

You should see fewer warning messages and more agents successfully registered.