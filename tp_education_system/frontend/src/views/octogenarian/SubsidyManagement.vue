<template>
  <div class="subsidy-management">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span class="title">高龄老人补贴信息管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索姓名或身份证号"
              style="width: 250px; margin-right: 10px;"
              clearable
              @clear="handleSearch"
              @input="handleSearch"
            >
              <template #append>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              手动添加
            </el-button>
            <el-button type="success" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入数据
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        :row-class-name="tableRowClassName"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="姓名" label="姓名" width="100" />
        <el-table-column prop="性别" label="性别" width="60" align="center" />
        <el-table-column prop="身份证号码" label="身份证号码" width="180" />
        <el-table-column prop="退休单位" label="退休单位" min-width="150" show-overflow-tooltip />
        <el-table-column prop="户籍地" label="户籍地" min-width="150" show-overflow-tooltip />
        <el-table-column prop="现住址" label="现住址" min-width="150" show-overflow-tooltip />
        <el-table-column prop="本人联系电话" label="联系电话" width="120" />
        <el-table-column prop="代理人姓名" label="代理人" width="100" />
        <el-table-column prop="状态" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.状态 === '健在' ? 'success' : 'danger'">{{ row.状态 }}</el-tag>
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

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 编辑/添加对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        class="subsidy-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="序号" prop="序号">
              <el-input v-model.number="formData.序号" type="number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="姓名">
              <el-input v-model="formData.姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="性别">
              <el-select v-model="formData.性别" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号码" prop="身份证号码">
              <el-input v-model="formData.身份证号码" :disabled="isEdit" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="退休单位" prop="退休单位">
              <el-input v-model="formData.退休单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="状态">
              <el-select
                v-model="formData.状态"
                style="width: 100%"
                @change="handleStatusChange"
              >
                <el-option label="健在" value="健在" />
                <el-option label="死亡" value="死亡" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="户籍地" prop="户籍地">
          <el-input v-model="formData.户籍地" placeholder="详细到村社区" />
        </el-form-item>

        <el-form-item label="现住址" prop="现住址">
          <el-input v-model="formData.现住址" placeholder="详细到村社区" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="银行账号" prop="银行账号">
              <el-input v-model="formData.银行账号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开户行" prop="开户行">
              <el-input v-model="formData.开户行" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="本人联系电话" prop="本人联系电话">
              <el-input v-model="formData.本人联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="代理人姓名" prop="代理人姓名">
              <el-input v-model="formData.代理人姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="与本人关系" prop="与本人关系">
              <el-input v-model="formData.与本人关系" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="代理人联系电话" prop="代理人联系电话">
              <el-input v-model="formData.代理人联系电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="备注">
          <el-input v-model="formData.备注" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 死亡登记对话框 -->
    <el-dialog
      v-model="deathDialogVisible"
      title="死亡登记"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="deathFormRef"
        :model="deathFormData"
        :rules="deathFormRules"
        label-width="100px"
      >
        <el-form-item label="姓名">
          <el-input v-model="deathFormData.姓名" disabled />
        </el-form-item>
        <el-form-item label="身份证号码">
          <el-input v-model="deathFormData.身份证号码" disabled />
        </el-form-item>
        <el-form-item label="死亡日期" prop="死亡日期">
          <el-date-picker
            v-model="deathFormData.死亡日期"
            type="date"
            placeholder="选择死亡日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="死亡原因" prop="死亡原因">
          <el-input v-model="deathFormData.死亡原因" placeholder="可选" />
        </el-form-item>
        <el-form-item label="备注" prop="备注">
          <el-input v-model="deathFormData.备注" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="deathDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="deathSubmitting" @click="handleDeathSubmit">
          确认登记死亡
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Upload } from '@element-plus/icons-vue'

// 表格数据
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()
const currentId = ref<number | null>(null)

// 死亡登记对话框
const deathDialogVisible = ref(false)
const deathSubmitting = ref(false)
const deathFormRef = ref()

// 表单数据
const formData = reactive({
  序号: null as number | null,
  姓名: '',
  性别: '',
  身份证号码: '',
  退休单位: '',
  户籍地: '',
  现住址: '',
  银行账号: '',
  开户行: '',
  本人联系电话: '',
  代理人姓名: '',
  与本人关系: '',
  代理人联系电话: '',
  备注: '',
  状态: '健在'
})

// 死亡登记表单
const deathFormData = reactive({
  id: null as number | null,
  姓名: '',
  身份证号码: '',
  死亡日期: '',
  死亡原因: '',
  备注: '',
  登记人: '系统'
})

// 表单验证规则
const formRules = {
  姓名: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  身份证号码: [
    { required: true, message: '请输入身份证号码', trigger: 'blur' },
    { pattern: /^\d{17}[\dXx]$/, message: '身份证号码格式不正确', trigger: 'blur' }
  ],
  性别: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

const deathFormRules = {
  死亡日期: [{ required: true, message: '请选择死亡日期', trigger: 'change' }]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString()
    })
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value)
    }

    const response = await fetch(`/api/octogenarian/subsidies?${params}`)
    const result = await response.json()

    if (result.status === 'success') {
      tableData.value = result.data
      total.value = result.total
    } else {
      ElMessage.error(result.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 添加
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '添加高龄老人补贴信息'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑高龄老人补贴信息'
  currentId.value = row.id

  // 填充表单
  Object.keys(formData).forEach(key => {
    if (row[key] !== undefined) {
      (formData as any)[key] = row[key]
    }
  })

  dialogVisible.value = true
}

// 状态改变处理
const handleStatusChange = (val: string) => {
  if (val === '死亡' && isEdit.value && currentId.value) {
    // 如果状态改为死亡，显示死亡登记对话框
    const row = tableData.value.find((item: any) => item.id === currentId.value)
    if (row) {
      deathFormData.id = row.id
      deathFormData.姓名 = row.姓名
      deathFormData.身份证号码 = row.身份证号码
      deathDialogVisible.value = true
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    submitting.value = true
    try {
      const url = isEdit.value
        ? `/api/octogenarian/subsidies/${currentId.value}`
        : '/api/octogenarian/subsidies'
      const method = isEdit.value ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const result = await response.json()

      if (result.status === 'success') {
        ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
        dialogVisible.value = false
        loadData()
      } else {
        ElMessage.error(result.detail || result.message || '操作失败')
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    } finally {
      submitting.value = false
    }
  })
}

// 死亡登记提交
const handleDeathSubmit = async () => {
  if (!deathFormRef.value) return

  await deathFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    deathSubmitting.value = true
    try {
      const response = await fetch(`/api/octogenarian/subsidies/${deathFormData.id}/register-death`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          死亡日期: deathFormData.死亡日期,
          死亡原因: deathFormData.死亡原因,
          备注: deathFormData.备注,
          登记人: deathFormData.登记人
        })
      })

      const result = await response.json()

      if (result.status === 'success') {
        ElMessage.success('死亡登记成功')
        deathDialogVisible.value = false
        dialogVisible.value = false
        loadData()
      } else {
        ElMessage.error(result.detail || result.message || '登记失败')
      }
    } catch (error) {
      console.error('死亡登记失败:', error)
      ElMessage.error('死亡登记失败')
    } finally {
      deathSubmitting.value = false
    }
  })
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除"${row.姓名}"的补贴信息吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await fetch(`/api/octogenarian/subsidies/${row.id}`, {
      method: 'DELETE'
    })

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 导入
const handleImport = () => {
  // 跳转到数据导入工作台
  window.location.href = '/import/data-import'
}

// 重置表单
const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key === '序号') {
      (formData as any)[key] = null
    } else if (key === '状态') {
      (formData as any)[key] = '健在'
    } else {
      (formData as any)[key] = ''
    }
  })
  currentId.value = null
}

// 表格行样式
const tableRowClassName = ({ row }: { row: any }) => {
  return row.状态 === '死亡' ? 'death-row' : ''
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.subsidy-management {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.subsidy-form {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

:deep(.death-row) {
  background-color: #f5f7fa;
  color: #909399;
}
</style>
