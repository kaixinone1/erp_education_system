<template>
  <div class="universal-template-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通用模板管理</span>
          <el-button type="primary" @click="showUploadDialog = true">上传模板</el-button>
        </div>
      </template>

      <el-table :data="templateList" border stripe>
        <el-table-column prop="template_name" label="模板名称" min-width="150" />
        <el-table-column prop="file_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.file_type === 'docx' ? 'primary' : 'success'">
              {{ row.file_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="激活方式" width="120">
          <template #default="{ row }">
            <el-tag :type="row.activation_type === 'scheduled_task' ? 'warning' : 'info'" size="small">
              {{ row.activation_type === 'scheduled_task' ? '固定时段' : '状态变更' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="placeholders" label="占位符" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="p in (row.placeholders || []).slice(0, 5)" :key="p" size="small" class="placeholder-tag">
              {{ p }}
            </el-tag>
            <el-tag v-if="(row.placeholders || []).length > 5" size="small" type="info">
              +{{ (row.placeholders || []).length - 5 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="480" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openFillDialog(row)">填报</el-button>
            <el-button type="success" size="small" @click="openManualEdit(row)">编辑</el-button>
            <el-button type="warning" size="small" @click="openBatchExport(row)">批量</el-button>
            <el-button type="info" size="small" @click="editConfig(row)">配置</el-button>
            <el-button type="primary" size="small" plain @click="openActivationDialog(row)">激活</el-button>
            <el-button type="danger" size="small" @click="deleteTemplate(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>字段映射管理</span>
          <el-button type="primary" size="small" @click="showMappingDialog = true">添加映射</el-button>
        </div>
      </template>

      <el-table :data="fieldMappings" border stripe max-height="300">
        <el-table-column prop="placeholder_name" label="占位符" width="150" />
        <el-table-column prop="table_name" label="数据表" width="200" />
        <el-table-column prop="field_name" label="字段名" width="150" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteMapping(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showUploadDialog" title="上传模板" width="500px">
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="模板名称">
          <el-input v-model="uploadForm.template_name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="选择文件">
          <el-upload
            ref="upload"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            accept=".doc,.docx,.xls,.xlsx"
          >
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持.doc/.docx/.xls/.xlsx格式，带占位符{{}}</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showMappingDialog" title="添加字段映射" width="500px">
      <el-form :model="mappingForm" label-width="80px">
        <el-form-item label="占位符">
          <el-input v-model="mappingForm.placeholder_name" placeholder="如：姓名" />
        </el-form-item>
        <el-form-item label="数据表">
          <el-select v-model="mappingForm.table_name" placeholder="选择数据表">
            <el-option label="teacher_basic_info" value="teacher_basic_info" />
            <el-option label="retirement_report_data" value="retirement_report_data" />
            <el-option label="retirement_report_form" value="retirement_report_form" />
          </el-select>
        </el-form-item>
        <el-form-item label="字段名">
          <el-input v-model="mappingForm.field_name" placeholder="如：name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMappingDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddMapping">添加</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showExportDialog" title="导出测试" width="400px">
      <el-form :model="exportForm" label-width="80px">
        <el-form-item label="教师ID">
          <el-input v-model="exportForm.teacher_id" type="number" placeholder="请输入教师ID" />
        </el-form-item>
        <el-form-item label="教师姓名">
          <el-input v-model="exportForm.teacher_name" placeholder="请输入教师姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="exporting">导出</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchExportDialog" title="批量导出" width="600px">
      <el-alert type="info" :closable="false" style="margin-bottom: 15px">
        选择多个教师后，将为每位教师生成一个独立的Word/Excel文件，并打包成ZIP下载
      </el-alert>
      <el-form :model="batchExportForm" label-width="80px">
        <el-form-item label="教师列表">
          <el-select
            v-model="batchExportForm.teacher_ids"
            multiple
            filterable
            remote
            :remote-method="searchTeachers"
            :loading="searchingTeachers"
            placeholder="搜索教师姓名或ID"
            style="width: 100%"
          >
            <el-option
              v-for="t in teacherOptions"
              :key="t.id"
              :label="`${t.name} (ID: ${t.id})`"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="已选教师">
          <el-tag v-for="id in batchExportForm.teacher_ids" :key="id" style="margin-right: 5px" closable @close="removeTeacher(id)">
            {{ getTeacherName(id) }}
          </el-tag>
          <span v-if="batchExportForm.teacher_ids.length === 0" style="color: #999">请在上方搜索并选择教师</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchExportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchExport" :loading="exporting" :disabled="batchExportForm.teacher_ids.length === 0">
          导出 {{ batchExportForm.teacher_ids.length }} 人
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showSummaryExportDialog" title="汇总导出" width="600px">
      <el-alert type="info" :closable="false" style="margin-bottom: 15px">
        将多个教师的数据填入同一张表格中，生成一个汇总的Word/Excel文件
      </el-alert>
      <el-form :model="summaryExportForm" label-width="80px">
        <el-form-item label="教师列表">
          <el-select
            v-model="summaryExportForm.teacher_ids"
            multiple
            filterable
            remote
            :remote-method="searchTeachers"
            :loading="searchingTeachers"
            placeholder="搜索教师姓名或ID"
            style="width: 100%"
          >
            <el-option
              v-for="t in teacherOptions"
              :key="t.id"
              :label="`${t.name} (ID: ${t.id})`"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="已选教师">
          <el-tag v-for="id in summaryExportForm.teacher_ids" :key="id" style="margin-right: 5px" closable @close="removeSummaryTeacher(id)">
            {{ getTeacherName(id) }}
          </el-tag>
          <span v-if="summaryExportForm.teacher_ids.length === 0" style="color: #999">请在上方搜索并选择教师</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSummaryExportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSummaryExport" :loading="exporting" :disabled="summaryExportForm.teacher_ids.length === 0">
          导出 {{ summaryExportForm.teacher_ids.length }} 人汇总
        </el-button>
      </template>
    </el-dialog>

    <!-- 填报对话框 -->
    <el-dialog v-model="showFillDialog" title="模板填报" width="800px">
      <el-form :model="fillForm" label-width="100px">
        <!-- 模板类型选择 -->
        <el-form-item label="模板类型">
          <el-radio-group v-model="fillForm.template_scope">
            <el-radio label="individual">个人模板（针对教师）</el-radio>
            <el-radio label="collective">集体模板（针对群体）</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 个人模板：选择教师 -->
        <el-form-item v-if="fillForm.template_scope === 'individual'" label="选择教师">
          <el-select
            v-model="fillForm.teacher_id"
            filterable
            remote
            placeholder="输入姓名搜索教师"
            :remote-method="searchTeachers"
            :loading="searchingTeachers"
            style="width: 100%"
          >
            <el-option
              v-for="teacher in teacherOptions"
              :key="teacher.id"
              :label="teacher.name + ' (' + (teacher.id_card ? teacher.id_card.substring(0, 6) : 'N/A') + '...) ' + (teacher.employment_status || '')"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>

        <!-- 集体模板：说明 -->
        <el-alert
          v-if="fillForm.template_scope === 'collective'"
          title="集体模板用于汇总、统计等场景，不需要选择具体教师"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        />

        <el-form-item label="填报方式">
          <el-radio-group v-model="fillForm.fill_mode">
            <el-radio label="auto">自动填报（从数据库获取）</el-radio>
            <el-radio label="manual">手工编辑（空模板）</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-alert
          v-if="fillForm.fill_mode === 'auto' && fillForm.template_scope === 'individual'"
          title="自动填报会根据字段映射配置从数据库自动填充该教师的数据"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        />
        <el-alert
          v-if="fillForm.fill_mode === 'auto' && fillForm.template_scope === 'collective'"
          title="自动填报会根据字段映射配置从数据库自动填充汇总数据"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        />
        <el-alert
          v-if="fillForm.fill_mode === 'manual'"
          title="手工编辑会打开空模板，您可以手动填写所有字段"
          type="warning"
          :closable="false"
          style="margin-bottom: 15px"
        />
      </el-form>

      <template #footer>
        <el-button @click="showFillDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="openReportView" 
          :disabled="fillForm.template_scope === 'individual' && !fillForm.teacher_id"
        >
          打开填报
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showConfigDialog" title="字段映射配置" width="1000px">
      <el-alert
        title="每个模板占位符都可以从不同的数据源表获取数据"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />
      
      <el-table :data="configTableData" border style="width: 100%">
        <el-table-column prop="placeholder" label="模板占位符" width="140">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.placeholder }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="数据源表" min-width="160">
          <template #default="{ row }">
            <el-select 
              v-model="row.table_name" 
              placeholder="选择数据源表"
              style="width: 100%"
              clearable
              @change="(val) => onTableChange(row)"
            >
              <el-option
                v-for="table in sourceTables"
                :key="table.name"
                :label="table.name_cn"
                :value="table.name"
              />
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column label="字段" min-width="130">
          <template #default="{ row }">
            <el-select 
              v-model="row.field_name" 
              placeholder="选择字段"
              style="width: 100%"
              clearable
              :disabled="!row.table_name"
            >
              <el-option
                v-for="field in getFieldsForTable(row.table_name)"
                :key="field.name"
                :label="field.name_cn"
                :value="field.name"
              >
                <span>{{ field.name_cn }}</span>
                <span class="field-type">({{ field.type }})</span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column label="聚合函数" width="110">
          <template #default="{ row }">
            <el-select 
              v-model="row.aggregate_func" 
              placeholder="无"
              style="width: 100%"
              clearable
              :disabled="!row.field_name"
            >
              <el-option label="计数 COUNT" value="COUNT" />
              <el-option label="求和 SUM" value="SUM" />
              <el-option label="最大值 MAX" value="MAX" />
              <el-option label="最小值 MIN" value="MIN" />
              <el-option label="平均值 AVG" value="AVG" />
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column label="过滤条件" min-width="180">
          <template #default="{ row }">
            <el-input
              v-model="row.filter_condition"
              placeholder="如: 行政级别='副处级'"
              :disabled="!row.field_name"
              clearable
            />
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.field_name" type="success">已配置</el-tag>
            <el-tag v-else type="warning">未配置</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 15px">
        <el-alert
          :title="`已配置 ${configuredCount}/${configTableData.length} 个字段映射`"
          :type="configuredCount === configTableData.length ? 'success' : 'info'"
          show-icon
        />
      </div>
      
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">保存映射</el-button>
      </template>
    </el-dialog>

    <!-- 激活方式配置对话框 -->
    <el-dialog v-model="showActivationDialog" title="激活方式配置" width="600px">
      <el-form :model="activationForm" label-width="120px">
        <el-form-item label="激活方式">
          <el-radio-group v-model="activationForm.activation_type">
            <el-radio label="status_change">任职状态变更</el-radio>
            <el-radio label="scheduled_task">固定时段任务</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 任职状态变更配置 -->
        <template v-if="activationForm.activation_type === 'status_change'">
          <el-form-item label="触发状态">
            <el-select v-model="activationForm.activation_config.trigger_status" placeholder="选择触发状态">
              <el-option label="退休" value="retired" />
              <el-option label="离职" value="resigned" />
              <el-option label="调岗" value="transferred" />
              <el-option label="晋升" value="promoted" />
            </el-select>
          </el-form-item>
        </template>

        <!-- 固定时段任务配置 -->
        <template v-if="activationForm.activation_type === 'scheduled_task'">
          <el-form-item label="执行周期">
            <el-radio-group v-model="activationForm.activation_config.schedule_type">
              <el-radio label="monthly">每月</el-radio>
              <el-radio label="quarterly">每季度</el-radio>
              <el-radio label="yearly">每年</el-radio>
              <el-radio label="custom">自定义</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="执行日期" v-if="activationForm.activation_config.schedule_type === 'monthly'">
            <el-input-number v-model="activationForm.activation_config.day_of_month" :min="1" :max="31" />
            <span style="margin-left: 10px">日</span>
          </el-form-item>

          <el-form-item label="执行月份" v-if="activationForm.activation_config.schedule_type === 'quarterly'">
            <el-checkbox-group v-model="activationForm.activation_config.months">
              <el-checkbox :label="3">3月</el-checkbox>
              <el-checkbox :label="6">6月</el-checkbox>
              <el-checkbox :label="9">9月</el-checkbox>
              <el-checkbox :label="12">12月</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="执行月份" v-if="activationForm.activation_config.schedule_type === 'yearly'">
            <el-select v-model="activationForm.activation_config.month_of_year" placeholder="选择月份">
              <el-option v-for="m in 12" :key="m" :label="m + '月'" :value="m" />
            </el-select>
            <el-input-number v-model="activationForm.activation_config.day_of_month" :min="1" :max="31" style="margin-left: 10px" />
            <span style="margin-left: 10px">日</span>
          </el-form-item>

          <el-form-item label="Cron表达式" v-if="activationForm.activation_config.schedule_type === 'custom'">
            <el-input v-model="activationForm.activation_config.cron_expression" placeholder="如: 0 0 1 * *" />
            <div class="form-tip">格式: 分 时 日 月 周</div>
          </el-form-item>

          <el-form-item label="任务说明">
            <el-input v-model="activationForm.activation_config.description" type="textarea" :rows="2" placeholder="任务说明，如: 每月1日生成工资报表" />
          </el-form-item>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="showActivationDialog = false">取消</el-button>
        <el-button type="primary" @click="saveActivationConfig" :loading="saving">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 手工编辑对话框 -->
    <ManualEditorDialog
      v-model="showManualEditor"
      :template-id="currentEditTemplate.template_id"
      :template-name="currentEditTemplate.template_name"
      :file-type="currentEditTemplate.file_type"
      :file-path="currentEditTemplate.file_path"
      @saved="loadTemplates"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ManualEditorDialog from '@/components/ManualEditorDialog.vue'

const route = useRoute()
const router = useRouter()

const templateList = ref<any[]>([])
const fieldMappings = ref<any[]>([])
const showUploadDialog = ref(false)
const showMappingDialog = ref(false)
const showExportDialog = ref(false)
const showBatchExportDialog = ref(false)
const showSummaryExportDialog = ref(false)
const showConfigDialog = ref(false)
const showActivationDialog = ref(false)
const showFillDialog = ref(false)
const showManualEditor = ref(false)
const currentEditTemplate = ref<any>({})
const uploading = ref(false)
const exporting = ref(false)
const saving = ref(false)
const searchingTeachers = ref(false)

const fillForm = ref({
  template_id: '',
  template_name: '',
  teacher_id: '',
  template_scope: 'individual', // 'individual' 个人模板 或 'collective' 集体模板
  fill_mode: 'auto' // 'auto' 或 'manual'
})

const activationForm = ref({
  template_id: '',
  activation_type: 'status_change',
  activation_config: {
    trigger_status: '',
    schedule_type: 'monthly',
    day_of_month: 1,
    months: [3, 6, 9, 12],
    month_of_year: 1,
    cron_expression: '',
    description: ''
  }
})

const uploadForm = ref({
  template_name: '',
  file: null as any
})

const mappingForm = ref({
  placeholder_name: '',
  table_name: '',
  field_name: ''
})

const exportForm = ref({
  teacher_id: '',
  teacher_name: '',
  template_id: ''
})

const batchExportForm = ref({
  template_id: '',
  teacher_ids: [] as number[]
})

const summaryExportForm = ref({
  template_id: '',
  teacher_ids: [] as number[]
})

const currentConfig = ref({
  template_id: '',
  template_name: '',
  placeholders: [] as string[],
  config: {} as Record<string, any>
})

const teacherOptions = ref<any[]>([])
const selectedTeachers = ref<any[]>([])
const configTableData = ref<any[]>([])
const sourceTables = ref<any[]>([])
const tableFieldsMap = ref<Record<string, any[]>>({})

const configuredCount = computed(() => {
  return configTableData.value.filter(m => m.field_name).length
})

const tableOptions = [
  'teacher_basic_info',
  'teacher_education_record',
  'retirement_report_data',
  'retirement_report_form',
  'position_upgrade_form'
]

const tableFields: Record<string, string[]> = {
  'teacher_basic_info': ['id', 'name', 'id_card', 'gender', 'birth_date', 'ethnicity', 'native_place', 'contact_phone', 'work_start_date', 'entry_date', 'employment_status', 'position', 'job_title', 'technical_level', 'education', 'party_join_date'],
  'teacher_education_record': ['id', 'teacher_id', 'education', 'graduate_date', 'graduate_school', 'major', 'degree'],
  'retirement_report_data': ['id', 'teacher_id', '姓名', '身份证号码', '性别', '出生日期', '民族', '文化程度', '参加工作时间', '工作年限', '籍贯', '现住址', '职务', '岗位', '技术职称', '退休原因', '退休时间'],
  'retirement_report_form': ['id', 'teacher_id', '姓名', '身份证号码', '出生日期', '单位名称', '职务', '岗位', '技术职称', '参加工作时间'],
  'position_upgrade_form': ['id', 'teacher_id', '姓名', '身份证号码', '单位名称', '职务', '岗位等级', '申报时间']
}

const getFieldsForTable = (tableName: string) => {
  return tableFieldsMap.value[tableName] || []
}

const loadSourceTables = async () => {
  try {
    const response = await fetch('/api/template-field-mapping/intermediate-tables')
    if (response.ok) {
      const result = await response.json()
      sourceTables.value = result.tables || []
      
      for (const table of sourceTables.value) {
        await loadTableFields(table.name)
      }
    }
  } catch (error) {
    console.error('加载源数据表列表失败:', error)
  }
}

const loadTableFields = async (tableName: string) => {
  try {
    const response = await fetch(`/api/template-field-mapping/table-fields/${tableName}`)
    if (response.ok) {
      const result = await response.json()
      tableFieldsMap.value[tableName] = result.fields || []
    }
  } catch (error) {
    console.error(`加载表 ${tableName} 字段失败:`, error)
  }
}

const onTableChange = (row: any) => {
  if (!row.table_name) {
    row.field_name = ''
    row.aggregate_func = ''
    row.filter_condition = ''
  }
}

const clearRowConfig = (row: any) => {
  row.table_name = ''
  row.field_name = ''
  row.aggregate_func = ''
  row.filter_condition = ''
}

const loadTemplates = async () => {
  try {
    const response = await fetch('/api/universal-templates/list')
    const res = await response.json()
    if (res.status === 'success') {
      templateList.value = res.data
    }
  } catch (e: any) {
    ElMessage.error('加载模板列表失败')
  }
}

const loadMappings = async () => {
  try {
    const response = await fetch('/api/universal-templates/field-mappings')
    const res = await response.json()
    if (res.status === 'success') {
      fieldMappings.value = res.data
    }
  } catch (e: any) {
    ElMessage.error('加载字段映射失败')
  }
}

const handleFileChange = (file: any) => {
  uploadForm.value.file = file.raw
  if (!uploadForm.value.template_name) {
    uploadForm.value.template_name = file.name.replace(/\.(docx|xlsx)$/i, '')
  }
}

const handleUpload = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('template_name', uploadForm.value.template_name)
    
    const response = await fetch('/api/universal-templates/upload', {
      method: 'POST',
      body: formData
    })
    const res = await response.json()
    
    if (res.status === 'success') {
      ElMessage.success(res.message)
      showUploadDialog.value = false
      uploadForm.value = { template_name: '', file: null }
      loadTemplates()
    }
  } catch (e: any) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleAddMapping = async () => {
  if (!mappingForm.value.placeholder_name || !mappingForm.value.table_name || !mappingForm.value.field_name) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  try {
    const response = await fetch('/api/universal-templates/field-mappings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mappingForm.value)
    })
    const res = await response.json()
    if (res.status === 'success') {
      ElMessage.success('添加成功')
      showMappingDialog.value = false
      mappingForm.value = { placeholder_name: '', table_name: '', field_name: '' }
      loadMappings()
    }
  } catch (e: any) {
    ElMessage.error('添加失败')
  }
}

const deleteMapping = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除此映射?', '提示', { type: 'warning' })
    await fetch(`/api/universal-templates/field-mappings/${row.id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadMappings()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const exportTemplate = (row: any) => {
  exportForm.value.template_id = row.template_id
  exportForm.value.teacher_id = ''
  exportForm.value.teacher_name = ''
  showExportDialog.value = true
}

const handleExport = async () => {
  if (!exportForm.value.teacher_id) {
    ElMessage.warning('请输入教师ID')
    return
  }
  
  exporting.value = true
  try {
    const url = `/api/universal-templates/${exportForm.value.template_id}/export?teacher_id=${exportForm.value.teacher_id}&teacher_name=${exportForm.value.teacher_name}`
    const response = await fetch(url, { method: 'POST' })
    
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '导出失败')
    }
    
    const blob = await response.blob()
    const url2 = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url2
    a.download = `${exportForm.value.template_id}_${exportForm.value.teacher_name || exportForm.value.teacher_id}_已填充.docx`
    a.click()
    window.URL.revokeObjectURL(url2)
    
    ElMessage.success('导出成功')
    showExportDialog.value = false
  } catch (e: any) {
    ElMessage.error(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

const openBatchExport = (row: any) => {
  batchExportForm.value.template_id = row.template_id
  batchExportForm.value.teacher_ids = []
  teacherOptions.value = []
  selectedTeachers.value = []
  showBatchExportDialog.value = true
}

const openSummaryExport = (row: any) => {
  summaryExportForm.value.template_id = row.template_id
  summaryExportForm.value.teacher_ids = []
  teacherOptions.value = []
  selectedTeachers.value = []
  showSummaryExportDialog.value = true
}

const searchTeachers = async (query: string) => {
  if (!query) {
    teacherOptions.value = []
    return
  }
  
  searchingTeachers.value = true
  try {
    const response = await fetch(`/api/universal-templates/teachers/search?q=${encodeURIComponent(query)}`)
    const res = await response.json()
    if (res.status === 'success') {
      teacherOptions.value = res.data || []
      selectedTeachers.value = [...teacherOptions.value]
    }
  } catch (e) {
    console.error('搜索教师失败', e)
  } finally {
    searchingTeachers.value = false
  }
}

const getTeacherName = (teacherId: number) => {
  const teacher = selectedTeachers.value.find(t => t.id === teacherId)
  return teacher ? teacher.name : `ID: ${teacherId}`
}

const removeTeacher = (teacherId: number) => {
  batchExportForm.value.teacher_ids = batchExportForm.value.teacher_ids.filter(id => id !== teacherId)
}

const removeSummaryTeacher = (teacherId: number) => {
  summaryExportForm.value.teacher_ids = summaryExportForm.value.teacher_ids.filter(id => id !== teacherId)
}

const handleBatchExport = async () => {
  if (batchExportForm.value.teacher_ids.length === 0) {
    ElMessage.warning('请选择教师')
    return
  }
  
  exporting.value = true
  try {
    const url = `/api/universal-templates/${batchExportForm.value.template_id}/batch-export?teacher_ids=${batchExportForm.value.teacher_ids.join(',')}`
    const response = await fetch(url, { method: 'POST' })
    
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '批量导出失败')
    }
    
    const blob = await response.blob()
    const url2 = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url2
    a.download = `批量导出_${batchExportForm.value.teacher_ids.length}人.zip`
    a.click()
    window.URL.revokeObjectURL(url2)
    
    ElMessage.success('批量导出成功')
    showBatchExportDialog.value = false
  } catch (e: any) {
    ElMessage.error(e.message || '批量导出失败')
  } finally {
    exporting.value = false
  }
}

const handleSummaryExport = async () => {
  if (summaryExportForm.value.teacher_ids.length === 0) {
    ElMessage.warning('请选择教师')
    return
  }
  
  exporting.value = true
  try {
    const url = `/api/universal-templates/${summaryExportForm.value.template_id}/summary-export?teacher_ids=${summaryExportForm.value.teacher_ids.join(',')}`
    const response = await fetch(url, { method: 'POST' })
    
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '汇总导出失败')
    }
    
    const blob = await response.blob()
    const url2 = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url2
    a.download = `汇总数据_${summaryExportForm.value.teacher_ids.length}人.docx`
    a.click()
    window.URL.revokeObjectURL(url2)
    
    ElMessage.success('汇总导出成功')
    showSummaryExportDialog.value = false
  } catch (e: any) {
    ElMessage.error(e.message || '汇总导出失败')
  } finally {
    exporting.value = false
  }
}

const editConfig = async (row: any) => {
  try {
    const response = await fetch(`/api/universal-templates/${row.template_id}/refresh-placeholders`, {
      method: 'POST'
    })
    const res = await response.json()
    if (res.status === 'success') {
      const placeholders = res.data.placeholders || []
      currentConfig.value = {
        template_id: row.template_id,
        template_name: row.template_name,
        placeholders: placeholders,
        config: row.placeholder_config ? JSON.parse(JSON.stringify(row.placeholder_config)) : {}
      }
      
      configTableData.value = placeholders.map((ph: string) => {
        const existingConfig = currentConfig.value.config[ph] || null
        return {
          placeholder: ph,
          table_name: existingConfig ? (existingConfig['表名'] || existingConfig.table || '') : '',
          field_name: existingConfig ? (existingConfig['字段名'] || existingConfig.field || '') : '',
          aggregate_func: existingConfig ? (existingConfig['聚合函数'] || existingConfig.aggregate_func || '') : '',
          filter_condition: existingConfig ? (existingConfig['过滤条件'] || existingConfig.filter_condition || '') : ''
        }
      })
      ElMessage.success(`已重新提取 ${placeholders.length} 个占位符`)
    } else {
      throw new Error(res.detail || '提取失败')
    }
  } catch (e: any) {
    console.error('重新提取占位符失败', e)
    ElMessage.warning('提取失败，使用原有占位符')
    currentConfig.value = {
      template_id: row.template_id,
      template_name: row.template_name,
      placeholders: row.placeholders || [],
      config: row.placeholder_config ? JSON.parse(JSON.stringify(row.placeholder_config)) : {}
    }
    
    configTableData.value = (row.placeholders || []).map((ph: string) => {
      const existingConfig = currentConfig.value.config[ph] || null
      return {
        placeholder: ph,
        table_name: existingConfig ? (existingConfig['表名'] || existingConfig.table || '') : '',
        field_name: existingConfig ? (existingConfig['字段名'] || existingConfig.field || '') : '',
        aggregate_func: existingConfig ? (existingConfig['聚合函数'] || existingConfig.aggregate_func || '') : '',
        filter_condition: existingConfig ? (existingConfig['过滤条件'] || existingConfig.filter_condition || '') : ''
      }
    })
  }
  
  showConfigDialog.value = true
  loadSourceTables()
}

const clearConfig = (placeholder: string) => {
  if (currentConfig.value.config[placeholder]) {
    delete currentConfig.value.config[placeholder]
  }
}

const saveConfig = async () => {
  const config: Record<string, any> = {}
  for (const row of configTableData.value) {
    if (row.table_name && row.field_name) {
      config[row.placeholder] = {
        '表名': row.table_name,
        '字段名': row.field_name,
        '聚合函数': row.aggregate_func || '',
        '过滤条件': row.filter_condition || ''
      }
    }
  }

  saving.value = true
  try {
    const response = await fetch(`/api/universal-templates/${currentConfig.value.template_id}/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ placeholder_config: config })
    })
    const res = await response.json()
    if (res.status === 'success') {
      ElMessage.success('映射保存成功')
      showConfigDialog.value = false
      loadTemplates()
    }
  } catch (e: any) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 打开填报对话框
const openFillDialog = (template: any) => {
  fillForm.value.template_id = template.template_id
  fillForm.value.template_name = template.template_name
  fillForm.value.teacher_id = ''
  fillForm.value.template_scope = 'individual' // 默认个人模板
  fillForm.value.fill_mode = 'auto'
  teacherOptions.value = []
  showFillDialog.value = true
}

const openReportView = () => {
  const query: any = {}
  if (fillForm.value.fill_mode === 'manual') {
    query.manual = 'true'
  }
  // 集体模板使用 teacher_id=0
  const teacherId = fillForm.value.template_scope === 'collective' ? '0' : fillForm.value.teacher_id
  const queryString = new URLSearchParams(query).toString()
  const url = `/universal-report/${encodeURIComponent(fillForm.value.template_id)}/${teacherId}${queryString ? '?' + queryString : ''}`
  window.open(url, '_blank')
  showFillDialog.value = false
}

// 打开手工编辑对话框
const openManualEdit = (template: any) => {
  currentEditTemplate.value = template
  showManualEditor.value = true
}

const openActivationDialog = (template: any) => {
  activationForm.value.template_id = template.template_id
  activationForm.value.activation_type = template.activation_type || 'status_change'
  activationForm.value.activation_config = {
    trigger_status: template.activation_config?.trigger_status || '',
    schedule_type: template.activation_config?.schedule_type || 'monthly',
    day_of_month: template.activation_config?.day_of_month || 1,
    months: template.activation_config?.months || [3, 6, 9, 12],
    month_of_year: template.activation_config?.month_of_year || 1,
    cron_expression: template.activation_config?.cron_expression || '',
    description: template.activation_config?.description || ''
  }
  showActivationDialog.value = true
}

// 保存激活方式配置
const saveActivationConfig = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/universal-templates/${activationForm.value.template_id}/activation`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        activation_type: activationForm.value.activation_type,
        activation_config: activationForm.value.activation_config
      })
    })
    const res = await response.json()
    if (res.status === 'success') {
      ElMessage.success('激活方式配置保存成功')
      showActivationDialog.value = false
      loadTemplates()
    }
  } catch (e: any) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const deleteTemplate = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除此模板?', '提示', { type: 'warning' })
    await fetch(`/api/universal-templates/${row.template_id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadTemplates()
  loadMappings()
  
  // 检查是否有URL参数（从清单跳转过来）
  const action = route.query.action as string
  const templateId = route.query.template_id as string
  const teacherId = route.query.teacher_id as string
  const teacherName = route.query.teacher_name as string
  
  if (action === 'export' && templateId && teacherId) {
    // 自动打开导出对话框
    setTimeout(() => {
      const template = templateList.value.find(t => t.template_id === templateId)
      if (template) {
        exportForm.value = {
          template_id: templateId,
          teacher_id: parseInt(teacherId),
          teacher_name: teacherName || ''
        }
        showExportDialog.value = true
      }
    }, 500)
  }
})
</script>

<style scoped>
.universal-template-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.placeholder-tag {
  margin-right: 5px;
  margin-bottom: 2px;
}
</style>
