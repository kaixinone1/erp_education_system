<template>
  <div class="yearly-summary">
    <el-dialog
      v-model="visible"
      title="绩效工资年度汇总表"
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
          <h2 class="report-title">绩效工资年度汇总表</h2>
          <div class="report-info">
            <span>填报单位：{{ reportData.填报单位 }}</span>
            <span>年度：{{ currentYear }}年</span>
          </div>
        </div>

        <!-- 数据表格 -->
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-position">岗位</th>
              <th class="col-count">年度总人数</th>
              <th class="col-standard">月工资标准</th>
              <th class="col-subtotal">年度总金额</th>
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
              <td class="col-count">{{ yearlyData[level.countKey] || 0 }}</td>
              <td class="col-standard">{{ level.defaultStd }}</td>
              <td class="col-subtotal">{{ calculateYearlyAmount(level.countKey, level.defaultStd) }}</td>
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
              <td class="col-count">{{ yearlyData[level.countKey] || 0 }}</td>
              <td class="col-standard">{{ level.defaultStd }}</td>
              <td class="col-subtotal">{{ calculateYearlyAmount(level.countKey, level.defaultStd) }}</td>
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
              <td class="col-count">{{ yearlyData[level.countKey] || 0 }}</td>
              <td class="col-standard">{{ level.defaultStd }}</td>
              <td class="col-subtotal">{{ calculateYearlyAmount(level.countKey, level.defaultStd) }}</td>
            </tr>

            <!-- 乡镇补贴 -->
            <tr class="special-row">
              <td class="col-position">乡镇补贴</td>
              <td class="col-count">{{ yearlyData['在职人数'] || 0 }}</td>
              <td class="col-standard">350</td>
              <td class="col-subtotal">{{ (yearlyData['乡镇补贴合计'] || 0) }}</td>
            </tr>

            <!-- 岗位设置遗留 -->
            <tr class="special-row">
              <td class="col-position">岗位设置遗留</td>
              <td class="col-count">{{ yearlyData['遗留问题人数'] || 0 }}</td>
              <td class="col-standard"></td>
              <td class="col-subtotal">{{ yearlyData['遗留问题金额'] || 0 }}</td>
            </tr>

            <!-- 遗留人员明细 -->
            <tr v-for="person in legacyPersons" :key="person.name" class="legacy-row">
              <td class="col-position indent">{{ person.name }}</td>
              <td class="col-count">{{ person.months }}</td>
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

        <!-- 汇总说明 -->
        <div class="summary-note">
          <p><strong>汇总说明：</strong>{{ summaryNote }}</p>
          <p class="months-detail">已汇总月份：{{ monthsList }}</p>
        </div>

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
          <el-button @click="visible = false">关闭</el-button>
          <el-button type="primary" :loading="loading" @click="refreshData">
            刷新数据
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
const currentYear = ref(new Date().getFullYear())
const yearlyData = ref<Record<string, number>>({})
const summaryNote = ref('')
const months = ref<number[]>([])

// 遗留人员示例数据
const legacyPersons = ref([
  { name: '李法金', months: 12, amount: 3855.6 },
  { name: '张照凯', months: 12, amount: 4247.28 },
])

// 岗位级别配置
const adminLevels = [
  { key: '副处级', label: '1、副处级', countKey: '副处级人数', defaultStd: 0 },
  { key: '正科级', label: '2、正科级', countKey: '正科级人数', defaultStd: 0 },
  { key: '副科级', label: '3、副科级', countKey: '副科级人数', defaultStd: 0 },
  { key: '科员级', label: '4、科员级', countKey: '科员级人数', defaultStd: 1185 },
  { key: '办事员级', label: '5、办事员级', countKey: '办事员级人数', defaultStd: 0 },
]

const teacherLevels = [
  { key: '正高级教师', label: '1、正高级教师', countKey: '正高级教师人数', defaultStd: 1862 },
  { key: '高级教师', label: '2、高级教师', countKey: '高级教师人数', defaultStd: 1523 },
  { key: '一级教师', label: '3、一级教师', countKey: '一级教师人数', defaultStd: 1309 },
  { key: '二级教师', label: '4、二级教师', countKey: '二级教师人数', defaultStd: 1241 },
  { key: '三级教师', label: '5、三级教师', countKey: '三级教师人数', defaultStd: 1128 },
]

const workerLevels = [
  { key: '高级技师', label: '1、高级技师', countKey: '高级技师人数', defaultStd: 0 },
  { key: '技师', label: '2、技师', countKey: '技师人数', defaultStd: 1331 },
  { key: '高级工', label: '3、高级工', countKey: '高级工人数', defaultStd: 1219 },
  { key: '中级工', label: '4、中级工', countKey: '中级工人数', defaultStd: 1185 },
  { key: '初级工', label: '5、初级工', countKey: '初级工人数', defaultStd: 1106 },
  { key: '普工', label: '6、普工', countKey: '普工人数', defaultStd: 1106 },
]

// 报表数据
const reportData = reactive({
  填报单位: '太平中心学校',
  年度: currentYear.value,
  备注: ''
})

// 已汇总月份列表
const monthsList = computed(() => {
  if (months.value.length === 0) return '无'
  return months.value.map(m => `${m}月`).join('、')
})

// 计算年度金额（人数 × 标准 × 12个月）
const calculateYearlyAmount = (countKey: string, std: number) => {
  const count = yearlyData.value[countKey] || 0
  // 年度总金额 = 月度人数总和 × 标准
  return count * std
}

// 计算年度总人数
const calculateTotalCount = () => {
  const allLevels = [...adminLevels, ...teacherLevels, ...workerLevels]
  let total = 0
  allLevels.forEach(level => {
    total += yearlyData.value[level.countKey] || 0
  })
  // 加上遗留人数
  total += yearlyData.value['遗留问题人数'] || 0
  return total
}

// 计算年度总金额
const calculateTotalAmount = () => {
  const allLevels = [...adminLevels, ...teacherLevels, ...workerLevels]
  let total = 0
  allLevels.forEach(level => {
    total += calculateYearlyAmount(level.countKey, level.defaultStd)
  })
  // 加上乡镇补贴和遗留金额
  total += yearlyData.value['乡镇补贴合计'] || 0
  total += yearlyData.value['遗留问题金额'] || 0
  return total
}

// 打开报表
const open = async () => {
  visible.value = true
  await refreshData()
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  
  try {
    const response = await fetch(`/api/performance-pay-approval/yearly-summary?year=${currentYear.value}`)
    
    if (!response.ok) {
      throw new Error('加载数据失败')
    }
    
    const result = await response.json()
    
    if (result.status === 'success') {
      yearlyData.value = result.data || {}
      summaryNote.value = result.summary_note || ''
      months.value = result.months || []
      currentYear.value = result.year || new Date().getFullYear()
    } else {
      throw new Error(result.message || '加载数据失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 导出
const handleExport = async (format: string) => {
  if (format === 'print') {
    window.print()
    return
  }
  
  try {
    const exportData = {
      ...yearlyData.value,
      填报单位: reportData.填报单位,
      年度: currentYear.value,
      备注: reportData.备注,
      summary_note: summaryNote.value,
      months: months.value
    }
    
    const response = await fetch(`/api/performance-pay-approval/export-yearly?format=${format}&year=${currentYear.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(exportData)
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
    
    link.download = `绩效工资年度汇总表_${currentYear.value}年.${extensions[format]}`
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

.summary-note {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.summary-note p {
  margin: 5px 0;
}

.months-detail {
  color: #666;
  font-size: 13px;
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
  .dialog-footer {
    display: none;
  }
}
</style>
