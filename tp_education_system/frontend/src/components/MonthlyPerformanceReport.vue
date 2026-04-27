<template>
  <div class="monthly-report">
    <el-dialog
      v-model="visible"
      title="绩效工资月报表"
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="20" animated />
      </div>

      <div v-else class="report-content">
        <!-- 报表头部 -->
        <div class="report-header">
          <h2 class="report-title">绩效工资月报表</h2>
          <div class="report-info">
            <span>填报单位：{{ reportData.填报单位 }}</span>
            <span>年月：{{ reportData.年月 }}</span>
          </div>
        </div>

        <!-- 数据表格 -->
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-position">岗位</th>
              <th class="col-count">人数</th>
              <th class="col-standard">月工资标准</th>
              <th class="col-subtotal">小计</th>
            </tr>
          </thead>
          <tbody>
            <!-- 行政管理人员 -->
            <tr class="category-row">
              <td class="col-position">行政管理人员</td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr v-for="level in adminLevels" :key="level.key">
              <td class="col-position indent">{{ level.label }}</td>
              <td class="col-count">
                <el-input v-model="reportData[level.countKey]" size="small" class="cell-input" />
              </td>
              <td class="col-standard">{{ reportData[level.stdKey] || level.defaultStd }}</td>
              <td class="col-subtotal">{{ calculateSubtotal(level.countKey, level.stdKey, level.defaultStd) }}</td>
            </tr>

            <!-- 专业技术人员 -->
            <tr class="category-row">
              <td class="col-position">专业技术人员</td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr v-for="level in teacherLevels" :key="level.key">
              <td class="col-position indent">{{ level.label }}</td>
              <td class="col-count">
                <el-input v-model="reportData[level.countKey]" size="small" class="cell-input" />
              </td>
              <td class="col-standard">{{ reportData[level.stdKey] || level.defaultStd }}</td>
              <td class="col-subtotal">{{ calculateSubtotal(level.countKey, level.stdKey, level.defaultStd) }}</td>
            </tr>

            <!-- 工人 -->
            <tr class="category-row">
              <td class="col-position">工人</td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr v-for="level in workerLevels" :key="level.key">
              <td class="col-position indent">{{ level.label }}</td>
              <td class="col-count">
                <el-input v-model="reportData[level.countKey]" size="small" class="cell-input" />
              </td>
              <td class="col-standard">{{ reportData[level.stdKey] || level.defaultStd }}</td>
              <td class="col-subtotal">{{ calculateSubtotal(level.countKey, level.stdKey, level.defaultStd) }}</td>
            </tr>

            <!-- 乡镇补贴 -->
            <tr class="special-row">
              <td class="col-position">乡镇补贴</td>
              <td class="col-count">{{ reportData.在职人数 || 0 }}</td>
              <td class="col-standard">{{ reportData.乡镇补贴标准 || 350 }}</td>
              <td class="col-subtotal">{{ calculateTownshipSubsidy() }}</td>
            </tr>

            <!-- 岗位设置遗留 -->
            <tr class="special-row">
              <td class="col-position">岗位设置遗留</td>
              <td class="col-count">{{ reportData.遗留问题人数 || 0 }}</td>
              <td class="col-standard"></td>
              <td class="col-subtotal">{{ reportData.遗留问题金额 || 0 }}</td>
            </tr>

            <!-- 遗留人员明细 -->
            <tr v-for="person in legacyPersons" :key="person.name" class="legacy-row">
              <td class="col-position indent">{{ person.name }}</td>
              <td class="col-count">1</td>
              <td class="col-standard"></td>
              <td class="col-subtotal">{{ person.amount }}</td>
            </tr>

            <!-- 合计 -->
            <tr class="total-row">
              <td class="col-position">合计</td>
              <td class="col-count">{{ calculateTotalCount() }}</td>
              <td class="col-standard"></td>
              <td class="col-subtotal">{{ calculateTotalAmount() }}</td>
            </tr>
          </tbody>
        </table>

        <!-- 备注 -->
        <div class="remark-section">
          <span class="remark-label">备注：</span>
          <el-input
            v-model="reportData.备注"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
            class="remark-input"
          />
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visible = false">取消</el-button>
          <el-button type="success" :loading="loadingData" @click="handleLoadData">
            从数据库加载
          </el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存
          </el-button>
          <el-dropdown @command="handleExport" split-button type="warning">
            导出
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
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

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const loadingData = ref(false)

// 当前年月
const now = new Date()
const currentYear = now.getFullYear()
const currentMonth = now.getMonth() + 1

// 岗位级别配置
const adminLevels = [
  { key: '副处级', label: '1、副处级', countKey: '副处级人数', stdKey: '副处级标准', defaultStd: 0 },
  { key: '正科级', label: '2、正科级', countKey: '正科级人数', stdKey: '正科级标准', defaultStd: 0 },
  { key: '副科级', label: '3、副科级', countKey: '副科级人数', stdKey: '副科级标准', defaultStd: 0 },
  { key: '科员级', label: '4、科员级', countKey: '科员级人数', stdKey: '科员级标准', defaultStd: 1185 },
  { key: '办事员级', label: '5、办事员级', countKey: '办事员级人数', stdKey: '办事员级标准', defaultStd: 0 },
]

const teacherLevels = [
  { key: '正高级教师', label: '1、正高级教师', countKey: '正高级教师人数', stdKey: '正高级教师标准', defaultStd: 1862 },
  { key: '高级教师', label: '2、高级教师', countKey: '高级教师人数', stdKey: '高级教师标准', defaultStd: 1523 },
  { key: '一级教师', label: '3、一级教师', countKey: '一级教师人数', stdKey: '一级教师标准', defaultStd: 1309 },
  { key: '二级教师', label: '4、二级教师', countKey: '二级教师人数', stdKey: '二级教师标准', defaultStd: 1241 },
  { key: '三级教师', label: '5、三级教师', countKey: '三级教师人数', stdKey: '三级教师标准', defaultStd: 1128 },
]

const workerLevels = [
  { key: '高级技师', label: '1、高级技师', countKey: '高级技师人数', stdKey: '高级技师标准', defaultStd: 0 },
  { key: '技师', label: '2、技师', countKey: '技师人数', stdKey: '技师标准', defaultStd: 1331 },
  { key: '高级工', label: '3、高级工', countKey: '高级工人数', stdKey: '高级工标准', defaultStd: 1219 },
  { key: '中级工', label: '4、中级工', countKey: '中级工人数', stdKey: '中级工标准', defaultStd: 1185 },
  { key: '初级工', label: '5、初级工', countKey: '初级工人数', stdKey: '初级工标准', defaultStd: 1106 },
  { key: '普工', label: '6、普工', countKey: '普工人数', stdKey: '普工标准', defaultStd: 1106 },
]

// 遗留人员示例数据
const legacyPersons = ref([
  { name: '李法金', amount: 321.3 },
  { name: '张照凯', amount: 353.94 },
])

// 报表数据
const reportData = reactive({
  填报单位: '太平中心学校',
  年月: `${currentYear}年${currentMonth}月`,
  
  // 行政管理人员
  副处级人数: 0, 副处级标准: 0,
  正科级人数: 0, 正科级标准: 0,
  副科级人数: 0, 副科级标准: 0,
  科员级人数: 0, 科员级标准: 1185,
  办事员级人数: 0, 办事员级标准: 0,
  
  // 专业技术人员
  正高级教师人数: 0, 正高级教师标准: 1862,
  高级教师人数: 0, 高级教师标准: 1523,
  一级教师人数: 0, 一级教师标准: 1309,
  二级教师人数: 0, 二级教师标准: 1241,
  三级教师人数: 0, 三级教师标准: 1128,
  
  // 工人
  高级技师人数: 0, 高级技师标准: 0,
  技师人数: 0, 技师标准: 1331,
  高级工人数: 0, 高级工标准: 1219,
  中级工人数: 0, 中级工标准: 1185,
  初级工人数: 0, 初级工标准: 1106,
  普工人数: 0, 普工标准: 1106,
  
  // 其他
  在职人数: 0,
  乡镇补贴标准: 350,
  遗留问题人数: 0,
  遗留问题金额: 0,
  遗留问题详情: '',
  
  // 备注
  备注: ''
})

// 计算小计
const calculateSubtotal = (countKey: string, stdKey: string, defaultStd: number) => {
  const count = Number(reportData[countKey] || 0)
  const std = Number(reportData[stdKey] || defaultStd)
  return count * std
}

// 计算乡镇补贴
const calculateTownshipSubsidy = () => {
  const count = Number(reportData.在职人数 || 0)
  const std = Number(reportData.乡镇补贴标准 || 350)
  return count * std
}

// 计算总人数
const calculateTotalCount = () => {
  const allLevels = [...adminLevels, ...teacherLevels, ...workerLevels]
  let total = 0
  allLevels.forEach(level => {
    total += Number(reportData[level.countKey] || 0)
  })
  // 加上遗留人数
  total += Number(reportData.遗留问题人数 || 0)
  return total
}

// 计算总金额
const calculateTotalAmount = () => {
  const allLevels = [...adminLevels, ...teacherLevels, ...workerLevels]
  let total = 0
  allLevels.forEach(level => {
    total += calculateSubtotal(level.countKey, level.stdKey, level.defaultStd)
  })
  // 加上乡镇补贴和遗留金额
  total += calculateTownshipSubsidy()
  total += Number(reportData.遗留问题金额 || 0)
  return total
}

// 打开报表
const open = async () => {
  visible.value = true
  loading.value = true
  
  try {
    // 尝试加载本月数据
    const response = await fetch(`/api/performance-pay-approval/current?year=${currentYear}&month=${currentMonth}`)
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success' && result.data) {
        Object.assign(reportData, result.data)
        // 解析遗留人员
        if (result.data.遗留问题详情) {
          parseLegacyPersons(result.data.遗留问题详情)
        }
      }
    }
  } catch (error) {
    console.log('加载数据失败', error)
  } finally {
    loading.value = false
  }
}

// 解析遗留人员信息
const parseLegacyPersons = (detail: string) => {
  // 格式：李法金：321.3 张照凯：353.94
  const persons = []
  const regex = /(\S+?)：(\d+\.?\d*)/g
  let match
  while ((match = regex.exec(detail)) !== null) {
    persons.push({
      name: match[1],
      amount: parseFloat(match[2])
    })
  }
  if (persons.length > 0) {
    legacyPersons.value = persons
  }
}

// 从数据库加载数据
const handleLoadData = async () => {
  loadingData.value = true
  
  try {
    const response = await fetch('/api/performance-pay-approval/load-from-database', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year: currentYear, month: currentMonth })
    })
    
    if (!response.ok) {
      throw new Error('加载数据失败')
    }
    
    const result = await response.json()
    
    if (result.status === 'success') {
      Object.assign(reportData, result.data)
      if (result.data.遗留问题详情) {
        parseLegacyPersons(result.data.遗留问题详情)
      }
      ElMessage.success('数据加载成功')
    } else {
      throw new Error(result.message || '加载数据失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loadingData.value = false
  }
}

// 保存
const handleSave = async () => {
  saving.value = true
  
  try {
    // 构建遗留问题详情
    const legacyDetail = legacyPersons.value.map(p => `${p.name}：${p.amount}`).join(' ')
    reportData.遗留问题详情 = legacyDetail
    reportData.遗留问题人数 = legacyPersons.value.length
    reportData.遗留问题金额 = legacyPersons.value.reduce((sum, p) => sum + p.amount, 0)
    
    const response = await fetch('/api/performance-pay-approval/save', {
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
  
  try {
    const response = await fetch(`/api/performance-pay-approval/export-monthly?format=${format}`, {
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
      excel: 'xlsx',
      pdf: 'pdf'
    }
    
    link.download = `绩效工资月报表_${reportData.年月}.${extensions[format]}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`已导出 ${format.toUpperCase()} 格式`)
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

defineExpose({
  open
})
</script>

<style scoped>
.loading-container {
  padding: 40px;
}

.report-content {
  font-family: '宋体', 'SimSun', serif;
  font-size: 14px;
}

.report-header {
  text-align: center;
  margin-bottom: 20px;
}

.report-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
}

.report-info {
  display: flex;
  justify-content: center;
  gap: 30px;
  color: #666;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #000;
}

.data-table th,
.data-table td {
  border: 1px solid #000;
  padding: 8px;
  text-align: center;
  height: 32px;
}

.data-table th {
  background: #f5f5f5;
  font-weight: bold;
}

.col-position {
  width: 40%;
  text-align: left;
}

.col-count,
.col-standard,
.col-subtotal {
  width: 20%;
}

.indent {
  padding-left: 20px;
}

.category-row {
  font-weight: bold;
  background: #fafafa;
}

.category-row td {
  font-weight: bold;
}

.special-row {
  background: #f0f9ff;
}

.special-row td {
  font-weight: 500;
}

.legacy-row {
  background: #fff;
}

.legacy-row td {
  color: #666;
}

.total-row {
  font-weight: bold;
  background: #f5f5f5;
}

.total-row td {
  font-weight: bold;
  font-size: 15px;
}

.cell-input {
  width: 100%;
}

.cell-input :deep(.el-input__inner) {
  padding: 0 4px;
  height: 28px;
  text-align: center;
}

.remark-section {
  margin-top: 20px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.remark-label {
  font-weight: bold;
  white-space: nowrap;
  padding-top: 8px;
}

.remark-input {
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media print {
  .dialog-footer,
  .cell-input :deep(.el-input__inner) {
    display: none;
  }
  
  .cell-input :deep(.el-input__inner) {
    border: none;
    background: transparent;
  }
}
</style>
