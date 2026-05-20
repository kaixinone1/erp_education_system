<template>
  <div class="school-multi-select">
    <el-cascader
      v-model="selectedSchools"
      :options="schoolOptions"
      :props="cascaderProps"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :filterable="filterable"
      :collapse-tags="collapseTags"
      :collapse-tags-tooltip="collapseTagsTooltip"
      @change="handleChange"
      style="width: 100%"
    />
    
    <div v-if="selectedSchoolsInfo.length > 0" class="selected-info">
      <el-tag
        v-for="school in selectedSchoolsInfo"
        :key="school.id"
        closable
        @close="removeSchool(school.id)"
        style="margin: 2px;"
      >
        {{ school.unit_name }}
      </el-tag>
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
  },
  placeholder: {
    type: String,
    default: '请选择学校（可多选）'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: true
  },
  filterable: {
    type: Boolean,
    default: true
  },
  collapseTags: {
    type: Boolean,
    default: true
  },
  collapseTagsTooltip: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedSchools = ref([])
const unitTree = ref([])
const selectedSchoolsInfo = ref([])

const cascaderProps = {
  value: 'id',
  label: 'unit_name',
  children: 'children',
  multiple: true,
  checkStrictly: true,
  emitPath: false
}

const schoolOptions = computed(() => {
  return buildTree(unitTree.value)
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

function handleChange(value) {
  const schools = Array.isArray(value) ? value : [value]
  selectedSchoolsInfo.value = schools.map(id => findUnitById(id, unitTree.value)).filter(u => u)
  
  emit('update:modelValue', schools)
  emit('change', {
    ids: schools,
    schools: selectedSchoolsInfo.value
  })
}

function removeSchool(schoolId) {
  selectedSchools.value = selectedSchools.value.filter(id => id !== schoolId)
  handleChange(selectedSchools.value)
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

watch(() => props.modelValue, (newVal) => {
  if (Array.isArray(newVal)) {
    selectedSchools.value = newVal
    selectedSchoolsInfo.value = newVal.map(id => findUnitById(id, unitTree.value)).filter(u => u)
  } else {
    selectedSchools.value = []
    selectedSchoolsInfo.value = []
  }
}, { immediate: true })

onMounted(() => {
  loadUnitTree()
})
</script>

<style scoped>
.school-multi-select {
  width: 100%;
}

.selected-info {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}
</style>

