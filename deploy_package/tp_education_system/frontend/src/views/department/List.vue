<template>
  <div class="department-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><OfficeBuilding /></el-icon>
          <span>部门管理</span>
        </div>
      </template>
      <div class="card-content">
        <el-button type="primary" class="add-button">
          <el-icon><Plus /></el-icon>
          新增部门
        </el-button>
        <el-button type="success" class="import-button">
          <el-icon><Upload /></el-icon>
          导入部门
        </el-button>
        <el-button type="info" class="export-button">
          <el-icon><Download /></el-icon>
          导出部门
        </el-button>
        
        <el-divider />
        
        <el-form :inline="true" class="search-form">
          <el-form-item label="部门名称">
            <el-input placeholder="请输入部门名称" />
          </el-form-item>
          <el-form-item label="上级部门">
            <el-select placeholder="请选择上级部门">
              <el-option label="无" value="none" />
              <el-option label="教育局" value="education" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="departmentList" style="width: 100%">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="name" label="部门名称" width="150" />
          <el-table-column prop="parent" label="上级部门" width="150" />
          <el-table-column prop="code" label="部门代码" width="120" />
          <el-table-column prop="leader" label="负责人" width="120" />
          <el-table-column prop="phone" label="联系电话" width="150" />
          <el-table-column prop="description" label="部门描述" />
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
          :total="100"
          :page-size="10"
          :page-sizes="[10, 20, 50, 100]"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { OfficeBuilding, Plus, Upload, Download, Search, View, Edit, Delete } from '@element-plus/icons-vue'

const departmentList = ref([
  {
    name: '教育局',
    parent: '无',
    code: 'EDU',
    leader: '张三',
    phone: '13800138001',
    description: '负责全镇教育管理工作'
  },
  {
    name: '第一中学',
    parent: '教育局',
    code: 'SCH001',
    leader: '李四',
    phone: '13800138002',
    description: '镇属初级中学'
  },
  {
    name: '第二中学',
    parent: '教育局',
    code: 'SCH002',
    leader: '王五',
    phone: '13800138003',
    description: '镇属初级中学'
  }
])
</script>

<style scoped>
.department-page {
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