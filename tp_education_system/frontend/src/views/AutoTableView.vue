<template>
  <div class="auto-table-view">
    <AutoTableManager :table-name="tableName" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AutoTableManager from '@/components/AutoTableManager.vue'

const route = useRoute()

const tableName = computed(() => {
  return route.params.tableName as string
})
</script>

<style scoped>
.auto-table-view {
  height: 100%;
}
</style>
