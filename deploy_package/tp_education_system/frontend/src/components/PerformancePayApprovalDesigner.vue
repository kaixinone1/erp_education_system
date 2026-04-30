<template>
  <div class="report-designer">
    <el-dialog
      v-model="visible"
      title="义务教育学校教职工绩效工资审批表"
      width="1350px"
      :close-on-click-modal="false"
      class="designer-dialog"
      destroy-on-close
    >
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="25" animated />
      </div>

      <div v-else class="report-container">
        <!-- A4纸张容器 -->
        <div class="a4-page">
          <!-- 标题区域 -->
          <table class="header-table">
            <tr>
              <td class="header-left"></td>
              <td class="header-month">{{ currentYearMonth }}</td>
              <td class="header-title" colspan="6">义务教育学校教职工绩效工资审批表</td>
              <td class="header-right"></td>
            </tr>
            <tr>
              <td class="info-label">填报单位：</td>
              <td class="info-value" colspan="3">
                <el-input v-model="reportData.填报单位" size="small" class="edit-input" />
              </td>
              <td class="info-label">填报时间:</td>
              <td class="info-value">{{ currentDate }}</td>
              <td class="info-label">单位：</td>
              <td class="info-value">人、元</td>
            </tr>
          </table>

          <!-- 主表格 -->
          <table class="main-table">
            <!-- 表头 -->
            <tr>
              <td class="col-project" rowspan="2">项  目</td>
              <td class="col-count" colspan="3">基础性工资</td>
              <td class="col-opinion" rowspan="5">呈报单位意见</td>
              <td class="col-opinion-content" colspan="6" rowspan="2">
                <div class="opinion-text">据实填写，同意呈报。</div>
              </td>
            </tr>
            <tr>
              <td class="col-count">人数</td>
              <td class="col-standard">月工资标准</td>
              <td class="col-subtotal">小计</td>
            </tr>

            <!-- 行政管理人员 -->
            <tr>
              <td class="row-header">行政管理人员</td>
              <td></td>
              <td></td>
              <td></td>
              <td colspan="6" rowspan="3" class="opinion-area">
                <div class="opinion-placeholder">（盖章）</div>
                <div class="opinion-date">{{ currentDate }}</div>
              </td>
            </tr>
            <tr>
              <td class="row-item">1、副处级</td>
              <td class="cell-center">
                <el-input v-model="reportData.副处级人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">
                <el-input v-model="reportData.副处级标准" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ calculateSubtotal('副处级') }}</td>
            </tr>
            <tr>
              <td class="row-item">2、正科级</td>
              <td class="cell-center">
                <el-input v-model="reportData.正科级人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">
                <el-input v-model="reportData.正科级标准" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ calculateSubtotal('正科级') }}</td>
            </tr>
            <tr>
              <td class="row-item">3、副科级</td>
              <td class="cell-center">
                <el-input v-model="reportData.副科级人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">
                <el-input v-model="reportData.副科级标准" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ calculateSubtotal('副科级') }}</td>
              <td class="col-opinion-bordered" rowspan="5">教育局意见</td>
              <td colspan="6" rowspan="5" class="opinion-area">
                <div class="opinion-placeholder">（盖章）</div>
                <div class="opinion-date">{{ nextDate }}</div>
              </td>
            </tr>
            <tr>
              <td class="row-item">4、科员级</td>
              <td class="cell-center">
                <el-input v-model="reportData.科员级人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.科员级标准 || 1185 }}</td>
              <td class="cell-center">{{ calculateSubtotal('科员级') }}</td>
            </tr>
            <tr>
              <td class="row-item">5、办事员级</td>
              <td class="cell-center">
                <el-input v-model="reportData.办事员级人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">
                <el-input v-model="reportData.办事员级标准" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ calculateSubtotal('办事员级') }}</td>
            </tr>

            <!-- 专业技术人员 -->
            <tr>
              <td class="row-header">专业技术人员</td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr>
              <td class="row-item">1、正高级教师</td>
              <td class="cell-center">
                <el-input v-model="reportData.正高级教师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.正高级教师标准 || 1862 }}</td>
              <td class="cell-center">{{ calculateSubtotal('正高级教师') }}</td>
            </tr>
            <tr>
              <td class="row-item">2、高级教师</td>
              <td class="cell-center">
                <el-input v-model="reportData.高级教师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.高级教师标准 || 1523 }}</td>
              <td class="cell-center">{{ calculateSubtotal('高级教师') }}</td>
              <td class="col-opinion-bordered" rowspan="12">人事部门意见</td>
              <td colspan="6" rowspan="12" class="opinion-area detailed">
                <div class="approval-text">
                  根据相关文件及有关规定，经审核，同意你单位：
                </div>
                <div class="approval-item">
                  <span class="approval-label">基础性绩效工资</span>
                  <span class="approval-value">{{ reportData.绩效人数合计 || 0 }}</span>
                  <span>人：</span>
                  <span class="approval-value">{{ reportData.绩效工资合计 || 0 }}</span>
                  <span>元；</span>
                </div>
                <div class="approval-item">
                  <span class="approval-label">生活补贴</span>
                  <span class="approval-value">{{ reportData.在职人数 || 0 }}</span>
                  <span>人：</span>
                  <span class="approval-value">{{ reportData.乡镇补贴合计 || 0 }}</span>
                  <span>元；</span>
                </div>
                <div class="approval-item">
                  <span class="approval-label">岗位设置遗留问题</span>
                  <span class="approval-value">{{ reportData.遗留问题人数 || 0 }}</span>
                  <span>人：</span>
                  <span class="approval-value">{{ reportData.遗留问题金额 || 0 }}</span>
                  <span>元；</span>
                </div>
                <div class="approval-summary">
                  <span>合计：</span>
                  <span class="approval-total">{{ calculateTotalAmount() }}</span>
                  <span>元</span>
                </div>
                <div class="approval-note">
                  注：<span class="note-text">无生活补贴</span>
                  <span class="approval-value">{{ reportData.无补贴人数 || 0 }}</span>
                  <span>人：</span>
                  <span>{{ reportData.无补贴名单 || '' }}</span>
                </div>
                <div class="opinion-date">{{ nextDate2 }}</div>
              </td>
            </tr>
            <tr>
              <td class="row-item">3、一级教师</td>
              <td class="cell-center">
                <el-input v-model="reportData.一级教师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.一级教师标准 || 1309 }}</td>
              <td class="cell-center">{{ calculateSubtotal('一级教师') }}</td>
            </tr>
            <tr>
              <td class="row-item">4、二级教师</td>
              <td class="cell-center">
                <el-input v-model="reportData.二级教师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.二级教师标准 || 1241 }}</td>
              <td class="cell-center">{{ calculateSubtotal('二级教师') }}</td>
            </tr>
            <tr>
              <td class="row-item">5、三级教师</td>
              <td class="cell-center">
                <el-input v-model="reportData.三级教师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.三级教师标准 || 1128 }}</td>
              <td class="cell-center">{{ calculateSubtotal('三级教师') }}</td>
            </tr>

            <!-- 工人 -->
            <tr>
              <td class="row-header">工人</td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr>
              <td class="row-item">1、高级技师</td>
              <td class="cell-center">
                <el-input v-model="reportData.高级技师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">
                <el-input v-model="reportData.高级技师标准" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ calculateSubtotal('高级技师') }}</td>
            </tr>
            <tr>
              <td class="row-item">2、技师</td>
              <td class="cell-center">
                <el-input v-model="reportData.技师人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.技师标准 || 1331 }}</td>
              <td class="cell-center">{{ calculateSubtotal('技师') }}</td>
            </tr>
            <tr>
              <td class="row-item">3、高级工</td>
              <td class="cell-center">
                <el-input v-model="reportData.高级工人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.高级工标准 || 1219 }}</td>
              <td class="cell-center">{{ calculateSubtotal('高级工') }}</td>
            </tr>
            <tr>
              <td class="row-item">4、中级工</td>
              <td class="cell-center">
                <el-input v-model="reportData.中级工人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.中级工标准 || 1185 }}</td>
              <td class="cell-center">{{ calculateSubtotal('中级工') }}</td>
            </tr>
            <tr>
              <td class="row-item">5、初级工</td>
              <td class="cell-center">
                <el-input v-model="reportData.初级工人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.初级工标准 || 1106 }}</td>
              <td class="cell-center">{{ calculateSubtotal('初级工') }}</td>
            </tr>
            <tr>
              <td class="row-item">6、普工</td>
              <td class="cell-center">
                <el-input v-model="reportData.普工人数" size="small" class="cell-input" />
              </td>
              <td class="cell-center">{{ reportData.普工标准 || 1106 }}</td>
              <td class="cell-center">{{ calculateSubtotal('普工') }}</td>
            </tr>

            <!-- 绩效汇总 -->
            <tr>
              <td class="row-header">绩效人数</td>
              <td class="cell-center">{{ reportData.绩效人数合计 || calculateTotalCount() }}</td>
              <td class="row-header">绩效合计</td>
              <td class="cell-center">{{ reportData.绩效工资合计 || calculateTotalAmount() }}</td>
              <td></td>
              <td class="opinion-date-cell" colspan="6">{{ nextDate2 }}</td>
            </tr>

            <!-- 乡镇补贴 -->
            <tr>
              <td class="row-header" colspan="2">乡镇工作补贴人数</td>
              <td class="cell-center">{{ reportData.在职人数 || 0 }}</td>
              <td class="row-header">标准</td>
              <td class="cell-center" colspan="2">{{ reportData.乡镇补贴标准 || 350 }}</td>
              <td class="row-header">金额</td>
              <td class="cell-center" colspan="4">{{ reportData.乡镇补贴合计 || calculateTownshipSubsidy() }}</td>
            </tr>

            <!-- 退休人员 -->
            <tr>
              <td class="row-header">退休干部人数</td>
              <td class="cell-center">{{ reportData.退休干部 || 0 }}</td>
              <td class="row-header" colspan="2">退休工人人数</td>
              <td class="cell-center" colspan="2">{{ reportData.退休职工 || 0 }}</td>
              <td class="row-header">离休干部人数</td>
              <td class="cell-center" colspan="4">
                <el-input v-model="reportData.离休干部人数" size="small" class="cell-input" />
              </td>
            </tr>

            <!-- 岗位设置遗留问题 -->
            <tr class="legacy-row">
              <td class="row-header" colspan="2">岗位设置遗留问题</td>
              <td class="cell-left">
                <el-input 
                  v-model="reportData.遗留问题详情" 
                  type="textarea" 
                  :rows="2"
                  placeholder="例如：李法金：321.3 张照凯：353.94"
                  class="legacy-input"
                />
              </td>
              <td class="row-header">人数</td>
              <td class="cell-center" colspan="2">{{ reportData.遗留问题人数 || 0 }}</td>
              <td class="row-header">金额</td>
              <td class="cell-center" colspan="4">{{ reportData.遗留问题金额 || 0 }}</td>
            </tr>

            <!-- 备注 -->
            <tr>
              <td class="remark-cell" colspan="11">
                <span class="remark-label">备注:</span>
                <el-input 
                  v-model="reportData.备注" 
                  type="textarea" 
                  :rows="2"
                  class="remark-input"
                />
              </td>
            </tr>
          </table>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存
          </el-button>
          <el-button type="success" :loading="loadingData" @click="handleLoadData">
            从数据库加载数据
          </el-button>
          <el-dropdown @command="handleExport" split-button type="warning" :loading="exporting">
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

    <!-- 历史记录对话框 -->
    <el-dialog
      v-model="historyVisible"
      title="历史审批表记录"
      width="900px"
    >
      <el-table :data="historyList" style="width: 100%">
        <el-table-column prop="年月" label="年月" width="120" />
        <el-table-column prop="填报单位" label="填报单位" />
        <el-table-column prop="绩效人数合计" label="绩效人数" width="100" />
        <el-table-column prop="绩效工资合计" label="绩效金额" width="120" />
        <el-table-column prop="创建时间" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="loadHistory(scope.row)">加载</el-button>
            <el-button type="success" size="small" @click="downloadExcel(scope.row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const loadingData = ref(false)
const historyVisible = ref(false)
const historyList = ref<any[]>([])

// 当前日期
const now = new Date()
const currentYear = now.getFullYear()
const currentMonth = now.getMonth() + 1
const currentDay = now.getDate()

const currentYearMonth = computed(() => `${currentYear}年${currentMonth}月`)
const currentDate = computed(() => `${currentYear}年${currentMonth}月${currentDay}日`)
const nextDate = computed(() => {
  const next = new Date(now)
  next.setDate(next.getDate() + 1)
  return `${next.getFullYear()}年${next.getMonth() + 1}月${next.getDate()}日`
})
const nextDate2 = computed(() => {
  const next = new Date(now)
  next.setDate(next.getDate() + 2)
  return `${next.getFullYear()}年${next.getMonth() + 1}月${next.getDate()}日`
})

// 报表数据
const reportData = reactive({
  // 基本信息
  填报单位: '太平中心学校',
  年月: currentYearMonth.value,
  
  // 行政管理人员
  副处级人数: 0,
  副处级标准: 0,
  正科级人数: 0,
  正科级标准: 0,
  副科级人数: 0,
  副科级标准: 0,
  科员级人数: 0,
  科员级标准: 1185,
  办事员级人数: 0,
  办事员级标准: 0,
  
  // 专业技术人员
  正高级教师人数: 0,
  正高级教师标准: 1862,
  高级教师人数: 0,
  高级教师标准: 1523,
  一级教师人数: 0,
  一级教师标准: 1309,
  二级教师人数: 0,
  二级教师标准: 1241,
  三级教师人数: 0,
  三级教师标准: 1128,
  
  // 工人
  高级技师人数: 0,
  高级技师标准: 0,
  技师人数: 0,
  技师标准: 1331,
  高级工人数: 0,
  高级工标准: 1219,
  中级工人数: 0,
  中级工标准: 1185,
  初级工人数: 0,
  初级工标准: 1106,
  普工人数: 0,
  普工标准: 1106,
  
  // 汇总
  绩效人数合计: 0,
  绩效工资合计: 0,
  
  // 乡镇补贴
  在职人数: 0,
  乡镇补贴标准: 350,
  乡镇补贴合计: 0,
  
  // 退休人员
  退休干部: 0,
  退休职工: 0,
  离休干部人数: 0,
  
  // 遗留问题
  遗留问题详情: '',
  遗留问题人数: 0,
  遗留问题金额: 0,
  无补贴人数: 0,
  无补贴名单: '',
  
  // 备注
  备注: ''
})

// 计算小计
const calculateSubtotal = (level: string) => {
  const count = Number(reportData[`${level}人数`] || 0)
  const standard = Number(reportData[`${level}标准`] || 0)
  return count * standard
}

// 计算总人数
const calculateTotalCount = () => {
  const levels = ['副处级', '正科级', '副科级', '科员级', '办事员级', 
                  '正高级教师', '高级教师', '一级教师', '二级教师', '三级教师',
                  '高级技师', '技师', '高级工', '中级工', '初级工', '普工']
  return levels.reduce((sum, level) => sum + Number(reportData[`${level}人数`] || 0), 0)
}

// 计算总金额
const calculateTotalAmount = () => {
  const levels = ['副处级', '正科级', '副科级', '科员级', '办事员级', 
                  '正高级教师', '高级教师', '一级教师', '二级教师', '三级教师',
                  '高级技师', '技师', '高级工', '中级工', '初级工', '普工']
  return levels.reduce((sum, level) => sum + calculateSubtotal(level), 0)
}

// 计算乡镇补贴
const calculateTownshipSubsidy = () => {
  const count = Number(reportData.在职人数 || 0)
  const standard = Number(reportData.乡镇补贴标准 || 350)
  return count * standard
}

// 打开报表设计器
const open = async () => {
  visible.value = true
  loading.value = true
  
  try {
    // 尝试加载本月数据
    await loadCurrentMonthData()
  } catch (error) {
    console.log('加载本月数据失败，显示空白表单')
  } finally {
    loading.value = false
  }
}

// 加载本月数据
const loadCurrentMonthData = async () => {
  const response = await fetch(`/api/performance-pay-approval/current?year=${currentYear}&month=${currentMonth}`)
  if (response.ok) {
    const result = await response.json()
    if (result.status === 'success' && result.data) {
      Object.assign(reportData, result.data)
    }
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

// 保存报表
const handleSave = async () => {
  saving.value = true
  
  try {
    // 更新汇总数据
    reportData.绩效人数合计 = calculateTotalCount()
    reportData.绩效工资合计 = calculateTotalAmount()
    reportData.乡镇补贴合计 = calculateTownshipSubsidy()
    
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
  
  exporting.value = true
  
  try {
    // 更新汇总数据
    reportData.绩效人数合计 = calculateTotalCount()
    reportData.绩效工资合计 = calculateTotalAmount()
    reportData.乡镇补贴合计 = calculateTownshipSubsidy()
    
    const response = await fetch(`/api/performance-pay-approval/export?format=${format}`, {
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
    
    link.download = `义务教育学校教职工绩效工资审批表_${currentYear}年${currentMonth}月.${extensions[format]}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`已导出 ${format.toUpperCase()} 格式`)
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 显示历史记录
const showHistory = async () => {
  historyVisible.value = true
  
  try {
    const response = await fetch('/api/performance-pay-approval/history')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        historyList.value = result.data
      }
    }
  } catch (error) {
    console.error('加载历史记录失败', error)
  }
}

// 加载历史记录
const loadHistory = (row: any) => {
  Object.assign(reportData, row)
  historyVisible.value = false
  ElMessage.success('历史记录加载成功')
}

// 下载历史Excel
const downloadExcel = async (row: any) => {
  try {
    const response = await fetch(`/api/performance-pay-approval/download/${row.id}`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `绩效工资审批表_${row.年月}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 关闭
const close = () => {
  visible.value = false
}

defineExpose({
  open,
  close,
  showHistory
})
</script>

<style scoped>
.report-designer {
  :deep(.designer-dialog) {
    .el-dialog__body {
      max-height: 80vh;
      overflow-y: auto;
      padding: 20px;
      background: #f5f5f5;
    }
  }
}

.loading-container {
  padding: 40px;
}

/* A4纸张容器 */
.a4-page {
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto;
  background: white;
  padding: 20mm 15mm 20mm 15mm; /* 上、右、下、左页边距 */
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  font-family: '宋体', 'SimSun', serif;
  font-size: 10pt;
  line-height: 1.4;
}

/* 头部表格 */
.header-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0;
}

.header-table td {
  padding: 8px 4px;
  vertical-align: middle;
}

.header-left {
  width: 50pt;
}

.header-month {
  width: 100pt;
  text-align: right;
  font-size: 16pt;
  font-weight: bold;
  white-space: nowrap;
}

.header-title {
  width: 380pt;
  text-align: center;
  font-size: 18pt;
  font-weight: bold;
  padding: 15px 0;
  white-space: nowrap;
}

.header-right {
  width: 50pt;
}

.info-label {
  font-size: 10pt;
  text-align: left;
  white-space: nowrap;
}

.info-value {
  font-size: 10pt;
  border-bottom: 0.5pt solid #000;
}

/* 主表格 */
.main-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.main-table td {
  border: 0.5pt solid #000;
  padding: 4px;
  vertical-align: middle;
  height: 25pt;
}

/* 列宽设置 */
.col-project {
  width: 100pt;
  text-align: center;
  font-weight: bold;
}

.col-count {
  width: 85pt;
  text-align: center;
}

.col-standard {
  width: 110pt;
  text-align: center;
}

.col-subtotal {
  width: 120pt;
  text-align: center;
}

.col-opinion {
  width: 48pt;
  text-align: center;
  font-weight: bold;
  writing-mode: vertical-rl;
  letter-spacing: 4px;
  border-left: 0.5pt solid #000 !important;
  border-top: 0.5pt solid #000 !important;
  border-bottom: 0.5pt solid #000 !important;
  border-right: none !important;
}

.col-opinion-bordered {
  width: 48pt;
  text-align: center;
  font-weight: bold;
  writing-mode: vertical-rl;
  letter-spacing: 4px;
  border: 0.5pt solid #000 !important;
}

.col-opinion-content {
  width: 360pt;
  border-left: none !important;
  border-top: 0.5pt solid #000 !important;
  border-right: 0.5pt solid #000 !important;
  border-bottom: 0.5pt solid #000 !important;
}

/* 行样式 */
.row-header {
  font-weight: bold;
  text-align: center;
  background: #f9f9f9;
}

.row-item {
  padding-left: 8px;
  text-align: left;
}

.cell-center {
  text-align: center;
}

.cell-left {
  text-align: left;
}

/* 输入框样式 */
.cell-input {
  width: 100%;
}

.cell-input :deep(.el-input__inner) {
  padding: 0 4px;
  height: 24px;
  text-align: center;
}

.edit-input {
  width: 100%;
}

.edit-input :deep(.el-input__inner) {
  border: none;
  border-bottom: 1px solid #ccc;
  border-radius: 0;
  background: transparent;
}

/* 意见区域 */
.opinion-area {
  vertical-align: top;
  padding: 10px;
  border-left: none !important;
  border-top: none !important;
  border-right: 0.5pt solid #000 !important;
  border-bottom: none !important;
}

.opinion-text {
  text-align: left;
  padding: 10px;
}

.opinion-placeholder {
  text-align: center;
  margin-top: 30px;
}

.opinion-date {
  text-align: right;
  margin-top: 20px;
  padding-right: 20px;
}

.opinion-area.detailed {
  font-size: 10pt;
  line-height: 2;
  border-top: 0.5pt solid #000;
  border-bottom: 0.5pt solid #000;
}

.approval-text {
  margin-bottom: 10px;
  text-indent: 2em;
}

.approval-item {
  margin: 8px 0;
  padding-left: 20px;
}

.approval-label {
  display: inline-block;
  width: 120px;
}

.approval-value {
  display: inline-block;
  min-width: 60px;
  text-align: center;
  border-bottom: 1px solid #000;
  margin: 0 4px;
}

.approval-summary {
  margin: 15px 0;
  padding-left: 20px;
}

.approval-total {
  display: inline-block;
  min-width: 80px;
  text-align: center;
  border-bottom: 1px solid #000;
  margin: 0 4px;
  font-weight: bold;
}

.approval-note {
  margin-top: 15px;
  padding-left: 20px;
}

.note-text {
  color: #666;
}

/* 意见区域日期单元格 */
.opinion-date-cell {
  text-align: center;
  border-left: none !important;
  border-top: none !important;
  border-right: 0.5pt solid #000 !important;
  border-bottom: 0.5pt solid #000 !important;
}

/* 遗留问题行 */
.legacy-row td {
  height: 37pt;
}

.legacy-input :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  resize: none;
  font-size: 9pt;
  padding: 2px;
}

/* 备注行 */
.remark-cell {
  height: 21pt;
  vertical-align: top;
}

.remark-label {
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
}

.remark-input :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  resize: none;
  font-size: 9pt;
}

/* 对话框底部 */
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
  
  .a4-page {
    width: 100%;
    padding: 0;
    box-shadow: none;
  }
  
  .cell-input :deep(.el-input__inner),
  .edit-input :deep(.el-input__inner) {
    border: none;
    background: transparent;
  }
  
  .legacy-input :deep(.el-textarea__inner),
  .remark-input :deep(.el-textarea__inner) {
    border: none;
    background: transparent;
  }
}
</style>
