<template>
  <div class="data-preview-panel">
    <h3>第三步：数据预览</h3>
    <el-divider></el-divider>
    
    <!-- 预览统计信息 -->
    <div class="preview-stats">
      <el-card shadow="hover" :body-style="{ padding: '10px' }">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">总记录数</div>
              <div class="stat-value">{{ totalRows }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">有效记录</div>
              <div class="stat-value" style="color: #67c23a;">{{ validRows }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">无效记录</div>
              <div class="stat-value" style="color: #f56c6c;">{{ invalidRows }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">警告记录</div>
              <div class="stat-value" style="color: #e6a23c;">{{ warningRows }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
    
    <!-- 数据预览表格 -->
    <div class="preview-table">
      <el-table
        :data="previewData"
        style="width: 100%"
        border
        height="500"
        :row-class-name="tableRowClassName"
      >
        <el-table-column
          v-for="column in tableColumns"
          :key="column.prop"
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
        >
          <template #default="scope">
            <div v-if="scope.row._errors && scope.row._errors[column.prop]" class="cell-with-error">
              <span>{{ scope.row[column.prop] }}</span>
              <el-tooltip
                :content="scope.row._errors[column.prop]"
                placement="top"
                effect="dark"
              >
                <el-icon class="error-icon"><CircleClose /></el-icon>
              </el-tooltip>
            </div>
            <div v-else-if="scope.row._warnings && scope.row._warnings[column.prop]" class="cell-with-warning">
              <span>{{ scope.row[column.prop] }}</span>
              <el-tooltip
                :content="scope.row._warnings[column.prop]"
                placement="top"
                effect="dark"
              >
                <el-icon class="warning-icon"><Warning /></el-icon>
              </el-tooltip>
            </div>
            <div v-else>{{ scope.row[column.prop] }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag
              v-if="scope.row._errors"
              type="danger"
              size="small"
            >
              错误
            </el-tag>
            <el-tag
              v-else-if="scope.row._warnings"
              type="warning"
              size="small"
            >
              警告
            </el-tag>
            <el-tag
              v-else
              type="success"
              size="small"
            >
              有效
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalRows"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    
    <!-- 错误和警告信息 -->
    <div v-if="errorRecords.length > 0 || warningRecords.length > 0" class="validation-results">
      <el-tabs>
        <el-tab-pane label="错误记录" :name="'errors'">
          <el-table
            :data="errorRecords"
            style="width: 100%"
            border
            size="small"
          >
            <el-table-column prop="_index" label="行号" width="80"></el-table-column>
            <el-table-column prop="_errorMessage" label="错误信息" min-width="300"></el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="警告记录" :name="'warnings'">
          <el-table
            :data="warningRecords"
            style="width: 100%"
            border
            size="small"
          >
            <el-table-column prop="_index" label="行号" width="80"></el-table-column>
            <el-table-column prop="_warningMessage" label="警告信息" min-width="300"></el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <div class="panel-tip">
      <el-alert
        title="操作提示"
        type="info"
        :closable="false"
        show-icon
      >
        <ul>
          <li>系统已对数据进行初步校验，请检查错误和警告信息</li>
          <li>错误记录：必须修复才能导入</li>
          <li>警告记录：可以选择忽略，但可能影响数据质量</li>
          <li>点击表格单元格中的图标可以查看详细的错误/警告信息</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { CircleClose, Warning } from '@element-plus/icons-vue'

// 分页信息
const currentPage = ref(1)
const pageSize = ref(10)

// 表格列定义
const tableColumns = ref([
  { prop: 'name', label: '姓名', width: '120' },
  { prop: 'gender', label: '性别', width: '80' },
  { prop: 'age', label: '年龄', width: '80' },
  { prop: 'employee_id', label: '工号', width: '100' },
  { prop: 'department', label: '部门', width: '150' },
  { prop: 'position', label: '职位', width: '120' },
  { prop: 'phone', label: '联系电话', width: '150' },
  { prop: 'email', label: '邮箱', width: '200' },
  { prop: 'hire_date', label: '入职日期', width: '120' },
  { prop: 'status', label: '状态', width: '100' }
])

// 模拟数据
const allData = ref<any[]>([])

// 总记录数
const totalRows = computed(() => allData.value.length)

// 有效记录数
const validRows = computed(() => {
  return allData.value.filter(row => !row._errors).length
})

// 无效记录数
const invalidRows = computed(() => {
  return allData.value.filter(row => row._errors).length
})

// 警告记录数
const warningRows = computed(() => {
  return allData.value.filter(row => row._warnings && !row._errors).length
})

// 当前页数据
const previewData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allData.value.slice(start, end)
})

// 错误记录
const errorRecords = computed(() => {
  return allData.value
    .filter(row => row._errors)
    .map(row => ({
      _index: row._index,
      _errorMessage: Object.values(row._errors).join('; ')
    }))
})

// 警告记录
const warningRecords = computed(() => {
  return allData.value
    .filter(row => row._warnings && !row._errors)
    .map(row => ({
      _index: row._index,
      _warningMessage: Object.values(row._warnings).join('; ')
    }))
})

// 表格行样式
const tableRowClassName = ({ row }: any) => {
  if (row._errors) {
    return 'row-error'
  } else if (row._warnings) {
    return 'row-warning'
  }
  return ''
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

// 处理分页页码变化
const handleCurrentChange = (current: number) => {
  currentPage.value = current
}

// 模拟数据验证
const validateData = (data: any[]) => {
  return data.map((row, index) => {
    const validatedRow = { ...row, _index: index + 1 }
    const errors: any = {}
    const warnings: any = {}
    
    // 验证姓名
    if (!row.name || row.name.trim() === '') {
      errors.name = '姓名不能为空'
    }
    
    // 验证性别
    if (!row.gender || !['男', '女'].includes(row.gender)) {
      errors.gender = '性别必须为男或女'
    }
    
    // 验证年龄
    if (!row.age || isNaN(row.age) || row.age < 18 || row.age > 65) {
      errors.age = '年龄必须在18-65之间'
    }
    
    // 验证工号
    if (!row.employee_id || row.employee_id.trim() === '') {
      errors.employee_id = '工号不能为空'
    }
    
    // 验证联系电话
    if (row.phone) {
      const phoneRegex = /^1[3-9]\d{9}$/
      if (!phoneRegex.test(row.phone)) {
        warnings.phone = '联系电话格式可能不正确'
      }
    } else {
      warnings.phone = '联系电话为空'
    }
    
    // 验证邮箱
    if (row.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(row.email)) {
        warnings.email = '邮箱格式可能不正确'
      }
    }
    
    // 验证入职日期
    if (row.hire_date) {
      const date = new Date(row.hire_date)
      if (isNaN(date.getTime())) {
        errors.hire_date = '入职日期格式不正确'
      }
    }
    
    // 添加错误和警告
    if (Object.keys(errors).length > 0) {
      validatedRow._errors = errors
    }
    if (Object.keys(warnings).length > 0) {
      validatedRow._warnings = warnings
    }
    
    return validatedRow
  })
}

// 初始化
onMounted(() => {
  // 模拟数据
  const mockData = [
    {
      name: '张三',
      gender: '男',
      age: 30,
      employee_id: 'T001',
      department: '第一中学',
      position: '教师',
      phone: '13800138001',
      email: 'zhangsan@example.com',
      hire_date: '2020-01-01',
      status: '在职'
    },
    {
      name: '李四',
      gender: '女',
      age: 25,
      employee_id: 'T002',
      department: '第二中学',
      position: '教师',
      phone: '13800138002',
      email: 'lisi@example.com',
      hire_date: '2021-01-01',
      status: '在职'
    },
    {
      name: '', // 错误：姓名为空
      gender: '男',
      age: 35,
      employee_id: 'T003',
      department: '中心小学',
      position: '教师',
      phone: '13800138003',
      email: 'wangwu@example.com',
      hire_date: '2019-01-01',
      status: '在职'
    },
    {
      name: '赵六',
      gender: '男',
      age: 17, // 错误：年龄太小
      employee_id: 'T004',
      department: '第一中学',
      position: '教师',
      phone: '13800138004',
      email: 'zhaoliu@example.com',
      hire_date: '2022-01-01',
      status: '在职'
    },
    {
      name: '钱七',
      gender: '女',
      age: 40,
      employee_id: 'T005',
      department: '第二中学',
      position: '教师',
      phone: '13800138', // 警告：电话格式不正确
      email: 'qianqi@example.com',
      hire_date: '2018-01-01',
      status: '在职'
    },
    {
      name: '孙八',
      gender: '男',
      age: 45,
      employee_id: 'T006',
      department: '中心小学',
      position: '教师',
      phone: '13800138006',
      email: 'sunba', // 警告：邮箱格式不正确
      hire_date: '2017-01-01',
      status: '在职'
    }
  ]
  
  // 生成更多模拟数据
  for (let i = 7; i <= 30; i++) {
    mockData.push({
      name: `测试用户${i}`,
      gender: i % 2 === 0 ? '男' : '女',
      age: 20 + i,
      employee_id: `T${String(i).padStart(3, '0')}`,
      department: i % 3 === 0 ? '第一中学' : i % 3 === 1 ? '第二中学' : '中心小学',
      position: '教师',
      phone: `138001380${i}`,
      email: `test${i}@example.com`,
      hire_date: `202${i % 3}-01-01`,
      status: '在职'
    })
  }
  
  // 验证数据
  allData.value = validateData(mockData)
})

// 导出数据供父组件使用
defineExpose({
  allData,
  totalRows,
  validRows,
  invalidRows,
  warningRows,
  errorRecords,
  warningRecords
})
</script>

<style scoped>
.data-preview-panel {
  padding: 20px;
}

.preview-stats {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.preview-table {
  margin-bottom: 30px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.validation-results {
  margin-bottom: 30px;
}

.cell-with-error {
  position: relative;
  display: flex;
  align-items: center;
  gap: 5px;
}

.cell-with-warning {
  position: relative;
  display: flex;
  align-items: center;
  gap: 5px;
}

.error-icon {
  color: #f56c6c;
  cursor: pointer;
}

.warning-icon {
  color: #e6a23c;
  cursor: pointer;
}

:deep(.row-error) {
  background-color: #fef0f0;
}

:deep(.row-warning) {
  background-color: #fdf6ec;
}

.panel-tip {
  margin-top: 30px;
}
</style>
