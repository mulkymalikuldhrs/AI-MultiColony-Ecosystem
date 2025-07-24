import React, { useState, useEffect } from 'react';
import AgentCard from '../components/AgentCard';
import LogViewer from '../components/LogViewer';
import { getAgents, runAgent, stopAgent } from '../api/agents';
import { socket } from '../api/chat';

const AgentsList = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAgents = () => {
    setLoading(true);
    getAgents()
      .then((data) => {
        setAgents(data.agents);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching agents:', error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAgents();

    socket.on('registry_updated', () => {
      fetchAgents();
    });

    return () => {
      socket.off('registry_updated');
    };
  }, []);

  const handleRunAgent = (agentName) => {
    const taskDescription = prompt(`Enter task description for ${agentName}:`);
    if (taskDescription) {
      runAgent(agentName, taskDescription)
        .then((data) => {
          console.log(data.message);
          // Refresh agent status
        })
        .catch((error) => {
          console.error('Error running agent:', error);
        });
    }
  };

  const handleStopAgent = (agentName) => {
    stopAgent(agentName)
      .then((data) => {
        console.log(data.message);
        // Refresh agent status
      })
      .catch((error) => {
        console.error('Error stopping agent:', error);
      });
  };

  return (
    <div>
      <h1>Agents</h1>
      {loading ? (
        <p>Loading agents...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onRun={() => handleRunAgent(agent.id)}
              onStop={() => handleStopAgent(agent.id)}
              onSelect={() => setSelectedAgent(agent.id)}
            />
          ))}
        </div>
      )}
      {selectedAgent && <LogViewer agentName={selectedAgent} />}
    </div>
  );
};

export default AgentsList;
