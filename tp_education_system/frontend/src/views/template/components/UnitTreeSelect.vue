<template>
  <div class="unit-tree-select">
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索单位名称..."
        clearable
        prefix-icon="Search"
        style="width: 300px;"
      />
      <div class="action-buttons">
        <el-button size="small" @click="handleSelectAll">全选</el-button>
        <el-button size="small" @click="handleSelectInverse">反选</el-button>
        <el-button size="small" type="danger" @click="handleClearAll">清空</el-button>
      </div>
    </div>

    <el-tree
      ref="treeRef"
      :data="filteredTreeData"
      :props="treeProps"
      show-checkbox
      check-strictly
      :default-expand-all="false"
      :expand-on-click-node="false"
      node-key="id"
      :filter-node-method="filterNode"
      @check="handleCheck"
      style="max-height: 400px; overflow-y: auto; margin-top: 10px;"
    >
      <template #default="{ node, data }">
        <span class="custom-tree-node">
          <span>{{ data.unit_name }}</span>
          <el-tag size="small" style="margin-left: 8px;">
            {{ getLevelLabel(data.unit_level) }}
          </el-tag>
        </span>
      </template>
    </el-tree>
    
    <div v-if="selectedUnits.length > 0" class="selected-info">
      <div class="selected-header">
        <span>已选择 <strong>{{ selectedUnits.length }}</strong> 个单位：</span>
        <el-button type="text" size="small" @click="handleClearAll">清空</el-button>
      </div>
      <div class="selected-tags">
        <el-tag
          v-for="unit in selectedUnits"
          :key="unit.id"
          closable
          @close="removeUnit(unit.id)"
          style="margin: 2px;"
        >
          {{ unit.full_path }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const treeRef = ref(null)
const unitTree = ref([])
const selectedUnits = ref([])
const searchKeyword = ref('')

const treeProps = {
  children: 'children',
  label: 'unit_name'
}

const treeData = computed(() => {
  return buildTree(unitTree.value)
})

const filteredTreeData = computed(() => {
  return treeData.value
})

function buildTree(units) {
  const unitMap = {}
  const roots = []

  units.forEach(unit => {
    unitMap[unit.id] = {
      id: unit.id,
      unit_name: unit.unit_name,
      unit_level: unit.unit_level,
      parent_id: unit.parent_id,
      school_dict_id: unit.school_dict_id,
      full_path: unit.full_path,
      children: []
    }
  })

  units.forEach(unit => {
    if (unit.parent_id === null) {
      roots.push(unitMap[unit.id])
    } else if (unitMap[unit.parent_id]) {
      unitMap[unit.parent_id].children.push(unitMap[unit.id])
    }
  })

  return roots
}

function getLevelLabel(level) {
  const labels = {
    'province': '省',
    'city': '地级市',
    'county': '县',
    'town': '镇',
    'school': '校'
  }
  return labels[level] || level
}

async function loadUnitTree() {
  try {
    const response = await axios.get('/api/unit/tree')
    if (response.data.success) {
      unitTree.value = response.data.units
    }
  } catch (error) {
    ElMessage.error('加载单位树失败：' + error.message)
  }
}

function filterNode(value, data) {
  if (!value) return true
  return data.unit_name.includes(value) || data.full_path.includes(value)
}

function handleCheck(data, { checkedKeys }) {
  const units = checkedKeys.map(id => findUnitById(id, unitTree.value)).filter(u => u)
  selectedUnits.value = units
  
  emit('update:modelValue', checkedKeys)
  emit('change', {
    ids: checkedKeys,
    units: units
  })
}

function handleSelectAll() {
  if (!treeRef.value) return
  
  const allIds = unitTree.value.map(u => u.id)
  treeRef.value.setCheckedKeys(allIds)
  
  selectedUnits.value = unitTree.value.map(u => ({
    id: u.id,
    unit_name: u.unit_name,
    unit_level: u.unit_level,
    full_path: u.full_path
  }))
  
  emit('update:modelValue', allIds)
  emit('change', {
    ids: allIds,
    units: selectedUnits.value
  })
  
  ElMessage.success(`已全选 ${allIds.length} 个单位`)
}

function handleSelectInverse() {
  if (!treeRef.value) return
  
  const checkedKeys = treeRef.value.getCheckedKeys()
  const allIds = unitTree.value.map(u => u.id)
  const invertedIds = allIds.filter(id => !checkedKeys.includes(id))
  
  treeRef.value.setCheckedKeys(invertedIds)
  
  const units = invertedIds.map(id => findUnitById(id, unitTree.value)).filter(u => u)
  selectedUnits.value = units
  
  emit('update:modelValue', invertedIds)
  emit('change', {
    ids: invertedIds,
    units: units
  })
  
  ElMessage.success(`已反选，当前选中 ${invertedIds.length} 个单位`)
}

function handleClearAll() {
  if (treeRef.value) {
    treeRef.value.setCheckedKeys([])
  }
  selectedUnits.value = []
  emit('update:modelValue', [])
  emit('change', {
    ids: [],
    units: []
  })
}

function removeUnit(unitId) {
  if (treeRef.value) {
    treeRef.value.setChecked(unitId, false)
  }
}

function findUnitById(id, units) {
  for (const unit of units) {
    if (unit.id === id) {
      return unit
    }
    if (unit.children && unit.children.length > 0) {
      const found = findUnitById(id, unit.children)
      if (found) return found
    }
  }
  return null
}

watch(searchKeyword, (val) => {
  if (treeRef.value) {
    treeRef.value.filter(val)
  }
})

watch(() => props.modelValue, (newVal) => {
  if (Array.isArray(newVal) && treeRef.value) {
    treeRef.value.setCheckedKeys(newVal)
    selectedUnits.value = newVal.map(id => findUnitById(id, unitTree.value)).filter(u => u)
  }
}, { immediate: true })

onMounted(() => {
  loadUnitTree()
})
</script>

<style scoped>
.unit-tree-select {
  width: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  font-size: 14px;
  padding-right: 8px;
}

.selected-info {
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.selected-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 500;
}

.selected-tags {
  max-height: 200px;
  overflow-y: auto;
}
</style>

