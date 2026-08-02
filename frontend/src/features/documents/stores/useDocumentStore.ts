import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentService } from '../services/documentService'
import type { Document, ListDocumentsQuery, Tag } from '../types/document'

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<Document[]>([])
  const currentDocument = ref<Document | null>(null)
  const tags = ref<Tag[]>([])
  const nextToken = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDocuments(query?: ListDocumentsQuery, append = false): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const res = await documentService.listDocuments(query)
      documents.value = append ? [...documents.value, ...res.items] : res.items
      nextToken.value = res.nextToken
    } catch (e) {
      error.value = e instanceof Error ? e.message : '取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function fetchDocument(docId: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentDocument.value = await documentService.getDocument(docId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(docId: string): Promise<void> {
    await documentService.deleteDocument(docId)
    documents.value = documents.value.filter((d) => d.docId !== docId)
  }

  async function fetchTags(): Promise<void> {
    tags.value = await documentService.listTags()
  }

  function clearCurrent(): void {
    currentDocument.value = null
  }

  return {
    documents,
    currentDocument,
    tags,
    nextToken,
    loading,
    error,
    fetchDocuments,
    fetchDocument,
    deleteDocument,
    fetchTags,
    clearCurrent,
  }
})
