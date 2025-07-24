import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAgentStatus, runAgent, stopAgent, getAgentLogs, Agent } from '../api/agents'
import AgentControlPanel from '../components/AgentControlPanel'
import LogViewer from '../components/LogViewer'

const AgentDetail = () => {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  
  const [agent, setAgent] = useState<Agent | null>(null)
  const [logs, setLogs] = useState<{ timestamp: string; level: string; message: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAgentDetails = useCallback(async () => {
    if (!name) return;
    try {
      setLoading(true)
      const agentData = await getAgentStatus(name)
      setAgent(agentData)
      const logsData = await getAgentLogs(name)
      setLogs(logsData.logs.reverse()) // Assuming logs are chronological
      setError(null)
    } catch (err) {
      setError('Failed to fetch agent details.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [name]);

  useEffect(() => {
    if (!name) {
      navigate('/agents');
    } else {
      fetchAgentDetails();
    }
  }, [name, navigate, fetchAgentDetails])

  const addLog = (level: string, message: string) => {
    setLogs(prev => [{ timestamp: new Date().toISOString(), level, message }, ...prev]);
  };

  const handleRunAgent = async (taskDescription: string) => {
    if (!name) return;
    try {
      addLog('INFO', `Attempting to run task: ${taskDescription}`);
      await runAgent(name, taskDescription);
      addLog('SUCCESS', 'Task started successfully.');
      await fetchAgentDetails(); // Refresh details
    } catch (err) {
      addLog('ERROR', 'Failed to run agent.');
      console.error(err);
    }
  };

  const handleStopAgent = async () => {
    if (!name) return;
    try {
      addLog('INFO', 'Attempting to stop agent...');
      await stopAgent(name);
      addLog('SUCCESS', 'Agent stopped successfully.');
      await fetchAgentDetails(); // Refresh details
    } catch (err) {
      addLog('ERROR', 'Failed to stop agent.');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error || 'Agent not found'}
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <div className="mb-6">
        <button 
          onClick={() => navigate('/agents')}
          className="text-primary-600 hover:text-primary-800"
        >
          ← Back to Agents
        </button>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold">{agent.name}</h1>
            <p className="text-gray-600 dark:text-gray-300">{agent.description}</p>
          </div>
          
          <div className="flex items-center">
            <span className="mr-2">Status:</span>
            <span className={`px-2 py-1 rounded text-white text-sm ${
              agent.status === 'running' ? 'bg-green-500' : 
              agent.status === 'error' ? 'bg-red-500' : 
              'bg-yellow-500'
            }`}>
              {agent.status}
            </span>
          </div>
        </div>
        
        <AgentControlPanel
          agentStatus={agent.status}
          onRun={handleRunAgent}
          onStop={handleStopAgent}
        />
        
        <LogViewer logs={logs} />
      </div>
    </div>
  );
};

export default AgentDetail