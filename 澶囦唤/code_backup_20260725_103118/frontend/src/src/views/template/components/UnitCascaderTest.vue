<template>
  <div class="test-page">
    <h2>单位选择器测试</h2>
    <UnitCascader
      v-model="selectedUnit"
      @change="handleChange"
      placeholder="请选择单位（省/市/县/镇/校）"
    />
    <div v-if="selectedUnit" style="margin-top: 20px;">
      <p>选中的单位ID: {{ selectedUnit }}</p>
      <p>选中的单位信息: {{ unitInfo }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UnitCascader from './UnitCascader.vue'

const selectedUnit = ref(null)
const unitInfo = ref(null)

function handleChange(data) {
  unitInfo.value = data.unit
  console.log('选择的单位：', data)
}
</script>

<style scoped>
.test-page {
  padding: 20px;
}
</style>

