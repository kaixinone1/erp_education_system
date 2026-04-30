<template>
  <div class="performance-pay-approval-page">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>绩效工资审批管理</h2>
          <div class="header-actions">
            <el-button type="success" @click="showMonthDialog">
              <el-icon><Download /></el-icon>
              从数据库加载数据
            </el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
            <el-dropdown @command="handleExport" split-button type="warning" :loading="exporting">
              <el-icon><Document /></el-icon>
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
        </div>
      </template>

      <div class="report-container" v-loading="loadingTemplate">
        <div class="a4-page" id="printArea">
          <table class="salary-table" cellpadding="0" cellspacing="0">
            <colgroup>
              <col v-for="(w, i) in colWidths" :key="i" :style="{width: w}">
            </colgroup>
            <template v-for="(row, rowIndex) in templateRows" :key="rowIndex">
              <tr :style="{height: rowHeights[rowIndex] || '25pt'}">
                <template v-for="(cell, cellIndex) in row" :key="cellIndex">
                  <td v-if="!cell.hidden" 
                      :rowspan="cell.rowspan" 
                      :colspan="cell.colspan"
                      :style="cell.style"
                      :class="getCellClass(cell)">
                    <template v-if="isEditableCell(cell)">
                      <el-input 
                        v-model="reportData[getDataKey(cell.text)]" 
                        size="small" 
                        class="cell-input"
                        @change="onCellChange(rowIndex, cellIndex, cell)"
                      />
                    </template>
                    <template v-else-if="isCalculatedCell(cell)">
                      {{ calculateCellValue(cell) }}
                    </template>
                    <template v-else>
                      {{ formatCellText(cell) }}
                    </template>
                  </td>
                </template>
              </tr>
            </template>
          </table>
        </div>
      </div>

      <!-- 月份选择对话框 -->
      <el-dialog v-model="monthDialogVisible" title="选择填报月份" width="300px">
        <p style="margin-bottom: 15px; font-size: 14px;">请选择需要填报绩效工资的月份：</p>
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          placeholder="选择月份"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          style="width: 200px;"
        />
      <template #footer>
        <el-button @click="monthDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loadingData" @click="confirmLoadData">确认加载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Download, Check } from '@element-plus/icons-vue'

const saving = ref(false)
const exporting = ref(false)
const loadingData = ref(false)
const loadingTemplate = ref(false)
const monthDialogVisible = ref(false)
const selectedMonth = ref('')

const reportYear = ref(new Date().getFullYear())
const reportMonth = ref(new Date().getMonth() + 1)

const currentYearMonth = computed(() => `${reportYear.value}年${reportMonth.value}月`)
const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${String(now.getMonth() + 1).padStart(2, '0')}月${String(now.getDate()).padStart(2, '0')}日`
})

const templateRows = ref<any[]>([])
const colWidths = ref<string[]>([])
const rowHeights = ref<string[]>([])

const reportData = reactive<Record<string, any>>({
  '填报单位': '太平中心学校',
  '填报时间': '',
  '副处级人数': 0,
  '副处级标准': 0,
  '正科级人数': 0,
  '正科级标准': 0,
  '副科级人数': 0,
  '副科级标准': 0,
  '科员级人数': 0,
  '科员级标准': 1185,
  '办事员级人数': 0,
  '办事员级标准': 0,
  '正高级教师人数': 0,
  '正高级教师标准': 0,
  '高级教师人数': 0,
  '高级教师标准': 0,
  '一级教师人数': 0,
  '一级教师标准': 0,
  '二级教师人数': 0,
  '二级教师标准': 0,
  '三级教师人数': 0,
  '三级教师标准': 0,
  '高级技师人数': 0,
  '高级技师标准': 0,
  '技师人数': 0,
  '技师标准': 0,
  '高级工人数': 0,
  '高级工标准': 0,
  '中级工人数': 0,
  '中级工标准': 0,
  '初级工人数': 0,
  '初级工标准': 0,
  '普工人数': 0,
  '普工标准': 0,
  '在职人数': 0,
  '绩效工资合计': 0,
  '乡镇补贴人数': 0,
  '乡镇补贴标准': 350,
  '乡镇补贴合计': 0,
  '退休干部': 0,
  '退休职工': 0,
  '离休干部人数': 0,
  '遗留问题详情': '',
  '遗留问题人数': 0,
  '遗留问题金额': 0,
  '无补贴人数': 0,
  '无补贴名单': '',
  '备注': ''
})

// 加载模板
const loadTemplate = async () => {
  loadingTemplate.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/template')
    const result = await response.json()
    if (result.status === 'success') {
      // 解析模板数据
      const rows = result.template
      // 提取列宽
      colWidths.value = ['76pt', '42pt', '69pt', '44pt', '34pt', '49pt', '97pt', '28pt', '22pt', '61pt', '48pt']
      // 提取行高
      rowHeights.value = ['30pt', '25pt', '50pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt', '25pt']
      
      // 处理rowspan/colspan，填充隐藏单元格
      const processedRows: any[] = []
      const cellMap: Record<string, boolean> = {}
      
      for (let r = 0; r < rows.length; r++) {
        const row = rows[r]
        const processedRow: any[] = []
        let cellIdx = 0
        
        for (let c = 0; c < row.length; c++) {
          const cell = row[c]
          const key = `${r}-${cellIdx}`
          
          // 检查是否被之前的rowspan占用
          if (cellMap[key]) {
            processedRow.push({ hidden: true })
            cellIdx++
            c--
            continue
          }
          
          // 添加单元格
          processedRow.push({
            text: cell.text,
            rowspan: cell.rowspan,
            colspan: cell.colspan,
            style: cell.style,
            originalIndex: c
          })
          
          // 标记被占用的位置
          for (let rs = 0; rs < cell.rowspan; rs++) {
            for (let cs = 0; cs < cell.colspan; cs++) {
              if (rs > 0 || cs > 0) {
                cellMap[`${r + rs}-${cellIdx + cs}`] = true
              }
            }
          }
          
          cellIdx++
        }
        processedRows.push(processedRow)
      }
      
      templateRows.value = processedRows
    }
  } catch (e) {
    console.error('加载模板失败', e)
  } finally {
    loadingTemplate.value = false
  }
}

// 判断是否为可编辑单元格
const isEditableCell = (cell: any) => {
  const text = cell.text
  return text.includes('人数') || text.includes('标准')
}

// 判断是否为计算单元格
const isCalculatedCell = (cell: any) => {
  const text = cell.text
  return text.includes('小计') || text.includes('合计') || text.includes('总计')
}

// 获取数据键名
const getDataKey = (text: string) => {
  const map: Record<string, string> = {
    '副处级': '副处级',
    '正科级': '正科级',
    '副科级': '副科级',
    '科员级': '科员级',
    '办事员级': '办事员级',
    '正高级': '正高级教师',
    '高级教师': '高级教师',
    '一级教师': '一级教师',
    '二级教师': '二级教师',
    '三级教师': '三级教师',
    '高级技师': '高级技师',
    '技师': '技师',
    '高级工': '高级工',
    '中级工': '中级工',
    '初级工': '初级工',
    '普工': '普工',
    '绩效工资合计': '绩效工资合计',
    '乡镇补贴合计': '乡镇补贴合计',
    '岗位设置遗留问题': '遗留问题',
    '退休干部': '退休干部',
    '退休工人': '退休职工',
    '离休干部': '离休干部人数',
    '备注': '备注'
  }
  
  for (const [key, value] of Object.entries(map)) {
    if (text.includes(key)) return value
  }
  return text
}

// 格式化单元格文本
const formatCellText = (cell: any) => {
  return cell.text
}

// 计算单元格值
const calculateCellValue = (cell: any) => {
  const text = cell.text
  if (text.includes('小计')) {
    return 0 // 需要根据具体行计算
  }
  if (text.includes('合计') || text.includes('总计')) {
    return 0 // 需要汇总计算
  }
  return ''
}

// 获取单元格样式类
const getCellClass = (cell: any) => {
  const classes: string[] = []
  if (cell.style?.includes('border:none')) {
    classes.push('no-border')
  }
  if (cell.style?.includes('text-align:center')) {
    classes.push('text-center')
  }
  if (cell.style?.includes('font-weight:bold') || cell.style?.includes('font-weight:700')) {
    classes.push('bold')
  }
  return classes.join(' ')
}

// 单元格变化事件
const onCellChange = (rowIndex: number, cellIndex: number, cell: any) => {
  console.log('Cell changed', rowIndex, cellIndex, cell)
}

// 显示月份选择对话框
const showMonthDialog = () => {
  monthDialogVisible.value = true
}

// 确认加载数据
const confirmLoadData = async () => {
  if (!selectedMonth.value) {
    ElMessage.warning('请选择月份')
    return
  }
  
  const [year, month] = selectedMonth.value.split('-')
  reportYear.value = parseInt(year)
  reportMonth.value = parseInt(month)
  
  monthDialogVisible.value = false
  await handleLoadData()
}

// 从数据库加载数据
const handleLoadData = async () => {
  loadingData.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/load-from-database', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year: reportYear.value, month: reportMonth.value })
    })
    if (!response.ok) throw new Error('加载数据失败')
    const result = await response.json()
    if (result.status === 'success') { 
      Object.assign(reportData, result.data); 
      ElMessage.success('数据加载成功') 
    }
  } catch (error: any) { ElMessage.error(error.message || '加载数据失败') }
  finally { loadingData.value = false }
}

// 保存数据
const handleSave = async () => {
  saving.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/save', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...reportData, 年月: currentYearMonth.value })
    })
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error: any) { ElMessage.error(error.message || '保存失败') }
  finally { saving.value = false }
}

// 导出
const handleExport = async (format: string) => {
  if (format === 'print') {
    window.print()
    return
  }
  
  exporting.value = true
  try {
    const response = await fetch(`/api/performance-pay-approval/export?format=${format}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...reportData, 年月: currentYearMonth.value })
    })
    if (!response.ok) throw new Error('导出失败')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `绩效工资审批表_${currentYearMonth.value}.${format === 'excel' ? 'xlsx' : 'pdf'}`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success(`已导出 ${format.toUpperCase()} 格式`)
  } catch (error: any) { ElMessage.error(error.message || '导出失败') }
  finally { exporting.value = false }
}

onMounted(async () => {
  await loadTemplate()
})
</script>

<style scoped>
.performance-pay-approval-page { padding: 20px; }
.page-card { min-height: calc(100vh - 140px); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 10px; }
.report-container { overflow: auto; display: flex; justify-content: center; background: #f5f5f5; padding: 20px; }
.a4-page { background: white; width: 794px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.salary-table { width: 100%; border-collapse: collapse; font-size: 10pt; }
.salary-table td { padding: 2px 5px; }
.cell-input { width: 100%; }
.no-border { border: none !important; }
.text-center { text-align: center; }
.bold { font-weight: bold; }

@media print {
  .header-actions { display: none; }
  .a4-page { box-shadow: none; }
}
</style>
