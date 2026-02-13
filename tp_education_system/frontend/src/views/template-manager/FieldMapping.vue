<template>
  <div class="field-mapping-container">
    <el-card class="mapping-card">
      <template #header>
        <div class="card-header">
          <span>字段映射配置 - {{ templateName }}</span>
          <div class="header-actions">
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="saveMapping" :loading="saving">保存映射</el-button>
          </div>
        </div>
      </template>

      <div class="mapping-content">
        <!-- 选择中间表 -->
        <div class="section">
          <h3>1. 选择数据来源（中间表）</h3>
          <el-select 
            v-model="selectedTable" 
            placeholder="请选择中间表"
            @change="handleTableChange"
            style="width: 300px"
          >
            <el-option
              v-for="table in intermediateTables"
              :key="table.name"
              :label="table.name_cn"
              :value="table.name"
            />
          </el-select>
        </div>

        <!-- 字段映射 -->
        <div class="section" v-if="selectedTable">
          <h3>2. 配置字段映射</h3>
          <p class="tip">请将模板占位符与中间表字段进行匹配</p>
          
          <el-table :data="mappingList" border style="width: 100%">
            <el-table-column prop="placeholder" label="模板占位符" width="200">
              <template #default="{ row }">
                <el-tag type="primary">{{ row.placeholder }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="映射关系" width="100" align="center">
              <template #default>
                <el-icon><ArrowRight /></el-icon>
              </template>
            </el-table-column>
            
            <el-table-column label="中间表字段" min-width="300">
              <template #default="{ row, $index }">
                <el-select 
                  v-model="row.selectedField" 
                  placeholder="请选择字段"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="field in tableFields"
                    :key="field.name"
                    :label="field.name_cn"
                    :value="field.name"
                  >
                    <span>{{ field.name_cn }}</span>
                    <span class="field-type">({{ field.type }})</span>
                  </el-option>
                </el-select>
              </template>
            </el-table-column>
            
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.selectedField" type="success">已配置</el-tag>
                <el-tag v-else type="warning">未配置</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 统计信息 -->
        <div class="section" v-if="selectedTable">
          <el-alert
            :title="`已配置 ${configuredCount}/${mappingList.length} 个字段映射`"
            :type="configuredCount === mappingList.length ? 'success' : 'info'"
            show-icon
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 模板信息
const templateId = computed(() => Number(route.params.id))
const templateName = ref('')

// 中间表列表
const intermediateTables = ref<any[]>([])
const selectedTable = ref('')
const selectedTableCn = ref('')

// 表字段列表
const tableFields = ref<any[]>([])

// 映射列表
const mappingList = ref<any[]>([])

// 保存状态
const saving = ref(false)

// 计算已配置的字段数
const configuredCount = computed(() => {
  return mappingList.value.filter(m => m.selectedField).length
})

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取中间表列表
const loadIntermediateTables = async () => {
  try {
    const response = await fetch('/api/template-field-mapping/intermediate-tables')
    if (response.ok) {
      const result = await response.json()
      intermediateTables.value = result.tables || []
    }
  } catch (error) {
    console.error('加载中间表列表失败:', error)
    ElMessage.error('加载中间表列表失败')
  }
}

// 获取模板占位符
const loadTemplatePlaceholders = async () => {
  try {
    console.log('正在加载模板占位符，模板ID:', templateId.value)
    console.log('路由参数id:', route.params.id)
    const url = `/api/template-field-mapping/template-placeholders/${templateId.value}`
    console.log('请求URL:', url)
    const response = await fetch(url)
    console.log('API响应状态:', response.status)
    console.log('API响应状态文本:', response.statusText)
    if (response.ok) {
      const result = await response.json()
      console.log('API返回数据:', result)
      templateName.value = result.template_name
      // 初始化映射列表
      if (result.placeholders && result.placeholders.length > 0) {
        mappingList.value = result.placeholders.map((p: any) => ({
          placeholder: p.name,
          placeholderCn: p.name_cn,
          selectedField: ''
        }))
        console.log('映射列表已更新:', mappingList.value)
      } else {
        console.warn('API返回的占位符为空')
        mappingList.value = []
      }
    } else {
      console.error('API响应失败:', response.statusText)
      ElMessage.error('加载模板占位符失败: ' + response.statusText)
    }
  } catch (error) {
    console.error('加载模板占位符失败:', error)
    ElMessage.error('加载模板占位符失败')
  }
}

// 获取表字段
const loadTableFields = async (tableName: string) => {
  try {
    const response = await fetch(`/api/template-field-mapping/table-fields/${tableName}`)
    if (response.ok) {
      const result = await response.json()
      tableFields.value = result.fields || []
      selectedTableCn.value = result.table_name_cn
    }
  } catch (error) {
    console.error('加载表字段失败:', error)
    ElMessage.error('加载表字段失败')
  }
}

// 加载已保存的映射
const loadSavedMapping = async () => {
  try {
    const response = await fetch(`/api/template-field-mapping/get-mapping/${templateId.value}`)
    if (response.ok) {
      const result = await response.json()
      if (result.intermediate_table) {
        selectedTable.value = result.intermediate_table
        selectedTableCn.value = result.intermediate_table_cn
        // 加载表字段
        await loadTableFields(result.intermediate_table)
        // 恢复映射
        result.mappings.forEach((m: any) => {
          const item = mappingList.value.find(item => item.placeholder === m.placeholder)
          if (item) {
            item.selectedField = m.field
          }
        })
      }
    }
  } catch (error) {
    console.error('加载已保存映射失败:', error)
  }
}

// 选择表变化
const handleTableChange = async (tableName: string) => {
  if (!tableName) return
  
  const table = intermediateTables.value.find(t => t.name === tableName)
  if (table) {
    selectedTableCn.value = table.name_cn
  }
  
  await loadTableFields(tableName)
  // 清空已选择的字段
  mappingList.value.forEach(m => m.selectedField = '')
}

// 保存映射
const saveMapping = async () => {
  if (!selectedTable.value) {
    ElMessage.warning('请先选择中间表')
    return
  }
  
  // 检查是否有未配置的字段
  const unconfigured = mappingList.value.filter(m => !m.selectedField)
  if (unconfigured.length > 0) {
    const confirm = await ElMessageBox.confirm(
      `有 ${unconfigured.length} 个字段未配置，是否继续保存？`,
      '提示',
      {
        confirmButtonText: '继续保存',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).catch(() => false)
    
    if (!confirm) return
  }
  
  saving.value = true
  
  try {
    const mappings = mappingList.value
      .filter(m => m.selectedField)
      .map(m => {
        const field = tableFields.value.find(f => f.name === m.selectedField)
        return {
          placeholder: m.placeholder,
          field: m.selectedField,
          field_cn: field?.name_cn || m.selectedField
        }
      })
    
    const response = await fetch('/api/template-field-mapping/save-mapping', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: templateId.value,
        template_name: templateName.value,
        intermediate_table: selectedTable.value,
        intermediate_table_cn: selectedTableCn.value,
        mappings
      })
    })
    
    if (response.ok) {
      ElMessage.success('保存成功')
    } else {
      throw new Error('保存失败')
    }
  } catch (error) {
    console.error('保存映射失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 初始化
onMounted(async () => {
  console.log('FieldMapping页面挂载')
  console.log('路由参数:', route.params)
  console.log('模板ID:', templateId.value)
  await Promise.all([
    loadIntermediateTables(),
    loadTemplatePlaceholders()
  ])
  // 加载已保存的映射
  await loadSavedMapping()
})
</script>

<style scoped>
.field-mapping-container {
  padding: 20px;
}

.mapping-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.section {
  margin-bottom: 30px;
}

.section h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.tip {
  color: #666;
  margin-bottom: 15px;
  font-size: 14px;
}

.field-type {
  color: #999;
  font-size: 12px;
  margin-left: 5px;
}
</style>
