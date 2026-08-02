import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useDocumentUpload } from './useDocumentUpload'
import { documentService } from '../services/documentService'

vi.mock('../services/documentService', () => ({
  documentService: {
    createDocument: vi.fn(),
    uploadToS3: vi.fn(),
    completeUpload: vi.fn(),
  },
}))

const mockCreate = vi.mocked(documentService.createDocument)
const mockS3 = vi.mocked(documentService.uploadToS3)
const mockComplete = vi.mocked(documentService.completeUpload)

const MOCK_FILE = new File(['content'], 'test.pdf', { type: 'application/pdf' })
const MOCK_META = {
  title: 'テスト文書',
  description: '',
  visibility: 'public' as const,
  department: null,
  tags: [],
}

describe('useDocumentUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('正常フロー: presigned取得 → S3 PUT → complete の順に呼ばれる', async () => {
    mockCreate.mockResolvedValue({ docId: 'doc-1', presignedUrl: 'https://s3.example/put', s3Key: 'documents/doc-1.pdf' })
    mockS3.mockResolvedValue(undefined)
    mockComplete.mockResolvedValue({ docId: 'doc-1' } as never)

    const { upload, uploading } = useDocumentUpload()
    const result = await upload(MOCK_FILE, MOCK_META)

    expect(mockCreate).toHaveBeenCalledOnce()
    expect(mockS3).toHaveBeenCalledWith('https://s3.example/put', MOCK_FILE)
    expect(mockComplete).toHaveBeenCalledWith('doc-1', { s3Key: 'documents/doc-1.pdf' })
    expect(result).not.toBeNull()
    expect(uploading.value).toBe(false)
  })

  it('S3 PUT が失敗した場合は error に設定されて null を返す', async () => {
    mockCreate.mockResolvedValue({ docId: 'doc-2', presignedUrl: 'https://s3.example/put', s3Key: 'key' })
    mockS3.mockRejectedValue(new Error('S3 upload failed: 403'))

    const { upload, error, uploading } = useDocumentUpload()
    const result = await upload(MOCK_FILE, MOCK_META)

    expect(result).toBeNull()
    expect(error.value).toContain('S3 upload failed')
    expect(uploading.value).toBe(false)
    expect(mockComplete).not.toHaveBeenCalled()
  })

  it('アップロード中は uploading=true で progress が進む', async () => {
    let resolveS3!: () => void
    mockCreate.mockResolvedValue({ docId: 'doc-3', presignedUrl: 'https://s3.example/put', s3Key: 'key' })
    mockS3.mockReturnValue(new Promise((resolve) => { resolveS3 = resolve }))
    mockComplete.mockResolvedValue({ docId: 'doc-3' } as never)

    const { upload, uploading, progress } = useDocumentUpload()
    const uploadPromise = upload(MOCK_FILE, MOCK_META)

    await vi.waitFor(() => expect(uploading.value).toBe(true))
    expect(progress.value).toBeGreaterThan(0)

    resolveS3()
    await uploadPromise
    expect(uploading.value).toBe(false)
  })
})
