import { fetchAuthSession } from 'aws-amplify/auth'
import axios from 'axios'
import { camelizeKeys, decamelizeKeys } from 'humps'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// リクエスト: JWT 付与 + camelCase → snake_case 変換
apiClient.interceptors.request.use(async (config) => {
  const session = await fetchAuthSession()
  const token = session.tokens?.idToken?.toString()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.data) {
    config.data = decamelizeKeys(config.data)
  }
  if (config.params) {
    config.params = decamelizeKeys(config.params)
  }
  return config
})

// レスポンス: snake_case → camelCase 変換
apiClient.interceptors.response.use(
  (response) => {
    if (response.data) {
      response.data = camelizeKeys(response.data)
    }
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      // トークン期限切れ: Hosted UI へリダイレクト
      const { signInWithRedirect } = await import('aws-amplify/auth')
      await signInWithRedirect()
    }
    return Promise.reject(error)
  },
)

export default apiClient
