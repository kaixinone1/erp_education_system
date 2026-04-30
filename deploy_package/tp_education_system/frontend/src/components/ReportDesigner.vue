<template>
  <div class="report-designer">
    <el-dialog
      v-model="visible"
      title="职工退休呈报表 - 报表设计器"
      width="1100px"
      :close-on-click-modal="false"
      class="designer-dialog"
      destroy-on-close
    >
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="20" animated />
      </div>

      <div v-else class="report-container">
        <!-- 报表头部 -->
        <div class="report-header">
          <div class="report-title">职 工 退 休 呈 报 表</div>
          <div class="report-subtitle">枣阳市人力资源和社会保障局制</div>
        </div>

        <!-- 基本信息区域 -->
        <div class="section">
          <div class="section-title">基本信息</div>
          <div class="form-grid">
            <div class="form-item">
              <label>姓名：</label>
              <span class="value">{{ reportData.teacher_name }}</span>
            </div>
            <div class="form-item">
              <label>性别：</label>
              <span class="value">{{ reportData.gender }}</span>
            </div>
            <div class="form-item">
              <label>出生年月：</label>
              <span class="value">{{ reportData.birth_date }}</span>
            </div>
            <div class="form-item">
              <label>身份证号：</label>
              <span class="value">{{ reportData.id_card }}</span>
            </div>
            <div class="form-item">
              <label>民族：</label>
              <span class="value">{{ reportData.ethnicity }}</span>
            </div>
            <div class="form-item">
              <label>籍贯：</label>
              <span class="value">{{ reportData.native_place }}</span>
            </div>
          </div>
        </div>

        <!-- 教育信息区域 -->
        <div class="section">
          <div class="section-title">教育信息</div>
          <div class="form-grid">
            <div class="form-item">
              <label>文化程度：</label>
              <el-input v-model="reportData.education" placeholder="请输入" size="small" class="edit-input" />
            </div>
            <div class="form-item">
              <label>毕业学校：</label>
              <el-input v-model="reportData.graduation_school" placeholder="请输入" size="small" class="edit-input" />
            </div>
            <div class="form-item">
              <label>专业：</label>
              <el-input v-model="reportData.major" placeholder="请输入" size="small" class="edit-input" />
            </div>
            <div class="form-item">
              <label>学位：</label>
              <el-input v-model="reportData.degree" placeholder="请输入" size="small" class="edit-input" />
            </div>
          </div>
        </div>

        <!-- 工作信息区域 -->
        <div class="section">
          <div class="section-title">工作信息</div>
          <div class="form-grid">
            <div class="form-item">
              <label>参加工作时间：</label>
              <span class="value">{{ reportData.work_start_date }}</span>
            </div>
            <div class="form-item">
              <label>工作单位：</label>
              <el-input v-model="reportData.work_unit" placeholder="请输入" size="small" class="edit-input" />
            </div>
            <div class="form-item">
              <label>职务：</label>
              <el-input v-model="reportData.position" placeholder="请输入" size="small" class="edit-input" />
            </div>
            <div class="form-item">
              <label>职称：</label>
              <el-input v-model="reportData.title" placeholder="请输入" size="small" class="edit-input" />
            </div>
          </div>
        </div>

        <!-- 退休信息区域 -->
        <div class="section">
          <div class="section-title">退休信息</div>
          <div class="form-grid">
            <div class="form-item">
              <label>年龄：</label>
              <span class="value">{{ reportData.age }} 岁</span>
            </div>
            <div class="form-item">
              <label>退休日期：</label>
              <el-date-picker
                v-model="reportData.retirement_date"
                type="date"
                placeholder="选择日期"
                size="small"
                value-format="YYYY-MM-DD"
                class="edit-input"
              />
            </div>
            <div class="form-item">
              <label>退休原因：</label>
              <el-select v-model="reportData.retirement_reason" placeholder="请选择" size="small" class="edit-input">
                <el-option label="达到法定退休年龄" value="达到法定退休年龄" />
                <el-option label="提前退休" value="提前退休" />
                <el-option label="其他" value="其他" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- 审批意见区域 -->
        <div class="section">
          <div class="section-title">审批意见</div>
          <div class="approval-section">
            <div class="approval-item">
              <div class="approval-title">呈报单位意见</div>
              <div class="approval-content">
                <p>经研究，同意 {{ reportData.teacher_name }} 同志按以下第（&nbsp;&nbsp;&nbsp;&nbsp;）条办理退休，从 {{ reportData.retirement_date || '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' }} 执行。</p>
                <p>（一）弹性提前退休</p>
                <p>（二）法定退休年龄退休</p>
                <div class="approval-date">
                  <span>{{ currentYear }}</span> 年
                  <span>{{ currentMonth }}</span> 月
                  <span>{{ currentDay }}</span> 日
                </div>
              </div>
            </div>

            <div class="approval-item">
              <div class="approval-title">主管部门审查意见</div>
              <div class="approval-content">
                <p>同意呈报</p>
                <div class="approval-date">
                  <span>{{ currentYear }}</span> 年
                  <span>{{ currentMonth }}</span> 月
                  <span>{{ currentDay }}</span> 日
                </div>
              </div>
            </div>

            <div class="approval-item">
              <div class="approval-title">退休一次性补贴审批意见</div>
              <div class="approval-content">
                <p>根据鄂人社发【2017】8号文件规定，同意 {{ reportData.teacher_name }} 同志发放一次性独生子女费 <el-input v-model="reportData.only_child_fee" size="small" class="inline-input" /> 元，教育特殊贡献奖 <el-input v-model="reportData.education_contribution_award" size="small" class="inline-input" /> 元，从 {{ reportData.retirement_date || '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' }} 执行。</p>
                <div class="approval-date">
                  <span>{{ currentYear }}</span> 年
                  <span>{{ currentMonth }}</span> 月
                  <span>{{ currentDay }}</span> 日
                </div>
              </div>
            </div>

            <div class="approval-item">
              <div class="approval-title">批准机关审批意见</div>
              <div class="approval-content">
                <p>根据人社部发【2024】94号文件规定，同意 {{ reportData.teacher_name }} 同志按第（&nbsp;&nbsp;&nbsp;&nbsp;）条退休，从 {{ reportData.retirement_date || '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' }} 执行。</p>
                <div class="approval-date">
                  <span>{{ currentYear }}</span> 年
                  <span>{{ currentMonth }}</span> 月
                  <span>{{ currentDay }}</span> 日
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 备注 -->
        <div class="section">
          <div class="section-title">备注</div>
          <el-input
            v-model="reportData.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存
          </el-button>
          <el-dropdown @command="handleExport" split-button type="success" :loading="exporting">
            导出
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="word">导出 Word</el-dropdown-item>
                <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
                <el-dropdown-item command="print">打印</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  teacherId: number
}>()

const emit = defineEmits(['save', 'export', 'close'])

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)

// 当前日期
const now = new Date()
const currentYear = computed(() => now.getFullYear())
const currentMonth = computed(() => now.getMonth() + 1)
const currentDay = computed(() => now.getDate())

// 报表数据
const reportData = reactive({
  teacher_id: 0,
  teacher_name: '',
  gender: '',
  birth_date: '',
  id_card: '',
  ethnicity: '',
  native_place: '',
  education: '',
  graduation_school: '',
  major: '',
  degree: '',
  work_start_date: '',
  work_unit: '',
  position: '',
  title: '',
  work_years: 0,
  age: 0,
  retirement_date: '',
  retirement_reason: '',
  only_child_fee: '',
  education_contribution_award: '',
  remarks: ''
})

// 打开报表设计器
const open = async () => {
  visible.value = true
  loading.value = true

  try {
    // 获取教师完整数据（多表关联）
    const response = await fetch(`/api/report-designer/teacher-full-data?teacher_id=${props.teacherId}`)

    if (!response.ok) {
      throw new Error('获取教师数据失败')
    }

    const result = await response.json()

    if (result.status === 'success') {
      Object.assign(reportData, result.data)
      reportData.teacher_id = props.teacherId
    } else {
      throw new Error(result.message || '获取数据失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

// 保存报表
const handleSave = async () => {
  saving.value = true

  try {
    const response = await fetch('/api/report-designer/save-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData)
    })

    if (!response.ok) {
      throw new Error('保存失败')
    }

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('保存成功')
      emit('save', reportData)
    } else {
      throw new Error(result.message || '保存失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 导出
const handleExport = async (format: string) => {
  if (format === 'print') {
    window.print()
    return
  }

  exporting.value = true

  try {
    const response = await fetch(`/api/report-designer/export?format=${format}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData)
    })

    if (!response.ok) {
      throw new Error('导出失败')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    const extensions: Record<string, string> = {
      word: 'docx',
      pdf: 'pdf'
    }

    link.download = `职工退休呈报表_${reportData.teacher_name}.${extensions[format]}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(`已导出 ${format.toUpperCase()} 格式`)
    emit('export', { format, data: reportData })
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 关闭
const close = () => {
  visible.value = false
  emit('close')
}

defineExpose({
  open,
  close
})
</script>

<style scoped>
.report-designer {
  :deep(.designer-dialog) {
    .el-dialog__body {
      max-height: 70vh;
      overflow-y: auto;
      padding: 20px;
    }
  }
}

.loading-container {
  padding: 40px;
}

.report-container {
  font-family: 'SimSun', '宋体', serif;
  font-size: 14px;
  line-height: 1.6;
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #333;

  .report-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    letter-spacing: 8px;
  }

  .report-subtitle {
    font-size: 14px;
    color: #666;
  }
}

.section {
  margin-bottom: 25px;

  .section-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 4px solid #409eff;
  }
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;

  .form-item {
    display: flex;
    align-items: center;

    label {
      min-width: 120px;
      font-weight: 500;
      color: #333;
    }

    .value {
      flex: 1;
      padding: 5px 10px;
      background: #f5f7fa;
      border-radius: 4px;
      min-height: 28px;
    }

    .edit-input {
      flex: 1;
    }
  }
}

.approval-section {
  border: 1px solid #dcdfe6;
  border-radius: 4px;

  .approval-item {
    display: flex;
    border-bottom: 1px solid #dcdfe6;

    &:last-child {
      border-bottom: none;
    }

    .approval-title {
      width: 120px;
      padding: 15px;
      background: #f5f7fa;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      border-right: 1px solid #dcdfe6;
    }

    .approval-content {
      flex: 1;
      padding: 15px;

      p {
        margin: 8px 0;
      }

      .approval-date {
        margin-top: 20px;
        text-align: right;

        span {
          display: inline-block;
          min-width: 40px;
          text-align: center;
          border-bottom: 1px solid #333;
          margin: 0 5px;
        }
      }
    }
  }
}

.inline-input {
  width: 80px;
  display: inline-block;
  margin: 0 5px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 打印样式 */
@media print {
  .report-designer :deep(.el-dialog__header),
  .report-designer :deep(.el-dialog__footer) {
    display: none !important;
  }

  .report-container {
    font-size: 12pt;
  }

  .edit-input,
  .inline-input {
    border: none;
    background: transparent;
  }
}
</style>
