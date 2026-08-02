<script setup lang="ts">
import { ElContainer, ElMain } from 'element-plus'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <el-container class="app-container">
    <AppHeader />
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.app-main {
  flex: 1;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
