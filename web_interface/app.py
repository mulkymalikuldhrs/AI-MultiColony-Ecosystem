"""
🌐 Agentic AI System - Web Interface
Modern Flask-based control panel for multi-agent system

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import json
import sys
import os
import asyncio
from datetime import datetime
import threading
import time
from pathlib import Path
import logging # Import logging module

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
            socketio.emit('system_log', {'message': log_entry, 'timestamp': datetime.now().isoformat()}, room='system_updates')

# Configure logging
# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO) # Set minimum logging level

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
from src.agents.agent_registry import agent_registry
from connectors.llm_gateway import llm_gateway
from core.memory_bus import memory_bus

print("✅ Agent Registry loaded")
print("✅ LLM Gateway loaded")
print("✅ Memory Bus loaded")

# Placeholder for camel_agent if it's still needed for specific logic
# In a fully modular system, camel_agent would also be registered via @register_agent
camel_agent = agent_registry.get_agent_class("camel_agent") # Assuming camel_agent is registered
if camel_agent:
    print("✅ Camel Agent found in registry")
else:
    print("⚠️ Camel Agent not found in registry. Ensure it's registered.")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'agentic-ai-system-secret-key-indonesia')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global system status
system_status = {
    'status': 'running',
    'agents_active': 0,
    'total_agents': 0,
    'last_update': datetime.now().isoformat(),
    'version': '7.0.0',
    'owner': 'Mulky Malikul Dhaher',
    'owner_id': '1108151509970001'
}

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('enhanced_index.html')

@app.route('/dashboard')
def dashboard():
    """Ultimate AGI Force Dashboard"""
    return render_template('dashboard.html')

@app.route('/agents')
def agents_page():
    """Agents management page"""
    return render_template('agents.html')

@app.route('/workflows')
def workflows():
    """Workflows management page"""
    return render_template('workflows.html')

@app.route('/monitoring')
def monitoring():
    """System monitoring page"""
    return render_template('monitoring.html')

@app.route('/platform_integrations')
def platform_integrations():
    """Platform integrations page"""
    return render_template('platform_integrations.html')

@app.route('/credentials')
def credentials():
    """Credential management page"""
    return render_template('credentials.html')

@app.route('/camel_collaboration')
def camel_collaboration():
    """Camel AI Collaboration page"""
    return render_template('camel_collaboration.html')

# API Routes
@app.route('/api/system/status')
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
                llm_status = {'total_requests': 0, 'total_tokens': 0}
        
        camel_stats = {}
        if camel_agent:
            try:
                # Assuming camel_agent is an instance or has a static method
                if hasattr(camel_agent, 'get_collaboration_stats'):
                    camel_stats = camel_agent.get_collaboration_stats()
                else:
                    print("Camel Agent instance does not have get_collaboration_stats method.")
            except Exception as camel_e:
                print(f"Error getting Camel Agent stats: {camel_e}")
                camel_stats = {'active_collaborations': 0}
        
        # Get agent counts from the registry
        total_agents_registered = len(agent_registry.get_all_agents())
        # Assuming agents update their status in their metadata
        active_agents_from_registry = len([
            a for a_name, a_info in agent_registry.get_all_agents().items() 
            if a_info.get('metadata', {}).get('status') == 'active'
        ])

        return jsonify({
            'success': True,
            'data': {
                'system_status': 'running', # Assuming web interface implies system is running
                'agents_active': active_agents_from_registry,
                'total_agents': total_agents_registered,
                'uptime': 'active', # Placeholder
                'memory_usage': 'Normal', # Placeholder
                'cpu_usage': '< 25%', # Placeholder
                'last_update': datetime.now().isoformat(),
                'version': '7.0.0', # Hardcoded for now, should come from config
                'owner': 'Mulky Malikul Dhaher',
                'owner_id': '1108151509970001',
                'llm_providers': len(llm_gateway.providers) if llm_gateway and hasattr(llm_gateway, 'providers') else 0,
                'llm_requests': llm_status.get('total_requests', 0),
                'llm_tokens': llm_status.get('total_tokens', 0),
                'camel_collaborations': camel_stats.get('active_collaborations', 0),
                'core_components': ['AgentRegistry', 'LLMGateway', 'MemoryBus'] # Example components
            }
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/list')
def list_agents():
    """List all registered agents with their metadata."""
    try:
        agents_list = []
        for agent_name, agent_info in agent_registry.get_all_agents().items():
            metadata = agent_info.get('metadata', {})
            agents_list.append({
                'id': agent_name,
                'name': metadata.get('name', agent_name),
                'description': metadata.get('description', 'No description available.'),
                'route': metadata.get('route', f'/api/agents/{agent_name}'),
                'dependencies': metadata.get('dependencies', []),
                'status': metadata.get('status', 'ready') # Default status from metadata
            })
        
        return jsonify({
            'success': True,
            'data': agents_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>/status')
def get_agent_status(agent_id):
    """Get specific agent status from registry metadata."""
    try:
        agent_info = agent_registry.get_agent_info(agent_id)
        
        if not agent_info:
            return jsonify({
                'success': False,
                'error': 'Agent not found in registry'
            }), 404
        
        # Return metadata as status
        return jsonify({
            'success': True,
            'data': agent_info.get('metadata', {})
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camel/collaborate', methods=['POST'])
def start_camel_collaboration():
    """Start a Camel AI collaboration session"""
    try:
        if not camel_agent:
            return jsonify({
                'success': False,
                'error': 'Camel Agent not available'
            }), 500
        
        data = request.get_json()
        topic = data.get('topic', '')
        participants = data.get('participants', ['task_analyst', 'solution_architect'])
        complexity = data.get('complexity', 'medium')
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Create task for camel agent
        task_data = {
            'content': topic,
            'complexity': complexity,
            'participants': participants
        }
        
        # Run collaboration asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(camel_agent.process_task(task_data))
        loop.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camel/stats')
def get_camel_stats():
    """Get Camel AI collaboration statistics"""
    try:
        if not camel_agent:
            return jsonify({
                'success': False,
                'error': 'Camel Agent not available'
            }), 500
        
        stats = camel_agent.get_collaboration_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/prompt/process', methods=['POST'])
def process_prompt():
    """Process a prompt through the system"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        input_type = data.get('input_type', 'text')
        metadata = data.get('metadata', {})
        use_camel = data.get('use_camel', False)
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Use Camel Agent for collaborative processing if requested
        if use_camel and camel_agent:
            task_data = {
                'content': prompt,
                'complexity': metadata.get('complexity', 'medium'),
                'participants': metadata.get('participants', ['solution_architect', 'implementation_expert'])
            }
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(camel_agent.process_task(task_data))
            loop.close()
            
            return jsonify({
                'success': True,
                'data': result,
                'processing_method': 'camel_collaboration'
            })
        
        # Use prompt master if available (assuming it's registered as 'prompt_master')
        prompt_master_info = agent_registry.get_agent_info('prompt_master')
        if prompt_master_info:
            prompt_master_class = prompt_master_info.get('class')
            if prompt_master_class:
                # Instantiate if necessary, or get existing instance if managed by a singleton/factory
                # For now, we'll assume it's a class that can be instantiated
                prompt_master_instance = prompt_master_class() 
                
                if hasattr(prompt_master_instance, 'process_prompt'):
                    if asyncio.iscoroutinefunction(prompt_master_instance.process_prompt):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            prompt_master_instance.process_prompt(prompt, input_type, metadata)
                        )
                        loop.close()
                    else:
                        result = prompt_master_instance.process_prompt(prompt, input_type, metadata)
                else:
                    result = {
                        'success': False,
                        'error': 'Prompt processing not implemented by prompt_master agent'
                    }
            else:
                result = {
                    'success': False,
                    'error': 'Prompt Master agent class not found in registry'
                }
        else:
            # Fallback: try to route to appropriate agent or indicate no prompt master
            result = {
                'success': True,
                'message': 'Prompt received but prompt master agent not available or registered',
                'prompt': prompt,
                'suggested_agents': list(agent_registry.get_all_agents().keys()),
                'processing_method': 'fallback'
            }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/llm/providers')
def get_llm_providers():
    """Get LLM provider status"""
    try:
        if llm_gateway:
            status = llm_gateway.get_provider_status()
            usage = llm_gateway.get_usage_summary()
            
            return jsonify({
                'success': True,
                'data': {
                    'providers': status,
                    'usage': usage,
                    'gateway_status': llm_gateway.status
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'LLM Gateway not available'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/llm/test', methods=['POST'])
def test_llm_providers():
    """Test all LLM providers"""
    try:
        if not llm_gateway:
            return jsonify({
                'success': False,
                'error': 'LLM Gateway not available'
            }), 500
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        test_results = loop.run_until_complete(llm_gateway.test_all_providers())
        loop.close()
        
        return jsonify({
            'success': True,
            'data': test_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def make_execute_handler(agent_class):
    """Creates a handler function for agent execution."""
    async def execute_handler():
        try:
            data = request.get_json()
            task_data = data.get('task', {})
            
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
            
            return jsonify({
                'success': True,
                'message': f'Task executed by {agent_instance.agent_id}',
                'result': result
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    return execute_handler

# Dynamically generate agent endpoints
for agent_name, agent_info in agent_registry.get_all_agents().items():
    agent_class = agent_info.get('class')
    metadata = agent_info.get('metadata', {})
    
    if agent_class and metadata.get('route'):
        endpoint = metadata['route']
        # Ensure endpoint starts with /api/agents/
        if not endpoint.startswith('/api/agents/'):
            endpoint = f'/api/agents/{agent_name}' # Fallback to default if route is malformed
        
        # Flask's add_url_rule requires a unique endpoint name
        # Use agent_name as the endpoint name
        app.add_url_rule(endpoint, agent_name, make_execute_handler(agent_class), methods=['POST'])
        print(f"🔗 Dynamically added endpoint: {endpoint} for agent {agent_name}")

@app.route('/api/task/submit', methods=['POST'])
def submit_task():
    """Submit a task to an agent via its dynamically generated endpoint."""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})

        if not agent_id or not task_data:
            return jsonify({'success': False, 'error': 'agent_id and task are required'}), 400

        agent_info = agent_registry.get_agent_info(agent_id)
        if not agent_info:
            return jsonify({'success': False, 'error': f'Agent {agent_id} not found in registry'}), 404

        agent_route = agent_info.get('metadata', {}).get('route')
        if not agent_route:
            return jsonify({'success': False, 'error': f'Agent {agent_id} has no defined route'}), 500

        # Instead of writing to a file queue, directly call the agent's endpoint
        # This requires the Flask test client or a direct function call if within the same app context
        # For simplicity, we'll simulate a direct call to the handler function
        # In a real-world scenario with separate processes, this would be an HTTP POST to the agent's endpoint
        
        # For now, we'll directly call the handler function for the agent
        # This is a simplification and assumes the agent's process_task is synchronous or handled by Flask-SocketIO
        # A more robust solution would involve a message queue or inter-process communication
        
        agent_class = agent_info.get('class')
        if not agent_class:
            return jsonify({'success': False, 'error': f'Agent class for {agent_id} not found'}), 500
        
        agent_instance = agent_class()
        
        # Execute the agent's process_task method
        if asyncio.iscoroutinefunction(agent_instance.process_task):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(agent_instance.process_task(task_data))
            loop.close()
        else:
            result = agent_instance.process_task(task_data)

        return jsonify({
            'success': True,
            'message': f'Task submitted and executed by {agent_id}',
            'task_result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Remove the old agent_action route as it's replaced by dynamic endpoints
# @app.route('/api/agents/<agent_id>/<action>', methods=['POST'])
# def agent_action(agent_id, action):
#     """Perform action on specific agent"""
#     ... (old code removed)

@app.route('/api/system/emergency-stop', methods=['POST'])
def emergency_stop():
    """Emergency stop all agents by sending a stop signal to each registered agent."""
    try:
        stopped_agents = []
        for agent_name, agent_info in agent_registry.get_all_agents().items():
            agent_class = agent_info.get('class')
            if agent_class and hasattr(agent_class, 'stop_agent'): # Assuming agents have a static stop method
                agent_class.stop_agent() # Call a static method to stop
                stopped_agents.append(agent_name)
            elif agent_class: # If not static, try to get instance and call stop
                try:
                    agent_instance = agent_class()
                    if hasattr(agent_instance, 'stop'): # Assuming an instance method 'stop'
                        agent_instance.stop()
                        stopped_agents.append(agent_name)
                except Exception as inst_e:
                    print(f"⚠️ Could not stop instance of {agent_name}: {inst_e}")
        
        return jsonify({
            'success': True,
            'message': f'Emergency stop initiated for {len(stopped_agents)} agents',
            'stopped_agents': stopped_agents
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/restart-all', methods=['POST'])
def restart_all():
    """Restart all agents by sending a restart signal to each registered agent."""
    try:
        restarted_agents = []
        for agent_name, agent_info in agent_registry.get_all_agents().items():
            agent_class = agent_info.get('class')
            if agent_class and hasattr(agent_class, 'restart_agent'): # Assuming agents have a static restart method
                agent_class.restart_agent() # Call a static method to restart
                restarted_agents.append(agent_name)
            elif agent_class: # If not static, try to get instance and call restart
                try:
                    agent_instance = agent_class()
                    if hasattr(agent_instance, 'restart'): # Assuming an instance method 'restart'
                        agent_instance.restart()
                        restarted_agents.append(agent_name)
                except Exception as inst_e:
                    print(f"⚠️ Could not restart instance of {agent_name}: {inst_e}")

        return jsonify({
            'success': True,
            'message': f'Restart initiated for {len(restarted_agents)} agents',
            'restarted_agents': restarted_agents
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/memory/stats')
def get_memory_stats():
    """Get memory bus statistics"""
    try:
        if memory_bus:
            if hasattr(memory_bus, 'get_usage_stats'):
                stats = memory_bus.get_usage_stats()
            else:
                stats = {
                    'status': memory_bus.status,
                    'entries': len(memory_bus.data) if hasattr(memory_bus, 'data') else 0
                }
            return jsonify({
                'success': True,
                'data': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Memory bus not available'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'🌐 Client connected: {request.sid}')
    emit('connection_status', {
        'status': 'connected',
        'message': '🚀 Connected to Ultimate AGI Force',
        'timestamp': datetime.now().isoformat(),
        'system_version': '7.0.0',
        'owner': 'Mulky Malikul Dhaher',
        'owner_id': '1108151509970001'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'❌ Client disconnected: {request.sid}')

@socketio.on('subscribe_updates')
def handle_subscribe_updates():
    """Subscribe to system updates"""
    from flask_socketio import join_room
    join_room('system_updates')
    emit('subscription_confirmed', {
        'message': 'Subscribed to system updates',
        'room': 'system_updates'
    })

@socketio.on('request_status_update')
def handle_status_request():
    """Handle status update request"""
    try:
        # Get current system status from registry
        total_agents = len(agent_registry.get_all_agents())
        active_agents = len([a for a_name, a_info in agent_registry.get_all_agents().items() if a_info.get('metadata', {}).get('status') == 'active'])
        
        status_data = {
            'agents_count': total_agents,
            'active_agents': active_agents,
            'system_status': 'running', # Assuming web interface implies system is running
            'timestamp': datetime.now().isoformat(),
            'camel_active': camel_agent is not None,
            'llm_gateway_active': llm_gateway is not None
        }
        
        emit('status_update', status_data)
        
    except Exception as e:
        emit('error', {
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })

# Background monitoring
def background_monitoring():
    """Background monitoring and updates"""
    while True:
        try:
            # Update system status based on agent registry
            total_agents = len(agent_registry.get_all_agents())
            active_agents = len([a for a_name, a_info in agent_registry.get_all_agents().items() if a_info.get('metadata', {}).get('status') == 'active'])
            
            global system_status
            system_status.update({
                'status': 'running', # Assuming web interface implies system is running
                'agents_active': active_agents,
                'total_agents': total_agents,
                'last_update': datetime.now().isoformat(),
                'camel_available': camel_agent is not None,
                'llm_gateway_available': llm_gateway is not None
            })
            
            # Emit updates to subscribed clients
            socketio.emit('system_update', system_status, room='system_updates')
            
            time.sleep(10)  # Update every 10 seconds
            
        except Exception as e:
            print(f"🔥 Background monitoring error: {e}")
            time.sleep(30)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Ultimate AGI Force Web Interface v7.0.0")
    print("👑 Owned by: Mulky Malikul Dhaher (1108151509970001)")
    print("🇮🇩 Made with ❤️ in Indonesia")
    print(f"📊 Dashboard will be available at: http://localhost:{os.getenv('WEB_INTERFACE_PORT', 5000)}")
    print(f"🤖 Loaded {len(agent_registry.get_all_agents())} agents from registry")
    print(f"🐪 Camel Agent: {'✅ Available' if camel_agent else '❌ Not Available'}")
    print(f"🧠 LLM Gateway: {'✅ Available' if llm_gateway else '❌ Not Available'}")
    print(f"💾 Memory Bus: {'✅ Available' if memory_bus else '❌ Not Available'}")
    
    # Start background monitoring
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    
    # Run the application
    port = int(os.getenv('WEB_INTERFACE_PORT', 5000))
    host = os.getenv('WEB_INTERFACE_HOST', '0.0.0.0')
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
