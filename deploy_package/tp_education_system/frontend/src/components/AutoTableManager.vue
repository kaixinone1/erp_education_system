<template>
  <div class="auto-table-manager">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ chineseName || tableName }}</span>
          <div class="header-actions">
            <el-button size="small" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 功能按钮栏 -->
      <div class="action-bar">
        <el-button type="primary" size="small" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
        <el-button type="success" size="small" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        style="width: 100%"
        border
        v-loading="loading"
        :max-height="600"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column
          v-for="field in schema"
          :key="field.name"
          :prop="field.name"
          :label="field.label || field.name"
          :width="getColumnWidth(field)"
          sortable
        />
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
            <el-button 
              v-if="tableName === 'retirement_report_data'" 
              type="success" 
              size="small" 
              @click="handleCalculate(row)"
            >
              计算
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="viewReport(row)"
            >
              查看报表
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEditing ? '编辑' : '新增'"
      width="700px"
    >
      <el-form :model="formData" label-width="140px">
        <el-row :gutter="20">
          <el-col 
            :span="12" 
            v-for="field in schema" 
            :key="field.name"
          >
            <el-form-item :label="field.name">
              <el-input
                v-if="field.type === 'VARCHAR' || field.type === 'TEXT'"
                v-model="formData[field.name]"
                :type="field.type === 'TEXT' ? 'textarea' : 'text'"
                :rows="field.type === 'TEXT' ? 2 : 1"
              />
              <el-input-number
                v-else-if="field.type === 'INTEGER'"
                v-model="formData[field.name]"
                style="width: 100%"
              />
              <el-input-number
                v-else-if="field.type === 'DECIMAL'"
                v-model="formData[field.name]"
                :precision="2"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="field.type === 'DATE'"
                v-model="formData[field.name]"
                type="date"
                format="YYYY年M月D日"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
              <el-switch
                v-else-if="field.type === 'BOOLEAN'"
                v-model="formData[field.name]"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 计算弹窗 -->
    <AutoCalculatorDialog
      v-if="tableName === 'retirement_report_data'"
      v-model="calculatorVisible"
      :table-name="tableName"
      :teacher-id="selectedTeacherId"
      @saved="handleRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Download } from '@element-plus/icons-vue'
import AutoCalculatorDialog from './AutoCalculatorDialog.vue'

interface FieldSchema {
  name: string
  type: string
  length?: number
  nullable: boolean
}

const props = defineProps<{
  tableName: string
}>()

// 状态
const loading = ref(false)
const schema = ref<FieldSchema[]>([])
const tableData = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 编辑弹窗
const editDialogVisible = ref(false)
const isEditing = ref(false)
const formData = ref<Record<string, any>>({})

// 计算弹窗
const calculatorVisible = ref(false)
const selectedTeacherId = ref<number | null>(null)

// 中文表名
const chineseName = ref('')

// 获取表结构
const loadSchema = async () => {
  try {
    const response = await fetch(`/api/auto-table/${props.tableName}/schema`)
    const result = await response.json()
    if (result.status === 'success') {
      schema.value = result.data.fields
      chineseName.value = result.data.chinese_name || props.tableName
    }
  } catch (error) {
    console.error('加载表结构失败:', error)
    ElMessage.error('加载表结构失败')
  }
}

// 获取数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await fetch(
      `/api/auto-table/${props.tableName}/list?page=${currentPage.value}&page_size=${pageSize.value}`
    )
    const result = await response.json()
    if (result.status === 'success') {
      tableData.value = result.data
      total.value = result.total
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 获取列宽
const getColumnWidth = (field: FieldSchema) => {
  if (field.type === 'DATE') return 130
  if (field.type === 'INTEGER' || field.type === 'DECIMAL') return 100
  if (field.length && field.length > 50) return 150
  return 120
}

// 刷新
const handleRefresh = () => {
  loadData()
}

// 分页
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadData()
}

// 新增
const handleCreate = () => {
  isEditing.value = false
  formData.value = {}
  editDialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  isEditing.value = true
  formData.value = { ...row }
  editDialogVisible.value = true
}

// 保存
const handleSave = async () => {
  try {
    const teacherId = formData.value.teacher_id
    const url = `/api/auto-table/${props.tableName}/update/${teacherId}`
    
    const response = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
      editDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      type: 'warning'
    })
    
    const response = await fetch(
      `/api/auto-table/${props.tableName}/delete/${row.teacher_id}`,
      { method: 'DELETE' }
    )
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 计算
const handleCalculate = (row: any) => {
  selectedTeacherId.value = row.teacher_id
  calculatorVisible.value = true
}

// 查看报表 - 跳转到统一报表查看页面
const viewReport = (row: any) => {
  console.log('【AutoTableManager】viewReport 被调用，row:', row)
  // 直接使用 template_id - 从行数据中获取
  const templateId = row.template_id || props.tableName.replace('_data', '')
  const encodedTemplateId = encodeURIComponent(templateId)
  const teacherId = row.teacher_id || 0
  console.log('【AutoTableManager】跳转参数:', { templateId, teacherId, encodedTemplateId })
  router.push(`/report-view/${encodedTemplateId}/${teacherId}`)
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// 初始化
onMounted(() => {
  loadSchema()
  loadData()
})

// 监听表名变化
watch(() => props.tableName, () => {
  loadSchema()
  loadData()
})
</script>

<style scoped>
.auto-table-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  overflow-x: auto;
}
</style>
