"""
🔌 Ultimate AGI Force - WebSocket Event Handlers
Real-time communication for agent control and monitoring

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

from flask_socketio import emit
from datetime import datetime
import json

def register_socketio_handlers(socketio, agents_registry):
    """Register all WebSocket event handlers"""
    
    @socketio.on('agent_action')
    def handle_agent_action(data):
        """Handle agent control actions"""
        try:
            agent_id = data.get('agent_id')
            action = data.get('action')
            
            if agent_id not in agents_registry:
                emit('agent_action_result', {
                    'success': False,
                    'error': f'Agent {agent_id} not found'
                })
                return
            
            agent = agents_registry[agent_id]
            
            # Execute action based on type
            if action == 'start':
                if hasattr(agent, 'status'):
                    agent.status = 'active'
                result = {'success': True, 'message': f'Agent {agent_id} started'}
            elif action == 'pause':
                if hasattr(agent, 'status'):
                    agent.status = 'paused'
                result = {'success': True, 'message': f'Agent {agent_id} paused'}
            elif action == 'stop':
                if hasattr(agent, 'status'):
                    agent.status = 'stopped'
                result = {'success': True, 'message': f'Agent {agent_id} stopped'}
            else:
                result = {'success': False, 'error': f'Unknown action: {action}'}
            
            emit('agent_action_result', result)
            
            # Broadcast status update to all clients
            socketio.emit('agent_status_update', {
                'agent_id': agent_id,
                'status': getattr(agent, 'status', 'unknown'),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            emit('agent_action_result', {
                'success': False,
                'error': str(e)
            })

    @socketio.on('get_initial_data')
    def handle_get_initial_data():
        """Get initial dashboard data"""
        try:
            # Get agents data
            agents_data = {}
            for agent_id, agent in agents_registry.items():
                agents_data[agent_id] = {
                    'name': getattr(agent, 'name', agent_id),
                    'status': getattr(agent, 'status', 'ready'),
                    'capabilities': getattr(agent, 'capabilities', [])
                }
            
            # Get system metrics
            metrics = {
                'active_agents': len([a for a in agents_registry.values() if hasattr(a, 'status') and a.status in ['ready', 'active']]),
                'total_tasks': 0,
                'revenue': 0,
                'threats': 0,
                'backups': 0,
                'campaigns': 0
            }
            
            emit('initial_data', {
                'agents': agents_data,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            emit('error', {
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })

    @socketio.on('get_system_metrics')
    def handle_get_system_metrics():
        """Get real-time system metrics"""
        try:
            metrics = {
                'active_agents': len([a for a in agents_registry.values() if hasattr(a, 'status') and a.status in ['ready', 'active']]),
                'total_tasks': 0,
                'revenue': 0,
                'threats': 0,
                'backups': 0,
                'campaigns': 0
            }
            
            # Try to get real metrics from specific agents
            if 'money_maker' in agents_registry:
                try:
                    money_agent = agents_registry['money_maker']
                    if hasattr(money_agent, 'metrics'):
                        metrics['revenue'] = money_agent.metrics.get('total_earnings', 0)
                except:
                    pass
            
            if 'commander_agi' in agents_registry:
                try:
                    commander = agents_registry['commander_agi']
                    if hasattr(commander, 'metrics'):
                        metrics['threats'] = commander.metrics.get('threats_detected', 0)
                except:
                    pass
            
            if 'backup_colony' in agents_registry:
                try:
                    backup_agent = agents_registry['backup_colony']
                    if hasattr(backup_agent, 'analytics'):
                        metrics['backups'] = backup_agent.analytics.get('total_items', 0)
                except:
                    pass
            
            if 'marketing' in agents_registry:
                try:
                    marketing_agent = agents_registry['marketing']
                    if hasattr(marketing_agent, 'metrics'):
                        metrics['campaigns'] = marketing_agent.metrics.get('campaigns_created', 0)
                except:
                    pass
            
            emit('system_metrics', metrics)
            
        except Exception as e:
            emit('error', {
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })

    @socketio.on('emergency_stop')
    def handle_emergency_stop():
        """Emergency stop all agents"""
        try:
            stopped_agents = []
            
            for agent_id, agent in agents_registry.items():
                try:
                    if hasattr(agent, 'status'):
                        agent.status = 'stopped'
                    stopped_agents.append(agent_id)
                except:
                    pass
            
            emit('emergency_stop_result', {
                'success': True,
                'stopped_agents': stopped_agents,
                'message': f'Emergency stop executed. {len(stopped_agents)} agents stopped.'
            })
            
            # Broadcast to all clients
            socketio.emit('emergency_stop_broadcast', {
                'message': 'Emergency stop executed by admin',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            emit('emergency_stop_result', {
                'success': False,
                'error': str(e)
            })

    @socketio.on('restart_all')
    def handle_restart_all():
        """Restart all agents"""
        try:
            restarted_agents = []
            
            for agent_id, agent in agents_registry.items():
                try:
                    if hasattr(agent, 'status'):
                        agent.status = 'ready'
                    restarted_agents.append(agent_id)
                except:
                    pass
            
            emit('restart_all_result', {
                'success': True,
                'restarted_agents': restarted_agents,
                'message': f'Restart completed. {len(restarted_agents)} agents restarted.'
            })
            
            # Broadcast to all clients
            socketio.emit('restart_all_broadcast', {
                'message': 'System restart executed by admin',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            emit('restart_all_result', {
                'success': False,
                'error': str(e)
            })

    return socketio
