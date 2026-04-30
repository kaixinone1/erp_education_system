<template>
  <div class="test-page">
    <h1>测试表格</h1>
    <table border="1" style="border-collapse: collapse;">
      <tr>
        <td colspan="2">标题1</td>
        <td colspan="3">标题2</td>
        <td>标题3</td>
      </tr>
      <tr>
        <td>项目</td>
        <td>人数</td>
        <td>标准</td>
        <td>小计</td>
        <td rowspan="2">审批区1</td>
        <td rowspan="2">审批区2</td>
      </tr>
      <tr>
        <td>行政人员</td>
        <td>5</td>
        <td>1185</td>
        <td>5925</td>
      </tr>
    </table>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.test-page {
  padding: 20px;
}

table {
  border: 1px solid #000;
}

td {
  border: 1px solid #000;
  padding: 5px 10px;
  text-align: center;
}
</style>
