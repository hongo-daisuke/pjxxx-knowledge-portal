<script setup lang="ts">
import { ElButton, ElCard } from 'element-plus'
import { signInWithRedirect } from 'aws-amplify/auth'

async function login(): Promise<void> {
  await signInWithRedirect()
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h1>ナレッジポータル</h1>
      <p>社内文書の検索・管理・AIチャットを利用できます。</p>
      <el-button type="primary" size="large" @click="login">ログイン</el-button>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f7fa;
}
.login-card {
  width: 400px;
  text-align: center;
  padding: 40px;
}
.login-card h1 {
  margin-bottom: 16px;
  font-size: 24px;
}
.login-card p {
  margin-bottom: 32px;
  color: #666;
}
</style>
