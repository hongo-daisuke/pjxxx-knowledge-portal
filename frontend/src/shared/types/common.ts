export type Role = 'viewer' | 'editor' | 'admin'
export type Visibility = 'public' | 'department' | 'private'

export interface ApiError {
  error: {
    code: string
    message: string
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  nextToken: string | null
}
