<template>
  <div class="standards-container">
    <el-card class="standards-card">
      <template #header>
        <div class="card-header">
          <span>绩效工资标准管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>新增标准
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 绩效工资标准 -->
        <el-tab-pane label="绩效工资标准" name="performance">
          <el-table :data="performanceStandards" v-loading="loading" border stripe>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="level_name" label="岗位等级" min-width="150" />
            <el-table-column prop="level_code" label="等级代码" width="100" />
            <el-table-column prop="performance_pay" label="绩效工资" width="120" align="right">
              <template #default="{ row }">
                {{ formatMoney(row.performance_pay) }}
              </template>
            </el-table-column>
            <el-table-column prop="effective_date" label="生效日期" width="120" />
            <el-table-column prop="remarks" label="备注" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-space>
                  <el-button type="primary" size="small" @click="editStandard(row)">编辑</el-button>
                  <el-button type="danger" size="small" @click="deleteStandard(row)">删除</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 乡镇补贴标准 -->
        <el-tab-pane label="乡镇补贴标准" name="town">
          <el-table :data="townSubsidyStandards" v-loading="loading" border stripe>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="town_name" label="乡镇名称" min-width="150" />
            <el-table-column prop="subsidy_amount" label="补贴金额" width="120" align="right">
              <template #default="{ row }">
                {{ formatMoney(row.subsidy_amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="effective_date" label="生效日期" width="120" />
            <el-table-column prop="remarks" label="备注" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-space>
                  <el-button type="primary" size="small" @click="editTownStandard(row)">编辑</el-button>
                  <el-button type="danger" size="small" @click="deleteTownStandard(row)">删除</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新增/编辑绩效工资标准对话框 -->
    <el-dialog
      v-model="performanceDialogVisible"
      :title="isEdit ? '编辑绩效工资标准' : '新增绩效工资标准'"
      width="500px"
    >
      <el-form :model="performanceForm" label-width="100px" :rules="performanceRules" ref="performanceFormRef">
        <el-form-item label="岗位等级" prop="level_name">
          <el-select v-model="performanceForm.level_name" placeholder="选择岗位等级" style="width: 100%">
            <el-option label="九级管理" value="九级管理" />
            <el-option label="八级管理" value="八级管理" />
            <el-option label="七级管理" value="七级管理" />
            <el-option label="六级管理" value="六级管理" />
            <el-option label="正高级教师" value="正高级教师" />
            <el-option label="高级教师" value="高级教师" />
            <el-option label="一级教师" value="一级教师" />
            <el-option label="二级教师" value="二级教师" />
            <el-option label="三级教师" value="三级教师" />
            <el-option label="高级工" value="高级工" />
            <el-option label="中级工" value="中级工" />
            <el-option label="初级工" value="初级工" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级代码" prop="level_code">
          <el-input v-model="performanceForm.level_code" placeholder="如：9GL、GJJS" />
        </el-form-item>
        <el-form-item label="绩效工资" prop="performance_pay">
          <el-input-number v-model="performanceForm.performance_pay" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生效日期" prop="effective_date">
          <el-date-picker v-model="performanceForm.effective_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="performanceForm.remarks" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="performanceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePerformanceStandard">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑乡镇补贴标准对话框 -->
    <el-dialog
      v-model="townDialogVisible"
      :title="isEdit ? '编辑乡镇补贴标准' : '新增乡镇补贴标准'"
      width="500px"
    >
      <el-form :model="townForm" label-width="100px" :rules="townRules" ref="townFormRef">
        <el-form-item label="乡镇名称" prop="town_name">
          <el-input v-model="townForm.town_name" placeholder="输入乡镇名称" />
        </el-form-item>
        <el-form-item label="补贴金额" prop="subsidy_amount">
          <el-input-number v-model="townForm.subsidy_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生效日期" prop="effective_date">
          <el-date-picker v-model="townForm.effective_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="townForm.remarks" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="townDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTownStandard">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('performance')
const loading = ref(false)
const isEdit = ref(false)

// 绩效工资标准
const performanceStandards = ref([])
const performanceDialogVisible = ref(false)
const performanceFormRef = ref()
const performanceForm = ref({
  id: null,
  level_name: '',
  level_code: '',
  performance_pay: 0,
  effective_date: '',
  remarks: ''
})

const performanceRules = {
  level_name: [{ required: true, message: '请选择岗位等级', trigger: 'change' }],
  performance_pay: [{ required: true, message: '请输入绩效工资', trigger: 'blur' }]
}

// 乡镇补贴标准
const townSubsidyStandards = ref([])
const townDialogVisible = ref(false)
const townFormRef = ref()
const townForm = ref({
  id: null,
  town_name: '',
  subsidy_amount: 0,
  effective_date: '',
  remarks: ''
})

const townRules = {
  town_name: [{ required: true, message: '请输入乡镇名称', trigger: 'blur' }],
  subsidy_amount: [{ required: true, message: '请输入补贴金额', trigger: 'blur' }]
}

// 格式化金额
const formatMoney = (value: number) => {
  if (value === null || value === undefined) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 加载绩效工资标准
const loadPerformanceStandards = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/performance-pay/standards/performance')
    const result = await response.json()
    if (result.status === 'success') {
      performanceStandards.value = result.data
    } else {
      ElMessage.error(result.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载绩效工资标准失败:', error)
    ElMessage.error('加载绩效工资标准失败')
  } finally {
    loading.value = false
  }
}

// 加载乡镇补贴标准
const loadTownSubsidyStandards = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/performance-pay/standards/town')
    const result = await response.json()
    if (result.status === 'success') {
      townSubsidyStandards.value = result.data
    } else {
      ElMessage.error(result.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载乡镇补贴标准失败:', error)
    ElMessage.error('加载乡镇补贴标准失败')
  } finally {
    loading.value = false
  }
}

// 显示新增对话框
const showAddDialog = () => {
  isEdit.value = false
  if (activeTab.value === 'performance') {
    performanceForm.value = {
      id: null,
      level_name: '',
      level_code: '',
      performance_pay: 0,
      effective_date: '',
      remarks: ''
    }
    performanceDialogVisible.value = true
  } else {
    townForm.value = {
      id: null,
      town_name: '',
      subsidy_amount: 0,
      effective_date: '',
      remarks: ''
    }
    townDialogVisible.value = true
  }
}

// 编辑绩效工资标准
const editStandard = (row: any) => {
  isEdit.value = true
  performanceForm.value = { ...row }
  performanceDialogVisible.value = true
}

// 编辑乡镇补贴标准
const editTownStandard = (row: any) => {
  isEdit.value = true
  townForm.value = { ...row }
  townDialogVisible.value = true
}

// 保存绩效工资标准
const savePerformanceStandard = async () => {
  const valid = await performanceFormRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    const url = isEdit.value
      ? `/api/performance-pay/standards/performance/${performanceForm.value.id}`
      : '/api/performance-pay/standards/performance'
    const method = isEdit.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(performanceForm.value)
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      performanceDialogVisible.value = false
      loadPerformanceStandards()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 保存乡镇补贴标准
const saveTownStandard = async () => {
  const valid = await townFormRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    const url = isEdit.value
      ? `/api/performance-pay/standards/town/${townForm.value.id}`
      : '/api/performance-pay/standards/town'
    const method = isEdit.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(townForm.value)
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      townDialogVisible.value = false
      loadTownSubsidyStandards()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 删除绩效工资标准
const deleteStandard = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该标准吗？', '提示', { type: 'warning' })
    const response = await fetch(`/api/performance-pay/standards/performance/${row.id}`, {
      method: 'DELETE'
    })
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadPerformanceStandards()
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

// 删除乡镇补贴标准
const deleteTownStandard = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该标准吗？', '提示', { type: 'warning' })
    const response = await fetch(`/api/performance-pay/standards/town/${row.id}`, {
      method: 'DELETE'
    })
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadTownSubsidyStandards()
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

onMounted(() => {
  loadPerformanceStandards()
  loadTownSubsidyStandards()
})
</script>

<style scoped>
.standards-container {
  padding: 20px;
}

.standards-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
