import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatService } from '../services/chatService'
import type { ChatMessage, Citation } from '../types/chat'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function ask(userMessage: string): Promise<void> {
    messages.value.push({
      role: 'user',
      content: userMessage,
      createdAt: new Date().toISOString(),
    })

    loading.value = true
    error.value = null

    try {
      const res = await chatService.ask({ message: userMessage })
      messages.value.push({
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        createdAt: res.createdAt,
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : '回答の取得に失敗しました'
    } finally {
      loading.value = false
    }
  }

  function clearMessages(): void {
    messages.value = []
  }

  return { messages, loading, error, ask, clearMessages }
})
