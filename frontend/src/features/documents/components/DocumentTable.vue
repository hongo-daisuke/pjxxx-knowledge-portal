<script setup lang="ts">
import { ElButton, ElTag, ElTable, ElTableColumn } from 'element-plus'
import type { Document } from '../types/document'

const props = defineProps<{
  documents: Document[]
  loading: boolean
}>()

const emit = defineEmits<{
  view: [doc: Document]
  edit: [doc: Document]
  delete: [doc: Document]
}>()

const VISIBILITY_LABEL: Record<string, string> = {
  public: '全体',
  department: '部署',
  private: '非公開',
}

const VISIBILITY_TYPE: Record<string, 'success' | 'warning' | 'info'> = {
  public: 'success',
  department: 'warning',
  private: 'info',
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ja-JP')
}
</script>

<template>
  <el-table :data="props.documents" v-loading="props.loading" stripe style="width: 100%">
    <el-table-column prop="title" label="タイトル" min-width="200">
      <template #default="{ row }">
        <a class="doc-link" @click="emit('view', row)">{{ row.title }}</a>
      </template>
    </el-table-column>

    <el-table-column label="公開範囲" width="100">
      <template #default="{ row }">
        <el-tag :type="VISIBILITY_TYPE[row.visibility]" size="small">
          {{ VISIBILITY_LABEL[row.visibility] }}
        </el-tag>
      </template>
    </el-table-column>

    <el-table-column label="タグ" min-width="160">
      <template #default="{ row }">
        <el-tag v-for="tag in row.tags" :key="tag" size="small" class="tag-chip">{{ tag }}</el-tag>
      </template>
    </el-table-column>

    <el-table-column prop="ownerEmail" label="投稿者" min-width="160" />

    <el-table-column label="サイズ" width="90">
      <template #default="{ row }">{{ formatSize(row.fileSize) }}</template>
    </el-table-column>

    <el-table-column label="更新日" width="110">
      <template #default="{ row }">{{ formatDate(row.updatedAt) }}</template>
    </el-table-column>

    <el-table-column label="操作" width="160" fixed="right">
      <template #default="{ row }">
        <el-button size="small" @click="emit('view', row)">詳細</el-button>
        <el-button size="small" type="primary" @click="emit('edit', row)">編集</el-button>
        <el-button size="small" type="danger" @click="emit('delete', row)">削除</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<style scoped>
.doc-link {
  color: var(--el-color-primary);
  cursor: pointer;
  text-decoration: underline;
}
.tag-chip {
  margin-right: 4px;
  margin-bottom: 2px;
}
</style>
