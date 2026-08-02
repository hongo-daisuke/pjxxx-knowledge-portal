import axios from '@/shared/api/client'
import type { ChatRequest, ChatResponse } from '../types/chat'

export const chatService = {
  async ask(payload: ChatRequest): Promise<ChatResponse> {
    const { data } = await axios.post<ChatResponse>('/chat', payload)
    return data
  },
}
