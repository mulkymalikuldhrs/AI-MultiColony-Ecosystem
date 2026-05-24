[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=2E9EF7&center=true&vCenter=true&width=800&lines=AI-MultiColony-Ecosystem;多智能体群体协调平台;v8.0.0+作者+Mulky+Malikul+Dhaher)](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem)

<p align="center">
  <img src="https://img.shields.io/badge/版本-8.0.0-gold?style=for-the-badge&logo=semver" alt="版本 8.0.0"/>
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/多智能体-40%2B-FF6F00?style=for-the-badge&logo=robotframework&logoColor=white" alt="40+ 智能体"/>
  <img src="https://img.shields.io/badge/许可证-MIT-green?style=for-the-badge" alt="MIT 许可证"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-仪表盘-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js"/>
</p>

<p align="center">
  <a href="./README.md">🇬🇧 English</a> |
  <a href="./README_id.md">🇮🇩 Bahasa Indonesia</a> |
  <a href="./README_zh.md">🇨🇳 中文</a>
</p>

---

## 概述

**AI-MultiColony-Ecosystem** 是一个前沿的多智能体群体协调平台，旨在统一协作的生态系统中编排数十个专业化的 AI 智能体。由 [Mulky Malikul Dhaher](https://github.com/mulkymalikuldhrs) 构建，该平台提供了一个稳健的框架，用于在多个领域部署、管理和协调智能体，包括自主软件开发、金融交易、Web 自动化、安全监控等。

其核心遵循**群体隐喻**——每个智能体作为更大群体的专业化成员运作，通过共享内存总线进行通信，由中央智能体注册表协调，并通过调度器和守护进程管理器编排。该平台集成了领先的 AI 框架（CAMEL AI、AutoGen、CrewAI、LangGraph），并提供基于 Next.js 和 FastAPI 构建的现代 Web 仪表盘，用于实时监控和控制。

系统架构支持动态智能体创建、自我改进的自主循环、通过统一网关的多供应商 LLM 访问，以及用于模型上下文协议（MCP）工具的可扩展连接器。无论您是构建自主交易系统、AI 驱动的开发流水线，还是多智能体研究平台，AI-MultiColony-Ecosystem 都提供了实现目标的基础设施。

> **相关项目**：[HermesQuantOS](https://github.com/mulkymalikuldhrs/HermesQuantOS) — 基于此生态系统构建的生产就绪量化交易操作系统。

---

## 架构

AI-MultiColony-Ecosystem 组织为五个主要层，每层负责平台运营的关键方面。这些层协同工作，提供从智能体创建到部署和监控的无缝体验。

### 群体核心（Colony Core）

群体核心是平台的中枢神经系统。它管理智能体的整个生命周期，从注册和发现到调度和内存管理。关键组件包括：

| 组件 | 文件 | 描述 |
|------|------|------|
| **智能体注册表** | `colony/core/agent_registry.py` | 基于装饰器的注册系统，自动发现并编目所有智能体类。支持元数据、API 路由和依赖追踪。 |
| **基础智能体** | `colony/core/base_agent.py` | 所有智能体继承的抽象基类。提供状态管理、错误处理、输出持久化、任务验证和生命周期钩子（`run`、`process_task`、`stop`、`restart`）。 |
| **智能体管理器** | `colony/core/agent_manager.py` | 编排智能体执行，管理智能体实例，处理智能体间通信，提供集中式智能体控制。 |
| **统一智能体注册表** | `colony/core/unified_agent_registry.py` | 增强型注册表，具有动态智能体创建的工厂方法、实例管理和跨群体智能体发现。 |
| **调度器** | `colony/core/scheduler.py` | 任务调度引擎，支持类 cron 模式、优先级队列、循环任务和依赖感知的执行排序。 |
| **内存总线** | `colony/core/memory_bus.py` | 共享通信骨干，使智能体能够实时交换消息、共享状态和协调活动。 |
| **守护进程管理器** | `colony/core/daemon_manager.py` | 管理长期运行的后台进程（守护进程）、健康检查、自动重启和资源监控。 |
| **配置加载器** | `colony/core/config_loader.py` | 基于 YAML 的配置系统，支持环境变量插值、验证和热重载。 |
| **提示词大师** | `colony/core/prompt_master.py` | 高级提示词工程和管理系统，用于优化跨智能体的 LLM 交互。 |
| **系统引导** | `colony/core/system_bootstrap.py` | 启动初始化序列，加载配置、初始化数据库、注册智能体并启动系统服务。 |
| **报告引擎** | `colony/core/reporting/` | 结果收集、验证、冲突解决、报告生成和输出存储子系统。 |

### 群体智能体（Colony Agents）

平台内置 40+ 专业化智能体，每个智能体针对特定领域设计。智能体继承自 `BaseAgent` 并由注册表自动发现。关键智能体包括：

| 类别 | 关键智能体 | 描述 |
|------|-----------|------|
| **指挥与控制** | `commander_agi` | 安全监控、威胁检测、系统健康追踪和智能体任务协调，具备自主响应能力。 |
| **交易与金融** | `smart_money_trading_agent`、`money_making_agent`、`money_making_orchestrator` | 基于 Smart Money Concepts（SMC）和 ICT 的交易，支持订单块分析、公允价值缺口检测、流动性映射和多时间框架汇合扫描。 |
| **开发** | `autonomous_fullstack_dev_agent`、`fullstack_dev`、`fullstack_agent`、`dev_engine` | 自主代码生成、系统分析、持续改进循环和具有研究能力的自主开发。 |
| **Web 自动化** | `web_automation_agent`、`cybershell` | 基于 Selenium 的浏览器自动化、凭证管理、表单填充、登录/注册自动化和 Web 交互。 |
| **智能体创建** | `dynamic_agent_factory`、`enhanced_agent_creator`、`meta_agent_creator`、`agent_maker` | 从模板运行时生成智能体、动态能力注入和智能体蓝图管理。 |
| **运维** | `deployment_agent`、`deploy_manager`、`auto_deployment_system` | 自动化部署流水线、服务管理和基础设施配置。 |
| **安全** | `authentication_agent`、`credential_manager`、`auto_redactor_agent` | 凭证存储、认证流程、敏感数据脱敏和安全策略执行。 |
| **研究与 AI** | `ai_research_agent`、`knowledge_management_agent`、`camel_agent_integration` | AI 研究自动化、知识库管理和 CAMEL AI 协作推理。 |
| **设计与 UI** | `ui_designer`、`agent_05_designer` | UI/UX 设计生成、组件创建和可视化界面开发。 |
| **系统** | `system_supervisor`、`system_optimizer`、`autonomous_maintainer`、`bug_hunter_bot` | 系统健康监控、性能优化、自动维护和缺陷检测。 |
| **专家** | `agent_06_specialist`、`quality_control_specialist`、`deployment_specialist`、`specialist_agents` | 质量控制、部署操作和专业任务执行的领域专家。 |
| **营销** | `marketing_agent` | 营销自动化、内容生成和活动管理。 |

### 群体 API（Colony API）

群体 API 层提供 RESTful 和 WebSocket 端点，用于与生态系统交互：

- **FastAPI / Flask 后端**（`colony/api/app.py`）— 高性能 API 服务器，支持从智能体注册表动态生成端点
- **WebSocket 服务器**（`colony/api/websocket.py`）— 实时双向通信，支持实时更新和流式传输
- **启动器 API**（`colony/api/launcher_api.py`）— 系统控制端点，用于启动、停止和管理智能体
- **智能体端点**（`colony/api/endpoints/agents.py`、`tasks.py`、`agent_creator.py`）— 智能体和任务的 CRUD 操作
- **聊天 API** — `/api/chat/message`、`/api/chat/history`、`/api/chat/clear` 用于对话式 AI 交互
- **系统 API** — `/api/system/status`、`/api/system/emergency-stop`、`/api/system/restart-all` 用于系统管理
- **内存 API** — `/api/memory/stats` 用于共享内存总线统计

### 群体集成（Colony Integrations）

平台集成了领先的 AI 和云框架：

| 集成 | 文件 | 描述 |
|------|------|------|
| **CAMEL AI** | `colony/integrations/camel_ai_integration.py` | 多智能体协作推理、角色扮演对话和合作任务求解 |
| **AutoGen** | `colony/integrations/autogen_integration.py` | 微软 AutoGen 多智能体对话框架，用于复杂推理任务 |
| **CrewAI** | `colony/integrations/crewai_integration.py` | 基于角色的智能体团队，支持顺序和并行任务执行 |
| **LangGraph** | `colony/integrations/langgraph_integration.py` | 基于图的智能体工作流，支持有状态执行和条件路由 |
| **Supabase** | `colony/integrations/supabase_integration.py` | 云数据库、认证和实时订阅 |
| **Netlify** | `colony/integrations/netlify_integration.py` | 自动化 Web 部署和托管集成 |

### Web 界面

Next.js 仪表盘提供现代化、响应式的控制面板：

- **仪表盘** — 实时系统监控、智能体状态和性能指标
- **智能体管理器** — 浏览、创建、配置和控制所有已注册智能体
- **聊天界面** — 对话式 AI，支持多智能体路由和上下文管理
- **智能体创建器** — 从模板动态创建智能体，支持能力定制
- **部署面板** — 一键部署，支持环境配置
- **监控** — 系统健康、资源使用和告警管理
- **凭证保险库** — 安全凭证管理，支持加密存储
- **平台集成** — 配置 CAMEL AI、AutoGen、CrewAI、LangGraph 和云提供商
- **PWA 支持** — 渐进式 Web 应用，支持离线功能和推送通知

### 连接器

| 连接器 | 文件 | 描述 |
|--------|------|------|
| **MCP 连接器** | `connectors/mcp_connector.py` | 模型上下文协议客户端，用于连接 MCP 服务器，通过 WebSocket 访问工具/资源/提示词 |
| **LLM 网关** | `connectors/llm_gateway.py` | 多供应商 LLM 访问，支持自动故障转移、负载均衡和使用量追踪。支持 LLM7、OpenRouter 和自定义供应商 |

---

## 核心特性

- **群体式智能体协调** — 智能体作为群体的专业化成员运作，通过共享内存总线通信，由统一注册表协调。这使涌现的集体智能成为可能，智能体可以协作处理任何单个智能体无法独立完成的复杂任务。

- **动态智能体工厂** — 使用增强型智能体创建器，在运行时从模板或从头创建新智能体。工厂系统支持能力注入、模板继承和运行时配置，允许您快速原型设计和部署新的智能体类型，而无需修改核心代码。

- **多框架集成** — 无缝集成 CAMEL AI 用于协作推理、AutoGen 用于对话式智能体网络、CrewAI 用于基于角色的团队、LangGraph 用于有状态图工作流。根据任务需求在框架之间切换或组合使用。

- **Smart Money 交易引擎** — 内置的 Smart Money Concepts（SMC）和 ICT 交易智能体提供机构级市场分析，包括订单块识别、公允价值缺口检测、流动性池映射和多时间框架汇合扫描，支持可配置的风险管理。

- **统一 LLM 网关** — 通过单一接口访问多个 LLM 供应商（LLM7、OpenRouter、OpenAI、自定义端点），支持自动故障转移、速率限制、令牌追踪和供应商健康监控。再也不用担心供应商宕机了。

- **MCP 连接器** — 连接到模型上下文协议服务器，访问外部工具、资源和提示词。连接器处理完整的 MCP 生命周期，包括初始化、能力发现和工具调用。

- **实时 Web 仪表盘** — 通过现代化的 Next.js 仪表盘监控整个群体，支持通过 WebSocket 实时更新智能体状态、交互式聊天、系统健康指标和一键部署控制。可作为 PWA 用于移动端访问。

- **自主自我改进** — 自主开发智能体持续分析系统、识别改进机会、进行研究并执行增强——创建一个随时间推移不断进化的自我演化生态系统。

- **安全优先设计** — Commander AGI 提供实时安全监控、威胁检测和自主响应。带加密存储的凭证管理、认证智能体和自动脱敏保护敏感数据。

---

## 快速开始

### 前提条件

- Python 3.8 或更高版本
- Node.js 18+（用于 Web 界面）
- 推荐 4GB+ 内存
- 用于 LLM 供应商访问的互联网连接

### 安装

```bash
# 克隆仓库
git clone https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem.git
cd AI-MultiColony-Ecosystem

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Web 界面依赖（可选）
cd web-interface && npm install && cd ..

# 复制环境配置
cp .env.example .env
# 使用您的 API 密钥和配置编辑 .env 文件
```

### 运行生态系统

```bash
# 启动包含 Web 界面的完整生态系统
python main.py --start-all

# 以特定模式启动
python main.py --mode ultimate

# 仅启动 Web 界面
python main.py --web-ui --port 8080

# 检查系统状态
python main.py --status --detailed

# 列出所有已注册智能体
python main.py --list-agents
```

### 访问仪表盘

运行后，在浏览器中打开：

```
http://localhost:8080
```

仪表盘提供实时监控、智能体管理、聊天界面和系统控制。

### Docker 部署

```bash
# 使用 Docker Compose 构建并运行
docker-compose up -d

# 或手动构建
docker build -t ai-multicolony .
docker run -p 8080:8080 -p 5000:5000 ai-multicolony
```

---

## 项目结构

```
AI-MultiColony-Ecosystem/
├── main.py                          # 统一入口 / 启动器
├── colony/
│   ├── core/                        # 群体核心引擎
│   │   ├── base_agent.py            # 抽象基础智能体类
│   │   ├── agent_registry.py        # 智能体发现与注册
│   │   ├── unified_agent_registry.py # 增强型注册表（含工厂）
│   │   ├── agent_manager.py         # 智能体生命周期管理
│   │   ├── scheduler.py             # 任务调度引擎
│   │   ├── memory_bus.py            # 共享通信总线
│   │   ├── daemon_manager.py        # 后台进程管理器
│   │   ├── config_loader.py         # YAML 配置系统
│   │   ├── prompt_master.py         # 提示词工程系统
│   │   ├── system_bootstrap.py      # 启动初始化
│   │   ├── llm_client.py            # LLM 客户端工具
│   │   ├── reporting/               # 结果与报告子系统
│   │   └── ...                      # 其他核心模块
│   ├── agents/                      # 40+ 专业化智能体
│   │   ├── commander_agi.py         # 安全与指挥智能体
│   │   ├── smart_money_trading_agent.py  # SMC/ICT 交易
│   │   ├── autonomous_fullstack_dev_agent.py  # 自主开发
│   │   ├── web_automation_agent.py  # 浏览器自动化
│   │   ├── dynamic_agent_factory.py # 运行时智能体创建
│   │   └── ...                      # 另外 35+ 智能体
│   ├── api/                         # REST 与 WebSocket API
│   │   ├── app.py                   # Flask/FastAPI 服务器
│   │   ├── websocket.py             # WebSocket 处理器
│   │   └── endpoints/               # API 端点模块
│   └── integrations/                # AI 框架集成
│       ├── camel_ai_integration.py
│       ├── autogen_integration.py
│       ├── crewai_integration.py
│       ├── langgraph_integration.py
│       ├── supabase_integration.py
│       └── netlify_integration.py
├── connectors/                      # 外部连接器
│   ├── mcp_connector.py             # 模型上下文协议
│   └── llm_gateway.py               # 多供应商 LLM 网关
├── web-interface/                   # Next.js 仪表盘
│   ├── src/                         # React/Next.js 源码
│   ├── templates/                   # Flask HTML 模板
│   ├── static/                      # CSS、JS、图标
│   └── package.json
├── config/                          # 配置文件
│   ├── system_config.yaml
│   ├── agent_templates.yaml
│   └── prompts.yaml
├── data/                            # 运行时数据（已 gitignore）
├── database/                        # 数据库模型与初始化
├── docs/                            # 文档
├── examples/                        # 使用示例
├── scripts/                         # 实用脚本
├── sandbox/                         # 沙盒管理器
├── requirements.txt                 # Python 依赖
├── docker-compose.yml               # Docker 配置
├── Dockerfile                       # 容器定义
└── LICENSE                          # MIT 许可证
```

---

## 智能体目录

以下是生态系统中可用关键智能体的详细目录。每个智能体由注册表自动发现，可通过 API 端点或 Web 仪表盘访问。

| 智能体 | ID | 类别 | 描述 |
|--------|----|------|------|
| Commander AGI | `commander_agi` | 指挥与控制 | 高级安全监控、威胁检测、系统健康追踪和自主任务协调，支持实时网络分析和事件响应 |
| Smart Money Trading | `smart_money_trading_agent` | 交易与金融 | 使用 Smart Money Concepts（SMC）和 ICT 方法论进行机构级交易——订单块、公允价值缺口、流动性池、多时间框架分析 |
| Autonomous Fullstack Dev | `autonomous_fullstack_dev_agent` | 开发 | 自主开发智能体，持续分析系统、识别改进、进行研究并自主执行代码变更 |
| Web Automation | `web_automation_agent` | Web 自动化 | 基于 Selenium 的浏览器自动化，支持凭证管理、自动登录/注册、表单填充和 Web 交互功能 |
| Dynamic Agent Factory | `dynamic_agent_factory` | 智能体创建 | 从模板运行时生成智能体，支持能力注入、自定义配置和自动注册表集成 |
| Enhanced Agent Creator | `enhanced_agent_creator` | 智能体创建 | 高级智能体构建器，支持模板管理、验证和部署自动化 |
| Meta Agent Creator | `meta_agent_creator` | 智能体创建 | 创建其他智能体创建器——用于生成专业化智能体工厂的元级工厂 |
| Chatbot Agent | `chatbot_agent` | 通信 | 对话式 AI 智能体，支持会话管理、上下文追踪和多轮对话 |
| Deployment Agent | `deployment_agent` | 运维 | 自动化部署流水线管理，支持环境配置和回滚 |
| Deploy Manager | `deploy_manager` | 运维 | 跨多环境和平台的集中式部署编排 |
| Auto Deployment System | `auto_deployment_system` | 运维 | 完全自主部署系统，支持健康检查、金丝雀发布和自动回滚 |
| Authentication Agent | `authentication_agent` | 安全 | 用户认证流程、令牌管理和访问控制执行 |
| Credential Manager | `credential_manager` | 安全 | 加密凭证存储、检索和生命周期管理，支持使用追踪 |
| Auto Redactor | `auto_redactor_agent` | 安全 | 自动检测和脱敏智能体输出及日志中的敏感信息 |
| AI Research Agent | `ai_research_agent` | 研究 | 自主 AI 研究，支持文献综述、假设生成和实验设计 |
| Knowledge Management | `knowledge_management_agent` | 研究 | 知识库策划、检索增强生成和信息生命周期管理 |
| CAMEL Agent Integration | `camel_agent_integration` | 研究 | CAMEL AI 协作推理框架的桥接，用于多智能体对话 |
| Fullstack Dev | `fullstack_dev` | 开发 | 通用全栈开发智能体，支持代码生成和调试 |
| Fullstack Agent | `fullstack_agent` | 开发 | 从需求到部署的端到端开发 |
| Dev Engine | `dev_engine` | 开发 | 开发任务执行引擎，支持测试和 CI/CD 集成 |
| System Supervisor | `system_supervisor` | 系统 | 高级系统监控、健康检查和自动修复 |
| System Optimizer | `system_optimizer` | 系统 | 性能分析、资源优化和配置调优 |
| Autonomous Maintainer | `autonomous_maintainer` | 系统 | 自愈系统维护，支持日志轮转、缓存清理和依赖更新 |
| Bug Hunter Bot | `bug_hunter_bot` | 系统 | 自动缺陷检测、复现和报告，支持严重性分类 |
| Quality Control Specialist | `quality_control_specialist` | 质量 | 代码审查、测试监督和质量指标执行 |
| Marketing Agent | `marketing_agent` | 营销 | 内容生成、活动管理和社交媒体自动化 |
| UI Designer | `ui_designer` | 设计 | 可视化界面设计生成，支持组件库集成 |
| Agent 05 Designer | `agent_05_designer` | 设计 | 专业化 UI/UX 设计智能体，面向仪表盘和控制面板界面 |
| Backup Colony System | `backup_colony_system` | 运维 | 自动备份、灾难恢复和数据复制 |
| Data Sync | `data_sync` | 运维 | 跨系统数据同步和一致性管理 |
| LLM Provider Manager | `llm_provider_manager` | 基础设施 | 多供应商 LLM 配置、健康监控和成本追踪 |
| Prompt Generator | `prompt_generator` | 基础设施 | 自动化提示词工程、优化和模板管理 |
| CyberShell | `cybershell` | 安全 | 高级 Shell 和终端自动化，支持安全审计 |
| Launcher Agent | `launcher_agent` | 基础设施 | 系统启动编排和服务依赖管理 |
| AGI Colony Connector | `agi_colony_connector` | 集成 | 跨群体通信和独立部署间的资源共享 |
| Output Handler | `output_handler` | 系统 | 结果格式化、交付和持久化管理 |
| Agent 02 Meta Spawner | `agent_02_meta_spawner` | 智能体创建 | 根据系统需求和工作负载分析生成其他智能体的元智能体 |
| Agent 03 Planner | `agent_03_planner` | 规划 | 战略任务规划，支持依赖解析和资源分配 |
| Agent 04 Executor | `agent_04_executor` | 执行 | 任务执行引擎，支持重试逻辑和错误恢复 |
| Agent 06 Specialist | `agent_06_specialist` | 专家 | 用于定向任务执行的领域专家智能体 |
| Money Making Orchestrator | `money_making_orchestrator` | 交易 | 编排多个创收智能体和策略 |
| Autonomous Money Ecosystem | `autonomous_money_making_ecosystem` | 交易 | 完整的自主创收系统，支持市场分析和执行 |
| Code Executor | `code_executor` | 开发 | 安全代码执行环境，支持沙盒化和结果验证 |
| Advanced Agent Creator | `advanced_agent_creator` | 智能体创建 | 复杂智能体构建器，支持 ML 驱动的能力建议 |

---

## 贡献

欢迎贡献者！AI-MultiColony-Ecosystem 是一个开源项目，我们积极鼓励社区参与。无论您是想添加新智能体、改进现有智能体、增强 Web 界面还是修复缺陷，都有很多方式可以贡献。

### 如何贡献

1. **Fork 仓库** — 在 [https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem/fork) 创建您自己的 Fork
2. **创建特性分支** — `git checkout -b feature/your-feature-name`
3. **开发您的特性** — 遵循现有代码模式，新智能体需继承自 `BaseAgent`
4. **测试您的变更** — 确保所有现有测试通过，并为您的特性添加新测试
5. **提交 Pull Request** — 清晰描述您的变更并引用相关问题

### 创建新智能体

```python
from colony.core.base_agent import BaseAgent
from colony.core.agent_registry import register_agent

@register_agent(
    name="my_custom_agent",
    description="执行出色操作的自定义智能体",
    route="/api/agents/my_custom_agent"
)
class MyCustomAgent(BaseAgent):
    def __init__(self, name="my_custom_agent", config=None, memory_manager=None):
        super().__init__(name=name, config=config, memory_manager=memory_manager)

    def run(self):
        """智能体主执行逻辑"""
        self.update_status("running")
        # 您的智能体逻辑在此
        self.update_status("completed")

    async def process_task(self, task):
        """处理传入任务"""
        result = {"success": True, "data": "已处理"}
        return self.format_response(str(result))
```

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black colony/ connectors/
```

### 联系方式

如有问题、建议或合作机会，请联系：

- **邮箱**：[mulkymalikuldhaher@email.com](mailto:mulkymalikuldhaher@email.com)
- **GitHub**：[https://github.com/mulkymalikuldhrs](https://github.com/mulkymalikuldhrs)

---

## 联系方式

<p align="center">
  <a href="mailto:mulkymalikuldhaher@email.com">
    <img src="https://img.shields.io/badge/邮箱-mulkymalikuldhaher@email.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="邮箱"/>
  </a>
  <a href="https://github.com/mulkymalikuldhrs">
    <img src="https://img.shields.io/badge/GitHub-mulkymalikuldhrs-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem">
    <img src="https://img.shields.io/badge/仓库-AI--MultiColony--Ecosystem-2E9EF7?style=for-the-badge&logo=github&logoColor=white" alt="仓库"/>
  </a>
  <a href="https://github.com/mulkymalikuldhrs/HermesQuantOS">
    <img src="https://img.shields.io/badge/相关项目-HermesQuantOS-8B5CF6?style=for-the-badge&logo=github&logoColor=white" alt="HermesQuantOS"/>
  </a>
</p>

---

## 许可证

本项目基于 MIT 许可证授权。详见 [LICENSE](./LICENSE) 文件。

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=80&section=footer" alt="页脚波浪"/>
</p>

<p align="center">
  由 <strong>Mulky Malikul Dhaher</strong> 在印度尼西亚 🇮🇩 用 ❤️ 构建
</p>
