import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useDocumentStore } from './useDocumentStore'
import { documentService } from '../services/documentService'

vi.mock('../services/documentService', () => ({
  documentService: {
    listDocuments: vi.fn(),
    getDocument: vi.fn(),
    deleteDocument: vi.fn(),
    listTags: vi.fn(),
  },
}))

const mockList = vi.mocked(documentService.listDocuments)
const mockDelete = vi.mocked(documentService.deleteDocument)
const mockTags = vi.mocked(documentService.listTags)

const MOCK_DOC = { docId: 'doc-1', title: 'テスト', tags: [] } as never
const MOCK_PAGE1 = { items: [MOCK_DOC], nextToken: 'token-2' }
const MOCK_PAGE2 = { items: [{ docId: 'doc-2', title: '文書2', tags: [] } as never], nextToken: null }

describe('useDocumentStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchDocuments で documents と nextToken がセットされる', async () => {
    mockList.mockResolvedValue(MOCK_PAGE1)
    const store = useDocumentStore()
    await store.fetchDocuments()

    expect(store.documents).toHaveLength(1)
    expect(store.nextToken).toBe('token-2')
    expect(store.loading).toBe(false)
  })

  it('append=true のとき既存リストに追記される', async () => {
    mockList.mockResolvedValueOnce(MOCK_PAGE1).mockResolvedValueOnce(MOCK_PAGE2)
    const store = useDocumentStore()

    await store.fetchDocuments()
    await store.fetchDocuments({ nextToken: 'token-2' }, true)

    expect(store.documents).toHaveLength(2)
    expect(store.nextToken).toBeNull()
  })

  it('deleteDocument は store から対象 docId を除去する', async () => {
    mockList.mockResolvedValue(MOCK_PAGE1)
    mockDelete.mockResolvedValue(undefined)
    const store = useDocumentStore()
    await store.fetchDocuments()

    await store.deleteDocument('doc-1')

    expect(mockDelete).toHaveBeenCalledWith('doc-1')
    expect(store.documents).toHaveLength(0)
  })

  it('fetchDocuments が失敗したとき error にメッセージがセットされる', async () => {
    mockList.mockRejectedValue(new Error('network error'))
    const store = useDocumentStore()
    await store.fetchDocuments()

    expect(store.error).toBe('network error')
    expect(store.documents).toHaveLength(0)
  })

  it('fetchTags でタグ一覧がセットされる', async () => {
    mockTags.mockResolvedValue([{ tagName: '規程', count: 3 }])
    const store = useDocumentStore()
    await store.fetchTags()

    expect(store.tags).toHaveLength(1)
    expect(store.tags[0].tagName).toBe('規程')
  })
})
