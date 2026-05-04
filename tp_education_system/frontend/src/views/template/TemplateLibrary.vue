<template>
  <div class="template-library">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模板库</span>
          <el-input
            v-model="searchText"
            placeholder="搜索模板"
            style="width: 300px;"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <!-- 分类筛选 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="4">
          <el-checkbox v-model="categories.personnel">人事管理</el-checkbox>
        </el-col>
        <el-col :span="4">
          <el-checkbox v-model="categories.performance">绩效管理</el-checkbox>
        </el-col>
        <el-col :span="4">
          <el-checkbox v-model="categories.retirement">退休管理</el-checkbox>
        </el-col>
        <el-col :span="4">
          <el-checkbox v-model="categories.party">党建管理</el-checkbox>
        </el-col>
      </el-row>

      <!-- 模板列表 -->
      <el-row :gutter="20">
        <el-col
          v-for="template in filteredTemplates"
          :key="template.template_id"
          :span="6"
          style="margin-bottom: 20px;"
        >
          <el-card shadow="hover" @click="previewTemplate(template)">
            <div class="template-card">
              <el-icon :size="40" style="margin-bottom: 10px;">
                <Document />
              </el-icon>
              <div class="template-name">{{ template.chinese_name }}</div>
              <div class="template-info">
                <el-tag size="small">{{ template.category || '未分类' }}</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty v-if="filteredTemplates.length === 0" description="暂无模板" />
    </el-card>

    <!-- 模板预览对话框 -->
    <el-dialog v-model="previewDialogVisible" :title="currentTemplate?.chinese_name" width="80%">
      <div v-if="currentTemplate">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="模板ID">{{ currentTemplate.template_id }}</el-descriptions-item>
          <el-descriptions-item label="中文名称">{{ currentTemplate.chinese_name }}</el-descriptions-item>
          <el-descriptions-item label="英文名称">{{ currentTemplate.english_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTemplate.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ currentTemplate.updated_at }}</el-descriptions-item>
          <el-descriptions-item label="字段数量">{{ currentTemplate.fields?.length || 0 }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>字段列表</el-divider>

        <el-table :data="currentTemplate.fields" border>
          <el-table-column prop="chinese_name" label="中文名称" width="150" />
          <el-table-column prop="english_name" label="英文名称" width="150" />
          <el-table-column prop="data_type" label="数据类型" width="100" />
          <el-table-column prop="required" label="是否必填" width="100">
            <template #default="{ row }">
              <el-tag :type="row.required ? 'danger' : 'info'">
                {{ row.required ? '必填' : '选填' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="useTemplate">使用模板</el-button>
        <el-button type="warning" @click="editTemplate">编辑模板</el-button>
        <el-button type="danger" @click="deleteTemplate">删除模板</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchText = ref('')
const categories = reactive({
  personnel: true,
  performance: true,
  retirement: true,
  party: true
})

const templates = ref([])
const previewDialogVisible = ref(false)
const currentTemplate = ref(null)

const filteredTemplates = computed(() => {
  let result = templates.value
  
  // 搜索过滤
  if (searchText.value) {
    result = result.filter(t => 
      t.chinese_name.includes(searchText.value) ||
      t.english_name.includes(searchText.value)
    )
  }
  
  // 分类过滤（暂时显示所有）
  // TODO: 根据模板的category字段过滤
  
  return result
})

const loadTemplates = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/template/list')
    
    if (response.data.success) {
      templates.value = response.data.templates
    }
  } catch (error) {
    ElMessage.error('加载模板列表失败：' + error.message)
  }
}

const previewTemplate = (template) => {
  currentTemplate.value = template
  previewDialogVisible.value = true
}

const useTemplate = () => {
  ElMessage.success('模板调用功能开发中...')
  previewDialogVisible.value = false
}

const editTemplate = () => {
  router.push({
    path: '/report/template-center/design',
    query: { template_id: currentTemplate.value.template_id }
  })
  previewDialogVisible.value = false
}

const deleteTemplate = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await axios.delete(
      `http://127.0.0.1:8000/api/template/${currentTemplate.value.template_id}`
    )
    
    if (response.data.success) {
      ElMessage.success('模板删除成功')
      loadTemplates()
      previewDialogVisible.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除模板失败：' + error.message)
    }
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-library {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-card {
  text-align: center;
  padding: 20px;
  cursor: pointer;
}

.template-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.template-info {
  color: #909399;
  font-size: 12px;
}
</style>
