<template>
  <div class="generic-data-view">
    <el-card class="box-card" style="height: calc(100vh - 120px);">
      <template #header>
        <div class="card-header">
          <span>{{ tableTitle }}</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入搜索关键词"
              size="small"
              style="width: 200px; margin-right: 10px;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button size="small" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <div class="card-body">
        <!-- 第一行：通用按钮栏 -->
        <CommonActionBar
          :selected-rows="selectedRows"
          @create="handleCreate"
          @edit="handleEdit"
          @delete="handleDelete"
          @import="handleImport"
          @export="handleExport"
          @refresh="handleRefresh"
          @filter="handleFilter"
        />

        <!-- 第二行：专用按钮栏 -->
        <DynamicActionBar
          :table-name="tableName"
          :selected-rows="selectedRows"
          @action="handleDynamicAction"
        />

        <!-- 筛选区域 -->
        <div v-if="showFilter" class="filter-section">
          <el-form :model="filterForm" inline>
            <el-form-item
              v-for="field in filterableFields"
              :key="field.name"
              :label="field.label || field.source_name || field.name"
            >
              <el-input
                v-if="field.type === 'VARCHAR' || field.type === 'TEXT'"
                v-model="filterForm[field.name]"
                :placeholder="`请输入${field.label || field.source_name || field.name}`"
                clearable
              />
              <el-input-number
                v-else-if="field.type === 'INTEGER' || field.type === 'DECIMAL'"
                v-model="filterForm[field.name]"
                :placeholder="`请输入${field.label || field.source_name || field.name}`"
                clearable
              />
              <el-date-picker
                v-else-if="field.type === 'DATE' || field.type === 'DATETIME'"
                v-model="filterForm[field.name]"
                :placeholder="`请选择${field.label || field.source_name || field.name}`"
                clearable
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="applyFilter">筛选</el-button>
              <el-button @click="resetFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 数据表格 -->
        <div class="table-section">
          <el-table
            :data="tableData"
            style="width: 100%"
            border
            max-height="calc(100vh - 350px)"
            @selection-change="handleSelectionChange"
            v-loading="loading"
            :fit="true"
          >
            <el-table-column type="selection" width="55" fixed />
            <el-table-column type="index" label="序号" width="60" fixed />

            <el-table-column
              v-for="field in displayFields"
              :key="field.name"
              :prop="field.name"
              :label="field.label || field.source_name || field.name"
              min-width="120"
              show-overflow-tooltip
              resizable
            >
              <template #default="{ row }">
                <!-- 通用字典关联显示 - 如果存在 {字段名}_name 则显示中文名称 -->
                <span v-if="row[getDictAlias(field.name)]">
                  {{ row[getDictAlias(field.name)] }}
                </span>
                <span v-else-if="field.type === 'BOOLEAN'">
                  {{ row[field.name] ? '是' : '否' }}
                </span>
                <span v-else-if="field.type === 'DATE'">
                  {{ formatDate(row[field.name]) }}
                </span>
                <span v-else-if="field.type === 'DATETIME'">
                  {{ formatDateTime(row[field.name]) }}
                </span>
                <span v-else>{{ row[field.name] }}</span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleEdit(row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页 -->
        <div class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalCount"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item
          v-for="field in editableFields"
          :key="field.name"
          :label="field.label || field.source_name || field.name"
          :prop="field.name"
        >
          <el-input
            v-if="field.type === 'VARCHAR' || field.type === 'TEXT'"
            v-model="formData[field.name]"
            :type="field.type === 'TEXT' ? 'textarea' : 'text'"
            :rows="field.type === 'TEXT' ? 3 : 1"
            :placeholder="`请输入${field.label || field.source_name || field.name}`"
          />
          <el-input-number
            v-else-if="field.type === 'INTEGER'"
            v-model="formData[field.name]"
            :placeholder="`请输入${field.label || field.source_name || field.name}`"
            style="width: 100%"
          />
          <el-input-number
            v-else-if="field.type === 'DECIMAL'"
            v-model="formData[field.name]"
            :precision="field.scale || 2"
            :placeholder="`请输入${field.label || field.source_name || field.name}`"
            style="width: 100%"
          />
          <el-date-picker
            v-else-if="field.type === 'DATE'"
            v-model="formData[field.name]"
            type="date"
            :placeholder="`请选择${field.label || field.source_name || field.name}`"
            style="width: 100%"
          />
          <el-date-picker
            v-else-if="field.type === 'DATETIME'"
            v-model="formData[field.name]"
            type="datetime"
            :placeholder="`请选择${field.label || field.source_name || field.name}`"
            style="width: 100%"
          />
          <el-switch
            v-else-if="field.type === 'BOOLEAN'"
            v-model="formData[field.name]"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出数据"
      width="500px"
      destroy-on-close
    >
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="excel">Excel (.xlsx)</el-radio>
            <el-radio label="pdf">PDF (.pdf)</el-radio>
            <el-radio label="sql">SQL数据库 (.sql)</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="导出范围">
          <el-radio-group v-model="exportForm.scope">
            <el-radio label="all">全部数据</el-radio>
            <el-radio label="current">当前页</el-radio>
            <el-radio label="selected">选中行</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="保存位置" v-if="exportForm.format !== 'sql'">
          <el-input
            v-model="exportForm.path"
            placeholder="请选择或输入保存路径"
            clearable
          >
            <template #append>
              <el-button @click="selectFolder">浏览...</el-button>
            </template>
          </el-input>
          <div class="path-hint">点击"浏览"选择文件夹，或手动输入路径</div>
        </el-form-item>
        
        <el-form-item label="文件名">
          <el-input
            v-model="exportForm.filename"
            :placeholder="`${tableTitle}_${getCurrentDate()}`"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="executeExport" :loading="exporting">
          导出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTagsStore } from '@/store/tags'
import CommonActionBar from '@/components/data/CommonActionBar.vue'
import DynamicActionBar from '@/components/data/DynamicActionBar.vue'

const route = useRoute()
const tagsStore = useTagsStore()

// 表名和标题
const tableName = computed(() => {
  // 尝试从路由参数获取表名，支持多种路由格式
  const params = route.params as Record<string, string | string[]>
  
  console.log('=== 调试信息 ===')
  console.log('路由参数:', params)
  console.log('路由路径:', route.path)
  
  // 1. 直接 /data/:tableName 格式
  if (params.tableName) {
    const result = Array.isArray(params.tableName) ? params.tableName[0] : params.tableName
    console.log('从路由参数获取表名:', result)
    return result
  }
  
  // 2. 从路径最后一段获取（如 /module-xxx/table-name 或 /system/module-xxx/table-name）
  const pathParts = route.path.split('/').filter(Boolean)
  console.log('路径分割:', pathParts)
  if (pathParts.length > 0) {
    const lastPart = pathParts[pathParts.length - 1]
    console.log('最后一段:', lastPart)
    // 如果最后一段看起来像表名（包含下划线或data_前缀或dict_前缀）
    if (lastPart.includes('_') || lastPart.startsWith('data_') || lastPart.startsWith('dict_')) {
      console.log('从路径最后一段获取表名:', lastPart)
      return lastPart
    }
  }
  
  console.log('未找到表名，返回空字符串')
  return ''
})

// 从navigation.json获取节点中文名
const nodeTitle = ref('数据管理')

// 加载节点名称
const loadNodeTitle = async () => {
  try {
    const response = await fetch('/api/navigation-admin/tree')
    if (response.ok) {
      const data = await response.json()
      const currentPath = route.path
      
      // 递归查找匹配的节点
      const findNodeTitle = (modules: any[]): string | null => {
        for (const module of modules) {
          // 检查当前节点
          if (module.path === currentPath && module.table_name === tableName.value) {
            return module.title
          }
          // 递归检查子节点
          if (module.children && module.children.length > 0) {
            const found = findNodeTitle(module.children)
            if (found) return found
          }
        }
        return null
      }
      
      const title = findNodeTitle(data.modules || [])
      if (title) {
        nodeTitle.value = title
        
        // 更新标签页标题
        const currentPath = route.path
        const existingTag = tagsStore.tagsList.find(t => t.path === currentPath)
        if (existingTag) {
          // 更新现有标签的标题
          existingTag.title = title
        } else {
          // 添加新标签
          tagsStore.addTag({
            path: currentPath,
            title: title,
            icon: 'Document'
          })
        }
      }
    }
  } catch (error) {
    console.error('加载节点名称失败:', error)
  }
}

// 计算属性：表格标题（使用节点中文名）
const tableTitle = computed(() => nodeTitle.value)

// 加载状态
const loading = ref(false)

// 表格数据
const tableData = ref<any[]>([])
const selectedRows = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// 表结构
const tableSchema = ref<any>(null)

// 筛选
const showFilter = ref(false)
const filterForm = ref<Record<string, any>>({})

// 搜索
const searchKeyword = ref('')

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const formData = ref<Record<string, any>>({})
const isEditing = ref(false)
const currentRow = ref<any>(null)

// 导出相关
const exportDialogVisible = ref(false)
const exporting = ref(false)
const exportForm = ref({
  format: 'excel',
  scope: 'all',
  path: '',
  filename: ''
})

// 获取当前日期
const getCurrentDate = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

// 计算属性：显示字段
const displayFields = computed(() => {
  return tableSchema.value?.fields?.filter((f: any) => f.name !== 'id' && !f.hidden) || []
})

// 计算属性：可编辑字段
const editableFields = computed(() => {
  return displayFields.value.filter((f: any) => f.name !== 'created_at' && f.name !== 'updated_at')
})

// 计算属性：可筛选字段
const filterableFields = computed(() => {
  return displayFields.value.filter((f: any) => 
    ['VARCHAR', 'INTEGER', 'DECIMAL', 'DATE', 'DATETIME'].includes(f.type)
  )
})

// 计算属性：表单验证规则
const formRules = computed(() => {
  const rules: Record<string, any[]> = {}
  editableFields.value.forEach((field: any) => {
    const fieldRules = []
    if (field.required) {
      const fieldLabel = field.label || field.source_name || field.name
      fieldRules.push({ required: true, message: `请输入${fieldLabel}`, trigger: 'blur' })
    }
    rules[field.name] = fieldRules
  })
  return rules
})

// 加载表结构
const loadTableSchema = async () => {
  try {
    const response = await fetch(`/api/data/schema/${tableName.value}`)
    if (response.ok) {
      tableSchema.value = await response.json()
    } else {
      // 使用默认结构
      tableSchema.value = {
        fields: [
          { name: 'id', type: 'INTEGER', required: true },
          { name: 'name', type: 'VARCHAR', length: 50 },
          { name: 'created_at', type: 'DATETIME' }
        ]
      }
    }
  } catch (error) {
    console.error('加载表结构失败:', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    console.log('=== 加载数据调试信息 ===')
    console.log('表名(tableName.value):', tableName.value)
    
    if (!tableName.value) {
      console.error('表名为空，无法加载数据')
      ElMessage.error('表名不存在，无法加载数据')
      tableData.value = []
      totalCount.value = 0
      loading.value = false
      return
    }
    
    // 构建查询参数
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString()
    })
    
    // 添加搜索关键词
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value)
    }
    
    // 添加筛选条件
    const filterParams: Record<string, string> = {}
    Object.entries(filterForm.value).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        filterParams[key] = String(value)
      }
    })
    
    if (Object.keys(filterParams).length > 0) {
      params.append('filter', JSON.stringify(filterParams))
    }

    const apiUrl = `/api/data/${tableName.value}?${params.toString()}`
    console.log('API请求URL:', apiUrl)
    
    try {
      const response = await fetch(apiUrl)
      console.log('API响应状态:', response.status)
      
      if (response.ok) {
        const result = await response.json()
        console.log('API返回数据:', result)
        tableData.value = result.data || []
        totalCount.value = result.total || 0
        console.log('加载数据成功，共', totalCount.value, '条记录')
      } else {
        console.error('API请求失败:', response.status, await response.text())
        // 表可能存在但没有数据，或者API暂时不可用
        // 保持空数据状态，不显示错误
        tableData.value = []
        totalCount.value = 0
        console.log('表可能存在但没有数据，显示空表格')
      }
    } catch (apiError) {
      console.error('API请求异常:', apiError)
      // API请求异常，可能是网络问题或服务暂时不可用
      // 保持空数据状态，不显示错误
      tableData.value = []
      totalCount.value = 0
      console.log('API请求异常，显示空表格')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    // 捕获其他错误，保持空数据状态
    tableData.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
  loadData()
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 获取列宽
const getColumnWidth = (field: any) => {
  switch (field.type) {
    case 'VARCHAR':
      return Math.min(field.length || 100, 200)
    case 'INTEGER':
    case 'DECIMAL':
      return 100
    case 'DATE':
      return 120
    case 'DATETIME':
      return 150
    case 'BOOLEAN':
      return 80
    default:
      return 150
  }
}

// 格式化日期
const formatDate = (value: any) => {
  if (!value) return ''
  const date = new Date(value)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (value: any) => {
  if (!value) return ''
  const date = new Date(value)
  return date.toLocaleString('zh-CN')
}

// 获取字典关联字段的别名
const getDictAlias = (fieldName: string) => {
  return `${fieldName}_name`
}

// 通用按钮事件
const handleCreate = () => {
  isEditing.value = false
  currentRow.value = null
  formData.value = {}
  dialogTitle.value = '新增数据'
  dialogVisible.value = true
}

const handleEdit = (row?: any) => {
  if (row) {
    isEditing.value = true
    currentRow.value = row
    formData.value = { ...row }
    dialogTitle.value = '编辑数据'
    dialogVisible.value = true
  } else if (selectedRows.value.length === 1) {
    handleEdit(selectedRows.value[0])
  } else {
    ElMessage.warning('请选择一条记录')
  }
}

const handleDelete = async (row?: any) => {
  const rowsToDelete = row ? [row] : selectedRows.value
  
  if (rowsToDelete.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${rowsToDelete.length} 条记录吗？`,
      '确认删除',
      { type: 'warning' }
    )

    // 调用删除API
      for (const row of rowsToDelete) {
        await fetch(`/api/data/${tableName.value}/${row.id}`, {
          method: 'DELETE'
        })
      }

    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleImport = () => {
  // 跳转到导入页面
  window.location.href = '/import/workbench'
}

const handleExport = () => {
  // 设置默认文件名（使用节点中文名）
  exportForm.value.filename = `${tableTitle.value}_${getCurrentDate()}`
  // 路径为空，让用户自己选择
  exportDialogVisible.value = true
}

// 选择文件夹
const selectFolder = async () => {
  try {
    // 调用后端API打开文件夹选择对话框
    const response = await fetch('/api/select-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        current_path: exportForm.value.path || '' 
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.selected_path) {
        exportForm.value.path = result.selected_path
      }
    } else {
      // 如果后端不支持，回退到提示用户手动输入
      ElMessage.info('请手动输入保存路径')
    }
  } catch (error) {
    console.error('选择文件夹失败:', error)
    ElMessage.info('请手动输入保存路径')
  }
}

// 执行导出
const executeExport = async () => {
  exporting.value = true
  
  try {
    // 准备导出数据
    let exportData: any[] = []
    
    console.log('=== 导出调试信息 ===')
    console.log('导出范围:', exportForm.value.scope)
    console.log('当前路由参数:', route.params)
    console.log('当前表名(tableName):', tableName.value)
    console.log('当前路径(route.path):', route.path)
    console.log('当前页数据条数:', tableData.value.length)
    console.log('选中行数:', selectedRows.value.length)
    console.log('====================')
    
    switch (exportForm.value.scope) {
      case 'selected':
        exportData = selectedRows.value
        break
      case 'current':
        exportData = tableData.value
        break
      case 'all':
      default:
        // 获取所有数据
        console.log('正在获取全部数据...')
        const response = await fetch(
          `/api/data/${tableName.value}?page=1&size=10000`
        )
        console.log('API响应状态:', response.status)
        if (response.ok) {
          const result = await response.json()
          console.log('API返回数据条数:', result.data?.length)
          exportData = result.data || []
        } else {
          const errorText = await response.text()
          console.error('API错误:', errorText)
        }
        break
    }
    
    console.log('最终导出数据条数:', exportData.length)
    
    if (exportData.length === 0) {
      ElMessage.warning('没有数据可导出')
      exporting.value = false
      return
    }
    
    // 调用后端导出API
    const exportResponse = await fetch('/api/data/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: tableName.value,
        data: exportData,
        format: exportForm.value.format,
        filename: exportForm.value.filename,
        path: exportForm.value.path
      })
    })
    
    if (exportResponse.ok) {
      const result = await exportResponse.json()
      console.log('导出成功，返回结果:', JSON.stringify(result, null, 2))
      console.log('result类型:', typeof result)
      console.log('result.keys:', Object.keys(result))
      const savedPath = result.file_path || result.path || JSON.stringify(result)
      ElMessage.success(`导出成功，文件保存到: ${savedPath}`)
      exportDialogVisible.value = false
    } else {
      const error = await exportResponse.json()
      ElMessage.error(error.detail || '导出失败')
    }
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

const handleRefresh = () => {
  loadData()
  ElMessage.success('刷新成功')
}

const handleFilter = () => {
  showFilter.value = !showFilter.value
}

// 筛选操作
const applyFilter = () => {
  currentPage.value = 1
  loadData()
}

const resetFilter = () => {
  filterForm.value = {}
  applyFilter()
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    const url = isEditing.value
      ? `/api/data/${tableName.value}/${currentRow.value.id}`
      : `/api/data/${tableName.value}`
    
    const method = isEditing.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })

    if (response.ok) {
      ElMessage.success(isEditing.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadData()
    } else {
      throw new Error('操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  }
}

// 专用按钮事件
const handleDynamicAction = (action: string, data?: any) => {
  switch (action) {
    case 'smartFill':
      ElMessage.info('智能填充功能')
      break
    case 'batchTag':
      ElMessage.info('批量打标签功能')
      break
    case 'generateReport':
      ElMessage.info('生成报表功能')
      break
    default:
      console.log('未知操作:', action, data)
  }
}

// 分页事件
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadData()
}

// 监听搜索关键词变化，实现实时搜索
watch(searchKeyword, (newValue) => {
  currentPage.value = 1 // 重置到第一页
  loadData()
})

// 监听筛选条件变化，实现即时筛选
watch(filterForm, (newValue) => {
  currentPage.value = 1 // 重置到第一页
  loadData()
}, { deep: true })

// 监听路由变化
watch(() => route.params.tableName, () => {
  loadTableSchema()
  loadNodeTitle()  // 重新加载节点中文名
  loadData()
})

// 组件挂载
onMounted(() => {
  loadTableSchema()
  loadNodeTitle()  // 加载节点中文名
  loadData()
})
</script>

<style scoped>
.generic-data-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.filter-section {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.table-section {
  flex: 1;
}

.pagination-section {
  display: flex;
  justify-content: flex-end;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.path-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
