<template>
  <div class="simple-test">
    <h3>字段提取测试</h3>
    <el-button @click="testExtract" :loading="loading">测试提取字段</el-button>
    
    <div v-if="fields.length > 0" class="fields-list">
      <h4>提取到 {{ fields.length }} 个字段:</h4>
      <div v-for="(field, index) in fields" :key="index" class="field-item">
        <div><strong>{{ field.field_label }}</strong></div>
        <div>位置: 第{{ field.position_data?.page }}页 ({{ Math.round(field.position_data?.x) }}, {{ Math.round(field.position_data?.y) }})</div>
        <div>区域: 区域{{ field.region_id }}</div>
      </div>
    </div>
    
    <div v-else-if="tested" class="no-fields">
      没有提取到字段
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  templateId: string
}>()

const loading = ref(false)
const tested = ref(false)
const fields = ref<any[]>([])

const testExtract = async () => {
  loading.value = true
  tested.value = false
  
  try {
    const response = await fetch(`/api/templates/${props.templateId}/a3-regions/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: 1,
        regions: [
          { id: 1, bounds: { x0: 85, y0: 85, x1: 585.3, y1: 756.9 } },
          { id: 2, bounds: { x0: 605.3, y0: 85, x1: 1105.5, y1: 756.9 } }
        ]
      })
    })
    
    const result = await response.json()
    console.log('提取结果:', result)
    
    if (result.status === 'success') {
      fields.value = result.fields.map((f: any, index: number) => ({
        field_name: f.name || `field_${index}`,
        field_label: f.label || f.name || `字段${index + 1}`,
        data_source: '',
        cell_ref: `第${f.page}页 (${Math.round(f.x)},${Math.round(f.y)})`,
        position_data: { x: f.x, y: f.y, page: f.page },
        default_value: '',
        sort_order: index,
        confidence: f.confidence,
        match_status: f.confidence > 0.8 ? 'high' : f.confidence > 0.5 ? 'medium' : 'low',
        region_id: f.region_id
      }))
      
      ElMessage.success(`成功提取 ${fields.value.length} 个字段`)
    } else {
      ElMessage.error('提取失败')
    }
  } catch (error) {
    console.error('提取失败:', error)
    ElMessage.error('提取失败')
  } finally {
    loading.value = false
    tested.value = true
  }
}
</script>

<style scoped>
.simple-test {
  padding: 20px;
}

.fields-list {
  margin-top: 20px;
}

.field-item {
