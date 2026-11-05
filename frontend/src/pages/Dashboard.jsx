import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client.js'
import { Upload, FileText, Trash2, MessageSquare, AlertCircle, CheckCircle, Clock, XCircle, Plus } from 'lucide-react'

const STATUS_ICON = {
  ready: <CheckCircle size={14} className="status-icon ready" />,
  processing: <Clock size={14} className="status-icon processing" />,
  pending: <Clock size={14} className="status-icon pending" />,
  failed: <XCircle size={14} className="status-icon failed" />,
}
const STATUS_LABEL = { ready: 'Ready', processing: 'Processing...', pending: 'Pending', failed: 'Failed' }

function fmt(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

export default function Dashboard() {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadErr, setUploadErr] = useState('')
  const [uploadOk, setUploadOk] = useState('')
  const fileRef = useRef()
  const navigate = useNavigate()

  const fetchDocs = async () => {
    try {
      const r = await api.get('/documents/')
      setDocs(r.data.documents)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchDocs() }, [])

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadErr(''); setUploadOk('')
    setUploading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      await api.post('/documents/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setUploadOk(`"${file.name}" uploaded and processed successfully!`)
      await fetchDocs()
    } catch (err) {
      setUploadErr(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
      fileRef.current.value = ''
    }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return
    try {
      await api.delete(`/documents/${id}`)
      setDocs(prev => prev.filter(d => d.id !== id))
    } catch (err) { alert(err.response?.data?.detail || 'Delete failed.') }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">My Documents</h1>
          <p className="page-subtitle">Upload PDFs and chat with them using AI</p>
        </div>
        <button className="btn btn-primary" onClick={() => fileRef.current?.click()} disabled={uploading}>
          {uploading ? <span className="spinner" /> : <><Plus size={16} /> Upload PDF</>}
        </button>
        <input ref={fileRef} type="file" accept=".pdf,application/pdf"
          onChange={handleUpload} style={{ display: 'none' }} id="file-input" />
      </div>

      {uploadErr && <div className="alert alert-error"><AlertCircle size={16} /> {uploadErr}</div>}
      {uploadOk  && <div className="alert alert-success"><CheckCircle size={16} /> {uploadOk}</div>}

      {loading ? (
        <div className="loading-center"><span className="spinner spinner-lg" /></div>
      ) : docs.length === 0 ? (
        <div className="empty-state">
          <Upload size={48} strokeWidth={1} />
          <h2>No documents yet</h2>
          <p>Upload a PDF to get started. You can then chat with it using AI.</p>
          <button className="btn btn-primary" onClick={() => fileRef.current?.click()}>
            <Plus size={16} /> Upload your first PDF
          </button>
        </div>
      ) : (
        <div className="doc-grid">
          {docs.map(doc => (
            <div key={doc.id} className="doc-card">
              <div className="doc-card-header">
                <FileText size={24} strokeWidth={1.5} className="doc-icon" />
                <div className="doc-status">{STATUS_ICON[doc.status]}<span>{STATUS_LABEL[doc.status]}</span></div>
              </div>
              <div className="doc-card-body">
                <h3 className="doc-name" title={doc.original_name}>{doc.original_name}</h3>
                <p className="doc-meta">{fmt(doc.file_size)}{doc.chunk_count > 0 && ` · ${doc.chunk_count} chunks`}</p>
                <p className="doc-date">{new Date(doc.created_at).toLocaleDateString()}</p>
              </div>
              <div className="doc-card-actions">
                <button className="btn btn-secondary btn-sm" disabled={doc.status !== 'ready'}
                  onClick={() => navigate('/chat', { state: { documentId: doc.id } })}>
                  <MessageSquare size={14} /> Chat
                </button>
                <button className="btn btn-danger btn-sm"
                  onClick={() => handleDelete(doc.id, doc.original_name)}>
                  <Trash2 size={14} /> Delete
                </button>
              </div>
              {doc.error_message && <p className="doc-error">{doc.error_message}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
