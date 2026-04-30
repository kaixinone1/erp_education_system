<template>
  <div class="retirement-report-fill">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <span>职工退休呈报表 - 智能填报</span>
        </div>
      </template>

      <div class="search-section">
        <el-radio-group v-model="searchType" class="search-type">
          <el-radio-button label="name">按姓名搜索</el-radio-button>
          <el-radio-button label="id_card">按身份证号搜索</el-radio-button>
          <el-radio-button label="id">按教师ID搜索</el-radio-button>
        </el-radio-group>

        <div class="search-input">
          <el-input
            v-model="searchKeyword"
            :placeholder="searchPlaceholder"
            size="large"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button type="primary" :loading="searching" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <div class="search-tips">
          <el-alert
            :title="searchTip"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-card>

    <!-- 搜索结果 -->
    <el-card v-if="searchResults.length > 0" class="results-card">
      <template #header>
        <div class="card-header">
          <span>搜索结果 ({{ searchResults.length }}人)</span>
        </div>
      </template>

      <el-table :data="searchResults" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="teacher_name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="id_card_display" label="身份证号" min-width="180" />
        <el-table-column prop="birth_date" label="出生日期" width="120" />
        <el-table-column prop="age" label="年龄" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_retirement_age ? 'danger' : 'success'">
              {{ scope.row.age }}岁
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="work_unit" label="工作单位" min-width="200" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleFillReport(scope.row)"
            >
              填报
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 无结果提示 -->
    <el-card v-else-if="hasSearched && !searching" class="empty-card">
      <el-empty description="未找到匹配的教师信息">
        <template #description>
          <p>未找到匹配的教师信息</p>
          <p class="sub-text">请检查输入的关键词是否正确</p>
        </template>
      </el-empty>
    </el-card>

    <!-- 报表设计器 -->
    <ReportDesigner
      ref="reportDesignerRef"
      :teacher-id="selectedTeacherId"
      @save="handleReportSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import ReportDesigner from '../components/ReportDesigner.vue'

const searchType = ref('name')
const searchKeyword = ref('')
const searching = ref(false)
const hasSearched = ref(false)
const searchResults = ref<any[]>([])
const selectedTeacherId = ref(0)
const reportDesignerRef = ref<InstanceType<typeof ReportDesigner> | null>(null)

// 搜索提示
const searchPlaceholder = computed(() => {
  switch (searchType.value) {
    case 'name':
      return '请输入教师姓名（支持模糊搜索）'
    case 'id_card':
      return '请输入18位身份证号码'
    case 'id':
      return '请输入教师ID（数字）'
    default:
      return '请输入搜索关键词'
  }
})

const searchTip = computed(() => {
  switch (searchType.value) {
    case 'name':
      return '提示：输入姓名可模糊搜索，如输入"王"可找到所有姓王的教师'
    case 'id_card':
      return '提示：输入完整的18位身份证号码进行精确搜索'
    case 'id':
      return '提示：输入教师的系统ID号（数字）'
    default:
      return ''
  }
})

// 搜索教师
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  searching.value = true
  hasSearched.value = true

  try {
    let url = ''

    switch (searchType.value) {
      case 'name':
        url = `/api/retirement/search-by-name?name=${encodeURIComponent(searchKeyword.value)}`
        break
      case 'id_card':
        url = `/api/retirement/search-by-id-card?id_card=${encodeURIComponent(searchKeyword.value)}`
        break
      case 'id':
        url = `/api/retirement/teacher-data?teacher_id=${searchKeyword.value}`
        break
    }

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error('搜索失败')
    }

    const result = await response.json()

    if (result.status === 'success') {
      if (searchType.value === 'id') {
        // 按ID搜索返回单个对象，需要包装成数组
        searchResults.value = [result.data]
      } else {
        searchResults.value = result.data || []
      }

      if (searchResults.value.length === 0) {
        ElMessage.info('未找到匹配的教师')
      } else {
        ElMessage.success(`找到 ${searchResults.value.length} 位教师`)
      }
    } else {
      throw new Error(result.message || '搜索失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '搜索失败')
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

// 填报报表
const handleFillReport = (teacher: any) => {
  selectedTeacherId.value = teacher.id || teacher.teacher_id
  reportDesignerRef.value?.open()
}

// 报表保存成功
const handleReportSaved = () => {
  ElMessage.success('报表保存成功')
}
</script>

<style scoped>
.retirement-report-fill {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.search-section {
  padding: 20px;
}

.search-type {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.search-input {
  max-width: 600px;
  margin: 0 auto 20px;
}

.search-tips {
  max-width: 600px;
  margin: 0 auto;
}

.results-card {
  margin-bottom: 20px;
}

.empty-card {
  text-align: center;
  padding: 40px;

  .sub-text {
    color: #909399;
    font-size: 14px;
    margin-top: 10px;
  }
}
</style>
