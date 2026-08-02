import { ref } from 'vue'
import { documentService } from '../services/documentService'
import type { CreateDocumentRequest, Document } from '../types/document'

export function useDocumentUpload() {
  const uploading = ref(false)
  const progress = ref(0)
  const error = ref<string | null>(null)

  async function upload(file: File, meta: Omit<CreateDocumentRequest, 'fileName' | 'fileSize' | 'contentType'>): Promise<Document | null> {
    uploading.value = true
    progress.value = 0
    error.value = null

    try {
      const createRes = await documentService.createDocument({
        ...meta,
        fileName: file.name,
        fileSize: file.size,
        contentType: file.type || 'application/octet-stream',
      })
      progress.value = 30

      await documentService.uploadToS3(createRes.presignedUrl, file)
      progress.value = 80

      const doc = await documentService.completeUpload(createRes.docId, {
        s3Key: createRes.s3Key,
      })
      progress.value = 100

      return doc
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'アップロードに失敗しました'
      return null
    } finally {
      uploading.value = false
    }
  }

  return { uploading, progress, error, upload }
}
