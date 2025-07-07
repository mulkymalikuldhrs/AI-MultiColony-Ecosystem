'use client';

import { useState, useEffect } from 'react';

// Mock data for agents, replace with API call
const mockAgents = [
  { id: 'roo', name: 'Roo', status: 'idle', description: 'Core task processing agent.' },
  { id: 'kilo', name: 'Kilo', status: 'active', description: 'Secondary processing unit.' },
  { id: 'kilo2', name: 'Kilo2', status: 'error', description: 'Tertiary processing unit.' },
  { id: 'cline', name: 'Cline', status: 'idle', description: 'UI/UX and frontend agent.' },
];

const AgentCard = ({ agent }) => (
  <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex justify-between items-center">
    <div>
      <h3 className="text-xl font-bold text-white">{agent.name}</h3>
      <p className="text-gray-400">{agent.description}</p>
    </div>
    <div className="flex items-center space-x-4">
      <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
        agent.status === 'active' ? 'bg-green-500 text-white' :
        agent.status === 'idle' ? 'bg-yellow-500 text-black' :
        'bg-red-500 text-white'
      }`}>
        {agent.status}
      </span>
      <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
        Details
      </button>
    </div>
  </div>
);

const Dashboard = () => {
  const [agents, setAgents] = useState([]);
  const [logs, setLogs] = useState('');

  useEffect(() => {
    // In a real app, you'd fetch this data from an API
    setAgents(mockAgents);
    // Mock logs
    setLogs('Initializing system...\nAgent Kilo started successfully.\nWatching for tasks...');
  }, []);

  return (
    <div className="w-full max-w-7xl mx-auto p-8 space-y-8">
      <header className="text-center">
        <h1 className="text-5xl font-extrabold text-white tracking-tight">AI Colony Control Center</h1>
        <p className="mt-2 text-lg text-gray-400">Monitor and manage your autonomous AI agents in real-time.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-3xl font-bold text-white border-b-2 border-gray-700 pb-2">Agent Status</h2>
          <div className="space-y-4">
            {agents.map(agent => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h2 className="text-3xl font-bold text-white mb-4 border-b-2 border-gray-700 pb-2">System Logs</h2>
          <div className="bg-black text-green-400 font-mono text-sm rounded p-4 h-96 overflow-y-auto">
            <pre>{logs}</pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
