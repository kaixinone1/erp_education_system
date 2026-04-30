<template>
  <div class="html-template-editor">
    <!-- 顶部工具栏 -->
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>HTML模板编辑器 - {{ templateName }}</h2>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="autoExtractFields" :loading="extracting">
          <el-icon><MagicStick /></el-icon>
          智能提取字段
        </el-button>
        <el-button type="primary" @click="saveFields" :loading="saving">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="editor-container">
      <!-- 左侧：HTML预览和编辑 -->
      <div class="preview-panel">
        <div class="panel-header">
          <h3>点击表格单元格添加输入框</h3>
          <el-alert
            title="操作说明：点击需要填写的空白单元格，输入字段名称后保存"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
        <div class="html-container" ref="htmlContainer">
          <!-- HTML内容将通过v-html渲染 -->
          <div v-html="htmlContent" class="html-content"></div>
        </div>
      </div>

      <!-- 右侧：字段列表 -->
      <div class="fields-panel">
        <div class="panel-header">
          <h3>字段列表 ({{ fields.length }})</h3>
          <el-button type="danger" size="small" @click="clearAllFields">
            清空全部
          </el-button>
        </div>
        
        <el-scrollbar class="fields-list">
          <div
            v-for="(field, index) in fields"
            :key="index"
            class="field-item"
          >
            <div class="field-info">
              <span class="field-index">{{ index + 1 }}</span>
              <el-input
                v-model="field.name"
                size="small"
                placeholder="字段名称"
                @change="updateFieldName(index)"
              />
            </div>
            <div class="field-actions">
              <el-button
                type="danger"
                size="small"
                circle
                @click="removeField(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          
          <el-empty v-if="fields.length === 0" description="暂无字段，点击左侧表格添加" />
        </el-scrollbar>
      </div>
    </div>

    <!-- 添加字段对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加输入框"
      width="500px"
    >
      <el-form :model="newField" label-width="100px">
        <el-form-item label="字段名称">
          <el-select
            v-model="newField.name"
            placeholder="选择字段名称"
            filterable
            style="width: 100%"
            @change="onFieldNameChange"
          >
            <el-option-group label="教师基本信息">
              <el-option label="姓名" value="姓名" />
              <el-option label="身份证号" value="身份证号" />
              <el-option label="性别" value="性别" />
              <el-option label="出生日期" value="出生日期" />
              <el-option label="民族" value="民族" />
              <el-option label="籍贯" value="籍贯" />
              <el-option label="参加工作时间" value="参加工作时间" />
              <el-option label="联系电话" value="联系电话" />
            </el-option-group>
            <el-option-group label="档案信息">
              <el-option label="档案出生日期" value="档案出生日期" />
              <el-option label="档案参加工作时间" value="档案参加工作时间" />
              <el-option label="退休日期" value="退休日期" />
              <el-option label="退休类别" value="退休类别" />
            </el-option-group>
            <el-option-group label="单位信息">
              <el-option label="单位名称" value="单位名称" />
              <el-option label="单位意见" value="单位意见" />
              <el-option label="主管部门意见" value="主管部门意见" />
              <el-option label="审批日期" value="审批日期" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="字段标识">
          <el-select
            v-model="newField.id"
            placeholder="选择字段标识"
            filterable
            style="width: 100%"
          >
            <el-option-group label="教师基本信息">
              <el-option label="teacher_basic_info.name" value="teacher_basic_info.name" />
              <el-option label="teacher_basic_info.id_card" value="teacher_basic_info.id_card" />
              <el-option label="teacher_basic_info.gender" value="teacher_basic_info.gender" />
              <el-option label="teacher_basic_info.birth_date" value="teacher_basic_info.birth_date" />
              <el-option label="teacher_basic_info.ethnicity" value="teacher_basic_info.ethnicity" />
              <el-option label="teacher_basic_info.native_place" value="teacher_basic_info.native_place" />
              <el-option label="teacher_basic_info.work_start_date" value="teacher_basic_info.work_start_date" />
              <el-option label="teacher_basic_info.contact_phone" value="teacher_basic_info.contact_phone" />
            </el-option-group>
            <el-option-group label="档案信息">
              <el-option label="teacher_basic_info.archive_birth_date" value="teacher_basic_info.archive_birth_date" />
              <el-option label="teacher_basic_info.archive_work_date" value="teacher_basic_info.archive_work_date" />
              <el-option label="retirement.date" value="retirement.date" />
              <el-option label="retirement.type" value="retirement.type" />
            </el-option-group>
            <el-option-group label="单位信息">
              <el-option label="unit.name" value="unit.name" />
              <el-option label="unit.opinion" value="unit.opinion" />
              <el-option label="dept.opinion" value="dept.opinion" />
              <el-option label="approval.date" value="approval.date" />
            </el-option-group>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAddField">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Check, Delete, MagicStick } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const templateId = route.params.id as string

// 数据
const templateName = ref('')
const htmlContent = ref('')
const fields = ref<Array<{name: string, id: string, cellIndex: number}>>([])
const saving = ref(false)
const extracting = ref(false)
const showAddDialog = ref(false)
const newField = ref({ name: '', id: '' })
const selectedCell = ref<HTMLElement | null>(null)
const htmlContainer = ref<HTMLElement | null>(null)

// 字段映射表 - 用于智能提取
const fieldMapping: Record<string, { name: string, id: string }> = {
  '姓名': { name: '姓名', id: 'teacher_basic_info.name' },
  '性别': { name: '性别', id: 'teacher_basic_info.gender' },
  '身份证号': { name: '身份证号', id: 'teacher_basic_info.id_card' },
  '出生日期': { name: '出生日期', id: 'teacher_basic_info.birth_date' },
  '民族': { name: '民族', id: 'teacher_basic_info.ethnicity' },
  '籍贯': { name: '籍贯', id: 'teacher_basic_info.native_place' },
  '参加工作时间': { name: '参加工作时间', id: 'teacher_basic_info.work_start_date' },
  '档案出生日期': { name: '档案出生日期', id: 'teacher_basic_info.archive_birth_date' },
  '档案参加工作时间': { name: '档案参加工作时间', id: 'teacher_basic_info.archive_work_date' },
  '退休日期': { name: '退休日期', id: 'retirement.date' },
  '退休类别': { name: '退休类别', id: 'retirement.type' },
  '单位名称': { name: '单位名称', id: 'unit.name' },
  '单位意见': { name: '单位意见', id: 'unit.opinion' },
  '主管部门意见': { name: '主管部门意见', id: 'dept.opinion' },
  '审批日期': { name: '审批日期', id: 'approval.date' },
  '联系电话': { name: '联系电话', id: 'teacher_basic_info.contact_phone' }
}

// 字段名称变化时自动匹配标识
const onFieldNameChange = (value: string) => {
  const mapping = fieldMapping[value]
  if (mapping) {
    newField.value.id = mapping.id
  }
}

// 加载模板
const loadTemplate = async () => {
  try {
    // 获取模板信息
    const response = await fetch(`/api/templates/list`)
    const result = await response.json()
    if (result.status === 'success') {
      const templates = result.templates || result.data || []
      const template = templates.find((t: any) => t.template_id === templateId)
      if (template) {
        templateName.value = template.template_name
      }
    }

    // 获取HTML内容
    const htmlResponse = await fetch(`/api/templates/${templateId}/preview?teacher_id=273`)
    htmlContent.value = await htmlResponse.text()

    // 加载已有字段
    await loadFields()

    // 渲染后添加点击事件
    nextTick(() => {
      addClickHandlers()
    })
  } catch (error) {
    ElMessage.error('加载模板失败')
  }
}

// 加载已有字段
const loadFields = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId}/fields`)
    const result = await response.json()
    if (result.status === 'success') {
      const fieldData = result.fields || result.data || []
      fields.value = fieldData.map((f: any) => ({
        name: f.field_label || f.field_name,
        id: f.field_name,
        cellIndex: f.position_data?.cellIndex || 0
      }))
    }
  } catch (error) {
    console.error('加载字段失败:', error)
  }
}

// 添加点击事件处理
const addClickHandlers = () => {
  if (!htmlContainer.value) return

  const tables = htmlContainer.value.querySelectorAll('table')
  tables.forEach((table, tableIndex) => {
    const cells = table.querySelectorAll('td, th')
    cells.forEach((cell, cellIndex) => {
      const htmlCell = cell as HTMLElement
      
      // 获取单元格文本内容
      const text = htmlCell.textContent?.trim() || ''
      
      // 只处理空白单元格（没有文本内容）
      if (!text || text === '') {
        htmlCell.style.cursor = 'pointer'
        htmlCell.style.position = 'relative'
        
        // 添加悬停效果
        htmlCell.addEventListener('mouseenter', () => {
          htmlCell.style.backgroundColor = '#e6f7ff'
          htmlCell.style.border = '2px dashed #1890ff'
        })
        
        htmlCell.addEventListener('mouseleave', () => {
          htmlCell.style.backgroundColor = ''
          htmlCell.style.border = ''
        })
        
        // 添加点击事件
        htmlCell.addEventListener('click', (e) => {
          e.preventDefault()
          e.stopPropagation()
          selectedCell.value = htmlCell
          newField.value = { name: '', id: '' }
          showAddDialog.value = true
        })
      }
    })
  })
}

// 智能提取字段
const autoExtractFields = async () => {
  if (!htmlContainer.value) return

  extracting.value = true
  try {
    const tables = htmlContainer.value.querySelectorAll('table')
    let cellIndex = 0
    let extractedCount = 0

    tables.forEach((table) => {
      const rows = table.querySelectorAll('tr')
      rows.forEach((row) => {
        const cells = row.querySelectorAll('td, th')
        cells.forEach((cell, idx) => {
          const text = cell.textContent?.trim() || ''

          // 检查是否是标签单元格（包含冒号或特定关键词）
          const isLabelCell = /[:：]$/.test(text) ||
            ['姓名', '性别', '身份证号', '出生日期', '民族', '籍贯',
             '参加工作时间', '档案出生日期', '档案参加工作时间',
             '退休日期', '退休类别', '单位名称', '联系电话'].some(keyword =>
              text.includes(keyword) && text.length < 15
            )

          if (isLabelCell) {
            // 查找下一个空白单元格
            const nextCell = cells[idx + 1]
            if (nextCell && !nextCell.textContent?.trim()) {
              // 尝试匹配字段
              let matchedField = null
              for (const [key, value] of Object.entries(fieldMapping)) {
                if (text.includes(key)) {
                  matchedField = value
                  break
                }
              }

              if (matchedField) {
                // 在下一个单元格插入输入框
                const input = document.createElement('input')
                input.type = 'text'
                input.name = matchedField.id
                input.id = matchedField.id
                input.className = 'html-form-input'
                input.style.cssText = 'width:95%;height:90%;border:1px solid #409eff;padding:2px 5px;'
                input.placeholder = matchedField.name

                nextCell.innerHTML = ''
                nextCell.appendChild(input)

                // 添加到字段列表
                fields.value.push({
                  name: matchedField.name,
                  id: matchedField.id,
                  cellIndex: cellIndex
                })

                extractedCount++
              }
            }
          }

          cellIndex++
        })
      })
    })

    if (extractedCount > 0) {
      ElMessage.success(`智能提取完成！共提取 ${extractedCount} 个字段`)
    } else {
      ElMessage.info('未识别到可提取的字段，请手动添加')
    }
  } catch (error) {
    console.error('提取失败:', error)
    ElMessage.error('智能提取失败')
  } finally {
    extracting.value = false
  }
}

// 确认添加字段
const confirmAddField = () => {
  if (!newField.value.name || !newField.value.id) {
    ElMessage.warning('请填写字段名称和标识')
    return
  }

  if (!selectedCell.value) return

  // 在单元格中插入输入框
  const input = document.createElement('input')
  input.type = 'text'
  input.name = newField.value.id
  input.id = newField.value.id
  input.className = 'html-form-input'
  input.style.cssText = 'width:95%;height:90%;border:1px solid #ccc;padding:2px 5px;'
  input.placeholder = newField.value.name

  selectedCell.value.innerHTML = ''
  selectedCell.value.appendChild(input)

  // 添加到字段列表
  fields.value.push({
    name: newField.value.name,
    id: newField.value.id,
    cellIndex: fields.value.length
  })

  showAddDialog.value = false
  ElMessage.success('添加成功')
}

// 更新字段名称
const updateFieldName = (index: number) => {
  const field = fields.value[index]
  // 更新对应的input placeholder
  const inputs = htmlContainer.value?.querySelectorAll('input')
  if (inputs && inputs[index]) {
    inputs[index].placeholder = field.name
  }
}

// 删除字段
const removeField = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定删除这个字段吗？', '提示', { type: 'warning' })
    fields.value.splice(index, 1)
    
    // 重新渲染HTML
    await loadTemplate()
    ElMessage.success('删除成功')
  } catch {
    // 取消
  }
}

// 清空全部字段
const clearAllFields = async () => {
  try {
    await ElMessageBox.confirm('确定清空所有字段吗？', '提示', { type: 'warning' })
    fields.value = []
    await loadTemplate()
    ElMessage.success('已清空')
  } catch {
    // 取消
  }
}

// 保存字段配置
const saveFields = async () => {
  if (fields.value.length === 0) {
    ElMessage.warning('请先添加字段')
    return
  }

  saving.value = true
  try {
    // 保存字段配置
    const response = await fetch(`/api/templates/${templateId}/html-fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fields: fields.value.map((f, idx) => ({
          field_name: f.id,
          field_label: f.name,
          field_type: 'text',
          position_type: 'coordinate',
          position_data: { cellIndex: idx },
          sort_order: idx
        }))
      })
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功！')
      // 生成可填写HTML
      await generateFormHtml()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 生成可填写HTML
const generateFormHtml = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId}/generate-form`, {
      method: 'POST'
    })
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('已生成可填写表单')
    }
  } catch (error) {
    console.error('生成表单失败:', error)
  }
}

// 返回
const goBack = () => {
  router.push('/report/template-mgt')
}

onMounted(() => {
  loadTemplate()
})
</script>

<style scoped>
.html-template-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.panel-header h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.html-container {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: #f5f7fa;
}

.html-content {
  background: #fff;
  padding: 20px;
  min-height: 100%;
}

.html-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
}

.html-content :deep(td),
.html-content :deep(th) {
  border: 1px solid #dcdfe6;
  padding: 8px;
  min-width: 50px;
  min-height: 30px;
}

.html-content :deep(.html-form-input) {
  width: 95%;
  height: 90%;
  border: 1px solid #409eff;
  padding: 2px 5px;
  font-size: inherit;
  background: #fff;
}

.fields-panel {
  width: 350px;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.fields-list {
  flex: 1;
  padding: 16px;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.field-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.field-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
}
</style>
