<script setup lang="ts">
import { ElCheckbox, ElCheckboxGroup } from 'element-plus'
import type { Tag } from '../types/document'

const props = defineProps<{
  tags: Tag[]
  modelValue: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()
</script>

<template>
  <div class="tag-filter">
    <p class="label">タグで絞り込む</p>
    <el-checkbox-group :model-value="props.modelValue" @update:model-value="emit('update:modelValue', $event as string[])">
      <el-checkbox v-for="tag in props.tags" :key="tag.tagName" :value="tag.tagName">
        {{ tag.tagName }} ({{ tag.count }})
      </el-checkbox>
    </el-checkbox-group>
  </div>
</template>

<style scoped>
.tag-filter {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.label {
  font-size: 13px;
  font-weight: 600;
  color: #666;
  margin: 0;
}
</style>
