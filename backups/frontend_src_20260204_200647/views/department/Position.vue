<template>
  <div class="position-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><Briefcase /></el-icon>
          <span>职位管理</span>
        </div>
      </template>
      <div class="card-content">
        <el-button type="primary" class="add-button">
          <el-icon><Plus /></el-icon>
          新增职位
        </el-button>
        <el-button type="success" class="import-button">
          <el-icon><Upload /></el-icon>
          导入职位
        </el-button>
        <el-button type="info" class="export-button">
          <el-icon><Download /></el-icon>
          导出职位
        </el-button>
        
        <el-divider />
        
        <el-form :inline="true" class="search-form">
          <el-form-item label="职位名称">
            <el-input placeholder="请输入职位名称" />
          </el-form-item>
          <el-form-item label="部门">
            <el-select placeholder="请选择部门">
              <el-option label="教育局" value="education" />
              <el-option label="第一中学" value="school1" />
              <el-option label="第二中学" value="school2" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="positionList" style="width: 100%">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="name" label="职位名称" width="150" />
          <el-table-column prop="department" label="所属部门" width="150" />
          <el-table-column prop="code" label="职位代码" width="120" />
          <el-table-column prop="level" label="职位等级" width="100" />
          <el-table-column prop="description" label="职位描述" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" type="primary">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button size="small" type="success">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          class="pagination"
          layout="total, sizes, prev, pager, next, jumper"
          :total="150"
          :page-size="10"
          :page-sizes="[10, 20, 50, 100]"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Briefcase, Plus, Upload, Download, Search, View, Edit, Delete } from '@element-plus/icons-vue'

const positionList = ref([
  {
    name: '局长',
    department: '教育局',
    code: 'DIR',
    level: '1',
    description: '教育局负责人'
  },
  {
    name: '副局长',
    department: '教育局',
    code: 'DEP_DIR',
    level: '2',
    description: '教育局副职'
  },
  {
    name: '校长',
    department: '第一中学',
    code: 'PRIN',
    level: '2',
    description: '第一中学校长'
  },
  {
    name: '副校长',
    department: '第一中学',
    code: 'DEP_PRIN',
    level: '3',
    description: '第一中学副校长'
  }
])
</script>

<style scoped>
.position-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.card-content {
  padding-top: 20px;
}

.add-button,
.import-button,
.export-button {
  margin-right: 10px;
}

.search-form {
  margin: 20px 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>