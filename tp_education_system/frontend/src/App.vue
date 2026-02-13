<template>
  <div class="app-container">
    <!-- 顶部Header -->
    <Header />
    
    <div class="main-layout">
      <!-- 左侧Sidebar -->
      <Sidebar />
      
      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 多标签导航栏 -->
        <TagsView />
        
        <!-- 主工作区域 -->
        <AppMain />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import Header from './components/Layout/Header.vue'
import Sidebar from './components/Layout/Sidebar.vue'
import TagsView from './components/Layout/TagsView.vue'
import AppMain from './components/Layout/AppMain.vue'

onMounted(() => {
  console.log('应用已挂载')
})
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.main-layout {
  display: flex;
  height: calc(100vh - 60px);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  font-size: 14px;
  color: #303133;
  background-color: #f5f7fa;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
