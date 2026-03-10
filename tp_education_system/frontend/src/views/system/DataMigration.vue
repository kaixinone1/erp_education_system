<template>
  <div class="migration-container">
    <el-card class="migration-card">
      <template #header>
        <div class="card-header">
          <span class="title">数据迁移工具</span>
          <el-tag type="info">宽表转长表</el-tag>
        </div>
      </template>

      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" class="steps">
        <el-step title="选择源表" description="选择原始宽表" />
        <el-step title="预览数据" description="查看转换效果" />
        <el-step title="执行迁移" description="生成关系数据" />
        <el-step title="完成" description="迁移完成" />
      </el-steps>

      <!-- 步骤1: 选择源表 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-form :model="migrationForm" label-width="120px">
          <el-form-item label="源宽表">
            <el-select 
              v-model="migrationForm.source_table" 
              placeholder="选择源表" 
              style="width: 300px"
              @change="autoDetectColumns"
            >
              <el-option
                v-for="table in getSourceTables()"
                :key="table.name"
                :label="table.chinese_name || table.name"
                :value="table.name"
              >
                <span>{{ table.chinese_name || table.name }}</span>
                <el-tag size="small" type="info" style="margin-left: 10px">{{ table.name }}</el-tag>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="教师主表">
            <el-select v-model="migrationForm.teacher_table" placeholder="选择教师表" style="width: 300px">
              <el-option
                v-for="table in teacherTables"
                :key="table.name"
                :label="table.chinese_name || table.name"
                :value="table.name"
              >
                <span>{{ table.chinese_name || table.name }}</span>
                <el-tag size="small" type="info" style="margin-left: 10px">{{ table.name }}</el-tag>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="标签字典表">
            <el-select v-model="migrationForm.tag_table" placeholder="选择标签表" style="width: 300px">
              <el-option
                v-for="table in tagTables"
                :key="table.name"
                :label="table.chinese_name || table.name"
                :value="table.name"
              >
                <span>{{ table.chinese_name || table.name }}</span>
                <el-tag size="small" type="info" style="margin-left: 10px">{{ table.name }}</el-tag>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="关系表">
            <el-input v-model="migrationForm.relation_table" placeholder="employee_tag_relations" style="width: 300px" />
          </el-form-item>

          <el-form-item label="身份证列">
            <el-input v-model="migrationForm.id_card_column" placeholder="身份证号码" style="width: 300px" />
          </el-form-item>

          <el-form-item label="姓名列">
            <el-input v-model="migrationForm.name_column" placeholder="姓名" style="width: 300px" />
          </el-form-item>
        </el-form>

        <div class="step-actions">
          <el-button type="primary" @click="handlePreview" :loading="previewLoading">
            下一步：预览数据
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 预览数据 -->
      <div v-if="currentStep === 1" class="step-content">
        <el-alert
          title="数据预览"
          :description="`源表共 ${previewData.total_rows} 行，${previewData.tag_columns?.length} 个标签列，预览前10行转换结果`"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-table :data="previewData.data" border style="width: 100%" max-height="400">
          <el-table-column prop="身份证号码" label="身份证号码" width="180" v-if="hasColumn('身份证号码')" />
          <el-table-column prop="id_card" label="身份证号码" width="180" v-else-if="hasColumn('id_card')" />
          <el-table-column prop="姓名" label="姓名" width="100" v-if="hasColumn('姓名')" />
          <el-table-column prop="name" label="姓名" width="100" v-else-if="hasColumn('name')" />
          <el-table-column prop="标签名称" label="标签名称" />
          <el-table-column prop="标签值" label="标签值" width="100" />
        </el-table>

        <div class="step-actions">
          <el-button @click="currentStep = 0">上一步</el-button>
          <el-button type="primary" @click="currentStep = 2">
            下一步：执行迁移
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 执行迁移 -->
      <div v-if="currentStep === 2" class="step-content">
        <el-alert
          title="准备执行迁移"
          description="此操作将读取源宽表数据，转换为长表格式，并写入关系表。请确认配置正确。"
          type="warning"
          show-icon
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="源宽表">{{ migrationForm.source_table }}</el-descriptions-item>
          <el-descriptions-item label="教师主表">{{ migrationForm.teacher_table }}</el-descriptions-item>
          <el-descriptions-item label="标签字典表">{{ migrationForm.tag_table }}</el-descriptions-item>
          <el-descriptions-item label="关系表">{{ migrationForm.relation_table }}</el-descriptions-item>
          <el-descriptions-item label="身份证列">{{ migrationForm.id_card_column }}</el-descriptions-item>
          <el-descriptions-item label="姓名列">{{ migrationForm.name_column }}</el-descriptions-item>
        </el-descriptions>

        <div class="step-actions">
          <el-button @click="currentStep = 1">上一步</el-button>
          <el-button type="danger" @click="executeMigration" :loading="migrationLoading">
            执行迁移
          </el-button>
        </div>
      </div>

      <!-- 步骤4: 完成 -->
      <div v-if="currentStep === 3" class="step-content">
        <el-result
          :icon="migrationResult.success ? 'success' : 'error'"
          :title="migrationResult.success ? '迁移成功' : '迁移失败'"
          :sub-title="migrationResult.message"
        >
          <template #extra>
            <el-descriptions :column="3" border v-if="migrationResult.success">
              <el-descriptions-item label="处理记录">{{ migrationResult.processed_count }}</el-descriptions-item>
              <el-descriptions-item label="成功写入">{{ migrationResult.success_count }}</el-descriptions-item>
              <el-descriptions-item label="失败记录">{{ migrationResult.failed_count }}</el-descriptions-item>
            </el-descriptions>

            <div v-if="migrationResult.unmatched_count > 0" style="margin-top: 20px">
              <el-alert 
                :title="`有 ${migrationResult.unmatched_count} 个教师在基础信息表中不存在`" 
                type="warning" 
                show-icon 
                :closable="false" 
              />
              <div style="margin-top: 10px">
                <el-button type="primary" size="small" @click="downloadUnmatchedFile">
                  <el-icon><Download /></el-icon>
                  下载未匹配教师列表
                </el-button>
                <span style="margin-left: 10px; color: #666; font-size: 12px">
                  请核对后导入教师基础信息表
                </span>
              </div>
            </div>

            <div v-if="migrationResult.failed_records?.length > 0 && migrationResult.failed_records[0].reason.includes('标签')" style="margin-top: 20px">
              <el-alert title="部分标签未找到" type="warning" show-icon :closable="false" />
              <el-table :data="migrationResult.failed_records" border style="width: 100%; margin-top: 10px" max-height="200">
                <el-table-column prop="id_card" label="身份证" width="180" />
                <el-table-column prop="tag_name" label="标签" />
                <el-table-column prop="reason" label="失败原因" />
              </el-table>
            </div>

            <div style="margin-top: 20px">
              <el-button type="primary" @click="resetMigration">重新迁移</el-button>
              <el-button @click="$router.push('/data-center')">返回数据中心</el-button>
            </div>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 说明卡片 -->
    <el-card class="info-card" style="margin-top: 20px">
      <template #header>
        <span>功能说明</span>
      </template>
      <el-timeline>
        <el-timeline-item type="primary" :hollow="true">
          <h4>宽表转长表</h4>
          <p>将一行包含多个标签的宽表数据，转换为每行只有一个标签的长表格式</p>
        </el-timeline-item>
        <el-timeline-item type="success" :hollow="true">
          <h4>ID自动映射</h4>
          <p>根据身份证号码自动匹配教师ID，根据标签名称自动匹配标签ID</p>
        </el-timeline-item>
        <el-timeline-item type="warning" :hollow="true">
          <h4>批量写入</h4>
          <p>使用批量插入方式，高效将关系数据写入数据库</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 当前步骤
const currentStep = ref(0)

// 迁移表单
const migrationForm = ref({
  source_table: '',
  teacher_table: 'teacher_basic_info',
  tag_table: 'personal_dict_dictionary',  // 使用 personal_dict_dictionary 作为标签表
  relation_table: 'employee_tag_relations',
  id_card_column: '',  // 动态检测
  name_column: ''      // 动态检测
})

// 表字段信息
const tableColumns = ref<Record<string, string[]>>({})

// 获取表的字段列表
const fetchTableColumns = async (tableName: string) => {
  try {
    const response = await fetch(`/api/table-structure/${tableName}`)
    if (response.ok) {
      const result = await response.json()
      if (result.columns) {
        tableColumns.value[tableName] = result.columns.map((col: any) => col.name)
        return tableColumns.value[tableName]
      }
    }
  } catch (error) {
    console.error('获取表字段失败:', error)
  }
  return []
}

// 自动检测标识列
const autoDetectColumns = async () => {
  const tableName = migrationForm.value.source_table
  if (!tableName) return
  
  const columns = await fetchTableColumns(tableName)
  
  // 检测身份证列
  const idCardFields = ['身份证号码', 'id_card', '身份证号', '身份证', 'idcard']
  for (const field of idCardFields) {
    if (columns.includes(field)) {
      migrationForm.value.id_card_column = field
      break
    }
  }
  
  // 检测姓名列
  const nameFields = ['姓名', 'name', '教师姓名', 'teacher_name']
  for (const field of nameFields) {
    if (columns.includes(field)) {
      migrationForm.value.name_column = field
      break
    }
  }
}

// 表列表
const allTables = ref<any[]>([])
const sourceTables = ref<any[]>([])
const teacherTables = ref<any[]>([])
const tagTables = ref<any[]>([])

// 获取源表列表（所有表都可以作为源表）
const getSourceTables = () => {
  // 返回所有表，不只是 source 类型
  return allTables.value.filter(t => 
    t.type === 'source' || 
    t.type === 'master' || 
    t.type === 'dictionary' ||
    t.type === 'other'
  )
}

// 预览数据
const previewData = ref<any>({
  data: [],
  total_rows: 0,
  tag_columns: []
})
const previewLoading = ref(false)

// 迁移结果
const migrationResult = ref<any>({
  success: false,
  processed_count: 0,
  success_count: 0,
  failed_count: 0,
  failed_records: [],
  message: ''
})
const migrationLoading = ref(false)

// 获取表列表
const fetchTables = async () => {
  try {
    const response = await fetch('/api/migration/tables')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        allTables.value = result.tables
        sourceTables.value = result.tables.filter((t: any) => t.type === 'source')
        teacherTables.value = result.tables.filter((t: any) => t.type === 'master')
        tagTables.value = result.tables.filter((t: any) => t.type === 'dictionary')
      }
    }
  } catch (error) {
    console.error('获取表列表失败:', error)
  }
}

// 预览数据
const handlePreview = async () => {
  if (!migrationForm.value.source_table) {
    ElMessage.warning('请选择源表')
    return
  }

  previewLoading.value = true
  try {
    const response = await fetch(`/api/migration/preview?source_table=${migrationForm.value.source_table}&limit=10`)
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        previewData.value = result
        currentStep.value = 1
        ElMessage.success('预览数据加载成功')
      } else if (result.status === 'error') {
        // 表不存在等错误
        ElMessage.warning(result.message || '预览失败')
      } else {
        ElMessage.error(result.message || '预览失败')
      }
    } else {
      ElMessage.error('预览请求失败')
    }
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  } finally {
    previewLoading.value = false
  }
}

// 执行迁移
const executeMigration = async () => {
  migrationLoading.value = true
  try {
    const response = await fetch('/api/migration/transform-tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(migrationForm.value)
    })

    if (response.ok) {
      const result = await response.json()
      migrationResult.value = result
      currentStep.value = 3

      if (result.success) {
        ElMessage.success(result.message)
      } else {
        ElMessage.warning(result.message)
      }
    } else {
      ElMessage.error('迁移请求失败')
    }
  } catch (error) {
    console.error('迁移失败:', error)
    ElMessage.error('迁移失败')
    migrationResult.value = {
      success: false,
      message: '迁移过程发生错误'
    }
    currentStep.value = 3
  } finally {
    migrationLoading.value = false
  }
}

// 重置迁移
const resetMigration = () => {
  currentStep.value = 0
  migrationResult.value = {
    success: false,
    processed_count: 0,
    success_count: 0,
    failed_count: 0,
    failed_records: [],
    unmatched_count: 0,
    unmatched_export_file: '',
    message: ''
  }
}

// 下载未匹配教师列表
const downloadUnmatchedFile = () => {
  if (migrationResult.value.unmatched_export_file) {
    // 从后端获取文件下载
    const fileName = migrationResult.value.unmatched_export_file.split('\\').pop()
    window.open(`/api/migration/download-unmatched?file=${encodeURIComponent(fileName)}`, '_blank')
  }
}

// 检查数据中是否包含指定列
const hasColumn = (columnName: string) => {
  if (!previewData.value.data || previewData.value.data.length === 0) {
    return false
  }
  return columnName in previewData.value.data[0]
}

onMounted(() => {
  fetchTables()
})
</script>

<style scoped>
.migration-container {
  padding: 20px;
}

.migration-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.steps {
  margin: 30px 0;
}

.step-content {
  padding: 20px 0;
}

.step-actions {
  margin-top: 30px;
  text-align: center;
}

.info-card {
  max-width: 1000px;
  margin: 0 auto;
}
</style>
