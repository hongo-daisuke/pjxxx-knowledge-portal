<script setup lang="ts">
import {
  ElButton,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElOption,
  ElSelect,
  ElTag,
} from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/shared'
import { useDocumentUpload } from '../composables/useDocumentUpload'
import UploadDropzone from '../components/UploadDropzone.vue'
import { documentService } from '../services/documentService'
import { useDocumentStore } from '../stores/useDocumentStore'
import type { Visibility } from '@/shared'

const route = useRoute()
const router = useRouter()
const store = useDocumentStore()
const auth = useAuthStore()
const { uploading, progress, upload } = useDocumentUpload()

const docId = route.params.docId as string | undefined
const isEdit = !!docId

const form = reactive({
  title: '',
  description: '',
  visibility: 'public' as Visibility,
  department: null as string | null,
  tags: [] as string[],
})

const selectedFile = ref<File | null>(null)
const tagInput = ref('')
const submitting = ref(false)

onMounted(async () => {
  if (isEdit && docId) {
    await store.fetchDocument(docId)
    const doc = store.currentDocument
    if (doc) {
      form.title = doc.title
      form.description = doc.description
      form.visibility = doc.visibility
      form.department = doc.department
      form.tags = [...doc.tags]
    }
  }
})

function addTag(): void {
  const t = tagInput.value.trim()
  if (t && !form.tags.includes(t)) {
    form.tags.push(t)
  }
  tagInput.value = ''
}

function removeTag(tag: string): void {
  form.tags = form.tags.filter((t) => t !== tag)
}

async function onSubmit(): Promise<void> {
  if (!form.title.trim()) {
    ElMessage.warning('タイトルを入力してください')
    return
  }

  submitting.value = true
  try {
    if (isEdit && docId) {
      await documentService.updateDocument(docId, {
        title: form.title,
        description: form.description,
        visibility: form.visibility,
        department: form.department,
        tags: form.tags,
      })
      ElMessage.success('更新しました')
      router.push(`/documents/${docId}`)
    } else {
      if (!selectedFile.value) {
        ElMessage.warning('ファイルを選択してください')
        return
      }
      const doc = await upload(selectedFile.value, {
        title: form.title,
        description: form.description,
        visibility: form.visibility,
        department: form.department,
        tags: form.tags,
      })
      if (doc) {
        ElMessage.success('アップロードしました')
        router.push(`/documents/${doc.docId}`)
      }
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="form-view">
    <h2>{{ isEdit ? '文書を編集' : '文書を追加' }}</h2>

    <el-form label-position="top" class="form">
      <el-form-item label="タイトル" required>
        <el-input v-model="form.title" placeholder="文書のタイトル" />
      </el-form-item>

      <el-form-item label="説明">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="概要・備考" />
      </el-form-item>

      <el-form-item label="公開範囲">
        <el-select v-model="form.visibility" style="width: 200px">
          <el-option value="public" label="全体公開" />
          <el-option value="department" label="部署公開" />
          <el-option value="private" label="非公開（自分のみ）" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="form.visibility === 'department'" label="部署名">
        <el-input v-model="form.department" placeholder="部署名を入力" style="max-width: 300px" />
      </el-form-item>

      <el-form-item label="タグ">
        <div class="tag-section">
          <div class="tags">
            <el-tag
              v-for="tag in form.tags"
              :key="tag"
              closable
              @close="removeTag(tag)"
              class="tag"
            >
              {{ tag }}
            </el-tag>
          </div>
          <div class="tag-input">
            <el-input
              v-model="tagInput"
              placeholder="タグを追加 (Enterで確定)"
              style="max-width: 240px"
              @keyup.enter="addTag"
            />
            <el-button @click="addTag">追加</el-button>
          </div>
        </div>
      </el-form-item>

      <el-form-item v-if="!isEdit" label="ファイル" required>
        <div class="dropzone-wrap">
          <UploadDropzone
            :uploading="uploading"
            :progress="progress"
            @select="selectedFile = $event"
          />
          <p v-if="selectedFile" class="selected-file">選択中: {{ selectedFile.name }}</p>
        </div>
      </el-form-item>

      <div class="actions">
        <el-button @click="router.back()">キャンセル</el-button>
        <el-button type="primary" :loading="submitting || uploading" @click="onSubmit">
          {{ isEdit ? '更新' : 'アップロード' }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<style scoped>
.form-view {
  padding: 24px;
  max-width: 720px;
}
.form-view h2 {
  margin-bottom: 24px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.tag-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag {
  margin: 0;
}
.tag-input {
  display: flex;
  gap: 8px;
  align-items: center;
}
.dropzone-wrap {
  width: 100%;
}
.selected-file {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--el-color-primary);
}
.actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
</style>
