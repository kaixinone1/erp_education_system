<template>
  <div class="unit-cascader">
    <el-cascader
      v-model="selectedUnit"
      :options="unitOptions"
      :props="cascaderProps"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :filterable="filterable"
      @change="handleChange"
      style="width: 100%"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: null
  },
  placeholder: {
    type: String,
    default: '请选择单位'
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
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedUnit = ref([])
const unitTree = ref([])

const cascaderProps = {
  value: 'id',
  label: 'unit_name',
  children: 'children',
  checkStrictly: true,
  emitPath: false
}

const unitOptions = computed(() => {
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
  emit('update:modelValue', value)
  
  const selectedUnitInfo = findUnitById(value, unitTree.value)
  emit('change', {
    id: value,
    unit: selectedUnitInfo
  })
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
  if (newVal) {
    selectedUnit.value = [newVal]
  } else {
    selectedUnit.value = []
  }
}, { immediate: true })

onMounted(() => {
  loadUnitTree()
})
</script>

<style scoped>
.unit-cascader {
  width: 100%;
}
</style>

