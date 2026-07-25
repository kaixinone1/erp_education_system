<template>
  <div class="data-fill-wizard">
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step title="标签筛选" description="选择统计范围" />
      <el-step title="数据预览" description="查看岗位分布" />
      <el-step title="统计计算" description="自动计算数据" />
      <el-step title="结果确认" description="保存并导出" />
    </el-steps>

    <div class="step-content">
      <div v-if="currentStep === 0" class="step-panel">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
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
                @close="removeTag(tag)"
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
      </div>

      <div v-else-if="currentStep === 1" class="step-panel">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
          <template #title>
            <div style="font-size: 14px;">
              <strong>数据预览：</strong><br>
              • 标签筛选结果：{{ filteredTeacherCount }}名教师<br>
              • 请确认岗位分布是否正确
            </div>
          </template>
        </el-alert>

        <el-table :data="previewData" border style="width: 100%" v-loading="loadingPreview">
          <el-table-column prop="post" label="岗位" width="200" />
          <el-table-column prop="count" label="人数" width="100" />
        </el-table>
      </div>

      <div v-else-if="currentStep === 2" class="step-panel">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
          <template #title>
            <div style="font-size: 14px;">
              <strong>计算进度：</strong><br>
              • 统计岗位人数...完成<br>
              • 查询绩效标准...完成<br>
              • 计算岗位小计...完成<br>
              • 汇总绩效合计...完成
            </div>
          </template>
        </el-alert>

        <el-table :data="calculationResult" border style="width: 100%" v-loading="loadingCalculation">
          <el-table-column prop="field" label="字段" width="200" />
          <el-table-column prop="value" label="值" width="150" />
        </el-table>
      </div>

      <div v-else-if="currentStep === 3" class="step-panel">
        <el-alert type="success" :closable="false" style="margin-bottom: 20px;">
          <template #title>
            <div style="font-size: 14px;">
              <strong>统计结果：</strong><br>
              • 数据已计算完成，请确认后保存
            </div>
          </template>
        </el-alert>

        <el-form label-width="120px">
          <el-form-item label="填报年月">
            <el-date-picker
              v-model="reportDate"
              type="month"
              placeholder="选择年月"
              format="YYYY年MM月"
              value-format="YYYY-MM"
            />
          </el-form-item>

          <el-form-item label="导出格式">
            <el-checkbox-group v-model="exportFormats">
              <el-checkbox label="json">JSON数据</el-checkbox>
              <el-checkbox label="excel">Excel文件</el-checkbox>
              <el-checkbox label="pdf">PDF文件</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="备份选项">
            <el-checkbox v-model="enableBackup">自动备份到历史记录</el-checkbox>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="step-actions">
      <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
      <el-button v-if="currentStep < 3" type="primary" @click="nextStep" :disabled="!canNextStep">
        下一步
      </el-button>
      <el-button v-if="currentStep === 3" type="success" @click="saveData" :loading="saving">
        保存并导出
      </el-button>
      <el-button @click="$emit('close')">取消</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  templateId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'save'])

const currentStep = ref(0)
const tagLogic = ref('OR')
const selectedTags = ref([])
const tagList = ref([])
const filteredTeacherIds = ref([])
const filteredTeacherCount = ref(0)
const previewData = ref([])
const calculationResult = ref([])
const reportDate = ref(new Date().toISOString().substr(0, 7))
const exportFormats = ref(['json', 'excel'])
const enableBackup = ref(true)
const loadingPreview = ref(false)
const loadingCalculation = ref(false)
const saving = ref(false)

const canNextStep = computed(() => {
  if (currentStep.value === 0) {
    return selectedTags.value.length > 0
  }
  return true
})

async function loadTagList() {
  try {
    const response = await axios.get('/api/aggregate-query/tags')
    if (response.data.状态 === '成功') {
      tagList.value = response.data.标签列表
    }
  } catch (error) {
    ElMessage.error('加载标签列表失败：' + error.message)
  }
}

function removeTag(tag) {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  }
}

async function executeTagFilter() {
  try {
    const response = await axios.post('/api/template-management/filter-by-tags', {
      template_id: props.templateId,
      tags: selectedTags.value,
      logic: tagLogic.value
    })
    
    if (response.data.状态 === '成功') {
      filteredTeacherIds.value = response.data.教师ID列表
      filteredTeacherCount.value = response.data.数量
    }
  } catch (error) {
    ElMessage.error('标签筛选失败：' + error.message)
  }
}

async function loadPreviewData() {
  loadingPreview.value = true
  try {
    const response = await axios.post('/api/template-management/calculate', {
      template_id: props.templateId,
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1,
      teacher_ids: filteredTeacherIds.value
    })
    
    if (response.data.状态 === '成功') {
      const data = response.data.数据
      previewData.value = Object.keys(data).map(key => ({
        post: key,
        count: data[key]
      }))
    }
  } catch (error) {
    ElMessage.error('加载预览数据失败：' + error.message)
  } finally {
    loadingPreview.value = false
  }
}

async function executeCalculation() {
  loadingCalculation.value = true
  try {
    const response = await axios.post('/api/template-management/calculate', {
      template_id: props.templateId,
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1,
      teacher_ids: filteredTeacherIds.value
    })
    
    if (response.data.状态 === '成功') {
      const data = response.data.数据
      calculationResult.value = Object.keys(data).map(key => ({
        field: key,
        value: data[key]
      }))
    }
  } catch (error) {
    ElMessage.error('统计计算失败：' + error.message)
  } finally {
    loadingCalculation.value = false
  }
}

async function saveData() {
  saving.value = true
  try {
    const [year, month] = reportDate.value.split('-')
    
    const dataObj = {}
    calculationResult.value.forEach(item => {
      dataObj[item.field] = item.value
    })
    
    const response = await axios.post('/api/template-management/save', {
      template_id: props.templateId,
      year: parseInt(year),
      month: parseInt(month),
      data: dataObj
    })
    
    if (response.data.状态 === '成功') {
      ElMessage.success('保存成功')
      emit('save')
    }
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

async function nextStep() {
  if (currentStep.value === 0) {
    await executeTagFilter()
  } else if (currentStep.value === 1) {
    await executeCalculation()
  }
  
  currentStep.value++
}

function prevStep() {
  currentStep.value--
}

onMounted(() => {
  loadTagList()
})
</script>

<style scoped>
.data-fill-wizard {
  padding: 20px;
}

.step-content {
  margin: 30px 0;
  min-height: 400px;
}

.step-panel {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
</style>

