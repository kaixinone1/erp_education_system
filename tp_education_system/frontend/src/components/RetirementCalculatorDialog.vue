<template>
  <el-dialog
    v-model="visible"
    title="计算工作年限"
    width="600px"
    :close-on-click-modal="false"
  >
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else class="calculator-content">
      <!-- 基本信息（只读） -->
      <el-form :model="formData" label-width="120px">
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
              <el-select v-model="formData.personal_identity" placeholder="请选择" style="width: 100%">
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
      
      <!-- 计算结果 -->
      <div class="result-section">
        <h4>计算结果</h4>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="原退休日期">
              <el-input v-model="calcResult.original_retirement_date" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="延迟月数">
              <el-input v-model="calcResult.delay_months" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计算退休日期">
              <el-input v-model="calcResult.calculated_retirement_date" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="现退休日期">
              <el-date-picker
                v-model="calcResult.actual_retirement_date"
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
              <el-input v-model="calcResult.work_years" disabled>
                <template #append>年</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <el-alert
        v-if="calcResult.actual_retirement_date !== calcResult.calculated_retirement_date"
        title="已调整退休日期，工作年限已重新计算"
        type="warning"
        :closable="false"
        style="margin-top: 10px"
      />
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="calculating" @click="handleCalculate">
          计算
        </el-button>
        <el-button type="success" :loading="saving" @click="handleSave">
          确认保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
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

const calcResult = reactive({
  original_retirement_date: '',
  delay_months: 0,
  calculated_retirement_date: '',
  actual_retirement_date: '',
  work_years: 0
})

// 监听visible变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.teacherId) {
    loadTeacherData()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载教师数据
const loadTeacherData = async () => {
  if (!props.teacherId) return
  
  loading.value = true
  try {
    const response = await fetch(`/api/retirement-data/detail/${props.teacherId}`)
    const result = await response.json()
    if (result.status === 'success') {
      const data = result.data
      formData.birth_date = data['出生日期'] || ''
      formData.gender = data['性别'] || ''
      formData.personal_identity = data['个人身份'] || '干部'
      formData.work_start_date = data['参加工作时间'] || ''
      
      // 自动计算
      await handleCalculate()
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 计算退休信息
const handleCalculate = async () => {
  if (!props.teacherId) return
  
  calculating.value = true
  try {
    const response = await fetch(`/api/retirement-data/calculate-retirement/${props.teacherId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        custom_retirement_date: calcResult.actual_retirement_date || null
      })
    })
    const result = await response.json()
    
    if (result.status === 'success') {
      const data = result.data
      calcResult.original_retirement_date = data.original_retirement_date
      calcResult.delay_months = data.delay_months
      calcResult.calculated_retirement_date = data.calculated_retirement_date
      calcResult.actual_retirement_date = data.actual_retirement_date
      calcResult.work_years = data.work_years
      
      // 同步个人身份
      formData.personal_identity = data.personal_identity
    }
  } catch (error) {
    ElMessage.error('计算失败')
    console.error(error)
  } finally {
    calculating.value = false
  }
}

// 日期改变时重新计算工作年限
const handleDateChange = async () => {
  if (!calcResult.actual_retirement_date || !formData.work_start_date) return
  
  // 简单计算工作年限
  const retirementDate = new Date(calcResult.actual_retirement_date)
  const workStartDate = new Date(formData.work_start_date)
  
  let years = retirementDate.getFullYear() - workStartDate.getFullYear()
  if (retirementDate.getMonth() < workStartDate.getMonth() ||
      (retirementDate.getMonth() === workStartDate.getMonth() && retirementDate.getDate() < workStartDate.getDate())) {
    years--
  }
  
  calcResult.work_years = Math.max(0, years)
}

// 保存计算结果
const handleSave = async () => {
  if (!props.teacherId) return
  
  saving.value = true
  try {
    const response = await fetch(`/api/retirement-data/save-retirement-calculation/${props.teacherId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        retirement_date: calcResult.actual_retirement_date,
        work_years: calcResult.work_years
      })
    })
    const result = await response.json()
    
    if (result.status === 'success') {
      ElMessage.success('保存成功')
      emit('saved')
      handleClose()
    }
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
  // 重置数据
  calcResult.original_retirement_date = ''
  calcResult.delay_months = 0
  calcResult.calculated_retirement_date = ''
  calcResult.actual_retirement_date = ''
  calcResult.work_years = 0
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
  margin-top: 10px;
}

.result-section h4 {
  margin: 0 0 15px 0;
  color: #606266;
}

.loading-container {
  padding: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
