import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import AgentsList from './pages/AgentsList'
import AgentDetail from './pages/AgentDetail'
import Chat from './pages/Chat'
import Creator from './pages/Creator'
import Deploy from './pages/Deploy'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<AgentsList />} />
        <Route path="agents" element={<AgentsList />} />
        <Route path="agents/:name" element={<AgentDetail />} />
        <Route path="chat" element={<Chat />} />
        <Route path="creator" element={<Creator />} />
        <Route path="deploy" element={<Deploy />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default App