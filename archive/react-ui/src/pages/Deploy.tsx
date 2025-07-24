import { useState } from 'react'

const Deploy = () => {
  const [deploymentType, setDeploymentType] = useState<'local' | 'cloud' | 'custom'>('local')
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState<string[]>([])

  const handleDeploy = () => {
    setLoading(true)
    setLogs([])
    
    // Simulate deployment process
    const deploymentSteps = [
      'Initializing deployment...',
      'Checking dependencies...',
      'Building application...',
      'Configuring environment...',
      'Starting services...',
      `Deployment to ${deploymentType} environment completed!`
    ]
    
    let step = 0
    const interval = setInterval(() => {
      if (step < deploymentSteps.length) {
        setLogs(prev => [...prev, deploymentSteps[step]])
        step++
      } else {
        clearInterval(interval)
        setLoading(false)
      }
    }, 1000)
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold mb-6">Deploy AI-MultiColony-Ecosystem</h1>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Deployment Options</h2>
        
        <div className="mb-6">
          <div className="flex space-x-4">
            <div 
              onClick={() => setDeploymentType('local')}
              className={`flex-1 p-4 border rounded-lg cursor-pointer ${
                deploymentType === 'local' 
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                  : 'border-gray-300 hover:border-primary-300'
              }`}
            >
              <h3 className="font-medium mb-2">Local Deployment</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Deploy to your local machine for development and testing.
              </p>
            </div>
            
            <div 
              onClick={() => setDeploymentType('cloud')}
              className={`flex-1 p-4 border rounded-lg cursor-pointer ${
                deploymentType === 'cloud' 
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                  : 'border-gray-300 hover:border-primary-300'
              }`}
            >
              <h3 className="font-medium mb-2">Cloud Deployment</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Deploy to a cloud provider for production use.
              </p>
            </div>
            
            <div 
              onClick={() => setDeploymentType('custom')}
              className={`flex-1 p-4 border rounded-lg cursor-pointer ${
                deploymentType === 'custom' 
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                  : 'border-gray-300 hover:border-primary-300'
              }`}
            >
              <h3 className="font-medium mb-2">Custom Deployment</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Configure a custom deployment environment.
              </p>
            </div>
          </div>
        </div>
        
        {deploymentType === 'local' && (
          <div className="mb-6">
            <h3 className="font-medium mb-2">Local Deployment Settings</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="port">
                  Port
                </label>
                <input
                  id="port"
                  type="number"
                  defaultValue={8080}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="workers">
                  Workers
                </label>
                <input
                  id="workers"
                  type="number"
                  defaultValue={4}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
        )}
        
        {deploymentType === 'cloud' && (
          <div className="mb-6">
            <h3 className="font-medium mb-2">Cloud Provider</h3>
            <select
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="aws">AWS</option>
              <option value="gcp">Google Cloud</option>
              <option value="azure">Azure</option>
              <option value="digitalocean">DigitalOcean</option>
            </select>
          </div>
        )}
        
        {deploymentType === 'custom' && (
          <div className="mb-6">
            <h3 className="font-medium mb-2">Custom Configuration</h3>
            <textarea
              className="w-full border border-gray-300 rounded px-4 py-2 h-32 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Enter custom deployment configuration..."
            />
          </div>
        )}
        
        <button
          onClick={handleDeploy}
          disabled={loading}
          className={`px-4 py-2 rounded ${
            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700'
          } text-white`}
        >
          {loading ? 'Deploying...' : 'Deploy'}
        </button>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold mb-4">Deployment Logs</h2>
        <div className="bg-gray-100 dark:bg-gray-900 rounded p-4 h-64 overflow-y-auto font-mono text-sm">
          {logs.length === 0 ? (
            <p className="text-gray-500">No deployment logs yet</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Deploy