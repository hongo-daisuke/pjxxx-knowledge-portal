import { fetchAuthSession, signOut } from 'aws-amplify/auth'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import type { Role } from '../types/common'

export const useAuthStore = defineStore('auth', () => {
  const sub = ref<string>('')
  const email = ref<string>('')
  const department = ref<string>('')
  const role = ref<Role>('viewer')
  const isAuthenticated = ref(false)

  async function loadSession(): Promise<void> {
    try {
      const session = await fetchAuthSession()
      const payload = session.tokens?.idToken?.payload
      if (!payload) return

      sub.value = String(payload.sub ?? '')
      email.value = String(payload.email ?? '')
      department.value = String(payload['custom:department'] ?? '')

      const groups = (payload['cognito:groups'] as string[] | undefined) ?? []
      if (groups.includes('admin')) {
        role.value = 'admin'
      } else if (groups.includes('editor')) {
        role.value = 'editor'
      } else {
        role.value = 'viewer'
      }
      isAuthenticated.value = true
    } catch {
      isAuthenticated.value = false
    }
  }

  async function logout(): Promise<void> {
    await signOut()
    isAuthenticated.value = false
  }

  function isEditor(): boolean {
    return role.value === 'editor' || role.value === 'admin'
  }

  function isAdmin(): boolean {
    return role.value === 'admin'
  }

  return { sub, email, department, role, isAuthenticated, loadSession, logout, isEditor, isAdmin }
})
