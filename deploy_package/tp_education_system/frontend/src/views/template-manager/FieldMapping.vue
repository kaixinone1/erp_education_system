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
        <!-- 说明 -->
        <el-alert
          title="每个模板占位符都可以从不同的数据源表获取数据，可使用聚合函数和过滤条件进行统计"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <!-- 字段映射表格 -->
        <div class="section">
          <h3>配置字段映射</h3>
          <p class="tip">请为每个模板占位符配置数据源表、字段、聚合函数和过滤条件。示例：统计副处级人数 → 数据源表:教师基础信息, 字段:id, 聚合函数:COUNT, 过滤条件:行政级别='副处级'</p>
          
          <el-table :data="mappingList" border style="width: 100%">
            <el-table-column prop="placeholder" label="模板占位符" width="140">
              <template #default="{ row }">
                <el-tag type="primary">{{ row.placeholder }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="数据源表" min-width="160">
              <template #default="{ row }">
                <el-select 
                  v-model="row.selectedTable" 
                  placeholder="选择数据源表"
                  style="width: 100%"
                  clearable
                  @change="(val) => handleRowTableChange(row, val)"
                >
                  <el-option
                    v-for="table in sourceTables"
                    :key="table.name"
                    :label="table.name_cn"
                    :value="table.name"
                  />
                </el-select>
              </template>
            </el-table-column>
            
            <el-table-column label="字段" min-width="130">
              <template #default="{ row }">
                <el-select 
                  v-model="row.selectedField" 
                  placeholder="选择字段"
                  style="width: 100%"
                  clearable
                  :disabled="!row.selectedTable"
                  @change="() => { row.aggregateFunc = ''; row.filterCondition = '' }"
                >
                  <el-option
                    v-for="field in getFieldsForTable(row.selectedTable)"
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
            
            <el-table-column label="聚合函数" width="110">
              <template #default="{ row }">
                <el-select 
                  v-model="row.aggregateFunc" 
                  placeholder="无"
                  style="width: 100%"
                  clearable
                  :disabled="!row.selectedField"
                >
                  <el-option label="计数 COUNT" value="COUNT" />
                  <el-option label="求和 SUM" value="SUM" />
                  <el-option label="最大值 MAX" value="MAX" />
                  <el-option label="最小值 MIN" value="MIN" />
                  <el-option label="平均值 AVG" value="AVG" />
                </el-select>
              </template>
            </el-table-column>
            
            <el-table-column label="过滤条件" min-width="220">
              <template #default="{ row }">
                <div class="filter-condition-cell">
                  <el-select
                    v-model="row.selectedFilterTemplate"
                    placeholder="选择预设条件"
                    style="width: 100%; margin-bottom: 5px"
                    clearable
                    :disabled="!row.selectedField"
                    @change="(val) => handleFilterTemplateChange(row, val)"
                  >
                    <el-option-group
                      v-for="group in filterConditionGroups"
                      :key="group.category"
                      :label="group.category"
                    >
                      <el-option
                        v-for="item in group.conditions"
                        :key="item.id"
                        :label="item.name"
                        :value="item.filter_condition"
                      />
                    </el-option-group>
                  </el-select>
                  <el-input
                    v-model="row.filterCondition"
                    placeholder="或自定义: 行政级别='副处级'"
                    :disabled="!row.selectedField"
                    clearable
                    size="small"
                  />
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.selectedField" type="success">已配置</el-tag>
                <el-tag v-else type="warning">未配置</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 统计信息 -->
        <div class="section">
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

const templateId = computed(() => {
  const id = route.params.id as string
  try {
    return decodeURIComponent(id)
  } catch {
    return id
  }
})
const templateName = ref('')

const sourceTables = ref<any[]>([])
const tableFieldsMap = ref<Record<string, any[]>>({})
const filterConditionGroups = ref<any[]>([])

const mappingList = ref<any[]>([])

const saving = ref(false)

const configuredCount = computed(() => {
  return mappingList.value.filter(m => m.selectedField).length
})

const goBack = () => {
  router.back()
}

const loadSourceTables = async () => {
  try {
    const response = await fetch('/api/template-field-mapping/intermediate-tables')
    if (response.ok) {
      const result = await response.json()
      sourceTables.value = result.tables || []
      
      for (const table of sourceTables.value) {
        await loadTableFields(table.name)
      }
    }
  } catch (error) {
    console.error('加载源数据表列表失败:', error)
    ElMessage.error('加载源数据表列表失败')
  }
}

const loadTableFields = async (tableName: string) => {
  try {
    const response = await fetch(`/api/template-field-mapping/table-fields/${tableName}`)
    if (response.ok) {
      const result = await response.json()
      tableFieldsMap.value[tableName] = result.fields || []
    }
  } catch (error) {
    console.error(`加载表 ${tableName} 字段失败:`, error)
  }
}

const getFieldsForTable = (tableName: string) => {
  return tableFieldsMap.value[tableName] || []
}

const loadFilterConditions = async () => {
  try {
    const response = await fetch('/api/filter-conditions/list')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        // 按类别分组
        const grouped: Record<string, any[]> = {}
        result.data.forEach((item: any) => {
          if (!grouped[item.category]) {
            grouped[item.category] = []
          }
          grouped[item.category].push(item)
        })
        
        filterConditionGroups.value = Object.entries(grouped).map(([category, conditions]) => ({
          category,
          conditions
        }))
      }
    }
  } catch (error) {
    console.error('加载过滤条件失败:', error)
  }
}

const handleFilterTemplateChange = (row: any, filterCondition: string) => {
  if (filterCondition) {
    row.filterCondition = filterCondition
  }
}

const loadTemplatePlaceholders = async () => {
  try {
    if (!templateId.value || templateId.value === 'undefined' || templateId.value === '') {
      ElMessage.error('模板ID无效，请先选择模板')
      // 跳转到模板列表
      setTimeout(() => {
        router.push('/template-manager')
      }, 1500)
      return
    }
    
    const url = `/api/template-field-mapping/template-placeholders/${templateId.value}`
    const response = await fetch(url)
    
    if (response.ok) {
      const result = await response.json()
      templateName.value = result.template_name
      
      if (result.placeholders && result.placeholders.length > 0) {
        mappingList.value = result.placeholders.map((p: any) => ({
          placeholder: p.name,
          placeholderCn: p.name_cn,
          selectedTable: '',
          selectedField: '',
          aggregateFunc: '',
          filterCondition: '',
          selectedFilterTemplate: ''
        }))
      } else {
        mappingList.value = []
      }
    } else {
      ElMessage.error('加载模板占位符失败')
    }
  } catch (error) {
    console.error('加载模板占位符失败:', error)
    ElMessage.error('加载模板占位符失败')
  }
}

const loadSavedMapping = async () => {
  try {
    if (!templateId.value || templateId.value === 'undefined' || templateId.value === '') {
      return
    }
    
    const encodedTemplateId = encodeURIComponent(templateId.value)
    const response = await fetch(`/api/template-field-mapping/get-mapping/${encodedTemplateId}`)
    
    if (response.ok) {
      const result = await response.json()
      
      if (result.mappings && result.mappings.length > 0) {
        result.mappings.forEach((m: any) => {
          const item = mappingList.value.find(item => item.placeholder === m.placeholder)
          if (item) {
            item.selectedTable = m.table || m.intermediate_table || ''
            item.selectedField = m.field || m.intermediate_field || ''
            item.aggregateFunc = m.aggregate_func || ''
            item.filterCondition = m.filter_condition || ''
          }
        })
      }
    }
  } catch (error) {
    console.error('加载已保存映射失败:', error)
  }
}

const handleRowTableChange = (row: any, tableName: string) => {
  row.selectedField = ''
  row.aggregateFunc = ''
  row.filterCondition = ''
}

const saveMapping = async () => {
  const configuredMappings = mappingList.value.filter(m => m.selectedField)
  
  if (configuredMappings.length === 0) {
    ElMessage.warning('请至少配置一个字段映射')
    return
  }
  
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
    for (const mapping of configuredMappings) {
      const tableName = mapping.selectedTable
      const fields = tableFieldsMap.value[tableName] || []
      const field = fields.find(f => f.name === mapping.selectedField)
      
      await fetch('/api/template-field-mapping/save-mapping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: templateId.value,
          template_name: templateName.value,
          intermediate_table: mapping.selectedTable,
          intermediate_table_cn: sourceTables.value.find(t => t.name === mapping.selectedTable)?.name_cn || '',
          mappings: [{
            placeholder: mapping.placeholder,
            field: mapping.selectedField,
            field_cn: field?.name_cn || mapping.selectedField,
            aggregate_func: mapping.aggregateFunc || '',
            filter_condition: mapping.filterCondition || ''
          }]
        })
      })
    }
    
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存映射失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadSourceTables()
  await loadFilterConditions()
  await loadTemplatePlaceholders()
  await loadSavedMapping()
})
</script>

<style scoped>
.field-mapping-container {
  padding: 20px;
}

.mapping-card {
  max-width: 1400px;
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

.filter-condition-cell {
  display: flex;
  flex-direction: column;
}
</style>
