export interface Citation {
  docId: string
  title: string
  excerpt: string
  score: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  createdAt: string
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  sessionId: string
  createdAt: string
}

// ChatHistoryItem は Phase 3 (履歴閲覧 API 追加時) に復元する
