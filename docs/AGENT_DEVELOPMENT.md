# AI-MultiColony-Ecosystem Agent Development Guide

This document provides a guide for developing agents for the AI-MultiColony-Ecosystem.

## Overview

Agents are the core components of the AI-MultiColony-Ecosystem. They are responsible for performing specific tasks and can be combined to create complex workflows.

## Agent Structure

Agents in the AI-MultiColony-Ecosystem follow a standard structure:

```python
from colony.core.base_agent import BaseAgent

class MyAgent(BaseAgent):
    """
    My custom agent.
    """
    
    def __init__(self, name=None, config=None, memory=None):
        """Initialize the agent."""
        super().__init__(name or "MyAgent", config, memory)
        
        # Default configuration
        self.default_config = {
            "parameter1": "value1",
            "parameter2": "value2"
        }
        
        # Merge with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize memory if not provided
        self.memory = memory or {}
    
    async def run(self, task):
        """
        Run the agent on a task.
        
        Args:
            task: Task to run
            
        Returns:
            Task result
        """
        try:
            # Process task
            result = self._process_task(task)
            
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            return self.handle_error(e, task)
    
    def _process_task(self, task):
        """
        Process a task.
        
        Args:
            task: Task to process
            
        Returns:
            Task result
        """
        # Implement task processing logic here
        return "Task processed"
    
    def handle_error(self, error, task):
        """
        Handle an error.
        
        Args:
            error: Error to handle
            task: Task that caused the error
            
        Returns:
            Error result
        """
        return {
            "status": "error",
            "message": str(error),
            "task": task
        }
```

## Creating a New Agent

### Manual Creation

To create a new agent manually, follow these steps:

1. Create a new Python file in the `colony/agents` directory
2. Define a new class that inherits from `BaseAgent`
3. Implement the required methods
4. Register the agent in the agent registry

### Using the Agent Creator

The AI-MultiColony-Ecosystem provides an agent creator API that can be used to create agents dynamically:

```python
from colony.api.endpoints.agent_creator import create_agent

# Create a new agent
response = create_agent({
    "name": "MyCustomAgent",
    "prompt_template": "You are a helpful assistant that {task_description}...",
    "config": {
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "description": "A custom agent that does something amazing"
})
```

## Agent Registration

Agents are automatically registered in the agent registry when they are imported. The agent registry is responsible for managing agent instances and providing access to them.

### Manual Registration

To register an agent manually, use the `register_agent` decorator:

```python
from colony.core.agent_registry import register_agent

@register_agent
class MyAgent(BaseAgent):
    """
    My custom agent.
    """
    # ...
```

### Accessing Registered Agents

To access registered agents, use the agent registry:

```python
from colony.core.agent_registry import get_agent, list_all_agents

# Get a specific agent
agent_class = get_agent("my_agent")
agent = agent_class()

# List all agents
agents = list_all_agents()
```

## Agent Configuration

Agents can be configured using a configuration dictionary. The configuration is passed to the agent constructor and merged with the default configuration.

```python
# Create an agent with custom configuration
agent = MyAgent(config={
    "parameter1": "custom_value1",
    "parameter2": "custom_value2"
})
```

## Agent Memory

Agents can store and retrieve data using the memory dictionary. The memory is passed to the agent constructor and can be accessed and modified during agent execution.

```python
# Create an agent with custom memory
agent = MyAgent(memory={
    "key1": "value1",
    "key2": "value2"
})

# Access memory
value = agent.memory["key1"]

# Modify memory
agent.memory["key3"] = "value3"
```

## Agent Execution

Agents are executed using the `run` method. The method takes a task dictionary as input and returns a result dictionary.

```python
# Execute an agent
result = await agent.run({
    "task_id": "task_12345",
    "type": "my_task_type",
    "description": "My task description",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    }
})
```

## Agent Communication

Agents can communicate with each other using the memory bus. The memory bus is a shared memory space that allows agents to exchange data.

```python
from colony.core.memory_bus import memory_bus

# Store data in the memory bus
memory_bus.store("key1", "value1")

# Retrieve data from the memory bus
value = memory_bus.retrieve("key1")
```

## Agent Logging

Agents can log messages using the standard Python logging module. The logs are automatically captured and can be viewed in the agent logs.

```python
import logging

# Get a logger
logger = logging.getLogger("agents.my_agent")

# Log a message
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
```

## Agent Testing

Agents can be tested using the standard Python testing framework. The AI-MultiColony-Ecosystem provides a test framework for testing agents.

```python
import unittest
from colony.core.agent_registry import get_agent

class TestMyAgent(unittest.TestCase):
    def setUp(self):
        # Get the agent class
        agent_class = get_agent("my_agent")
        
        # Create an agent instance
        self.agent = agent_class()
    
    async def test_run(self):
        # Define a test task
        task = {
            "task_id": "test_task",
            "type": "test",
            "description": "Test task"
        }
        
        # Run the agent
        result = await self.agent.run(task)
        
        # Check the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "Task processed")
```

## Best Practices

- **Separation of Concerns**: Each agent should have a single responsibility
- **Error Handling**: Always handle errors and return appropriate error responses
- **Configuration**: Use configuration to make agents flexible and reusable
- **Memory Management**: Use memory to store and retrieve data between agent executions
- **Logging**: Use logging to track agent execution and debug issues
- **Testing**: Write tests for agents to ensure they work as expected

## License

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩