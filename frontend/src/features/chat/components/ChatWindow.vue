<script setup lang="ts">
import { ElAvatar } from 'element-plus'
import { nextTick, ref, watch } from 'vue'
import CitationCard from './CitationCard.vue'
import type { ChatMessage } from '../types/chat'

const props = defineProps<{
  messages: ChatMessage[]
  loading: boolean
}>()

const scrollEl = ref<HTMLElement | null>(null)

watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    if (scrollEl.value) {
      scrollEl.value.scrollTop = scrollEl.value.scrollHeight
    }
  },
)
</script>

<template>
  <div ref="scrollEl" class="chat-window">
    <div v-if="props.messages.length === 0" class="empty">
      <p>社内文書に関する質問を入力してください</p>
    </div>

    <div
      v-for="(msg, i) in props.messages"
      :key="i"
      class="message-row"
      :class="msg.role"
    >
      <el-avatar class="avatar" :size="32">{{ msg.role === 'user' ? 'U' : 'AI' }}</el-avatar>
      <div class="bubble-wrap">
        <div class="bubble">{{ msg.content }}</div>
        <CitationCard v-if="msg.citations?.length" :citations="msg.citations" />
      </div>
    </div>

    <div v-if="props.loading" class="message-row assistant">
      <el-avatar class="avatar" :size="32">AI</el-avatar>
      <div class="bubble-wrap">
        <div class="bubble typing">回答を生成中...</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #aaa;
}
.message-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.message-row.user {
  flex-direction: row-reverse;
}
.avatar {
  flex-shrink: 0;
}
.bubble-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 75%;
}
.bubble {
  background: #f0f2f5;
  padding: 10px 14px;
  border-radius: 12px;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 14px;
}
.message-row.user .bubble {
  background: var(--el-color-primary-light-8);
  color: #333;
}
.typing {
  color: #888;
  font-style: italic;
}
</style>
