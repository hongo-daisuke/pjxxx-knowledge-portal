<script setup lang="ts">
import { ElInput } from 'element-plus'
import { ref } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  search: [value: string]
}>()

const inputRef = ref(props.modelValue)

function onInput(val: string): void {
  inputRef.value = val
  emit('update:modelValue', val)
}

function onSearch(): void {
  emit('search', inputRef.value)
}
</script>

<template>
  <el-input
    :model-value="props.modelValue"
    placeholder="キーワードで検索"
    clearable
    @update:model-value="onInput"
    @keyup.enter="onSearch"
  >
    <template #append>
      <span style="cursor: pointer" @click="onSearch">検索</span>
    </template>
  </el-input>
</template>
