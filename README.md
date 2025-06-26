# Agentic-AI-System
AI berbasis multi-agent. Setiap agent (Planner, Executor, Designer, dll) memiliki peran dan instruksi jelas, dikendalikan oleh Agent Base dan dikoordinasi melalui arsitektur cerdas.
# 🧠 Agentic AI System – Prompt Architecture

## Overview
This repository/document contains a **comprehensive prompt schema** for building an **Agentic AI System** based on modular agents. Each agent serves a specific function and is coordinated by a central orchestrator (Agent Base) to perform complex tasks efficiently.

Designed for integration with tools like **LangGraph**, **AutoGen**, **CrewAI**, or custom-built LLM stacks.

---

## 🧩 Core Components

| Agent Name          | Role/Function                                                |
|---------------------|--------------------------------------------------------------|
| Agent Base          | Master controller and task coordinator                       |
| Dynamic Agent Factory | Spawns new agents based on task and role                   |
| Agent 02 (Meta-Spawner) | Monitors performance and bottlenecks                   |
| Prompt Library      | Provides context-specific prompt templates                   |
| Knowledge Base (RAG DB) | Retrieves semantic data context for each task          |
| Agent 03 (Planner)  | Breaks down goals into executable steps                      |
| Agent 04 (Executor) | Runs scripts, APIs, tools, or automation pipelines           |
| Agent 05 (Designer) | Produces visual assets: UI, diagrams, infographics           |
| Agent 06 (Specialist)| Provides expertise in security, law, AI tuning, etc.        |
| Output Handler      | Finalizes and formats deliverables                           |

---

## 📦 Features

- **Modular prompt structure** for scalable agent orchestration
- **Dynamic agent spawning** based on role/task
- **Integrated RAG retrieval** for knowledge injection
- **Execution-ready** with code, API, and UI generation agents
- **Designed for no-code and low-code platforms** (e.g., AutoGen Studio, LangChain GUI)

---

## 🛠️ Integration

| Platform | Compatibility | Notes |
|----------|----------------|-------|
| LangGraph | ✅ Full        | Agent flows & DAG orchestration |
| AutoGen   | ✅ Full        | Conversational multi-agent logic |
| CrewAI    | ✅ Full        | Agent roles & delegation system |
| Custom    | ✅ Customizable| YAML or Python integration available |

---

## 📁 Files

- `Agentic_Prompts.docx` → Full prompt schema for each agent
- `A_flowchart_infographic.png` → Visual architecture of the system
- `README.md` → This file

---

## 🔧 How to Use

1. Import prompt templates from `Agentic_Prompts.docx`
2. Use or modify the prompt instructions for your agents
3. Integrate into your orchestration layer (LangGraph, etc.)
4. Run tasks with automatic agent delegation and supervision
5. Use Output Handler to compile results

---

## 📌 License

This system and prompt architecture are open for customization and private projects. Attribution appreciated but not required.

---

## 🤝 Credits

Developed by: **Mulky Malikul Dhaher (Mul)**  
System Design & Prompt Engineering by: **Mul & ChatGPT Agentic Support**

---
