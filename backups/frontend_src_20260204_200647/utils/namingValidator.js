/**
 * 命名验证器 - 验证表名和字段名的规范性
 */

// 命名规则配置
const NAMING_RULES = {
  // 表名规则
  table: {
    maxLength: 64,
    minLength: 1,
    allowedPattern: /^[a-z][a-z0-9_]*$/,
    reservedKeywords: [
      'id', 'name', 'title', 'created_at', 'updated_at',
      'status', 'type', 'code', 'value', 'user', 'admin',
      'table', 'column', 'database', 'schema', 'index'
    ],
    // 模块前缀规则
    modulePrefixes: {
      '人事管理': 'hr_',
      '工资管理': 'salary_',
      '党建管理': 'party_',
      '学生管理': 'student_',
      '系统管理': 'system_',
      '教师管理': 'teacher_',
      '数据中心': 'data_',
      '部门管理': 'dept_',
      '考勤管理': 'attendance_'
    }
  },
  // 字段名规则
  field: {
    maxLength: 64,
    minLength: 1,
    allowedPattern: /^[a-z][a-z0-9_]*$/,
    reservedKeywords: [
      'id', 'created_at', 'updated_at', 'deleted_at',
      'created_by', 'updated_by', 'deleted_by'
    ]
  }
}

/**
 * 验证表名
 * @param {string} name - 表名
 * @param {string} moduleName - 模块名称（可选）
 * @returns {Object} - 验证结果 { valid: boolean, errors: string[], warnings: string[] }
 */
export function validateTableName(name, moduleName = '') {
  const errors = []
  const warnings = []
  const rules = NAMING_RULES.table
  
  // 检查是否为空
  if (!name || name.trim() === '') {
    errors.push('表名不能为空')
    return { valid: false, errors, warnings }
  }
  
  const cleanName = name.trim().toLowerCase()
  
  // 检查长度
  if (cleanName.length > rules.maxLength) {
    errors.push(`表名长度不能超过${rules.maxLength}个字符`)
  }
  if (cleanName.length < rules.minLength) {
    errors.push(`表名长度不能少于${rules.minLength}个字符`)
  }
  
  // 检查字符规范
  if (!rules.allowedPattern.test(cleanName)) {
    errors.push('表名只能以小写字母开头，包含小写字母、数字和下划线')
  }
  
  // 检查保留关键字
  if (rules.reservedKeywords.includes(cleanName)) {
    errors.push(`"${cleanName}"是保留关键字，不能用作表名`)
  }
  
  // 检查是否包含连续下划线
  if (cleanName.includes('__')) {
    warnings.push('表名包含连续下划线，建议简化')
  }
  
  // 检查是否以下划线结尾
  if (cleanName.endsWith('_')) {
    warnings.push('表名以下划线结尾，建议移除')
  }
  
  // 检查模块前缀（如果提供了模块名）
  if (moduleName && rules.modulePrefixes[moduleName]) {
    const expectedPrefix = rules.modulePrefixes[moduleName]
    if (!cleanName.startsWith(expectedPrefix)) {
      warnings.push(`建议表名以"${expectedPrefix}"开头，以符合"${moduleName}"模块规范`)
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  }
}

/**
 * 验证字段名
 * @param {string} name - 字段名
 * @returns {Object} - 验证结果
 */
export function validateFieldName(name) {
  const errors = []
  const warnings = []
  const rules = NAMING_RULES.field
  
  // 检查是否为空
  if (!name || name.trim() === '') {
    errors.push('字段名不能为空')
    return { valid: false, errors, warnings }
  }
  
  const cleanName = name.trim().toLowerCase()
  
  // 检查长度
  if (cleanName.length > rules.maxLength) {
    errors.push(`字段名长度不能超过${rules.maxLength}个字符`)
  }
  if (cleanName.length < rules.minLength) {
    errors.push(`字段名长度不能少于${rules.minLength}个字符`)
  }
  
  // 检查字符规范
  if (!rules.allowedPattern.test(cleanName)) {
    errors.push('字段名只能以小写字母开头，包含小写字母、数字和下划线')
  }
  
  // 检查保留关键字
  if (rules.reservedKeywords.includes(cleanName)) {
    warnings.push(`"${cleanName}"是系统保留字段，建议更换`)
  }
  
  // 检查是否包含连续下划线
  if (cleanName.includes('__')) {
    warnings.push('字段名包含连续下划线，建议简化')
  }
  
  // 检查是否以下划线结尾
  if (cleanName.endsWith('_')) {
    warnings.push('字段名以下划线结尾，建议移除')
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  }
}

/**
 * 批量验证字段名
 * @param {string[]} names - 字段名数组
 * @returns {Object} - 验证结果
 */
export function validateFieldNames(names) {
  const results = []
  const allErrors = []
  const allWarnings = []
  
  for (const name of names) {
    const result = validateFieldName(name)
    results.push({ name, ...result })
    allErrors.push(...result.errors)
    allWarnings.push(...result.warnings)
  }
  
  return {
    valid: allErrors.length === 0,
    results,
    errors: allErrors,
    warnings: allWarnings
  }
}

/**
 * 获取模块前缀
 * @param {string} moduleName - 模块名称
 * @returns {string|null} - 模块前缀
 */
export function getModulePrefix(moduleName) {
  return NAMING_RULES.table.modulePrefixes[moduleName] || null
}

/**
 * 为表名添加模块前缀
 * @param {string} tableName - 表名
 * @param {string} moduleName - 模块名称
 * @returns {string} - 带前缀的表名
 */
export function addModulePrefix(tableName, moduleName) {
  const prefix = getModulePrefix(moduleName)
  if (!prefix) return tableName
  
  const cleanName = tableName.trim().toLowerCase()
  if (cleanName.startsWith(prefix)) {
    return cleanName
  }
  
  return prefix + cleanName
}

/**
 * 移除模块前缀
 * @param {string} tableName - 表名
 * @param {string} moduleName - 模块名称
 * @returns {string} - 移除前缀的表名
 */
export function removeModulePrefix(tableName, moduleName) {
  const prefix = getModulePrefix(moduleName)
  if (!prefix) return tableName
  
  const cleanName = tableName.trim().toLowerCase()
  if (cleanName.startsWith(prefix)) {
    return cleanName.substring(prefix.length)
  }
  
  return cleanName
}

/**
 * 格式化表名/字段名
 * @param {string} name - 原始名称
 * @returns {string} - 格式化后的名称
 */
export function formatName(name) {
  if (!name) return ''
  
  return name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '_')  // 非字母数字替换为下划线
    .replace(/_+/g, '_')          // 合并连续下划线
    .replace(/^_+|_+$/g, '')      // 移除首尾下划线
}

/**
 * 检查名称是否冲突
 * @param {string} name - 要检查的名称
 * @param {string[]} existingNames - 已有名称列表
 * @returns {boolean} - 是否冲突
 */
export function isNameConflict(name, existingNames) {
  const formattedName = formatName(name)
  return existingNames.some(existing => formatName(existing) === formattedName)
}

/**
 * 生成唯一名称
 * @param {string} baseName - 基础名称
 * @param {string[]} existingNames - 已有名称列表
 * @returns {string} - 唯一名称
 */
export function generateUniqueName(baseName, existingNames) {
  let name = formatName(baseName)
  let counter = 1
  
  while (isNameConflict(name, existingNames)) {
    name = `${formatName(baseName)}_${counter}`
    counter++
  }
  
  return name
}

export default {
  validateTableName,
  validateFieldName,
  validateFieldNames,
  getModulePrefix,
  addModulePrefix,
  removeModulePrefix,
  formatName,
  isNameConflict,
  generateUniqueName
}
