<template>
  <div class="backup-settings">
    <div class="page-header">
      <h2>数据库自动备份设置</h2>
      <p class="subtitle">每天自动备份数据库，一式三份保存到三个独立位置，备份失败时弹窗提醒</p>
    </div>

    <!-- 状态概览 -->
    <el-row :gutter="16" class="status-row">
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">上次备份时间</div>
          <div class="card-value">{{ backupStatus.last_backup_time || '暂无' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">上次备份结果</div>
          <div class="card-value">
            <el-tag v-if="backupStatus.last_backup_success === true" type="success">成功</el-tag>
            <el-tag v-else-if="backupStatus.last_backup_success === false" type="danger">失败</el-tag>
            <el-tag v-else type="info">暂无记录</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">连续失败次数</div>
          <div class="card-value">
            <span :style="{ color: backupStatus.consecutive_failures > 0 ? 'red' : 'green', fontSize: '24px' }">
              {{ backupStatus.consecutive_failures || 0 }}
            </span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <div class="card-label">备份状态</div>
          <div class="card-value">
            <el-switch v-model="config.enabled" active-text="启用" inactive-text="禁用" @change="saveConfig" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 备份路径配置 -->
    <el-card class="config-card">
      <template #header>
        <span>备份位置配置（一式三份）</span>
      </template>
      <div class="path-list">
        <div v-for="(path, index) in config.backup_paths" :key="index" class="path-item">
          <div class="path-label">备份位置{{ index + 1 }}</div>
          <div class="path-input-row">
            <el-input
              v-model="config.backup_paths[index]"
              :placeholder="'请选择备份位置' + (index + 1) + '的文件夹路径'"
              readonly
              style="flex: 1;"
            />
            <el-button type="primary" @click="selectFolder(index)" style="margin-left: 8px;">
              <el-icon><FolderOpened /></el-icon>
              选择文件夹
            </el-button>
            <el-button @click="config.backup_paths[index] = ''" :disabled="!config.backup_paths[index]">
              清除
            </el-button>
          </div>
          <div class="path-status">
            <el-tag v-if="!path" type="info" size="small">未配置</el-tag>
            <el-tag v-else-if="pathStatuses[index] === 'ok'" type="success" size="small">可写入</el-tag>
            <el-tag v-else-if="pathStatuses[index] === 'error'" type="danger" size="small">无法写入</el-tag>
            <el-tag v-else type="warning" size="small">待检测</el-tag>
          </div>
        </div>
      </div>
      <div style="margin-top: 16px;">
        <el-button type="primary" @click="saveConfig" :loading="saving">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
        <el-button @click="checkPaths">检测路径可写性</el-button>
      </div>
    </el-card>

    <!-- 备份设置 -->
    <el-card class="config-card">
      <template #header>
        <span>备份计划设置</span>
      </template>
      <el-form label-width="120px">
        <el-form-item label="每日备份时间">
          <el-time-picker
            v-model="backupTime"
            format="HH:mm"
            placeholder="选择时间"
            @change="onTimeChange"
          />
          <span style="margin-left: 10px; color: #909399;">每天此时自动备份数据库</span>
        </el-form-item>
        <el-form-item label="备份保留天数">
          <el-input-number v-model="config.keep_days" :min="7" :max="365" @change="saveConfig" />
          <span style="margin-left: 10px; color: #909399;">超过天数的备份文件自动清理</span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Git 仓库备份 -->
    <el-card class="config-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>Git 仓库备份（自动提交并推送至远程仓库）</span>
          <el-switch v-model="config.git_config.enabled" active-text="启用" inactive-text="禁用" @change="saveGitConfig" />
        </div>
      </template>
      <template v-if="config.git_config.enabled">
        <!-- Git仓库状态（自动检测，无需手动配置） -->
        <el-form label-width="120px">
          <el-form-item label="Git仓库状态">
            <el-tag v-if="gitRepoStatus === 'checking'" type="warning">检测中...</el-tag>
            <el-tag v-else-if="gitRepoStatus === 'valid'" type="success">
              有效仓库
              <span v-if="gitRepoInfo.remote_url"> | 远程: {{ gitRepoInfo.remote_url }}</span>
              <span v-if="gitRepoInfo.branch"> | 分支: {{ gitRepoInfo.branch }}</span>
            </el-tag>
            <el-tag v-else-if="gitRepoStatus === 'invalid'" type="danger">{{ gitRepoMessage }}</el-tag>
            <el-button size="small" @click="verifyGitRepo" :loading="verifyingGit" style="margin-left: 8px;">
              重新检测
            </el-button>
          </el-form-item>
          <el-form-item label="仓库路径">
            <el-input :model-value="gitRepoInfo.repo_path || '自动检测中...'" readonly />
            <span style="margin-left: 10px; color: #909399; font-size: 12px;">系统自动检测，无需手动配置</span>
          </el-form-item>
          <el-form-item label="远程仓库名">
            <el-input v-model="config.git_config.remote_name" placeholder="origin" style="width: 200px;" @change="saveGitConfig" />
          </el-form-item>
          <el-form-item label="推送分支">
            <el-input v-model="config.git_config.branch" placeholder="main" style="width: 200px;" @change="saveGitConfig" />
          </el-form-item>
          <el-form-item label="仓库内子目录">
            <el-input v-model="config.git_config.backup_subdir" placeholder="数据库备份" style="width: 200px;" @change="saveGitConfig" />
            <span style="margin-left: 10px; color: #909399;">备份文件在仓库中的存放目录</span>
          </el-form-item>
        </el-form>
      </template>
    </el-card>

    <!-- 操作按钮 -->
    <div style="margin-top: 16px; text-align: center;">
      <el-button type="success" size="large" @click="runBackupNow" :loading="backingUp">
        <el-icon><Upload /></el-icon>
        立即备份
      </el-button>
    </div>

    <!-- 备份结果对话框 -->
    <el-dialog v-model="showResult" title="备份结果" width="550px">
      <div v-if="backupResult">
        <el-alert
          :title="backupResult.success ? '备份成功' : '备份失败'"
          :type="backupResult.success ? 'success' : 'error'"
          :closable="false"
          show-icon
        />
        <div v-if="backupResult.data" style="margin-top: 16px;">
          <div v-for="(r, i) in backupResult.data.results" :key="i" style="margin-bottom: 8px;">
            <el-tag v-if="r.skipped" type="info">{{ r.label }}：未配置路径</el-tag>
            <el-tag v-else-if="r.success" type="success">{{ r.label }}：备份成功</el-tag>
            <el-tag v-else type="danger">{{ r.label }}：{{ r.error }}</el-tag>
            <span v-if="r.file" style="margin-left: 8px; font-size: 12px; color: #909399;">{{ r.file }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showResult = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 备份失败弹窗（自动弹出） -->
    <el-dialog
      v-model="showFailureDialog"
      title="备份失败警告"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-alert
        title="以下备份位置无法完成备份，请修改备份路径！"
        type="error"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 16px;" v-for="(fd, i) in failedDetails" :key="i">
        <p style="font-weight: bold;">{{ fd.label }}：{{ fd.path }}</p>
        <el-button type="primary" size="small" @click="fixFailedPath(fd.index); showFailureDialog = false">
          选择新位置
        </el-button>
      </div>
      <template #footer>
        <el-button @click="acknowledgeFailure">已知晓</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, FolderOpened, Upload } from '@element-plus/icons-vue'
import axios from 'axios'

const API = axios.create({ baseURL: 'http://localhost:8000' })

const config = reactive({
  backup_paths: ['', '', ''],
  backup_time: '01:00',
  keep_days: 30,
  enabled: true,
  git_config: {
    enabled: false,
    remote_name: 'origin',
    branch: 'main',
    backup_subdir: '数据库备份',
  },
})

const backupTime = ref(new Date(2024, 0, 1, 1, 0))
const saving = ref(false)
const backingUp = ref(false)
const showResult = ref(false)
const showFailureDialog = ref(false)
const backupResult = ref(null)
const backupStatus = reactive({
  last_backup_time: null,
  last_backup_success: null,
  consecutive_failures: 0,
  has_failure: false,
})
const failedDetails = ref([])
const pathStatuses = ref({})
const verifyingGit = ref(false)
const gitRepoStatus = ref('unknown')  // 'unknown' | 'checking' | 'valid' | 'invalid'
const gitRepoInfo = ref({})
const gitRepoMessage = ref('')

let statusTimer = null

async function loadConfig() {
  try {
    const res = await API.get('/api/backup-config/config')
    if (res.data.success) {
      Object.assign(config, res.data.data)
      // 解析时间
      const [h, m] = (config.backup_time || '01:00').split(':')
      backupTime.value = new Date(2024, 0, 1, parseInt(h), parseInt(m))
    }
  } catch (e) {
    console.error('加载配置失败:', e)
  }
}

async function loadStatus() {
  try {
    const res = await API.get('/api/backup-config/status')
    if (res.data.success) {
      Object.assign(backupStatus, res.data.data)
      if (res.data.data.has_failure) {
        failedDetails.value = res.data.data.failed_details || []
        showFailureDialog.value = true
      }
    }
  } catch (e) {
    console.error('加载状态失败:', e)
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const res = await API.put('/api/backup-config/config', {
      backup_paths: config.backup_paths,
      backup_time: config.backup_time,
      keep_days: config.keep_days,
      enabled: config.enabled,
      git_config: config.git_config,
    })
    if (res.data.success) {
      ElMessage.success('配置已保存')
      await checkPaths()
    }
  } catch (e) {
    ElMessage.error('保存配置失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

function onTimeChange(val) {
  if (val) {
    const h = String(val.getHours()).padStart(2, '0')
    const m = String(val.getMinutes()).padStart(2, '0')
    config.backup_time = `${h}:${m}`
    saveConfig()
  }
}

async function selectFolder(index) {
  try {
    const res = await API.post('/api/select-folder', {
      current_path: config.backup_paths[index] || 'D:\\'
    })
    if (res.data.status === 'success' && res.data.selected_path) {
      config.backup_paths[index] = res.data.selected_path
      await saveConfig()
    }
  } catch (e) {
    ElMessage.error('选择文件夹失败')
  }
}

async function checkPaths() {
  for (let i = 0; i < config.backup_paths.length; i++) {
    const p = config.backup_paths[i]
    if (!p) {
      pathStatuses.value[i] = 'empty'
      continue
    }
    try {
      const res = await API.post('/api/backup-config/run')
      const results = res.data.data?.results || []
      const r = results.find(r => r.path === p)
      if (r) {
        pathStatuses.value[i] = r.success ? 'ok' : 'error'
      } else {
        pathStatuses.value[i] = 'unknown'
      }
    } catch {
      pathStatuses.value[i] = 'error'
    }
  }
}

async function runBackupNow() {
  backingUp.value = true
  try {
    const res = await API.post('/api/backup-config/run')
    backupResult.value = res.data
    showResult.value = true
    await loadStatus()
  } catch (e) {
    ElMessage.error('备份失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    backingUp.value = false
  }
}

async function acknowledgeFailure() {
  try {
    await API.post('/api/backup-config/acknowledge-failure')
    showFailureDialog.value = false
    await loadStatus()
  } catch (e) {
    console.error('确认失败:', e)
  }
}

function fixFailedPath(index) {
  selectFolder(index)
}

// Git 相关方法
async function saveGitConfig() {
  try {
    await API.put('/api/backup-config/git/config', {
      enabled: config.git_config.enabled,
      remote_name: config.git_config.remote_name,
      branch: config.git_config.branch,
      backup_subdir: config.git_config.backup_subdir,
    })
    ElMessage.success('Git备份配置已保存')
  } catch (e) {
    ElMessage.error('保存Git配置失败')
  }
}

async function loadGitStatus() {
  try {
    const res = await API.get('/api/backup-config/git/status')
    if (res.data.success) {
      const data = res.data.data
      gitRepoInfo.value = data
      if (data.is_git_repo && data.git_available) {
        gitRepoStatus.value = 'valid'
        // 自动填充远程仓库名和分支
        if (data.branch && !config.git_config.branch) {
          config.git_config.branch = data.branch
        }
      } else if (!data.git_available) {
        gitRepoStatus.value = 'invalid'
        gitRepoMessage.value = '未检测到Git，请确认Git已安装'
      } else {
        gitRepoStatus.value = 'invalid'
        gitRepoMessage.value = '当前项目不是Git仓库'
      }
    }
  } catch (e) {
    gitRepoStatus.value = 'invalid'
    gitRepoMessage.value = '获取Git状态失败'
  }
}

async function verifyGitRepo() {
  verifyingGit.value = true
  gitRepoStatus.value = 'checking'
  try {
    const res = await API.post('/api/backup-config/git/verify')
    if (res.data.success) {
      gitRepoStatus.value = 'valid'
      gitRepoInfo.value = res.data
      // 自动填充远程仓库名和分支
      if (res.data.current_branch && !config.git_config.branch) {
        config.git_config.branch = res.data.current_branch
      }
      if (res.data.remotes && Object.keys(res.data.remotes).length > 0) {
        const firstRemote = Object.keys(res.data.remotes)[0]
        config.git_config.remote_name = firstRemote
      }
      ElMessage.success('Git仓库验证成功')
    } else {
      gitRepoStatus.value = 'invalid'
      gitRepoMessage.value = res.data.message
    }
  } catch (e) {
    gitRepoStatus.value = 'invalid'
    gitRepoMessage.value = '验证失败: ' + (e.response?.data?.detail || e.message)
  } finally {
    verifyingGit.value = false
  }
}

onMounted(async () => {
  await loadConfig()
  await loadStatus()
  await loadGitStatus()
  // 每30秒轮询备份状态
  statusTimer = setInterval(loadStatus, 30000)
})

onUnmounted(() => {
  if (statusTimer) clearInterval(statusTimer)
})
</script>

<style scoped>
.backup-settings {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.subtitle {
  margin: 8px 0 0;
  color: #909399;
  font-size: 13px;
}

.status-row {
  margin-bottom: 16px;
}

.status-card {
  text-align: center;
}

.card-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.config-card {
  margin-bottom: 16px;
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.path-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.path-label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #303133;
}

.path-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.path-status {
  margin-top: 8px;
}
</style>