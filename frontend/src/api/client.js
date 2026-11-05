import axios from 'axios'

const TOKEN_KEY = 'rag_access_token'
const REFRESH_KEY = 'rag_refresh_token'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = false
let queue = []

api.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      if (refreshing) {
        return new Promise((res, rej) => queue.push({ res, rej })).then(
          (token) => { original.headers.Authorization = `Bearer ${token}`; return api(original) }
        )
      }
      original._retry = true
      refreshing = true
      try {
        const rt = sessionStorage.getItem(REFRESH_KEY)
        if (!rt) throw new Error('no refresh token')
        const r = await axios.post('/api/v1/auth/refresh', { refresh_token: rt })
        const newToken = r.data.access_token
        sessionStorage.setItem(TOKEN_KEY, newToken)
        sessionStorage.setItem(REFRESH_KEY, r.data.refresh_token)
        queue.forEach((p) => p.res(newToken))
        queue = []
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      } catch (e) {
        queue.forEach((p) => p.rej(e))
        queue = []
        sessionStorage.removeItem(TOKEN_KEY)
        sessionStorage.removeItem(REFRESH_KEY)
        window.location.href = '/login'
        return Promise.reject(e)
      } finally {
        refreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api
