import { useState } from 'react'

const Settings = () => {
  const [settings, setSettings] = useState({
    apiKey: '',
    modelName: 'gpt-4',
    temperature: 0.7,
    maxTokens: 1000,
    theme: 'system',
    logLevel: 'info',
    enableWebsocket: true,
    enableAutoSave: true
  })
  
  const [saved, setSaved] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked 
        : type === 'number' 
          ? parseFloat(value) 
          : value
    }))
    
    setSaved(false)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // In a real app, this would save to an API or localStorage
    console.log('Saving settings:', settings)
    
    // Show saved message
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      
      {saved && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          Settings saved successfully!
        </div>
      )}
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">API Configuration</h2>
            
            <div className="mb-4">
              <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="apiKey">
                API Key
              </label>
              <input
                id="apiKey"
                name="apiKey"
                type="password"
                value={settings.apiKey}
                onChange={handleChange}
                placeholder="Enter your API key"
                className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="modelName">
                  Model
                </label>
                <select
                  id="modelName"
                  name="modelName"
                  value={settings.modelName}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3-opus">Claude 3 Opus</option>
                  <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                  <option value="llama-3-70b">Llama 3 70B</option>
                </select>
              </div>
              
              <div>
                <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="temperature">
                  Temperature: {settings.temperature}
                </label>
                <input
                  id="temperature"
                  name="temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={handleChange}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="maxTokens">
                  Max Tokens
                </label>
                <input
                  id="maxTokens"
                  name="maxTokens"
                  type="number"
                  value={settings.maxTokens}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="logLevel">
                  Log Level
                </label>
                <select
                  id="logLevel"
                  name="logLevel"
                  value={settings.logLevel}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="debug">Debug</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">UI Settings</h2>
            
            <div className="mb-4">
              <label className="block text-gray-700 dark:text-gray-300 mb-2" htmlFor="theme">
                Theme
              </label>
              <select
                id="theme"
                name="theme"
                value={settings.theme}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
            </div>
            
            <div className="flex items-center mb-4">
              <input
                id="enableWebsocket"
                name="enableWebsocket"
                type="checkbox"
                checked={settings.enableWebsocket}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-gray-700 dark:text-gray-300" htmlFor="enableWebsocket">
                Enable WebSocket for real-time updates
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                id="enableAutoSave"
                name="enableAutoSave"
                type="checkbox"
                checked={settings.enableAutoSave}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-gray-700 dark:text-gray-300" htmlFor="enableAutoSave">
                Enable auto-save for chat sessions
              </label>
            </div>
          </div>
          
          <button
            type="submit"
            className="px-4 py-2 rounded bg-primary-600 hover:bg-primary-700 text-white"
          >
            Save Settings
          </button>
        </form>
      </div>
    </div>
  )
}

export default Settings