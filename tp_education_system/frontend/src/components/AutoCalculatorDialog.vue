<template>
  <el-dialog
    v-model="visible"
    title="计算工作年限"
    width="600px"
    :close-on-click-modal="false"
  >
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>
    
    <div v-else class="calculator-content">
      <el-form label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-input v-model="formData.birth_date" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-input v-model="formData.gender" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="个人身份">
              <el-select v-model="formData.personal_identity" style="width: 100%">
                <el-option label="干部" value="干部" />
                <el-option label="工勤" value="工勤" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参加工作时间">
              <el-input v-model="formData.work_start_date" disabled />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <el-divider />
      
      <div class="result-section">
        <h4>计算结果</h4>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="原退休日期">
              <el-input v-model="result.original_retirement_date" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="延迟月数">
              <el-input v-model="result.delay_months" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计算退休日期">
              <el-input v-model="result.calculated_retirement_date" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="现退休日期">
              <el-date-picker
                v-model="result.actual_retirement_date"
                type="date"
                placeholder="可调整"
                format="YYYY年M月D日"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                @change="handleDateChange"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作年限">
              <el-input v-model="result.work_years" disabled>
                <template #append>年</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="calculating" @click="handleCalculate">
        计算
      </el-button>
      <el-button type="success" :loading="saving" @click="handleSave">
        确认保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
  tableName: string
  teacherId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'saved': []
}>()

const visible = ref(false)
const loading = ref(false)
const calculating = ref(false)
const saving = ref(false)

const formData = reactive({
  birth_date: '',
  gender: '',
  personal_identity: '干部',
  work_start_date: ''
})

const result = reactive({
  original_retirement_date: '',
  delay_months: 0,
  calculated_retirement_date: '',
  actual_retirement_date: '',
  work_years: 0
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.teacherId) {
    loadData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadData = async () => {
  if (!props.teacherId) return
  
  loading.value = true
  try {
    const response = await fetch(`/api/auto-table/${props.tableName}/detail/${props.teacherId}`)
    const data = await response.json()
    if (data.status === 'success') {
      formData.birth_date = data.data['出生日期'] || ''
      formData.gender = data.data['性别'] || ''
      formData.personal_identity = data.data['个人身份'] || '干部'
      formData.work_start_date = data.data['参加工作时间'] || ''
      
      await handleCalculate()
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleCalculate = async () => {
  if (!props.teacherId) return
  
  calculating.value = true
  try {
    const response = await fetch(`/api/auto-table/${props.tableName}/calculate/${props.teacherId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    if (data.status === 'success') {
      result.original_retirement_date = data.data.original_retirement_date
      result.delay_months = data.data.delay_months
      result.calculated_retirement_date = data.data.calculated_retirement_date
      result.actual_retirement_date = data.data.actual_retirement_date
      result.work_years = data.data.work_years
    }
  } catch (error) {
    ElMessage.error('计算失败')
  } finally {
    calculating.value = false
  }
}

const handleDateChange = () => {
  if (!result.actual_retirement_date || !formData.work_start_date) return
  
  const retirementDate = new Date(result.actual_retirement_date)
  const workStartDate = new Date(formData.work_start_date)
  
  let years = retirementDate.getFullYear() - workStartDate.getFullYear()
  if (retirementDate.getMonth() < workStartDate.getMonth() ||
      (retirementDate.getMonth() === workStartDate.getMonth() && retirementDate.getDate() < workStartDate.getDate())) {
    years--
  }
  
  result.work_years = Math.max(0, years)
}

const handleSave = async () => {
  if (!props.teacherId) return
  
  saving.value = true
  try {
    const response = await fetch(`/api/auto-table/${props.tableName}/save-calculation/${props.teacherId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        retirement_date: result.actual_retirement_date,
        work_years: result.work_years
      })
    })
    
    const data = await response.json()
    if (data.status === 'success') {
      ElMessage.success('保存成功')
      emit('saved')
      handleClose()
    } else {
      ElMessage.error(data.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
  result.original_retirement_date = ''
  result.delay_months = 0
  result.calculated_retirement_date = ''
  result.actual_retirement_date = ''
  result.work_years = 0
}
</script>

<style scoped>
.calculator-content {
  padding: 10px 0;
}

.result-section {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.result-section h4 {
  margin: 0 0 15px 0;
  color: #606266;
}

.loading-container {
  padding: 20px;
}
</style>
