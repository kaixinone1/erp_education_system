<template>
  <div class="universal-template-system">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通用模板自动填报系统</span>
          <div>
            <el-button type="primary" @click="showImportDialog">
              <el-icon><Upload /></el-icon>
              导入新模板
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="templates" border stripe>
        <el-table-column prop="模板ID" label="模板ID" width="150" />
        <el-table-column prop="模板名称" label="模板名称" width="200" />
        <el-table-column prop="模板分类" label="模板分类" width="100" />
        <el-table-column prop="模板类型" label="模板类型" width="120" />
        <el-table-column prop="原始文件" label="原始文件" width="200" />
        <el-table-column prop="创建时间" label="创建时间" width="180" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="previewTemplate(scope.row)">预览</el-button>
            <el-button size="small" type="primary" @click="showFieldMappingDialog(scope.row)">配置映射</el-button>
            <el-button size="small" type="success" @click="showFillDialog(scope.row)">填报</el-button>
            <el-dropdown style="margin-left: 6px" trigger="click">
              <el-button size="small" type="warning">
                导出<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="print" @click="handlePrint(scope.row)">
                    打印
                  </el-dropdown-item>
                  <el-dropdown-item command="excel" @click="exportTemplate(scope.row)">
                    Excel格式
                  </el-dropdown-item>
                  <el-dropdown-item command="template" @click="downloadTemplateFile(scope.row)">
                    Excel模板
                  </el-dropdown-item>
                  <el-dropdown-item v-if="libreOfficeAvailable" command="pdf" @click="exportPdf(scope.row)">
                    PDF格式
                  </el-dropdown-item>
                  <el-dropdown-item command="history" @click="openHistoryDialog(scope.row)" divided>
                    历史文件
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button size="small" type="danger" @click="deleteTemplate(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="importDialogVisible" title="导入新模板" width="650px">
      <el-form :model="importForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="importForm.模板名称" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="importForm.模板类型" placeholder="请选择模板类型">
            <el-option label="呈报表" value="呈报表" />
            <el-option label="审批表" value="审批表" />
            <el-option label="公文" value="公文" />
            <el-option label="统计表" value="统计表" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板分类">
          <el-radio-group v-model="importForm.模板分类">
            <el-radio value="单位汇总表">单位汇总表（统计类）</el-radio>
            <el-radio value="个人表">个人表（明细类）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Excel文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
            :file-list="uploadFileList"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传xlsx/xls文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importTemplate">导入</el-button>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="previewDialogVisible" 
      :title="previewTitle" 
      width="95%"
      top="2vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div id="luckysheet-preview" style="width: 100%; height: 75vh; margin: 0; padding: 0;"></div>
      <template #footer>
        <el-button @click="closePreviewDialog" type="primary">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fieldMappingDialogVisible" title="字段映射配置" width="90%" top="5vh">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="mapping-preview">
            <h4>模板预览（点击单元格配置映射）</h4>
            <div id="mapping-template-preview" class="preview-container" @click="handleCellClick"></div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="mapping-config">
            <h4>当前配置</h4>
            <el-form :model="fieldMappingForm" label-width="100px">
              <el-form-item label="字段名称">
                <el-input v-model="fieldMappingForm.字段名称" placeholder="如：姓名" />
              </el-form-item>
              <el-form-item label="行号">
                <el-input-number v-model="fieldMappingForm.行号" :min="1" />
              </el-form-item>
              <el-form-item label="列号">
                <el-input-number v-model="fieldMappingForm.列号" :min="1" />
              </el-form-item>
              <el-form-item label="数据来源">
                <el-radio-group v-model="fieldMappingForm.数据来源类型" @change="onSourceTypeChange">
                  <el-radio value="数据库字段">数据库字段</el-radio>
                  <el-radio value="公式计算">公式计算</el-radio>
                </el-radio-group>
              </el-form-item>
              <template v-if="fieldMappingForm.数据来源类型 === '数据库字段'">
                <el-form-item label="数据源表">
                  <el-select ref="tableSelectRef" v-model="fieldMappingForm.数据源表" placeholder="请选择数据来源表" filterable @change="onTableChange">
                    <el-option 
                      v-for="table in availableTables" 
                      :key="table.英文表名" 
                      :label="table.显示名称" 
                      :value="table.英文表名" 
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="数据源字段">
                  <el-select ref="fieldSelectRef" v-model="fieldMappingForm.数据源字段" placeholder="请先选择数据源表" filterable :disabled="!fieldMappingForm.数据源表" @change="onFieldChange">
                    <el-option 
                      v-for="field in availableFields" 
                      :key="field.字段名" 
                      :label="field.显示名称" 
                      :value="field.字段名" 
                    />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="currentFieldDictValues.length > 0" label="可选值筛选">
                  <el-select 
                    :key="(fieldMappingForm.数据源表 || '') + '|' + (fieldMappingForm.数据源字段 || '')"
                    ref="dictSelectRef"
                    v-model="fieldMappingForm.字典值选择" 
                    multiple 
                    filterable 
                    collapse-tags
                    collapse-tags-tooltip
                    placeholder="请选择要统计的值（可多选，留空=全选）" 
                    style="width: 100%"
                    @change="nextTick(() => { if (dictSelectRef) dictSelectRef.query = '' })"
                  >
                    <el-option 
                      v-for="val in currentFieldDictValues" 
                      :key="typeof val === 'object' ? val.值 : val" 
                      :label="typeof val === 'object' ? val.标签 : val" 
                      :value="typeof val === 'object' ? val.值 : val" 
                    />
                  </el-select>
                  <div style="color:#909399;font-size:12px;margin-top:4px;">共 {{ currentFieldDictValues.length }} 个可选值，可多选筛选</div>
                </el-form-item>
                <el-form-item label="统计方法">
                  <el-select v-model="fieldMappingForm.统计方法" placeholder="请选择统计方法">
                    <el-option label="计数" value="计数" />
                    <el-option label="求和" value="求和" />
                    <el-option label="平均值" value="平均值" />
                    <el-option label="最大值" value="最大值" />
                    <el-option label="最小值" value="最小值" />
                    <el-option label="求积" value="求积" />
                    <el-option label="取值" value="取值" />
                  </el-select>
                </el-form-item>
              </template>
              <template v-if="fieldMappingForm.数据来源类型 === '公式计算'">
                <el-form-item label="公式表达式">
                  <el-input 
                    v-model="fieldMappingForm.公式表达式" 
                    type="textarea"
                    :rows="2"
                    placeholder="如：{绩效工资标准} * {绩效工资系数}"
                  />
                </el-form-item>
                <div style="color:#909399;font-size:12px;margin:0 0 12px 0;padding-left:100px;line-height:1.6;">
                  用法说明：用 <code>{`{字段名称}`}</code> 引用此模板中已配置映射的字段名。<br/>
                  支持：<code>+</code> <code>-</code> <code>*</code> <code>/</code> <code>%</code> <code>^</code> 和 <code>()</code><br/>
                  支持函数：<code>SUM(a,b,c)</code> <code>AVG(a,b,c)</code> <code>MAX(a,b,c)</code> <code>MIN(a,b,c)</code>
                  <code>IF(条件, 真值, 假值)</code> <code>ROUND(x, n)</code> <code>ABS(x)</code>
                </div>
              </template>
              <el-button type="primary" @click="saveFieldMapping">保存映射</el-button>
            </el-form>

            <el-divider />

            <h4>已配置的字段映射</h4>
            <div style="max-height: 300px; overflow-y: auto;">
              <el-table :data="fieldMappingsList" border size="small">
                <el-table-column prop="字段名称" label="字段名称" width="100" />
                <el-table-column prop="行号" label="行" width="60" />
                <el-table-column prop="列号" label="列" width="60" />
                <el-table-column label="数据源">
                  <template #default="scope">
                    {{ scope.row.数据源_中文 || scope.row.数据源 }}
                  </template>
                </el-table-column>
                <el-table-column prop="统计方法" label="统计方法" width="80" />
                <el-table-column label="操作" width="60" fixed="right">
                  <template #default="scope">
                    <el-button type="danger" size="small" link @click="deleteFieldMapping(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog v-model="fillDialogVisible" title="自动填报" width="850px" top="3vh" @close="onFillDialogClose">
      <!-- 阶段一：参数设置表单 -->
      <template v-if="!fillParamsConfirmed">
        <template v-if="currentFillTemplate.模板分类 === '单位汇总表'">
          <el-form label-width="80px">
            <el-form-item label="年月">
              <el-date-picker v-model="fillForm.年月" type="month" placeholder="选择年月" format="YYYY年M月" value-format="YYYY-MM" style="width: 220px" />
            </el-form-item>
            <el-form-item label="统计范围">
              <template v-if="fillScopeSummary">
                <el-tag type="primary" size="large" style="max-width: 500px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ fillScopeSummary }}</el-tag>
                <el-button size="small" style="margin-left: 10px" type="warning" plain @click="showScopeDialog">修改</el-button>
              </template>
              <template v-else>
                <span style="color: #909399; line-height: 32px;">未设置（将统计全部单位）</span>
                <el-button size="small" style="margin-left: 10px" type="primary" @click="showScopeDialog">设置</el-button>
              </template>
            </el-form-item>
            <el-form-item label="填报口径">
              <template v-if="fillCriteriaSummary">
                <el-tag type="success" size="large" style="max-width: 500px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ fillCriteriaSummary }}</el-tag>
                <el-button size="small" style="margin-left: 10px" type="warning" plain @click="showCriteriaDialog">修改</el-button>
              </template>
              <template v-else>
                <span style="color: #909399; line-height: 32px;">未设置（统计全部标签）</span>
                <el-button size="small" style="margin-left: 10px" type="primary" @click="showCriteriaDialog">设置</el-button>
              </template>
            </el-form-item>
          </el-form>
        </template>

        <template v-else>
          <el-form label-width="80px">
            <el-form-item label="职工查询">
              <el-select
                ref="employeeSelectRef"
                v-model="fillForm.职工ID"
                filterable
                remote
                placeholder="输入身份证号、姓名或ID搜索"
                :remote-method="searchEmployee"
                :loading="employeeSearchLoading"
                style="width: 100%"
                value-key="职工ID"
                @change="onEmployeeSelect; nextTick(() => { if (employeeSelectRef) employeeSelectRef.query = '' })"
              >
                <el-option v-for="emp in employeeSearchResults" :key="emp.职工ID" :value="emp.职工ID">
                  <span style="font-weight: bold;">{{ emp.姓名 }}</span>
                  <span style="float: right; color: #8492a6; font-size: 13px;">{{ emp.身份证号 }}</span>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item v-if="fillForm.职工ID && selectedEmployeeName" label="确认职工">
              <el-tag type="success" size="large">{{ selectedEmployeeName }}</el-tag>
            </el-form-item>
            <el-form-item label="年月">
              <el-date-picker v-model="fillForm.年月" type="month" placeholder="选择年月" format="YYYY年M月" value-format="YYYY-MM" style="width: 220px" />
            </el-form-item>
          </el-form>
        </template>
      </template>

      <!-- 阶段二：HTML预览（空白模板 或 填充后） -->
      <template v-if="fillParamsConfirmed">
        <div v-if="!fillResultHtml" id="blank-template-preview" class="preview-container" ref="previewContainerRef" v-html="blankTemplateHtml"></div>
        <div v-if="fillResultHtml" id="filled-template-preview" class="preview-container" ref="previewContainerRef" v-html="fillResultHtml"></div>
      </template>

      <template #footer>
        <el-button @click="fillDialogVisible = false">关闭</el-button>
        <!-- 阶段一：确定按钮 -->
        <el-button v-if="!fillParamsConfirmed" type="primary" @click="confirmFillParams" :loading="confirmingParams">确定</el-button>
        <!-- 阶段二：空白模板 → 开始填报 -->
        <el-button v-if="fillParamsConfirmed && !fillResultHtml" type="primary" @click="fillTemplate">开始填报</el-button>
        <!-- 阶段二：已填充 → 保存 -->
        <el-button v-if="fillResultHtml" type="warning" @click="saveFilledTemplate" :loading="saving">保存</el-button>
        <el-button v-if="fillResultHtml && !remarkEditable" @click="startEditRemark">修改备注</el-button>
        <el-button v-if="fillResultHtml && remarkEditable" type="primary" @click="saveRemark">保存备注</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="historyDialogVisible" title="历史文件查询" width="700px" top="5vh">
      <el-form :inline="true">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="historyDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="起始日期"
            end-placeholder="截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="queryHistory">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="historyRecords" style="width: 100%" max-height="400">
        <el-table-column prop="保存时间" label="保存时间" width="160" />
        <el-table-column prop="年月" label="年月" width="100" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" type="primary" @click="downloadHistoryFile(scope.row, 'Excel')">Excel下载</el-button>
            <el-button
              size="small"
              type="success"
              @click="downloadHistoryFile(scope.row, 'PDF')"
              :disabled="!scope.row.PDF路径"
            >
              PDF下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="historyDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fileSelectDialogVisible" :title="fileSelectTitle" width="650px" top="5vh">
      <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 13px; color: #606266;">筛选年月：</span>
        <el-date-picker v-model="fileSelectYearMonth" type="month" placeholder="全部" format="YYYY年M月" value-format="YYYY-MM" style="width: 200px" clearable @change="onFileSelectYearMonthChange" />
        <el-button size="small" @click="clearFileSelectFilter" :disabled="!fileSelectYearMonth">清除筛选</el-button>
        <span style="font-size: 12px; color: #909399;">共 {{ fileSelectRecords.length }} 条记录</span>
      </div>
      <div v-if="fileSelectRecords.length === 0" style="text-align:center;padding:30px;color:#999">
        暂无已保存的文件，请先点击「填报」按钮自动填报并保存
      </div>
      <el-table v-else :data="fileSelectRecords" style="width:100%" max-height="350">
        <el-table-column prop="保存时间" label="保存时间" width="160" />
        <el-table-column prop="年月" label="年月" width="100" />
        <el-table-column prop="单位名称" label="单位" min-width="120" />
        <el-table-column label="操作" width="160">
          <template #default="scope">
            <el-button size="small" type="primary" @click="downloadSelectedFile(scope.row)">
              {{ fileSelectActionLabel }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="fileSelectDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="scopeDialogVisible" title="设置统计范围" width="600px" top="5vh">
      <div class="scope-explain">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            从"省"开始，逐级勾选并选择具体单位。<strong>勾选到哪一级，就统计到哪一级。</strong>
          </template>
        </el-alert>
      </div>
      <div class="unit-scope">
        <div class="unit-level" v-for="level in fillLevelKeys" :key="level.label">
          <el-checkbox v-model="fillScope[level.label].勾选" :disabled="!isFillLevelCheckboxEnabled(level.label)">
            {{ level.label }}
          </el-checkbox>
          <el-select
            v-model="fillScope[level.label].unit_id"
            :placeholder="'请选择' + level.label"
            size="small"
            :disabled="!fillScope[level.label].勾选"
            style="width: 200px"
            @change="onFillUnitChange(level.label)"
          >
            <el-option v-for="u in getFillAvailableUnits(level.label)" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </div>
      </div>
      <div class="scope-tip">{{ fillScopeDescription }}</div>
      <template #footer>
        <el-button @click="scopeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmScope">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="criteriaDialogVisible" title="设置填报口径" width="700px" top="5vh">
      <div class="scope-explain">
        <el-alert type="success" :closable="false" show-icon>
          <template #title>选择要纳入统计的标签条件（可多选，不选则包含所有）</template>
        </el-alert>
      </div>
      <el-checkbox-group v-model="tempCriteriaTags" class="criteria-tags">
        <el-checkbox v-for="tag in allTags" :key="tag.id" :value="tag.id" :label="tag.id">
          {{ tag.标签名称 }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="criteriaDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCriteria">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Upload } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = '/api/universal-template'
const UNIT_API = '/api/unit'

const templates = ref([])
const importDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const fieldMappingDialogVisible = ref(false)
const fillDialogVisible = ref(false)
const previewTitle = ref('')
const libreOfficeAvailable = ref(false)
const saving = ref(false)
const historyDialogVisible = ref(false)
const historyDateRange = ref([])
const historyRecords = ref([])
const historyTemplateId = ref('')

const fileSelectDialogVisible = ref(false)
const fileSelectTitle = ref('')
const fileSelectActionLabel = ref('')
const fileSelectRecords = ref([])
const fileSelectMode = ref('excel')
const fileSelectRow = ref(null)
const fileSelectYearMonth = ref('')  // 独立的年月筛选器，不依赖fillForm全局状态

const fillLevelKeys = [
  { label: '省', index: 0 },
  { label: '地区', index: 1 },
  { label: '县', index: 2 },
  { label: '镇', index: 3 },
  { label: '学校', index: 4 }
]

function makeFillEmptyScope() {
  return {
    省: { 勾选: false, unit_id: null, unit_name: '' },
    地区: { 勾选: false, unit_id: null, unit_name: '' },
    县: { 勾选: false, unit_id: null, unit_name: '' },
    镇: { 勾选: false, unit_id: null, unit_name: '' },
    学校: { 勾选: false, unit_id: null, unit_name: '' }
  }
}

const fillScope = ref(makeFillEmptyScope())
const fillUnitLevels = ref({
  省: [],
  地区: [],
  县: [],
  镇: [],
  学校: []
})
const fillCriteriaTags = ref([])
const tempCriteriaTags = ref([])
const currentFillTemplate = ref({})
const allTags = ref([])
const scopeDialogVisible = ref(false)
const criteriaDialogVisible = ref(false)
const employeeSearchLoading = ref(false)
const employeeSearchResults = ref([])
const selectedEmployeeName = ref('')
const fillResultHtml = ref('')
const blankTemplateHtml = ref('')
const fillParamsConfirmed = ref(false)
const previewContainerRef = ref(null)
const remarkEditable = ref(false)
const editedRemark = ref('')
const confirmingParams = ref(false)
const filledConfigFromFill = ref(null)  // 存储 /fill 返回的已填充配置，避免重复填充

const fillScopeSummary = computed(() => {
  const s = fillScope.value
  const parts = []
  for (let i = 0; i < fillLevelKeys.length; i++) {
    const l = fillLevelKeys[i]
    if (s[l.label].勾选 && s[l.label].unit_name) {
      parts.push(s[l.label].unit_name)
    }
  }
  return parts.length > 0 ? parts.join(' ＞ ') : ''
})

const fillCriteriaSummary = computed(() => {
  if (fillCriteriaTags.value.length === 0) return ''
  const names = fillCriteriaTags.value.map(tid => {
    const tag = allTags.value.find(t => t.id === tid)
    return tag ? tag.标签名称 : String(tid)
  })
  if (names.length <= 5) return names.join('、')
  return names.slice(0, 5).join('、') + ` 等${names.length}个`
})

const fillScopeDescription = computed(() => {
  const s = fillScope.value
  const parts = []
  for (let i = 0; i < fillLevelKeys.length; i++) {
    const l = fillLevelKeys[i]
    if (s[l.label].勾选 && s[l.label].unit_name) {
      parts.push({ label: l.label, name: s[l.label].unit_name })
    }
  }
  if (parts.length === 0) {
    const anyChecked = fillLevelKeys.some(l => s[l.label].勾选)
    if (anyChecked) {
      return '⚠️ 已勾选级别但未选择具体单位，请从"省"开始逐级选择'
    }
    return '⚠️ 未设置统计范围 — 将统计全部单位'
  }
  const pathStr = parts.map(p => p.name).join(' ＞ ')
  const deepest = parts[parts.length - 1]
  if (deepest.label === '学校') {
    return `📍 ${pathStr} → 仅覆盖本校`
  }
  const belowLevels = {
    '省': '省、地区、县、镇、学校',
    '地区': '地区、县、镇、学校',
    '县': '县、镇、学校',
    '镇': '镇、学校'
  }
  const below = belowLevels[deepest.label] || '下级全部单位'
  return `📍 ${pathStr} → 覆盖本${deepest.label}及下属${below}`
})

const importForm = ref({
  模板名称: '',
  模板类型: '',
  模板分类: '单位汇总表',
  file: null
})

const fieldMappingForm = ref({
    模板ID: '',
    字段名称: '',
    行号: 1,
    列号: 1,
    数据来源类型: '数据库字段',
    数据源表: '',
    数据源字段: '',
    字典值选择: [],
    统计方法: '求和',
    公式表达式: ''
  })

const fieldMappingsList = ref([])
const currentFieldDictValues = ref([])
const availableTables = ref([])
const availableFields = ref([])
const tableSelectRef = ref(null)
const fieldSelectRef = ref(null)
const dictSelectRef = ref(null)
const employeeSelectRef = ref(null)

const fillForm = ref({
  模板ID: '',
  职工ID: '',
  年月: ''
})

const currentTemplateId = ref('')
const uploadRef = ref(null)
const uploadFileList = ref([])

onMounted(() => {
  loadTemplates()
  checkLibreOffice()
})

async function loadTemplates() {
  try {
    const resp = await fetch(`${API_BASE}/list`)
    const data = await resp.json()
    if (data.成功) {
      templates.value = data.数据
    }
  } catch (error) {
    ElMessage.error('加载模板列表失败: ' + error.message)
  }
}

function showImportDialog() {
  importForm.value = {
    模板名称: '',
    模板类型: '',
    模板分类: '单位汇总表',
    file: null
  }
  uploadFileList.value = []
  importDialogVisible.value = true
}

async function loadFillUnitLevels() {
  try {
    const response = await axios.get(`${UNIT_API}/levels`)
    if (response.data.success) {
      fillUnitLevels.value = response.data.levels
    }
  } catch (error) {
    console.error('加载单位层级失败:', error)
  }
}

async function loadAllTags() {
  try {
    const response = await axios.get(`${API_BASE}/tags`)
    if (response.data.成功) {
      allTags.value = response.data.数据 || []
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

function onFillUnitChange(changedLevel) {
  const levelData = fillUnitLevels.value[changedLevel]
  const selectedId = fillScope.value[changedLevel].unit_id
  if (selectedId && levelData) {
    const found = levelData.find(u => u.id === selectedId)
    if (found) {
      fillScope.value[changedLevel].unit_name = found.name
    }
  } else {
    fillScope.value[changedLevel].unit_name = ''
  }
  
  const currentIdx = fillLevelKeys.findIndex(l => l.label === changedLevel)
  for (let i = currentIdx + 1; i < fillLevelKeys.length; i++) {
    const label = fillLevelKeys[i].label
    fillScope.value[label].unit_id = null
    fillScope.value[label].unit_name = ''
  }
}

function getFillAvailableUnits(level) {
  const idx = fillLevelKeys.findIndex(l => l.label === level)
  if (idx === 0) {
    return fillUnitLevels.value[level] || []
  }
  const parentLevel = fillLevelKeys[idx - 1].label
  const parentId = fillScope.value[parentLevel].unit_id
  if (!parentId) return []
  return (fillUnitLevels.value[level] || []).filter(u => u.parent_id === parentId)
}

function isFillLevelCheckboxEnabled(level) {
  const idx = fillLevelKeys.findIndex(l => l.label === level)
  if (idx === 0) return true
  const parentLevel = fillLevelKeys[idx - 1].label
  return fillScope.value[parentLevel].勾选 && fillScope.value[parentLevel].unit_id
}

function handleFileChange(file) {
  importForm.value.file = file.raw
  
  if (!importForm.value.模板名称 && file.name) {
    const fileName = file.name.replace(/\.(xlsx|xls)$/i, '')
    importForm.value.模板名称 = fileName
  }
}

async function importTemplate() {
  if (!importForm.value.模板名称) {
    ElMessage.warning('请输入模板名称')
    return
  }
  if (!importForm.value.模板类型) {
    ElMessage.warning('请选择模板类型')
    return
  }
  if (!importForm.value.模板分类) {
    ElMessage.warning('请选择模板分类')
    return
  }
  if (!importForm.value.file) {
    ElMessage.warning('请选择Excel文件')
    return
  }

  let originalFileName = ''
  let saveFileName = ''

  try {
    originalFileName = importForm.value.file.name

    const checkResponse = await axios.get(`${API_BASE}/check-filename/${encodeURIComponent(originalFileName)}`)
    
    saveFileName = originalFileName

    if (checkResponse.data.成功 && checkResponse.data.磁盘存在) {
      const referencedTemplates = checkResponse.data.被引用模板 || []

      if (referencedTemplates.length > 0) {
        const templateNames = referencedTemplates.map(t => `"${t.模板名称}"`).join('、')
        await ElMessageBox.confirm(
          `文件"${originalFileName}"已被以下模板使用：${templateNames}。覆盖将导致上述模板无法正常使用！建议重命名。`,
          '文件重名警告',
          {
            confirmButtonText: '强制覆盖',
            cancelButtonText: '重命名',
            type: 'warning',
            distinguishCancelAndClose: true
          }
        )
      } else {
        try {
          await ElMessageBox.confirm(
            `文件"${originalFileName}"已存在但未被任何模板引用，是否覆盖？`,
            '文件重名提示',
            {
              confirmButtonText: '覆盖',
              cancelButtonText: '重命名',
              type: 'info',
              distinguishCancelAndClose: true
            }
          )
        } catch (cancelErr) {
          if (cancelErr === 'cancel' || cancelErr === 'close') {
            const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
            const ext = originalFileName.substring(originalFileName.lastIndexOf('.'))
            const baseName = originalFileName.substring(0, originalFileName.lastIndexOf('.'))
            saveFileName = `${baseName}_${timestamp}${ext}`
          }
        }
      }
    }

    const formData = new FormData()
    formData.append('file', importForm.value.file)
    formData.append('模板名称', importForm.value.模板名称)
    formData.append('模板类型', importForm.value.模板类型)
    formData.append('模板分类', importForm.value.模板分类)
    formData.append('保存文件名', saveFileName)

    const response = await axios.post(`${API_BASE}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data.成功) {
      ElMessage.success('模板导入成功')
      importDialogVisible.value = false
      loadTemplates()
    } else {
      ElMessage.error('导入失败: ' + response.data.消息)
    }
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
      const ext = originalFileName.substring(originalFileName.lastIndexOf('.'))
      const baseName = originalFileName.substring(0, originalFileName.lastIndexOf('.'))
      saveFileName = `${baseName}_${timestamp}${ext}`

      const formData = new FormData()
      formData.append('file', importForm.value.file)
      formData.append('模板名称', importForm.value.模板名称)
      formData.append('模板类型', importForm.value.模板类型)
      formData.append('模板分类', importForm.value.模板分类)
      formData.append('保存文件名', saveFileName)

      try {
        const response = await axios.post(`${API_BASE}/import`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        if (response.data.成功) {
          ElMessage.success('模板导入成功（已自动重命名文件）')
          importDialogVisible.value = false
          loadTemplates()
        } else {
          ElMessage.error('导入失败: ' + response.data.消息)
        }
        return
      } catch (retryErr) {
        ElMessage.error('导入失败: ' + retryErr.message)
        return
      }
    }
    ElMessage.error('导入失败: ' + error.message)
  }
}

function renderTemplateHTML(containerId, htmlContent) {
  const container = document.getElementById(containerId)
  if (container) {
    container.innerHTML = htmlContent
  }
}

function clearPreviewContainer(containerId) {
  const container = document.getElementById(containerId)
  if (container) {
    container.innerHTML = ''
  }
}

async function previewTemplate(row) {
  try {
    previewTitle.value = `${row.模板名称} - 预览`
    previewDialogVisible.value = true
    currentTemplateId.value = row.模板ID

    await nextTick()

    const response = await axios.get(`${API_BASE}/preview/${row.模板ID}`)
    const htmlContent = response.data.数据?.HTML || ''

    renderTemplateHTML('luckysheet-preview', htmlContent)
    ElMessage.success('预览加载成功')
  } catch (error) {
    console.error('预览错误:', error)
    ElMessage.error('预览失败: ' + error.message)
  }
}

function renderTemplateWithMetadata(metadata) {
  const { cells, styles, dimensions, merged_cells, page_setup, page_margins } = metadata
  
  const maxRow = dimensions.max_row || 20
  const maxCol = dimensions.max_column || 10
  
  const mergedMap = new Map()
  merged_cells.forEach(mc => {
    for (let r = mc.r; r < mc.r + mc.rs; r++) {
      for (let c = mc.c; c < mc.c + mc.cs; c++) {
        if (r === mc.r && c === mc.c) {
          mergedMap.set(`${r}-${c}`, { rs: mc.rs, cs: mc.cs, isMaster: true })
        } else {
          mergedMap.set(`${r}-${c}`, { isMaster: false })
        }
      }
    }
  })
  
  const cellData = new Map()
  cells.forEach(cell => {
    cellData.set(`${cell.r}-${cell.c}`, cell.v)
  })
  
  const styleMap = new Map()
  Object.keys(styles).forEach(key => {
    const match = key.match(/^([A-Z]+)(\d+)$/)
    if (match) {
      const col = match[1].charCodeAt(0) - 'A'.charCodeAt(0)
      const row = parseInt(match[2]) - 1
      styleMap.set(`${row}-${col}`, styles[key])
    }
  })
  
  let html = `<style>
    .template-preview { 
      overflow: auto; 
      max-height: 600px; 
      margin: 10px;
    }
    .template-table { 
      border-collapse: collapse; 
      border: 1px solid #000;
      min-width: 100%;
    }
    .template-cell { 
      border: 1px solid #000; 
      padding: 2px; 
      min-height: 20px;
      position: relative;
    }
  </style>
  <div class="template-preview">
    <table class="template-table">`
  
  for (let r = 0; r < maxRow; r++) {
    const rowHeight = dimensions.rows?.[r + 1] || 20
    html += `<tr style="height: ${rowHeight}px;">`
    
    for (let c = 0; c < maxCol; c++) {
      const key = `${r}-${c}`
      const mergedInfo = mergedMap.get(key)
      const cellValue = cellData.get(key)
      const style = styleMap.get(key)
      const colWidth = dimensions.columns?.[String.fromCharCode('A'.charCodeAt(0) + c)] || 80
      
      if (mergedInfo && !mergedInfo.isMaster) continue
      
      let cellStyle = `width: ${colWidth}px;`
      
      if (style) {
        if (style.font) {
          if (style.font.name) cellStyle += ` font-family: ${style.font.name};`
          if (style.font.size) cellStyle += ` font-size: ${style.font.size}pt;`
          if (style.font.bold) cellStyle += ` font-weight: bold;`
          if (style.font.italic) cellStyle += ` font-style: italic;`
          if (style.font.color) cellStyle += ` color: #${style.font.color};`
          if (style.font.strike) cellStyle += ` text-decoration: line-through;`
        }
        
        if (style.fill) {
          if (style.fill.fgColor) cellStyle += ` background-color: #${style.fill.fgColor};`
        }
        
        if (style.alignment) {
          if (style.alignment.horizontal) cellStyle += ` text-align: ${style.alignment.horizontal};`
          if (style.alignment.vertical) cellStyle += ` vertical-align: ${style.alignment.vertical};`
          if (style.alignment.wrapText) cellStyle += ` white-space: pre-wrap; word-wrap: break-word;`
        }
        
        if (style.border) {
          if (style.border.top) cellStyle += ` border-top: ${getBorderStyle(style.border.top)};`
          if (style.border.bottom) cellStyle += ` border-bottom: ${getBorderStyle(style.border.bottom)};`
          if (style.border.left) cellStyle += ` border-left: ${getBorderStyle(style.border.left)};`
          if (style.border.right) cellStyle += ` border-right: ${getBorderStyle(style.border.right)};`
        }
      }
      
      const rowspan = mergedInfo?.rs || 1
      const colspan = mergedInfo?.cs || 1
      const value = cellValue?.m || cellValue?.v || ''
      
      html += `<td class="template-cell" style="${cellStyle}" rowspan="${rowspan}" colspan="${colspan}">${escapeHtml(value)}</td>`
    }
    html += '</tr>'
  }
  
  html += '</table></div>'
  return html
}

function getBorderStyle(border) {
  const styleMap = {
    'thin': '1px solid',
    'medium': '2px solid',
    'thick': '3px solid',
    'dashed': '1px dashed',
    'dotted': '1px dotted',
    'double': '3px double'
  }
  const style = styleMap[border.style] || '1px solid'
  const color = border.color ? `#${border.color}` : '#000000'
  return `${style} ${color}`
}

function escapeHtml(text) {
  if (!text) return ''
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.toString().replace(/[&<>"']/g, m => map[m])
}

function closePreviewDialog() {
  clearPreviewContainer('luckysheet-preview')
  previewDialogVisible.value = false
}

async function loadAvailableTables() {
  try {
    const resp = await fetch(`${API_BASE}/available-tables`)
    const data = await resp.json()
    if (data.成功) {
      availableTables.value = data.数据
    }
  } catch (error) {
    console.error('加载数据表列表失败:', error)
  }
}

async function onTableChange(tableName) {
  availableFields.value = []
  fieldMappingForm.value.数据源字段 = ''
  fieldMappingForm.value.字典值选择 = []
  currentFieldDictValues.value = []
  if (!tableName) {
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/table-columns/${encodeURIComponent(tableName)}`)
    const data = await resp.json()
    availableFields.value = data.成功 ? (data.数据 || []) : []
  } catch (error) {
    availableFields.value = []
    console.error('加载表字段失败:', error)
    ElMessage.error('加载表字段失败: ' + error.message)
  }
  nextTick(() => { if (tableSelectRef.value) tableSelectRef.value.query = '' })
}

async function onFieldChange(fieldName) {
  fieldMappingForm.value.字典值选择 = []
  currentFieldDictValues.value = []
  if (!fieldName) return
  const tableName = fieldMappingForm.value.数据源表
  const field = availableFields.value.find(f => f.字段名 === fieldName)
  if (field && field.字典可选值 && field.字典可选值.length > 0) {
    currentFieldDictValues.value = field.字典可选值
    console.log(`[可选值] 使用缓存: ${tableName}.${fieldName}, 共 ${currentFieldDictValues.value.length} 个值`)
  } else if (field && tableName) {
    try {
      const url = `${API_BASE}/table-distinct-values/${encodeURIComponent(tableName)}/${encodeURIComponent(fieldName)}`
      console.log(`[可选值] 请求API: ${url}`)
      const resp = await fetch(url)
      const data = await resp.json()
      console.log(`[可选值] API响应: status=${resp.status}, 成功=${data.成功}, 数量=${data.数量}`)
      if (data.成功 && data.数据 && data.数据.length > 0) {
        field.字典可选值 = data.数据
        currentFieldDictValues.value = data.数据
      } else if (data.成功 && data.数据 && data.数据.length === 0) {
        console.log(`[可选值] ${tableName}.${fieldName} 无数据`)
        currentFieldDictValues.value = []
      } else {
        console.warn(`[可选值] ${tableName}.${fieldName} 返回异常:`, data)
      }
    } catch (e) {
      console.error(`[可选值] ${tableName}.${fieldName} 请求失败:`, e)
    }
  }
  nextTick(() => {
    if (fieldSelectRef.value) fieldSelectRef.value.query = ''
    if (dictSelectRef.value) dictSelectRef.value.query = ''
  })
}

async function showFieldMappingDialog(row) {
  if (!row || !row.模板ID) {
    ElMessage.warning('模板数据异常，请刷新页面重试')
    return
  }

  const templateId = row.模板ID
  currentTemplateId.value = templateId
  fieldMappingForm.value.模板ID = templateId
  fieldMappingForm.value.数据来源类型 = '数据库字段'
  fieldMappingForm.value.数据源表 = ''
  fieldMappingForm.value.数据源字段 = ''
  fieldMappingForm.value.字典值选择 = []
  fieldMappingForm.value.统计方法 = '求和'
  fieldMappingForm.value.公式表达式 = ''
  currentFieldDictValues.value = []
  availableFields.value = []
  fieldMappingDialogVisible.value = true

  loadAvailableTables()

  try {
    const resp = await fetch(`${API_BASE}/preview/${templateId}`)
    const data = await resp.json()
    if (data.成功) {
      await nextTick()
      const previewDiv = document.getElementById('mapping-template-preview')
      if (previewDiv) {
        previewDiv.innerHTML = data.数据.HTML
      }
    }

    const mResp = await fetch(`${API_BASE}/field-mappings/${templateId}`)
    const mData = await mResp.json()
    if (mData.成功) {
      const mappings = mData.数据
      fieldMappingsList.value = Object.keys(mappings).map(key => {
        const m = mappings[key]
        const isFormula = m.转换函数 && !['计数','求和','平均值','最大值','最小值','求积','取值'].includes(m.转换函数)
        return {
          字段名称: key,
          行号: m.行,
          列号: m.列,
          数据源: isFormula ? `公式: ${m.转换函数}` : (m.数据源 || ''),
          数据源_中文: isFormula ? `公式: ${m.转换函数}` : (m.数据源_中文 || ''),
          统计方法: isFormula ? '公式' : (m.转换函数 || '')
        }
      })
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  }
}

function handleCellClick(event) {
  const cell = event.target.closest('td')
  if (!cell) return

  // 使用 data-row 和 data-col 属性获取实际Excel坐标，而非DOM位置
  // 因为合并单元格使用了colspan/rowspan，DOM位置不等于实际坐标
  const rowIndex = parseInt(cell.getAttribute('data-row') || '0')
  const colIndex = parseInt(cell.getAttribute('data-col') || '0')

  if (!rowIndex || !colIndex) {
    // 降级：使用DOM位置
    const row = cell.parentElement
    const table = row.parentElement
    const domRow = Array.from(table.children).indexOf(row) + 1
    const domCol = Array.from(row.children).indexOf(cell) + 1
    ElMessage.warning(`无法获取单元格坐标，使用DOM位置：第${domRow}行第${domCol}列`)
    fieldMappingForm.value.行号 = domRow
    fieldMappingForm.value.列号 = domCol
    return
  }

  fieldMappingForm.value.行号 = rowIndex
  fieldMappingForm.value.列号 = colIndex

  ElMessage.info(`已选中第${rowIndex}行第${colIndex}列`)
}

async function saveFieldMapping() {
  if (!fieldMappingForm.value.字段名称) {
    ElMessage.warning('请输入字段名称')
    return
  }

  const duplicate = fieldMappingsList.value.find(
    m => m.字段名称 === fieldMappingForm.value.字段名称
  )
  if (duplicate) {
    try {
      await ElMessageBox.confirm(
        `字段名称"${fieldMappingForm.value.字段名称}"已存在（行${duplicate.行号}列${duplicate.列号}），是否覆盖？`,
        '名称重复',
        { confirmButtonText: '覆盖', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }
  }

  const isDbField = fieldMappingForm.value.数据来源类型 === '数据库字段'

  if (isDbField && (!fieldMappingForm.value.数据源表 || !fieldMappingForm.value.数据源字段)) {
    ElMessage.warning('请配置数据源')
    return
  }

  if (!isDbField && !fieldMappingForm.value.公式表达式) {
    ElMessage.warning('请输入公式表达式')
    return
  }

  try {
    const requestBody = {
      模板ID: fieldMappingForm.value.模板ID,
      字段名称: fieldMappingForm.value.字段名称,
      行号: fieldMappingForm.value.行号,
      列号: fieldMappingForm.value.列号,
      数据源: isDbField
        ? `${fieldMappingForm.value.数据源表}.${fieldMappingForm.value.数据源字段}`
        : '',
      转换函数: isDbField
        ? fieldMappingForm.value.统计方法
        : fieldMappingForm.value.公式表达式,
      字典值选择: fieldMappingForm.value.字典值选择 || []
    }
    const response = await axios.post(`${API_BASE}/field-mapping`, requestBody)

    if (response.data.成功) {
      ElMessage.success('字段映射保存成功')

      const mappingsResponse = await axios.get(`${API_BASE}/field-mappings/${fieldMappingForm.value.模板ID}`)
      if (mappingsResponse.data.成功) {
        const mappings = mappingsResponse.data.数据
        fieldMappingsList.value = Object.keys(mappings).map(key => {
          const m = mappings[key]
          const isFormula = m.转换函数 && !['计数','求和','平均值','最大值','最小值','求积','取值'].includes(m.转换函数)
          return {
            字段名称: key,
            行号: m.行,
            列号: m.列,
            数据源: isFormula ? `公式: ${m.转换函数}` : (m.数据源 || ''),
            数据源_中文: isFormula ? `公式: ${m.转换函数}` : (m.数据源_中文 || ''),
            统计方法: isFormula ? '公式' : (m.转换函数 || ''),
            字典值选择: m.字典值选择 || []
          }
        })
      }
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

async function deleteFieldMapping(row) {
  try {
    await ElMessageBox.confirm(`确定要删除字段"${row.字段名称}"的映射吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const resp = await fetch(
      `${API_BASE}/field-mapping/${encodeURIComponent(fieldMappingForm.value.模板ID)}/${encodeURIComponent(row.字段名称)}`,
      { method: 'DELETE' }
    )
    const data = await resp.json()
    if (data.成功) {
      ElMessage.success('已删除')
      const mappingsResponse = await fetch(`${API_BASE}/field-mappings/${fieldMappingForm.value.模板ID}`)
      const mappingsData = await mappingsResponse.json()
      if (mappingsData.成功) {
        const mappings = mappingsData.数据
        fieldMappingsList.value = Object.keys(mappings).map(key => {
          const m = mappings[key]
          const isFormula = m.转换函数 && !['计数','求和','平均值','最大值','最小值','求积','取值'].includes(m.转换函数)
          return {
            字段名称: key,
            行号: m.行,
            列号: m.列,
            数据源: isFormula ? `公式: ${m.转换函数}` : (m.数据源 || ''),
            数据源_中文: isFormula ? `公式: ${m.转换函数}` : (m.数据源_中文 || ''),
            统计方法: isFormula ? '公式' : (m.转换函数 || '')
          }
        })
      }
    } else {
      ElMessage.error(data.消息 || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

function onSourceTypeChange(newType) {
  if (newType === '公式计算') {
    fieldMappingForm.value.数据源表 = ''
    fieldMappingForm.value.数据源字段 = ''
    fieldMappingForm.value.字典值选择 = []
    currentFieldDictValues.value = []
    availableFields.value = []
  } else {
    fieldMappingForm.value.公式表达式 = ''
  }
}

function showFillDialog(row) {
  currentTemplateId.value = row.模板ID
  currentFillTemplate.value = row
  fillForm.value.模板ID = row.模板ID
  fillForm.value.职工ID = ''
  fillForm.value.年月 = ''
  fillScope.value = makeFillEmptyScope()
  fillCriteriaTags.value = []
  fillResultHtml.value = ''
  blankTemplateHtml.value = ''
  fillParamsConfirmed.value = false
  selectedEmployeeName.value = ''
  employeeSearchResults.value = []
  remarkEditable.value = false
  editedRemark.value = ''
  filledConfigFromFill.value = null
  fillDialogVisible.value = true

  if (row.模板分类 === '单位汇总表') {
    loadFillUnitLevels()
    loadAllTags()
  }
}

function onFillDialogClose() {
  // 关闭时重置状态
  fillParamsConfirmed.value = false
  fillResultHtml.value = ''
  blankTemplateHtml.value = ''
  remarkEditable.value = false
  editedRemark.value = ''
  filledConfigFromFill.value = null
}

// 确认填报参数，加载空白模板
async function confirmFillParams() {
  // 校验参数
  if (currentFillTemplate.value.模板分类 !== '单位汇总表') {
    if (!fillForm.value.职工ID) {
      ElMessage.warning('请选择职工')
      return
    }
  }
  if (!fillForm.value.年月) {
    ElMessage.warning('请选择年月')
    return
  }

  confirmingParams.value = true
  try {
    // 加载空白模板HTML（不填充数据），传递年月用于解析{{年月+1}}等日期占位符
    let url = currentFillTemplate.value.模板分类 === '单位汇总表'
      ? `${API_BASE}/preview/${fillForm.value.模板ID}`
      : `${API_BASE}/preview/${fillForm.value.模板ID}?teacher_id=0`
    if (fillForm.value.年月) {
      url += (url.includes('?') ? '&' : '?') + `年月=${encodeURIComponent(fillForm.value.年月)}`
    }
    const response = await axios.get(url)
    if (response.data.成功) {
      blankTemplateHtml.value = response.data.数据?.HTML || ''
      fillParamsConfirmed.value = true
      ElMessage.success('参数已确认，请点击「开始填报」填充数据')
    }
  } catch (error) {
    ElMessage.error('加载模板失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    confirmingParams.value = false
  }
}

function showScopeDialog() {
  scopeDialogVisible.value = true
}

function confirmScope() {
  scopeDialogVisible.value = false
}

function showCriteriaDialog() {
  tempCriteriaTags.value = [...fillCriteriaTags.value]
  criteriaDialogVisible.value = true
  if (allTags.value.length === 0) {
    loadAllTags()
  }
}

function confirmCriteria() {
  fillCriteriaTags.value = [...tempCriteriaTags.value]
  criteriaDialogVisible.value = false
}

async function searchEmployee(keyword) {
  if (!keyword || keyword.length < 1) {
    employeeSearchResults.value = []
    return
  }
  employeeSearchLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/search-employee`, {
      params: { keyword }
    })
    if (response.data.成功) {
      employeeSearchResults.value = response.data.数据 || []
      if (response.data.数据 && response.data.数据.length === 1) {
        selectedEmployeeName.value = response.data.数据[0].姓名
      }
    }
  } catch (error) {
    console.error('搜索职工失败:', error)
  } finally {
    employeeSearchLoading.value = false
  }
}

function onEmployeeSelect(empId) {
  const emp = employeeSearchResults.value.find(e => e.职工ID === empId)
  selectedEmployeeName.value = emp ? emp.姓名 : ''
}

async function fillTemplate() {
  try {
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {}
    }

    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }

    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      let hasAnyScope = false
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
          hasAnyScope = true
        }
      }
      const hasAnyTags = fillCriteriaTags.value && fillCriteriaTags.value.length > 0
      if (hasAnyScope) {
        requestBody.统计范围 = scopeData
      }
      if (hasAnyTags) {
        requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
      }
    }

    console.log('[填报] 请求体:', JSON.stringify(requestBody, null, 2))

    const response = await axios.post(`${API_BASE}/fill`, requestBody)

    console.log('[填报] 响应成功:', response.data.成功)
    console.log('[填报] HTML长度:', response.data.数据?.HTML?.length || 0)
    
    if (response.data.成功) {
      fillResultHtml.value = response.data.数据?.HTML || ''
      // 存储已填充配置，避免后续保存时重复填充
      filledConfigFromFill.value = response.data.数据?.配置 || null
      remarkEditable.value = false
      ElMessage.success('数据填报成功')
    }
  } catch (error) {
    console.error('[填报] 失败:', error.message, error)
    ElMessage.error('填报失败: ' + error.message)
  }
}

async function downloadTemplateFile(row) {
  try {
    const response = await axios.get(`${API_BASE}/download-template/${row.模板ID}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${row.模板名称}_模板.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('下载失败: ' + error.message)
  }
}

function getExportFilename(response, defaultName) {
  const contentDisposition = response.headers['content-disposition']
  if (contentDisposition) {
    const match5987 = contentDisposition.match(/filename\*=utf-8''(.+)/i)
    if (match5987 && match5987[1]) {
      return decodeURIComponent(match5987[1])
    }
    const match = contentDisposition.match(/filename[^;=\n]*=["']?((["']).*?\2|[^;\n]*)["']?/i)
    if (match && match[1]) {
      return match[1].replace(/["']/g, '')
    }
  }
  return defaultName
}

function getFillRequestBodyForRow(row) {
  if (fillForm.value.模板ID !== row.模板ID) {
    return null
  }
  const requestBody = {
    模板ID: row.模板ID,
    查询条件: {}
  }
  if (fillForm.value.职工ID) {
    requestBody.查询条件.职工ID = fillForm.value.职工ID
  }
  if (fillForm.value.年月) {
    requestBody.查询条件.年月 = fillForm.value.年月
  }
  if (row.模板分类 === '单位汇总表') {
    const scopeData = { 单位范围: {} }
    let hasAnyScope = false
    for (const key of Object.keys(fillScope.value)) {
      const item = fillScope.value[key]
      if (item.勾选 && item.unit_id) {
        scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
        hasAnyScope = true
      }
    }
    const hasAnyTags = fillCriteriaTags.value && fillCriteriaTags.value.length > 0
    if (hasAnyScope) {
      requestBody.统计范围 = scopeData
    }
    if (hasAnyTags) {
      requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
    }
  }
  return requestBody
}

async function exportTemplate(row) {
  await openFileSelectDialog(row, 'excel')
}

async function handlePrint(row) {
  await openFileSelectDialog(row, 'print')
}

async function exportPdf(row) {
  await openFileSelectDialog(row, 'pdf')
}

async function fetchSavedFiles(templateId, yearMonth) {
  let url = `${API_BASE}/saved-files/${templateId}`
  if (yearMonth) {
    const [y, mStr] = yearMonth.split('-')
    const m = parseInt(mStr)
    const ymFormatted = `${y}年${m}月`
    url += `?年月=${encodeURIComponent(ymFormatted)}`
  }
  const response = await axios.get(url)
  return response.data.数据 || []
}

async function openFileSelectDialog(row, mode) {
  fileSelectRow.value = row
  fileSelectMode.value = mode
  fileSelectYearMonth.value = ''  // 重置筛选器，默认显示全部
  if (mode === 'print') {
    fileSelectTitle.value = '选择要打印的文件'
    fileSelectActionLabel.value = '打印'
  } else if (mode === 'pdf') {
    fileSelectTitle.value = '选择要导出的PDF文件'
    fileSelectActionLabel.value = '导出PDF'
  } else {
    fileSelectTitle.value = '选择要导出的Excel文件'
    fileSelectActionLabel.value = '导出Excel'
  }
  try {
    fileSelectRecords.value = await fetchSavedFiles(row.模板ID, '')
  } catch (error) {
    fileSelectRecords.value = []
    ElMessage.error('获取文件列表失败: ' + (error.response?.data?.detail || error.message))
  }
  fileSelectDialogVisible.value = true
}

async function onFileSelectYearMonthChange(value) {
  if (!fileSelectRow.value) return
  try {
    fileSelectRecords.value = await fetchSavedFiles(fileSelectRow.value.模板ID, value || '')
  } catch (error) {
    fileSelectRecords.value = []
    ElMessage.error('获取文件列表失败: ' + (error.response?.data?.detail || error.message))
  }
}

function clearFileSelectFilter() {
  fileSelectYearMonth.value = ''
  onFileSelectYearMonthChange('')
}

function downloadSelectedFile(record) {
  fileSelectDialogVisible.value = false
  if (fileSelectMode.value === 'print') {
    if (!record.有HTML) {
      ElMessage.warning('该记录无HTML文件，请先点击「填报」生成文件')
      return
    }
    const htmlUrl = `${API_BASE}/history-file/${record.ID}?format=HTML`
    const overlay = document.createElement('div')
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:99999;background:#fff;display:flex;flex-direction:column;'
    const closeBar = document.createElement('div')
    closeBar.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:8px 16px;background:#f5f5f5;border-bottom:1px solid #ddd;flex-shrink:0;'
    const titleSpan = document.createElement('span')
    titleSpan.style.cssText = 'font-size:14px;color:#333;'
    titleSpan.textContent = '打印预览'
    const btnGroup = document.createElement('div')
    btnGroup.style.cssText = 'display:flex;gap:8px;'
    const printBtn = document.createElement('button')
    printBtn.textContent = '打印'
    printBtn.style.cssText = 'padding:6px 16px;background:#409eff;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:13px;'
    printBtn.onclick = () => {
      try {
        printIframe.contentWindow.focus()
        printIframe.contentWindow.print()
      } catch (e) {
        ElMessage.error('打印失败: ' + e.message)
      }
    }
    const closeBtn = document.createElement('button')
    closeBtn.textContent = '关闭'
    closeBtn.style.cssText = 'padding:6px 16px;background:#f56c6c;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:13px;'
    closeBtn.onclick = () => {
      if (overlay.parentNode) {
        document.body.removeChild(overlay)
      }
    }
    btnGroup.appendChild(printBtn)
    btnGroup.appendChild(closeBtn)
    closeBar.appendChild(titleSpan)
    closeBar.appendChild(btnGroup)
    overlay.appendChild(closeBar)
    const printIframe = document.createElement('iframe')
    printIframe.src = htmlUrl
    printIframe.style.cssText = 'flex:1;width:100%;border:none;'
    overlay.appendChild(printIframe)
    document.body.appendChild(overlay)
    printIframe.onload = () => {
      setTimeout(() => {
        try {
          printIframe.contentWindow.focus()
          printIframe.contentWindow.print()
        } catch (e) {
          ElMessage.error('打印失败: ' + e.message)
        }
      }, 600)
    }
  } else if (fileSelectMode.value === 'pdf') {
    if (!record.有PDF) {
      ElMessage.warning('该记录无PDF文件')
      return
    }
    const link = document.createElement('a')
    link.href = `${API_BASE}/history-file/${record.ID}?format=PDF`
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('PDF导出成功')
  } else {
    if (!record.有Excel) {
      ElMessage.warning('该记录无Excel文件')
      return
    }
    const link = document.createElement('a')
    link.href = `${API_BASE}/history-file/${record.ID}?format=Excel`
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('Excel导出成功')
  }
}

async function checkLibreOffice() {
  try {
    const response = await axios.get(`${API_BASE}/check-libreoffice`)
    libreOfficeAvailable.value = response.data.可用
  } catch {
    libreOfficeAvailable.value = false
  }
}

async function exportFilledTemplate() {
  try {
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {}
    }
    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }
    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      let hasAnyScope2 = false
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
          hasAnyScope2 = true
        }
      }
      const hasAnyTags2 = fillCriteriaTags.value && fillCriteriaTags.value.length > 0
      if (hasAnyScope2) {
        requestBody.统计范围 = scopeData
      }
      if (hasAnyTags2) {
        requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
      }
    }

    const response = await axios.post(`${API_BASE}/export`, requestBody, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `填报结果.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

async function saveFilledTemplate() {
  try {
    saving.value = true
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {}
    }
    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }
    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      let hasAnyScope3 = false
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
          hasAnyScope3 = true
        }
      }
      const hasAnyTags3 = fillCriteriaTags.value && fillCriteriaTags.value.length > 0
      if (hasAnyScope3) {
        requestBody.统计范围 = scopeData
      }
      if (hasAnyTags3) {
        requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
      }
    }
    
    // 发送已填充配置（避免后端重新填充，保证数据一致性）
    if (filledConfigFromFill.value) {
      requestBody.填报配置 = filledConfigFromFill.value
    }
    
    // 读取编辑后的备注
    const remark = getEditedRemark()
    if (remark) {
      requestBody.备注 = remark
    }
    
    const response = await axios.post(`${API_BASE}/save`, requestBody)
    if (response.data.成功) {
      ElMessage.success(`保存成功！Excel: ${response.data.数据.Excel文件}${response.data.数据.PDF文件 ? '  PDF: ' + response.data.数据.PDF文件 : ''}`)
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

// 使备注栏直接可编辑
function makeRemarkEditable() {
  const container = previewContainerRef.value
  if (!container) return
  
  // 查找所有包含"备注"的单元格
  const allCells = container.querySelectorAll('td, th, span, p, div')
  let found = false
  allCells.forEach((cell) => {
    const text = cell.textContent || ''
    if (text.includes('备注')) {
      // 只对包含"备注"文字的 td 做可编辑
      const td = cell.closest('td') || cell
      td.setAttribute('contenteditable', 'true')
      td.style.backgroundColor = '#fffbe6'
      td.style.border = '2px dashed #faad14'
      td.style.padding = '4px'
      td.title = '点击此处直接编辑备注内容，完成后点击下方「保存备注」按钮'
      remarkEditable.value = true
      found = true
    }
  })
  
  if (!found) {
    // 如果没找到备注栏，也查找"备注："前缀
    allCells.forEach((cell) => {
      const text = cell.textContent || ''
      if (text.includes('备注：') && !cell.querySelector('[contenteditable]')) {
        const td = cell.closest('td') || cell
        td.setAttribute('contenteditable', 'true')
        td.style.backgroundColor = '#fffbe6'
        td.style.border = '2px dashed #faad14'
        td.style.padding = '4px'
        td.title = '点击此处直接编辑备注内容，完成后点击下方「保存备注」按钮'
        remarkEditable.value = true
      }
    })
  }
}

// 锁定备注栏（不可编辑）
function lockRemark() {
  const container = previewContainerRef.value
  if (!container) return
  const editableCells = container.querySelectorAll('[contenteditable="true"]')
  editableCells.forEach((cell) => {
    cell.removeAttribute('contenteditable')
    cell.style.backgroundColor = ''
    cell.style.border = ''
    cell.style.padding = ''
    cell.title = ''
  })
  remarkEditable.value = false
}

// 点击"修改备注"按钮，激活备注栏编辑
async function startEditRemark() {
  await nextTick()
  makeRemarkEditable()
}

// 保存备注（纯前端操作：更新缓存中的备注，不调后端API）
async function saveRemark() {
  const container = previewContainerRef.value
  if (!container) {
    ElMessage.error('未找到备注区域')
    return
  }
  
  // 找到 contenteditable 的备注元素
  const editableCell = container.querySelector('[contenteditable="true"]')
  if (!editableCell) {
    ElMessage.error('未找到可编辑的备注栏')
    return
  }
  
  // 用 innerText 读取内容（保留换行），再用 innerHTML 兜底处理 <br>、<div>、<p>
  let remarkContent = (editableCell.innerText || editableCell.textContent || '').trim()
  // 如果 innerText 没换行但 innerHTML 有 <br>、<div>、<p>，用 innerHTML 转换
  if (!remarkContent.includes('\n')) {
    const html = editableCell.innerHTML || ''
    if (/<br/i.test(html) || /<div/i.test(html) || /<p/i.test(html)) {
      remarkContent = html
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<div[^>]*>/gi, '\n')
        .replace(/<\/div>/gi, '')
        .replace(/<p[^>]*>/gi, '\n')
        .replace(/<\/p>/gi, '')
        .replace(/<[^>]+>/g, '')
        .replace(/\n{2,}/g, '\n')
        .trim()
    }
  }
  
  // 去掉可能存在的"备注："前缀
  const cleanedRemark = remarkContent.replace(/^备注[：:]\s*/, '')
  
  // 纯前端操作：更新缓存中的备注
  editedRemark.value = cleanedRemark
  
  // 同步更新已填充配置中的备注单元格
  if (filledConfigFromFill.value && filledConfigFromFill.value.单元格数据) {
    for (const cell of filledConfigFromFill.value.单元格数据) {
      const 显示值 = String(cell.显示值 || '')
      if (显示值.startsWith('备注：') || 显示值 === '备注' || 显示值.includes('备注')) {
        // 确保"备注："单独占一行，每条信息单独占一行
        cell.显示值 = cleanedRemark ? `备注：\n${cleanedRemark}` : cleanedRemark
        break
      }
    }
  }
  
  // 锁定备注栏
  lockRemark()
  ElMessage.success('备注已保存到缓存，请点击「保存」按钮保存完整文件')
}

// 获取编辑后的备注（从DOM或已保存的编辑记录）
function getEditedRemark() {
  // 优先从编辑记录中获取
  if (editedRemark.value) {
    return editedRemark.value
  }
  // 如果备注栏当前可编辑，从DOM中读取
  const container = previewContainerRef.value
  if (container) {
    const editableCell = container.querySelector('[contenteditable="true"]')
    if (editableCell) {
      const text = (editableCell.textContent || '').trim()
      if (text) return text
    }
  }
  return ''
}

function openHistoryDialog(row) {
  historyTemplateId.value = row.模板ID
  historyDateRange.value = []
  historyRecords.value = []
  historyDialogVisible.value = true
}

async function queryHistory() {
  try {
    const body = { 模板ID: historyTemplateId.value }
    if (historyDateRange.value && historyDateRange.value.length === 2) {
      body.起始日期 = historyDateRange.value[0]
      body.截止日期 = historyDateRange.value[1]
    }
    const response = await axios.post(`${API_BASE}/history`, body)
    historyRecords.value = response.data.数据 || []
    if (historyRecords.value.length === 0) {
      ElMessage.info('未找到历史文件')
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + (error.response?.data?.detail || error.message))
  }
}

function downloadHistoryFile(record, format) {
  const url = `${API_BASE}/history-file/${record.ID}?format=${format}`
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', '')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function deleteTemplate(row) {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await axios.delete(`${API_BASE}/${row.模板ID}`)
    if (response.data.成功) {
      ElMessage.success('删除成功')
      loadTemplates()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}
</script>

<style scoped>
.universal-template-system {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scope-explain {
  margin-bottom: 10px;
}

.unit-scope {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.unit-level {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f5f7fa;
}

.unit-level:hover {
  background: #ecf5ff;
}

.scope-tip {
  margin-top: 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-left: 4px solid #67c23a;
  border-radius: 4px;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.political-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.political-tags .el-checkbox {
  margin-right: 0;
  padding: 6px 12px;
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 4px;
}

.criteria-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.criteria-tags .el-checkbox {
  margin-right: 0;
  padding: 6px 12px;
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 4px;
}

.preview-container {
  width: 100%;
  overflow: auto;
  border: 1px solid #dcdfe6;
  padding: 20px;
  background: #fff;
  max-height: 70vh;
}

.mapping-preview {
  border: 1px solid #dcdfe6;
  padding: 15px;
  border-radius: 4px;
}

.mapping-config {
  border: 1px solid #dcdfe6;
  padding: 15px;
  border-radius: 4px;
}

.mapping-config h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style>

