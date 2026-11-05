import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import api from '../api/client.js'
import { Bot, LogOut, LayoutDashboard, MessageSquare } from 'lucide-react'

export default function Navbar() {
  const { token, clearTokens } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try { await api.post('/auth/logout') } catch {}
    clearTokens()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <Bot size={24} strokeWidth={1.5} />
        <span>RAG Chatbot</span>
      </Link>
      {token && (
        <div className="nav-links">
          <Link to="/" className="nav-link"><LayoutDashboard size={16} /> Dashboard</Link>
          <Link to="/chat" className="nav-link"><MessageSquare size={16} /> Chat</Link>
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      )}
    </nav>
  )
}
