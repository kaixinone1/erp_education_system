<template>
  <div class="tag-relations-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">标签关系管理</span>
          <el-tag type="success">共 {{ totalCount }} 条关系</el-tag>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="教师姓名">
          <el-input v-model="searchName" placeholder="请输入教师姓名" clearable @input="handleSearch" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="searchIdCard" placeholder="请输入身份证号" clearable @input="handleSearch" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="searchTag" placeholder="请选择标签" clearable @change="handleSearch">
            <el-option v-for="tag in tagList" :key="tag.id" :label="tag.biao_qian" :value="tag.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table 
        :data="tableData" 
        border 
        stripe 
        v-loading="loading"
      >
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

    <!-- 编辑教师标签对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="600px"
    >
      <!-- 选择教师（仅在未选择教师时显示） -->
      <el-form-item label="选择教师" v-if="!selectedTeacherId">
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

    <!-- 快捷操作按钮 -->
    <div class="quick-actions">
      <el-button type="primary" @click="handleManageTags">
        <el-icon><Plus /></el-icon>
        管理教师标签
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref<any[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 搜索条件
const searchName = ref('')
const searchIdCard = ref('')
const searchTag = ref<number | null>(null)

// 标签列表
const tagList = ref<any[]>([])

// 对话框
const dialogVisible = ref(false)
const selectedTeacherId = ref<number | null>(null)
const teacherList = ref<any[]>([])
const teacherLoading = ref(false)
const teacherSearchKeyword = ref('')
const selectedTags = ref<number[]>([])
const saveLoading = ref(false)

// 对话框标题
const dialogTitle = computed(() => {
  return selectedTeacherId.value ? '编辑教师标签' : '管理教师标签'
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
  teacherLoading.value = true
  try {
    // 使用 keyword 参数进行搜索
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
  } finally {
    teacherLoading.value = false
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

// 教师选择变化（保留兼容性）
const handleTeacherChange = async (teacherId: number) => {
  await fetchTeacherTags(teacherId)
}

// 获取教师已有标签
const fetchTeacherTags = async (teacherId: number) => {
  try {
    const response = await fetch(`/api/tag-relations/teacher/${teacherId}/tags`)
    if (response.ok) {
      const result = await response.json()
      // 设置已选中的标签ID
      selectedTags.value = (result.data || []).map((tag: any) => tag.tag_id)
    }
  } catch (error) {
    console.error('获取教师标签失败:', error)
    selectedTags.value = []
  }
}

// 编辑（从表格行点击）
const handleEdit = async (row: any) => {
  selectedTeacherId.value = row.employee_id
  // 设置教师信息
  teacherList.value = [{
    id: row.employee_id,
    name: row.teacher_name,
    id_card: row.id_card
  }]
  await fetchTeacherTags(row.employee_id)
  dialogVisible.value = true
}

// 管理教师标签（从按钮点击）
const handleManageTags = () => {
  selectedTeacherId.value = null
  teacherList.value = []
  selectedTags.value = []
  dialogVisible.value = true
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
    
    if (searchName.value) params.append('teacher_name', searchName.value)
    if (searchIdCard.value) params.append('id_card', searchIdCard.value)
    if (searchTag.value) params.append('tag_id', searchTag.value.toString())
    
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

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchName.value = ''
  searchIdCard.value = ''
  searchTag.value = null
  currentPage.value = 1
  fetchData()
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

// 删除
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
  position: relative;
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

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.quick-actions {
  position: absolute;
  top: 20px;
  right: 20px;
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
