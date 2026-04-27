<template>
  <div class="death-records">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span class="title">死亡登记信息</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索姓名或身份证号"
              style="width: 250px;"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="姓名" label="姓名" width="100" />
        <el-table-column prop="性别" label="性别" width="60" align="center" />
        <el-table-column prop="身份证号码" label="身份证号码" width="180" />
        <el-table-column prop="死亡日期" label="死亡日期" width="120" />
        <el-table-column prop="死亡原因" label="死亡原因" min-width="150" show-overflow-tooltip />
        <el-table-column prop="退休单位" label="退休单位" min-width="150" show-overflow-tooltip />
        <el-table-column prop="户籍地" label="户籍地" min-width="150" show-overflow-tooltip />
        <el-table-column prop="现住址" label="现住址" min-width="150" show-overflow-tooltip />
        <el-table-column prop="登记人" label="登记人" width="100" />
        <el-table-column prop="登记时间" label="登记时间" width="150" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="死亡登记详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="姓名">{{ currentRow.姓名 }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ currentRow.性别 }}</el-descriptions-item>
        <el-descriptions-item label="身份证号码">{{ currentRow.身份证号码 }}</el-descriptions-item>
        <el-descriptions-item label="死亡日期">{{ currentRow.死亡日期 }}</el-descriptions-item>
        <el-descriptions-item label="死亡原因" :span="2">{{ currentRow.死亡原因 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="退休单位" :span="2">{{ currentRow.退休单位 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="户籍地" :span="2">{{ currentRow.户籍地 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="现住址" :span="2">{{ currentRow.现住址 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行账号">{{ currentRow.银行账号 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开户行">{{ currentRow.开户行 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="本人联系电话">{{ currentRow.本人联系电话 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="代理人姓名">{{ currentRow.代理人姓名 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="与本人关系">{{ currentRow.与本人关系 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="代理人联系电话">{{ currentRow.代理人联系电话 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="登记人">{{ currentRow.登记人 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="登记时间">{{ currentRow.登记时间 }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRow.备注 || '-' }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 表格数据
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')

// 对话框
const dialogVisible = ref(false)
const currentRow = ref<any>({})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString()
    })
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value)
    }

    const response = await fetch(`/api/octogenarian/death-records?${params}`)
    const result = await response.json()

    if (result.status === 'success') {
      tableData.value = result.data
      total.value = result.total
    } else {
      ElMessage.error(result.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 查看详情
const handleView = (row: any) => {
  currentRow.value = row
  dialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.death-records {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
