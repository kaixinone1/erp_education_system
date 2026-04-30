<template>
  <div class="intermediate-table-view">
    <IntermediateTableManager :table-name="tableName" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import IntermediateTableManager from '@/components/IntermediateTableManager.vue'

const route = useRoute()

const tableName = computed(() => {
  return route.params.tableName as string
})
</script>

<style scoped>
.intermediate-table-view {
  height: 100%;
}
</style>
