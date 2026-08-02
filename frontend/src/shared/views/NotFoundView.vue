<script setup lang="ts">
import { ElButton, ElResult } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="error-page">
    <el-result icon="info" title="404" sub-title="ページが見つかりませんでした">
      <template #extra>
        <el-button type="primary" @click="router.push('/documents')">文書一覧に戻る</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
</style>
