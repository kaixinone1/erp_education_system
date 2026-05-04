<template>
  <div class="template-call-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模板调用管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 调用记录 -->
        <el-tab-pane label="调用记录" name="records">
          <el-table :data="callRecords" border>
            <el-table-column prop="template_name" label="模板名称" width="200" />
            <el-table-column prop="module_name" label="调用模块" width="150" />
            <el-table-column prop="call_time" label="调用时间" width="180" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="text" size="small" @click="viewDetail(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 调用统计 -->
        <el-tab-pane label="调用统计" name="statistics">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="never">
                <el-statistic title="总调用次数" :value="statistics.totalCalls" />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="never">
                <el-statistic title="今日调用" :value="statistics.todayCalls" />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="never">
                <el-statistic title="成功率" :value="statistics.successRate" suffix="%" />
              </el-card>
            </el-col>
          </el-row>

          <el-divider>热门模板</el-divider>

          <el-table :data="statistics.popularTemplates" border>
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="template_name" label="模板名称" width="200" />
            <el-table-column prop="call_count" label="调用次数" width="120" />
            <el-table-column prop="last_called" label="最后调用时间" width="180" />
          </el-table>
        </el-tab-pane>

        <!-- 权限管理 -->
        <el-tab-pane label="权限管理" name="permissions">
          <el-alert
            title="权限管理功能开发中..."
            type="info"
            :closable="false"
            show-icon
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('records')

const callRecords = ref([
  {
    template_name: '教师基础信息表',
    module_name: '人事管理',
    call_time: '2026-05-03 10:30:00',
    status: 'success'
  },
  {
    template_name: '退休呈报表',
    module_name: '退休管理',
    call_time: '2026-05-03 09:15:00',
    status: 'success'
  }
])

const statistics = reactive({
  totalCalls: 156,
  todayCalls: 23,
  successRate: 98.5,
  popularTemplates: [
    {
      rank: 1,
      template_name: '教师基础信息表',
      call_count: 89,
      last_called: '2026-05-03 10:30:00'
    },
    {
      rank: 2,
      template_name: '退休呈报表',
      call_count: 45,
      last_called: '2026-05-03 09:15:00'
    },
    {
      rank: 3,
      template_name: '绩效工资审批表',
      call_count: 22,
      last_called: '2026-05-02 16:45:00'
    }
  ]
})

const viewDetail = (row) => {
  ElMessage.info('查看详情功能开发中...')
}

onMounted(() => {
  // 加载调用记录和统计数据
})
</script>

<style scoped>
.template-call-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
