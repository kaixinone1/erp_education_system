<template>
  <div class="modules-container">
    <div class="modules-header">
      <h2 class="modules-title">
        <el-icon><Grid /></el-icon>
        模块管理
      </h2>
      <div class="modules-actions">
        <el-button type="primary">
          <el-icon><Plus /></el-icon>
          新增模块
        </el-button>
        <el-button>
          <el-icon><Upload /></el-icon>
          导入模块
        </el-button>
        <el-button>
          <el-icon><Download /></el-icon>
          导出模块
        </el-button>
      </div>
    </div>
    
    <div class="modules-content">
      <el-card class="modules-search-card">
        <el-form :inline="true" class="modules-search-form">
          <el-form-item label="模块名称">
            <el-input placeholder="请输入模块名称" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select placeholder="请选择状态">
              <el-option label="启用" value="enabled" />
              <el-option label="禁用" value="disabled" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button>
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <el-card class="modules-list-card">
        <el-table :data="modulesList" style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="模块名称" width="180" />
          <el-table-column prop="path" label="访问路径" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-switch v-model="scope.row.status" />
            </template>
          </el-table-column>
          <el-table-column prop="description" label="模块描述" />
          <el-table-column prop="createdAt" label="创建时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="modules-pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Grid, Plus, Upload, Download, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'

// 模拟模块数据
const modulesList = ref([
  {
    id: 1,
    name: '人事管理',
    path: '/personnel',
    status: true,
    description: '人员信息管理模块',
    createdAt: '2024-01-30 00:00:00'
  },
  {
    id: 2,
    name: '部门管理',
    path: '/department',
    status: true,
    description: '部门信息管理模块',
    createdAt: '2024-01-30 00:00:00'
  },
  {
    id: 3,
    name: '合同管理',
    path: '/contract',
    status: true,
    description: '合同信息管理模块',
    createdAt: '2024-01-30 00:00:00'
  },
  {
    id: 4,
    name: '绩效管理',
    path: '/performance',
    status: true,
    description: '绩效考核管理模块',
    createdAt: '2024-01-30 00:00:00'
  },
  {
    id: 5,
    name: '档案管理',
    path: '/archive',
    status: true,
    description: '档案信息管理模块',
    createdAt: '2024-01-30 00:00:00'
  }
])

// 分页数据
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(5)

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  console.log(`每页 ${size} 条`)
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
  console.log(`当前页: ${current}`)
}

// 编辑模块
const handleEdit = (row: any) => {
  console.log('编辑模块:', row)
}

// 删除模块
const handleDelete = (row: any) => {
  console.log('删除模块:', row)
}
</script>

<style scoped>
.modules-container {
  padding: 20px;
}

.modules-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modules-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.modules-actions {
  display: flex;
  gap: 10px;
}

.modules-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modules-search-card {
  margin-bottom: 20px;
}

.modules-search-form {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modules-list-card {
  min-height: 400px;
}

.modules-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
