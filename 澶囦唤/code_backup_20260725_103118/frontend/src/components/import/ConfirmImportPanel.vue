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
              {{ currentChineseTitle || chineseTitle || tableName }}
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
            type="warning"
            show-icon
            :closable="false"
            style="margin-bottom: 10px;"
          >
            <template #default>
              <div style="margin-top: 8px;">
                <p>该中文表名已存在，但字段结构与当前导入的数据不匹配。</p>
                
                <!-- 字段差异详情 -->
                <div v-if="fieldDiffResult" class="field-diff-detail" style="margin-top: 12px;">
                  <el-table :data="fieldDiffTable" border size="small" max-height="200px">
                    <el-table-column prop="category" label="类别" width="120" />
                    <el-table-column prop="field" label="字段" min-width="150" />
                    <el-table-column prop="detail" label="详情" min-width="200" />
                  </el-table>
                </div>
                
                <p style="margin-top: 10px;">请选择以下方式之一：</p>
                <div style="margin-top: 10px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                  <el-checkbox
                    v-model="forceOverwrite"
                    :disabled="importing"
                    style="margin-right: 8px;"
                  >
                    <span style="color: #e6a23c; font-weight: bold;">强制覆盖已有表</span>
                    <span style="color: #909399; font-size: 12px; margin-left: 4px;">（将删除旧表数据，使用新结构重建）</span>
                  </el-checkbox>
                </div>
                <p v-if="!forceOverwrite" style="margin-top: 8px; color: #909399;">或修改中文表名后重新导入：</p>
              </div>
            </template>
          </el-alert>
          <el-form v-if="!forceOverwrite" :inline="true">
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
            title="点击【开始导入】后，系统将先分析数据差异，再由您确认是否执行导入："
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <ol>
                <li>对比导入数据与数据库现有数据，精准识别每一条数据的变更类型</li>
                <li>展示分析报告：<strong>更新</strong>（数据有变化）、<strong>新增</strong>（全新记录）、<strong>插入</strong>（同标识符的新记录）、<strong>未变</strong>（数据无变化）</li>
                <li>由您确认后，再执行实际导入操作</li>
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
            @click="handleAnalyzeAndImport"
            :loading="analyzing"
            :disabled="!canImport"
          >
            <el-icon><Upload /></el-icon>
            开始导入
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据差异分析报告弹窗 -->
    <el-dialog
      v-model="analysisVisible"
      title="数据差异分析报告"
      width="800px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      top="5vh"
    >
      <div class="analysis-content">
        <!-- 分析摘要 -->
        <div class="analysis-summary">
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="stat-card stat-update">
                <div class="stat-number">{{ analysisResult?.更新 || 0 }}</div>
                <div class="stat-label">更新</div>
                <div class="stat-desc">数据有变化</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card stat-insert">
                <div class="stat-number">{{ analysisResult?.插入 || 0 }}</div>
                <div class="stat-label">插入</div>
                <div class="stat-desc">同标识符新记录</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card stat-new">
                <div class="stat-number">{{ analysisResult?.新增 || 0 }}</div>
                <div class="stat-label">新增</div>
                <div class="stat-desc">全新记录</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card stat-unchanged">
                <div class="stat-number">{{ analysisResult?.未变 || 0 }}</div>
                <div class="stat-label">未变</div>
                <div class="stat-desc">数据无变化</div>
              </div>
            </el-col>
          </el-row>

          <div class="analysis-meta" style="margin-top: 12px; color: #909399; font-size: 13px;">
            导入数据共 <strong>{{ analysisResult?.总计 || 0 }}</strong> 条，
            数据库现有 <strong>{{ analysisResult?.['数据库现有记录'] || 0 }}</strong> 条记录
          </div>
        </div>

        <!-- 变更明细表 -->
        <div v-if="analysisDetails.length > 0" class="analysis-details" style="margin-top: 20px;">
          <h4 style="margin-bottom: 10px; font-size: 14px; color: #606266;">
            变更明细
            <span v-if="analysisResult?.明细?.length >= 20" style="font-size: 12px; color: #909399;">
              （仅显示前20条）
            </span>
          </h4>
          <el-table
            :data="analysisDetails"
            style="width: 100%"
            max-height="350px"
            border
            size="small"
          >
            <el-table-column prop="行号" label="行号" width="60" align="center" />
            <el-table-column label="类型" width="80" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.类型 === '更新' ? 'warning' : row.类型 === '插入' ? 'primary' : 'success'"
                  size="small"
                >
                  {{ row.类型 }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="匹配键" label="匹配键" min-width="180" show-overflow-tooltip />
            <el-table-column label="变更详情" min-width="250">
              <template #default="{ row }">
                <div v-if="row.类型 === '更新' && row.变更字段">
                  <div
                    v-for="(change, idx) in row.变更字段"
                    :key="idx"
                    class="change-item"
                  >
                    <span class="change-field">{{ change.字段 }}：</span>
                    <span class="change-old">{{ change.原值 || '(空)' }}</span>
                    <el-icon style="margin: 0 4px;"><ArrowRight /></el-icon>
                    <span class="change-new">{{ change.新值 }}</span>
                  </div>
                </div>
                <span v-else-if="row.说明" class="change-desc">{{ row.说明 }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 无变更提示 -->
        <div v-if="analysisResult && analysisResult.更新 === 0 && analysisResult.插入 === 0 && analysisResult.新增 === 0" class="no-changes">
          <el-alert
            title="所有导入数据与数据库现有数据一致，无需导入。"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>

      <template #footer>
        <div class="analysis-footer">
          <el-button @click="handleCancelImport" :disabled="executingImport">
            取消导入
          </el-button>
          <el-button
            type="primary"
            @click="handleConfirmImport"
            :loading="executingImport"
            :disabled="analysisResult && analysisResult.更新 === 0 && analysisResult.插入 === 0 && analysisResult.新增 === 0"
          >
            <el-icon><Upload /></el-icon>
            确认导入
          </el-button>
        </div>
      </template>
    </el-dialog>

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
        <el-progress
          :percentage="importProgress"
          :status="importProgress === 100 ? 'success' : undefined"
          :stroke-width="20"
          :text-inside="true"
        />
        <div class="progress-text" style="margin-top: 16px; text-align: center; color: #606266;">
          {{ progressText }}
        </div>

        <div v-if="importResult" class="import-result">
          <el-alert
            :title="importResult.message"
            :type="importResult.status === 'success' ? 'success' : 'error'"
            show-icon
            :closable="false"
          />
          <div v-if="importResult.status === 'success'" class="result-stats" style="margin-top: 12px;">
            <el-row :gutter="12">
              <el-col :span="8">
                <div class="mini-stat">
                  <div class="mini-number">{{ importResult.updated || 0 }}</div>
                  <div class="mini-label">更新</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="mini-stat">
                  <div class="mini-number">{{ importResult.inserted || 0 }}</div>
                  <div class="mini-label">插入/新增</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="mini-stat">
                  <div class="mini-number">{{ importResult.errors || 0 }}</div>
                  <div class="mini-label">错误</div>
                </div>
              </el-col>
            </el-row>
          </div>
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
import { ArrowLeft, ArrowRight, Upload } from '@element-plus/icons-vue'
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

// ===== 导入状态 =====
const analyzing = ref(false)           // 正在分析数据差异
const executingImport = ref(false)     // 正在执行实际导入
const importing = computed(() => analyzing.value || executingImport.value)

// ===== 分析报告 =====
const analysisVisible = ref(false)
const analysisResult = ref<any>(null)

// 分析明细（格式化后的）
const analysisDetails = computed(() => {
  return analysisResult.value?.明细 || []
})

// ===== 导入进度 =====
const progressVisible = ref(false)
const importProgress = ref(0)
const progressText = ref('')
const importResult = ref<any>(null)

// ===== 错误处理 =====
const importError = ref<string>('')
const forceOverwrite = ref(false)
const fieldDiffResult = ref<any>(null)  // 字段差异报告

// 字段差异表格数据
const fieldDiffTable = computed(() => {
  if (!fieldDiffResult.value) return []
  const rows: any[] = []
  const diff = fieldDiffResult.value
  
  // 导入独有字段
  if (diff['导入独有字段'] && diff['导入独有字段'].length > 0) {
    diff['导入独有字段'].forEach((f: string) => {
      const importType = diff['导入字段类型']?.[f] || '未知'
      rows.push({ category: '导入独有', field: f, detail: `类型: ${importType}` })
    })
  }
  // 数据库独有字段
  if (diff['数据库独有字段'] && diff['数据库独有字段'].length > 0) {
    diff['数据库独有字段'].forEach((f: string) => {
      const dbType = diff['数据库字段类型']?.[f] || '未知'
      rows.push({ category: '数据库独有', field: f, detail: `类型: ${dbType}` })
    })
  }
  // 类型不一致字段
  if (diff['类型不一致字段']) {
    Object.entries(diff['类型不一致字段']).forEach(([field, types]: any) => {
      rows.push({ 
        category: '类型不一致', 
        field: field, 
        detail: `导入: ${types['导入类型']} → 数据库: ${types['数据库类型']}` 
      })
    })
  }
  return rows
})

// ===== 中文表名编辑 =====
const editableChineseTitle = ref(props.chineseTitle || '')
const updatingTitle = ref(false)
const titleUpdateMessage = ref('')
const titleUpdateStatus = ref<'success' | 'error'>('success')
const currentChineseTitle = ref(props.chineseTitle || '')
const currentTableName = ref(props.tableName || '')

// ===== 计算属性 =====
const canImport = computed(() => {
  return props.validatedData && props.validatedData.length > 0 &&
         props.fieldConfigs && props.fieldConfigs.length > 0 &&
         props.tableName && props.moduleId
})

const displayFields = computed(() => {
  return props.fieldConfigs?.slice(0, 5) || []
})

const previewData = computed(() => {
  return props.validatedData?.slice(0, 5).map((item: any) => item.data || item) || []
})

// ===== 事件处理 =====
const handlePrevious = () => {
  emit('previous-step')
}

// 核心流程：分析数据差异 → 展示报告 → 用户确认 → 执行导入
const handleAnalyzeAndImport = async () => {
  if (!canImport.value) {
    ElMessage.warning('数据不完整，无法导入')
    return
  }

  analyzing.value = true
  analysisResult.value = null

  try {
    const importData = props.validatedData?.map((item: any) => item.data || item) || []

    // 第一步：调用后端分析数据差异（analyze_only=true）
    const response = await fetch('/api/import/finalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: currentTableName.value || props.tableName,
        field_configs: props.fieldConfigs,
        data: importData,
        module_id: props.moduleId,
        module_name: props.moduleName,
        file_name: props.fileName,
        chinese_title: currentChineseTitle.value || props.chineseTitle,
        sub_module_id: props.subModuleId,
        sub_module_name: props.subModuleName,
        table_type: props.tableType || 'master',
        parent_table: props.parentTable,
        force_overwrite: forceOverwrite.value,
        analyze_only: true  // 关键：仅分析，不执行导入
      })
    })

    if (response.ok) {
      const result = await response.json()

      if (result.status === 'analyzed') {
        analysisResult.value = result.analysis
        analysisVisible.value = true
      } else if (result.status === 'field_diff_detected') {
        // 字段结构不一致，显示字段差异报告
        importError.value = `中文表名'${result.chinese_name || currentChineseTitle.value}'已存在，但表结构不一致`
        fieldDiffResult.value = result.field_diff
        ElMessage.warning('表结构不一致，请启用强制覆盖或修改中文表名')
      } else {
        // 可能是新表，没有分析结果，直接导入
        ElMessage.info('该表为新表，无需差异分析，直接执行导入')
        await executeRealImport(importData)
      }
    } else {
      const error = await response.json()
      throw new Error(error.detail || '分析数据差异失败')
    }
  } catch (error: any) {
    console.error('分析数据差异失败:', error)
    ElMessage.error(error.message || '分析数据差异失败')
  } finally {
    analyzing.value = false
  }
}

// 取消导入
const handleCancelImport = () => {
  analysisVisible.value = false
  analysisResult.value = null
  ElMessage.info('已取消导入')
}

// 确认导入：执行实际导入操作
const handleConfirmImport = async () => {
  const importData = props.validatedData?.map((item: any) => item.data || item) || []
  await executeRealImport(importData)
}

// 执行实际导入
const executeRealImport = async (importData: any[]) => {
  executingImport.value = true
  analysisVisible.value = false
  progressVisible.value = true
  importProgress.value = 0
  progressText.value = '正在执行导入...'
  importResult.value = null

  // 模拟进度动画
  const progressTimer = setInterval(() => {
    if (importProgress.value < 90) {
      importProgress.value += Math.random() * 15
      if (importProgress.value > 90) importProgress.value = 90
    }
  }, 500)

  try {
    const response = await fetch('/api/import/finalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: currentTableName.value || props.tableName,
        field_configs: props.fieldConfigs,
        data: importData,
        module_id: props.moduleId,
        module_name: props.moduleName,
        file_name: props.fileName,
        chinese_title: currentChineseTitle.value || props.chineseTitle,
        sub_module_id: props.subModuleId,
        sub_module_name: props.subModuleName,
        table_type: props.tableType || 'master',
        parent_table: props.parentTable,
        force_overwrite: forceOverwrite.value,
        analyze_only: false  // 关键：执行实际导入
      })
    })

    clearInterval(progressTimer)

    if (response.ok) {
      importProgress.value = 100
      progressText.value = '导入完成'

      const result = await response.json()
      importResult.value = {
        status: 'success',
        message: result.message || '数据导入成功',
        updated: result.updated || 0,
        inserted: result.inserted || 0,
        errors: result.errors || 0
      }

      ElMessage.success('导入成功！')

      // 自动导出导入报告
      await exportImportReport(result)

      // 触发导入完成事件
      emit('import-complete', result)
    } else {
      importProgress.value = 0
      progressText.value = '导入失败'

      const error = await response.json()
      throw new Error(error.detail || '导入失败')
    }
  } catch (error: any) {
    clearInterval(progressTimer)
    console.error('导入失败:', error)
    importProgress.value = 0
    progressText.value = '导入失败'
    importResult.value = {
      status: 'error',
      message: error.message || '导入失败'
    }
    ElMessage.error(error.message || '导入失败')
  } finally {
    executingImport.value = false
  }
}

// 处理完成
const handleComplete = () => {
  progressVisible.value = false
}

// 导出导入报告
const exportImportReport = async (result: any) => {
  try {
    const reportData = {
      file_name: props.fileName,
      chinese_title: currentChineseTitle.value || props.chineseTitle,
      table_name: currentTableName.value || props.tableName,
      module_name: props.moduleName,
      total_count: props.validatedData?.length || 0,
      success_count: (result.updated || 0) + (result.inserted || 0),
      error_count: result.errors || 0,
      import_time: new Date().toISOString()
    }

    const response = await fetch('/api/import/export-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        report_data: reportData,
        file_name: props.chineseTitle || '导入报告'
      })
    })

    if (response.ok) {
      const contentDisposition = response.headers.get('content-disposition')
      let fileName = '导入报告.xlsx'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/)
        if (match) {
          fileName = match[1]
        }
      }

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
    const response = await fetch('/api/import/check-table-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: editableChineseTitle.value,
        field_configs: props.fieldConfigs || [],
        table_type: props.tableType || 'master'
      })
    })

    if (response.ok) {
      const result = await response.json()

      if (result.status === 'new_table' || result.status === 'name_conflict') {
        currentChineseTitle.value = editableChineseTitle.value
        if (result.english_name) {
          currentTableName.value = result.english_name
        }
        titleUpdateMessage.value = '表名已更新，可以重新导入'
        titleUpdateStatus.value = 'success'
        importError.value = ''
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

/* ===== 分析报告样式 ===== */
.analysis-content {
  padding: 0;
}

.analysis-summary {
  margin-bottom: 8px;
}

.stat-card {
  text-align: center;
  padding: 16px 8px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  background: #fafafa;
}

.stat-card.stat-update {
  border-left: 4px solid #e6a23c;
  background: #fdf6ec;
}

.stat-card.stat-insert {
  border-left: 4px solid #409eff;
  background: #ecf5ff;
}

.stat-card.stat-new {
  border-left: 4px solid #67c23a;
  background: #f0f9eb;
}

.stat-card.stat-unchanged {
  border-left: 4px solid #909399;
  background: #f4f4f5;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-top: 4px;
}

.stat-desc {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.analysis-details h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.change-item {
  font-size: 12px;
  line-height: 1.6;
  display: flex;
  align-items: center;
  gap: 2px;
}

.change-field {
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
}

.change-old {
  color: #f56c6c;
  text-decoration: line-through;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.change-new {
  color: #67c23a;
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.change-desc {
  font-size: 12px;
  color: #909399;
}

.no-changes {
  margin-top: 20px;
}

.analysis-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* ===== 进度弹窗样式 ===== */
.progress-content {
  padding: 20px;
}

.import-result {
  margin-top: 20px;
}

.result-stats {
  margin-top: 12px;
}

.mini-stat {
  text-align: center;
  padding: 8px;
  border-radius: 6px;
  background: #f5f7fa;
}

.mini-number {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.mini-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* ===== 中文表名更新消息 ===== */
.update-message {
  margin-top: 8px;
  font-size: 13px;
}

.update-message.success {
  color: #67c23a;
}

.update-message.error {
  color: #f56c6c;
}
</style>