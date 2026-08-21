<template>
  <div class="radio-test">
    <h3>单选按钮测试</h3>
    
    <div class="test-section">
      <h4>测试1：基础单选按钮</h4>
      <el-radio-group v-model="test1">
        <el-radio label="option1">选项1</el-radio>
        <el-radio label="option2">选项2</el-radio>
      </el-radio-group>
      <p>当前值: {{ test1 }}</p>
    </div>
    
    <div class="test-section">
      <h4>测试2：带边框的单选按钮</h4>
      <el-radio-group v-model="test2">
        <el-radio label="unit" border>单位统计</el-radio>
        <el-radio label="personal" border>个人统计</el-radio>
      </el-radio-group>
      <p>当前值: {{ test2 }}</p>
    </div>
    
    <div class="test-section">
      <h4>测试3：按钮样式</h4>
      <el-radio-group v-model="test3">
        <el-radio-button label="unit">单位统计</el-radio-button>
        <el-radio-button label="personal">个人统计</el-radio-button>
      </el-radio-group>
      <p>当前值: {{ test3 }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const test1 = ref('option1')
const test2 = ref('unit')
const test3 = ref('unit')
</script>

<style scoped>
.radio-test {
  padding: 20px;
}

.test-section {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

h4 {
  margin-bottom: 10px;
}

p {
  margin-top: 10px;
  color: #666;
}
</style>

