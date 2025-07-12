import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAgentStatus, runAgent, stopAgent, getAgentLogs, Agent } from '../api/agents'

const AgentDetail = () => {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  
  const [agent, setAgent] = useState<Agent | null>(null)
  const [logs, setLogs] = useState<{ timestamp: string; level: string; message: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [taskDescription, setTaskDescription] = useState('')
  const [running, setRunning] = useState(false)

  useEffect(() => {
    if (!name) {
      navigate('/agents')
      return
    }

    const fetchAgentDetails = async () => {
      try {
        setLoading(true)
        const agentData = await getAgentStatus(name)
        setAgent(agentData)
        
        // Fetch logs
        const logsData = await getAgentLogs(name)
        setLogs(logsData.logs)
        
        setError(null)
      } catch (err) {
        setError('Failed to fetch agent details. Please try again later.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchAgentDetails()
  }, [name, navigate])

  const handleRunAgent = async () => {
    if (!name || !taskDescription.trim()) return
    
    try {
      setRunning(true)
      await runAgent(name, taskDescription)
      
      // Refresh agent status
      const agentData = await getAgentStatus(name)
      setAgent(agentData)
      
      // Add a log entry
      setLogs(prev => [
        {
          timestamp: new Date().toISOString(),
          level: 'INFO',
          message: `Started task: ${taskDescription}`
        },
        ...prev
      ])
    } catch (err) {
      setError('Failed to run agent. Please try again later.')
      console.error(err)
    } finally {
      setRunning(false)
    }
  }

  const handleStopAgent = async () => {
    if (!name) return
    
    try {
      await stopAgent(name)
      
      // Refresh agent status
      const agentData = await getAgentStatus(name)
      setAgent(agentData)
      
      // Add a log entry
      setLogs(prev => [
        {
          timestamp: new Date().toISOString(),
          level: 'INFO',
          message: 'Agent stopped'
        },
        ...prev
      ])
    } catch (err) {
      setError('Failed to stop agent. Please try again later.')
      console.error(err)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error || 'Agent not found'}
      </div>
    )
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
        
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-2">Run Agent</h2>
          <div className="flex">
            <input
              type="text"
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              placeholder="Enter task description..."
              className="flex-1 border border-gray-300 rounded-l px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleRunAgent}
              disabled={running || !taskDescription.trim()}
              className={`px-4 py-2 rounded-r ${
                running || !taskDescription.trim() 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-primary-600 hover:bg-primary-700'
              } text-white`}
            >
              {running ? 'Running...' : 'Run'}
            </button>
          </div>
        </div>
        
        {agent.status === 'running' && (
          <div className="mb-6">
            <button
              onClick={handleStopAgent}
              className="px-4 py-2 rounded bg-red-600 hover:bg-red-700 text-white"
            >
              Stop Agent
            </button>
          </div>
        )}
        
        <div>
          <h2 className="text-lg font-semibold mb-2">Logs</h2>
          <div className="bg-gray-100 dark:bg-gray-900 rounded p-4 h-64 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500">No logs available</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="mb-2">
                  <span className="text-gray-500 text-xs">{log.timestamp}</span>
                  <span className={`ml-2 px-1 rounded text-xs ${
                    log.level === 'ERROR' ? 'bg-red-200 text-red-800' :
                    log.level === 'WARNING' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-blue-200 text-blue-800'
                  }`}>
                    {log.level}
                  </span>
                  <span className="ml-2">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentDetail