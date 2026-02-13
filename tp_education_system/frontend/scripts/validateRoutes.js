/**
 * 路由一致性检查工具
 * 
 * 使用方法:
 * node scripts/validateRoutes.js
 * 
 * 功能:
 * 1. 检查导航配置中的所有路径是否在路由配置中存在
 * 2. 检查路由配置中的所有路径是否在导航配置中被引用
 * 3. 输出不匹配的路径列表
 */

const fs = require('fs')
const path = require('path')

// 文件路径
const NAVIGATION_FILE = path.join(__dirname, '../src/config/navigation.json')
const ROUTER_FILE = path.join(__dirname, '../src/router/index.ts')

/**
 * 从导航配置中提取所有路径
 */
function extractNavPaths(navConfig) {
  const paths = []
  
  function traverse(node, parentPath = '') {
    if (node.path) {
      paths.push({
        id: node.id,
        title: node.title,
        path: node.path,
        type: node.type,
        parentPath
      })
    }
    
    if (node.children && Array.isArray(node.children)) {
      node.children.forEach(child => traverse(child, node.path || parentPath))
    }
  }
  
  if (navConfig.modules) {
    navConfig.modules.forEach(module => traverse(module))
  }
  
  return paths
}

/**
 * 从路由配置中提取所有路径
 */
function extractRoutePaths(routerContent) {
  const paths = []
  
  // 匹配 path: "/xxx" 或 path: '/xxx'
  const pathRegex = /path:\s*["']([^"']+)["']/g
  let match
  
  while ((match = pathRegex.exec(routerContent)) !== null) {
    paths.push(match[1])
  }
  
  return [...new Set(paths)] // 去重
}

/**
 * 验证路径一致性
 */
function validateRoutes() {
  console.log('='.repeat(80))
  console.log('路由一致性检查')
  console.log('='.repeat(80))
  
  // 读取导航配置
  let navConfig
  try {
    const navContent = fs.readFileSync(NAVIGATION_FILE, 'utf-8')
    navConfig = JSON.parse(navContent)
    console.log('\n✓ 导航配置加载成功')
  } catch (error) {
    console.error('\n✗ 导航配置加载失败:', error.message)
    return
  }
  
  // 读取路由配置
  let routerContent
  try {
    routerContent = fs.readFileSync(ROUTER_FILE, 'utf-8')
    console.log('✓ 路由配置加载成功')
  } catch (error) {
    console.error('✗ 路由配置加载失败:', error.message)
    return
  }
  
  // 提取路径
  const navPaths = extractNavPaths(navConfig)
  const routePaths = extractRoutePaths(routerContent)
  
  console.log(`\n导航路径数量: ${navPaths.length}`)
  console.log(`路由路径数量: ${routePaths.length}`)
  
  // 检查导航路径是否在路由中存在
  console.log('\n' + '-'.repeat(80))
  console.log('检查1: 导航路径是否在路由配置中存在')
  console.log('-'.repeat(80))
  
  const missingInRoutes = []
  navPaths.forEach(nav => {
    // 处理动态路由参数，进行模糊匹配
    const normalizedNavPath = nav.path.replace(/\/:\w+/g, '')
    const found = routePaths.some(routePath => {
      const normalizedRoutePath = routePath.replace(/\/:\w+/g, '')
      return normalizedRoutePath === normalizedNavPath || 
             routePath === nav.path
    })
    
    if (!found) {
      missingInRoutes.push(nav)
      console.log(`✗ [${nav.type}] ${nav.title} (${nav.id}): ${nav.path}`)
    }
  })
  
  if (missingInRoutes.length === 0) {
    console.log('✓ 所有导航路径都在路由配置中找到了匹配')
  } else {
    console.log(`\n发现 ${missingInRoutes.length} 个导航路径在路由配置中缺失`)
  }
  
  // 检查路由路径是否在导航中被引用
  console.log('\n' + '-'.repeat(80))
  console.log('检查2: 路由路径是否在导航配置中被引用')
  console.log('-'.repeat(80))
  
  const missingInNav = []
  routePaths.forEach(routePath => {
    // 跳过动态路由和参数路由
    if (routePath.includes(':')) {
      return
    }
    
    const found = navPaths.some(nav => nav.path === routePath)
    if (!found) {
      missingInNav.push(routePath)
      console.log(`⚠ 路由路径未被导航引用: ${routePath}`)
    }
  })
  
  if (missingInNav.length === 0) {
    console.log('✓ 所有路由路径都在导航配置中被引用')
  } else {
    console.log(`\n发现 ${missingInNav.length} 个路由路径未被导航引用（可能是动态路由）`)
  }
  
  // 总结
  console.log('\n' + '='.repeat(80))
  console.log('检查结果总结')
  console.log('='.repeat(80))
  
  if (missingInRoutes.length === 0 && missingInNav.length === 0) {
    console.log('✓ 所有路径配置一致，检查通过！')
  } else {
    console.log(`✗ 发现配置不一致：
  - 导航路径缺失: ${missingInRoutes.length} 个
  - 路由路径未引用: ${missingInNav.length} 个`)
    process.exit(1)
  }
}

// 执行检查
validateRoutes()
