<template>
  <div class="retirement-estimate-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <h3>退休测算</h3>
        </div>
      </template>
      
      <!-- 查询条件 -->
      <el-form :inline="true" :model="queryForm" class="query-form">
        <el-form-item label="测算类型">
          <el-select v-model="queryForm.estimate_type" placeholder="请选择" style="width: 150px">
            <el-option label="按旧标准测算" value="old" />
            <el-option label="按新标准测算" value="new" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="queryForm.start_date"
            type="date"
            placeholder="选择开始日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="queryForm.end_date"
            type="date"
            placeholder="选择截止日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCalculate">开始测算</el-button>
          <el-button @click="handleExport">导出Excel</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 结果表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="id_card" label="身份证号码" width="180" />
        <el-table-column prop="unit_name" label="所在单位" min-width="150" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="birth_date" label="出生日期" width="120">
          <template #default="{ row }">
            {{ row.birth_date ? row.birth_date.substring(0, 10) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="personal_identity" label="个人身份" width="100" />
        <el-table-column prop="employment_status" label="任职状态" width="100" />
        <el-table-column prop="original_retirement_date" label="原退休时间" width="120">
          <template #default="{ row }">
            {{ row.original_retirement_date ? row.original_retirement_date.substring(0, 10) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="delay_months" label="延迟月数" width="90" />
        <el-table-column prop="new_retirement_date" label="现退休时间" width="120">
          <template #default="{ row }">
            {{ row.new_retirement_date ? row.new_retirement_date.substring(0, 10) : '-' }}
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calculator } from '@element-plus/icons-vue'

const API_BASE_URL = ''

const loading = ref(false)
const tableData = ref<any[]>([])

const getDefaultDateRange = () => {
  const today = new Date()
  const year = today.getFullYear()
  const startDate = `${year}-01-01`
  const endDate = `${year}-12-31`
  return { start_date: startDate, end_date: endDate }
}

const queryForm = reactive({
  estimate_type: 'new',
  ...getDefaultDateRange()
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const handleCalculate = async () => {
  if (!queryForm.start_date || !queryForm.end_date) {
    ElMessage.warning('请选择开始日期和截止日期')
    return
  }
  
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('estimate_type', queryForm.estimate_type)
    params.append('start_date', queryForm.start_date)
    params.append('end_date', queryForm.end_date)
    
    const res = await fetch(`${API_BASE_URL}/api/retirement/calculate?${params}`)
    const result = await res.json()
    
    if (result.success) {
      tableData.value = result.data
      pagination.total = result.total
      ElMessage.success('测算完成')
    } else {
      ElMessage.error(result.message || '测算失败')
    }
  } catch (error) {
    ElMessage.error('测算失败')
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  let csv = '序号,姓名,身份证号码,所在单位,性别,出生日期,是否干部,原退休时间,延迟月数,现退休时间\n'
  tableData.value.forEach((row, index) => {
    csv += `${index + 1},${row.name},${row.id_card || ''},${row.unit_name || ''},${row.gender || ''},${row.birth_date || ''},${row.is_cadre || ''},${row.original_retirement_date || ''},${row.delay_months || 0},${row.new_retirement_date || ''}\n`
  })
  
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `退休测算_${queryForm.estimate_type === 'new' ? '新标准' : '旧标准'}.csv`
  link.click()
  window.URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
}

onMounted(() => {
  // 初始加载空数据
})
</script>

<style scoped>
.retirement-estimate-container {
  padding: 20px;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.query-form {
  margin-bottom: 20px;
}
</style>
