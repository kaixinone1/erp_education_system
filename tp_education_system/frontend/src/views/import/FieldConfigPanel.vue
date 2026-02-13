<template>
  <div class="field-config-panel">
    <h3>第二步：字段配置</h3>
    <el-divider></el-divider>
    
    <div v-if="!fileColumns.length" class="empty-state">
      <el-empty description="请先上传文件以获取字段列表" />
    </div>
    
    <div v-else>
      <!-- 字段映射表格 -->
      <el-table :data="fieldMappings" style="width: 100%" border>
        <el-table-column prop="sourceField" label="源文件字段" width="200">
          <template #default="scope">
            <el-select v-model="scope.row.sourceField" placeholder="请选择源字段" style="width: 100%;">
              <el-option
                v-for="column in fileColumns"
                :key="column"
                :label="column"
                :value="column"
              ></el-option>
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column prop="targetField" label="目标表字段" width="200">
          <template #default="scope">
            <el-select v-model="scope.row.targetField" placeholder="请选择目标字段" style="width: 100%;">
              <el-option
                v-for="field in targetFields"
                :key="field.value"
                :label="field.label"
                :value="field.value"
              ></el-option>
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column prop="dataType" label="数据类型" width="120">
          <template #default="scope">
            <el-select v-model="scope.row.dataType" placeholder="数据类型" style="width: 100%;">
              <el-option label="字符串" value="string"></el-option>
              <el-option label="数字" value="number"></el-option>
              <el-option label="日期" value="date"></el-option>
              <el-option label="布尔值" value="boolean"></el-option>
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column prop="required" label="是否必填" width="100">
          <template #default="scope">
            <el-switch v-model="scope.row.required" />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button
              type="danger"
              size="small"
              @click="removeMapping(scope.$index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 添加映射按钮 -->
      <div class="add-mapping">
        <el-button type="primary" @click="addMapping">
          <el-icon><Plus /></el-icon>
          添加字段映射
        </el-button>
      </div>
      
      <!-- 自动映射按钮 -->
      <div class="auto-map">
        <el-button @click="autoMapFields">
          <el-icon><Refresh /></el-icon>
          自动匹配字段
        </el-button>
      </div>
      
      <!-- 预览数据 -->
      <div v-if="sampleData.length" class="sample-data">
        <h4>文件数据预览（前5行）</h4>
        <el-table :data="sampleData" style="width: 100%" border size="small">
          <el-table-column
            v-for="column in fileColumns"
            :key="column"
            :prop="column"
            :label="column"
            :width="120"
          ></el-table-column>
        </el-table>
      </div>
    </div>
    
    <div class="panel-tip">
      <el-alert
        title="操作提示"
        type="info"
        :closable="false"
        show-icon
      >
        <ul>
          <li>请为每个需要导入的字段创建映射关系</li>
          <li>确保源字段与目标字段的数据类型匹配</li>
          <li>标记必填字段，系统会进行数据校验</li>
          <li>使用自动匹配功能可以快速建立字段映射</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'

// 文件列���
const fileColumns = ref<string[]>([])

// 目标表字段
const targetFields = ref([
  { label: 'ID', value: 'id' },
  { label: '姓名', value: 'name' },
  { label: '性别', value: 'gender' },
  { label: '年龄', value: 'age' },
  { label: '工号', value: 'employee_id' },
  { label: '部门', value: 'department' },
  { label: '职位', value: 'position' },
  { label: '联系电话', value: 'phone' },
  { label: '邮箱', value: 'email' },
  { label: '入职日期', value: 'hire_date' },
  { label: '状态', value: 'status' }
])

// 字段映射
const fieldMappings = ref([
  {
    sourceField: '',
    targetField: '',
    dataType: 'string',
    required: false
  }
])

// 样本数据
const sampleData = ref<any[]>([])

// 添加映射
const addMapping = () => {
  fieldMappings.value.push({
    sourceField: '',
    targetField: '',
    dataType: 'string',
    required: false
  })
}

// 删除映射
const removeMapping = (index: number) => {
  fieldMappings.value.splice(index, 1)
}

// 自动匹配字段
const autoMapFields = () => {
  // 简单的自动匹配逻辑：基于字段名相似度
  const fieldMap: Record<string, string> = {
    '姓名': 'name',
    '性别': 'gender',
    '年龄': 'age',
    '工号': 'employee_id',
    '部门': 'department',
    '职位': 'position',
    '联系电话': 'phone',
    '电话': 'phone',
    '邮箱': 'email',
    '入职日期': 'hire_date',
    '状态': 'status'
  }
  
  // 清空现有映射
  fieldMappings.value = []
  
  // 为每个文件字段创建映射
  fileColumns.value.forEach(column => {
    let targetField = ''
    
    // 尝试精确匹配
    if (fieldMap[column]) {
      targetField = fieldMap[column]
    } else {
      // 尝试模糊匹配
      for (const [key, value] of Object.entries(fieldMap)) {
        if (column.includes(key)) {
          targetField = value
          break
        }
      }
    }
    
    fieldMappings.value.push({
      sourceField: column,
      targetField: targetField,
      dataType: 'string',
      required: true
    })
  })
}

// 初始化
onMounted(() => {
  // 模拟文件列��（实际项目中应从后端获取）
  fileColumns.value = ['姓名', '性别', '年龄', '工号', '部门', '职位', '联系电话', '邮箱', '入职日期', '状态']
  
  // 模拟样本数据
  sampleData.value = [
    {
      '姓名': '张三',
      '性别': '男',
      '年龄': 30,
      '工号': 'T001',
      '部门': '第一中学',
      '职位': '教师',
      '联系电话': '13800138001',
      '邮箱': 'zhangsan@example.com',
      '入职日期': '2020-01-01',
      '状态': '在职'
    },
    {
      '姓名': '李四',
      '性别': '女',
      '年龄': 25,
      '工号': 'T002',
      '部门': '第二中学',
      '职位': '教师',
      '联系电话': '13800138002',
      '邮箱': 'lisi@example.com',
      '入职日期': '2021-01-01',
      '状态': '在职'
    }
  ]
  
  // 自动生成映射
  autoMapFields()
})

// 导出数据供父组件使用
defineExpose({
  fieldMappings,
  fileColumns,
  sampleData,
  addMapping,
  removeMapping,
  autoMapFields
})
</script>

<style scoped>
.field-config-panel {
  padding: 20px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.add-mapping {
  margin-top: 20px;
  margin-bottom: 20px;
}

.auto-map {
  margin-bottom: 30px;
}

.sample-data {
  margin-top: 30px;
}

.sample-data h4 {
  margin-bottom: 10px;
}

.panel-tip {
  margin-top: 30px;
}
</style>
