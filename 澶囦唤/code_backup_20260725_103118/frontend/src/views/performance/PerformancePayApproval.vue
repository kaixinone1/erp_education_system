<template>
  <div class="performance-pay-approval-page">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>绩效工资审批</h2>
          <div class="header-actions">
            <el-button type="success" @click="showMonthDialog">
              <el-icon><Download /></el-icon>
              从数据库获取数据
            </el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
            <el-dropdown @command="handleExport" split-button type="warning">
              <el-icon><Document /></el-icon>
              导出
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <div v-if="loadingTemplate" class="loading">加载中...</div>
      <div v-else-if="templateData.rows.length > 0">
        <!-- 备注信息显示区域（独立于表格，确保一定可见） -->
        <el-alert 
          v-if="hasLoadedData && editableNotes" 
          type="info" 
          :closable="false"
          style="margin-bottom: 12px; white-space: pre-wrap;"
        >
          <template #title>
            <strong>备注信息：</strong>
          </template>
          {{ editableNotes }}
        </el-alert>
        <div class="a4-container" id="printArea">
          <div class="table-wrapper" v-html="tableHtml" style="max-height: calc(100vh - 400px); overflow-y: auto;"></div>
        </div>
        <el-card v-if="hasLoadedData" class="notes-card" style="margin-top: 16px;">
          <template #header>
            <div class="card-header">
              <span>备注编辑</span>
              <el-button type="primary" size="small" :loading="savingNotes" @click="handleSaveNotes">保存备注</el-button>
            </div>
          </template>
          <el-input
            v-model="editableNotes"
            type="textarea"
            :rows="6"
            placeholder="请输入备注内容..."
            resize="vertical"
          />
        </el-card>
      </div>
      <div v-else class="empty">暂无数据</div>
    </el-card>

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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Download, Check } from '@element-plus/icons-vue'

const saving = ref(false)
const savingNotes = ref(false)
const editableNotes = ref('')
const loadingData = ref(false)
const loadingTemplate = ref(false)
const monthDialogVisible = ref(false)
const selectedMonth = ref('')

const reportYear = ref(new Date().getFullYear())
const reportMonth = ref(new Date().getMonth() + 1)

// 用户选择的绩效月份（用于数据查询）
const selectedPerformanceYear = ref(new Date().getFullYear())
const selectedPerformanceMonth = ref(new Date().getMonth() + 1)

const currentYearMonth = computed(() => `${reportYear.value}年${reportMonth.value}月`)

const getCurrentDate = () => {
  const today = new Date()
  return `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`
}

const getNextDate = () => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return `${tomorrow.getFullYear()}年${tomorrow.getMonth() + 1}月${tomorrow.getDate()}日`
}

const templateData = reactive({
  rows: [],
  total_rows: 0
})

const dynamicData = reactive({
  administrative: {},
  professional: {},
  worker: {},
  totals: {},
  subsidies: {},
  legacy: [],
  retirees: {},
  no_subsidy_names: '',
  no_subsidy_count: 0,
  notes: ''
})

const hasLoadedData = ref(false)

const colWidths = ['84pt', '50pt', '50pt', '50pt', '25pt', 'auto']

const tableHtml = computed(() => {
  if (!templateData.rows || templateData.rows.length === 0) {
    return '<p>暂无数据</p>'
  }
  
  let html = ''
  
  const occupiedCells: {[key: string]: boolean} = {}
  let foundAdminRow = false
  
  templateData.rows.forEach((row: any, rowIdx: number) => {
    if (row.cells && row.cells.length > 0) {
      if (row.cells[0]?.class === 'title') {
        let titleText = row.cells[0].text
        const datePattern = /\d{4}年\d+月/
        
        if (datePattern.test(titleText)) {
          // 如果标题中已有日期格式，替换为当前日期
          titleText = titleText.replace(datePattern, currentYearMonth.value)
        }
        
        html += `<div style="text-align: center; font-size: 16pt; font-weight: bold; font-family: SimSun, Songti SC, serif; margin-bottom: 8px;">${titleText}</div>`
      } else if (row.cells[0]?.class === 'info') {
        const infoText = row.cells[0].text.replace(/填报时间:/, '填报日期：').replace(/\d{4}年\d+月\d+日/, getCurrentDate())
        html += `<div style="text-align: left; font-size: 11pt; font-family: SimSun, Songti SC, serif; padding-left: 5px; margin-bottom: 5px;">${infoText}</div>`
      } else {
        if (!html.includes('<table')) {
          html += '<table style="border-collapse: collapse; width: 100%; font-family: SimSun, Songti SC, serif; table-layout: fixed;">'
          html += '<colgroup>'
          html += `<col style="width: ${colWidths[0]}; word-break: break-all;">`
          html += `<col style="width: ${colWidths[1]};">`
          html += `<col style="width: ${colWidths[2]};">`
          html += `<col style="width: ${colWidths[3]};">`
          html += `<col style="width: ${colWidths[4]};">`
          html += `<col style="width: ${colWidths[5]};">`
          html += '</colgroup>'
        }
        
        html += '<tr>'
        
        let colIdx = 0
        let cellIdx = 0
        
        while (colIdx < 6) {
          const key = `${rowIdx}-${colIdx}`
          if (occupiedCells[key]) {
            colIdx++
            continue
          }
          
          const cell = row.cells[cellIdx]
          if (!cell) {
            html += '<td style="border: 1px solid #000; padding: 4px 6px; vertical-align: middle; text-align: center; font-size: 11px;">&nbsp;</td>'
            colIdx++
            continue
          }
          
          const rowspan = cell.rowspan || 1
          const colspan = cell.colspan || 1
          const text = cell.text || '&nbsp;'
          
          let align = cell.align || 'center'
          
          if (colIdx === 0 && foundAdminRow) {
            align = 'left'
          }
          
          if (text === '行政管理人员') {
            foundAdminRow = true
          }
          
          let cellStyle = `padding: 4px 6px; vertical-align: middle; text-align: ${align}; font-size: 11px; border: 1px solid #000;`
          
          if (cell.class === 'xl78' || cell.class === 'xl122') {
            cellStyle += 'writing-mode: vertical-rl; text-orientation: mixed;'
          }
          
          if (cell.isNotesRow) {
            cellStyle = `padding: 4px 6px; vertical-align: top; text-align: left; font-size: 11px; border: 1px solid #000; height: auto; min-height: 50px;`
          }
          
          let cellContent = text
          
          const rowText = row.cells[0]?.text || ''
          const cellIndex = cellIdx
          const isMiddleWorkerRow = rowText.includes('中级工')
          const isJuniorWorkerRow = rowText.includes('初级工')
          const isOrdinaryWorkerRow = rowText.includes('普工')
          const isRetiredCadreRow = rowText.includes('退休干部')
          const isRetiredWorkerRow = rowText.includes('退休工人')
          const isRetiredCadreRow2 = rowText.includes('离休干部')
          const isDataRow = isMiddleWorkerRow || isJuniorWorkerRow || isOrdinaryWorkerRow || isRetiredCadreRow || isRetiredWorkerRow || isRetiredCadreRow2
          
          if (hasLoadedData.value) {
            if (rowText.includes('项目') === false &&
                rowText.includes('行政管理人员') === false && rowText.includes('专业技术人员') === false && 
                rowText.includes('工人') === false && rowText.includes('合计') === false && 
                rowText.includes('乡镇补贴') === false && rowText.includes('遗留问题') === false &&
                rowText.includes('退休') === false && rowText.includes('离休') === false) {
              if (cellIndex === 1) {
                let count = ''
                if (rowText.includes('副处级')) count = dynamicData.administrative['副处级']?.count || ''
                else if (rowText.includes('正科级')) count = dynamicData.administrative['正科级']?.count || ''
                else if (rowText.includes('副科级')) count = dynamicData.administrative['副科级']?.count || ''
                else if (rowText.includes('科员级')) count = dynamicData.administrative['科员级']?.count || ''
                else if (rowText.includes('办事员级')) count = dynamicData.administrative['办事员级']?.count || ''
                else if (rowText.includes('正高级')) count = dynamicData.professional['正高级']?.count || ''
                else if (rowText.includes('高级教师')) count = dynamicData.professional['高级教师']?.count || ''
                else if (rowText.includes('一级教师')) count = dynamicData.professional['一级教师']?.count || ''
                else if (rowText.includes('二级教师')) count = dynamicData.professional['二级教师']?.count || ''
                else if (rowText.includes('三级教师')) count = dynamicData.professional['三级教师']?.count || ''
                else if (rowText.includes('高级技师')) count = dynamicData.worker['高级技师']?.count || ''
                else if (rowText.includes('技师')) count = dynamicData.worker['技师']?.count || ''
                else if (rowText.includes('高级工')) count = dynamicData.worker['高级工']?.count || ''
                else if (isMiddleWorkerRow) count = dynamicData.worker['中级工']?.count || ''
                else if (isJuniorWorkerRow) count = dynamicData.worker['初级工']?.count || ''
                cellContent = count || '&nbsp;'
              } else if (cellIndex === 2) {
                let standard = ''
                if (rowText.includes('副处级')) standard = dynamicData.administrative['副处级']?.standard || ''
                else if (rowText.includes('正科级')) standard = dynamicData.administrative['正科级']?.standard || ''
                else if (rowText.includes('副科级')) standard = dynamicData.administrative['副科级']?.standard || ''
                else if (rowText.includes('科员级')) standard = dynamicData.administrative['科员级']?.standard || ''
                else if (rowText.includes('办事员级')) standard = dynamicData.administrative['办事员级']?.standard || ''
                else if (rowText.includes('正高级')) standard = dynamicData.professional['正高级']?.standard || ''
                else if (rowText.includes('高级教师')) standard = dynamicData.professional['高级教师']?.standard || ''
                else if (rowText.includes('一级教师')) standard = dynamicData.professional['一级教师']?.standard || ''
                else if (rowText.includes('二级教师')) standard = dynamicData.professional['二级教师']?.standard || ''
                else if (rowText.includes('三级教师')) standard = dynamicData.professional['三级教师']?.standard || ''
                else if (rowText.includes('高级技师')) standard = dynamicData.worker['高级技师']?.standard || ''
                else if (rowText.includes('技师')) standard = dynamicData.worker['技师']?.standard || ''
                else if (rowText.includes('高级工')) standard = dynamicData.worker['高级工']?.standard || ''
                else if (isMiddleWorkerRow) standard = dynamicData.worker['中级工']?.standard || ''
                else if (isJuniorWorkerRow) standard = dynamicData.worker['初级工']?.standard || ''
                cellContent = standard || '&nbsp;'
              } else if (cellIndex === 3) {
                let subtotal = ''
                if (rowText.includes('副处级')) subtotal = dynamicData.administrative['副处级']?.subtotal || ''
                else if (rowText.includes('正科级')) subtotal = dynamicData.administrative['正科级']?.subtotal || ''
                else if (rowText.includes('副科级')) subtotal = dynamicData.administrative['副科级']?.subtotal || ''
                else if (rowText.includes('科员级')) subtotal = dynamicData.administrative['科员级']?.subtotal || ''
                else if (rowText.includes('办事员级')) subtotal = dynamicData.administrative['办事员级']?.subtotal || ''
                else if (rowText.includes('正高级')) subtotal = dynamicData.professional['正高级']?.subtotal || ''
                else if (rowText.includes('高级教师')) subtotal = dynamicData.professional['高级教师']?.subtotal || ''
                else if (rowText.includes('一级教师')) subtotal = dynamicData.professional['一级教师']?.subtotal || ''
                else if (rowText.includes('二级教师')) subtotal = dynamicData.professional['二级教师']?.subtotal || ''
                else if (rowText.includes('三级教师')) subtotal = dynamicData.professional['三级教师']?.subtotal || ''
                else if (rowText.includes('高级技师')) subtotal = dynamicData.worker['高级技师']?.subtotal || ''
                else if (rowText.includes('技师')) subtotal = dynamicData.worker['技师']?.subtotal || ''
                else if (rowText.includes('高级工')) subtotal = dynamicData.worker['高级工']?.subtotal || ''
                else if (isMiddleWorkerRow) subtotal = dynamicData.worker['中级工']?.subtotal || ''
                else if (isJuniorWorkerRow) subtotal = dynamicData.worker['初级工']?.subtotal || ''
                cellContent = subtotal || '&nbsp;'
              }
            } else if (rowText.includes('绩效工资合计')) {
              if (cellIndex === 1) cellContent = dynamicData.totals.performance_count || '&nbsp;'
              else if (cellIndex === 3) cellContent = dynamicData.totals.performance_total || '&nbsp;'
            } else if (rowText.includes('乡镇补贴合计')) {
              if (cellIndex === 1) cellContent = dynamicData.subsidies.count || '&nbsp;'
              else if (cellIndex === 2) cellContent = dynamicData.subsidies.standard || '&nbsp;'
              else if (cellIndex === 3) cellContent = dynamicData.subsidies.total || '&nbsp;'
            } else if (rowText.includes('岗位设置遗留问题')) {
              if (!rowText.includes('合计')) {
                const legacyIndex = rowText.match(/\d+/) ? parseInt(rowText.match(/\d+/)[0]) - 1 : 0
                if (dynamicData.legacy && dynamicData.legacy.length > 0 && legacyIndex >= 0 && legacyIndex < dynamicData.legacy.length) {
                  if (cellIndex === 1) {
                    cellContent = dynamicData.legacy[legacyIndex]?.name || '&nbsp;'
                  } else if (cellIndex === 2 || cellIndex === 3) {
                    cellContent = dynamicData.legacy[legacyIndex]?.amount || '&nbsp;'
                  }
                } else if (cellIndex > 0) {
                  cellContent = '&nbsp;'
                }
              } else {
                if (cellIndex === 1) cellContent = dynamicData.totals.legacy_count || '&nbsp;'
                else if (cellIndex === 3) cellContent = dynamicData.totals.legacy_total || '&nbsp;'
              }
            } else if (isRetiredCadreRow) {
              if (cellIndex === 1) cellContent = dynamicData.retirees.cadre_count || '&nbsp;'
            } else if (rowText.includes('退休工人')) {
              if (cellIndex === 1) cellContent = dynamicData.retirees.worker_count || '&nbsp;'
            } else if (rowText.includes('离休干部')) {
              if (cellIndex === 1) cellContent = dynamicData.retirees.retired_count || '&nbsp;'
            } else if (isDataRow) {
              cellContent = '&nbsp;'
            }
          } else {
            if (isDataRow && cellIndex > 0) {
              cellContent = '&nbsp;'
            }
            if (rowText.includes('岗位设置遗留问题') && cellIndex > 0) {
              cellContent = '&nbsp;'
            }
          }
          
          if (cell.isNotesRow) {
            if (hasLoadedData.value && editableNotes.value) {
              const notes = editableNotes.value
              const noteLines = notes.split('\n')
              let notesHtml = '<div style="white-space: pre-wrap; word-break: break-all;">'
              notesHtml += '<div>备注：</div>'
              noteLines.forEach(line => {
                if (line.trim()) {
                  notesHtml += `<div>${line.trim()}</div>`
                }
              })
              notesHtml += '</div>'
              cellContent = notesHtml
            } else {
              cellContent = '<div>备注：</div>'
            }
          }
          
          if (text.includes('据实填写，同意呈报') && text.includes('盖章') && text.includes('2026年')) {
            cellStyle = `padding: 0; vertical-align: top; text-align: center; font-size: 11px; border: 1px solid #000;`
            cellContent = `<div style="height: 100%; min-height: 175px; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;">
              <div>据实填写，同意呈报。</div>
              <div>（盖章）</div>
              <div style="position: absolute; bottom: 2px; right: 8px;">${getCurrentDate()}</div>
            </div>`
          } else if (text.includes('（盖章）') && text.includes('2026年4月29日') && !text.includes('据实填写')) {
            cellStyle = `padding: 0; vertical-align: top; text-align: center; font-size: 11px; border: 1px solid #000;`
            cellContent = `<div style="height: 100%; min-height: 225px; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;">
              <div>（盖章）</div>
              <div style="position: absolute; bottom: 2px; right: 8px;">${getNextDate()}</div>
            </div>`
          } else if (text.includes('根据相关文件') && text.includes('人事部门意见') === false) {
            const perfCount = dynamicData.totals.performance_count || 0
            const perfTotal = dynamicData.totals.performance_total || 0
            const subCount = dynamicData.subsidies.count || 0
            const subTotal = dynamicData.subsidies.total || 0
            const legacyCount = dynamicData.totals.legacy_count || 0
            const legacyTotal = dynamicData.totals.legacy_total || 0
            const totalTotal = perfTotal + subTotal + legacyTotal
            const noSubsidyNames = dynamicData.no_subsidy_names || ''
            const noSubsidyCount = dynamicData.no_subsidy_count || 0
            
            cellStyle = `padding: 0; vertical-align: top; text-align: center; font-size: 11px; border: 1px solid #000;`
            cellContent = `<div style="height: 100%; min-height: 300px; display: flex; flex-direction: column; position: relative; padding: 8px;">
              <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div>根据相关文件及有关规定，经审核，同意你单位：</div>
                <div style="text-align: right; padding-right: 48px;">基础性绩效工资${perfCount}人，${perfTotal}元；</div>
                <div style="text-align: right; padding-right: 48px;">生活补贴${subCount}人，${subTotal}元；</div>
                <div style="text-align: right; padding-right: 48px;">合计${perfTotal + subTotal}元；</div>
                <div style="text-align: right; padding-right: 48px;">岗位设置遗留${legacyCount}人，${legacyTotal}元；</div>
                <div style="text-align: right; padding-right: 48px;">总计${totalTotal}元。</div>
                <div style="text-align: right; padding-right: 48px;">无乡镇补贴${noSubsidyCount}人，${noSubsidyNames}。</div>
              </div>
              <div style="text-align: right; padding-right: 8px; padding-bottom: 2px;">${getNextDate()}</div>
            </div>`
          }
          
          html += `<td rowspan="${rowspan}" colspan="${colspan}" style="${cellStyle}">${cellContent}</td>`
          
          for (let r = 1; r < rowspan; r++) {
            for (let c = 0; c < colspan; c++) {
              occupiedCells[`${rowIdx + r}-${colIdx + c}`] = true
            }
          }
          
          colIdx += colspan
          cellIdx++
        }
        
        html += '</tr>'
      }
    }
  })
  
  if (html.includes('<table')) {
    html += '</table>'
  }
  
  console.log('生成的表格HTML长度:', html.length)
  return html
})

const loadTemplate = async () => {
  loadingTemplate.value = true
  console.log('开始加载模板...')
  try {
    const response = await fetch('/api/performance-pay-approval/template-metadata')
    console.log('API响应状态:', response.status)
    const result = await response.json()
    console.log('API响应数据:', result)
    if (result.status === 'success') {
      const data = result.data
      templateData.rows = data.rows
      templateData.total_rows = data.total_rows
      console.log('模板加载成功，行数:', data.rows.length)
      console.log('第一行数据:', JSON.stringify(data.rows[0]))
    }
  } catch (e) {
    console.error('加载模板失败', e)
  } finally {
    loadingTemplate.value = false
  }
}

const showMonthDialog = () => {
  monthDialogVisible.value = true
}

const confirmLoadData = async () => {
  if (!selectedMonth.value) {
    ElMessage.warning('请选择月份')
    return
  }
  
  const [year, month] = selectedMonth.value.split('-')
  const selectedYear = parseInt(year)
  const selectedMonthNum = parseInt(month)
  
  // 计算标题日期（选择日期 + 1个月）
  let titleYear = selectedYear
  let titleMonthNum = selectedMonthNum + 1
  if (titleMonthNum > 12) {
    titleYear++
    titleMonthNum = 1
  }
  
  // 获取当前系统日期
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonthNum = now.getMonth() + 1
  
  // 格式化显示
  const currentDateStr = `${currentYear}年${currentMonthNum}月`
  const selectedDateStr = `${selectedYear}年${selectedMonthNum}月`
  const titleDateStr = `${titleYear}年${titleMonthNum}月`
  
  // 显示确认对话框
  try {
    await ElMessageBox.confirm(
      `当前日期：${currentDateStr}<br>选择日期：${selectedDateStr}<br>标题日期：${titleDateStr}`,
      '确认填报信息',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info',
        dangerouslyUseHTMLString: true
      }
    )
    
    // 用户确认后更新日期并加载数据
    // 标题日期 = 选择日期 + 1个月
    reportYear.value = titleYear
    reportMonth.value = titleMonthNum
    // 保存用户选择的绩效月份（用于数据查询）
    selectedPerformanceYear.value = selectedYear
    selectedPerformanceMonth.value = selectedMonthNum
    
    monthDialogVisible.value = false
    await handleLoadData()
  } catch (error) {
    // 用户取消，不做任何操作
    if (error !== 'cancel') {
      console.error('确认失败:', error)
    }
  }
}

const handleLoadData = async () => {
  loadingData.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/load-from-database', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year: selectedPerformanceYear.value, month: selectedPerformanceMonth.value })
    })
    if (!response.ok) throw new Error('加载数据失败')
    const result = await response.json()
    if (result.status === 'success') {
      const data = result.data
      Object.assign(dynamicData, data)
      editableNotes.value = data.notes || ''
      console.log('[PerformancePayApproval] 数据加载成功, notes长度:', (data.notes || '').length, 'notes前50字:', (data.notes || '').substring(0, 50))
      console.log('[PerformancePayApproval] editableNotes.value长度:', editableNotes.value.length)
      console.log('[PerformancePayApproval] hasLoadedData:', hasLoadedData.value)
      hasLoadedData.value = true
      ElMessage.success('数据加载成功')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loadingData.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    const saveData = {
      ...JSON.parse(JSON.stringify(dynamicData)),
      年月: currentYearMonth.value,
      notes: editableNotes.value
    }
    const response = await fetch('/api/performance-pay-approval/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(saveData)
    })
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleSaveNotes = async () => {
  savingNotes.value = true
  try {
    const saveData = {
      ...JSON.parse(JSON.stringify(dynamicData)),
      年月: currentYearMonth.value,
      notes: editableNotes.value
    }
    const response = await fetch('/api/performance-pay-approval/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(saveData)
    })
    const result = await response.json()
    if (result.status === 'success') {
      dynamicData.notes = editableNotes.value
      ElMessage.success('备注保存成功')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    savingNotes.value = false
  }
}

const exporting = ref(false)

const handleExport = async (command: string) => {
  if (command !== 'excel') {
    ElMessage.info('暂不支持此格式')
    return
  }

  if (!hasLoadedData.value) {
    ElMessage.warning('请先从数据库获取数据')
    return
  }

  exporting.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/export-v2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...dynamicData,
        年月: currentYearMonth.value,
        填报单位: '太平镇中心学校'
      })
    })

    if (!response.ok) {
      throw new Error('导出失败')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `绩效工资审批表_${currentYearMonth.value}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  console.log('PerformancePayApproval组件已挂载')
  loadTemplate()
})
</script>

<style scoped>
.performance-pay-approval-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.a4-container {
  background: white;
  width: 210mm;
  min-height: 297mm;
  padding: 15mm;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  margin: 20px auto;
}

.table-wrapper {
  width: 100%;
}

.loading, .empty {
  text-align: center;
  padding: 50px;
  font-size: 18px;
}

.notes-card {
  max-width: 100%;
}

.notes-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scroll-hint {
  font-size: 12px;
  color: #666;
  margin-top: 10px;
  text-align: center;
}

@media print {
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  body {
    margin: 0;
    padding: 0;
    background: white;
    font-family: SimSun, Songti SC, serif;
  }
  .card-header,
  .header-actions,
  .scroll-hint,
  .el-card__header,
  .el-card__body {
    display: none !important;
  }
  .performance-pay-approval-page {
    padding: 0 !important;
    background: white !important;
    min-height: auto !important;
  }
  .page-card {
    box-shadow: none !important;
    border: none !important;
    min-height: auto !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  .a4-container {
    width: 210mm !important;
    min-height: 297mm !important;
    padding: 15mm !important;
    box-shadow: none !important;
    margin: 0 auto !important;
    background: white !important;
    display: block !important;
    page-break-after: always;
  }
  .table-wrapper {
    width: 100% !important;
    display: block !important;
  }
  table {
    page-break-inside: avoid;
  }
  td {
    page-break-inside: avoid;
  }
}
</style>
