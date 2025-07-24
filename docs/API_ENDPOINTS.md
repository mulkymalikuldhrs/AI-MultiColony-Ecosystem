# 🚀 AI-MultiColony-Ecosystem API Endpoints v7.3.0

## 📋 Overview

This document describes all available API endpoints for the AI-MultiColony-Ecosystem v7.3.0, including the new Camel AI integration and unified agent registry system.

## 🌐 Base URL

```
http://localhost:8080/api
```

## 🔐 Authentication

Currently, the API uses session-based authentication through the web interface. Future versions will include API key authentication.

## 📊 Core System Endpoints

### GET /api/system/status
Get basic system status information.

**Response:**
```json
{
  "success": true,
  "data": {
    "system_status": "running",
    "agents_active": 15,
    "total_agents": 23,
    "uptime": "2h 30m",
    "memory_usage": "1.2GB",
    "cpu_usage": "< 25%",
    "last_update": "2025-01-08T10:30:00Z",
    "version": "7.3.0",
    "llm_providers": 3
  }
}
```

### GET /api/system/comprehensive-status
Get comprehensive system status including all components.

**Response:**
```json
{
  "timestamp": "2025-01-08T10:30:00Z",
  "version": "7.3.0",
  "system_status": {
    "status": "running",
    "agents_active": 15,
    "total_agents": 23,
    "uptime": 9000,
    "last_update": "2025-01-08T10:30:00Z"
  },
  "unified_registry": {
    "available": true,
    "statistics": {
      "total_agent_classes": 50,
      "active_instances": 15,
      "registry_classes": ["CamelAIAgent", "DevAgent", "ChatAgent"],
      "active_instance_names": ["default_camel_agent", "dev_assistant"]
    }
  },
  "camel_integration": {
    "available": true,
    "status": {
      "integration_status": "initialized",
      "camel_ai_available": true,
      "total_agents": 5,
      "active_agents": 3,
      "agent_list": ["default_camel_agent", "research_agent"]
    }
  }
}
```

## 🤖 Agent Management Endpoints

### GET /api/agents/list
Get list of legacy agents.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "dev_engine",
      "name": "Development Engine",
      "status": "ready",
      "capabilities": ["code_generation", "debugging"],
      "agent_id": "dev_engine"
    }
  ]
}
```

### GET /api/agents/unified
Get comprehensive agent information from all registries.

**Response:**
```json
{
  "unified_registry": {
    "available": true,
    "agent_classes": ["CamelAIAgent", "DevAgent", "ChatAgent"],
    "active_instances": ["default_camel_agent", "dev_assistant"],
    "statistics": {
      "total_agent_classes": 50,
      "active_instances": 15
    }
  },
  "camel_integration": {
    "available": true,
    "agents": ["default_camel_agent", "research_agent"],
    "status": {
      "integration_status": "initialized",
      "total_agents": 5,
      "active_agents": 3
    }
  },
  "legacy_registry": {
    "available": true,
    "agents": ["dev_engine", "ui_designer"]
  }
}
```

### POST /api/agents/create
Create a new agent instance.

**Request Body:**
```json
{
  "type": "camel",
  "name": "my_custom_agent",
  "config": {
    "model_type": "gpt-4-turbo",
    "role_type": "assistant"
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent_name": "my_custom_agent",
  "agent_type": "camel",
  "status": {
    "name": "my_custom_agent",
    "status": "ready",
    "camel_ai_available": true,
    "model_type": "gpt-4-turbo",
    "conversation_count": 0,
    "uptime": 0
  }
}
```

### POST /api/agents/{agent_id}/task
Execute a task on a specific agent.

**Request Body:**
```json
{
  "task_type": "code_generation",
  "task_data": {
    "prompt": "Create a Python function to calculate fibonacci numbers",
    "language": "python"
  }
}
```

## 💬 Chat and Conversation Endpoints

### POST /api/chat
Chat with Camel AI integrated agents.

**Request Body:**
```json
{
  "message": "Hello, can you help me with Python programming?",
  "agent": "default_camel_agent",
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "response": "Hello! I'd be happy to help you with Python programming. What specific topic or problem would you like assistance with?",
  "agent": "default_camel_agent",
  "timestamp": "2025-01-08T10:30:00Z",
  "status": "success"
}
```

### POST /api/prompt/process
Process a prompt through the system.

**Request Body:**
```json
{
  "prompt": "Generate a REST API for user management",
  "input_type": "text",
  "metadata": {
    "framework": "flask",
    "database": "postgresql"
  }
}
```

## 🔗 LLM Provider Endpoints

### GET /api/llm/providers
Get LLM provider status and usage information.

**Response:**
```json
{
  "success": true,
  "data": {
    "providers": {
      "openai": {
        "status": "active",
        "models": ["gpt-4", "gpt-3.5-turbo"],
        "requests_today": 150
      },
      "anthropic": {
        "status": "active",
        "models": ["claude-3"],
        "requests_today": 75
      }
    },
    "usage": {
      "total_requests": 225,
      "total_tokens": 150000,
      "cost_estimate": "$12.50"
    }
  }
}
```

## 🔧 Configuration Endpoints

### GET /api/config/system
Get system configuration.

### POST /api/config/system
Update system configuration.

### GET /api/config/agents
Get agent-specific configurations.

## 📊 Monitoring and Analytics

### GET /api/monitoring/metrics
Get system performance metrics.

### GET /api/monitoring/logs
Get system logs with filtering options.

### GET /api/analytics/usage
Get usage analytics and statistics.

## 🚀 WebSocket Endpoints

### /socket.io/
Real-time communication for:
- Live agent status updates
- Chat conversations
- System monitoring
- Task progress updates

**Events:**
- `agent_status_update`
- `chat_message`
- `system_alert`
- `task_progress`

## 🔒 Security Considerations

1. **Rate Limiting**: All endpoints have rate limiting to prevent abuse
2. **Input Validation**: All inputs are validated and sanitized
3. **Error Handling**: Comprehensive error handling with proper HTTP status codes
4. **Logging**: All API calls are logged for monitoring and debugging

## 📝 Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request - Invalid input |
| 401  | Unauthorized - Authentication required |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource not found |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error |

## 🔄 Versioning

API versioning follows semantic versioning. Current version: `v7.3.0`

## 📚 Examples

### Creating and Chatting with a Camel AI Agent

```bash
# Create a new Camel AI agent
curl -X POST http://localhost:8080/api/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "type": "camel",
    "name": "coding_assistant",
    "config": {
      "model_type": "gpt-4-turbo",
      "role_type": "assistant"
    }
  }'

# Chat with the agent
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function to sort a list",
    "agent": "coding_assistant"
  }'
```

### Getting System Status

```bash
curl http://localhost:8080/api/system/comprehensive-status
```

## 🆕 What's New in v7.3.0

- ✅ Camel AI integration with `/api/chat` endpoint
- ✅ Unified agent registry with `/api/agents/unified`
- ✅ Enhanced agent creation with `/api/agents/create`
- ✅ Comprehensive system status with `/api/system/comprehensive-status`
- ✅ Real-time WebSocket updates
- ✅ Improved error handling and validation
- ✅ Better documentation and examples

---

For technical support, visit our [GitHub repository](https://github.com/mulkymalikuldhrs/AI-MultiColony-Ecosystem) or contact the development team.