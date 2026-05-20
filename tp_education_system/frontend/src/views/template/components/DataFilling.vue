<template>
  <div class="data-filling">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据填报</span>
          <div>
            <el-button type="primary" @click="showTagDialog = true">
              <el-icon><PriceTag /></el-icon>
              标签筛选 {{ selectedTags.length > 0 ? `(${selectedTags.length})` : '' }}
            </el-button>
            <el-button type="success" @click="handleSaveMapping" :disabled="!selectedTemplate">
              保存映射配置
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="selectedTags.length > 0" class="selected-tags-section">
        <div class="tags-label">
          已选标签
          <span v-if="!selectedTags.includes('全部人员')" style="font-weight: normal; color: #909399; margin-left: 10px;">
            ({{ tagLogic === 'OR' ? '满足任一标签' : '同时满足所有标签' }})
          </span>
        </div>
        <el-tag 
          v-for="tag in selectedTags" 
          :key="tag" 
          closable 
          @close="removeTag(tag)"
          style="margin-right: 8px; margin-bottom: 8px;"
          :type="tag === '全部人员' ? 'success' : ''"
        >
          {{ tag }}
        </el-tag>
      </div>

      <el-steps :active="currentStep" finish-status="success" simple>
        <el-step title="选择模板" />
        <el-step title="选择统计类型" />
        <el-step title="字段映射配置" />
        <el-step title="预览确认" />
      </el-steps>

      <div class="step-content" v-if="currentStep === 0">
        <el-form :model="form" label-width="120px">
          <el-form-item label="选择模板">
            <el-select v-model="selectedTemplate" placeholder="请选择模板" @change="handleTemplateChange">
              <el-option
                v-for="template in templates"
                :key="template.template_id"
                :label="template.template_name"
                :value="template.template_id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <div class="step-content" v-if="currentStep === 1">
        <el-form :model="form" label-width="120px">
          <el-form-item label="统计类型">
            <el-radio-group v-model="form.fillType">
              <el-radio label="unit" border>单位统计</el-radio>
              <el-radio label="personal" border>个人统计</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="选择单位" v-if="form.fillType === 'unit'">
            <UnitTreeSelect v-model="form.unitIds" @change="handleUnitsChange" />
          </el-form-item>

          <el-form-item label="搜索教师" v-if="form.fillType === 'personal'">
            <el-select
              v-model="form.teacherId"
              filterable
              remote
              reserve-keyword
              placeholder="请输入姓名/身份证/教师ID"
              :remote-method="searchTeachers"
              :loading="searchLoading"
              @change="handleTeacherSelect"
            >
              <el-option
                v-for="teacher in teacherOptions"
                :key="teacher.teacher_id"
                :label="`${teacher.name} (${teacher.id_card})`"
                :value="teacher.teacher_id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <div class="step-content" v-if="currentStep === 2">
        <FieldMapping
          :template-id="selectedTemplate"
          :metadata="templateMetadata"
          @mapping-change="handleMappingChange"
        />
      </div>

      <div class="step-content" v-if="currentStep === 3">
        <el-card>
          <template #header>
            <span>填报预览</span>
          </template>
          <div v-if="previewData">
            <el-descriptions :column="2" border>
              <el-descriptions-item
                v-for="(value, key) in previewData"
                :key="key"
                :label="key"
              >
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="暂无预览数据" />
        </el-card>
      </div>

      <div class="step-actions">
        <el-button @click="prevStep" :disabled="currentStep === 0">上一步</el-button>
        <el-button type="primary" @click="nextStep" :disabled="!canNextStep">
          {{ currentStep === 3 ? '确认填报' : '下一步' }}
        </el-button>
      </div>
    </el-card>

    <el-dialog v-model="showTagDialog" title="标签筛选（多选）" width="600px">
      <el-alert 
        type="info" 
        :closable="false" 
        style="margin-bottom: 15px;"
      >
        <template #title>
          <div style="font-size: 14px;">
            <strong>使用说明：</strong><br>
            • 选择"全部人员"：统计所有教师，不进行标签筛选<br>
            • 选择具体标签：只统计有这些标签的教师<br>
            • OR逻辑：满足任一标签即可<br>
            • AND逻辑：必须同时满足所有标签
          </div>
        </template>
      </el-alert>

      <el-form label-width="100px">
        <el-form-item label="组合逻辑">
          <el-radio-group v-model="tagLogic" :disabled="selectedTags.includes('全部人员')">
            <el-radio label="OR" border>OR（满足任一标签）</el-radio>
            <el-radio label="AND" border>AND（同时满足所有标签）</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="选择标签">
          <el-checkbox-group v-model="selectedTags" class="tag-list">
            <el-checkbox 
              value="全部人员" 
              class="tag-item"
              style="margin-right: 15px; margin-bottom: 10px; font-weight: bold; color: #409EFF;"
            >
              全部人员（不筛选标签）
            </el-checkbox>
            <el-checkbox 
              v-for="tag in tagList" 
              :key="tag.标签ID" 
              :value="tag.标签名称" 
              class="tag-item"
              style="margin-right: 15px; margin-bottom: 10px;"
              :disabled="selectedTags.includes('全部人员')"
            >
              {{ tag.标签名称 }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="已选标签">
          <div v-if="selectedTags.length > 0">
            <el-tag 
              v-for="tag in selectedTags" 
              :key="tag" 
              closable 
              @close="removeTagFromDialog(tag)"
              style="margin-right: 8px; margin-bottom: 8px;"
              :type="tag === '全部人员' ? 'success' : ''"
            >
              {{ tag }}
            </el-tag>
            <div style="margin-top: 10px; color: #909399; font-size: 13px;">
              <span v-if="selectedTags.includes('全部人员')">
                统计范围：所有教师
              </span>
              <span v-else-if="selectedTags.length > 0">
                统计范围：{{ tagLogic === 'OR' ? '满足任一标签' : '同时满足所有标签' }}的教师
              </span>
            </div>
          </div>
          <div v-else style="color: #909399;">请选择至少一个标签</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmTags" :disabled="selectedTags.length === 0">
          确认选择
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PriceTag } from '@element-plus/icons-vue'
import FieldMapping from './FieldMapping.vue'
import UnitTreeSelect from './UnitTreeSelect.vue'

const currentStep = ref(0)
const templates = ref([])
const selectedTemplate = ref(null)
const templateMetadata = ref(null)
const units = ref([])
const teacherOptions = ref([])
const searchLoading = ref(false)
const previewData = ref(null)
const fieldMappings = ref([])

const tagList = ref([])
const selectedTags = ref([])
const showTagDialog = ref(false)
const tagLogic = ref('OR')

const form = ref({
  fillType: 'unit',
  unitIds: [],
  unitsInfo: [],
  teacherId: null
})

const canNextStep = computed(() => {
  if (currentStep.value === 0) {
    return selectedTemplate.value !== null
  }
  if (currentStep.value === 1) {
    if (form.value.fillType === 'unit') {
      return form.value.unitIds.length > 0
    } else {
      return form.value.teacherId !== null
    }
  }
  if (currentStep.value === 2) {
    return fieldMappings.value.length > 0
  }
  return true
})

onMounted(async () => {
  await loadTemplates()
  await loadTags()
})

async function loadTags() {
  try {
    const response = await axios.get('/api/aggregate-query/tags')
    if (response.data.状态 === '成功') {
      tagList.value = response.data.标签列表
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

function confirmTags() {
  if (selectedTags.value.includes('全部人员')) {
    selectedTags.value = ['全部人员']
    tagLogic.value = 'OR'
  }
  showTagDialog.value = false
}

function removeTagFromDialog(tag) {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  }
}

function removeTag(tag) {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  }
}

async function loadTemplates() {
  try {
    const response = await axios.get('/api/template/list')
    if (response.data.success) {
      templates.value = response.data.templates
    }
  } catch (error) {
    ElMessage.error('加载模板列表失败：' + error.message)
  }
}

function handleUnitsChange(data) {
  form.value.unitsInfo = data.units
  console.log('选择的单位：', data.units)
}

async function handleTemplateChange(templateId) {
  try {
    const template = templates.value.find(t => t.template_id === templateId)
    if (template) {
      const response = await axios.get(`/api/template/preview?file_path=${template.file_path}`)
      if (response.data.success) {
        templateMetadata.value = response.data.metadata
      }
    }
  } catch (error) {
    ElMessage.error('加载模板元数据失败：' + error.message)
  }
}

async function searchTeachers(keyword) {
  if (!keyword) {
    teacherOptions.value = []
    return
  }
  
  searchLoading.value = true
  try {
    const response = await axios.get(`/api/template/search-teachers`, {
      params: {
        keyword: keyword,
        search_type: '姓名'
      }
    })
    if (response.data.success) {
      teacherOptions.value = response.data.teachers
    }
  } catch (error) {
    ElMessage.error('搜索教师失败：' + error.message)
  } finally {
    searchLoading.value = false
  }
}

function handleTeacherSelect(teacherId) {
  const teacher = teacherOptions.value.find(t => t.teacher_id === teacherId)
  if (teacher) {
    form.value.unitInfo = {
      teacher_name: teacher.name,
      teacher_id: teacherId
    }
  }
}

function handleMappingChange(mappings) {
  fieldMappings.value = mappings
}

async function handleSaveMapping() {
  if (!selectedTemplate.value || fieldMappings.value.length === 0) {
    ElMessage.warning('请先配置字段映射')
    return
  }
  
  try {
    const response = await axios.post('/api/template/field-mapping/save', {
      template_id: selectedTemplate.value,
      mappings: fieldMappings.value
    })
    if (response.data.success) {
      ElMessage.success('字段映射配置保存成功')
    }
  } catch (error) {
    ElMessage.error('保存字段映射失败：' + error.message)
  }
}

async function nextStep() {
  if (currentStep.value === 3) {
    await confirmFill()
  } else {
    if (currentStep.value === 2) {
      await loadPreviewData()
    }
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function loadPreviewData() {
  try {
    const response = await axios.post('/api/template/aggregate-data', {
      template_id: selectedTemplate.value,
      fill_type: form.value.fillType,
      unit_id: form.value.unitId,
      unit_info: form.value.unitInfo,
      teacher_id: form.value.teacherId
    })
    if (response.data.success) {
      previewData.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('加载预览数据失败：' + error.message)
  }
}

async function confirmFill() {
  try {
    await ElMessageBox.confirm('确认填报数据？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ElMessage.success('填报成功')
    currentStep.value = 0
    resetForm()
  } catch {
    ElMessage.info('已取消填报')
  }
}

function resetForm() {
  selectedTemplate.value = null
  templateMetadata.value = null
  form.value = {
    fillType: 'unit',
    unitIds: [],
    unitsInfo: [],
    teacherId: null
  }
  previewData.value = null
  fieldMappings.value = []
}
</script>

<style scoped>
.data-filling {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-tags-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.tags-label {
  font-weight: bold;
  margin-bottom: 10px;
  color: #606266;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
}

.tag-item {
  margin-right: 15px;
  margin-bottom: 10px;
}

.step-content {
  margin: 20px 0;
  min-height: 300px;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
</style>

