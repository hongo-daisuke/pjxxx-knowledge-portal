<script setup lang="ts">
import { ElButton, ElDescriptions, ElDescriptionsItem, ElMessage, ElTag } from 'element-plus'
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/shared'
import { documentService } from '../services/documentService'
import { useDocumentStore } from '../stores/useDocumentStore'

const route = useRoute()
const router = useRouter()
const store = useDocumentStore()
const auth = useAuthStore()

const docId = route.params.docId as string

onMounted(async () => {
  await store.fetchDocument(docId)
})

const VISIBILITY_LABEL: Record<string, string> = {
  public: '全体公開',
  department: '部署公開',
  private: '非公開（自分のみ）',
}

async function download(): Promise<void> {
  try {
    const url = await documentService.getDownloadUrl(docId)
    window.open(url, '_blank')
  } catch {
    ElMessage.error('ダウンロードURLの取得に失敗しました')
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('ja-JP')
}
</script>

<template>
  <div v-if="store.loading" class="loading">読み込み中...</div>
  <div v-else-if="store.currentDocument" class="detail">
    <div class="header">
      <h2>{{ store.currentDocument.title }}</h2>
      <div class="actions">
        <el-button @click="router.push('/documents')">一覧へ戻る</el-button>
        <el-button @click="download">ダウンロード</el-button>
        <el-button v-if="auth.isEditor()" type="primary" @click="router.push(`/documents/${docId}/edit`)">
          編集
        </el-button>
      </div>
    </div>

    <el-descriptions :column="2" border>
      <el-descriptions-item label="説明" :span="2">
        {{ store.currentDocument.description || '（なし）' }}
      </el-descriptions-item>
      <el-descriptions-item label="公開範囲">
        {{ VISIBILITY_LABEL[store.currentDocument.visibility] }}
      </el-descriptions-item>
      <el-descriptions-item label="部署">
        {{ store.currentDocument.department || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="タグ">
        <el-tag v-for="tag in store.currentDocument.tags" :key="tag" size="small" class="tag">
          {{ tag }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="ファイル名">
        {{ store.currentDocument.fileName }}
      </el-descriptions-item>
      <el-descriptions-item label="ファイルサイズ">
        {{ formatSize(store.currentDocument.fileSize) }}
      </el-descriptions-item>
      <el-descriptions-item label="バージョン">
        v{{ store.currentDocument.version }}
      </el-descriptions-item>
      <el-descriptions-item label="投稿者">
        {{ store.currentDocument.ownerEmail }}
      </el-descriptions-item>
      <el-descriptions-item label="作成日時">
        {{ formatDate(store.currentDocument.createdAt) }}
      </el-descriptions-item>
      <el-descriptions-item label="更新日時">
        {{ formatDate(store.currentDocument.updatedAt) }}
      </el-descriptions-item>
    </el-descriptions>
  </div>
  <div v-else class="error">文書が見つかりませんでした</div>
</template>

<style scoped>
.detail {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}
.header h2 {
  margin: 0;
  font-size: 22px;
}
.actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.tag {
  margin-right: 4px;
}
.loading,
.error {
  padding: 40px;
  text-align: center;
  color: #666;
}
</style>
