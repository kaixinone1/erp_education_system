/**
 * 表名管理器 - 管理中文表名和英文表名的双向映射
 */

// 本地缓存
const mappingCache = new Map()
let isInitialized = false

/**
 * 初始化表名管理器
 */
export async function initTableNameManager() {
  if (isInitialized) return
  
  try {
    // 从后端加载已有的表名映射
    const response = await fetch('http://127.0.0.1:8000/api/import/translate-table-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chinese_name: '测试', module_name: '' })
    })
    
    if (response.ok) {
      isInitialized = true
      console.log('表名管理器初始化成功')
    }
  } catch (error) {
    console.error('表名管理器初始化失败:', error)
  }
}

/**
 * 翻译中文表名为英文表名
 * @param {string} chineseName - 中文表名
 * @param {string} moduleName - 模块名称（可选）
 * @returns {Promise<string>} - 英文表名
 */
export async function translateTableName(chineseName, moduleName = '') {
  // 检查缓存
  const cacheKey = `${moduleName}_${chineseName}`
  if (mappingCache.has(cacheKey)) {
    return mappingCache.get(cacheKey)
  }
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/import/translate-table-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: chineseName,
        module_name: moduleName
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      const englishName = result.english_name
      
      // 缓存结果
      mappingCache.set(cacheKey, englishName)
      mappingCache.set(`${moduleName}_${englishName}`, chineseName)
      
      return englishName
    }
  } catch (error) {
    console.error('表名翻译失败:', error)
  }
  
  // 如果翻译失败，返回原始名称的简化版本
  return chineseName.toLowerCase().replace(/[^a-z0-9]/g, '_')
}

/**
 * 批量翻译字段名
 * @param {string[]} chineseFields - 中文字段名数组
 * @param {string} moduleName - 模块名称（可选）
 * @returns {Promise<Array>} - 字段映射数组
 */
export async function translateFieldNames(chineseFields, moduleName = '') {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/import/translate-field-names', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_fields: chineseFields,
        module_name: moduleName
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      return result.mappings
    }
  } catch (error) {
    console.error('字段翻译失败:', error)
  }
  
  // 如果翻译失败，返回简单的映射
  return chineseFields.map(field => ({
    source_field: field,
    target_field: field.toLowerCase().replace(/[^a-z0-9]/g, '_'),
    data_type: 'VARCHAR(255)',
    confidence: 'low'
  }))
}

/**
 * 根据英文表名获取中文表名
 * @param {string} englishName - 英文表名
 * @returns {string|null} - 中文表名
 */
export function getChineseTableName(englishName) {
  for (const [key, value] of mappingCache.entries()) {
    if (value === englishName && key.includes('_')) {
      return key.split('_').slice(1).join('_')
    }
  }
  return null
}

/**
 * 根据中文表名获取英文表名（从缓存）
 * @param {string} chineseName - 中文表名
 * @param {string} moduleName - 模块名称
 * @returns {string|null} - 英文表名
 */
export function getEnglishTableName(chineseName, moduleName = '') {
  const cacheKey = `${moduleName}_${chineseName}`
  return mappingCache.get(cacheKey) || null
}

/**
 * 清空缓存
 */
export function clearCache() {
  mappingCache.clear()
  isInitialized = false
}

/**
 * 获取所有缓存的映射
 * @returns {Map} - 缓存的映射
 */
export function getAllMappings() {
  return new Map(mappingCache)
}

export default {
  initTableNameManager,
  translateTableName,
  translateFieldNames,
  getChineseTableName,
  getEnglishTableName,
  clearCache,
  getAllMappings
}
