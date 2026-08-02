import type { RouteRecordRaw } from 'vue-router'

export const documentRoutes: RouteRecordRaw[] = [
  {
    path: '/documents',
    name: 'DocumentList',
    component: () => import('./views/DocumentListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents/new',
    name: 'DocumentNew',
    component: () => import('./views/DocumentFormView.vue'),
    meta: { requiresAuth: true, requiredRole: 'editor' },
  },
  {
    path: '/documents/:docId',
    name: 'DocumentDetail',
    component: () => import('./views/DocumentDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents/:docId/edit',
    name: 'DocumentEdit',
    component: () => import('./views/DocumentFormView.vue'),
    meta: { requiresAuth: true, requiredRole: 'editor' },
  },
]
