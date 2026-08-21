/**
 * useExport - 通用导出组合式函数
 * 
 * 提供统一的导出逻辑，支持：
 * - 四种导出范围：全部数据、筛选结果、当前页、选中行
 * - 多种导出格式：Excel、PDF、SQL
 * - 筛选条件传递（筛选结果导出时自动带上当前筛选条件）
 * 
 * 使用方式：
 * const exportUtil = useExport({
 *   tableName: 'my_table',
 *   tableTitle: '我的数据表',
 *   fetchAllData: async (params) => { ... },    // 获取全部/筛选数据
 *   getCurrentPageData: () => tableData.value,   // 当前页数据
 *   getSelectedRows: () => selectedRows.value,   // 选中行数据
 *   filterConditions: filterConditions,          // 筛选条件
 *   searchKeyword: searchKeyword,                // 搜索关键词
 * })
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FilterCondition } from './useFilter'

export interface UseExportOptions {
  /** 表名（用于导出API） */
  tableName: string | (() => string)
  /** 表格标题（用于文件名） */
  tableTitle: string | (() => string)
  /** 获取全部数据或筛选数据的函数 */
  fetchAllData: (params: {
    page: number
    size: number
    filter?: string | null
    keyword?: string
  }) => Promise<{ data: any[]; total: number }>
  /** 获取当前页数据 */
  getCurrentPageData: () => any[]
  /** 获取选中行数据 */
  getSelectedRows: () => any[]
  /** 筛选条件 */
  filterConditions?: () => FilterCondition[]
  /** 搜索关键词 */
  searchKeyword?: () => string
}

export function useExport(options: UseExportOptions) {
  const exportDialogVisible = ref(false)
  const exporting = ref(false)
  const exportForm = ref({
    format: 'excel',
    scope: 'filtered',
    path: '',
    filename: ''
  })

  // 获取当前日期
  const getCurrentDate = () => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  }

  // 获取表名
  const getTableName = () => {
    return typeof options.tableName === 'function' ? options.tableName() : options.tableName
  }

  // 获取表格标题
  const getTableTitle = () => {
    return typeof options.tableTitle === 'function' ? options.tableTitle() : options.tableTitle
  }

  // 获取激活的筛选条件
  const getActiveFilterConditions = (): FilterCondition[] => {
    if (!options.filterConditions) return []
    const conditions = options.filterConditions()
    return conditions.filter(
      c => c.field && c.operator && (c.value || c.operator === 'is_null' || c.operator === 'is_not_null')
    )
  }

  // 构建筛选条件 JSON
  const getFilterJson = (): string | null => {
    const active = getActiveFilterConditions()
    if (active.length > 0) {
      return JSON.stringify(active)
    }
    return null
  }

  // 打开导出对话框
  const openExport = () => {
    exportForm.value.filename = `${getTableTitle()}_${getCurrentDate()}`
    exportForm.value.path = ''
    exportForm.value.scope = 'filtered'
    exportDialogVisible.value = true
  }

  // 获取数据（带筛选条件）
  const fetchDataForExport = async (scope: string): Promise<any[]> => {
    const currentPageData = options.getCurrentPageData()
    const selectedRows = options.getSelectedRows()

    switch (scope) {
      case 'selected':
        return selectedRows

      case 'current':
        return currentPageData

      case 'all':
        // 导出全部数据（不含筛选条件）
        const allResult = await options.fetchAllData({
          page: 1,
          size: 10000,
          filter: null,
          keyword: undefined
        })
        return allResult.data || []

      case 'filtered':
      default:
        // 导出筛选结果（带上当前筛选条件和搜索关键词）
        const filterJson = getFilterJson()
        const keyword = options.searchKeyword ? options.searchKeyword() : ''
        const filteredResult = await options.fetchAllData({
          page: 1,
          size: 10000,
          filter: filterJson,
          keyword: keyword || undefined
        })
        return filteredResult.data || []
    }
  }

  // 执行导出
  // scope 参数可选：如果传入则直接使用，否则从 exportForm.value.scope 读取
  const executeExport = async (scope?: string) => {
    exporting.value = true

    try {
      const currentScope = scope || exportForm.value.scope
      const exportData = await fetchDataForExport(currentScope)

      console.log('=== 导出调试 ===')
      console.log('导出范围(参数):', scope)
      console.log('导出范围(exportForm.scope):', exportForm.value.scope)
      console.log('实际使用范围:', currentScope)
      console.log('导出数据条数:', exportData.length)

      if (exportData.length === 0) {
        ElMessage.warning('没有数据可导出')
        exporting.value = false
        return
      }

      // 调用后端导出API
      const exportResponse = await fetch('/api/data/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          table_name: getTableName(),
          data: exportData,
          format: exportForm.value.format,
          filename: exportForm.value.filename || getTableName(),
          path: ''
        })
      })

      if (exportResponse.ok) {
        const blob = await exportResponse.blob()
        const filename = exportForm.value.filename || getTableName()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename + '.' + (exportForm.value.format === 'pdf' ? 'pdf' : 'xlsx')
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)

        ElMessage.success('导出成功')
        exportDialogVisible.value = false
      } else {
        const error = await exportResponse.json()
        ElMessage.error(error.detail || '导出失败')
      }
    } catch (error: any) {
      console.error('导出失败:', error)
      ElMessage.error(error.message || '导出失败')
    } finally {
      exporting.value = false
    }
  }

  return {
    // 状态
    exportDialogVisible,
    exporting,
    exportForm,

    // 方法
    openExport,
    executeExport,
    getCurrentDate,
    getFilterJson
  }
}