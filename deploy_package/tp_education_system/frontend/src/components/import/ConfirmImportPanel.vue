<template>
  <div class="confirm-import-panel">
    <el-card class="panel-card">
      <template #header>
        <div class="card-header">
          <span>第四步：确认导入</span>
        </div>
      </template>

      <div class="panel-content">
        <!-- 导入摘要 -->
        <div class="summary-section">
          <h3>导入摘要</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="数据量">
              {{ validatedData?.length || 0 }} 条记录
            </el-descriptions-item>
            <el-descriptions-item label="目标表名">
              {{ tableName }}
            </el-descriptions-item>
            <el-descriptions-item label="归属模块">
              {{ moduleName }}
            </el-descriptions-item>
            <el-descriptions-item label="字段数量">
              {{ fieldConfigs?.length || 0 }} 个字段
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 中文表名编辑 -->
        <div class="chinese-title-section" style="margin-top: 20px;">
          <h3>中文表名设置</h3>
          <el-alert
            v-if="importError?.includes('表结构不一致')"
            :title="importError"
            type="error"
            show-icon
            :closable="false"
            style="margin-bottom: 10px;"
          >
            <template #default>
              <div style="margin-top: 8px;">
                <p>该中文表名已存在，但字段结构与当前导入的数据不匹配。</p>
                <p>请修改中文表名后重新导入：</p>
              </div>
            </template>
          </el-alert>
          <el-form :inline="true">
            <el-form-item label="中文表名">
              <el-input
                v-model="editableChineseTitle"
                placeholder="请输入中文表名"
                style="width: 300px;"
                :disabled="importing"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="updateChineseTitle"
                :loading="updatingTitle"
                :disabled="!editableChineseTitle || editableChineseTitle === chineseTitle"
              >
                更新表名
              </el-button>
            </el-form-item>
          </el-form>
          <p v-if="titleUpdateMessage" :class="['update-message', titleUpdateStatus]">
            {{ titleUpdateMessage }}
          </p>
        </div>

        <!-- 字段配置预览 -->
        <div class="fields-preview-section">
          <h3>字段配置</h3>
          <el-table
            :data="fieldConfigs"
            style="width: 100%"
            max-height="300px"
            border
            size="small"
          >
            <el-table-column
              prop="sourceField"
              label="原始字段"
              min-width="120"
            />
            <el-table-column
              prop="targetField"
              label="系统字段"
              min-width="120"
            />
            <el-table-column
              prop="dataType"
              label="数据类型"
              width="100"
            />
            <el-table-column
              label="约束"
              width="150"
            >
              <template #default="{ row }">
                <el-tag v-if="row.required" size="small" type="danger">必填</el-tag>
                <el-tag v-if="row.unique" size="small" type="warning">唯一</el-tag>
                <el-tag v-if="row.indexed" size="small" type="info">索引</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 数据预览 -->
        <div class="data-preview-section">
          <h3>数据预览（前5条）</h3>
          <el-table
            :data="previewData"
            style="width: 100%"
            max-height="250px"
            border
            size="small"
          >
            <el-table-column
              v-for="field in displayFields"
              :key="field.sourceField"
              :label="field.sourceField"
              min-width="100"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ row[field.sourceField] }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 导入确认 -->
        <div class="confirm-section">
          <el-alert
            title="确认导入后，系统将执行以下操作："
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <ol>
                <li>在数据库中创建/更新数据表</li>
                <li>将验证通过的数据批量插入新表</li>
                <li>更新系统配置文件（表结构、字段映射）</li>
                <li>在导航菜单中创建对应的数据节点</li>
                <li>刷新系统界面，显示新导入的数据</li>
              </ol>
            </template>
          </el-alert>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <el-button @click="handlePrevious">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button
            type="primary"
            size="large"
            @click="handleImport"
            :loading="importing"
            :disabled="!canImport"
          >
            <el-icon><Upload /></el-icon>
            开始导入
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 导入进度弹窗 -->
    <el-dialog
      v-model="progressVisible"
      title="导入进度"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="progress-content">
        <el-steps :active="currentStep" direction="vertical">
          <el-step title="创建数据表" :status="getStepStatus(0)">
            <template #description>
              {{ stepDescriptions[0] }}
            </template>
          </el-step>
          <el-step title="插入数据" :status="getStepStatus(1)">
            <template #description>
              {{ stepDescriptions[1] }}
            </template>
          </el-step>
          <el-step title="更新配置" :status="getStepStatus(2)">
            <template #description>
              {{ stepDescriptions[2] }}
            </template>
          </el-step>
          <el-step title="更新导航" :status="getStepStatus(3)">
            <template #description>
              {{ stepDescriptions[3] }}
            </template>
          </el-step>
        </el-steps>

        <div v-if="importResult" class="import-result">
          <el-alert
            :title="importResult.message"
            :type="importResult.status === 'success' ? 'success' : 'error'"
            show-icon
            :closable="false"
          />
        </div>
      </div>

      <template #footer>
        <el-button
          v-if="importResult"
          type="primary"
          @click="handleComplete"
        >
          完成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 组件属性
const props = defineProps<{
  validatedData?: any[]
  fieldConfigs?: any[]
  moduleId?: string
  moduleName?: string
  tableName?: string
  fileName?: string
  chineseTitle?: string
  subModuleId?: string
  subModuleName?: string
  tableType?: string
  parentTable?: string
}>()

// 组件事件
const emit = defineEmits(['previous-step', 'import-complete'])

// 导入状态
const importing = ref(false)
const progressVisible = ref(false)
const currentStep = ref(0)
const stepDescriptions = ref(['等待开始...', '等待开始...', '等待开始...', '等待开始...'])
const importResult = ref<any>(null)
const importError = ref<string>('')

// 中文表名编辑状态
const editableChineseTitle = ref(props.chineseTitle || '')
const updatingTitle = ref(false)
const titleUpdateMessage = ref('')
const titleUpdateStatus = ref<'success' | 'error'>('success')

// 当前使用的中文表名（可能被修改过）
const currentChineseTitle = ref(props.chineseTitle || '')
const currentTableName = ref(props.tableName || '')

// 计算属性：是否可以导入
const canImport = computed(() => {
  return props.validatedData && props.validatedData.length > 0 &&
         props.fieldConfigs && props.fieldConfigs.length > 0 &&
         props.tableName && props.moduleId
})

// 计算属性：显示字段
const displayFields = computed(() => {
  return props.fieldConfigs?.slice(0, 5) || []
})

// 计算属性：预览数据
const previewData = computed(() => {
  return props.validatedData?.slice(0, 5).map((item: any) => item.data || item) || []
})

// 获取步骤状态
const getStepStatus = (step: number) => {
  if (currentStep.value > step) {
    return 'success'
  } else if (currentStep.value === step) {
    return 'process'
  }
  return 'wait'
}

// 处理上一步
const handlePrevious = () => {
  emit('previous-step')
}

// 处理导入
const handleImport = async () => {
  if (!canImport.value) {
    ElMessage.warning('数据不完整，无法导入')
    return
  }

  importing.value = true
  progressVisible.value = true
  currentStep.value = 0
  importResult.value = null

  try {
    // 准备导入数据
    const importData = props.validatedData?.map((item: any) => item.data || item) || []

    // 模拟步骤进度
    stepDescriptions.value[0] = '正在创建数据表和字典表...'
    currentStep.value = 0
    await sleep(500)

    stepDescriptions.value[0] = '数据表创建完成'
    stepDescriptions.value[1] = '正在插入数据...'
    currentStep.value = 1
    await sleep(500)

    // 转换字段配置格式（适配V3服务）
    const v3FieldConfigs = props.fieldConfigs?.map((config: any) => ({
      source_field: config.sourceField,
      target_field: config.targetField,
      data_type: config.dataType,
      length: config.length,
      link_to_dictionary: config.relation_type === 'to_dict',
      dictionary_table: config.relation_table,
      value_mapping: config.value_mapping
    })) || []

    // 调用finalize后端API（支持导航更新）
    const response = await fetch('/api/import/finalize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        table_name: props.tableName,
        field_configs: props.fieldConfigs,
        data: importData,
        module_id: props.moduleId,
        module_name: props.moduleName,
        file_name: props.fileName,
        chinese_title: currentChineseTitle.value || props.chineseTitle,
        sub_module_id: props.subModuleId,
        sub_module_name: props.subModuleName,
        table_type: props.tableType || 'master',
        parent_table: props.parentTable
      })
    })

    if (response.ok) {
      const result = await response.json()

      stepDescriptions.value[1] = `成功插入 ${result.inserted} 条数据`
      stepDescriptions.value[2] = '正在更新配置文件...'
      currentStep.value = 2
      await sleep(500)

      stepDescriptions.value[2] = '配置文件更新完成'
      stepDescriptions.value[3] = '正在更新导航菜单...'
      currentStep.value = 3
      await sleep(500)

      stepDescriptions.value[3] = '导航菜单更新完成'
      currentStep.value = 4

      importResult.value = {
        status: 'success',
        message: result.message
      }

      ElMessage.success('导入成功！')

      // 自动导出导入报告
      await exportImportReport(result)

      // 触发导入完成事件
      emit('import-complete', result)
    } else {
      const error = await response.json()
      throw new Error(error.detail || '导入失败')
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    importResult.value = {
      status: 'error',
      message: error.message || '导入失败'
    }
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 处理完成
const handleComplete = () => {
  progressVisible.value = false
}

// 导出导入报告
const exportImportReport = async (importResult: any) => {
  try {
    const reportData = {
      file_name: props.fileName,
      chinese_title: currentChineseTitle.value || props.chineseTitle,
      table_name: props.tableName,
      module_name: props.moduleName,
      total_count: props.validatedData?.length || 0,
      success_count: importResult.inserted || 0,
      error_count: (props.validatedData?.length || 0) - (importResult.inserted || 0),
      import_time: new Date().toISOString()
    }

    const response = await fetch('/api/import/export-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        report_data: reportData,
        file_name: props.chineseTitle || '导入报告'
      })
    })

    if (response.ok) {
      // 获取文件名
      const contentDisposition = response.headers.get('content-disposition')
      let fileName = '导入报告.xlsx'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/)
        if (match) {
          fileName = match[1]
        }
      }

      // 下载文件
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('导入报告已自动下载')
    }
  } catch (error) {
    console.error('导出导入报告失败:', error)
    ElMessage.warning('导入报告导出失败，但数据已成功导入')
  }
}

// 更新中文表名
const updateChineseTitle = async () => {
  if (!editableChineseTitle.value) {
    titleUpdateMessage.value = '中文表名不能为空'
    titleUpdateStatus.value = 'error'
    return
  }

  updatingTitle.value = true
  titleUpdateMessage.value = ''

  try {
    // 调用后端API检查新表名是否可用
    const response = await fetch('/api/import/check-table-name', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        chinese_name: editableChineseTitle.value,
        field_configs: props.fieldConfigs || [],
        table_type: props.tableType || 'master'
      })
    })

    if (response.ok) {
      const result = await response.json()

      if (result.status === 'new_table' || result.status === 'name_conflict') {
        // 表名可用，更新当前使用的表名
        currentChineseTitle.value = editableChineseTitle.value
        if (result.english_name) {
          currentTableName.value = result.english_name
        }
        titleUpdateMessage.value = '表名已更新，可以重新导入'
        titleUpdateStatus.value = 'success'
        importError.value = '' // 清除错误信息
      } else if (result.status === 'existing') {
        titleUpdateMessage.value = '该表名已存在，请使用其他名称'
        titleUpdateStatus.value = 'error'
      } else if (result.status === 'structure_mismatch') {
        titleUpdateMessage.value = '该表名已存在但结构不同，请使用其他名称'
        titleUpdateStatus.value = 'error'
      }
    } else {
      const error = await response.json()
      titleUpdateMessage.value = error.detail || '检查表名失败'
      titleUpdateStatus.value = 'error'
    }
  } catch (error: any) {
    console.error('更新表名失败:', error)
    titleUpdateMessage.value = error.message || '更新表名失败'
    titleUpdateStatus.value = 'error'
  } finally {
    updatingTitle.value = false
  }
}

// 辅助函数：延迟
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
</script>

<style scoped>
.confirm-import-panel {
  padding: 20px;
}

.panel-card {
  min-height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.summary-section h3,
.fields-preview-section h3,
.data-preview-section h3 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.confirm-section {
  margin-top: 10px;
}

.confirm-section ol {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.confirm-section li {
  margin: 5px 0;
  color: #606266;
}

.action-section {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.progress-content {
  padding: 20px;
}

.import-result {
  margin-top: 20px;
}
</style>
