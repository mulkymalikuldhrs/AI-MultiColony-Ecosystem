import React, { useState, useEffect } from 'react';
import { getAgentLogs } from '../api/agents';

const LogViewer = ({ agentName }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (agentName) {
      setLoading(true);
      getAgentLogs(agentName)
        .then((data) => {
          setLogs(data.logs);
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching logs:', error);
          setLoading(false);
        });
    }
  }, [agentName]);

  return (
    <div className="bg-white rounded-lg shadow-md mt-4">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold">Logs for {agentName}</h2>
      </div>
      <div className="p-4 h-96 overflow-y-auto">
        {loading ? (
          <p>Loading logs...</p>
        ) : (
          <pre>
            {logs.map((log, index) => (
              <div key={index}>
                [{log.timestamp}] [{log.level}] {log.message}
              </div>
            ))}
          </pre>
        )}
      </div>
    </div>
  );
};

export default LogViewer;
