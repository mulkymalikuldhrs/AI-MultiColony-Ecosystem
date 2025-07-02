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

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'agentic-ai-system-secret-key-indonesia')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global system status
system_status = {
    'status': 'initializing',
    'agents_active': 0,
    'total_agents': 0,
    'uptime': 0,
    'last_update': datetime.now().isoformat()
}

# Import core components
try:
    from core.prompt_master import prompt_master
    from core.memory_bus import memory_bus
    from core.sync_engine import sync_engine
    from core.scheduler import agent_scheduler
    from connectors.llm_gateway import llm_gateway
    
    # Import agents - Enhanced AGI Force
    from agents.commander_agi import commander_agi
    from agents.quality_control_specialist import quality_control_specialist
    from agents.cybershell import cybershell_agent
    from agents.agent_maker import agent_maker
    from agents.ui_designer import ui_designer_agent
    from agents.dev_engine import dev_engine_agent
    from agents.data_sync import data_sync_agent
    from agents.fullstack_dev import fullstack_dev_agent
    from agents.meta_agent_creator import meta_agent_creator
    from agents.system_optimizer import system_optimizer
    from agents.code_executor import code_executor
    from agents.ai_research_agent import ai_research_agent
    from agents.credential_manager import credential_manager
    from agents.authentication_agent import authentication_agent
    from agents.llm_provider_manager import llm_provider_manager
    
    # Available agents - Enhanced AGI Force Registry
    agents_registry = {
        'commander_agi': commander_agi,
        'quality_control_specialist': quality_control_specialist,
        'prompt_master': prompt_master,
        'cybershell': cybershell_agent,
        'agent_maker': agent_maker,
        'ui_designer': ui_designer_agent,
        'dev_engine': dev_engine_agent,
        'data_sync': data_sync_agent,
        'fullstack_dev': fullstack_dev_agent,
        'meta_agent_creator': meta_agent_creator,
        'system_optimizer': system_optimizer,
        'code_executor': code_executor,
        'ai_research_agent': ai_research_agent,
        'credential_manager': credential_manager,
        'authentication_agent': authentication_agent,
        'llm_provider_manager': llm_provider_manager
    }
    
    print("✅ All core components loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Warning: Some components not available: {e}")
    agents_registry = {}

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('enhanced_index.html')

@app.route('/dashboard')
def dashboard():
    """System dashboard"""
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

@app.route('/agi_command_center')
def agi_command_center():
    """AGI Command Center - Enhanced monitoring and control"""
    return render_template('agi_command_center.html')

# API Routes
@app.route('/api/system/status')
def get_system_status():
    """Get current system status"""
    try:
        # Get status from prompt master if available
        if 'prompt_master' in agents_registry:
            master_status = agents_registry['prompt_master'].get_system_status()
            
            return jsonify({
                'success': True,
                'data': {
                    'system_status': 'running',
                    'agents_active': len([a for a in agents_registry.values() if hasattr(a, 'status') and a.status == 'ready']),
                    'total_agents': len(agents_registry),
                    'uptime': master_status.get('uptime', '0'),
                    'memory_usage': master_status.get('memory_usage', 'Unknown'),
                    'cpu_usage': '< 25%',
                    'last_update': datetime.now().isoformat(),
                    'version': '2.0.0',
                    'llm_providers': len(llm_gateway.providers) if llm_gateway else 0
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'system_status': 'partial',
                    'agents_active': len(agents_registry),
                    'total_agents': len(agents_registry),
                    'message': 'System running in basic mode'
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/list')
def list_agents():
    """List all agents"""
    try:
        agents_list = []
        
        for agent_id, agent in agents_registry.items():
            try:
                agent_info = {
                    'id': agent_id,
                    'name': getattr(agent, 'name', agent_id),
                    'status': getattr(agent, 'status', 'unknown'),
                    'capabilities': getattr(agent, 'capabilities', []),
                    'agent_id': getattr(agent, 'agent_id', agent_id)
                }
                agents_list.append(agent_info)
            except Exception as e:
                agents_list.append({
                    'id': agent_id,
                    'name': agent_id,
                    'status': 'error',
                    'error': str(e)
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
    """Get specific agent status"""
    try:
        if agent_id not in agents_registry:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        agent = agents_registry[agent_id]
        
        # Try to get performance metrics
        if hasattr(agent, 'get_performance_metrics'):
            status = agent.get_performance_metrics()
        else:
            status = {
                'agent_id': agent_id,
                'name': getattr(agent, 'name', agent_id),
                'status': getattr(agent, 'status', 'ready'),
                'capabilities': getattr(agent, 'capabilities', [])
            }
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/task/submit', methods=['POST'])
def submit_task():
    """Submit a task to specific agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if agent_id not in agents_registry:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        agent = agents_registry[agent_id]
        
        # Execute task
        if hasattr(agent, 'process_task'):
            if asyncio.iscoroutinefunction(agent.process_task):
                # Handle async agents
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(agent.process_task(task_data))
                loop.close()
            else:
                result = agent.process_task(task_data)
        else:
            result = {
                'success': False,
                'error': 'Agent does not support task processing'
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

@app.route('/api/prompt/process', methods=['POST'])
def process_prompt():
    """Process a prompt through the system"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        input_type = data.get('input_type', 'text')
        metadata = data.get('metadata', {})
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Use prompt master if available
        if 'prompt_master' in agents_registry:
            prompt_master = agents_registry['prompt_master']
            
            if hasattr(prompt_master, 'process_prompt'):
                if asyncio.iscoroutinefunction(prompt_master.process_prompt):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        prompt_master.process_prompt(prompt, input_type, metadata)
                    )
                    loop.close()
                else:
                    result = prompt_master.process_prompt(prompt, input_type, metadata)
            else:
                result = {
                    'success': False,
                    'error': 'Prompt processing not implemented'
                }
        else:
            # Fallback: try to route to appropriate agent
            result = {
                'success': True,
                'message': 'Prompt received but prompt master not available',
                'prompt': prompt,
                'suggested_agents': list(agents_registry.keys())
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
                    'usage': usage
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

@app.route('/api/memory/stats')
def get_memory_stats():
    """Get memory bus statistics"""
    try:
        if memory_bus:
            stats = memory_bus.get_usage_stats()
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

# AGI Command Center API Routes
@app.route('/api/agi/commander/status')
def get_commander_status():
    """Get Commander AGI status"""
    try:
        if 'commander_agi' in agents_registry:
            commander = agents_registry['commander_agi']
            status = commander.get_status()
            return jsonify({
                'success': True,
                'data': status
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Commander AGI not available'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agi/commander/command', methods=['POST'])
def send_commander_command():
    """Send command to Commander AGI"""
    try:
        if 'commander_agi' not in agents_registry:
            return jsonify({
                'success': False,
                'error': 'Commander AGI not available'
            }), 500
        
        data = request.get_json()
        command = data.get('command', '')
        parameters = data.get('parameters', {})
        
        commander = agents_registry['commander_agi']
        
        # Process command asynchronously
        if asyncio.iscoroutinefunction(commander.process_command):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(commander.process_command(command, parameters))
            loop.close()
        else:
            result = commander.process_command(command, parameters)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agi/quality/status')
def get_quality_control_status():
    """Get Quality Control Specialist status"""
    try:
        if 'quality_control_specialist' in agents_registry:
            qc = agents_registry['quality_control_specialist']
            status = qc.get_status()
            return jsonify({
                'success': True,
                'data': status
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Quality Control Specialist not available'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agi/quality/inspect', methods=['POST'])
def conduct_quality_inspection():
    """Conduct quality inspection"""
    try:
        if 'quality_control_specialist' not in agents_registry:
            return jsonify({
                'success': False,
                'error': 'Quality Control Specialist not available'
            }), 500
        
        data = request.get_json()
        inspection_config = data.get('inspection_config', {'type': 'general'})
        
        qc = agents_registry['quality_control_specialist']
        
        # Conduct inspection asynchronously
        if asyncio.iscoroutinefunction(qc.conduct_quality_inspection):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(qc.conduct_quality_inspection(inspection_config))
            loop.close()
        else:
            result = qc.conduct_quality_inspection(inspection_config)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agi/dashboard/data')
def get_agi_dashboard_data():
    """Get comprehensive AGI dashboard data"""
    try:
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'system_health': 'optimal',
            'threat_level': 'green'
        }
        
        # Get Commander AGI data
        if 'commander_agi' in agents_registry:
            commander = agents_registry['commander_agi']
            dashboard_data['commander'] = commander.get_status()
        
        # Get Quality Control data  
        if 'quality_control_specialist' in agents_registry:
            qc = agents_registry['quality_control_specialist']
            dashboard_data['quality_control'] = qc.get_status()
        
        # Get system metrics
        dashboard_data['system_metrics'] = {
            'total_agents': len(agents_registry),
            'active_agents': len([a for a in agents_registry.values() if hasattr(a, 'status') and getattr(a, 'status') in ['operational', 'ready', 'active']]),
            'cpu_usage': '35%',  # Would be actual system metrics
            'memory_usage': '68%',
            'network_status': 'stable'
        }
        
        # Get agent network status
        agent_network = []
        for agent_id, agent in agents_registry.items():
            agent_network.append({
                'id': agent_id,
                'name': getattr(agent, 'name', agent_id),
                'status': getattr(agent, 'status', 'unknown')
            })
        
        dashboard_data['agent_network'] = agent_network
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connection_status', {
        'status': 'connected',
        'message': '🧠 Connected to Agentic AI System',
        'timestamp': datetime.now().isoformat(),
        'system_version': '2.0.0'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('subscribe_updates')
def handle_subscribe_updates():
    """Subscribe to system updates"""
    from flask_socketio import join_room
    join_room('system_updates')
    emit('subscription_confirmed', {
        'message': 'Subscribed to system updates'
    })

@socketio.on('request_status_update')
def handle_status_request():
    """Handle status update request"""
    try:
        # Get current system status
        status_data = {
            'agents_count': len(agents_registry),
            'active_agents': len([a for a in agents_registry.values() if hasattr(a, 'status') and a.status == 'ready']),
            'system_status': 'running',
            'timestamp': datetime.now().isoformat()
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
            # Update system status
            global system_status
            system_status.update({
                'status': 'running',
                'agents_active': len([a for a in agents_registry.values() if hasattr(a, 'status') and a.status == 'ready']),
                'total_agents': len(agents_registry),
                'last_update': datetime.now().isoformat()
            })
            
            # Emit updates to subscribed clients
            socketio.emit('system_update', system_status, room='system_updates')
            
            time.sleep(10)  # Update every 10 seconds
            
        except Exception as e:
            print(f"Background monitoring error: {e}")
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
    print("🚀 Starting Agentic AI System Web Interface")
    print("🇮🇩 Made with ❤️ by Mulky Malikul Dhaher in Indonesia")
    print(f"📊 Dashboard will be available at: http://localhost:{os.getenv('WEB_INTERFACE_PORT', 5000)}")
    print(f"🤖 Loaded {len(agents_registry)} agents")
    
    # Start background monitoring
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    
    # Run the application
    port = int(os.getenv('WEB_INTERFACE_PORT', 5000))
    host = os.getenv('WEB_INTERFACE_HOST', '0.0.0.0')
    
    socketio.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)
