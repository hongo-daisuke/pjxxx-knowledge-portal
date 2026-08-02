<script setup lang="ts">
import { ElProgress } from 'element-plus'
import { ref } from 'vue'

const props = defineProps<{
  uploading: boolean
  progress: number
}>()

const emit = defineEmits<{
  select: [file: File]
}>()

const dragOver = ref(false)

function onDrop(e: DragEvent): void {
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (file) emit('select', file)
}

function onFileInput(e: Event): void {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emit('select', file)
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ 'is-over': dragOver }"
    @dragover.prevent="dragOver = true"
    @dragleave="dragOver = false"
    @drop.prevent="onDrop"
    @click="($refs.fileInput as HTMLInputElement).click()"
  >
    <input ref="fileInput" type="file" hidden @change="onFileInput" />
    <template v-if="!props.uploading">
      <p class="hint">クリックまたはドラッグ＆ドロップでファイルを選択</p>
      <p class="sub">最大 100 MB</p>
    </template>
    <template v-else>
      <p class="hint">アップロード中...</p>
      <el-progress :percentage="props.progress" style="width: 80%" />
    </template>
  </div>
</template>

<style scoped>
.dropzone {
  border: 2px dashed var(--el-border-color);
  border-radius: 8px;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.dropzone.is-over {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.hint {
  font-size: 15px;
  color: #555;
  margin: 0;
}
.sub {
  font-size: 12px;
  color: #aaa;
  margin: 0;
}
</style>
