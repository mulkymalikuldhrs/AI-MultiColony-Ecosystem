import { Link } from 'react-router-dom'

interface AgentCardProps {
  agent: {
    id: string
    name: string
    description: string
    status: string
  }
}

const AgentCard = ({ agent }: AgentCardProps) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      case 'idle':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold">{agent.name}</h3>
        <div className={`h-3 w-3 rounded-full ${getStatusColor(agent.status)}`} />
      </div>
      
      <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">
        {agent.description}
      </p>
      
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Status: {agent.status}
        </span>
        
        <Link 
          to={`/agents/${agent.id}`}
          className="text-primary-600 hover:text-primary-800 text-sm font-medium"
        >
          View Details →
        </Link>
      </div>
    </div>
  )
}

export default AgentCard