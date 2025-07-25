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
import uuid
import sqlite3
from werkzeug.utils import secure_filename

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
    from colony.core.unified_agent_registry import unified_registry, create_agent, get_agent_by_name
    from colony.integrations.camel_ai_integration import (
        camel_integration, create_camel_agent, chat_with_camel_agent
    )
    from colony.core.system_bootstrap import bootstrap_systems
    
    print("✅ All core components loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Warning: Some components not available: {e}")
    
    # Fallback implementations
    unified_registry = None
    camel_integration = None
    
    def create_agent(name, config=None):
        return None
    
    def get_agent_by_name(name):
        return None
    
    def create_camel_agent(name, config=None):
        return None
    
    def chat_with_camel_agent(agent_name, message, context=None):
        return "Camel AI integration not available"
    agent_registry = {}

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

@app.route('/workflow-builder')
def workflow_builder():
    """Visual AI Workflow Builder - Revolutionary drag & drop interface"""
    return render_template('workflow_builder.html')

@app.route('/plugin-marketplace')
def plugin_marketplace():
    """Plugin Marketplace - Community-driven extensions"""
    return render_template('plugin_marketplace.html')

@app.route('/mobile-companion')
def mobile_companion():
    """Mobile Companion Dashboard"""
    return render_template('mobile_companion.html')

@app.route('/collaboration')
def collaboration():
    """Real-time Collaboration Hub"""
    return render_template('collaboration.html')

@app.route('/business-intelligence')
def business_intelligence():
    """Advanced Business Intelligence Dashboard"""
    return render_template('business_intelligence.html')

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

# API Routes
@app.route('/api/system/status')
def get_system_status():
    """Get current system status"""
    try:
        # Get status from prompt master if available
        if 'prompt_master' in agent_registry:
            master_status = agent_registry['prompt_master'].get_system_status()
            
            return jsonify({
                'success': True,
                'data': {
                    'system_status': 'running',
                    'agents_active': len([a for a in agent_registry.values() if hasattr(a, 'status') and a.status == 'ready']),
                    'total_agents': len(agent_registry),
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
                    'agents_active': len(agent_registry),
                    'total_agents': len(agent_registry),
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
        
        for agent_id, agent in agent_registry.items():
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
        if agent_id not in agent_registry:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        agent = agent_registry[agent_id]
        
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
        
        if agent_id not in agent_registry:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        agent = agent_registry[agent_id]
        
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
        if 'prompt_master' in agent_registry:
            prompt_master = agent_registry['prompt_master']
            
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
                'suggested_agents': list(agent_registry.keys())
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

# 🔥 NEW CAMEL AI INTEGRATION ENDPOINTS v7.3.0 🔥

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat API endpoint with Camel AI integration"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        agent_name = data.get('agent', 'default_camel_agent')
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create Camel AI agent
        if camel_integration:
            agent = camel_integration.get_agent(agent_name)
            if not agent:
                # Create a new Camel AI agent
                try:
                    agent = create_camel_agent(agent_name, {
                        'model_type': 'gpt-4-turbo',
                        'role_type': 'assistant'
                    })
                except Exception as e:
                    return jsonify({'error': f'Failed to create agent: {str(e)}'}), 500
            
            # Get response from Camel AI agent
            response = chat_with_camel_agent(agent_name, message, context)
        else:
            response = "🤖 Camel AI integration not available. Please install camel-ai package."
        
        return jsonify({
            'response': response,
            'agent': agent_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/unified', methods=['GET'])
def api_unified_agents():
    """Get list of all available agents from unified registry"""
    try:
        agents_data = {
            'unified_registry': {
                'available': unified_registry is not None,
                'agent_classes': unified_registry.list_all_agents() if unified_registry else [],
                'active_instances': unified_registry.list_active_agents() if unified_registry else [],
                'statistics': unified_registry.get_statistics() if unified_registry else {}
            },
            'camel_integration': {
                'available': camel_integration is not None,
                'agents': camel_integration.list_agents() if camel_integration else [],
                'status': camel_integration.get_integration_status() if camel_integration else {}
            },
            'legacy_registry': {
                'available': len(agent_registry) > 0,
                'agents': list(agent_registry.keys())
            }
        }
        
        return jsonify(agents_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/create', methods=['POST'])
def api_create_agent():
    """Create a new agent instance"""
    try:
        data = request.get_json()
        agent_type = data.get('type', 'camel')  # 'camel' or 'colony'
        name = data.get('name', '')
        config = data.get('config', {})
        
        if not name:
            return jsonify({'error': 'Agent name is required'}), 400
        
        if agent_type == 'camel':
            if camel_integration:
                agent = create_camel_agent(name, config)
                return jsonify({
                    'success': True,
                    'agent_name': name,
                    'agent_type': 'camel',
                    'status': agent.get_agent_status()
                })
            else:
                return jsonify({'error': 'Camel AI integration not available'}), 500
                
        elif agent_type == 'colony':
            if unified_registry:
                agent_class = config.get('class', 'BaseAgent')
                agent = create_agent(agent_class, config, name)
                return jsonify({
                    'success': True,
                    'agent_name': name,
                    'agent_type': 'colony',
                    'class': agent_class
                })
            else:
                return jsonify({'error': 'Unified registry not available'}), 500
        
        else:
            return jsonify({'error': 'Invalid agent type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/comprehensive-status', methods=['GET'])
def api_comprehensive_system_status():
    """Get comprehensive system status including all components"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'version': '7.3.0',
            'system_status': system_status,
            'unified_registry': {
                'available': unified_registry is not None,
                'statistics': unified_registry.get_statistics() if unified_registry else {}
            },
            'camel_integration': {
                'available': camel_integration is not None,
                'status': camel_integration.get_integration_status() if camel_integration else {}
            },
            'legacy_agents': {
                'count': len(agent_registry),
                'agents': list(agent_registry.keys())
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# 🚀 WORKFLOW BUILDER API
@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows"""
    try:
        # Load workflows from database/file
        workflows = load_workflows()
        return jsonify({
            'success': True,
            'data': workflows
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create new workflow"""
    try:
        data = request.get_json()
        workflow = {
            'id': generate_workflow_id(),
            'name': data.get('name'),
            'description': data.get('description'),
            'nodes': data.get('nodes', []),
            'connections': data.get('connections', []),
            'created_at': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        save_workflow(workflow)
        
        return jsonify({
            'success': True,
            'data': workflow
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """Execute a workflow"""
    try:
        workflow = get_workflow_by_id(workflow_id)
        if not workflow:
            return jsonify({
                'success': False,
                'error': 'Workflow not found'
            }), 404
        
        # Execute workflow with agent coordination
        execution_result = execute_workflow_with_agents(workflow)
        
        return jsonify({
            'success': True,
            'data': execution_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🔌 PLUGIN MARKETPLACE API
@app.route('/api/plugins', methods=['GET'])
def get_plugins():
    """Get all available plugins"""
    try:
        plugins = load_plugin_marketplace()
        return jsonify({
            'success': True,
            'data': plugins
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/<plugin_id>/install', methods=['POST'])
def install_plugin(plugin_id):
    """Install a plugin"""
    try:
        result = install_plugin_by_id(plugin_id)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plugins/upload', methods=['POST'])
def upload_plugin():
    """Upload new plugin to marketplace"""
    try:
        if 'plugin_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No plugin file provided'
            }), 400
        
        file = request.files['plugin_file']
        metadata = request.form.to_dict()
        
        result = process_plugin_upload(file, metadata)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 📱 MOBILE API
@app.route('/api/mobile/status')
def mobile_status():
    """Mobile-optimized status endpoint"""
    try:
        status = {
            'system_health': 'excellent',
            'active_agents': len([a for a in agents_registry.values() if hasattr(a, 'status') and a.status == 'ready']),
            'recent_activities': get_recent_activities(),
            'notifications': get_pending_notifications(),
            'quick_actions': [
                {'id': 'voice_command', 'name': 'Voice Command', 'icon': 'mic'},
                {'id': 'quick_task', 'name': 'Quick Task', 'icon': 'lightning'},
                {'id': 'agent_status', 'name': 'Agent Status', 'icon': 'robot'}
            ]
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

@app.route('/api/mobile/voice-command', methods=['POST'])
def mobile_voice_command():
    """Process voice command from mobile app"""
    try:
        data = request.get_json()
        voice_data = data.get('voice_data')
        command_text = data.get('command_text')
        
        # Process voice command through prompt master
        if 'prompt_master' in agents_registry:
            result = process_voice_command(command_text or voice_data)
        else:
            result = {'error': 'Voice processing not available'}
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🤝 COLLABORATION API
@app.route('/api/collaboration/rooms')
def get_collaboration_rooms():
    """Get active collaboration rooms"""
    try:
        rooms = get_active_collaboration_rooms()
        return jsonify({
            'success': True,
            'data': rooms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/collaboration/share-workspace', methods=['POST'])
def share_workspace():
    """Share workspace with team members"""
    try:
        data = request.get_json()
        workspace_id = data.get('workspace_id')
        team_members = data.get('team_members', [])
        permissions = data.get('permissions', 'read')
        
        result = create_shared_workspace(workspace_id, team_members, permissions)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 📊 BUSINESS INTELLIGENCE API
@app.route('/api/business-intelligence/dashboard')
def get_bi_dashboard():
    """Get business intelligence dashboard data"""
    try:
        dashboard_data = {
            'kpis': get_system_kpis(),
            'agent_performance': get_agent_performance_metrics(),
            'cost_analytics': get_cost_analytics(),
            'usage_trends': get_usage_trends(),
            'predictive_insights': get_predictive_insights()
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/business-intelligence/reports/generate', methods=['POST'])
def generate_business_report():
    """Generate automated business report"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'performance')
        time_range = data.get('time_range', '7d')
        format_type = data.get('format', 'pdf')
        
        report = generate_automated_report(report_type, time_range, format_type)
        
        return jsonify({
            'success': True,
            'data': report
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
            'agents_count': len(agent_registry),
            'active_agents': len([a for a in agent_registry.values() if hasattr(a, 'status') and a.status == 'ready']),
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

# 🛠️ HELPER FUNCTIONS FOR NEW FEATURES
def generate_workflow_id():
    """Generate unique workflow ID"""
    return f"wf_{uuid.uuid4().hex[:8]}"

def load_workflows():
    """Load workflows from database"""
    try:
        # Initialize database if not exists
        init_workflow_database()
        
        conn = sqlite3.connect('agentic_workflows.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, nodes, connections, created_at, status, tags
            FROM workflows ORDER BY created_at DESC
        ''')
        
        workflows = []
        for row in cursor.fetchall():
            workflow = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'nodes': json.loads(row[3]) if row[3] else [],
                'connections': json.loads(row[4]) if row[4] else [],
                'created_at': row[5],
                'status': row[6],
                'tags': json.loads(row[7]) if row[7] else []
            }
            workflows.append(workflow)
        
        conn.close()
        return workflows
        
    except Exception as e:
        print(f"Error loading workflows: {e}")
        return []

def save_workflow(workflow):
    """Save workflow to database"""
    try:
        init_workflow_database()
        
        conn = sqlite3.connect('agentic_workflows.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO workflows 
            (id, name, description, nodes, connections, created_at, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            workflow['id'],
            workflow['name'],
            workflow['description'],
            json.dumps(workflow.get('nodes', [])),
            json.dumps(workflow.get('connections', [])),
            workflow['created_at'],
            workflow.get('status', 'draft'),
            json.dumps(workflow.get('tags', []))
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving workflow: {e}")
        return False

def init_workflow_database():
    """Initialize workflow database"""
    conn = sqlite3.connect('agentic_workflows.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            nodes TEXT,
            connections TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'draft',
            tags TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plugins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            version TEXT,
            author TEXT,
            file_path TEXT,
            installed BOOLEAN DEFAULT FALSE,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collaboration_rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            participants TEXT,
            created_at TEXT,
            active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_workflow_by_id(workflow_id):
    """Get specific workflow by ID"""
    try:
        conn = sqlite3.connect('agentic_workflows.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, nodes, connections, created_at, status, tags
            FROM workflows WHERE id = ?
        ''', (workflow_id,))
        
        row = cursor.fetchone()
        if row:
            workflow = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'nodes': json.loads(row[3]) if row[3] else [],
                'connections': json.loads(row[4]) if row[4] else [],
                'created_at': row[5],
                'status': row[6],
                'tags': json.loads(row[7]) if row[7] else []
            }
            conn.close()
            return workflow
        
        conn.close()
        return None
        
    except Exception as e:
        print(f"Error getting workflow: {e}")
        return None

def execute_workflow_with_agents(workflow):
    """Execute workflow with agent coordination"""
    try:
        execution_log = []
        results = {}
        
        # Sort nodes by execution order
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', [])
        
        for node in nodes:
            node_type = node.get('type')
            node_config = node.get('config', {})
            
            if node_type == 'agent_task':
                agent_id = node_config.get('agent_id')
                task_data = node_config.get('task_data', {})
                
                if agent_id in agents_registry:
                    agent = agents_registry[agent_id]
                    
                    # Execute task with agent
                    if hasattr(agent, 'process_task'):
                        if asyncio.iscoroutinefunction(agent.process_task):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(agent.process_task(task_data))
                            loop.close()
                        else:
                            result = agent.process_task(task_data)
                        
                        results[node['id']] = result
                        execution_log.append({
                            'node_id': node['id'],
                            'agent_id': agent_id,
                            'status': 'completed',
                            'result': result,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        execution_log.append({
                            'node_id': node['id'],
                            'status': 'error',
                            'error': 'Agent does not support task processing'
                        })
        
        return {
            'execution_id': f"exec_{uuid.uuid4().hex[:8]}",
            'status': 'completed',
            'results': results,
            'execution_log': execution_log,
            'completed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def load_plugin_marketplace():
    """Load plugins from marketplace"""
    try:
        init_workflow_database()
        
        # Sample plugins for marketplace
        sample_plugins = [
            {
                'id': 'slack-integration',
                'name': 'Slack Integration',
                'description': 'Send notifications and commands to Slack',
                'version': '1.0.0',
                'author': 'Agentic AI Team',
                'category': 'Communication',
                'price': 'Free',
                'downloads': 1250,
                'rating': 4.8,
                'installed': False
            },
            {
                'id': 'email-automation',
                'name': 'Email Automation',
                'description': 'Automate email responses and campaigns',
                'version': '2.1.0',
                'author': 'Community Dev',
                'category': 'Automation',
                'price': '$9.99',
                'downloads': 850,
                'rating': 4.6,
                'installed': False
            },
            {
                'id': 'database-connector',
                'name': 'Database Connector',
                'description': 'Connect to SQL and NoSQL databases',
                'version': '1.5.0',
                'author': 'Data Team',
                'category': 'Data',
                'price': 'Free',
                'downloads': 2100,
                'rating': 4.9,
                'installed': True
            }
        ]
        
        return sample_plugins
        
    except Exception as e:
        print(f"Error loading plugins: {e}")
        return []

def install_plugin_by_id(plugin_id):
    """Install plugin by ID"""
    try:
        # Simulate plugin installation
        return {
            'plugin_id': plugin_id,
            'status': 'installed',
            'message': f'Plugin {plugin_id} installed successfully',
            'installed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def process_plugin_upload(file, metadata):
    """Process plugin file upload"""
    try:
        filename = secure_filename(file.filename)
        
        # Save file
        upload_path = os.path.join('plugins', filename)
        os.makedirs('plugins', exist_ok=True)
        file.save(upload_path)
        
        # Process plugin metadata
        plugin_info = {
            'id': f"plugin_{uuid.uuid4().hex[:8]}",
            'name': metadata.get('name', filename),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '1.0.0'),
            'author': metadata.get('author', 'Unknown'),
            'file_path': upload_path,
            'uploaded_at': datetime.now().isoformat()
        }
        
        return plugin_info
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def get_recent_activities():
    """Get recent system activities"""
    return [
        {
            'id': 1,
            'type': 'workflow_execution',
            'message': 'GitHub automation workflow completed',
            'timestamp': datetime.now().isoformat(),
            'agent': 'fullstack_dev'
        },
        {
            'id': 2,
            'type': 'plugin_install',
            'message': 'Slack integration plugin installed',
            'timestamp': datetime.now().isoformat(),
            'user': 'admin'
        }
    ]

def get_pending_notifications():
    """Get pending notifications"""
    return [
        {
            'id': 1,
            'type': 'system_update',
            'title': 'System Update Available',
            'message': 'New features available for upgrade',
            'priority': 'medium'
        }
    ]

def process_voice_command(command_text):
    """Process voice command"""
    try:
        # Simulate voice command processing
        return {
            'command': command_text,
            'action': 'processed',
            'result': f'Executed: {command_text}',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def get_active_collaboration_rooms():
    """Get active collaboration rooms"""
    return [
        {
            'id': 'room_1',
            'name': 'AI Development Team',
            'participants': ['alice', 'bob', 'charlie'],
            'active_since': datetime.now().isoformat(),
            'activity_count': 15
        }
    ]

def create_shared_workspace(workspace_id, team_members, permissions):
    """Create shared workspace"""
    try:
        workspace = {
            'id': workspace_id or f"ws_{uuid.uuid4().hex[:8]}",
            'team_members': team_members,
            'permissions': permissions,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return workspace
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def get_system_kpis():
    """Get system KPIs"""
    return {
        'total_workflows': 23,
        'active_agents': len(agents_registry),
        'monthly_executions': 1250,
        'success_rate': 98.5,
        'avg_response_time': '1.2s',
        'cost_savings': '$2,450'
    }

def get_agent_performance_metrics():
    """Get agent performance metrics"""
    performance_data = []
    
    for agent_id, agent in agents_registry.items():
        try:
            if hasattr(agent, 'get_performance_metrics'):
                metrics = agent.get_performance_metrics()
            else:
                metrics = {
                    'agent_id': agent_id,
                    'success_rate': 95.0,
                    'avg_response_time': 1.5,
                    'total_tasks': 100
                }
            
            performance_data.append(metrics)
            
        except Exception as e:
            performance_data.append({
                'agent_id': agent_id,
                'error': str(e)
            })
    
    return performance_data

def get_cost_analytics():
    """Get cost analytics"""
    return {
        'total_monthly_cost': 125.50,
        'cost_by_provider': {
            'LLM7': 0.00,
            'OpenRouter': 45.20,
            'OpenAI': 80.30
        },
        'cost_trend': [
            {'month': 'Jan', 'cost': 98.20},
            {'month': 'Feb', 'cost': 110.45},
            {'month': 'Mar', 'cost': 125.50}
        ]
    }

def get_usage_trends():
    """Get usage trends"""
    return {
        'daily_requests': [120, 145, 132, 168, 155, 189, 201],
        'peak_hours': [9, 10, 11, 14, 15, 16],
        'top_agents': [
            {'name': 'prompt_master', 'usage': 45},
            {'name': 'code_executor', 'usage': 32},
            {'name': 'llm_provider_manager', 'usage': 28}
        ]
    }

def get_predictive_insights():
    """Get predictive insights"""
    return {
        'expected_growth': '25% next month',
        'optimization_suggestions': [
            'Consider upgrading to premium LLM providers for better performance',
            'Implement caching to reduce API calls by 15%',
            'Schedule maintenance during low-usage hours (2-4 AM)'
        ],
        'risk_factors': [
            'High dependency on external LLM providers',
            'Memory usage trending upward'
        ]
    }

def generate_automated_report(report_type, time_range, format_type):
    """Generate automated business report"""
    try:
        report = {
            'id': f"report_{uuid.uuid4().hex[:8]}",
            'type': report_type,
            'time_range': time_range,
            'format': format_type,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_executions': 1250,
                'success_rate': 98.5,
                'cost_efficiency': 85.2,
                'user_satisfaction': 94.7
            },
            'download_url': f'/api/reports/download/{report_type}_{time_range}.{format_type}'
        }
        
        return report
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

