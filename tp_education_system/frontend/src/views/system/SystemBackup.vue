<template>
  <div class="system-backup">
    <div class="page-header">
      <h2>系统自动备份与更新管理</h2>
      <p class="subtitle">一键备份到本地和远程Git，检查更新，安装更新，回滚，错误报告</p>
    </div>

    <!-- 状态概览卡片 -->
    <el-row :gutter="16" class="status-row">
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">Git 状态</div>
          <div class="card-value">
            <el-tag :type="statusData.git_available ? 'success' : 'danger'" size="small">
              {{ statusData.git_available ? '已连接' : '未检测到' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">远程仓库</div>
          <div class="card-value">
            <el-tag :type="statusData.remote_configured ? 'success' : 'warning'" size="small">
              {{ statusData.remote_configured ? '已配置' : '未配置' }}
            </el-tag>
          </div>
          <div class="card-detail" v-if="statusData.remote_url">{{ statusData.remote_url }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">最后备份</div>
          <div class="card-value">{{ statusData.last_backup_time || '暂无' }}</div>
          <div class="card-detail" v-if="statusData.last_backup_file">{{ statusData.last_backup_file }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card" :class="{ 'update-available': statusData.remote_updates_available }">
          <div class="card-label">远程更新</div>
          <div class="card-value">
            <el-tag :type="statusData.remote_updates_available ? 'warning' : 'info'" size="small">
              {{ statusData.remote_updates_available ? `${statusData.remote_commits_behind} 个更新可用` : '已是最新' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 当前提交信息 -->
    <el-card shadow="hover" class="commit-card" v-if="statusData.latest_commit">
      <div class="commit-info">
        <span class="commit-label">当前版本：</span>
        <el-tag type="info" size="small">{{ statusData.latest_commit }}</el-tag>
        <span class="commit-time">{{ statusData.latest_commit_time }}</span>
        <span class="commit-msg">{{ statusData.latest_commit_message }}</span>
        <el-tag v-if="statusData.uncommitted_changes" type="warning" size="small" style="margin-left: 8px">有未提交变更</el-tag>
        <el-tag v-if="statusData.unpushed_commits > 0" type="danger" size="small" style="margin-left: 8px">{{ statusData.unpushed_commits }} 个未推送</el-tag>
      </div>
    </el-card>

    <!-- 操作按钮区 -->
    <el-card shadow="hover" class="action-card">
      <template #header>
        <span class="card-title">备份与更新操作</span>
      </template>
      <div class="action-buttons">
        <el-button type="primary" :icon="Upload" @click="handleCreateBackup" :loading="backupLoading" size="large">
          <span v-if="!backupLoading">一键备份（本地+远程）</span>
          <span v-else>正在备份中...</span>
        </el-button>
        <el-button type="success" :icon="Search" @click="handleCheckUpdates" :loading="checkLoading">
          检查更新
        </el-button>
        <el-button type="warning" :icon="Download" @click="handlePullUpdates" :loading="pullLoading"
          :disabled="!statusData.remote_updates_available">
          安装更新
        </el-button>
        <el-button type="danger" :icon="RefreshLeft" @click="handleRollback" :loading="rollbackLoading">
          回滚上一版本
        </el-button>
        <el-button type="info" :icon="WarningFilled" @click="showErrorDialog = true"
          :disabled="!statusData.remote_updates_available">
          反馈错误报告
        </el-button>
      </div>
    </el-card>

    <!-- 操作日志 -->
    <el-card shadow="hover" class="log-card" v-if="operationLog.length > 0">
      <template #header>
        <span class="card-title">操作日志</span>
        <el-button type="text" size="small" @click="operationLog = []" style="float: right">清空</el-button>
      </template>
      <div v-for="(log, idx) in operationLog" :key="idx" class="log-item" :class="log.type">
        <span class="log-time">{{ log.time }}</span>
        <span class="log-msg">{{ log.message }}</span>
      </div>
    </el-card>

    <!-- 备份历史 -->
    <el-card shadow="hover" class="history-card">
      <template #header>
        <span class="card-title">备份历史</span>
        <el-button type="text" size="small" @click="loadHistory" style="float: right">刷新</el-button>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Git 提交历史" name="git">
          <el-table :data="historyData.git_history" style="width: 100%" size="small" max-height="400">
            <el-table-column prop="commit_hash" label="提交哈希" width="100" />
            <el-table-column prop="commit_time" label="提交时间" width="180" />
            <el-table-column prop="commit_message" label="提交信息" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="数据库备份文件" name="db">
          <el-table :data="historyData.backup_files" style="width: 100%" size="small" max-height="400">
            <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
            <el-table-column prop="file_size_mb" label="大小(MB)" width="100" />
            <el-table-column prop="backup_time" label="备份时间" width="180" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="danger" size="small" @click="handleRestoreDb(scope.row.file_name)">恢复</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 错误报告对话框 -->
    <el-dialog v-model="showErrorDialog" title="反馈错误报告" width="500px">
      <el-form label-width="80px">
        <el-form-item label="更新版本">
          <el-input v-model="errorForm.更新版本" placeholder="出错的更新版本号" />
        </el-form-item>
        <el-form-item label="错误描述">
          <el-input v-model="errorForm.误差描述" type="textarea" :rows="5"
            placeholder="请详细描述更新后出现的错误..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showErrorDialog = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateErrorReport" :loading="errorLoading">生成并发送报告</el-button>
      </template>
    </el-dialog>

    <!-- 更新确认对话框 -->
    <el-dialog v-model="showUpdateConfirm" title="确认安装更新" width="500px">
      <p>将安装以下更新：</p>
      <div v-for="(update, idx) in updateLog" :key="idx" class="update-item">
        {{ update }}
      </div>
      <el-alert type="warning" title="安装更新后需要重启后端服务才能生效" :closable="false" show-icon
        style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showUpdateConfirm = false">取消</el-button>
        <el-button type="primary" @click="confirmPullUpdates">确认安装</el-button>
      </template>
    </el-dialog>

    <!-- 回滚确认对话框 -->
    <el-dialog v-model="showRollbackConfirm" title="确认回滚" width="400px">
      <el-alert type="error" title="回滚将撤销最近一次提交的代码变更" :closable="false" show-icon />
      <p style="margin-top: 12px">回滚后需要重启后端服务才能生效。确定要继续吗？</p>
      <template #footer>
        <el-button @click="showRollbackConfirm = false">取消</el-button>
        <el-button type="danger" @click="confirmRollback">确认回滚</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Upload, Search, Download, RefreshLeft, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 状态数据
const statusData = reactive({
  git_available: false,
  remote_configured: false,
  remote_url: '',
  current_branch: '',
  latest_commit: '',
  latest_commit_time: '',
  latest_commit_message: '',
  uncommitted_changes: false,
  unpushed_commits: 0,
  last_backup_time: '',
  last_backup_file: '',
  remote_updates_available: false,
  remote_commits_behind: 0,
})

// 加载状态
const backupLoading = ref(false)
const checkLoading = ref(false)
const pullLoading = ref(false)
const rollbackLoading = ref(false)
const errorLoading = ref(false)

// 操作日志
const operationLog = ref<Array<{ time: string; message: string; type: string }>>([])

// 历史数据
const historyData = reactive({
  git_history: [] as any[],
  backup_files: [] as any[],
})
const activeTab = ref('git')

// 更新相关
const showUpdateConfirm = ref(false)
const showRollbackConfirm = ref(false)
const updateLog = ref<string[]>([])

// 错误报告
const showErrorDialog = ref(false)
const errorForm = reactive({
  更新版本: '',
  误差描述: '',
})

// 添加日志
function addLog(message: string, type: string = 'info') {
  const now = new Date().toLocaleTimeString()
  operationLog.value.unshift({ time: now, message, type })
  if (operationLog.value.length > 50) operationLog.value.pop()
}

// 加载状态
async function loadStatus() {
  try {
    const res = await fetch('/api/system/backup/status')
    const data = await res.json()
    if (data.success) {
      Object.assign(statusData, data.data)
    }
  } catch (e: any) {
    addLog('获取状态失败: ' + e.message, 'error')
  }
}

// 加载历史
async function loadHistory() {
  try {
    const res = await fetch('/api/system/backup/history?limit=20')
    const data = await res.json()
    if (data.success) {
      historyData.git_history = data.git_history
      historyData.backup_files = data.backup_files
    }
  } catch (e: any) {
    addLog('获取历史失败: ' + e.message, 'error')
  }
}

// 一键备份
async function handleCreateBackup() {
  try {
    await ElMessageBox.confirm(
      '将执行以下操作：\n1. 备份 PostgreSQL 数据库\n2. Git 提交所有变更\n3. 推送到远程仓库\n\n确认继续？',
      '确认一键备份',
      { confirmButtonText: '确认备份', cancelButtonText: '取消', type: 'info' }
    )
  } catch {
    return
  }

  backupLoading.value = true
  addLog('开始一键备份...', 'info')
  try {
    const res = await fetch('/api/system/backup/create', { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      addLog('备份完成！数据库 + Git 提交 + 远程推送', 'success')
      ElMessage.success('备份完成！')
    } else {
      addLog('备份部分失败: ' + data.message, 'warning')
      if (data.details?.errors?.length) {
        data.details.errors.forEach((e: string) => addLog('  - ' + e, 'error'))
      }
      ElMessage.warning(data.message)
    }
  } catch (e: any) {
    addLog('备份失败: ' + e.message, 'error')
    ElMessage.error('备份失败')
  } finally {
    backupLoading.value = false
    await loadStatus()
    await loadHistory()
  }
}

// 检查更新
async function handleCheckUpdates() {
  checkLoading.value = true
  addLog('正在检查远程更新...', 'info')
  try {
    const res = await fetch('/api/system/backup/check-updates')
    const data = await res.json()
    if (data.success) {
      if (data.updates_available) {
        addLog(`发现 ${data.commits_behind} 个可用更新`, 'warning')
        updateLog.value = data.update_log
        ElMessage.warning(`发现 ${data.commits_behind} 个可用更新`)
      } else {
        addLog('系统已是最新版本', 'success')
        ElMessage.success('系统已是最新版本')
      }
      statusData.remote_updates_available = data.updates_available
      statusData.remote_commits_behind = data.commits_behind
    }
  } catch (e: any) {
    addLog('检查更新失败: ' + e.message, 'error')
    ElMessage.error('检查更新失败')
  } finally {
    checkLoading.value = false
  }
}

// 安装更新
async function handlePullUpdates() {
  updateLog.value = []
  try {
    const res = await fetch('/api/system/backup/check-updates')
    const data = await res.json()
    if (data.success && data.updates_available) {
      updateLog.value = data.update_log
      showUpdateConfirm.value = true
    } else {
      ElMessage.info('没有可用的更新')
    }
  } catch (e: any) {
    ElMessage.error('检查更新失败')
  }
}

async function confirmPullUpdates() {
  showUpdateConfirm.value = false
  pullLoading.value = true
  addLog('正在安装更新...', 'info')
  try {
    const res = await fetch('/api/system/backup/pull-updates', { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      addLog(data.message, 'success')
      ElMessage.success(data.message + '，请重启后端服务以应用更新')
    } else {
      addLog('更新失败', 'error')
      ElMessage.error('更新失败')
    }
  } catch (e: any) {
    addLog('更新失败: ' + e.message, 'error')
    ElMessage.error('更新失败')
  } finally {
    pullLoading.value = false
    await loadStatus()
    await loadHistory()
  }
}

// 回滚
function handleRollback() {
  showRollbackConfirm.value = true
}

async function confirmRollback() {
  showRollbackConfirm.value = false
  rollbackLoading.value = true
  addLog('正在回滚到上一版本...', 'warning')
  try {
    const res = await fetch('/api/system/backup/rollback', { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      addLog(data.message, 'success')
      ElMessage.success(data.message + '，请重启后端服务以应用回滚')
    } else {
      addLog('回滚失败', 'error')
      ElMessage.error('回滚失败')
    }
  } catch (e: any) {
    addLog('回滚失败: ' + e.message, 'error')
    ElMessage.error('回滚失败')
  } finally {
    rollbackLoading.value = false
    await loadStatus()
    await loadHistory()
  }
}

// 生成错误报告
async function handleGenerateErrorReport() {
  if (!errorForm.误差描述.trim()) {
    ElMessage.warning('请填写错误描述')
    return
  }
  errorLoading.value = true
  try {
    const res = await fetch('/api/system/backup/generate-error-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorForm),
    })
    const data = await res.json()
    if (data.success) {
      addLog('错误报告已生成: ' + data.report_file, 'warning')
      ElMessage.success('错误报告已生成，请发送给开发团队')
      showErrorDialog.value = false
      errorForm.误差描述 = ''
      errorForm.更新版本 = ''
    }
  } catch (e: any) {
    addLog('生成报告失败: ' + e.message, 'error')
    ElMessage.error('生成报告失败')
  } finally {
    errorLoading.value = false
  }
}

// 恢复数据库
async function handleRestoreDb(fileName: string) {
  try {
    await ElMessageBox.confirm(
      `确定要从备份文件 "${fileName}" 恢复数据库吗？\n此操作将覆盖当前数据库的所有数据！`,
      '确认恢复数据库',
      { confirmButtonText: '确认恢复', cancelButtonText: '取消', type: 'error' }
    )
  } catch {
    return
  }

  addLog(`正在从 ${fileName} 恢复数据库...`, 'warning')
  try {
    const res = await fetch('/api/system/backup/restore-db', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ backup_file: fileName }),
    })
    const data = await res.json()
    if (data.success) {
      addLog('数据库恢复成功', 'success')
      ElMessage.success('数据库恢复成功')
    } else {
      addLog('数据库恢复失败', 'error')
      ElMessage.error('数据库恢复失败')
    }
  } catch (e: any) {
    addLog('恢复失败: ' + e.message, 'error')
    ElMessage.error('恢复失败')
  }
}

onMounted(() => {
  loadStatus()
  loadHistory()
})
</script>

<style scoped>
.system-backup {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 22px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.status-row {
  margin-bottom: 16px;
}

.status-card {
  text-align: center;
}

.status-card .card-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.status-card .card-value {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.status-card .card-detail {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
  word-break: break-all;
}

.status-card.update-available {
  border-color: #e6a23c;
  background: #fdf6ec;
}

.commit-card {
  margin-bottom: 16px;
}

.commit-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 13px;
}

.commit-label {
  color: #909399;
}

.commit-time {
  color: #c0c4cc;
  font-size: 12px;
}

.commit-msg {
  color: #606266;
  margin-left: 4px;
}

.action-card {
  margin-bottom: 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.log-card {
  margin-bottom: 16px;
}

.log-item {
  padding: 4px 0;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.log-item .log-time {
  color: #c0c4cc;
  margin-right: 12px;
  font-family: monospace;
}

.log-item.success .log-msg { color: #67c23a; }
.log-item.error .log-msg { color: #f56c6c; }
.log-item.warning .log-msg { color: #e6a23c; }
.log-item.info .log-msg { color: #409eff; }

.history-card {
  margin-bottom: 16px;
}

.update-item {
  padding: 4px 0;
  font-family: monospace;
  font-size: 13px;
  color: #606266;
}
</style>