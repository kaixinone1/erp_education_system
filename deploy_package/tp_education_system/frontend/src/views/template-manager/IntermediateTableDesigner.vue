<template>
  <div class="intermediate-table-designer">
    <el-card class="designer-card">
      <template #header>
        <div class="card-header">
          <div class="title-section">
            <el-button link @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <span class="title">{{ isEditing ? '编辑中间表' : '新建中间表' }}</span>
          </div>
          <div class="actions">
            <el-button @click="goBack">取消</el-button>
            <el-button type="primary" @click="saveTable" :loading="saving">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
          </div>
        </div>
      </template>

      <!-- 基本信息 -->
      <div class="section">
        <h3 class="section-title">基本信息</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="表中文名" required>
              <el-input 
                v-model="tableForm.chinese_name" 
                placeholder="如：年度考核数据"
                :disabled="isEditing"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="表英文名" required>
              <el-input 
                v-model="tableForm.table_name" 
                placeholder="如：annual_assessment_data"
                :disabled="isEditing"
              >
                <template #append>_data</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 字段设计 -->
      <div class="section">
        <div class="section-header">
          <h3 class="section-title">字段设计</h3>
          <el-button type="primary" size="small" @click="addField">
            <el-icon><Plus /></el-icon>
            添加字段
          </el-button>
        </div>

        <el-table :data="tableForm.fields" border class="fields-table">
          <el-table-column type="index" width="50" />
          
          <el-table-column label="中文字段名" min-width="150">
            <template #default="{ row, $index }">
              <el-input v-model="row.label" placeholder="如：姓名" />
            </template>
          </el-table-column>
          
          <el-table-column label="英文字段名" min-width="150">
            <template #default="{ row, $index }">
              <el-input v-model="row.name" placeholder="如：name" />
            </template>
          </el-table-column>
          
          <el-table-column label="字段类型" width="150">
            <template #default="{ row, $index }">
              <el-select v-model="row.type" style="width: 100%">
                <el-option label="文本" value="VARCHAR" />
                <el-option label="长文本" value="TEXT" />
                <el-option label="整数" value="INTEGER" />
                <el-option label="小数" value="DECIMAL" />
                <el-option label="日期" value="DATE" />
                <el-option label="布尔" value="BOOLEAN" />
              </el-select>
            </template>
          </el-table-column>
          
          <el-table-column label="长度" width="100">
            <template #default="{ row, $index }">
              <el-input-number 
                v-model="row.length" 
                :min="1" 
                :max="1000"
                style="width: 100%"
                v-if="row.type === 'VARCHAR'"
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="必填" width="80" align="center">
            <template #default="{ row, $index }">
              <el-checkbox v-model="row.required" />
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ $index }">
              <el-button type="danger" size="small" @click="removeField($index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="tableForm.fields.length === 0" description="点击上方按钮添加字段" />
      </div>

      <!-- 预览 -->
      <div class="section" v-if="tableForm.fields.length > 0">
        <h3 class="section-title">预览</h3>
        <el-alert type="info" :closable="false">
          <template #title>
            将创建表：<strong>{{ tableForm.table_name || '未命名' }}</strong>
            （{{ tableForm.fields.length }} 个字段）
          </template>
          <div class="preview-fields">
            <el-tag v-for="field in tableForm.fields" :key="field.name" size="small" class="field-tag">
              {{ field.label }} ({{ field.name }})
            </el-tag>
          </div>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, Delete, Check } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 判断是编辑还是新建
const isEditing = ref(false)
const tableName = ref('')

// 表单数据
const tableForm = reactive({
  chinese_name: '',
  table_name: '',
  fields: [] as Array<{
    name: string
    label: string
    type: string
    length: number
    required: boolean
  }>
})

const saving = ref(false)

// 添加字段
const addField = () => {
  tableForm.fields.push({
    name: '',
    label: '',
    type: 'VARCHAR',
    length: 50,
    required: false
  })
}

// 删除字段
const removeField = (index: number) => {
  tableForm.fields.splice(index, 1)
}

// 返回
const goBack = () => {
  router.push('/template-manager')
}

// 保存表
const saveTable = async () => {
  // 验证
  if (!tableForm.chinese_name.trim()) {
    ElMessage.warning('请输入表中文名')
    return
  }
  if (!tableForm.table_name.trim()) {
    ElMessage.warning('请输入表英文名')
    return
  }
  if (tableForm.fields.length === 0) {
    ElMessage.warning('至少需要添加一个字段')
    return
  }

  // 验证字段
  for (let i = 0; i < tableForm.fields.length; i++) {
    const field = tableForm.fields[i]
    if (!field.label.trim()) {
      ElMessage.warning(`第 ${i + 1} 个字段缺少中文名`)
      return
    }
    if (!field.name.trim()) {
      ElMessage.warning(`第 ${i + 1} 个字段缺少英文名`)
      return
    }
  }

  saving.value = true
  try {
    const response = await fetch('/api/intermediate-tables/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: tableForm.table_name,
        chinese_name: tableForm.chinese_name,
        fields: tableForm.fields
      })
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('中间表创建成功！')
      // 询问是否跳转到数据管理页面
      try {
        await ElMessageBox.confirm(
          `表 "${tableForm.chinese_name}" 创建成功！是否立即管理数据？`,
          '创建成功',
          {
            confirmButtonText: '管理数据',
            cancelButtonText: '返回列表',
            type: 'success'
          }
        )
        // 跳转到数据管理页面
        router.push(`/auto-table/${tableForm.table_name}`)
      } catch {
        // 用户选择返回列表
        router.push('/template-manager')
      }
    } else {
      ElMessage.error(result.message || '创建失败')
    }
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

// 加载现有表结构（编辑模式）
const loadTableSchema = async () => {
  if (!tableName.value) return
  
  try {
    const response = await fetch(`/api/auto-table/${tableName.value}/schema`)
    const result = await response.json()
    if (result.status === 'success') {
      tableForm.chinese_name = result.data.chinese_name
      tableForm.table_name = result.data.table_name
      // 转换字段格式
      tableForm.fields = result.data.fields.map((f: any) => ({
        name: f.name,
        label: f.label || f.name,
        type: f.type,
        length: f.length || 50,
        required: !f.nullable
      }))
    }
  } catch (error) {
    console.error('加载表结构失败:', error)
    ElMessage.error('加载表结构失败')
  }
}

onMounted(() => {
  tableName.value = route.params.tableName as string
  if (tableName.value) {
    isEditing.value = true
    loadTableSchema()
  } else {
    // 新建模式，添加一个默认字段
    addField()
  }
})
</script>

<style scoped>
.intermediate-table-designer {
  padding: 20px;
}

.designer-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.fields-table {
  margin-top: 10px;
}

.preview-fields {
  margin-top: 10px;
}

.field-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
