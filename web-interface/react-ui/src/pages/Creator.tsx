import { useState } from 'react'
import { createAgent } from '../api/creator'

const Creator = () => {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [promptTemplate, setPromptTemplate] = useState('')
  const [config, setConfig] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!name || !promptTemplate) {
      setError('Name and prompt template are required')
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      setSuccess(null)
      
      // Parse config if provided
      let configObj = {}
      if (config.trim()) {
        try {
          configObj = JSON.parse(config)
        } catch (err) {
          setError('Invalid JSON in config')
          setLoading(false)
          return
        }
      }
      
      const response = await createAgent({
        name,
        prompt_template: promptTemplate,
        description,
        config: configObj
      })
      
      setSuccess(`Agent ${response.agent.name} created successfully!`)
      
      // Reset form
      setName('')
      setDescription('')
      setPromptTemplate('')
      setConfig('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create agent')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold mb-6">Agent Creator</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="name">
              Agent Name (CamelCase)
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="MyCustomAgent"
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="description">
              Description
            </label>
            <input
              id="description"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="A custom agent that does something amazing"
              className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="promptTemplate">
              Prompt Template
            </label>
            <textarea
              id="promptTemplate"
              value={promptTemplate}
              onChange={(e) => setPromptTemplate(e.target.value)}
              placeholder="You are a helpful assistant that {task_description}..."
              className="w-full border border-gray-300 rounded px-4 py-2 h-32 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="config">
              Configuration (JSON)
            </label>
            <textarea
              id="config"
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              placeholder='{"temperature": 0.7, "max_tokens": 1000}'
              className="w-full border border-gray-300 rounded px-4 py-2 h-32 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className={`px-4 py-2 rounded ${
              loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700'
            } text-white`}
          >
            {loading ? 'Creating...' : 'Create Agent'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Creator