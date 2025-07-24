# AI-MultiColony-Ecosystem API Reference

This document provides a comprehensive reference for the AI-MultiColony-Ecosystem API.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8080/api
```

## Authentication

Authentication is not currently implemented. All endpoints are publicly accessible.

## Endpoints

### Agents

#### Get All Agents

```
GET /agents/
```

Returns a list of all registered agents.

**Response**

```json
{
  "status": "success",
  "agents": [
    {
      "id": "fullstack_agent",
      "name": "FullstackAgent",
      "description": "Autonomous agent for fullstack development",
      "status": "idle",
      "route": "/api/agents/fullstack_agent"
    },
    {
      "id": "authentication_agent",
      "name": "AuthenticationAgent",
      "description": "Agent for handling authentication",
      "status": "idle",
      "route": "/api/agents/authentication_agent"
    }
  ]
}
```

#### Get Agent Status

```
GET /agents/{name}/status
```

Returns the status of a specific agent.

**Parameters**

- `name`: Name of the agent

**Response**

```json
{
  "status": "success",
  "agent": {
    "id": "fullstack_agent",
    "name": "FullstackAgent",
    "status": "idle",
    "description": "Autonomous agent for fullstack development"
  }
}
```

#### Run Agent

```
POST /agents/{name}/run
```

Starts running an agent.

**Parameters**

- `name`: Name of the agent

**Request Body**

```json
{
  "agent_name": "fullstack_agent",
  "task_description": "Create a new user registration form"
}
```

**Response**

```json
{
  "status": "success",
  "message": "Agent 'fullstack_agent' started",
  "task_id": "task_12345",
  "task_description": "Create a new user registration form"
}
```

#### Stop Agent

```
POST /agents/{name}/stop
```

Stops a running agent.

**Parameters**

- `name`: Name of the agent

**Response**

```json
{
  "status": "success",
  "message": "Agent 'fullstack_agent' stopped"
}
```

#### Get Agent Logs

```
GET /agents/{name}/logs
```

Returns logs for a specific agent.

**Parameters**

- `name`: Name of the agent
- `limit` (optional): Maximum number of logs to return (default: 10)

**Response**

```json
{
  "status": "success",
  "agent": "fullstack_agent",
  "logs": [
    {
      "timestamp": "2025-07-12T12:00:00",
      "level": "INFO",
      "message": "Agent 'fullstack_agent' initialized"
    },
    {
      "timestamp": "2025-07-12T12:01:00",
      "level": "INFO",
      "message": "Agent 'fullstack_agent' processing task"
    }
  ]
}
```

### Agent Creator

#### Create Agent

```
POST /agent-creator/create
```

Creates a new agent dynamically.

**Request Body**

```json
{
  "name": "MyCustomAgent",
  "prompt_template": "You are a helpful assistant that {task_description}...",
  "config": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "description": "A custom agent that does something amazing"
}
```

**Response**

```json
{
  "status": "success",
  "message": "Agent 'MyCustomAgent' created successfully",
  "agent": {
    "name": "MyCustomAgent",
    "file_path": "/workspace/AI-MultiColony-Ecosystem/colony/agents/mycustomagent.py",
    "config": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }
}
```

## WebSocket Endpoints

### System Updates

```
WebSocket /ws/system
```

Provides real-time system updates.

**Messages**

- `connection_established`: Sent when a client connects to the WebSocket
- `system_update`: Sent when there is a system update
- `echo`: Sent in response to a message from the client

### Agent Logs

```
WebSocket /ws/agent/{agent_id}
```

Provides real-time logs for a specific agent.

**Parameters**

- `agent_id`: ID of the agent

**Messages**

- `connection_established`: Sent when a client connects to the WebSocket
- `agent_log`: Sent when there is a new log entry for the agent
- `echo`: Sent in response to a message from the client

### Chat

```
WebSocket /ws/chat
```

Provides real-time chat functionality.

**Messages**

- `connection_established`: Sent when a client connects to the WebSocket
- `chat_message`: Sent when there is a new chat message
- `echo`: Sent in response to a message from the client

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON object with details:

```json
{
  "status": "error",
  "message": "Error message"
}
```