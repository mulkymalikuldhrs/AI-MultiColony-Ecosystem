# AI-MultiColony-Ecosystem Frontend Guide

This document provides a guide for working with the AI-MultiColony-Ecosystem frontend.

## Overview

The frontend is built with React, TypeScript, Vite, and Tailwind CSS. It provides a modern, responsive user interface for interacting with the AI-MultiColony-Ecosystem.

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
# Navigate to the frontend directory
cd web-interface/react-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The development server will start at http://localhost:12000.

## Project Structure

```
web-interface/react-ui/
├── public/              # Static assets
├── src/
│   ├── api/             # API client functions
│   ├── components/      # Reusable UI components
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Page components
│   ├── App.tsx          # Main application component
│   ├── index.css        # Global styles
│   └── main.tsx         # Entry point
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── tailwind.config.js   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Features

### Agent Management

The frontend provides a comprehensive interface for managing AI agents:

- **Listing Agents**: View all registered agents
- **Agent Details**: View detailed information about an agent
- **Running Agents**: Start and stop agents
- **Agent Logs**: View logs for an agent

### Chat Interface

The chat interface allows users to interact with agents:

- **Agent Selection**: Select an agent to chat with
- **Message History**: View message history
- **Real-time Updates**: Receive real-time updates via WebSocket

### Agent Creator

The agent creator allows users to create new agents dynamically:

- **Agent Configuration**: Configure agent parameters
- **Prompt Template**: Define the agent's prompt template
- **Code Generation**: Generate agent code automatically

### Deployment Management

The deployment management interface allows users to deploy the AI-MultiColony-Ecosystem:

- **Deployment Options**: Configure deployment options
- **Deployment Logs**: View deployment logs
- **Environment Configuration**: Configure the deployment environment

### Settings

The settings interface allows users to configure the system:

- **API Configuration**: Configure API settings
- **UI Settings**: Configure UI settings
- **Theme Selection**: Select a theme for the UI

## API Integration

The frontend communicates with the backend API through the functions defined in the `src/api` directory. The API endpoints are proxied through Vite's development server to avoid CORS issues.

### Example API Call

```typescript
import { getAgents } from '../api/agents'

const fetchAgents = async () => {
  try {
    const data = await getAgents()
    setAgents(data)
  } catch (err) {
    console.error(err)
  }
}
```

## WebSocket Integration

The frontend uses WebSocket for real-time communication with the backend. The WebSocket functionality is implemented using the `useWebSocket` hook.

### Example WebSocket Usage

```typescript
import useWebSocket from '../hooks/useWebSocket'

const { isConnected, lastMessage, sendMessage } = useWebSocket('/ws/system', {
  onMessage: (message) => {
    console.log('Received message:', message)
  },
  onOpen: () => {
    console.log('WebSocket connected')
  },
  onClose: () => {
    console.log('WebSocket disconnected')
  }
})
```

## Styling

The frontend uses Tailwind CSS for styling. The theme configuration is defined in `tailwind.config.js`.

### Example Component with Tailwind CSS

```tsx
const Button = ({ children, onClick, disabled }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded ${
        disabled ? 'bg-gray-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700'
      } text-white`}
    >
      {children}
    </button>
  )
}
```

## Building for Production

To build the frontend for production, run:

```bash
npm run build
```

This will create a production-ready build in the `dist` directory.

## License

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩