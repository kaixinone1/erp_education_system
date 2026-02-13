<template>
  <div class="module-management">
    <el-card class="box-card" style="height: calc(100vh - 120px);">
      <template #header>
        <div class="card-header">
          <span>模块管理</span>
          <div class="header-buttons">
            <el-button size="small" @click="handleCancel">取消</el-button>
            <el-button type="primary" size="small" @click="handleSave">保存配置</el-button>
          </div>
        </div>
      </template>
      <div class="card-body">
        <el-container style="height: 100%;">
          <el-aside width="300px" style="border-right: 1px solid #eaeef1;">
            <div class="tree-container">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0;">导航树结构</h3>
                <div>
                  <el-button type="primary" size="small" @click="addMainModule">
                    <el-icon><Plus /></el-icon>
                    新增主模块
                  </el-button>
                </div>
              </div>
              
              <el-tree
                ref="tree"
                :data="navigationData"
                :props="treeProps"
                node-key="id"
                default-expand-all
                draggable
                @node-click="handleNodeClick"
                @node-drop="handleNodeDrop"
              >
                <template #default="{ node, data }">
                  <span class="tree-node">
                    <el-icon :size="16">
                      <component :is="getNodeIcon(data)" />
                    </el-icon>
                    <span class="node-label">{{ data.title }}</span>
                  </span>
                </template>
              </el-tree>
              

            </div>
          </el-aside>
          <el-main>
            <div class="properties-container">
              <h3 style="margin: 0 0 15px 0;">节点属性</h3>
              <div v-if="!selectedNode" class="empty-state">
                <p>请选择一个节点查看或编辑属性</p>
              </div>
              <div v-else>
                <!-- 节点属性编辑表单 -->
                <el-form label-width="100px">
                  <el-form-item label="节点名称">
                    <el-input v-model="selectedNode.title" placeholder="请输入节点名称" />
                  </el-form-item>
                  <el-form-item label="节点ID">
                    <el-input v-model="selectedNode.id" placeholder="请输入节点ID" disabled />
                  </el-form-item>
                  <el-form-item label="节点类型">
                    <el-select v-model="selectedNode.type" placeholder="请选择节点类型" @change="handleTypeChange">
                      <el-option label="📁 模块（文件夹）" value="module">
                        <span style="display: flex; align-items: center;">
                          <el-icon style="margin-right: 8px;"><Folder /></el-icon>
                          <span>模块（文件夹）- 用于组织子模块</span>
                        </span>
                      </el-option>
                      <el-option label="📊 数据节点" value="component">
                        <span style="display: flex; align-items: center;">
                          <el-icon style="margin-right: 8px;"><Document /></el-icon>
                          <span>数据节点 - 挂载数据管理器</span>
                        </span>
                      </el-option>
                      <el-option label="📈 报表节点" value="report">
                        <span style="display: flex; align-items: center;">
                          <el-icon style="margin-right: 8px;"><PieChart /></el-icon>
                          <span>报表节点 - 显示报表</span>
                        </span>
                      </el-option>
                    </el-select>
                  </el-form-item>
                  
                  <!-- 类型说明提示 -->
                  <el-alert
                    v-if="selectedNode.type === 'module'"
                    title="模块（文件夹）类型说明"
                    type="info"
                    :closable="false"
                    style="margin-bottom: 15px;"
                  >
                    <div style="font-size: 12px; line-height: 1.6;">
                      <p>• 用于组织和管理子模块</p>
                      <p>• 点击后展开子菜单，不显示数据</p>
                      <p>• 示例：系统管理、字典管理、教师管理</p>
                    </div>
                  </el-alert>
                  
                  <el-alert
                    v-if="selectedNode.type === 'component'"
                    title="数据节点类型说明"
                    type="success"
                    :closable="false"
                    style="margin-bottom: 15px;"
                  >
                    <div style="font-size: 12px; line-height: 1.6;">
                      <p>• 用于显示和管理数据</p>
                      <p>• 点击后显示数据管理器（增删改查）</p>
                      <p>• 必须关联数据表</p>
                      <p>• 示例：教师基础信息、教师学历记录</p>
                    </div>
                  </el-alert>
                  
                  <el-alert
                    v-if="selectedNode.type === 'report'"
                    title="报表节点类型说明"
                    type="warning"
                    :closable="false"
                    style="margin-bottom: 15px;"
                  >
                    <div style="font-size: 12px; line-height: 1.6;">
                      <p>• 用于显示报表</p>
                      <p>• 点击后显示报表界面</p>
                      <p>• 必须关联报表配置</p>
                    </div>
                  </el-alert>
                  <el-form-item label="节点路径">
                    <el-input v-model="selectedNode.path" placeholder="请输入节点路径" />
                  </el-form-item>
                  <el-form-item label="节点图标">
                    <el-select v-model="selectedNode.icon" placeholder="请选择节点图标">
                      <el-option label="设置" value="Setting" />
                      <el-option label="网格" value="Grid" />
                      <el-option label="文件夹" value="Folder" />
                      <el-option label="文档" value="Document" />
                      <el-option label="饼图" value="PieChart" />
                      <el-option label="星标" value="Star" />
                    </el-select>
                  </el-form-item>
                  
                  <!-- 数据节点特有属性 -->
                  <el-form-item v-if="selectedNode.type === 'component'" label="组件名称">
                    <el-input v-model="selectedNode.component" placeholder="请输入组件名称" />
                  </el-form-item>
                  
                  <!-- 数据节点关联数据表 -->
                  <el-form-item v-if="selectedNode.type === 'component'" label="关联数据表">
                    <el-select v-model="selectedNode.table" placeholder="请选择关联数据表">
                      <el-option label="人员表" value="personnel" />
                      <el-option label="部门表" value="department" />
                      <el-option label="工资表" value="salary" />
                      <el-option label="考勤表" value="attendance" />
                    </el-select>
                  </el-form-item>
                  
                  <!-- 报表节点特有属性 -->
                  <el-form-item v-if="selectedNode.type === 'report'" label="报表名称">
                    <el-input v-model="selectedNode.report" placeholder="请输入报表名称" />
                  </el-form-item>
                  
                  <!-- 报表节点关联报表 -->
                  <el-form-item v-if="selectedNode.type === 'report'" label="关联报表">
                    <el-select v-model="selectedNode.reportId" placeholder="请选择关联报表">
                      <el-option label="人员报表" value="personnelReport" />
                      <el-option label="部门报表" value="departmentReport" />
                      <el-option label="工资报表" value="salaryReport" />
                      <el-option label="考勤报表" value="attendanceReport" />
                    </el-select>
                  </el-form-item>
                </el-form>
                
                <!-- 节点操作按钮区域 -->
                <div v-if="selectedNode" class="node-actions" style="margin-top: 20px; padding: 15px; border: 1px solid #eaeef1; border-radius: 4px; background-color: #f9fafc;">
                  <h4 style="margin: 0 0 15px 0; color: #606266; font-size: 14px; font-weight: 500;">节点操作</h4>
                  <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <el-button size="small" @click="addSubModule">
                      <el-icon><Plus /></el-icon>
                      新增子模块
                    </el-button>
                    <el-button size="small" @click="addDataNode">
                      <el-icon><Plus /></el-icon>
                      新增数据节点
                    </el-button>
                    <el-button size="small" @click="addReportNode">
                      <el-icon><Plus /></el-icon>
                      新增报表节点
                    </el-button>
                    <el-button size="small" @click="renameNode">
                      <el-icon><Edit /></el-icon>
                      重命名
                    </el-button>
                    <el-button size="small" type="danger" @click="deleteNode">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-main>
        </el-container>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import {
  Setting,
  Grid,
  Folder,
  Document,
  Star,
  Plus,
  Edit,
  Delete,
  PieChart
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { eventBus, EVENT_TAGS_UPDATED } from '@/utils/eventBus'

// 元模块配置 - 仅系统管理和模块管理
const getMetaModules = () => [
  {
    id: "system",
    title: "系统管理",
    icon: "Setting",
    path: "/system",
    type: "module",
    children: [
      {
        id: "system-modules",
        title: "模块管理",
        icon: "Grid",
        path: "/system/module-mgt",
        type: "component",
        component: "Modules",
        api_endpoint: "/api/data/modules"
      }
    ]
  }
]

const navigationData = ref([])
const selectedNode = ref(null)
const tree = ref(null)

// 树节点属性配置
const treeProps = {
  children: 'children',
  label: 'title'
}

// 根据节点属性获取图标
const getNodeIcon = (data) => {
  if (data.type === 'module') {
    return Setting
  } else if (data.type === 'component') {
    return Grid
  } else if (data.type === 'report') {
    return Document
  } else {
    return Folder
  }
}

// 从后端API获取导航数据
const loadNavigationData = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/navigation-admin/tree')
    if (response.ok) {
      const data = await response.json()
      if (data.modules && data.modules.length > 0) {
        navigationData.value = data.modules
      } else {
        // 如果后端返回空数据，使用默认数据
        navigationData.value = defaultNavigationData
      }
    } else {
      console.error('获取导航数据失败:', response.status)
      // 使用默认数据
      navigationData.value = defaultNavigationData
    }
  } catch (error) {
    console.error('加载导航数据失败:', error)
    ElMessage.error('加载导航数据失败，请检查后端服务')
    // 只有在没有数据时才使用元模块
    if (navigationData.value.length === 0) {
      navigationData.value = getMetaModules()
    }
  }
}

// 处理节点点击事件
const handleNodeClick = (data) => {
  selectedNode.value = data
}

// 获取节点的根路径（用于生成新节点的路径）
const getRootPath = (node) => {
  // 如果是顶级节点，使用其path
  if (!node) return ''
  
  // 找到顶级模块的路径
  let rootPath = ''
  const findRoot = (nodes, targetId) => {
    for (const n of nodes) {
      if (n.id === targetId) {
        return n.path
      }
      if (n.children) {
        const found = findRoot(n.children, targetId)
        if (found) return found
      }
    }
    return null
  }
  
  // 从navigationData中找到当前节点所属的顶级模块
  for (const module of navigationData.value) {
    if (module.id === node.id) {
      // 当前节点就是顶级模块
      rootPath = module.path
      break
    }
    if (module.children) {
      const found = findRoot(module.children, node.id)
      if (found) {
        rootPath = module.path
        break
      }
    }
  }
  
  return rootPath
}

// 新增主模块
const addMainModule = () => {
  const timestamp = Date.now()
  const newModule = {
    id: `module-${timestamp}`,
    title: '新主模块',
    icon: 'Setting',
    path: `/module-${timestamp}`,
    type: 'module',
    children: []
  }
  
  navigationData.value.push(newModule)
  console.log('新增主模块:', newModule)
  ElMessage.success('主模块新增成功')
}

// 新增子模块
const addSubModule = () => {
  if (!selectedNode.value) return
  
  const timestamp = Date.now()
  const rootPath = getRootPath(selectedNode.value)
  const newPath = `${rootPath}/sub-${timestamp}`
  
  const newModule = {
    id: `module-${timestamp}`,
    title: '新子模块',
    icon: 'Setting',
    path: newPath,
    type: 'module',
    children: []
  }
  
  if (!selectedNode.value.children) {
    selectedNode.value.children = []
  }
  
  selectedNode.value.children.push(newModule)
  console.log('新增子模块:', newModule)
  ElMessage.success('子模块新增成功')
}

// 新增数据节点
const addDataNode = () => {
  if (!selectedNode.value) return
  
  const timestamp = Date.now()
  const rootPath = getRootPath(selectedNode.value)
  const newPath = `${rootPath}/data-${timestamp}`
  
  const newNode = {
    id: `data-${timestamp}`,
    title: '新数据节点',
    icon: 'Document',
    path: newPath,
    type: 'component',
    component: 'DataComponent'
  }
  
  if (!selectedNode.value.children) {
    selectedNode.value.children = []
  }
  
  selectedNode.value.children.push(newNode)
  console.log('新增数据节点:', newNode)
  ElMessage.success('数据节点新增成功')
}

// 新增报表节点
const addReportNode = () => {
  if (!selectedNode.value) return
  
  const timestamp = Date.now()
  const rootPath = getRootPath(selectedNode.value)
  const newPath = `${rootPath}/report-${timestamp}`
  
  const newNode = {
    id: `report-${timestamp}`,
    title: '新报表节点',
    icon: 'PieChart',
    path: newPath,
    type: 'report',
    report: 'ReportComponent'
  }
  
  if (!selectedNode.value.children) {
    selectedNode.value.children = []
  }
  
  selectedNode.value.children.push(newNode)
  console.log('新增报表节点:', newNode)
  ElMessage.success('报表节点新增成功')
}

// 重命名节点
const renameNode = () => {
  if (!selectedNode.value) return
  
  const newTitle = prompt('请输入新的节点名称:', selectedNode.value.title)
  if (newTitle && newTitle.trim()) {
    const oldTitle = selectedNode.value.title
    selectedNode.value.title = newTitle.trim()
    console.log('重命名节点:', { oldTitle, newTitle: selectedNode.value.title })
    ElMessage.success('节点重命名成功')
  }
}

// 删除节点
const deleteNode = () => {
  if (!selectedNode.value) return
  
  // 安全检查：如果是模块且有子节点，阻止删除
  if (selectedNode.value.type === 'module' && selectedNode.value.children && selectedNode.value.children.length > 0) {
    ElMessage.warning('该模块下包含子节点，请先处理所有子节点后再删除模块。')
    return
  }
  
  if (confirm('确定要删除该节点吗？')) {
    const nodeTitle = selectedNode.value.title
    
    // 查找并删除节点
    const removeNode = (nodes, nodeId) => {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].id === nodeId) {
          nodes.splice(i, 1)
          return true
        }
        if (nodes[i].children) {
          if (removeNode(nodes[i].children, nodeId)) {
            return true
          }
        }
      }
      return false
    }
    
    const success = removeNode(navigationData.value, selectedNode.value.id)
    if (success) {
      selectedNode.value = null
      console.log('删除节点:', nodeTitle)
      ElMessage.success('节点删除成功')
    } else {
      ElMessage.error('节点删除失败')
    }
  }
}

// 添加全局点击事件监听器
onMounted(() => {
  loadNavigationData()
})

// 移除全局点击事件监听器
onUnmounted(() => {
})

// 处理节点拖拽结束事件
const handleNodeDrop = (draggedNode, dropNode, dropType) => {
  console.log('拖拽结束:', {
    draggedNode: draggedNode.data,
    dropNode: dropNode.data,
    dropType
  })
  
  try {
    // 保存被拖拽的节点数据
    const draggedNodeData = draggedNode.data
    
    // 从原位置移除节点
    const removeNode = (nodes, nodeId) => {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].id === nodeId) {
          return nodes.splice(i, 1)[0]
        }
        if (nodes[i].children) {
          const removed = removeNode(nodes[i].children, nodeId)
          if (removed) {
            return removed
          }
        }
      }
      return null
    }
    
    // 从导航数据中移除被拖拽的节点
    const removedNode = removeNode(navigationData.value, draggedNodeData.id)
    
    if (!removedNode) {
      console.error('未找到要移除的节点:', draggedNodeData.id)
      return
    }
    
    console.log('成功从原位置移除节点:', removedNode)
    
    // 根据拖拽类型处理节点放置
    switch (dropType) {
      case 'before':
      case 'after':
        // 放置到兄弟节点位置
        if (dropNode.parent.data) {
          // 有父节点，作为兄弟节点添加
          const parent = dropNode.parent.data
          if (!parent.children) {
            parent.children = []
          }
          const dropIndex = parent.children.findIndex(node => node.id === dropNode.data.id)
          if (dropIndex !== -1) {
            if (dropType === 'before') {
              parent.children.splice(dropIndex, 0, removedNode)
              console.log('将节点添加到兄弟节点前面:', { parent: parent.title, index: dropIndex })
            } else {
              parent.children.splice(dropIndex + 1, 0, removedNode)
              console.log('将节点添加到兄弟节点后面:', { parent: parent.title, index: dropIndex + 1 })
            }
          } else {
            console.error('未找到放置目标节点:', dropNode.data.id)
          }
        } else {
          // 无父节点，作为顶级节点添加
          const dropIndex = navigationData.value.findIndex(node => node.id === dropNode.data.id)
          if (dropIndex !== -1) {
            if (dropType === 'before') {
              navigationData.value.splice(dropIndex, 0, removedNode)
              console.log('将节点添加到顶级节点前面:', { index: dropIndex })
            } else {
              navigationData.value.splice(dropIndex + 1, 0, removedNode)
              console.log('将节点添加到顶级节点后面:', { index: dropIndex + 1 })
            }
          } else {
            console.error('未找到放置目标节点:', dropNode.data.id)
          }
        }
        break
      case 'inner':
        // 放置到子节点位置
        if (!dropNode.data.children) {
          dropNode.data.children = []
        }
        dropNode.data.children.push(removedNode)
        console.log('将节点添加到子节点位置:', { parent: dropNode.data.title })
        break
      default:
        console.error('未知的拖拽类型:', dropType)
    }
    
    console.log('拖拽完成，更新后的导航数据:', navigationData.value)
    ElMessage.success('节点拖拽成功')
  } catch (error) {
    console.error('拖拽处理出错:', error)
    ElMessage.error('节点拖拽失败，请重试')
  }
}

// 保存配置
const handleSave = async () => {
  try {
    // 构建完整的导航数据
    const navigationDataToSave = {
      modules: navigationData.value
    }
    
    // 发送PUT请求到后端API
    const response = await fetch('http://127.0.0.1:8000/api/navigation-admin/tree', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(navigationDataToSave)
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('保存成功:', result)
      // 显示保存成功的提示
      ElMessage.success('配置保存成功！')
      // 触发导航更新事件，通知TagsView检查并关闭已删除模块的标签
      eventBus.emit(EVENT_TAGS_UPDATED, { type: 'navigation_updated' })
    } else {
      console.error('保存失败:', response.status)
      ElMessage.error('配置保存失败，请重试')
    }
  } catch (error) {
    console.error('保存配置时出错:', error)
    ElMessage.error('保存时发生错误，请检查网络连接')
  }
}

// 取消操作
const handleCancel = async () => {
  try {
    // 重新加载导航数据，放弃当前修改
    await loadNavigationData()
    // 清除选中状态
    selectedNode.value = null
    // 显示取消成功的提示
    ElMessage.info('已取消当前操作')
  } catch (error) {
    console.error('取消操作时出错:', error)
  }
}

// 处理节点类型变更
const handleTypeChange = (newType: string) => {
  if (!selectedNode.value) return
  
  // 根据类型自动设置默认值
  switch (newType) {
    case 'module':
      // 模块类型：清除数据相关属性
      selectedNode.value.component = undefined
      selectedNode.value.table = undefined
      selectedNode.value.table_name = undefined
      selectedNode.value.report = undefined
      selectedNode.value.reportId = undefined
      // 设置默认图标
      if (!selectedNode.value.icon || selectedNode.value.icon === 'Document') {
        selectedNode.value.icon = 'Folder'
      }
      ElMessage.info('已切换为模块（文件夹）类型，用于组织子模块')
      break
      
    case 'component':
      // 数据节点类型：设置默认组件
      selectedNode.value.component = selectedNode.value.component || 'DataTable'
      selectedNode.value.report = undefined
      selectedNode.value.reportId = undefined
      // 设置默认图标
      if (!selectedNode.value.icon || selectedNode.value.icon === 'Folder') {
        selectedNode.value.icon = 'Document'
      }
      ElMessage.info('已切换为数据节点类型，将挂载数据管理器')
      break
      
    case 'report':
      // 报表节点类型：设置默认报表
      selectedNode.value.report = selectedNode.value.report || 'ReportComponent'
      selectedNode.value.component = undefined
      selectedNode.value.table = undefined
      selectedNode.value.table_name = undefined
      // 设置默认图标
      if (!selectedNode.value.icon || selectedNode.value.icon === 'Folder') {
        selectedNode.value.icon = 'PieChart'
      }
      ElMessage.info('已切换为报表节点类型，将显示报表')
      break
  }
}

// 校验节点配置
const validateNode = (node: any): { valid: boolean; message: string } => {
  if (!node.type) {
    return { valid: false, message: '节点类型不能为空' }
  }
  
  switch (node.type) {
    case 'module':
      // 模块类型：校验通过，不需要额外属性
      return { valid: true, message: '' }
      
    case 'component':
      // 数据节点类型：必须有 component 和 table_name
      if (!node.component) {
        return { valid: false, message: '数据节点必须设置组件名称' }
      }
      if (!node.table && !node.table_name) {
        return { valid: false, message: '数据节点必须关联数据表' }
      }
      return { valid: true, message: '' }
      
    case 'report':
      // 报表节点类型：必须有 report 和 reportId
      if (!node.report) {
        return { valid: false, message: '报表节点必须设置报表名称' }
      }
      if (!node.reportId) {
        return { valid: false, message: '报表节点必须关联报表' }
      }
      return { valid: true, message: '' }
      
    default:
      return { valid: false, message: `未知的节点类型: ${node.type}` }
  }
}
</script>

<style scoped>
.module-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.card-body {
  height: calc(100% - 60px);
  padding: 0;
}

.tree-container {
  height: 100%;
  padding: 20px;
  overflow: auto;
  position: relative;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-size: 14px;
}

/* 拖拽相关样式 */
:deep(.el-tree-node__content) {
  cursor: move;
}

:deep(.el-tree-node.is-drop-inner) {
  background-color: #ecf5ff;
}

:deep(.el-tree-node.is-drop-before) {
  border-top: 2px solid #409eff;
}

:deep(.el-tree-node.is-drop-after) {
  border-bottom: 2px solid #409eff;
}

.tree-actions {
  background-color: #f9fafc;
}

.tree-actions h4 {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.properties-container {
  height: 100%;
  padding: 20px;
  overflow: auto;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
</style>
