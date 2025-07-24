import { useState } from 'react';

interface AgentControlPanelProps {
  agentStatus: string;
  onRun: (taskDescription: string) => Promise<void>;
  onStop: () => Promise<void>;
}

const AgentControlPanel = ({ agentStatus, onRun, onStop }: AgentControlPanelProps) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  const handleRun = async () => {
    if (!taskDescription.trim()) return;
    setIsRunning(true);
    try {
      await onRun(taskDescription);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="mb-6">
      <h2 className="text-lg font-semibold mb-2">Run Agent</h2>
      <div className="flex mb-4">
        <input
          type="text"
          value={taskDescription}
          onChange={(e) => setTaskDescription(e.target.value)}
          placeholder="Enter task description..."
          className="flex-1 border border-gray-300 rounded-l px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600"
        />
        <button
          onClick={handleRun}
          disabled={isRunning || !taskDescription.trim()}
          className={`px-4 py-2 rounded-r ${
            isRunning || !taskDescription.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700'
          } text-white`}
        >
          {isRunning ? 'Running...' : 'Run'}
        </button>
      </div>

      {agentStatus === 'running' && (
        <button
          onClick={onStop}
          className="px-4 py-2 rounded bg-red-600 hover:bg-red-700 text-white"
        >
          Stop Agent
        </button>
      )}
    </div>
  );
};

export default AgentControlPanel;
