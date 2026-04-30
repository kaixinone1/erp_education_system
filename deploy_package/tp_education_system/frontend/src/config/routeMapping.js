/**
 * 路由映射配置 - 统一管理导航路径和路由路径
 * 
 * 原则：
 * 1. 所有路径在此定义，避免硬编码
 * 2. 导航配置和路由配置都引用此文件
 * 3. 修改路径只需修改此处
 */

export const ROUTE_MAPPING = {
  // 系统管理
  system: {
    path: '/system',
    children: {
      modules: '/system/module-mgt',
      tables: '/system/table-mgt',
      dictionaries: '/system/dictionaries'
    }
  },
  
  // 数据中心
  dataCenter: {
    path: '/data-center',
    children: {
      // 数据导入工作台
      import: '/import/workbench',
      // 表结构管理
      tableStructure: '/data/table-structure',
      // 数据清理
      dataCleanup: '/admin/data-cleanup'
    }
  },
  
  // 人事管理
  personnel: {
    path: '/personnel',
    children: {}
  },
  
  // 通用数据视图
  genericDataView: '/data/:tableName',
  moduleDataView: '/:moduleId/:tableName'
}

/**
 * 获取路由路径
 * @param {string} routeKey - 路由键名，如 'dataCenter.children.import'
 * @returns {string} 路由路径
 */
export function getRoutePath(routeKey) {
  const keys = routeKey.split('.')
  let result = ROUTE_MAPPING
  
  for (const key of keys) {
    if (result[key] === undefined) {
      console.error(`路由键不存在: ${routeKey}`)
      return ''
    }
    result = result[key]
  }
  
  return result
}

/**
 * 检查路径是否匹配
 * @param {string} navPath - 导航路径
 * @param {string} routePath - 路由路径
 * @returns {boolean} 是否匹配
 */
export function checkPathMatch(navPath, routePath) {
  // 处理动态路由参数
  const normalizedNav = navPath.replace(/\/:\w+/g, '')
  const normalizedRoute = routePath.replace(/\/:\w+/g, '')
  
  return normalizedNav === normalizedRoute
}

/**
 * 验证所有路径配置
 * @returns {Array} 不匹配的路径列表
 */
export function validateAllRoutes() {
  const mismatches = []
  
  // 这里可以添加自动验证逻辑
  // 对比导航配置和路由配置
  
  return mismatches
}
