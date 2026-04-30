<template>
  <el-main class="app-main-container">
    <router-view v-slot="{ Component }">
      <transition name="fade-transform" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </transition>
    </router-view>
  </el-main>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.app-main-container {
  height: calc(100vh - 160px);
  background-color: #f5f7fa;
  overflow-y: auto;
  padding: 20px;
  margin: 0;
}

.app-main-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.app-main-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.app-main-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.app-main-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 路由切换动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>