import type { Visibility } from '@/shared'

export interface Document {
  docId: string
  title: string
  description: string
  visibility: Visibility
  department: string | null
  tags: string[]
  ownerId: string
  ownerEmail: string
  status: 'pending' | 'active' | 'deleted'
  fileSize: number
  fileName: string
  s3Key: string
  createdAt: string
  updatedAt: string
  version: number
}

export interface CreateDocumentRequest {
  title: string
  description: string
  visibility: Visibility
  department: string | null
  tags: string[]
  fileName: string
  fileSize: number
  contentType: string
}

export interface CreateDocumentResponse {
  docId: string
  presignedUrl: string
  s3Key: string
}

export interface CompleteUploadRequest {
  s3Key: string
}

export interface UpdateDocumentRequest {
  title?: string
  description?: string
  visibility?: Visibility
  department?: string | null
  tags?: string[]
}

export interface ListDocumentsQuery {
  tag?: string
  department?: string
  keyword?: string
  nextToken?: string
}

export interface Tag {
  tagName: string
  count: number
}
