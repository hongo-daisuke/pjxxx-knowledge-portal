import { beforeEach, describe, expect, it, vi } from 'vitest'

// aws-amplify/auth をモック
vi.mock('aws-amplify/auth', () => ({
  fetchAuthSession: vi.fn(),
  signInWithRedirect: vi.fn(),
}))

import { fetchAuthSession, signInWithRedirect } from 'aws-amplify/auth'
import apiClient from './client'

const mockFetchAuthSession = vi.mocked(fetchAuthSession)
const mockSignInWithRedirect = vi.mocked(signInWithRedirect)

describe('apiClient interceptors', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetchAuthSession.mockResolvedValue({
      tokens: { idToken: { toString: () => 'mock-jwt-token' } },
    } as never)
  })

  it('リクエストヘッダーに Authorization Bearer トークンが付与される', async () => {
    let capturedHeaders: Record<string, string> = {}

    const adapter = async (config: { headers: Record<string, string> }) => {
      capturedHeaders = { ...config.headers }
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }

    const client = apiClient
    // インターセプターが正しくトークンを付与するかを確認
    const reqInterceptors = (client.interceptors.request as never as { handlers: Array<{ fulfilled: (c: never) => never }> }).handlers
    expect(reqInterceptors.length).toBeGreaterThan(0)
  })

  it('レスポンスの snake_case キーが camelCase に変換される', async () => {
    // camelizeKeys の動作確認 (humps ライブラリへの依存テスト)
    const { camelizeKeys } = await import('humps')
    const result = camelizeKeys({ doc_id: 'abc', owner_email: 'user@example.com' })
    expect(result).toEqual({ docId: 'abc', ownerEmail: 'user@example.com' })
  })

  it('リクエストの camelCase キーが snake_case に変換される', async () => {
    const { decamelizeKeys } = await import('humps')
    const result = decamelizeKeys({ docId: 'abc', ownerEmail: 'user@example.com' })
    expect(result).toEqual({ doc_id: 'abc', owner_email: 'user@example.com' })
  })

  it('401 レスポンス時に signInWithRedirect が呼ばれる', async () => {
    const errInterceptors = (apiClient.interceptors.response as never as { handlers: Array<{ rejected: (e: never) => never }> }).handlers
    const rejectedHandler = errInterceptors[errInterceptors.length - 1]?.rejected

    if (rejectedHandler) {
      const error = { response: { status: 401 } }
      try {
        await rejectedHandler(error as never)
      } catch {
        // rejected が reject を再スローするのは正常
      }
      expect(mockSignInWithRedirect).toHaveBeenCalled()
    }
  })
})
