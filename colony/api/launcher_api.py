"""
Launcher API - API endpoints for the unified launcher
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

from flask import Blueprint, jsonify, request
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import unified launcher
try:
    from colony.core.unified_launcher import (
        get_system_status,
        start_web_ui,
        stop_web_ui,
        start_agent,
        stop_agent,
        start_all_agents,
        stop_all_agents,
        start_engine,
        stop_engine,
        start_all_engines,
        stop_all_engines,
        start_all,
        stop_all
    )
    launcher_available = True
except ImportError as e:
    print(f"Error importing unified launcher: {e}")
    launcher_available = False

# Setup logger
logger = logging.getLogger("launcher_api")

# Create blueprint
launcher_api = Blueprint('launcher_api', __name__)

@launcher_api.route('/status', methods=['GET'])
def api_get_system_status():
    """Get the status of the entire system."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        status = get_system_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/web-ui/start', methods=['POST'])
def api_start_web_ui():
    """Start the web UI."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        background = data.get('background', True)
        
        result = start_web_ui(background)
        return jsonify({
            'success': result,
            'message': 'Web UI started' if result else 'Failed to start Web UI'
        })
    except Exception as e:
        logger.error(f"Error starting web UI: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/web-ui/stop', methods=['POST'])
def api_stop_web_ui():
    """Stop the web UI."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        result = stop_web_ui()
        return jsonify({
            'success': result,
            'message': 'Web UI stopped' if result else 'Failed to stop Web UI'
        })
    except Exception as e:
        logger.error(f"Error stopping web UI: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/agents/start', methods=['POST'])
def api_start_agent():
    """Start an agent."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        agent_name = data.get('agent_name')
        background = data.get('background', True)
        
        if not agent_name:
            return jsonify({
                'success': False,
                'error': 'agent_name is required'
            }), 400
        
        result = start_agent(agent_name, background)
        return jsonify({
            'success': result,
            'message': f'Agent {agent_name} started' if result else f'Failed to start agent {agent_name}'
        })
    except Exception as e:
        logger.error(f"Error starting agent: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/agents/stop', methods=['POST'])
def api_stop_agent():
    """Stop an agent."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        agent_name = data.get('agent_name')
        
        if not agent_name:
            return jsonify({
                'success': False,
                'error': 'agent_name is required'
            }), 400
        
        result = stop_agent(agent_name)
        return jsonify({
            'success': result,
            'message': f'Agent {agent_name} stopped' if result else f'Failed to stop agent {agent_name}'
        })
    except Exception as e:
        logger.error(f"Error stopping agent: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/agents/start-all', methods=['POST'])
def api_start_all_agents():
    """Start all agents."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        background = data.get('background', True)
        
        results = start_all_agents(background)
        success_count = sum(1 for result in results.values() if result)
        
        return jsonify({
            'success': success_count > 0,
            'message': f'Started {success_count}/{len(results)} agents',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error starting all agents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/agents/stop-all', methods=['POST'])
def api_stop_all_agents():
    """Stop all agents."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        results = stop_all_agents()
        success_count = sum(1 for result in results.values() if result)
        
        return jsonify({
            'success': success_count > 0,
            'message': f'Stopped {success_count}/{len(results)} agents',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error stopping all agents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/engines/start', methods=['POST'])
def api_start_engine():
    """Start an engine."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        engine_name = data.get('engine_name')
        
        if not engine_name:
            return jsonify({
                'success': False,
                'error': 'engine_name is required'
            }), 400
        
        result = start_engine(engine_name)
        return jsonify({
            'success': result,
            'message': f'Engine {engine_name} started' if result else f'Failed to start engine {engine_name}'
        })
    except Exception as e:
        logger.error(f"Error starting engine: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/engines/stop', methods=['POST'])
def api_stop_engine():
    """Stop an engine."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        engine_name = data.get('engine_name')
        
        if not engine_name:
            return jsonify({
                'success': False,
                'error': 'engine_name is required'
            }), 400
        
        result = stop_engine(engine_name)
        return jsonify({
            'success': result,
            'message': f'Engine {engine_name} stopped' if result else f'Failed to stop engine {engine_name}'
        })
    except Exception as e:
        logger.error(f"Error stopping engine: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/engines/start-all', methods=['POST'])
def api_start_all_engines():
    """Start all engines."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        results = start_all_engines()
        success_count = sum(1 for result in results.values() if result)
        
        return jsonify({
            'success': success_count > 0,
            'message': f'Started {success_count}/{len(results)} engines',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error starting all engines: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/engines/stop-all', methods=['POST'])
def api_stop_all_engines():
    """Stop all engines."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        results = stop_all_engines()
        success_count = sum(1 for result in results.values() if result)
        
        return jsonify({
            'success': success_count > 0,
            'message': f'Stopped {success_count}/{len(results)} engines',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error stopping all engines: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/start-all', methods=['POST'])
def api_start_all():
    """Start all components (web UI, agents, engines)."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        background = data.get('background', True)
        
        results = start_all(background)
        
        # Check if at least one component started successfully
        web_ui_success = results.get('web_ui', False)
        agents_success = sum(1 for result in results.get('agents', {}).values() if result)
        engines_success = sum(1 for result in results.get('engines', {}).values() if result)
        
        overall_success = web_ui_success or agents_success > 0 or engines_success > 0
        
        return jsonify({
            'success': overall_success,
            'message': 'Started system components',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error starting all components: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@launcher_api.route('/stop-all', methods=['POST'])
def api_stop_all():
    """Stop all components (web UI, agents, engines)."""
    if not launcher_available:
        return jsonify({
            'success': False,
            'error': 'Unified launcher not available'
        }), 500
    
    try:
        results = stop_all()
        
        # Check if at least one component stopped successfully
        web_ui_success = results.get('web_ui', False)
        agents_success = sum(1 for result in results.get('agents', {}).values() if result)
        engines_success = sum(1 for result in results.get('engines', {}).values() if result)
        
        overall_success = web_ui_success or agents_success > 0 or engines_success > 0
        
        return jsonify({
            'success': overall_success,
            'message': 'Stopped system components',
            'results': results
        })
    except Exception as e:
        logger.error(f"Error stopping all components: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500