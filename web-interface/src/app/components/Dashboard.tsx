"use client";

import { useState, useEffect } from "react";
import io from "socket.io-client";

interface Agent {
  id: string;
  name: string;
  status: "initialized" | "ready" | "processing" | "error" | "unknown"; // Updated statuses based on backend
  capabilities: string[]; // Use capabilities directly
}

// Define the Socket.IO server URL
// Assuming Flask backend runs on port 8080 as configured in unified_launcher.py
const SOCKET_SERVER_URL = "http://localhost:8080";

const AgentCard = ({ agent }: { agent: Agent }) => (
  <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex justify-between items-center">
    <div>
      <h3 className="text-xl font-bold text-white">{agent.name}</h3>
      <p className="text-gray-400 text-sm">ID: {agent.id}</p>
      <p className="text-gray-400 text-sm">
        Capabilities: {agent.capabilities.join(", ") || "None"}
      </p>
    </div>
    <div className="flex items-center space-x-4">
      <span
        className={`px-3 py-1 text-sm font-semibold rounded-full ${
          agent.status === "ready"
            ? "bg-green-500 text-white"
            : agent.status === "processing"
              ? "bg-blue-500 text-white"
              : agent.status === "error"
                ? "bg-red-500 text-white"
                : "bg-yellow-500 text-black" // For 'initialized' or 'unknown'
        }`}
      >
        {agent.status}
      </span>
      {/* Add a button for more details or actions */}
      <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg text-sm transition duration-300">
        Details
      </button>
    </div>
  </div>
);

const Dashboard = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [logs, setLogs] = useState("Connecting to system...\n");
  const [systemStatus, setSystemStatus] = useState<{
    status?: string;
    agents_active?: number;
    total_agents?: number;
    version?: string;
    working_agents?: Record<string, Agent>;
  } | null>(null); // State for overall system status

  useEffect(() => {
    // Establish Socket.IO connection
    const socket = io(SOCKET_SERVER_URL);

    socket.on("connect", () => {
      console.log("Socket.IO connected");
      setLogs((prevLogs) => prevLogs + "Socket.IO connected.\n");
      // Subscribe to system updates
      socket.emit("subscribe_updates");
      // Request initial status update
      socket.emit("request_status_update");
    });

    socket.on("disconnect", () => {
      console.log("Socket.IO disconnected");
      setLogs((prevLogs) => prevLogs + "Socket.IO disconnected.\n");
    });

    socket.on("system_update", (data: unknown) => {
      // Type assertion for expected structure
      const sysData = data as {
        status: string;
        agents_active: number;
        total_agents: number;
        version: string;
        working_agents: Record<string, Agent>;
      };
      setSystemStatus(sysData);
      if (sysData && sysData.working_agents) {
        const updatedAgents: Agent[] = Object.values(sysData.working_agents);
        setAgents(updatedAgents);
      }
      setLogs(
        (prevLogs) =>
          prevLogs +
          `System status updated: ${sysData.status} (${sysData.agents_active}/${sysData.total_agents} agents active)\n`,
      );
    });

    socket.on("status_update", (data: unknown) => {
      const statData = data as {
        system_status: string;
        active_agents: number;
        agents_count: number;
      };
      setLogs(
        (prevLogs) =>
          prevLogs +
          `Initial status received: ${statData.system_status} (${statData.active_agents}/${statData.agents_count} agents active)\n`,
      );
    });

    socket.on("error", (data) => {
      console.error("Socket.IO error:", data);
      setLogs((prevLogs) => prevLogs + `Socket.IO Error: ${data.message}\n`);
    });

    // Cleanup function
    return () => {
      console.log("Disconnecting Socket.IO");
      socket.disconnect();
    };
  }, []); // Empty dependency array means this effect runs once on mount

  return (
    <div className="w-full max-w-7xl mx-auto p-8 space-y-8">
      <header className="text-center">
        <h1 className="text-5xl font-extrabold text-white tracking-tight">
          AI Colony Control Center
        </h1>
        <p className="mt-2 text-lg text-gray-400">
          Monitor and manage your autonomous AI agents in real-time.
        </p>
        {systemStatus && (
          <div className="mt-4 text-gray-300">
            System Status:{" "}
            <span
              className={`font-semibold ${systemStatus.status === "running" ? "text-green-400" : "text-yellow-400"}`}
            >
              {systemStatus.status}
            </span>{" "}
            | Agents:{" "}
            <span className="font-semibold">
              {systemStatus.agents_active}/{systemStatus.total_agents} active
            </span>{" "}
            | Version:{" "}
            <span className="font-semibold">{systemStatus.version}</span>
          </div>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-3xl font-bold text-white border-b-2 border-gray-700 pb-2">
            Agent Status
          </h2>
          <div className="space-y-4">
            {agents.length > 0 ? (
              agents.map((agent) => <AgentCard key={agent.id} agent={agent} />)
            ) : (
              <p className="text-gray-400">
                No agents found or system is not running.
              </p>
            )}
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h2 className="text-3xl font-bold text-white mb-4 border-b-2 border-gray-700 pb-2">
            System Logs
          </h2>
          <div className="bg-black text-green-400 font-mono text-sm rounded p-4 h-96 overflow-y-auto">
            <pre>{logs}</pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
