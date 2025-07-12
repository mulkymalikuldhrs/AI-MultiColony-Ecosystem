import { useState, useEffect } from 'react'
import AgentCard from '../components/AgentCard'
import { getAgents, Agent } from '../api/agents'

const AgentsList = () => {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true)
        const data = await getAgents()
        setAgents(data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch agents. Please try again later.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
  }, [])

  return (
    <div className="container mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">AI Agents</h1>
        <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded">
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      ) : agents.length === 0 ? (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          No agents found. Create your first agent in the Creator tab.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}
    </div>
  )
}

export default AgentsList