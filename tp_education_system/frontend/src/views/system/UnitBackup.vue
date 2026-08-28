<template>
  <div class="unit-backup">
    <div class="page-header">
      <h2>按单位数据备份与恢复</h2>
      <p class="subtitle">每个单位独立备份，恢复时只影响该单位数据，不影响其他单位</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="backupAllUnits" :loading="backingAll">
        <el-icon><Upload /></el-icon> 全部备份
      </el-button>
      <el-button @click="loadUnits" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
      <el-button @click="showLogs = true">
        <el-icon><Document /></el-icon> 操作日志
      </el-button>
    </div>

    <!-- 单位列表 -->
    <el-table :data="units" v-loading="loading" stripe style="margin-top: 16px;" max-height="520">
      <el-table-column prop="name" label="单位名称" min-width="200" />
      <el-table-column prop="teacher_count" label="教师数量" width="100" align="center">
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.teacher_count }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最近备份" width="180" align="center">
        <template #default="{ row }">
          <span v-if="row.last_backup" style="font-size: 13px;">{{ row.last_backup }}</span>
          <el-tag v-else type="warning" size="small">未备份</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="backupUnit(row)"
            :loading="row._backing"
            :disabled="row.teacher_count === 0"
          >
            备份
          </el-button>
          <el-button
            size="small"
            @click="showHistory(row)"
            :disabled="row.teacher_count === 0"
          >
            历史
          </el-button>
          <el-button
            type="warning"
            size="small"
            @click="prepareRestore(row)"
            :disabled="row.teacher_count === 0"
          >
            恢复
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 备份历史对话框 -->
    <el-dialog v-model="historyVisible" :title="`备份历史 - ${historyUnit}`" width="600px" destroy-on-close>
      <el-table :data="historyList" v-loading="historyLoading" max-height="400" stripe>
        <el-table-column prop="filename" label="备份文件" min-width="280" />
        <el-table-column label="文件大小" width="100" align="center">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="modified" label="备份时间" width="160" align="center" />
      </el-table>
      <template #footer>
        <el-button @click="historyVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 恢复确认对话框 -->
    <el-dialog v-model="restoreVisible" title="确认恢复数据" width="550px" destroy-on-close>
      <div v-if="restoreUnitName" class="restore-confirm">
        <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 16px;">
          <template #title>
            <strong>恢复操作将覆盖「{{ restoreUnitName }}」的当前数据！</strong>
          </template>
          <div style="margin-top: 8px; line-height: 1.8;">
            1. 系统会先自动备份当前数据（安全兜底）<br/>
            2. 然后从选定的备份文件恢复数据<br/>
            3. 其他单位的数据不受影响
          </div>
        </el-alert>

        <el-form label-width="100px">
          <el-form-item label="选择备份">
            <el-select v-model="restoreFile" placeholder="请选择备份文件" style="width: 100%;">
              <el-option
                v-for="h in restoreHistory"
                :key="h.filename"
                :label="`${h.filename} (${h.modified})`"
                :value="h.filename"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="确认输入">
            <div style="color: #e6a23c; margin-bottom: 4px; font-size: 13px;">
              请输入 <strong>确认恢复</strong> 以继续
            </div>
            <el-input
              v-model="restoreConfirm"
              placeholder="请输入「确认恢复」"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="restoreVisible = false">取消</el-button>
        <el-button
          type="danger"
          @click="doRestore"
          :loading="restoring"
          :disabled="!restoreFile || restoreConfirm !== '确认恢复'"
        >
          确认恢复
        </el-button>
      </template>
    </el-dialog>

    <!-- 操作日志对话框 -->
    <el-dialog v-model="showLogs" title="操作日志" width="700px" destroy-on-close>
      <el-table :data="logs" max-height="450" stripe>
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'backup' ? 'primary' : 'warning'" size="small">
              {{ row.type === 'backup' ? '备份' : '恢复' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" min-width="180" />
        <el-table-column label="结果" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="filename" label="文件" min-width="200" />
      </el-table>
      <template #footer>
        <el-button @click="showLogs = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, Document } from '@element-plus/icons-vue'
import axios from 'axios'

const API = '/api/unit-backup'

const units = ref([])
const loading = ref(false)
const backingAll = ref(false)

// 备份历史
const historyVisible = ref(false)
const historyUnit = ref('')
const historyList = ref([])
const historyLoading = ref(false)

// 恢复
const restoreVisible = ref(false)
const restoreUnitName = ref('')
const restoreHistory = ref([])
const restoreFile = ref('')
const restoreConfirm = ref('')
const restoring = ref(false)

// 操作日志
const showLogs = ref(false)
const logs = ref([])

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

async function loadUnits() {
  loading.value = true
  try {
    const res = await axios.get(`${API}/units`)
    const data = res.data.data || []
    // 为每个单位查询最近备份
    for (const unit of data) {
      unit._backing = false
      try {
        const hisRes = await axios.get(`${API}/history/${encodeURIComponent(unit.name)}`)
        const history = hisRes.data.data || []
        unit.last_backup = history.length > 0 ? history[0].modified : null
      } catch {
        unit.last_backup = null
      }
    }
    units.value = data
  } catch (e) {
    ElMessage.error('获取单位列表失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

async function backupUnit(unit) {
  unit._backing = true
  try {
    const res = await axios.post(`${API}/backup/${encodeURIComponent(unit.name)}`)
    if (res.data.success) {
      ElMessage.success(`「${unit.name}」备份成功: ${res.data.filename} (${formatSize(res.data.file_size)})`)
      await loadUnits()
    } else {
      ElMessage.warning(`「${unit.name}」: ${res.data.error || '备份失败'}`)
    }
  } catch (e) {
    ElMessage.error('备份失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    unit._backing = false
  }
}

async function backupAllUnits() {
  try {
    await ElMessageBox.confirm('确认备份所有单位？这将为每个有数据的单位创建独立备份文件。', '确认操作', {
      type: 'info',
      confirmButtonText: '开始备份',
    })
  } catch {
    return
  }

  backingAll.value = true
  try {
    const res = await axios.post(`${API}/backup-all`)
    const data = res.data
    ElMessage.success(`全部备份完成: ${data.success_count} 成功, ${data.failed_count} 失败`)
    await loadUnits()
  } catch (e) {
    ElMessage.error('全部备份失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    backingAll.value = false
  }
}

async function showHistory(unit) {
  historyUnit.value = unit.name
  historyVisible.value = true
  historyLoading.value = true
  try {
    const res = await axios.get(`${API}/history/${encodeURIComponent(unit.name)}`)
    historyList.value = res.data.data || []
  } catch (e) {
    ElMessage.error('获取备份历史失败')
    historyList.value = []
  } finally {
    historyLoading.value = false
  }
}

async function prepareRestore(unit) {
  restoreUnitName.value = unit.name
  restoreFile.value = ''
  restoreConfirm.value = ''
  restoreVisible.value = true
  try {
    const res = await axios.get(`${API}/history/${encodeURIComponent(unit.name)}`)
    restoreHistory.value = res.data.data || []
  } catch {
    restoreHistory.value = []
  }
}

async function doRestore() {
  if (!restoreFile.value || restoreConfirm.value !== '确认恢复') return

  restoring.value = true
  try {
    const res = await axios.post(`${API}/restore`, {
      unit_name: restoreUnitName.value,
      backup_filename: restoreFile.value,
    })
    if (res.data.success) {
      const safetyMsg = res.data.safety_backup ? `（安全备份: ${res.data.safety_backup}）` : ''
      ElMessage.success(`「${restoreUnitName.value}」恢复成功 ${safetyMsg}`)
      restoreVisible.value = false
      await loadUnits()
    } else {
      ElMessage.error('恢复失败: ' + (res.data.error || '未知错误'))
    }
  } catch (e) {
    ElMessage.error('恢复失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    restoring.value = false
  }
}

async function loadLogs() {
  try {
    const res = await axios.get(`${API}/logs?limit=50`)
    logs.value = res.data.data || []
  } catch {
    logs.value = []
  }
}

onMounted(() => {
  loadUnits()
  loadLogs()
})
</script>

<style scoped>
.unit-backup {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.action-bar {
  display: flex;
  gap: 8px;
}

.restore-confirm {
  line-height: 1.8;
}

:deep(.el-alert__title) {
  font-size: 14px;
}
</style>