<<<<<<< HEAD
# Agent Registry

Total Agents: 10

- **AdvancedAgentCreator**: Advanced agent creator that creates real working AI agents (Route: /api/agents/advancedagentcreator)
- **DynamicAIAgent**: Dynamically created AI agent with custom capabilities (Route: /api/agents/dynamicaiagent)
- **Agent02MetaSpawner**: Performance monitor and bottleneck analyzer (Route: /api/agents/agent02metaspawner)
- **Agent03Planner**: Specialized planning agent for task breakdown and scheduling (Route: /api/agents/agent03planner)
- **Agent05Designer**: Specialized design agent for visual assets creation (Route: /api/agents/agent05designer)
- **Agent06Specialist**: Domain specialist agent for expert consultation (Route: /api/agents/agent06specialist)
- **AgentBase**: Master controller and task coordinator (Route: /api/agents/agentbase)
- **DynamicAgentFactory**: Creates and manages dynamic agents for specific tasks (Route: /api/agents/dynamicagentfactory)
- **FullstackAgent**: 
Autonomous agent for fullstack development.

This agent can handle both frontend and backend development tasks,
including API development, UI implementation, and integration.
 (Route: /api/agents/fullstackagent)
- **OutputHandler**: 
Orchestrates the final compilation and delivery of agent results
by coordinating a set of specialized components.
 (Route: /api/agents/outputhandler)
=======
# AGENT REGISTRY

## Daftar Agent Terdaftar

Semua agent di bawah ini terdaftar otomatis melalui registry global (`AGENT_REGISTRY`).

```
# Contoh kode auto-register
def register_agent_class(agent_class):
    name = agent_class.__name__
    if name not in AGENT_REGISTRY:
        AGENT_REGISTRY[name] = agent_class
    return agent_class

@register_agent_class
class MyCustomAgent:
    ...
```

## List Agent (auto-generated)

- QuantumProcessorAgent
- QuantumEntanglerAgent
- AwarenessSimulatorAgent
- ReasoningEngineAgent
- PromptArchitectAgent
- ShellVirtuosoAgent
- UIRevolutionaryAgent
- PromptMastermindAgent
- VoiceSynthesizerAgent
- RevenueOptimizerAgent
- GlobalDeploymentAgent
- UltimateGenericAgent

> Untuk menambah agent baru, cukup gunakan dekorator `@register_agent_class` pada class agent Anda.
>>>>>>> main
