<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </div>
      </template>
      <div class="card-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本设置" name="basic">
            <el-form :inline="false" class="settings-form">
              <el-form-item label="系统名称">
                <el-input placeholder="请输入系统名称" value="太平镇教育人事管理系统" />
              </el-form-item>
              <el-form-item label="系统版本">
                <el-input placeholder="请输入系统版本" value="v1.0.0" disabled />
              </el-form-item>
              <el-form-item label="系统描述">
                <el-input
                  type="textarea"
                  placeholder="请输入系统描述"
                  value="太平镇教育人事管理系统，用于管理全镇教育系统的人事信息"
                  :rows="3"
                />
              </el-form-item>
              <el-form-item label="版权信息">
                <el-input placeholder="请输入版权信息" value="© 2026 太平镇教育局" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary">
                  <el-icon><Check /></el-icon>
                  保存设置
                </el-button>
                <el-button>
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="用户管理" name="user">
            <el-button type="primary" class="add-button">
              <el-icon><Plus /></el-icon>
              新增用户
            </el-button>
            <el-table :data="userList" style="width: 100%">
              <el-table-column type="selection" width="50" />
              <el-table-column prop="username" label="用户名" width="150" />
              <el-table-column prop="name" label="姓名" width="120" />
              <el-table-column prop="role" label="角色" width="100" />
              <el-table-column prop="department" label="部门" width="150" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-switch v-model="scope.row.status" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" type="primary">
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
          </el-tab-pane>
          
          <el-tab-pane label="角色管理" name="role">
            <el-button type="primary" class="add-button">
              <el-icon><Plus /></el-icon>
              新增角色
            </el-button>
            <el-table :data="roleList" style="width: 100%">
              <el-table-column prop="name" label="角色名称" width="150" />
              <el-table-column prop="description" label="角色描述" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" type="primary">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button size="small" type="success">
                    <el-icon><Key /></el-icon>
                    权限
                  </el-button>
                  <el-button size="small" type="danger">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="系统日志" name="log">
            <el-form :inline="true" class="search-form">
              <el-form-item label="用户">
                <el-select placeholder="请选择用户">
                  <el-option label="全部" value="all" />
                  <el-option label="管理员" value="admin" />
                </el-select>
              </el-form-item>
              <el-form-item label="操作类型">
                <el-select placeholder="请选择操作类型">
                  <el-option label="全部" value="all" />
                  <el-option label="登录" value="login" />
                  <el-option label="修改" value="update" />
                  <el-option label="删除" value="delete" />
                </el-select>
              </el-form-item>
              <el-form-item label="日期范围">
                <el-date-picker
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </el-form-item>
            </el-form>
            <el-table :data="logList" style="width: 100%">
              <el-table-column prop="time" label="操作时间" width="200" />
              <el-table-column prop="user" label="操作用户" width="150" />
              <el-table-column prop="action" label="操作类型" width="120" />
              <el-table-column prop="description" label="操作描述" />
              <el-table-column prop="ip" label="IP地址" width="150" />
            </el-table>
            <el-pagination
              class="pagination"
              layout="total, sizes, prev, pager, next, jumper"
              :total="1000"
              :page-size="10"
              :page-sizes="[10, 20, 50, 100]"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Setting, Check, Refresh, Plus, Edit, Delete, Key, Search } from '@element-plus/icons-vue'

const activeTab = ref('basic')

const userList = ref([
  {
    username: 'admin',
    name: '管理员',
    role: 'admin',
    department: '教育局',
    status: true
  },
  {
    username: 'user1',
    name: '张三',
    role: 'user',
    department: '第一中学',
    status: true
  }
])

const roleList = ref([
  {
    name: '管理员',
    description: '系统管理员，拥有所有权限'
  },
  {
    name: '普通用户',
    description: '普通用户，拥有基本操作权限'
  }
])

const logList = ref([
  {
    time: '2026-01-30 10:00:00',
    user: 'admin',
    action: '登录',
    description: '管理员登录系统',
    ip: '192.168.1.1'
  },
  {
    time: '2026-01-30 09:30:00',
    user: 'user1',
    action: '修改',
    description: '修改教师信息',
    ip: '192.168.1.2'
  }
])
</script>

<style scoped>
.settings-page {
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

.settings-form {
  max-width: 600px;
}

.add-button {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>