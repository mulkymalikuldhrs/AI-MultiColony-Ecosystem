# 🚀 QUICK START DEMO - Autonomous Agent Colony

## 📋 Langkah-langkah MUDAH untuk Memulai

### 🎯 **OPSI 1: TESTING CEPAT (RECOMMENDED)**

```bash
# 1. Langsung jalankan (tanpa install apapun!)
python3 main_standalone.py

# 2. Tunggu sistem start (10 detik)
# 3. Mulai berinteraksi dengan commands berikut
```

### 💬 **DEMO COMMANDS**

#### **Cek Status Sistem**
```bash
>>> status
System Status:
--------------
🤖 Total Agents: 3
📋 Queue Size: 0  
🧠 Models: 0 (Mock Mode)
⚡ Status: Running
```

#### **Lihat Agent yang Tersedia**
```bash
>>> agents
Agent List:
-----------
🤖 developer_1 (developer) - ready - Tasks: 0
🤖 analyst_1 (analyst) - ready - Tasks: 0  
🤖 researcher_1 (researcher) - ready - Tasks: 0
```

#### **Submit Task ke Agent Colony**
```bash
>>> task Create a Python web scraper for news articles
✅ Task 'Create a Python web scraper for news articles' submitted with ID: task_214759
📝 Task task_214759 submitted
✅ Task task_214759 completed by developer_1
```

#### **Test Code Completion**
```bash
>>> completion def hello_world():
Code Completion for: def hello_world():
--------------------
💡 Mock suggestion: # Mock completion
```

#### **Help & Exit**
```bash
>>> help
Available Commands:
-------------------
task <description>    - Submit a task to the agent colony
status               - Show system status
agents              - List all agents
completion <code>   - Test AI code completion
help                - Show this help
quit/exit           - Exit the system

>>> quit
🛑 Shutting down gracefully...
```

---

## 🎯 **OPSI 2: FULL PRODUCTION SETUP**

### **Step 1: Installation**
```bash
# Install semua dependencies
python3 install.py
```

### **Step 2: Configure API Keys**
```bash
# Edit file .env dengan API keys Anda
nano .env

# Contoh isi .env:
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GROQ_API_KEY=gsk_your-groq-key-here  # FREE!
```

### **Step 3: Start Full System**
```bash
# Jalankan sistem lengkap
python3 main.py

# Akses web interface di:
# http://localhost:8000/admin
```

### **Step 4: Use Web Dashboard**
- 🌐 **Web Dashboard**: `http://localhost:8000/admin`
- 📚 **API Documentation**: `http://localhost:8000/docs`
- 🔧 **Health Check**: `http://localhost:8000/health`

---

## 🎮 **DEMO SCENARIO REAL-WORLD**

### **Scenario: AI-Powered Development Assistant**

```bash
# 1. Start system
python3 main_standalone.py

# 2. Create agents for different tasks
>>> task Analyze the requirements for a todo app
>>> task Write Python code for a REST API
>>> task Review the code for security issues  
>>> task Write unit tests for the API

# 3. Monitor progress
>>> status
>>> agents

# 4. Test code intelligence
>>> completion class TodoAPI:
>>> completion async def create_todo(
```

### **Expected Output Flow:**
```
📝 Task task_001 submitted (Analyst working on requirements)
✅ Task task_001 completed by analyst_1
📝 Task task_002 submitted (Developer writing code)  
✅ Task task_002 completed by developer_1
📝 Task task_003 submitted (Critic reviewing security)
✅ Task task_003 completed by developer_1  
📝 Task task_004 submitted (Developer writing tests)
✅ Task task_004 completed by developer_1
```

---

## 🌟 **ADVANCED FEATURES DEMO**

### **API Usage (dengan curl)**
```bash
# Create new agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"role": "developer", "config": {}}'

# Submit task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"type": "coding", "content": "Write a FastAPI endpoint"}'

# Get code completion
curl -X POST http://localhost:8000/code/completion \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test.py", "code_context": "def hello():", "cursor_position": 12}'
```

### **WebSocket Real-time Updates**
```javascript
// Connect ke WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Real-time update:', message);
};

// Send message
ws.send(JSON.stringify({type: 'ping', data: 'hello'}));
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **"Permission denied" Error**
```bash
# Make file executable
chmod +x main_standalone.py
python3 main_standalone.py
```

#### **"Port already in use" Error**
```bash
# Change port in config or kill process
lsof -ti:8000 | xargs kill -9
```

#### **"API key not found" Warning**
```bash
# Normal dalam mock mode - tidak perlu API key untuk testing
# Untuk production, edit .env file
```

#### **Dependencies Error**
```bash
# Use standalone mode for zero dependencies
python3 main_standalone.py

# Or force install (if needed)
pip3 install --break-system-packages fastapi uvicorn
```

---

## 💡 **TIPS & BEST PRACTICES**

### **Development Workflow**
1. **Start**: `python3 main_standalone.py` untuk quick testing
2. **Test**: Submit beberapa tasks untuk verify functionality  
3. **Monitor**: Use `status` dan `agents` commands
4. **Iterate**: Modify code dan restart sistem

### **Production Deployment**
1. **Setup**: Configure .env dengan real API keys
2. **Deploy**: Use `python3 main.py` atau Docker
3. **Monitor**: Access web dashboard untuk monitoring
4. **Scale**: Add more agents based on load

### **Cost Optimization**
1. **Free Tier**: Gunakan Groq API (unlimited free)
2. **Local Models**: Setup Ollama untuk offline usage
3. **Mock Mode**: Use standalone untuk development

---

## 🎯 **SUCCESS CRITERIA CHECKLIST**

Setelah menjalankan demo, Anda harus bisa:

✅ **Start sistem dalam <15 detik**  
✅ **Submit task dan lihat response**  
✅ **Monitor agent status real-time**  
✅ **Test code completion features**  
✅ **Access web dashboard (production mode)**  
✅ **Use API endpoints dengan curl**  
✅ **See real-time WebSocket updates**  

### **Jika semua ✅ → SISTEM WORKING PERFECTLY! 🎉**

---

## 🚀 **NEXT STEPS AFTER DEMO**

1. **Customize**: Modify agent roles dan skills sesuai needs
2. **Integrate**: Connect dengan existing development workflow  
3. **Scale**: Deploy ke production environment
4. **Extend**: Add custom features dan integrations
5. **Optimize**: Fine-tune performance dan costs

---

### **🎊 READY TO REVOLUTIONIZE YOUR AI DEVELOPMENT! 🐫**

**Your Autonomous Agent Colony is now at your command!** ⚡