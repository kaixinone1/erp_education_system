<template>
  <div class="retirement-report-form">
    <el-dialog
      v-model="visible"
      title="职工退休呈报表 - A3横向对折册子"
      width="1400px"
      :close-on-click-modal="false"
      class="report-dialog"
      destroy-on-close
    >
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="30" animated />
      </div>

      <div v-else class="report-content">
        <!-- 页面切换 -->
        <div class="page-tabs">
          <el-radio-group v-model="currentPage" size="large">
            <el-radio-button label="page1">图一（封面+审批意见）</el-radio-button>
            <el-radio-button label="page2">图二（基本信息+工资信息）</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 图一：封面 + 审批意见 -->
        <div v-if="currentPage === 'page1'" class="a3-page">
          <div class="a3-container">
            <!-- 左栏：审批意见 -->
            <div class="left-column">
              <table class="approval-table">
                <tr>
                  <td class="approval-label" rowspan="2">
                    呈<br>报<br>单<br>位<br>意<br>见
                  </td>
                  <td class="approval-content">
                    <p>经研究，同意 <el-input v-model="formData.teacher_name" size="small" class="inline-input" /> 同志按以下第（<el-input v-model="formData.retirement_option" size="small" class="inline-input-short" />）条办理退休，从 <el-input v-model="formData.retirement_year" size="small" class="inline-input-short" /> 年 <el-input v-model="formData.retirement_month" size="small" class="inline-input-short" /> 月执行。</p>
                    <p>（一）弹性提前退休</p>
                    <p>（二）法定退休年龄退休</p>
                    <div class="date-line">
                      <el-input v-model="formData.approval_year" size="small" class="date-input" /> 年
                      <el-input v-model="formData.approval_month" size="small" class="date-input" /> 月
                      <el-input v-model="formData.approval_day" size="small" class="date-input" /> 日
                    </div>
                  </td>
                </tr>
              </table>

              <table class="approval-table">
                <tr>
                  <td class="approval-label" rowspan="2">
                    主 管 部<br>门 审 查<br>意 见
                  </td>
                  <td class="approval-content">
                    <p style="text-align: center; padding: 20px 0;">同意呈报</p>
                    <div class="date-line">
                      <el-input v-model="formData.dept_approval_year" size="small" class="date-input" /> 年
                      <el-input v-model="formData.dept_approval_month" size="small" class="date-input" /> 月
                      <el-input v-model="formData.dept_approval_day" size="small" class="date-input" /> 日
                    </div>
                  </td>
                </tr>
              </table>

              <table class="approval-table">
                <tr>
                  <td class="approval-label" rowspan="2">
                    退 休<br>一次性补贴<br>审批意见
                  </td>
                  <td class="approval-content">
                    <p>根据鄂人社发【2017】8号文件规定，同意 <el-input v-model="formData.teacher_name" size="small" class="inline-input" /> 同志发放一次性独生子女费 <el-input v-model="formData.only_child_fee" size="small" class="inline-input" /> 元，教育特殊贡献奖 <el-input v-model="formData.education_award" size="small" class="inline-input" /> 元，从 <el-input v-model="formData.subsidy_year" size="small" class="inline-input-short" /> 年 <el-input v-model="formData.subsidy_month" size="small" class="inline-input-short" /> 月执行。</p>
                    <div class="date-line">
                      <el-input v-model="formData.subsidy_approval_year" size="small" class="date-input" /> 年
                      <el-input v-model="formData.subsidy_approval_month" size="small" class="date-input" /> 月
                      <el-input v-model="formData.subsidy_approval_day" size="small" class="date-input" /> 日
                    </div>
                  </td>
                </tr>
              </table>

              <table class="approval-table">
                <tr>
                  <td class="approval-label" rowspan="2">
                    批 准 机<br>关 审 批<br>意 见
                  </td>
                  <td class="approval-content">
                    <p>根据人社部发【2024】94号文件规定，同意 <el-input v-model="formData.teacher_name" size="small" class="inline-input" /> 同志按第（<el-input v-model="formData.final_option" size="small" class="inline-input-short" />）条退休，从 <el-input v-model="formData.final_year" size="small" class="inline-input-short" /> 年 <el-input v-model="formData.final_month" size="small" class="inline-input-short" /> 月执行。</p>
                    <div class="date-line">
                      <el-input v-model="formData.final_approval_year" size="small" class="date-input" /> 年
                      <el-input v-model="formData.final_approval_month" size="small" class="date-input" /> 月
                      <el-input v-model="formData.final_approval_day" size="small" class="date-input" /> 日
                    </div>
                  </td>
                </tr>
              </table>

              <div class="footer-text">枣阳市人力资源和社会保障局制</div>
            </div>

            <!-- 右栏：封面 -->
            <div class="right-column cover-page">
              <div class="cover-content">
                <div class="cover-number">编号：<el-input v-model="formData.report_number" size="small" class="number-input" /></div>
                <div class="cover-title">职 工 退 休 呈 报 表</div>
                <div class="cover-info">
                  <div class="info-row">
                    <span class="info-label">单位：</span>
                    <el-input v-model="formData.work_unit" size="large" class="info-input" />
                  </div>
                  <div class="info-row">
                    <span class="info-label">姓名：</span>
                    <el-input v-model="formData.teacher_name" size="large" class="info-input-short" />
                  </div>
                </div>
                <div class="cover-date">
                  <el-input v-model="formData.cover_year" size="large" class="date-input-large" /> 年
                  <el-input v-model="formData.cover_month" size="large" class="date-input-large" /> 月
                  <el-input v-model="formData.cover_day" size="large" class="date-input-large" /> 日
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 图二：基本信息 + 工资信息 -->
        <div v-if="currentPage === 'page2'" class="a3-page">
          <div class="a3-container">
            <!-- 左栏：基本信息 -->
            <div class="left-column">
              <div class="page-title">退 休 呈 报 表</div>

              <table class="info-table">
                <!-- 第1行：姓名、性别、出生年月 -->
                <tr>
                  <td class="label">姓 名</td>
                  <td class="value"><el-input v-model="formData.teacher_name" size="small" /></td>
                  <td class="label">性 别</td>
                  <td class="value"><el-input v-model="formData.gender" size="small" /></td>
                  <td class="label">出生年月</td>
                  <td class="value"><el-input v-model="formData.birth_date" size="small" /></td>
                </tr>

                <!-- 第2行：民族、文化程度、是否独生子女 -->
                <tr>
                  <td class="label">民 族</td>
                  <td class="value"><el-input v-model="formData.ethnicity" size="small" /></td>
                  <td class="label">文化程度</td>
                  <td class="value"><el-input v-model="formData.education" size="small" /></td>
                  <td class="label">是否独生子女</td>
                  <td class="value"><el-input v-model="formData.is_only_child" size="small" /></td>
                </tr>

                <!-- 第3行：入党年月、职务、技术职称 -->
                <tr>
                  <td class="label">入党年月</td>
                  <td class="value"><el-input v-model="formData.join_party_date" size="small" /></td>
                  <td class="label">职 务</td>
                  <td class="value"><el-input v-model="formData.position" size="small" /></td>
                  <td class="label">技术职称</td>
                  <td class="value"><el-input v-model="formData.title" size="small" /></td>
                </tr>

                <!-- 第4行：参加工作时间、工作年限 -->
                <tr>
                  <td class="label" colspan="2">参 加 工 作 时 间</td>
                  <td class="value" colspan="2"><el-input v-model="formData.work_start_date" size="small" /></td>
                  <td class="label">工 作 年 限</td>
                  <td class="value"><el-input v-model="formData.work_years" size="small" /></td>
                </tr>

                <!-- 第5行：籍贯、现在住址 -->
                <tr>
                  <td class="label">籍 贯</td>
                  <td class="value" colspan="2"><el-input v-model="formData.native_place" size="small" /></td>
                  <td class="label">现在住址</td>
                  <td class="value" colspan="2"><el-input v-model="formData.current_address" size="small" /></td>
                </tr>

                <!-- 第6行：工作简历标题 -->
                <tr>
                  <td class="label" colspan="6" style="text-align: center; font-weight: bold;">工 作 简 历</td>
                </tr>

                <!-- 第7行：工作简历表头 -->
                <tr>
                  <td class="label" colspan="2">自何年何月</td>
                  <td class="label" colspan="2">至何年何月</td>
                  <td class="label">在何单位任何职</td>
                  <td class="label">证明人及其住址</td>
                </tr>

                <!-- 第8-12行：工作简历内容 -->
                <tr v-for="(item, index) in formData.work_experience" :key="index">
                  <td class="value" colspan="2"><el-input v-model="item.start_date" size="small" /></td>
                  <td class="value" colspan="2"><el-input v-model="item.end_date" size="small" /></td>
                  <td class="value"><el-input v-model="item.unit_position" size="small" /></td>
                  <td class="value"><el-input v-model="item.witness" size="small" /></td>
                </tr>

                <!-- 第13行：退休原因 -->
                <tr>
                  <td class="label">退休原因</td>
                  <td class="value" colspan="5"><el-input v-model="formData.retirement_reason" type="textarea" :rows="2" /></td>
                </tr>

                <!-- 第14行：供养直系亲属 -->
                <tr>
                  <td class="label" colspan="2" style="line-height: 1.4;">
                    供养直系亲属、<br>
                    姓名、出生年月、<br>
                    与退休人员的关系
                  </td>
                  <td class="value" colspan="4"><el-input v-model="formData.family_members" type="textarea" :rows="3" /></td>
                </tr>

                <!-- 第15行：退休后居住地址和发给退休费的单位 -->
                <tr>
                  <td class="label">退休后<br>居住地址</td>
                  <td class="value" colspan="2"><el-input v-model="formData.retirement_address" size="small" /></td>
                  <td class="label">发给退休<br>费的单位</td>
                  <td class="value" colspan="2"><el-input v-model="formData.pension_unit" size="small" /></td>
                </tr>
              </table>
            </div>

            <!-- 右栏：工资信息 -->
            <div class="right-column">
              <table class="salary-table">
                <!-- 2014年9月30日 -->
                <tr>
                  <td class="label" rowspan="4" style="text-align: center; line-height: 1.4;">
                    <div>2014 年 9 月</div>
                    <div>30 日</div>
                  </td>
                  <td class="label">机关工人</td>
                  <td class="label">技术等级</td>
                  <td class="value"><el-input v-model="formData.salary_2014_worker_level" size="small" /></td>
                  <td class="label">级别薪级</td>
                  <td class="value"><el-input v-model="formData.salary_2014_worker_grade" size="small" /></td>
                  <td class="label">级</td>
                </tr>
                <tr>
                  <td class="label">事业管理</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.salary_2014_mgmt_level" size="small" /></td>
                  <td class="label">对应原职务</td>
                  <td class="value"><el-input v-model="formData.salary_2014_mgmt_position" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
                <tr>
                  <td class="label">事业专技</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.salary_2014_tech_level" size="small" /></td>
                  <td class="label">对应原职务</td>
                  <td class="value"><el-input v-model="formData.salary_2014_tech_position" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
                <tr>
                  <td class="label">事业工勤</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.salary_2014_service_level" size="small" /></td>
                  <td class="label">对应技术等级</td>
                  <td class="value"><el-input v-model="formData.salary_2014_service_tech" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>

                <!-- 最后一次职务升降时间 -->
                <tr>
                  <td class="label" rowspan="4" style="text-align: center; line-height: 1.4;">
                    <div style="display: flex; flex-direction: column; align-items: center;">
                      <span>最后一次职务</span>
                      <span>（技术职称）</span>
                      <span>升降时间</span>
                      <span style="font-size: 10px; margin-top: 4px;">«最后一次职务升降时间»</span>
                    </div>
                  </td>
                  <td class="label">机关工人</td>
                  <td class="label">技术等级</td>
                  <td class="value"><el-input v-model="formData.last_promotion_worker_level" size="small" /></td>
                  <td class="label">级别薪级</td>
                  <td class="value"><el-input v-model="formData.last_promotion_worker_grade" size="small" /></td>
                  <td class="label">级</td>
                </tr>
                <tr>
                  <td class="label">事业管理</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.last_promotion_mgmt_level" size="small" /></td>
                  <td class="label">对应原职务</td>
                  <td class="value"><el-input v-model="formData.last_promotion_mgmt_position" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
                <tr>
                  <td class="label">事业专技</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.last_promotion_tech_level" size="small" /></td>
                  <td class="label">对应原职务</td>
                  <td class="value"><el-input v-model="formData.last_promotion_tech_position" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
                <tr>
                  <td class="label">事业工勤</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.last_promotion_service_level" size="small" /></td>
                  <td class="label">对应技术等级</td>
                  <td class="value"><el-input v-model="formData.last_promotion_service_tech" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>

                <!-- 退休时 -->
                <tr>
                  <td class="label" rowspan="4" style="writing-mode: vertical-rl; text-align: center;">退休时</td>
                  <td class="label">机关工人</td>
                  <td class="label">技术等级</td>
                  <td class="value"><el-input v-model="formData.retirement_worker_level" size="small" /></td>
                  <td class="label">级别薪级</td>
                  <td class="value"><el-input v-model="formData.retirement_worker_grade" size="small" /></td>
                  <td class="label">级</td>
                </tr>
                <tr>
                  <td class="label">事业管理</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.retirement_mgmt_level" size="small" /></td>
                  <td class="label">对应原职务</td>
                  <td class="value"><el-input v-model="formData.retirement_mgmt_position" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
                <tr>
                  <td class="label">事业专技</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.retirement_tech_level" size="small" /></td>
                  <td class="label">对应原职务</td>
                  <td class="value"><el-input v-model="formData.retirement_tech_position" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
                <tr>
                  <td class="label">事业工勤</td>
                  <td class="label">岗位</td>
                  <td class="value"><el-input v-model="formData.retirement_service_level" size="small" /></td>
                  <td class="label">对应技术等级</td>
                  <td class="value"><el-input v-model="formData.retirement_service_tech" size="small" /></td>
                  <td class="label">薪级</td>
                </tr>
              </table>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  teacherId: number
}>()

const emit = defineEmits(['save', 'close'])

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const currentPage = ref('page1')

// 表单数据
const formData = reactive({
  // 封面信息
  report_number: '',
  work_unit: '枣阳市太平镇中心学校',
  teacher_name: '',
  cover_year: '',
  cover_month: '',
  cover_day: '',

  // 基本信息
  gender: '',
  birth_date: '',
  ethnicity: '',
  education: '',
  is_only_child: '',
  join_party_date: '',
  position: '',
  title: '',
  work_start_date: '',
  work_years: '',
  native_place: '',
  current_address: '',
  retirement_reason: '',
  family_members: '',
  retirement_address: '',
  pension_unit: '枣阳市人力资源和社会保障局',

  // 工作简历（5行）
  work_experience: [
    { start_date: '', end_date: '', unit_position: '', witness: '' },
    { start_date: '', end_date: '', unit_position: '', witness: '' },
    { start_date: '', end_date: '', unit_position: '', witness: '' },
    { start_date: '', end_date: '', unit_position: '', witness: '' },
    { start_date: '', end_date: '', unit_position: '', witness: '' }
  ],

  // 2014年9月30日工资信息
  salary_2014_worker_level: '',
  salary_2014_worker_grade: '',
  salary_2014_mgmt_level: '',
  salary_2014_mgmt_position: '',
  salary_2014_tech_level: '',
  salary_2014_tech_position: '',
  salary_2014_service_level: '',
  salary_2014_service_tech: '',

  // 最后一次职务升降时间
  last_promotion_worker_level: '',
  last_promotion_worker_grade: '',
  last_promotion_mgmt_level: '',
  last_promotion_mgmt_position: '',
  last_promotion_tech_level: '',
  last_promotion_tech_position: '',
  last_promotion_service_level: '',
  last_promotion_service_tech: '',

  // 退休时工资信息
  retirement_worker_level: '',
  retirement_worker_grade: '',
  retirement_mgmt_level: '',
  retirement_mgmt_position: '',
  retirement_tech_level: '',
  retirement_tech_position: '',
  retirement_service_level: '',
  retirement_service_tech: '',

  // 审批意见
  retirement_option: '',
  retirement_year: '',
  retirement_month: '',
  approval_year: '',
  approval_month: '',
  approval_day: '',
  dept_approval_year: '',
  dept_approval_month: '',
  dept_approval_day: '',
  only_child_fee: '',
  education_award: '',
  subsidy_year: '',
  subsidy_month: '',
  subsidy_approval_year: '',
  subsidy_approval_month: '',
  subsidy_approval_day: '',
  final_option: '',
  final_year: '',
  final_month: '',
  final_approval_year: '',
  final_approval_month: '',
  final_approval_day: ''
})

// 打开表单
const open = async () => {
  // 检查teacherId是否有效
  if (!props.teacherId || props.teacherId === 0) {
    ElMessage.error('教师ID无效，请重新选择教师')
    return
  }

  visible.value = true
  loading.value = true

  try {
    // 获取教师数据
    const response = await fetch(`/api/report-designer/teacher-full-data?teacher_id=${props.teacherId}`)

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('教师不存在')
      }
      throw new Error('获取数据失败')
    }

    const result = await response.json()

    if (result.status === 'success') {
      const data = result.data

      // 填充基本信息
      formData.teacher_name = data.teacher_name || ''
      formData.gender = data.gender || ''
      formData.birth_date = data.birth_date || ''
      formData.ethnicity = data.ethnicity || ''
      formData.education = data.education || ''
      formData.position = data.position || ''
      formData.title = data.title || ''
      formData.work_start_date = data.work_start_date || ''
      formData.work_years = data.work_years || ''
      formData.native_place = data.native_place || ''
      formData.work_unit = data.work_unit || '枣阳市太平镇中心学校'
      formData.contact_phone = data.contact_phone || ''
      formData.id_card = data.id_card || ''
      formData.age = data.age || ''
      formData.retirement_date = data.retirement_date || ''

      // 填充新增字段
      formData.is_only_child = data.is_only_child || ''
      formData.join_party_date = data.join_party_date || ''
      formData.current_address = data.current_address || ''
      formData.retirement_reason = data.retirement_reason || ''
      formData.family_members = data.family_members || ''
      formData.retirement_address = data.retirement_address || ''
      formData.pension_unit = data.pension_unit || '枣阳市人力资源和社会保障局'

      // 填充工作简历
      if (data.work_experience && Array.isArray(data.work_experience) && data.work_experience.length > 0) {
        formData.work_experience = data.work_experience
      } else {
        // 初始化5条空记录
        formData.work_experience = [
          { start_date: '', end_date: '', unit_position: '', witness: '' },
          { start_date: '', end_date: '', unit_position: '', witness: '' },
          { start_date: '', end_date: '', unit_position: '', witness: '' },
          { start_date: '', end_date: '', unit_position: '', witness: '' },
          { start_date: '', end_date: '', unit_position: '', witness: '' }
        ]
      }

      // 设置默认日期
      const now = new Date()
      const year = now.getFullYear().toString()
      const month = (now.getMonth() + 1).toString()
      const day = now.getDate().toString()

      formData.cover_year = year
      formData.cover_month = month
      formData.cover_day = day
      formData.approval_year = year
      formData.approval_month = month
      formData.approval_day = day
      formData.dept_approval_year = year
      formData.dept_approval_month = month
      formData.dept_approval_day = day
      formData.subsidy_approval_year = year
      formData.subsidy_approval_month = month
      formData.subsidy_approval_day = day
      formData.final_approval_year = year
      formData.final_approval_month = month
      formData.final_approval_day = day
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

// 保存
const handleSave = async () => {
  saving.value = true

  try {
    const response = await fetch('/api/report-designer/save-full-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: props.teacherId,
        ...formData
      })
    })

    if (!response.ok) {
      throw new Error('保存失败')
    }

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('保存成功')
      emit('save', formData)
    } else {
      throw new Error(result.message || '保存失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 关闭
const close = () => {
  visible.value = false
  emit('close')
}

defineExpose({
  open,
  close
})
</script>

<style scoped>
.retirement-report-form {
  :deep(.report-dialog) {
    .el-dialog__body {
      max-height: 80vh;
      overflow-y: auto;
      padding: 20px;
    }
  }
}

.loading-container {
  padding: 40px;
}

.page-tabs {
  text-align: center;
  margin-bottom: 20px;
}

/* A3页面容器 */
.a3-page {
  background: #f0f0f0;
  padding: 20px;
  border-radius: 8px;
}

.a3-container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  min-height: 800px;
  height: 800px;
}

/* 左栏 */
.left-column {
  flex: 1;
  padding: 20px;
  border-right: 2px dashed #ccc;
  display: flex;
  flex-direction: column;
  height: 100%;

  .info-table {
    flex: 1;

    td {
      height: auto;
    }
  }
}

/* 右栏 */
.right-column {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;

  .salary-table {
    flex: 1;

    td {
      height: auto;
    }
  }
}

/* 封面样式 */
.cover-page {
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-content {
  text-align: center;
  width: 80%;
}

.cover-number {
  text-align: right;
  margin-bottom: 60px;
  font-size: 14px;
}

.number-input {
  width: 150px;
}

.cover-title {
  font-size: 32px;
  font-weight: bold;
  letter-spacing: 8px;
  margin: 80px 0;
}

.cover-info {
  margin: 60px 0;
  text-align: left;
  padding: 0 40px;
}

.info-row {
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.info-label {
  font-size: 18px;
  min-width: 60px;
}

.info-input {
  flex: 1;
  margin-left: 10px;
}

.info-input-short {
  width: 150px;
  margin-left: 10px;
}

.cover-date {
  margin: 40px 0;
  font-size: 18px;
}

.date-input-large {
  width: 80px;
  margin: 0 5px;
}

.cover-subtitle {
  font-size: 24px;
  letter-spacing: 4px;
  margin-top: 60px;
}

/* 页面标题 */
.page-title {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 4px;
  margin-bottom: 10px;
  height: 30px;
  line-height: 30px;
}

/* 审批意见表格 */
.approval-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
  font-size: 13px;

  td {
    border: 1px solid #333;
    padding: 10px;
    vertical-align: top;
  }

  .approval-label {
    width: 60px;
    background: #f5f5f5;
    text-align: center;
    font-weight: bold;
    line-height: 2;
  }

  .approval-content {
    line-height: 1.8;

    p {
      margin: 8px 0;
    }
  }
}

/* 基本信息表格 */
.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  table-layout: fixed;

  td {
    border: 1px solid #333;
    padding: 4px 3px;
    vertical-align: middle;
  }

  /* 让表格行均匀分布 */
  tr {
    height: calc(100% / 15);
  }

  .label {
    background: #f5f5f5;
    text-align: center;
    font-weight: normal;
    min-width: 50px;
  }

  .value {
    text-align: left;
  }
}

/* 工资信息表格 */
.salary-table {
  width: 100%;
  height: 100%;
  border-collapse: collapse;
  font-size: 11px;
  table-layout: fixed;

  td {
    border: 1px solid #333;
    padding: 5px 3px;
    vertical-align: middle;
    text-align: center;
  }

  /* 让表格行均匀分布 */
  tr {
    height: calc(100% / 12);
  }

  .label {
    background: #f5f5f5;
    font-weight: normal;
  }

  .value {
    text-align: left;
  }
}

/* 内联输入框 */
.inline-input {
  width: 80px;
  display: inline-block;
  margin: 0 3px;
}

.inline-input-short {
  width: 40px;
  display: inline-block;
  margin: 0 3px;
}

.date-input {
  width: 50px;
  display: inline-block;
  margin: 0 3px;
}

.date-line {
  text-align: right;
  margin-top: 15px;
}

.footer-text {
  text-align: center;
  font-size: 12px;
  margin-top: 20px;
  color: #666;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 打印样式 */
@media print {
  .retirement-report-form :deep(.el-dialog__header),
  .retirement-report-form :deep(.el-dialog__footer),
  .page-tabs {
    display: none !important;
  }

  .a3-page {
    background: white;
    padding: 0;
  }

  .a3-container {
    box-shadow: none;
  }
}
</style>
