import React from 'react';

const AgentCard = ({ agent, onRun, onStop, onSelect }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h2 className="text-xl font-bold">{agent.name}</h2>
      <p className="text-gray-600">{agent.description}</p>
      <div className="mt-4">
        <button
          className="px-4 py-2 bg-green-500 text-white rounded-lg mr-2"
          onClick={onRun}
        >
          Run
        </button>
        <button
          className="px-4 py-2 bg-red-500 text-white rounded-lg mr-2"
          onClick={onStop}
        >
          Stop
        </button>
        <button
          className="px-4 py-2 bg-blue-500 text-white rounded-lg"
          onClick={onSelect}
        >
          View Logs
        </button>
      </div>
    </div>
  );
};

export default AgentCard;
