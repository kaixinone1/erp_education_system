<template>
  <div class="checklist-template-container">
    <div class="header">
      <h2>清单模板管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增清单模板
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="清单名称" label="清单名称" min-width="150" />
      <el-table-column label="触发条件" min-width="150">
        <template #default="{ row }">
          <span v-if="row.触发条件 && row.触发条件.target_status">
            状态: {{ row.触发条件.target_status.join(', ') }}
          </span>
          <span v-else class="text-gray">未设置</span>
        </template>
      </el-table-column>
      <el-table-column label="任务项" min-width="250">
        <template #default="{ row }">
          <div v-if="row.任务项列表 && row.任务项列表.length > 0" class="task-list">
            <div v-for="(item, idx) in row.任务项列表.slice(0, 3)" :key="idx" class="task-item-preview">
              <span class="task-num">{{ item.序号 }}.</span>
              <span class="task-title">{{ item.标题 }}</span>
              <span class="task-target" v-if="item.目标">({{ getTargetDisplayName(item.目标) }})</span>
            </div>
            <div v-if="row.任务项列表.length > 3" class="more-tasks">
              + 还有 {{ row.任务项列表.length - 3 }} 项...
            </div>
          </div>
          <span v-else class="text-gray">暂无任务</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.是否有效 ? 'success' : 'danger'">
            {{ row.是否有效 ? '有效' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑清单模板' : '新增清单模板'"
      width="800px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="清单名称" prop="清单名称">
          <el-input v-model="form.清单名称" placeholder="请输入清单名称" />
        </el-form-item>

        <el-form-item label="触发条件" prop="触发条件">
          <div class="trigger-condition">
            <span>当教师任职状态变更为：</span>
            <el-select
              v-model="form.触发条件.target_status"
              multiple
              placeholder="选择触发状态"
              style="width: 300px"
            >
              <el-option
                v-for="opt in employmentStatusOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
            <span style="margin-left: 10px; color: #909399; font-size: 12px">（根据教师基础信息表中任职状态字段）</span>
          </div>
        </el-form-item>

        <el-form-item label="任务项列表" prop="任务项列表">
          <div class="task-items">
            <div v-for="(item, index) in form.任务项列表" :key="index" class="task-item">
              <el-card shadow="never">
                <template #header>
                  <div class="task-header">
                    <span>任务项 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" text @click="removeTaskItem(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item label="标题">
                  <el-input v-model="item.标题" placeholder="任务标题" />
                </el-form-item>
                <el-form-item label="类型">
                  <el-select v-model="item.类型" placeholder="选择类型">
                    <el-option label="内部表" value="内部表" />
                    <el-option label="外部链接" value="外部链接" />
                    <el-option label="自动汇总" value="自动汇总" />
                    <el-option label="签发证件" value="签发证件" />
                  </el-select>
                </el-form-item>
                <el-form-item label="目标">
                  <el-select 
                    v-model="item.目标" 
                    placeholder="选择目标"
                    filterable
                    allow-create
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option
                      v-for="opt in targetOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    >
                      <span>{{ opt.label }}</span>
                      <span style="float: right; color: #8492a6; font-size: 12px">{{ opt.type }}</span>
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="说明">
                  <el-input v-model="item.参数.说明" type="textarea" rows="2" placeholder="任务说明" />
                </el-form-item>
                <el-form-item v-if="item.类型 === '内部表'" label="关联模板">
                  <el-select v-model="item.参数.template_id" placeholder="选择模板" clearable>
                    <el-option-group label="通用模板">
                      <el-option
                        v-for="tpl in universalTemplateList"
                        :key="tpl.template_id"
                        :label="tpl.template_name"
                        :value="tpl.template_id"
                      />
                    </el-option-group>
                    <el-option-group label="旧模板">
                      <el-option
                        v-for="tpl in templateList"
                        :key="tpl.template_id"
                        :label="tpl.template_id"
                        :value="tpl.template_id"
                      />
                    </el-option-group>
                  </el-select>
                </el-form-item>
              </el-card>
            </div>
            <el-button type="primary" text @click="addTaskItem">+ 添加任务项</el-button>
          </div>
        </el-form-item>

        <el-form-item label="是否有效">
          <el-switch v-model="form.是否有效" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const API_BASE = '/api/checklist-template'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const templateList = ref<any[]>([])
const universalTemplateList = ref<any[]>([])
const targetOptions = ref<any[]>([])
const employmentStatusOptions = ref<any[]>([])

const form = ref({
  id: null,
  清单名称: '',
  触发条件: { target_status: [] as string[] },
  任务项列表: [] as any[],
  是否有效: true,
  关联模板ID: null
})

const rules = {
  清单名称: [{ required: true, message: '请输入清单名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/list`)
    const result = await res.json()
    if (result.status === 'success') {
      tableData.value = result.data
    }
  } catch (e: any) {
    ElMessage.error('加载数据失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    // 加载旧模板
    const res = await fetch('/api/document-templates/list')
    const result = await res.json()
    if (result.status === 'success') {
      templateList.value = result.data || []
    }
    
    // 加载通用模板
    const res2 = await fetch('/api/universal-templates/list')
    const result2 = await res2.json()
    if (result2.status === 'success') {
      universalTemplateList.value = result2.data || []
    }
  } catch (e) {
    console.error('加载模板列表失败', e)
  }
}

const loadTargetOptions = async () => {
  try {
    const res = await fetch('/api/checklist-template/target-options')
    const result = await res.json()
    if (result.status === 'success') {
      targetOptions.value = result.data || []
    }
  } catch (e) {
    console.error('加载目标选项失败', e)
  }
}

const loadEmploymentStatusOptions = async () => {
  try {
    const res = await fetch('/api/checklist-template/employment-status-options')
    const result = await res.json()
    if (result.status === 'success') {
      employmentStatusOptions.value = result.data || []
    }
  } catch (e) {
    console.error('加载任职状态选项失败', e)
  }
}

const getTargetDisplayName = (target: string) => {
  if (!target) return ''
  // 如果是网址，直接显示
  if (target.startsWith('http://') || target.startsWith('https://')) {
    return target
  }
  // 从选项中查找
  const found = targetOptions.value.find(opt => opt.value === target)
  return found ? found.label : target
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null,
    清单名称: '',
    触发条件: { target_status: [] },
    任务项列表: [],
    是否有效: true,
    关联模板ID: null
  }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    清单名称: row.清单名称,
    触发条件: row.触发条件 || { target_status: [] },
    任务项列表: row.任务项列表 || [],
    是否有效: row.是否有效,
    关联模板ID: row.关联模板ID
  }
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除清单模板 "${row.清单名称}" 吗？`, '提示', {
      type: 'warning'
    })
    await fetch(`${API_BASE}/${row.id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + e.message)
    }
  }
}

const addTaskItem = () => {
  form.value.任务项列表.push({
    序号: form.value.任务项列表.length + 1,
    标题: '',
    类型: '内部表',
    目标: '',
    参数: {
      说明: '',
      template_id: ''
    },
    完成状态: false
  })
}

const removeTaskItem = (index: number) => {
  form.value.任务项列表.splice(index, 1)
  form.value.任务项列表.forEach((item, i) => {
    item.序号 = i + 1
  })
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true
  try {
    const data = { ...form.value }
    let result
    if (isEdit.value) {
      const res = await fetch(`${API_BASE}/${data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      result = await res.json()
      ElMessage.success('更新成功')
    } else {
      const res = await fetch(`${API_BASE}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      result = await res.json()
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + e.message)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
  loadTemplates()
  loadTargetOptions()
  loadEmploymentStatusOptions()
})
</script>

<style scoped>
.checklist-template-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.trigger-condition {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  margin-bottom: 10px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-gray {
  color: #999;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-item-preview {
  font-size: 12px;
  line-height: 1.4;
}

.task-num {
  color: #409eff;
  font-weight: bold;
  margin-right: 4px;
}

.task-title {
  color: #303133;
}

.task-target {
  color: #909399;
  font-size: 11px;
  margin-left: 4px;
}

.more-tasks {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
</style>
