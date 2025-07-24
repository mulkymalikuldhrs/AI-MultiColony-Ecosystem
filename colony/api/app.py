"""
🌐 Agentic AI System - Web Interface
Modern Flask-based control panel for multi-agent system

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import json
import logging  # Import logging module
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO, emit

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


# Custom logging handler to emit logs via SocketIO
class SocketIOHandler(logging.Handler):
    def emit(self, record):
        # Use app.app_context() to ensure SocketIO can be accessed
        with app.app_context():
            # Use socketio.emit to send the log record
            # Need to format the record first
            log_entry = self.format(record)
            socketio.emit(
                "system_log",
                {"message": log_entry, "timestamp": datetime.now().isoformat()},
                room="system_updates",
            )


# Configure logging
# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  # Set minimum logging level

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create and add the SocketIO handler
socketio_handler = SocketIOHandler()
socketio_handler.setFormatter(formatter)
root_logger.addHandler(socketio_handler)

# Optional: Add a console handler if you still want logs in the console
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setFormatter(formatter)
# root_logger.addHandler(console_handler)

print("✅ Configured SocketIO logging handler")

# Import system components
try:
    from colony.agents.agent_registry import agent_registry

    print("✅ Agent Registry loaded from colony.agents")
except ImportError:
    print("⚠️ Could not import agent registry from colony.agents")
    agent_registry = None

try:
    from connectors.llm_gateway import llm_gateway

    print("✅ LLM Gateway loaded")
except ImportError:
    print("⚠️ Could not import LLM Gateway")
    llm_gateway = None

try:
    from colony.core.memory_bus import memory_bus

    print("✅ Memory Bus loaded")
except ImportError:
    print("⚠️ Could not import Memory Bus")
    memory_bus = None


# Placeholder for camel_agent if it's still needed for specific logic
# In a fully modular system, camel_agent would also be registered via @register_agent
camel_agent = None
if agent_registry:
    camel_agent = agent_registry.get_agent_class(
        "camel_agent"
    )  # Assuming camel_agent is registered
    if camel_agent:
        print("✅ Camel Agent found in registry")
    else:
        print("⚠️ Camel Agent not found in registry. Ensure it's registered.")
else:
    print("⚠️ Agent registry not available, camel_agent disabled")


# Helper function to safely access agent registry
def safe_agent_registry_call(func_name, *args, **kwargs):
    """Safely call agent registry functions with fallback"""
    if not agent_registry:
        return None
    try:
        func = getattr(agent_registry, func_name)
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Error calling agent_registry.{func_name}: {e}")
        return None


# Create Flask app with correct template and static directories
template_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "web-interface",
    "templates",
)
static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "web-interface",
    "static",
)
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "agentic-ai-system-secret-key-indonesia"
)
socketio = SocketIO(app, cors_allowed_origins="*")

# Import and register launcher API blueprint
try:
    from colony.api.launcher_api import launcher_api

    app.register_blueprint(launcher_api, url_prefix="/api/launcher")
    print("✅ Launcher API registered")
except ImportError as e:
    print(f"⚠️ Could not import launcher API: {e}")

# Global system status
system_status = {
    "status": "running",
    "agents_active": 0,
    "total_agents": 0,
    "last_update": datetime.now().isoformat(),
    "version": "7.0.0",
    "owner": "Mulky Malikul Dhaher",
    "owner_id": "1108151509970001",
}


@app.route("/")
def index():
    """Main dashboard"""
    return render_template("dynamic_dashboard.html")


@app.route("/dashboard")
def dashboard():
    """Ultimate AGI Force Dashboard"""
    return render_template("dynamic_dashboard.html")


@app.route("/agents")
def agents_page():
    """Agents management page"""
    return render_template("agents.html")


@app.route("/workflows")
def workflows():
    """Workflows management page"""
    return render_template("workflows.html")


@app.route("/monitoring")
def monitoring():
    """System monitoring page"""
    return render_template("monitoring.html")


@app.route("/platform_integrations")
def platform_integrations():
    """Platform integrations page"""
    return render_template("platform_integrations.html")


@app.route("/credentials")
def credentials():
    """Credential management page"""
    return render_template("credentials.html")


@app.route("/camel_collaboration")
def camel_collaboration():
    """Camel AI Collaboration page"""
    return render_template("camel_collaboration.html")


# API Routes
@app.route("/api/system/status")
def get_system_status():
    """Get current system status"""
    try:
        # Get additional stats if components are available
        llm_status = {}
        if llm_gateway:
            try:
                llm_status = llm_gateway.get_usage_summary()
            except Exception as llm_e:
                print(f"Error getting LLM usage summary: {llm_e}")
                llm_status = {"total_requests": 0, "total_tokens": 0}

        camel_stats = {}
        if camel_agent:
            try:
                # Assuming camel_agent is an instance or has a static method
                if hasattr(camel_agent, "get_collaboration_stats"):
                    camel_stats = camel_agent.get_collaboration_stats()
                else:
                    print(
                        "Camel Agent instance does not have get_collaboration_stats method."
                    )
            except Exception as camel_e:
                print(f"Error getting Camel Agent stats: {camel_e}")
                camel_stats = {"active_collaborations": 0}

        # Get agent counts from the registry
        total_agents_registered = 0
        active_agents_from_registry = 0
        if agent_registry:
            total_agents_registered = len(agent_registry.get_all_agents())
            # Assuming agents update their status in their metadata
            active_agents_from_registry = len(
                [
                    a
                    for a_name, a_info in agent_registry.get_all_agents().items()
                    if a_info.get("metadata", {}).get("status") == "active"
                ]
            )

        return jsonify(
            {
                "success": True,
                "data": {
                    "system_status": "running",  # Assuming web interface implies system is running
                    "agents_active": active_agents_from_registry,
                    "total_agents": total_agents_registered,
                    "uptime": "active",  # Placeholder
                    "memory_usage": "Normal",  # Placeholder
                    "cpu_usage": "< 25%",  # Placeholder
                    "last_update": datetime.now().isoformat(),
                    "version": "7.0.0",  # Hardcoded for now, should come from config
                    "owner": "Mulky Malikul Dhaher",
                    "owner_id": "1108151509970001",
                    "llm_providers": (
                        len(llm_gateway.providers)
                        if llm_gateway and hasattr(llm_gateway, "providers")
                        else 0
                    ),
                    "llm_requests": llm_status.get("total_requests", 0),
                    "llm_tokens": llm_status.get("total_tokens", 0),
                    "camel_collaborations": camel_stats.get("active_collaborations", 0),
                    "core_components": [
                        "AgentRegistry",
                        "LLMGateway",
                        "MemoryBus",
                    ],  # Example components
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/agents/list")
def list_agents():
    """List all registered agents with their metadata."""
    try:
        agents_list = []
        if not agent_registry:
            return (
                jsonify({"success": False, "error": "Agent registry not available"}),
                500,
            )

        for agent_name, agent_info in agent_registry.get_all_agents().items():
            metadata = agent_info.get("metadata", {})
            agents_list.append(
                {
                    "id": agent_name,
                    "name": metadata.get("name", agent_name),
                    "description": metadata.get(
                        "description", "No description available."
                    ),
                    "route": metadata.get("route", f"/api/agents/{agent_name}"),
                    "dependencies": metadata.get("dependencies", []),
                    "status": metadata.get(
                        "status", "ready"
                    ),  # Default status from metadata
                }
            )

        return jsonify({"success": True, "data": agents_list})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/agents/<agent_id>/status")
def get_agent_status(agent_id):
    """Get specific agent status from registry metadata."""
    try:
        if not agent_registry:
            return (
                jsonify({"success": False, "error": "Agent registry not available"}),
                500,
            )

        agent_info = agent_registry.get_agent_info(agent_id)

        if not agent_info:
            return (
                jsonify({"success": False, "error": "Agent not found in registry"}),
                404,
            )

        # Return metadata as status
        return jsonify({"success": True, "data": agent_info.get("metadata", {})})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/camel/collaborate", methods=["POST"])
def start_camel_collaboration():
    """Start a Camel AI collaboration session"""
    try:
        if not camel_agent:
            return (
                jsonify({"success": False, "error": "Camel Agent not available"}),
                500,
            )

        data = request.get_json()
        topic = data.get("topic", "")
        participants = data.get("participants", ["task_analyst", "solution_architect"])
        complexity = data.get("complexity", "medium")

        if not topic:
            return jsonify({"success": False, "error": "Topic is required"}), 400

        # Create task for camel agent
        task_data = {
            "content": topic,
            "complexity": complexity,
            "participants": participants,
        }

        # Run collaboration asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(camel_agent.process_task(task_data))
        loop.close()

        return jsonify({"success": True, "data": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/camel/stats")
def get_camel_stats():
    """Get Camel AI collaboration statistics"""
    try:
        if not camel_agent:
            return (
                jsonify({"success": False, "error": "Camel Agent not available"}),
                500,
            )

        stats = camel_agent.get_collaboration_stats()

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/prompt/process", methods=["POST"])
def process_prompt():
    """Process a prompt through the system"""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        input_type = data.get("input_type", "text")
        metadata = data.get("metadata", {})
        use_camel = data.get("use_camel", False)

        if not prompt:
            return jsonify({"success": False, "error": "Prompt is required"}), 400

        # Use Camel Agent for collaborative processing if requested
        if use_camel and camel_agent:
            task_data = {
                "content": prompt,
                "complexity": metadata.get("complexity", "medium"),
                "participants": metadata.get(
                    "participants", ["solution_architect", "implementation_expert"]
                ),
            }

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(camel_agent.process_task(task_data))
            loop.close()

            return jsonify(
                {
                    "success": True,
                    "data": result,
                    "processing_method": "camel_collaboration",
                }
            )

        # Use prompt master if available (assuming it's registered as 'prompt_master')
        prompt_master_info = safe_agent_registry_call("get_agent_info", "prompt_master")
        if prompt_master_info:
            prompt_master_class = prompt_master_info.get("class")
            if prompt_master_class:
                # Instantiate if necessary, or get existing instance if managed by a singleton/factory
                # For now, we'll assume it's a class that can be instantiated
                prompt_master_instance = prompt_master_class()

                if hasattr(prompt_master_instance, "process_prompt"):
                    if asyncio.iscoroutinefunction(
                        prompt_master_instance.process_prompt
                    ):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            prompt_master_instance.process_prompt(
                                prompt, input_type, metadata
                            )
                        )
                        loop.close()
                    else:
                        result = prompt_master_instance.process_prompt(
                            prompt, input_type, metadata
                        )
                else:
                    result = {
                        "success": False,
                        "error": "Prompt processing not implemented by prompt_master agent",
                    }
            else:
                result = {
                    "success": False,
                    "error": "Prompt Master agent class not found in registry",
                }
        else:
            # Fallback: try to route to appropriate agent or indicate no prompt master
            result = {
                "success": True,
                "message": "Prompt received but prompt master agent not available or registered",
                "prompt": prompt,
                "suggested_agents": (
                    list(safe_agent_registry_call("get_all_agents", {}).keys())
                    if agent_registry
                    else []
                ),
                "processing_method": "fallback",
            }

        return jsonify({"success": True, "data": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def make_execute_handler(agent_class):
    """Creates a handler function for agent execution."""

    async def execute_handler():
        try:
            data = request.get_json()
            task_data = data.get("task", {})

            # Instantiate the agent class
            agent_instance = agent_class()

            # Execute the agent's process_task method
            if asyncio.iscoroutinefunction(agent_instance.process_task):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(agent_instance.process_task(task_data))
                loop.close()
            else:
                result = agent_instance.process_task(task_data)

            return jsonify(
                {
                    "success": True,
                    "message": f"Task executed by {agent_instance.agent_id}",
                    "result": result,
                }
            )
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return execute_handler


# Dynamically generate agent endpoints
if agent_registry:
    for agent_name, agent_info in agent_registry.get_all_agents().items():
        agent_class = agent_info.get("class")
        metadata = agent_info.get("metadata", {})

        if agent_class and metadata.get("route"):
            endpoint = metadata["route"]
            # Ensure endpoint starts with /api/agents/
            if not endpoint.startswith("/api/agents/"):
                endpoint = f"/api/agents/{agent_name}"  # Fallback to default if route is malformed

            # Flask's add_url_rule requires a unique endpoint name
            # Use agent_name as the endpoint name
            app.add_url_rule(
                endpoint,
                agent_name,
                make_execute_handler(agent_class),
                methods=["POST"],
            )
            print(f"🔗 Dynamically added endpoint: {endpoint} for agent {agent_name}")
else:
    print("⚠️ Agent registry not available, no dynamic endpoints created")


@app.route("/api/task/submit", methods=["POST"])
def submit_task():
    """Submit a task to an agent via its dynamically generated endpoint."""
    try:
        data = request.get_json()
        agent_id = data.get("agent_id")
        task_data = data.get("task", {})

        if not agent_id or not task_data:
            return (
                jsonify({"success": False, "error": "agent_id and task are required"}),
                400,
            )

        agent_info = safe_agent_registry_call("get_agent_info", agent_id)
        if not agent_info:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Agent {agent_id} not found in registry",
                    }
                ),
                404,
            )

        agent_route = agent_info.get("metadata", {}).get("route")
        if not agent_route:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Agent {agent_id} has no defined route",
                    }
                ),
                500,
            )

        # Instead of writing to a file queue, directly call the agent's endpoint
        # This requires the Flask test client or a direct function call if within the same app context
        # For simplicity, we'll simulate a direct call to the handler function
        # In a real-world scenario with separate processes, this would be an HTTP POST to the agent's endpoint

        # For now, we'll directly call the handler function for the agent
        # This is a simplification and assumes the agent's process_task is synchronous or handled by Flask-SocketIO
        # A more robust solution would involve a message queue or inter-process communication

        agent_class = agent_info.get("class")
        if not agent_class:
            return (
                jsonify(
                    {"success": False, "error": f"Agent class for {agent_id} not found"}
                ),
                500,
            )

        agent_instance = agent_class()

        # Execute the agent's process_task method
        if asyncio.iscoroutinefunction(agent_instance.process_task):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(agent_instance.process_task(task_data))
            loop.close()
        else:
            result = agent_instance.process_task(task_data)

        return jsonify(
            {
                "success": True,
                "message": f"Task submitted and executed by {agent_id}",
                "task_result": result,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Remove the old agent_action route as it's replaced by dynamic endpoints
# @app.route('/api/agents/<agent_id>/<action>', methods=['POST'])
# def agent_action(agent_id, action):
#     """Perform action on specific agent"""
#     ... (old code removed)


@app.route("/api/system/emergency-stop", methods=["POST"])
def emergency_stop():
    """Emergency stop all agents by sending a stop signal to each registered agent."""
    try:
        # Try to use unified launcher if available
        try:
            from colony.core.unified_launcher import stop_all

            # Stop all components (web UI, agents, engines)
            results = stop_all()

            # Count stopped agents
            stopped_count = sum(
                1 for agent_name, result in results.get("agents", {}).items() if result
            )

            return jsonify(
                {
                    "success": True,
                    "message": f"Emergency stop initiated for {stopped_count} agents via unified launcher",
                    "stopped_agents": [
                        agent_name
                        for agent_name, result in results.get("agents", {}).items()
                        if result
                    ],
                    "additional_components": {
                        "web_ui": results.get("web_ui", False),
                        "engines": sum(
                            1
                            for result in results.get("engines", {}).values()
                            if result
                        ),
                    },
                }
            )

        except ImportError:
            # Fall back to legacy method if unified launcher is not available
            stopped_agents = []
            all_agents = safe_agent_registry_call("get_all_agents") or {}
            for agent_name, agent_info in all_agents.items():
                agent_class = agent_info.get("class")
                if agent_class and hasattr(
                    agent_class, "stop_agent"
                ):  # Assuming agents have a static stop method
                    agent_class.stop_agent()  # Call a static method to stop
                    stopped_agents.append(agent_name)
                elif agent_class:  # If not static, try to get instance and call stop
                    try:
                        agent_instance = agent_class()
                        if hasattr(
                            agent_instance, "stop"
                        ):  # Assuming an instance method 'stop'
                            agent_instance.stop()
                            stopped_agents.append(agent_name)
                    except Exception as inst_e:
                        print(f"⚠️ Could not stop instance of {agent_name}: {inst_e}")

            return jsonify(
                {
                    "success": True,
                    "message": f"Emergency stop initiated for {len(stopped_agents)} agents",
                    "stopped_agents": stopped_agents,
                }
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/system/restart-all", methods=["POST"])
def restart_all():
    """Restart all agents by sending a restart signal to each registered agent."""
    try:
        # Try to use unified launcher if available
        try:
            from colony.core.unified_launcher import start_all_agents, stop_all_agents

            # Stop all agents first
            stop_results = stop_all_agents()

            # Then start them again
            start_results = start_all_agents(background=True)

            # Count successful restarts
            restarted_count = sum(
                1 for agent_name, result in start_results.items() if result
            )

            return jsonify(
                {
                    "success": True,
                    "message": f"Restart initiated for {restarted_count} agents via unified launcher",
                    "restarted_agents": [
                        agent_name
                        for agent_name, result in start_results.items()
                        if result
                    ],
                }
            )

        except ImportError:
            # Fall back to legacy method if unified launcher is not available
            restarted_agents = []
            all_agents = safe_agent_registry_call("get_all_agents") or {}
            for agent_name, agent_info in all_agents.items():
                agent_class = agent_info.get("class")
                if agent_class and hasattr(
                    agent_class, "restart_agent"
                ):  # Assuming agents have a static restart method
                    agent_class.restart_agent()  # Call a static method to restart
                    restarted_agents.append(agent_name)
                elif agent_class:  # If not static, try to get instance and call restart
                    try:
                        agent_instance = agent_class()
                        if hasattr(
                            agent_instance, "restart"
                        ):  # Assuming an instance method 'restart'
                            agent_instance.restart()
                            restarted_agents.append(agent_name)
                    except Exception as inst_e:
                        print(f"⚠️ Could not restart instance of {agent_name}: {inst_e}")

            return jsonify(
                {
                    "success": True,
                    "message": f"Restart initiated for {len(restarted_agents)} agents",
                    "restarted_agents": restarted_agents,
                }
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/memory/stats")
def get_memory_stats():
    """Get memory bus statistics"""
    try:
        if memory_bus:
            if hasattr(memory_bus, "get_usage_stats"):
                stats = memory_bus.get_usage_stats()
            else:
                stats = {
                    "status": memory_bus.status,
                    "entries": (
                        len(memory_bus.data) if hasattr(memory_bus, "data") else 0
                    ),
                }
            return jsonify({"success": True, "data": stats})
        else:
            return jsonify({"success": False, "error": "Memory bus not available"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# WebSocket Events
@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    print(f"🌐 Client connected: {request.sid}")
    emit(
        "connection_status",
        {
            "status": "connected",
            "message": "🚀 Connected to Ultimate AGI Force",
            "timestamp": datetime.now().isoformat(),
            "system_version": "7.0.0",
            "owner": "Mulky Malikul Dhaher",
            "owner_id": "1108151509970001",
        },
    )


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    print(f"❌ Client disconnected: {request.sid}")


@socketio.on("subscribe_updates")
def handle_subscribe_updates():
    """Subscribe to system updates"""
    from flask_socketio import join_room

    join_room("system_updates")
    emit(
        "subscription_confirmed",
        {"message": "Subscribed to system updates", "room": "system_updates"},
    )


@socketio.on("request_status_update")
def handle_status_request():
    """Handle status update request"""
    try:
        # Get current system status from registry
        all_agents = safe_agent_registry_call("get_all_agents") or {}
        total_agents = len(all_agents)
        active_agents = len(
            [
                a
                for a_name, a_info in all_agents.items()
                if a_info.get("metadata", {}).get("status") == "active"
            ]
        )

        status_data = {
            "agents_count": total_agents,
            "active_agents": active_agents,
            "system_status": "running",  # Assuming web interface implies system is running
            "timestamp": datetime.now().isoformat(),
            "camel_active": camel_agent is not None,
            "llm_gateway_active": llm_gateway is not None,
        }

        emit("status_update", status_data)

    except Exception as e:
        emit("error", {"message": str(e), "timestamp": datetime.now().isoformat()})


# Background monitoring
def background_monitoring():
    """Background monitoring and updates"""
    while True:
        try:
            # Update system status based on agent registry
            all_agents = safe_agent_registry_call("get_all_agents") or {}
            total_agents = len(all_agents)
            active_agents = len(
                [
                    a
                    for a_name, a_info in all_agents.items()
                    if a_info.get("metadata", {}).get("status") == "active"
                ]
            )

            global system_status
            system_status.update(
                {
                    "status": "running",  # Assuming web interface implies system is running
                    "agents_active": active_agents,
                    "total_agents": total_agents,
                    "last_update": datetime.now().isoformat(),
                    "camel_available": camel_agent is not None,
                    "llm_gateway_available": llm_gateway is not None,
                }
            )

            # Emit updates to subscribed clients
            socketio.emit("system_update", system_status, room="system_updates")

            time.sleep(10)  # Update every 10 seconds

        except Exception as e:
            print(f"🔥 Background monitoring error: {e}")
            time.sleep(30)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    print("🚀 Starting Ultimate AGI Force Web Interface v7.0.0")
    print("👑 Owned by: Mulky Malikul Dhaher (1108151509970001)")
    print("🇮🇩 Made with ❤️ in Indonesia")
    port = int(os.getenv("WEB_INTERFACE_PORT", 5000))
    print(f"📊 Dashboard will be available at: http://localhost:{port}")
    agent_count = len(agent_registry.get_all_agents()) if agent_registry else 0
    print(f"🤖 Loaded {agent_count} agents from registry")
    print(f"🐪 Camel Agent: {'✅ Available' if camel_agent else '❌ Not Available'}")
    print(f"🧠 LLM Gateway: {'✅ Available' if llm_gateway else '❌ Not Available'}")
    print(f"💾 Memory Bus: {'✅ Available' if memory_bus else '❌ Not Available'}")

    # Start background monitoring
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()

    # Run the application
    port = int(os.getenv("WEB_INTERFACE_PORT", 5000))
    host = os.getenv("WEB_INTERFACE_HOST", "0.0.0.0")

    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

# ============================================================================
# NEW DYNAMIC DASHBOARD API ENDPOINTS
# ============================================================================


# Chatbot API endpoints
@app.route("/api/chat/message", methods=["POST"])
def chat_message():
    """Process chat message"""
    try:
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        user_id = data.get("user_id", "anonymous")

        # Import chatbot agent
        try:
            # Process message asynchronously
            import asyncio

            from colony.agents.chatbot_agent import chatbot_agent

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                chatbot_agent.process_message(message, session_id, user_id)
            )

            loop.close()

            return jsonify(result)

        except ImportError:
            return jsonify(
                {
                    "success": False,
                    "error": "Chatbot agent not available",
                    "response": "Sorry, the chatbot is currently unavailable.",
                }
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "response": "Sorry, I encountered an error processing your message.",
                }
            ),
            500,
        )


@app.route("/api/chat/history/<session_id>")
def chat_history(session_id):
    """Get chat history for session"""
    try:
        import asyncio

        from colony.agents.chatbot_agent import chatbot_agent

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        history = loop.run_until_complete(
            chatbot_agent.get_conversation_history(session_id)
        )

        loop.close()

        return jsonify({"success": True, "history": history})

    except ImportError:
        return jsonify(
            {"success": False, "error": "Chatbot agent not available", "history": []}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat/clear/<session_id>", methods=["POST"])
def clear_chat(session_id):
    """Clear chat history"""
    try:
        import asyncio

        from colony.agents.chatbot_agent import chatbot_agent

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(chatbot_agent.clear_conversation(session_id))

        loop.close()

        return jsonify(result)

    except ImportError:
        return jsonify({"success": False, "error": "Chatbot agent not available"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Agent Creator API endpoints
@app.route("/api/agents/create", methods=["POST"])
def create_agent():
    """Create new agent"""
    try:
        data = request.get_json()

        # Import enhanced agent creator
        try:
            import asyncio

            from colony.agents.enhanced_agent_creator import enhanced_agent_creator

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(enhanced_agent_creator.create_agent(data))

            loop.close()

            # Emit agent update via SocketIO
            if result.get("success"):
                socketio.emit(
                    "agent_created",
                    {
                        "agent_id": result.get("agent_id"),
                        "message": f"Agent {data.get('name', 'Unknown')} created successfully",
                    },
                )

            return jsonify(result)

        except ImportError:
            return jsonify(
                {"success": False, "error": "Enhanced Agent Creator not available"}
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/agents/templates")
def get_agent_templates():
    """Get available agent templates"""
    try:
        import asyncio

        from colony.agents.enhanced_agent_creator import enhanced_agent_creator

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        templates = loop.run_until_complete(
            enhanced_agent_creator.get_agent_templates()
        )

        loop.close()

        return jsonify({"success": True, "templates": templates})

    except ImportError:
        return jsonify(
            {
                "success": False,
                "error": "Enhanced Agent Creator not available",
                "templates": {},
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/agents/created")
def get_created_agents():
    """Get list of created agents"""
    try:
        import asyncio

        from colony.agents.enhanced_agent_creator import enhanced_agent_creator

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        agents = loop.run_until_complete(enhanced_agent_creator.list_created_agents())

        loop.close()

        return jsonify({"success": True, "agents": agents})

    except ImportError:
        return jsonify(
            {
                "success": False,
                "error": "Enhanced Agent Creator not available",
                "agents": [],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/agents/delete/<agent_id>", methods=["DELETE"])
def delete_agent(agent_id):
    """Delete created agent"""
    try:
        import asyncio

        from colony.agents.enhanced_agent_creator import enhanced_agent_creator

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(enhanced_agent_creator.delete_agent(agent_id))

        loop.close()

        # Emit agent update via SocketIO
        if result.get("success"):
            socketio.emit(
                "agent_deleted",
                {
                    "agent_id": agent_id,
                    "message": f"Agent {agent_id} deleted successfully",
                },
            )

        return jsonify(result)

    except ImportError:
        return jsonify(
            {"success": False, "error": "Enhanced Agent Creator not available"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
