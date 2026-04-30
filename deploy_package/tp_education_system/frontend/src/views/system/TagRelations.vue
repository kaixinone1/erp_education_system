<template>
  <div class="tag-relations-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">标签关系管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入搜索关键词"
              size="small"
              style="width: 200px; margin-right: 10px;"
              clearable
              @input="handleSearchInput"
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

      <!-- 第一行：通用按钮栏 -->
      <CommonActionBar
        :selected-rows="selectedRows"
        @create="handleCreate"
        @edit="handleEdit"
        @delete="handleBatchDelete"
        @import="handleImport"
        @export="handleExport"
        @refresh="handleRefresh"
        @filter="handleFilter"
      />

      <!-- 第二行：专用按钮栏 -->
      <DynamicActionBar
        table-name="tag_relations"
        :selected-rows="selectedRows"
        @action="handleDynamicAction"
      />

      <!-- 筛选区域 -->
      <div v-if="showFilter" class="filter-section">
        <el-form :model="filterForm" inline>
          <el-form-item label="教师姓名">
            <el-input
              v-model="filterForm.teacher_name"
              placeholder="请输入教师姓名"
              clearable
              @input="handleFilterInput"
            />
          </el-form-item>
          <el-form-item label="身份证号">
            <el-input
              v-model="filterForm.id_card"
              placeholder="请输入身份证号"
              clearable
              @input="handleFilterInput"
            />
          </el-form-item>
          <el-form-item label="标签">
            <el-select 
              v-model="filterForm.tag_id" 
              placeholder="请选择标签" 
              clearable
              @change="applyFilter"
              style="width: 200px"
            >
              <el-option 
                v-for="tag in tagList" 
                :key="tag.id" 
                :label="tag.biao_qian" 
                :value="tag.id"
              >
                <el-tag size="small" type="info">{{ tag.biao_qian }}</el-tag>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilter">筛选</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table
        ref="dataTable"
        :data="tableData"
        border
        stripe
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" fixed />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="teacher_name" label="教师姓名" width="120" />
        <el-table-column prop="id_card" label="身份证号" width="180" />
        <el-table-column prop="tag_name" label="标签" width="150" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑教师标签对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <!-- 选择教师（仅在未选择教师时显示） -->
      <el-form-item label="选择教师" v-if="!selectedTeacherId && !isEditing">
        <div class="teacher-search">
          <el-input
            v-model="teacherSearchKeyword"
            placeholder="请输入教师姓名搜索"
            @input="handleTeacherSearch"
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <!-- 搜索结果列表 -->
          <div v-if="teacherList.length > 0" class="teacher-search-results">
            <div
              v-for="teacher in teacherList"
              :key="teacher.id"
              class="teacher-search-item"
              @click="handleSelectTeacher(teacher)"
            >
              {{ teacher.name }} ({{ teacher.id_card }})
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- 显示已选教师信息 -->
      <div v-if="selectedTeacherId && teacherInfo" class="teacher-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="教师姓名">{{ teacherInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ teacherInfo.id_card }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 标签选择（复选框形式） -->
      <div v-if="selectedTeacherId" class="tag-selection">
        <div class="section-title">选择标签</div>
        <el-checkbox-group v-model="selectedTags">
          <el-checkbox
            v-for="tag in tagList"
            :key="tag.id"
            :label="tag.id"
            border
            style="margin-right: 10px; margin-bottom: 10px"
          >
            {{ tag.biao_qian }}
          </el-checkbox>
        </el-checkbox-group>
        <div v-if="tagList.length === 0" class="no-tags">暂无可用标签</div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saveLoading">保存</el-button>
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
          </el-radio-group>
        </el-form-item>

        <el-form-item label="导出范围">
          <el-radio-group v-model="exportForm.scope">
            <el-radio label="all">全部数据</el-radio>
            <el-radio label="current">当前页</el-radio>
            <el-radio label="selected">选中行</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="文件名">
          <el-input
            v-model="exportForm.filename"
            placeholder="标签关系管理_YYYYMMDD"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="executeExport" :loading="exporting">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import CommonActionBar from '@/components/data/CommonActionBar.vue'
import DynamicActionBar from '@/components/data/DynamicActionBar.vue'

const loading = ref(false)
const tableData = ref<any[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedRows = ref<any[]>([])

// 搜索关键词
const searchKeyword = ref('')

// 筛选
const showFilter = ref(false)
const filterForm = ref({
  teacher_name: '',
  id_card: '',
  tag_id: null as number | null
})

// 标签列表
const tagList = ref<any[]>([])

// 对话框
const dialogVisible = ref(false)
const isEditing = ref(false)
const selectedTeacherId = ref<number | null>(null)
const teacherList = ref<any[]>([])
const teacherSearchKeyword = ref('')
const selectedTags = ref<number[]>([])
const saveLoading = ref(false)
const currentRow = ref<any>(null)

// 导出相关
const exportDialogVisible = ref(false)
const exporting = ref(false)
const exportForm = ref({
  format: 'excel',
  scope: 'all',
  filename: ''
})

// 对话框标题
const dialogTitle = computed(() => {
  return isEditing.value ? '编辑教师标签' : '新增教师标签'
})

// 当前选中的教师信息
const teacherInfo = computed(() => {
  if (!selectedTeacherId.value) return null
  return teacherList.value.find(t => t.id === selectedTeacherId.value) || null
})

// 获取标签列表
const fetchTags = async () => {
  try {
    const response = await fetch('/api/data/personal_dict_dictionary?page=1&size=100')
    if (response.ok) {
      const result = await response.json()
      tagList.value = result.data || []
    }
  } catch (error) {
    console.error('获取标签列表失败:', error)
  }
}

// 搜索教师
const searchTeachers = async (query: string) => {
  try {
    const params = new URLSearchParams({ page: '1', size: '50' })
    if (query && query.trim()) {
      params.append('keyword', query.trim())
    }
    const response = await fetch(`/api/data/teacher_basic_info?${params}`)
    if (response.ok) {
      const result = await response.json()
      teacherList.value = result.data || []
    } else {
      teacherList.value = []
    }
  } catch (error) {
    console.error('获取教师列表失败:', error)
    teacherList.value = []
  }
}

// 教师搜索
let searchTimer: number | null = null
const handleTeacherSearch = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = window.setTimeout(async () => {
    await searchTeachers(teacherSearchKeyword.value)
  }, 300)
}

// 选择教师
const handleSelectTeacher = (teacher: any) => {
  selectedTeacherId.value = teacher.id
  teacherList.value = []
  teacherSearchKeyword.value = ''
  fetchTeacherTags(teacher.id)
}

// 获取教师已有标签
const fetchTeacherTags = async (teacherId: number) => {
  try {
    const response = await fetch(`/api/tag-relations/teacher/${teacherId}/tags`)
    if (response.ok) {
      const result = await response.json()
      selectedTags.value = (result.data || []).map((tag: any) => tag.tag_id)
    }
  } catch (error) {
    console.error('获取教师标签失败:', error)
    selectedTags.value = []
  }
}

// 通用按钮事件 - 新增
const handleCreate = () => {
  isEditing.value = false
  selectedTeacherId.value = null
  teacherList.value = []
  selectedTags.value = []
  currentRow.value = null
  dialogVisible.value = true
}

// 编辑（从表格行点击或从选中行）
const handleEdit = (row?: any) => {
  if (row) {
    // 从表格行点击编辑
    isEditing.value = true
    currentRow.value = row
    selectedTeacherId.value = row.employee_id
    teacherList.value = [{
      id: row.employee_id,
      name: row.teacher_name,
      id_card: row.id_card
    }]
    fetchTeacherTags(row.employee_id)
    dialogVisible.value = true
  } else if (selectedRows.value.length === 1) {
    // 从选中行编辑
    const selectedRow = selectedRows.value[0]
    handleEdit(selectedRow)
  } else {
    ElMessage.warning('请选择一条记录')
  }
}

// 删除单行
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条标签关系吗？', '提示', {
      type: 'warning'
    })

    const response = await fetch(`/api/tag-relations/${row.id}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      ElMessage.success('删除成功')
      fetchData()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    // 用户取消
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条记录吗？`,
      '确认删除',
      { type: 'warning' }
    )

    for (const row of selectedRows.value) {
      await fetch(`/api/tag-relations/${row.id}`, {
        method: 'DELETE'
      })
    }

    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 导入
const handleImport = () => {
  // 跳转到导入页面
  window.location.href = '/import/workbench'
}

// 导出
const handleExport = () => {
  exportForm.value.filename = `标签关系管理_${getCurrentDate()}`
  exportDialogVisible.value = true
}

// 获取当前日期
const getCurrentDate = () => {
  const now = new Date()
  return `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`
}

// 执行导出
const executeExport = async () => {
  exporting.value = true

  try {
    let exportData: any[] = []
    const scope = exportForm.value.scope
    
    console.log('导出范围:', scope)
    console.log('当前选中行:', selectedRows.value.length)
    console.log('当前页数据:', tableData.value.length)

    if (scope === 'selected') {
      exportData = selectedRows.value
      console.log('使用选中行数据:', exportData.length)
    } else if (scope === 'current') {
      exportData = tableData.value
      console.log('使用当前页数据:', exportData.length)
    } else if (scope === 'all') {
      // 获取所有数据（分页获取，每页200条）
      console.log('开始获取全部数据...')
      try {
        let page = 1
        const pageSize = 200
        let hasMore = true
        exportData = []
        
        while (hasMore) {
          const response = await fetch(`/api/tag-relations/list?page=${page}&size=${pageSize}`)
          console.log(`获取第${page}页数据响应状态:`, response.status)
          
          if (response.ok) {
            const result = await response.json()
            console.log(`获取第${page}页数据结果:`, result)
            
            if (result.data && Array.isArray(result.data)) {
              exportData = exportData.concat(result.data)
              console.log(`已获取${exportData.length}条数据`)
              
              // 如果返回的数据少于pageSize，说明没有更多数据了
              if (result.data.length < pageSize) {
                hasMore = false
              } else {
                page++
              }
            } else {
              console.error('返回数据格式不正确:', result)
              hasMore = false
            }
          } else {
            const errorText = await response.text()
            console.error('获取全部数据失败:', errorText)
            ElMessage.error('获取数据失败')
            exporting.value = false
            return
          }
        }
        
        console.log('导出数据总条数:', exportData.length)
      } catch (error) {
        console.error('获取全部数据异常:', error)
        ElMessage.error('获取数据异常')
        exporting.value = false
        return
      }
    } else {
      console.error('未知的导出范围:', scope)
      ElMessage.error('未知的导出范围')
      exporting.value = false
      return
    }

    console.log('最终导出数据条数:', exportData.length)

    if (!exportData || exportData.length === 0) {
      ElMessage.warning('没有数据可导出')
      exporting.value = false
      return
    }

    // 调用后端导出API
    const exportResponse = await fetch('/api/data/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: 'tag_relations',
        data: exportData,
        format: exportForm.value.format,
        filename: exportForm.value.filename
      })
    })

    if (exportResponse.ok) {
      const result = await exportResponse.json()
      ElMessage.success(`导出成功`)
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

// 刷新
const handleRefresh = () => {
  fetchData()
  ElMessage.success('刷新成功')
}

// 筛选
const handleFilter = () => {
  showFilter.value = !showFilter.value
}

// 搜索输入防抖
let headerSearchTimer: number | null = null
const handleSearchInput = () => {
  console.log('搜索输入:', searchKeyword.value)
  if (headerSearchTimer) {
    clearTimeout(headerSearchTimer)
  }
  headerSearchTimer = window.setTimeout(() => {
    console.log('执行搜索:', searchKeyword.value)
    currentPage.value = 1
    fetchData()
  }, 500)
}

// 筛选输入防抖
let filterTimer: number | null = null
const handleFilterInput = () => {
  if (filterTimer) {
    clearTimeout(filterTimer)
  }
  filterTimer = window.setTimeout(() => {
    applyFilter()
  }, 500)
}

// 应用筛选
const applyFilter = () => {
  currentPage.value = 1
  fetchData()
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    teacher_name: '',
    id_card: '',
    tag_id: null
  }
  applyFilter()
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
    case 'batchExport':
      handleExport()
      break
    default:
      console.log('未知操作:', action, data)
  }
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 保存标签
const handleSave = async () => {
  if (!selectedTeacherId.value) {
    ElMessage.warning('请选择教师')
    return
  }

  saveLoading.value = true
  try {
    const response = await fetch('/api/tag-relations/save-tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        employee_id: selectedTeacherId.value,
        tag_ids: selectedTags.value
      })
    })

    if (response.ok) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      fetchData()
    } else {
      const result = await response.json()
      ElMessage.error(result.detail || '保存失败')
    }
  } catch (error) {
    console.error('保存标签失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

// 获取关系数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString()
    })

    // 添加搜索关键词
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value)
      console.log('添加搜索关键词:', searchKeyword.value)
    }
    
    console.log('请求URL:', `/api/tag-relations/list?${params}`)

    // 添加筛选条件
    if (filterForm.value.teacher_name) {
      params.append('teacher_name', filterForm.value.teacher_name)
    }
    if (filterForm.value.id_card) {
      params.append('id_card', filterForm.value.id_card)
    }
    if (filterForm.value.tag_id) {
      params.append('tag_id', filterForm.value.tag_id.toString())
    }

    const response = await fetch(`/api/tag-relations/list?${params}`)
    if (response.ok) {
      const result = await response.json()
      tableData.value = result.data || []
      totalCount.value = result.total || 0
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 分页
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchData()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchTags()
  fetchData()
})
</script>

<style scoped>
.tag-relations-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.filter-section {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-top: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.teacher-info {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
}

.tag-selection {
  min-height: 100px;
  padding: 15px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}

.no-tags {
  color: #909399;
  font-size: 14px;
}

.teacher-search {
  position: relative;
}

.teacher-search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #dcdfe6;
  border-top: none;
  border-radius: 0 0 4px 4px;
  z-index: 100;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.teacher-search-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.teacher-search-item:last-child {
  border-bottom: none;
}

.teacher-search-item:hover {
  background-color: #f5f7fa;
}
</style>
