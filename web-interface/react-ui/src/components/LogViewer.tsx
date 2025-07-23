interface Log {
  timestamp: string;
  level: string;
  message: string;
}

interface LogViewerProps {
  logs: Log[];
}

const LogViewer = ({ logs }: LogViewerProps) => {
  const getLogLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-100';
      case 'WARNING':
        return 'bg-yellow-200 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-100';
      default:
        return 'bg-blue-200 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
    }
  };

  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">Logs</h2>
      <div className="bg-gray-100 dark:bg-gray-900 rounded p-4 h-64 overflow-y-auto">
        {logs.length === 0 ? (
          <p className="text-gray-500">No logs available</p>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="mb-2 font-mono text-sm">
              <span className="text-gray-500 dark:text-gray-400 text-xs">{new Date(log.timestamp).toLocaleTimeString()}</span>
              <span className={`ml-2 px-1 rounded text-xs ${getLogLevelColor(log.level)}`}>
                {log.level}
              </span>
              <span className="ml-2">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default LogViewer;
