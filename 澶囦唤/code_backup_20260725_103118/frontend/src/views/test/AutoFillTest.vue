<template>
  <div class="auto-fill-test">
    <el-card>
      <template #header>
        <h2>模板自动填报系统测试</h2>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="配置管理" name="configs">
          <el-button @click="loadConfigs" type="primary">加载配置</el-button>
          <el-table :data="configs" style="margin-top: 20px">
            <el-table-column prop="name" label="配置名称" />
            <el-table-column prop="template_name" label="模板名称" />
            <el-table-column prop="template_type" label="模板类型" />
            <el-table-column prop="description" label="描述" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="数据源" name="datasources">
          <el-button @click="loadDataSources" type="primary">加载数据源</el-button>
          <div style="margin-top: 20px">
            <p>总表数: {{ dataSourceCount }}</p>
            <p>类别: {{ categories.join(', ') }}</p>
          </div>
        </el-tab-pane>

        <el-tab-pane label="自动填报" name="autofill">
          <el-form :model="fillForm" label-width="120px">
            <el-form-item label="配置名称">
              <el-select v-model="fillForm.configName" placeholder="选择配置">
                <el-option
                  v-for="config in configs"
                  :key="config.name"
                  :label="config.template_name"
                  :value="config.name"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="筛选条件">
              <el-input v-model="fillForm.filters" placeholder='{"employment_status": "退休"}' />
            </el-form-item>
            <el-form-item>
              <el-button @click="executeFill" type="primary">执行填报</el-button>
              <el-button @click="previewFill">预览数据</el-button>
            </el-form-item>
          </el-form>
          <div v-if="fillResult" style="margin-top: 20px">
            <h3>填报结果</h3>
            <pre>{{ JSON.stringify(fillResult, null, 2) }}</pre>
          </div>
        </el-tab-pane>

        <el-tab-pane label="历史记录" name="history">
          <el-button @click="loadHistory" type="primary">加载历史</el-button>
          <el-table :data="history" style="margin-top: 20px">
            <el-table-column prop="config_name" label="配置名称" />
            <el-table-column prop="data_count" label="数据量" />
            <el-table-column prop="status" label="状态" />
            <el-table-column prop="created_at" label="生成时间" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="统计信息" name="statistics">
          <el-button @click="loadStatistics" type="primary">加载统计</el-button>
          <div v-if="statistics" style="margin-top: 20px">
            <p>总生成次数: {{ statistics.total_count }}</p>
            <p>成功次数: {{ statistics.success_count }}</p>
            <p>失败次数: {{ statistics.failed_count }}</p>
            <p>平均执行时间: {{ statistics.avg_execution_time }}秒</p>
            <p>总数据量: {{ statistics.total_data_count }}</p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = '/api/auto-fill'

const activeTab = ref('configs')
const configs = ref([])
const dataSourceCount = ref(0)
const categories = ref([])
const history = ref([])
const statistics = ref(null)
const fillResult = ref(null)

const fillForm = ref({
  configName: '',
  filters: '{"employment_status": "退休"}'
})

async function loadConfigs() {
  try {
    const response = await axios.get(`${API_BASE}/configs`)
    configs.value = response.data.configs
    ElMessage.success(`加载 ${response.data.count} 个配置`)
  } catch (error) {
    ElMessage.error('加载配置失败: ' + error.message)
  }
}

async function loadDataSources() {
  try {
    const response = await axios.get(`${API_BASE}/data-sources`)
    dataSourceCount.value = response.data.count
    categories.value = response.data.categories
    ElMessage.success(`加载 ${response.data.count} 个数据源表`)
  } catch (error) {
    ElMessage.error('加载数据源失败: ' + error.message)
  }
}

async function executeFill() {
  if (!fillForm.value.configName) {
    ElMessage.warning('请选择配置')
    return
  }

  try {
    const filters = JSON.parse(fillForm.value.filters)
    const response = await axios.post(`${API_BASE}/execute`, {
      config_name: fillForm.value.configName,
      filters: filters
    })
    fillResult.value = response.data
    ElMessage.success('填报完成')
  } catch (error) {
    ElMessage.error('填报失败: ' + error.message)
  }
}

async function previewFill() {
  if (!fillForm.value.configName) {
    ElMessage.warning('请选择配置')
    return
  }

  try {
    const filters = JSON.parse(fillForm.value.filters)
    const response = await axios.post(`${API_BASE}/preview-fill`, {
      config_name: fillForm.value.configName,
      filters: filters
    })
    fillResult.value = response.data
    ElMessage.success(`预览成功，共 ${response.data.count} 条数据`)
  } catch (error) {
    ElMessage.error('预览失败: ' + error.message)
  }
}

async function loadHistory() {
  try {
    const response = await axios.get(`${API_BASE}/history?limit=20`)
    history.value = response.data.history
    ElMessage.success(`加载 ${response.data.count} 条历史记录`)
  } catch (error) {
    ElMessage.error('加载历史失败: ' + error.message)
  }
}

async function loadStatistics() {
  try {
    const response = await axios.get(`${API_BASE}/statistics`)
    statistics.value = response.data.statistics
    ElMessage.success('加载统计成功')
  } catch (error) {
    ElMessage.error('加载统计失败: ' + error.message)
  }
}

loadConfigs()
loadDataSources()
</script>

<style scoped>
.auto-fill-test {
  padding: 20px;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
}
</style>

