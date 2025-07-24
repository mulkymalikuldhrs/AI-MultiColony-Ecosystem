import { NavLink } from 'react-router-dom'

const Sidebar = () => {
  return (
    <aside className="w-64 bg-primary-800 text-white p-4">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">AI-MultiColony</h1>
        <p className="text-sm text-primary-200">Ecosystem v7.2.0</p>
      </div>
      
      <nav className="space-y-2">
        <NavLink 
          to="/agents" 
          className={({ isActive }) => 
            `block p-2 rounded ${isActive ? 'bg-primary-700' : 'hover:bg-primary-700'}`
          }
        >
          🤖 Agents
        </NavLink>
        
        <NavLink 
          to="/chat" 
          className={({ isActive }) => 
            `block p-2 rounded ${isActive ? 'bg-primary-700' : 'hover:bg-primary-700'}`
          }
        >
          💬 Chat
        </NavLink>
        
        <NavLink 
          to="/creator" 
          className={({ isActive }) => 
            `block p-2 rounded ${isActive ? 'bg-primary-700' : 'hover:bg-primary-700'}`
          }
        >
          ✨ Creator
        </NavLink>
        
        <NavLink 
          to="/deploy" 
          className={({ isActive }) => 
            `block p-2 rounded ${isActive ? 'bg-primary-700' : 'hover:bg-primary-700'}`
          }
        >
          🚀 Deploy
        </NavLink>
        
        <NavLink 
          to="/settings" 
          className={({ isActive }) => 
            `block p-2 rounded ${isActive ? 'bg-primary-700' : 'hover:bg-primary-700'}`
          }
        >
          ⚙️ Settings
        </NavLink>
      </nav>
      
      <div className="absolute bottom-4 left-4 right-4">
        <div className="p-2 bg-primary-700 rounded text-xs">
          <p>Made with ❤️ by Mulky Malikul Dhaher</p>
          <p>Indonesia 🇮🇩</p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar