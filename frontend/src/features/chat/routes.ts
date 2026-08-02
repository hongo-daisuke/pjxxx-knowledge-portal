import type { RouteRecordRaw } from 'vue-router'

export const chatRoutes: RouteRecordRaw[] = [
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('./views/ChatView.vue'),
    meta: { requiresAuth: true },
  },
]
