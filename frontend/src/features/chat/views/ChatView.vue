<script setup lang="ts">
import { ElButton, ElInput } from 'element-plus'
import { ref } from 'vue'
import ChatWindow from '../components/ChatWindow.vue'
import { useChatStore } from '../stores/useChatStore'

const store = useChatStore()
const inputText = ref('')

async function send(): Promise<void> {
  const msg = inputText.value.trim()
  if (!msg || store.loading) return
  inputText.value = ''
  await store.ask(msg)
}

function onKeydown(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}
</script>

<template>
  <div class="chat-view">
    <div class="chat-header">
      <h2>AIチャット</h2>
      <el-button size="small" @click="store.clearMessages">会話をクリア</el-button>
    </div>

    <ChatWindow :messages="store.messages" :loading="store.loading" />

    <div v-if="store.error" class="error">{{ store.error }}</div>

    <div class="input-bar">
      <el-input
        v-model="inputText"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 4 }"
        placeholder="質問を入力 (Enterで送信、Shift+Enterで改行)"
        resize="none"
        @keydown="onKeydown"
      />
      <el-button type="primary" :loading="store.loading" @click="send">送信</el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px 8px;
  border-bottom: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
}
.chat-header h2 {
  margin: 0;
  font-size: 18px;
}
.error {
  padding: 8px 24px;
  color: var(--el-color-danger);
  font-size: 13px;
  flex-shrink: 0;
}
.input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 24px;
  border-top: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
}
.input-bar .el-textarea {
  flex: 1;
}
</style>
