import { useState, useEffect, useRef } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import api from '../api/client.js'
import ReactMarkdown from 'react-markdown'
import { Send, Bot, User, ChevronLeft, MessageSquare, Trash2, Plus } from 'lucide-react'

export default function Chat() {
  const { conversationId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const documentId = location.state?.documentId || null

  const [convos, setConvos] = useState([])
  const [activeId, setActiveId] = useState(conversationId || null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [loadingConvos, setLoadingConvos] = useState(true)
  const bottomRef = useRef()

  useEffect(() => { fetchConvos() }, [])
  useEffect(() => { if (activeId) fetchMsgs(activeId) }, [activeId])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const fetchConvos = async () => {
    try { const r = await api.get('/chat/conversations'); setConvos(r.data) }
    finally { setLoadingConvos(false) }
  }

  const fetchMsgs = async (id) => {
    try { const r = await api.get(`/chat/conversations/${id}`); setMessages(r.data.messages || []) }
    catch { setMessages([]) }
  }

  const send = async () => {
    if (!input.trim() || sending) return
    const q = input.trim(); setInput(''); setSending(true)
    setMessages(prev => [...prev, { id: 'tmp', role: 'user', content: q, created_at: new Date().toISOString() }])
    try {
      const r = await api.post('/chat/', { query: q, conversation_id: activeId, document_id: documentId })
      if (!activeId) {
        setActiveId(r.data.conversation_id)
        navigate(`/chat/${r.data.conversation_id}`, { replace: true, state: { documentId } })
        await fetchConvos()
      }
      await fetchMsgs(r.data.conversation_id)
    } catch (err) {
      setMessages(prev => [...prev, {
        id: 'err', role: 'assistant',
        content: `Error: ${err.response?.data?.detail || 'Something went wrong.'}`,
        created_at: new Date().toISOString()
      }])
    } finally { setSending(false) }
  }

  const delConvo = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this conversation?')) return
    await api.delete(`/chat/conversations/${id}`)
    setConvos(prev => prev.filter(c => c.id !== id))
    if (activeId === id) { setActiveId(null); setMessages([]); navigate('/chat', { replace: true }) }
  }

  return (
    <div className="chat-layout">
      <aside className="chat-sidebar">
        <div className="sidebar-header">
          <h2>Conversations</h2>
          <button className="btn btn-secondary btn-sm icon-btn"
            onClick={() => { setActiveId(null); setMessages([]); navigate('/chat', { replace: true }) }}>
            <Plus size={16} />
          </button>
        </div>
        {loadingConvos ? (
          <div className="sidebar-loading"><span className="spinner" /></div>
        ) : convos.length === 0 ? (
          <p className="sidebar-empty">No conversations yet</p>
        ) : (
          <ul className="convo-list">
            {convos.map(c => (
              <li key={c.id} className={`convo-item ${activeId === c.id ? 'active' : ''}`}
                onClick={() => setActiveId(c.id)}>
                <MessageSquare size={14} />
                <span className="convo-title">{c.title || 'Untitled'}</span>
                <button className="convo-delete" onClick={(e) => delConvo(c.id, e)}><Trash2 size={12} /></button>
              </li>
            ))}
          </ul>
        )}
        <button className="btn btn-ghost btn-sm back-btn" onClick={() => navigate('/')}>
          <ChevronLeft size={14} /> My Documents
        </button>
      </aside>

      <div className="chat-main">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="chat-welcome">
              <Bot size={48} strokeWidth={1} />
              <h2>Ask anything about your documents</h2>
              <p>Type a question below. The AI answers based on your uploaded PDFs only.</p>
            </div>
          )}
          {messages.map(msg => (
            <div key={msg.id} className={`message message-${msg.role}`}>
              <div className="message-avatar">{msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}</div>
              <div className="message-bubble"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
            </div>
          ))}
          {sending && (
            <div className="message message-assistant">
              <div className="message-avatar"><Bot size={16} /></div>
              <div className="message-bubble typing"><span /><span /><span /></div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <textarea className="chat-textarea" value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
              placeholder="Ask a question... (Enter to send, Shift+Enter for newline)"
              rows={1} disabled={sending} />
            <button className="send-btn" onClick={send}
              disabled={!input.trim() || sending} aria-label="Send">
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
