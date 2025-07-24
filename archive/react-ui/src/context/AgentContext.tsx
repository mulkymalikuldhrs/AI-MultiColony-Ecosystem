import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { getAgents, Agent } from '../api/agents';

interface AgentContextType {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const AgentProvider = ({ children }: { children: ReactNode }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const data = await getAgents();
      setAgents(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch agents. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const refetch = () => {
    fetchAgents();
  };

  return (
    <AgentContext.Provider value={{ agents, loading, error, refetch }}>
      {children}
    </AgentContext.Provider>
  );
};

export const useAgents = () => {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgents must be used within an AgentProvider');
  }
  return context;
};
