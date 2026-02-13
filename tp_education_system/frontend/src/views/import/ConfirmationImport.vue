<template>
  <div class="confirmation-import-panel">
    <h3>第四步：确认导入</h3>
    <el-divider></el-divider>
    
    <!-- 导入配置概览 -->
    <div class="import-overview">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>导入配置概览</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="目标数据表">
            {{ targetTable }}
          </el-descriptions-item>
          <el-descriptions-item label="导入模式">
            <el-tag :type="importMode === 'insert' ? 'success' : importMode === 'update' ? 'warning' : 'info'">
              {{ importModeMap[importMode] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总记录数">
            {{ totalRows }}
          </el-descriptions-item>
          <el-descriptions-item label="有效记录数">
            <el-tag type="success">{{ validRows }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="无效记录数">
            <el-tag type="danger">{{ invalidRows }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="警告记录数">
            <el-tag type="warning">{{ warningRows }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="字段映射数" :span="2">
            {{ fieldMappingsCount }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
    
    <!-- 导入选项 -->
    <div class="import-options">
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>导入选项</span>
          </div>
        </template>
        <el-form :model="importOptions" label-width="120px">
          <el-form-item label="处理无效记录">
            <el-radio-group v-model="importOptions.handleInvalidRows">
              <el-radio label="skip">跳过无效记录</el-radio>
              <el-radio label="abort">遇到无效记录时中止</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="处理警告记录">
            <el-radio-group v-model="importOptions.handleWarningRows">
              <el-radio label="ignore">忽略警告</el-radio>
              <el-radio label="skip">跳过警告记录</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="是否备份现有数据">
            <el-switch v-model="importOptions.backupExistingData" />
            <span class="form-tip">（建议在导入大量数据时启用）</span>
          </el-form-item>
          
          <el-form-item label="导入后操作">
            <el-checkbox-group v-model="importOptions.postImportActions">
              <el-checkbox label="refresh">刷新数据列表</el-checkbox>
              <el-checkbox label="export">导出导入结果</el-checkbox>
              <el-checkbox label="notify">发送导入通知</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
    
    <!-- 导入进度 -->
    <div v-if="isImporting" class="import-progress">
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>导入进度</span>
          </div>
        </template>
        <div class="progress-content">
          <el-progress
            :percentage="importProgress"
            :status="importStatus"
            :stroke-width="15"
          />
          <div class="progress-info">
            <p>{{ importMessage }}</p>
            <p v-if="importDetails">
              <span>已处理: {{ importDetails.processed }}</span>
              <span>成功: {{ importDetails.success }}</span>
              <span>失败: {{ importDetails.failed }}</span>
            </p>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 导入结果 -->
    <div v-if="importResult" class="import-result">
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>导入结果</span>
          </div>
        </template>
        <div class="result-content" :class="importResult.success ? 'success' : 'error'">
          <el-result
            :icon="importResult.success ? 'success' : 'error'"
            :title="importResult.success ? '导入成功' : '导入失败'"
            :sub-title="importResult.message"
          >
            <template #extra>
              <div class="result-stats">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="stat-item">
                      <div class="stat-label">总处理数</div>
                      <div class="stat-value">{{ importResult.total || 0 }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item">
                      <div class="stat-label">成功导入</div>
                      <div class="stat-value" style="color: #67c23a;">{{ importResult.successCount || 0 }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item">
                      <div class="stat-label">导入失败</div>
                      <div class="stat-value" style="color: #f56c6c;">{{ importResult.failureCount || 0 }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item">
                      <div class="stat-label">耗时</div>
                      <div class="stat-value">{{ importResult.duration || '0' }}s</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
              <div class="result-actions">
                <el-button @click="handleViewDetails">查看详细报告</el-button>
                <el-button type="primary" @click="handleFinish">完成</el-button>
              </div>
            </template>
          </el-result>
        </div>
      </el-card>
    </div>
    
    <div class="panel-tip">
      <el-alert
        title="操作提示"
        type="info"
        :closable="false"
        show-icon
      >
        <ul>
          <li>请仔细检查导入配置和数据统计信息</li>
          <li>选择合适的导入选项，以确保数据导入的正确性</li>
          <li>导入过程中请勿关闭浏览器窗口</li>
          <li>导入完成后，系统会显示详细的导入结果</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

// 路由
const router = useRouter()

// 目标数据表
const targetTable = ref('教师信息表')

// 导入模式
const importMode = ref('insert')

// 导入模式映射
const importModeMap: Record<string, string> = {
  insert: '新增数据',
  update: '更新数据',
  upsert: '新增或更新'
}

// 数据统计
const totalRows = ref(30)
const validRows = ref(28)
const invalidRows = ref(2)
const warningRows = ref(1)

// 字段映射数
const fieldMappingsCount = ref(10)

// 导入选项
const importOptions = reactive({
  handleInvalidRows: 'skip', // skip: 跳过, abort: 中止
  handleWarningRows: 'ignore', // ignore: 忽略, skip: 跳过
  backupExistingData: true,
  postImportActions: ['refresh']
})

// 导入状态
const isImporting = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const importMessage = ref('准备导入...')
const importDetails = ref({
  processed: 0,
  success: 0,
  failed: 0
})

// 导入结果
const importResult = ref<any>(null)

// 处理开始导入
const handleStartImport = () => {
  isImporting.value = true
  importProgress.value = 0
  importStatus.value = ''
  importMessage.value = '开始导入数据...'
  importDetails.value = {
    processed: 0,
    success: 0,
    failed: 0
  }
  
  // 模拟导入过程
  simulateImportProcess()
}

// 模拟导入过程
const simulateImportProcess = () => {
  const total = totalRows.value
  let processed = 0
  let success = 0
  let failed = 0
  
  const interval = setInterval(() => {
    processed++
    
    // 模拟成功率
    if (Math.random() > 0.1) {
      success++
    } else {
      failed++
    }
    
    importProgress.value = Math.round((processed / total) * 100)
    importDetails.value = {
      processed,
      success,
      failed
    }
    
    // 更新导入消息
    if (importProgress.value < 30) {
      importMessage.value = '正在准备导入数据...'
    } else if (importProgress.value < 70) {
      importMessage.value = '正在导入数据...'
    } else if (importProgress.value < 90) {
      importMessage.value = '正在验证导入结果...'
    } else {
      importMessage.value = '正在完成导入过程...'
    }
    
    // 导入完成
    if (processed >= total) {
      clearInterval(interval)
      importStatus.value = success === total ? 'success' : 'warning'
      importMessage.value = '导入完成'
      
      // 设置导入结果
      importResult.value = {
        success: success > 0,
        message: `成功导入 ${success} 条记录，失败 ${failed} 条记录`,
        total: processed,
        successCount: success,
        failureCount: failed,
        duration: Math.round(Math.random() * 5 + 2) // 2-7秒
      }
      
      isImporting.value = false
    }
  }, 200)
}

// 处理查看详细报告
const handleViewDetails = () => {
  // 这里可以跳转到详细报告页面
  console.log('查看详细报告')
}

// 处理完成
const handleFinish = () => {
  // 跳转到数据管理页面
  router.push('/personnel/teacher')
}

// 导出数据供父组件使用
defineExpose({
  handleStartImport,
  importOptions,
  importResult
})
</script>

<style scoped>
.confirmation-import-panel {
  padding: 20px;
}

.import-overview {
  margin-bottom: 20px;
}

.import-options {
  margin-bottom: 20px;
}

.import-progress {
  margin-bottom: 20px;
}

.import-result {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-content {
  padding: 20px 0;
}

.progress-info {
  margin-top: 20px;
}

.progress-info p {
  margin: 5px 0;
}

.progress-info span {
  margin-right: 20px;
}

.result-content {
  padding: 20px 0;
}

.result-stats {
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.panel-tip {
  margin-top: 30px;
}
</style>
