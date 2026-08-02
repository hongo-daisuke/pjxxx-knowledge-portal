<script setup lang="ts">
import { ElCard, ElTag } from 'element-plus'
import { useRouter } from 'vue-router'
import type { Citation } from '../types/chat'

const props = defineProps<{
  citations: Citation[]
}>()

const router = useRouter()
</script>

<template>
  <div v-if="props.citations.length > 0" class="citation-list">
    <p class="label">参照文書</p>
    <el-card
      v-for="(c, i) in props.citations"
      :key="c.docId"
      shadow="never"
      class="citation-card"
    >
      <div class="citation-header">
        <span class="index">[{{ i + 1 }}]</span>
        <a class="title" @click="router.push(`/documents/${c.docId}`)">{{ c.title }}</a>
        <el-tag size="small" type="info">スコア {{ c.score.toFixed(2) }}</el-tag>
      </div>
      <p class="excerpt">{{ c.excerpt }}</p>
    </el-card>
  </div>
</template>

<style scoped>
.citation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.label {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  margin: 0;
}
.citation-card {
  font-size: 13px;
}
.citation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.index {
  color: #888;
  font-weight: 700;
}
.title {
  color: var(--el-color-primary);
  cursor: pointer;
  text-decoration: underline;
  flex: 1;
}
.excerpt {
  margin: 0;
  color: #555;
  line-height: 1.5;
  white-space: pre-wrap;
}
</style>
