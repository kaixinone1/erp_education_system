<template>
  <div class="template-marker">
    <h2>模板字段标记工具</h2>
    <p class="description">在模板中点击需要填充数据的位置，添加字段标记</p>
    
    <div class="toolbar">
      <el-select v-model="selectedField" placeholder="选择