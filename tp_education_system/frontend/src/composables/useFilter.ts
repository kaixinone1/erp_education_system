/**
 * useFilter - 通用多条件筛选组合式函数
 * 
 * 提供统一的多条件筛选逻辑，支持：
 * - 动态添加/删除筛选条件
 * - 多种操作符（包含、等于、大于、为空等）
 * - 条件数组格式，与后端 data_routes.py 兼容
 * 
 * 使用方式：
 * const filter = useFilter({
 *   filterableFields: computed(() => [...]),  // 可选筛选字段列表
 *   onFilterChange: () => { loadData() }       // 筛选变化回调
 * })
 */
import { ref, computed } from 'vue'

export interface FilterCondition {
  field: string
  operator: string
  value: string
}

export interface UseFilterOptions {
  /** 可筛选字段列表（响应式） */
  filterableFields?: () => Array<{ name: string; label?: string; source_name?: string; type?: string }>
  /** 筛选条件变化时的回调 */
  onFilterChange?: () => void
}

export function useFilter(options: UseFilterOptions = {}) {
  const showFilter = ref(false)
  const filterConditions = ref<FilterCondition[]>([])

  // 兼容旧代码：从 filterConditions 计算 filterForm
  const filterForm = computed(() => {
    const form: Record<string, any> = {}
    filterConditions.value.forEach(c => {
      if (c.field && c.operator && (c.value || c.operator === 'is_null' || c.operator === 'is_not_null')) {
        form[c.field] = c.value || ''
      }
    })
    return form
  })

  // 获取当前激活的筛选条件
  const activeConditions = computed(() => {
    return filterConditions.value.filter(
      c => c.field && c.operator && (c.value || c.operator === 'is_null' || c.operator === 'is_not_null')
    )
  })

  // 是否有激活的筛选条件
  const hasActiveFilter = computed(() => activeConditions.value.length > 0)

  // 切换筛选面板显示
  const toggleFilter = () => {
    showFilter.value = !showFilter.value
  }

  // 添加筛选条件
  const addFilterCondition = () => {
    filterConditions.value.push({
      field: '',
      operator: 'contains',
      value: ''
    })
  }

  // 删除筛选条件
  const removeFilterCondition = (index: number) => {
    filterConditions.value.splice(index, 1)
  }

  // 筛选字段变化时自动设置默认操作符
  const onFilterFieldChange = (index: number) => {
    const condition = filterConditions.value[index]
    if (condition && !condition.operator) {
      condition.operator = 'contains'
    }
  }

  // 应用筛选
  const applyFilter = () => {
    if (options.onFilterChange) {
      options.onFilterChange()
    }
  }

  // 重置筛选
  const resetFilter = () => {
    filterConditions.value = []
    applyFilter()
  }

  // 构建筛选参数（URLSearchParams 格式）
  const buildFilterParams = (): URLSearchParams => {
    const params = new URLSearchParams()
    if (activeConditions.value.length > 0) {
      params.append('filter', JSON.stringify(activeConditions.value))
    }
    return params
  }

  // 获取筛选条件的 JSON 字符串
  const getFilterJson = (): string | null => {
    if (activeConditions.value.length > 0) {
      return JSON.stringify(activeConditions.value)
    }
    return null
  }

  return {
    // 状态
    showFilter,
    filterConditions,
    filterForm,
    activeConditions,
    hasActiveFilter,

    // 方法
    toggleFilter,
    addFilterCondition,
    removeFilterCondition,
    onFilterFieldChange,
    applyFilter,
    resetFilter,
    buildFilterParams,
    getFilterJson
  }
}