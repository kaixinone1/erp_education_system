<template>
  <div class="table-structure-management">
    <el-card class="box-card" style="height: calc(100vh - 120px);">
      <template #header>
        <div class="card-header">
          <span>表结构管理</span>
          <div class="header-actions">
            <el-select
              v-model="selectedTable"
              placeholder="选择数据表"
              style="width: 250px"
              @change="handleTableChange"
            >
              <el-option
                v-for="table in tableList"
                :key="table.name"
                :label="`${table.chinese_name} (${table.name})`"
                :value="table.name"
              />
            </el-select>
            <el-button type="primary" @click="refreshTableList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="selectedTable" class="table-content">
        <!-- 表基本信息 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="section-header">
              <span>表基本信息</span>
              <el-button type="primary" size="small" @click="showRenameDialog">
                修改表名
              </el-button>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="表名">{{ tableInfo.table_name }}</el-descriptions-item>
            <el-descriptions-item label="中文名称">{{ tableInfo.chinese_name }}</el-descriptions-item>
            <el-descriptions-item label="主键">{{ tableInfo.primary_keys?.join(', ') || '无' }}</el-descriptions-item>
            <el-descriptions-item label="字段数量">{{ tableInfo.columns?.length || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 字段列表 -->
        <el-card class="fields-card" shadow="never" style="margin-top: 20px;">
          <template #header>
            <div class="section-header">
              <span>字段列表</span>
              <el-button type="primary" size="small" @click="showAddFieldDialog">
                <el-icon><Plus /></el-icon>
                添加字段
              </el-button>
            </div>
          </template>

          <el-table
            :data="tableInfo.columns"
            style="width: 100%"
            border
            v-loading="loading"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="字段名" min-width="150" />
            <el-table-column prop="chinese_name" label="中文名称" min-width="150">
              <template #default="{ row }">
                <el-input
                  v-if="row.editing"
                  v-model="row.temp_chinese_name"
                  size="small"
                />
                <span v-else>{{ getFieldChineseName(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="data_type" label="数据类型" width="120" />
            <el-table-column prop="is_nullable" label="可空" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_nullable ? 'success' : 'danger'">
                  {{ row.is_nullable ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="max_length" label="长度" width="100">
              <template #default="{ row }">
                {{ row.max_length || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <template v-if="!isSystemField(row.name)">
                  <el-button
                    v-if="!row.editing"
                    type="primary"
                    size="small"
                    @click="startEdit(row)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    v-if="row.editing"
                    type="success"
                    size="small"
                    @click="saveField(row)"
                  >
                    保存
                  </el-button>
                  <el-button
                    v-if="row.editing"
                    size="small"
                    @click="cancelEdit(row)"
                  >
                    取消
                  </el-button>
                  <el-button
                    v-if="!row.editing"
                    type="danger"
                    size="small"
                    @click="deleteField(row)"
                  >
                    删除
                  </el-button>
                </template>
                <el-tag v-else type="info" size="small">系统字段</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 索引信息 -->
        <el-card class="indexes-card" shadow="never" style="margin-top: 20px;" v-if="tableInfo.indexes?.length">
          <template #header>
            <span>索引信息</span>
          </template>
          <el-table :data="tableInfo.indexes" style="width: 100%" border>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="索引名" min-width="200" />
            <el-table-column prop="definition" label="定义" min-width="400" />
          </el-table>
        </el-card>
      </div>

      <el-empty v-else description="请选择要管理的数据表" />
    </el-card>

    <!-- 添加字段对话框 -->
    <el-dialog
      v-model="addFieldDialogVisible"
      title="添加字段"
      width="500px"
    >
      <el-form :model="newField" label-width="100px">
        <el-form-item label="字段名" required>
          <el-input v-model="newField.name" placeholder="请输入字段名（英文）" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="newField.chinese_name" placeholder="请输入中文名称" />
        </el-form-item>
        <el-form-item label="数据类型" required>
          <el-select v-model="newField.type" style="width: 100%">
            <el-option label="字符串 (VARCHAR)" value="VARCHAR" />
            <el-option label="整数 (INTEGER)" value="INTEGER" />
            <el-option label="小数 (DECIMAL)" value="DECIMAL" />
            <el-option label="日期 (DATE)" value="DATE" />
            <el-option label="日期时间 (DATETIME)" value="DATETIME" />
            <el-option label="布尔值 (BOOLEAN)" value="BOOLEAN" />
            <el-option label="长文本 (TEXT)" value="TEXT" />
          </el-select>
        </el-form-item>
        <el-form-item label="长度" v-if="newField.type === 'VARCHAR'">
          <el-input-number v-model="newField.length" :min="1" :max="4000" />
        </el-form-item>
        <el-form-item label="必填">
          <el-switch v-model="newField.required" />
        </el-form-item>
        <el-form-item label="唯一">
          <el-switch v-model="newField.unique" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addFieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addField">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改表名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="修改表中文名称"
      width="400px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前名称">
          <el-input v-model="tableInfo.chinese_name" disabled />
        </el-form-item>
        <el-form-item label="新名称" required>
          <el-input v-model="newTableName" placeholder="请输入新的中文名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="renameTable">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'

// 状态
const loading = ref(false)
const tableList = ref<any[]>([])
const selectedTable = ref('')
const tableInfo = ref<any>({})
const addFieldDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const newTableName = ref('')

// 新字段表单
const newField = ref({
  name: '',
  chinese_name: '',
  type: 'VARCHAR',
  length: 255,
  required: false,
  unique: false
})

// 系统字段列表
const systemFields = ['id', 'created_at', 'updated_at', 'import_batch', 'code', 'teacher_id']

// 获取表列表
const refreshTableList = async () => {
  try {
    const response = await fetch('/api/table-structure/tables')
    if (response.ok) {
      const result = await response.json()
      tableList.value = result.tables || []
    }
  } catch (error) {
    console.error('获取表列表失败:', error)
    ElMessage.error('获取表列表失败')
  }
}

// 获取表结构
const handleTableChange = async () => {
  if (!selectedTable.value) return
  
  loading.value = true
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}`)
    if (response.ok) {
      const result = await response.json()
      // 为每个字段添加编辑状态
      result.columns = result.columns.map((col: any) => ({
        ...col,
        editing: false,
        temp_chinese_name: ''
      }))
      tableInfo.value = result
    }
  } catch (error) {
    console.error('获取表结构失败:', error)
    ElMessage.error('获取表结构失败')
  } finally {
    loading.value = false
  }
}

// 获取字段中文名称
const getFieldChineseName = (row: any) => {
  const config = tableInfo.value.config?.fields || []
  const fieldConfig = config.find((f: any) => f.name === row.name)
  return fieldConfig?.chinese_name || row.name
}

// 判断是否为系统字段
const isSystemField = (fieldName: string) => {
  return systemFields.includes(fieldName.toLowerCase())
}

// 开始编辑
const startEdit = (row: any) => {
  row.temp_chinese_name = getFieldChineseName(row)
  row.editing = true
}

// 取消编辑
const cancelEdit = (row: any) => {
  row.editing = false
  row.temp_chinese_name = ''
}

// 保存字段
const saveField = async (row: any) => {
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field/${row.name}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: row.temp_chinese_name
      })
    })
    
    if (response.ok) {
      ElMessage.success('字段更新成功')
      row.editing = false
      handleTableChange() // 刷新数据
    } else {
      const error = await response.text()
      ElMessage.error(`更新失败: ${error}`)
    }
  } catch (error) {
    console.error('保存字段失败:', error)
    ElMessage.error('保存字段失败')
  }
}

// 删除字段
const deleteField = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除字段 "${row.name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field/${row.name}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('字段删除成功')
      handleTableChange() // 刷新数据
    } else {
      const error = await response.text()
      ElMessage.error(`删除失败: ${error}`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除字段失败:', error)
      ElMessage.error('删除字段失败')
    }
  }
}

// 显示添加字段对话框
const showAddFieldDialog = () => {
  newField.value = {
    name: '',
    chinese_name: '',
    type: 'VARCHAR',
    length: 255,
    required: false,
    unique: false
  }
  addFieldDialogVisible.value = true
}

// 添加字段
const addField = async () => {
  if (!newField.value.name) {
    ElMessage.warning('请输入字段名')
    return
  }
  
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newField.value)
    })
    
    if (response.ok) {
      ElMessage.success('字段添加成功')
      addFieldDialogVisible.value = false
      handleTableChange() // 刷新数据
    } else {
      const error = await response.text()
      ElMessage.error(`添加失败: ${error}`)
    }
  } catch (error) {
    console.error('添加字段失败:', error)
    ElMessage.error('添加字段失败')
  }
}

// 显示重命名对话框
const showRenameDialog = () => {
  newTableName.value = tableInfo.value.chinese_name
  renameDialogVisible.value = true
}

// 修改表名
const renameTable = async () => {
  if (!newTableName.value) {
    ElMessage.warning('请输入新的表名')
    return
  }
  
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/rename`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chinese_name: newTableName.value })
    })
    
    if (response.ok) {
      ElMessage.success('表名修改成功')
      renameDialogVisible.value = false
      handleTableChange() // 刷新数据
      refreshTableList() // 刷新表列表
    } else {
      const error = await response.text()
      ElMessage.error(`修改失败: ${error}`)
    }
  } catch (error) {
    console.error('修改表名失败:', error)
    ElMessage.error('修改表名失败')
  }
}

// 初始化
onMounted(() => {
  refreshTableList()
})
</script>

<style scoped>
.table-structure-management {
  padding: 20px;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-card,
.fields-card,
.indexes-card {
  margin-bottom: 0;
}
</style>
