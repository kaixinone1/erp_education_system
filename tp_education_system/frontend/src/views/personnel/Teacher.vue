<template>
  <div class="teacher-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>教师信息管理</span>
        </div>
      </template>
      <div class="card-content">
        <el-button type="primary" class="add-button">
          <el-icon><Plus /></el-icon>
          新增教师
        </el-button>
        <el-button type="success" class="import-button">
          <el-icon><Upload /></el-icon>
          导入教师
        </el-button>
        <el-button type="info" class="export-button">
          <el-icon><Download /></el-icon>
          导出教师
        </el-button>
        
        <el-divider />
        
        <el-form :inline="true" class="search-form">
          <el-form-item label="姓名">
            <el-input placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="部门">
            <el-select placeholder="请选择部门">
              <el-option label="教育局" value="education" />
              <el-option label="第一中学" value="school1" />
              <el-option label="第二中学" value="school2" />
            </el-select>
          </el-form-item>
          <el-form-item label="职称">
            <el-select placeholder="请选择职称">
              <el-option label="教授" value="professor" />
              <el-option label="副教授" value="associate" />
              <el-option label="讲师" value="lecturer" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-table :data="teacherList" style="width: 100%">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="gender" label="性别" width="80" />
          <el-table-column prop="age" label="年龄" width="80" />
          <el-table-column prop="department" label="部门" width="150" />
          <el-table-column prop="title" label="职称" width="120" />
          <el-table-column prop="phone" label="电话" width="150" />
          <el-table-column prop="email" label="邮箱" width="200" />
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
          :total="1000"
          :page-size="10"
          :page-sizes="[10, 20, 50, 100]"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Plus, Upload, Download, Search, View, Edit, Delete } from '@element-plus/icons-vue'

const teacherList = ref([
  {
    name: '张三',
    gender: '男',
    age: 35,
    department: '第一中学',
    title: '讲师',
    phone: '13800138001',
    email: 'zhangsan@example.com'
  },
  {
    name: '李四',
    gender: '女',
    age: 42,
    department: '第二中学',
    title: '副教授',
    phone: '13800138002',
    email: 'lisi@example.com'
  },
  {
    name: '王五',
    gender: '男',
    age: 28,
    department: '教育局',
    title: '讲师',
    phone: '13800138003',
    email: 'wangwu@example.com'
  }
])
</script>

<style scoped>
.teacher-page {
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