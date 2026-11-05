import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api/client.js'
import { useAuth } from '../hooks/useAuth.js'
import { Bot, Mail, Lock, User, UserPlus } from 'lucide-react'

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { saveTokens } = useAuth()
  const navigate = useNavigate()

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/register', form)
      const lr = await api.post('/auth/login', { email: form.email, password: form.password })
      saveTokens(lr.data.access_token, lr.data.refresh_token)
      navigate('/')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail.map((d) => d.msg).join(', ') : (detail || 'Registration failed.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <Bot size={40} strokeWidth={1.5} />
          <h1>Create Account</h1>
          <p>Start asking questions from your documents</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label htmlFor="reg-name">Full Name</label>
            <div className="input-icon-wrapper">
              <User size={16} className="input-icon" />
              <input id="reg-name" type="text" value={form.full_name}
                onChange={update('full_name')} placeholder="John Doe" />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="reg-email">Email</label>
            <div className="input-icon-wrapper">
              <Mail size={16} className="input-icon" />
              <input id="reg-email" type="email" value={form.email}
                onChange={update('email')} placeholder="you@example.com" required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="reg-pw">Password</label>
            <div className="input-icon-wrapper">
              <Lock size={16} className="input-icon" />
              <input id="reg-pw" type="password" value={form.password}
                onChange={update('password')}
                placeholder="Min. 8 chars with a letter and digit" required />
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <span className="spinner" /> : <><UserPlus size={16} /> Create Account</>}
          </button>
        </form>
        <p className="auth-link">Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  )
}
