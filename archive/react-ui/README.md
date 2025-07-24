# AI-MultiColony-Ecosystem Web UI

This is the web interface for the AI-MultiColony-Ecosystem project, built with React, TypeScript, Vite, and Tailwind CSS.

## Features

- Agent management and monitoring
- Chat interface for interacting with agents
- Dynamic agent creation
- Deployment management
- System settings

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

- `src/components`: Reusable UI components
- `src/pages`: Page components
- `src/api`: API client functions
- `src/hooks`: Custom React hooks
- `public`: Static assets

## API Integration

The web UI communicates with the backend API through the functions defined in the `src/api` directory. The API endpoints are proxied through Vite's development server to avoid CORS issues.

## Styling

The project uses Tailwind CSS for styling. The theme configuration is defined in `tailwind.config.js`.

## License

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩