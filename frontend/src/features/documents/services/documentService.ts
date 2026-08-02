import axios from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared'
import type {
  CompleteUploadRequest,
  CreateDocumentRequest,
  CreateDocumentResponse,
  Document,
  ListDocumentsQuery,
  Tag,
  UpdateDocumentRequest,
} from '../types/document'

export const documentService = {
  async createDocument(payload: CreateDocumentRequest): Promise<CreateDocumentResponse> {
    const { data } = await axios.post<CreateDocumentResponse>('/documents', payload)
    return data
  },

  async completeUpload(docId: string, payload: CompleteUploadRequest): Promise<Document> {
    const { data } = await axios.post<Document>(`/documents/${docId}/complete`, payload)
    return data
  },

  async listDocuments(query?: ListDocumentsQuery): Promise<PaginatedResponse<Document>> {
    const { data } = await axios.get<PaginatedResponse<Document>>('/documents', { params: query })
    return data
  },

  async getDocument(docId: string): Promise<Document> {
    const { data } = await axios.get<Document>(`/documents/${docId}`)
    return data
  },

  async updateDocument(docId: string, payload: UpdateDocumentRequest): Promise<Document> {
    const { data } = await axios.put<Document>(`/documents/${docId}`, payload)
    return data
  },

  async deleteDocument(docId: string): Promise<void> {
    await axios.delete(`/documents/${docId}`)
  },

  async getDownloadUrl(docId: string): Promise<string> {
    const { data } = await axios.get<{ url: string }>(`/documents/${docId}/download-url`)
    return data.url
  },

  async listTags(): Promise<Tag[]> {
    const { data } = await axios.get<Tag[]>('/tags')
    return data
  },

  async uploadToS3(presignedUrl: string, file: File): Promise<void> {
    await fetch(presignedUrl, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type },
    }).then((res) => {
      if (!res.ok) throw new Error(`S3 upload failed: ${res.status}`)
    })
  },
}
