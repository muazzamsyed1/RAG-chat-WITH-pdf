import { useState, useCallback } from 'react'

const TOKEN_KEY = 'rag_access_token'
const REFRESH_KEY = 'rag_refresh_token'

export function useAuth() {
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY))

  const saveTokens = useCallback((access, refresh) => {
    sessionStorage.setItem(TOKEN_KEY, access)
    sessionStorage.setItem(REFRESH_KEY, refresh)
    setToken(access)
  }, [])

  const clearTokens = useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
    setToken(null)
  }, [])

  const getRefreshToken = useCallback(
    () => sessionStorage.getItem(REFRESH_KEY),
    []
  )

  return { token, saveTokens, clearTokens, getRefreshToken }
}
