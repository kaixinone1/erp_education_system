<template>
  <div class="filter-condition-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>过滤条件模板管理</span>
          <el-button type="primary" @click="showAddDialog">新增过滤条件</el-button>
        </div>
      </template>

      <!-- 按类别分组显示 -->
      <div v-for="category in categories" :key="category" class="category-section">
        <h3>{{ category }}</h3>
        <el-table :data="groupedConditions[category]" border style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="field_name" label="字段名" width="120" />
          <el-table-column prop="field_value" label="字段值" width="120" />
          <el-table-column prop="filter_condition" label="过滤条件" min-width="200" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="editCondition(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="deleteCondition(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑过滤条件' : '新增过滤条件'"
      width="500px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="类别">
          <el-select v-model="form.category" placeholder="选择类别" style="width: 100%">
            <el-option label="行政管理人员" value="行政管理人员" />
            <el-option label="专业技术人员" value="专业技术人员" />
            <el-option label="工人" value="工人" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="如：副处级" />
        </el-form-item>
        <el-form-item label="字段名">
          <el-select v-model="form.field_name" placeholder="选择字段名" style="width: 100%">
            <el-option label="行政级别" value="行政级别" />
            <el-option label="职称" value="职称" />
            <el-option label="技术等级" value="技术等级" />
          </el-select>
        </el-form-item>
        <el-form-item label="字段值">
          <el-input v-model="form.field_value" placeholder="如：副处级" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCondition">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_BASE = '/api/filter-conditions'

const conditions = ref<any[]>([])
const categories = ref<string[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null as number | null,
  category: '',
  name: '',
  field_name: '',
  field_value: '',
  filter_condition: '',
  sort_order: 0
})

// 按类别分组
const groupedConditions = computed(() => {
  const grouped: Record<string, any[]> = {}
  conditions.value.forEach(item => {
    if (!grouped[item.category]) {
      grouped[item.category] = []
    }
    grouped[item.category].push(item)
  })
  return grouped
})

const loadConditions = async () => {
  try {
    const res = await fetch(`${API_BASE}/list`)
    const result = await res.json()
    if (result.status === 'success') {
      conditions.value = result.data
      // 提取类别
      const cats = new Set(result.data.map((item: any) => item.category))
      categories.value = Array.from(cats)
    }
  } catch (e) {
    console.error('加载过滤条件失败', e)
    ElMessage.error('加载失败')
  }
}

const showAddDialog = () => {
  isEdit.value = false
  form.value = {
    id: null,
    category: '',
    name: '',
    field_name: '',
    field_value: '',
    filter_condition: '',
    sort_order: 0
  }
  dialogVisible.value = true
}

const editCondition = (row: any) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const saveCondition = async () => {
  // 自动生成过滤条件
  form.value.filter_condition = `${form.value.field_name}='${form.value.field_value}'`
  
  try {
    const url = isEdit.value ? `${API_BASE}/${form.value.id}` : API_BASE
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    const result = await res.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      loadConditions()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (e) {
    console.error('保存失败', e)
    ElMessage.error('保存失败')
  }
}

const deleteCondition = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除该过滤条件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await fetch(`${API_BASE}/${row.id}`, { method: 'DELETE' })
    const result = await res.json()
    
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadConditions()
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败', e)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(loadConditions)
</script>

<style scoped>
.filter-condition-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-section {
  margin-bottom: 30px;
}

.category-section h3 {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
  color: #303133;
}
</style>
