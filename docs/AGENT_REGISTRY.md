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