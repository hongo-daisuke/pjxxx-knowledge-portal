<script setup lang="ts">
import { ElButton, ElEmpty, ElMessageBox, ElPagination } from 'element-plus'
import { ElMessage } from 'element-plus'
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/shared'
import DocumentTable from '../components/DocumentTable.vue'
import SearchBar from '../components/SearchBar.vue'
import TagFilter from '../components/TagFilter.vue'
import { useDocumentStore } from '../stores/useDocumentStore'
import type { Document } from '../types/document'

const store = useDocumentStore()
const auth = useAuthStore()
const router = useRouter()

const keyword = ref('')
const selectedTags = ref<string[]>([])

onMounted(async () => {
  await Promise.all([store.fetchDocuments(), store.fetchTags()])
})

async function search(): Promise<void> {
  await store.fetchDocuments({
    keyword: keyword.value || undefined,
    tag: selectedTags.value[0],
  })
}

watch(selectedTags, () => search())

function onView(doc: Document): void {
  router.push(`/documents/${doc.docId}`)
}

function onEdit(doc: Document): void {
  router.push(`/documents/${doc.docId}/edit`)
}

async function onDelete(doc: Document): Promise<void> {
  await ElMessageBox.confirm(`「${doc.title}」を削除しますか？`, '削除確認', {
    confirmButtonText: '削除',
    cancelButtonText: 'キャンセル',
    type: 'warning',
  })
  await store.deleteDocument(doc.docId)
  ElMessage.success('削除しました')
}
</script>

<template>
  <div class="document-list">
    <div class="toolbar">
      <SearchBar v-model="keyword" class="search" @search="search" />
      <el-button v-if="auth.isEditor()" type="primary" @click="router.push('/documents/new')">
        ＋ 文書を追加
      </el-button>
    </div>

    <div class="content">
      <aside class="sidebar">
        <TagFilter v-model="selectedTags" :tags="store.tags" />
      </aside>

      <main class="main">
        <el-empty v-if="!store.loading && store.documents.length === 0" description="文書がありません" />
        <DocumentTable
          v-else
          :documents="store.documents"
          :loading="store.loading"
          @view="onView"
          @edit="onEdit"
          @delete="onDelete"
        />

        <div v-if="store.nextToken" class="load-more">
          <el-button @click="store.fetchDocuments({ keyword: keyword || undefined, nextToken: store.nextToken }, true)">
            さらに読み込む
          </el-button>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.document-list {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search {
  flex: 1;
  max-width: 480px;
}
.content {
  display: flex;
  gap: 24px;
}
.sidebar {
  width: 200px;
  flex-shrink: 0;
}
.main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.load-more {
  display: flex;
  justify-content: center;
}
</style>
