<script setup lang="ts">
import { ElAvatar, ElButton, ElDropdown, ElDropdownItem, ElDropdownMenu, ElHeader, ElMenu, ElMenuItem } from 'element-plus'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/shared'

const auth = useAuthStore()
const router = useRouter()

function handleLogout(): void {
  auth.logout()
}
</script>

<template>
  <el-header class="app-header">
    <div class="header-left">
      <span class="logo" @click="router.push('/documents')">ナレッジポータル</span>
      <el-menu mode="horizontal" :ellipsis="false" class="nav-menu">
        <el-menu-item index="documents" @click="router.push('/documents')">文書一覧</el-menu-item>
        <el-menu-item index="chat" @click="router.push('/chat')">AIチャット</el-menu-item>
      </el-menu>
    </div>
    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-avatar size="small">{{ auth.email.charAt(0).toUpperCase() }}</el-avatar>
          <span class="email">{{ auth.email }}</span>
          <el-tag size="small" :type="auth.isAdmin() ? 'danger' : auth.isEditor() ? 'warning' : 'info'">
            {{ auth.role }}
          </el-tag>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleLogout">ログアウト</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color);
  background: #fff;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}
.logo {
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  color: var(--el-color-primary);
}
.nav-menu {
  border-bottom: none;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.email {
  font-size: 14px;
}
</style>
