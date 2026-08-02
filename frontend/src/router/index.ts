import { fetchAuthSession } from 'aws-amplify/auth'
import { createRouter, createWebHistory } from 'vue-router'

import { authRoutes } from '@/features/auth'
import { chatRoutes } from '@/features/chat'
import { documentRoutes } from '@/features/documents'
import { useAuthStore } from '@/shared'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/documents',
    },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      children: [...documentRoutes, ...chatRoutes],
    },
    ...authRoutes,
    {
      path: '/403',
      component: () => import('@/shared/views/ForbiddenView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/shared/views/NotFoundView.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth === false) return true

  try {
    const session = await fetchAuthSession()
    if (!session.tokens) {
      return { name: 'Login' }
    }

    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      await auth.loadSession()
    }

    const required = to.meta.requiredRole as string | undefined
    if (required === 'editor' && !auth.isEditor()) return { path: '/403' }

    return true
  } catch {
    return { name: 'Login' }
  }
})

export default router
