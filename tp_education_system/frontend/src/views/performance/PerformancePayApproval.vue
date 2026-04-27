<template>
  <div class="performance-pay-approval-page">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>绩效工资审批管理</h2>
          <div class="header-actions">
            <el-button type="success" @click="showMonthDialog">
              <el-icon><Download /></el-icon>
              从数据库加载数据
            </el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
            <el-dropdown @command="handleExport" split-button type="warning" :loading="exporting">
              <el-icon><Document /></el-icon>
              导出
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
                  <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
                  <el-dropdown-item command="print">打印</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <div class="report-container">
        <div class="a4-page" id="printArea">
          <table class="salary-table" cellpadding="0" cellspacing="0">
            <col style="width:76pt"><col style="width:42pt"><col style="width:69pt"><col style="width:44pt"><col style="width:34pt"><col style="width:49pt"><col style="width:97pt"><col style="width:28pt"><col style="width:22pt"><col style="width:61pt"><col style="width:48pt">
            <tr style="height:30pt">
              <td colspan="11" style="border:none;text-align:center;font-size:14pt;font-weight:bold;">{{ currentYearMonth }}义务教育学校教职工绩效工资审批表</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:none;">填报单位：</td>
              <td colspan="3" style="border-right:none;border-bottom:.5pt solid #000;">
                <el-input v-model="reportData.填报单位" size="small" class="inline-input" />
              </td>
              <td colspan="2" style="border-right:none;border-bottom:.5pt solid #000;text-align:right;">填报时间:</td>
              <td style="border-bottom:.5pt solid #000;">{{ currentDate }}</td>
              <td colspan="2" style="border-right:none;border-bottom:.5pt solid #000;text-align:right;">单位：</td>
              <td style="border-bottom:.5pt solid #000;">人、元</td>
            </tr>
            <tr style="height:50pt">
              <td rowspan="2" style="border:.5pt solid #000;text-align:center;vertical-align:middle;font-weight:bold;">项&nbsp;目</td>
              <td colspan="3" style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;text-align:center;font-weight:bold;">基础性工资</td>
              <td rowspan="5" style="border-left:.5pt solid #000;border-top:.5pt solid #000;text-align:center;vertical-align:middle;writing-mode:vertical-rl;text-orientation:upright;letter-spacing:2px;font-weight:bold;">呈报单位意见</td>
              <td style="border-left:.5pt solid #000;border-top:.5pt solid #000;"></td>
              <td colspan="4" style="border-top:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:center;font-weight:bold;">人数</td>
              <td style="border:.5pt solid #000;text-align:center;font-weight:bold;">月工资标准</td>
              <td style="border:.5pt solid #000;text-align:center;font-weight:bold;">小计</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;text-align:left;padding-left:8px;">据实填写，同意呈报。</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:5px;font-weight:bold;">行政管理人员</td>
              <td style="border:.5pt solid #000;"></td>
              <td style="border:.5pt solid #000;"></td>
              <td style="border:.5pt solid #000;"></td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">1、副处级</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.副处级人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.副处级标准 || 0 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('副处级人数', '副处级标准', 0) }}</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;text-align:center;">（盖章）</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">2、正科级</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.正科级人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.正科级标准 || 0 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('正科级人数', '正科级标准', 0) }}</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;text-align:right;padding-right:10px;">{{ currentDate }}</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">3、副科级</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.副科级人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.副科级标准 || 0 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('副科级人数', '副科级标准', 0) }}</td>
              <td rowspan="5" style="border-left:.5pt solid #000;border-top:.5pt solid #000;border-right:.5pt solid #000;text-align:center;vertical-align:middle;writing-mode:vertical-rl;text-orientation:upright;letter-spacing:2px;font-weight:bold;">教育局意见</td>
              <td style="border-left:.5pt solid #000;border-top:.5pt solid #000;"></td>
              <td colspan="4" style="border-top:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">4、科员级</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.科员级人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.科员级标准 || 1185 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('科员级人数', '科员级标准', 1185) }}</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">5、办事员级</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.办事员级人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.办事员级标准 || 0 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('办事员级人数', '办事员级标准', 0) }}</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:5px;font-weight:bold;">专业技术人员</td>
              <td style="border:.5pt solid #000;"></td>
              <td style="border:.5pt solid #000;"></td>
              <td style="border:.5pt solid #000;"></td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;text-align:center;">（盖章）</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">1、正高级教师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.正高级教师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.正高级教师标准 || 1862 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('正高级教师人数', '正高级教师标准', 1862) }}</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-right:.5pt solid #000;text-align:right;padding-right:10px;">{{ nextDate }}</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">2、高级教师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.高级教师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.高级教师标准 || 1523 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('高级教师人数', '高级教师标准', 1523) }}</td>
              <td rowspan="12" style="border-left:.5pt solid #000;border-top:.5pt solid #000;border-right:.5pt solid #000;text-align:center;vertical-align:middle;writing-mode:vertical-rl;text-orientation:upright;letter-spacing:2px;font-weight:bold;font-size:9pt;">人事部门意见</td>
              <td colspan="6" style="border-left:.5pt solid #000;border-top:.5pt solid #000;border-bottom:.5pt solid #000;border-right:.5pt solid #000;text-align:left;padding-left:8px;">根据相关文件及有关规定，经审核，同意你单位：</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">3、一级教师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.一级教师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.一级教师标准 || 1309 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('一级教师人数', '一级教师标准', 1309) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;text-align:right;">基础性绩效工资</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.绩效人数合计 || calculateTotalCount() }}</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">人：</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.绩效工资合计 || calculateTotalAmount() }}</td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;">元；</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">4、二级教师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.二级教师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.二级教师标准 || 1241 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('二级教师人数', '二级教师标准', 1241) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;text-align:right;">生活补贴</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.在职人数 || 0 }}</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">人：</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.乡镇补贴合计 || calculateTownshipSubsidy() }}</td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;">元；</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">5、三级教师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.三级教师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.三级教师标准 || 1128 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('三级教师人数', '三级教师标准', 1128) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;text-align:right;">岗位设置遗留问题</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.遗留问题人数 || 0 }}</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">人：</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.遗留问题金额 || 0 }}</td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;">元；</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:5px;font-weight:bold;">工人</td>
              <td style="border:.5pt solid #000;"></td>
              <td style="border:.5pt solid #000;"></td>
              <td style="border:.5pt solid #000;"></td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">1、高级技师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.高级技师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.高级技师标准 || 0 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('高级技师人数', '高级技师标准', 0) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">2、技师</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.技师人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.技师标准 || 1331 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('技师人数', '技师标准', 1331) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">3、高级工</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.高级工人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.高级工标准 || 1219 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('高级工人数', '高级工标准', 1219) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">4、中级工</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.中级工人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.中级工标准 || 1185 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('中级工人数', '中级工标准', 1185) }}</td>
              <td style="border-left:.5pt solid #000;border-top:.5pt solid #000;"></td>
              <td colspan="4" style="border-top:.5pt solid #000;"></td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;"></td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">5、初级工</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.初级工人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.初级工标准 || 1106 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('初级工人数', '初级工标准', 1106) }}</td>
              <td colspan="4" style="border-left:.5pt solid #000;border-top:.5pt solid #000;border-bottom:.5pt solid #000;text-align:right;">合计：</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ calculateGrandTotal() }}</td>
              <td style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;">元</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;text-align:left;padding-left:10px;">6、普工</td>
              <td style="border:.5pt solid #000;"><el-input v-model="reportData.普工人数" size="small" class="cell-input" /></td>
              <td style="border:.5pt solid #000;">{{ reportData.普工标准 || 1106 }}</td>
              <td style="border:.5pt solid #000;">{{ calculateSubtotal('普工人数', '普工标准', 1106) }}</td>
              <td colspan="2" style="border-left:.5pt solid #000;border-bottom:.5pt solid #000;text-align:right;">注：无生活补贴</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.无补贴人数 || 0 }}</td>
              <td style="border-top:.5pt solid #000;border-bottom:.5pt solid #000;">人：</td>
              <td colspan="2" style="border-top:.5pt solid #000;border-right:.5pt solid #000;border-bottom:.5pt solid #000;">{{ reportData.无补贴名单 || '' }}</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;font-weight:bold;">绩效人数</td>
              <td style="border:.5pt solid #000;">{{ reportData.绩效人数合计 || calculateTotalCount() }}</td>
              <td style="border:.5pt solid #000;font-weight:bold;">绩效合计</td>
              <td style="border:.5pt solid #000;">{{ reportData.绩效工资合计 || calculateTotalAmount() }}</td>
              <td colspan="6" style="border-bottom:.5pt solid #000;border-right:.5pt solid #000;text-align:right;padding-right:10px;">{{ nextDate2 }}</td>
            </tr>
            <tr style="height:25pt">
              <td colspan="2" style="border:.5pt solid #000;font-weight:bold;">乡镇工作补贴人数</td>
              <td style="border:.5pt solid #000;">{{ reportData.在职人数 || 0 }}</td>
              <td style="border:.5pt solid #000;font-weight:bold;">标准</td>
              <td colspan="2" style="border:.5pt solid #000;">{{ reportData.乡镇补贴标准 || 350 }}</td>
              <td style="border:.5pt solid #000;font-weight:bold;">金额</td>
              <td colspan="4" style="border:.5pt solid #000;border-right:.5pt solid #000;">{{ reportData.乡镇补贴合计 || calculateTownshipSubsidy() }}</td>
            </tr>
            <tr style="height:25pt">
              <td style="border:.5pt solid #000;font-weight:bold;">退休干部人数</td>
              <td style="border:.5pt solid #000;">{{ reportData.退休干部 || 0 }}</td>
              <td colspan="2" style="border:.5pt solid #000;font-weight:bold;">退休工人人数</td>
              <td colspan="2" style="border:.5pt solid #000;">{{ reportData.退休职工 || 0 }}</td>
              <td style="border:.5pt solid #000;font-weight:bold;">离休干部人数</td>
              <td colspan="4" style="border:.5pt solid #000;border-right:.5pt solid #000;"><el-input v-model="reportData.离休干部人数" size="small" class="cell-input" /></td>
            </tr>
            <tr style="height:37pt">
              <td colspan="2" style="border:.5pt solid #000;font-weight:bold;">岗位设置遗留问题</td>
              <td style="border:.5pt solid #000;text-align:left;padding:2px;font-size:8pt;">{{ reportData.遗留问题详情 || '' }}</td>
              <td style="border:.5pt solid #000;font-weight:bold;">人数</td>
              <td colspan="2" style="border:.5pt solid #000;">{{ reportData.遗留问题人数 || 0 }}</td>
              <td style="border:.5pt solid #000;font-weight:bold;">金额</td>
              <td colspan="4" style="border:.5pt solid #000;border-right:.5pt solid #000;">{{ reportData.遗留问题金额 || 0 }}</td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border:.5pt solid #000;text-align:left;padding-left:10px;">备注:</td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;text-align:left;padding-left:10px;">{{ reportData.备注 || '' }}</td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;"></td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;"></td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;"></td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;"></td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;"></td>
            </tr>
            <tr style="height:21pt">
              <td colspan="11" style="border-right:.5pt solid #000;border-bottom:.5pt solid #000;border-left:.5pt solid #000;border-top:none;"></td>
            </tr>
          </table>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="monthDialogVisible" title="设置填报月份" width="360px" :close-on-click-modal="false">
      <div style="text-align: center; padding: 20px 0;">
        <p style="margin-bottom: 15px; font-size: 14px;">请选择需要填报绩效工资的月份：</p>
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          placeholder="选择月份"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          style="width: 200px;"
        />
      </div>
      <template #footer>
        <el-button @click="monthDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loadingData" @click="confirmLoadData">确认加载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Download, Check } from '@element-plus/icons-vue'

const saving = ref(false)
const exporting = ref(false)
const loadingData = ref(false)
const monthDialogVisible = ref(false)

const now = new Date()
const todayYear = now.getFullYear()
const todayMonth = now.getMonth() + 1
const todayDay = now.getDate()

const defaultMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1)
const selectedMonth = ref(`${defaultMonth.getFullYear()}-${String(defaultMonth.getMonth() + 1).padStart(2, '0')}`)

const reportYear = ref(defaultMonth.getFullYear())
const reportMonth = ref(defaultMonth.getMonth() + 1)

const currentYearMonth = computed(() => `${reportYear.value}年${reportMonth.value}月`)
const currentDate = computed(() => `${todayYear}年${todayMonth}月${todayDay}日`)
const nextDate = computed(() => {
  const d = new Date(now); d.setDate(d.getDate() + 1)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})
const nextDate2 = computed(() => {
  const d = new Date(now); d.setDate(d.getDate() + 2)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

const showMonthDialog = () => {
  monthDialogVisible.value = true
}

const confirmLoadData = () => {
  if (!selectedMonth.value) {
    ElMessage.warning('请选择月份')
    return
  }
  const parts = selectedMonth.value.split('-')
  reportYear.value = parseInt(parts[0])
  reportMonth.value = parseInt(parts[1])
  monthDialogVisible.value = false
  handleLoadData()
}

const reportData = reactive({
  填报单位: '太平中心学校',
  副处级人数: 0, 副处级标准: 0,
  正科级人数: 0, 正科级标准: 0,
  副科级人数: 0, 副科级标准: 0,
  科员级人数: 0, 科员级标准: 1185,
  办事员级人数: 0, 办事员级标准: 0,
  正高级教师人数: 0, 正高级教师标准: 1862,
  高级教师人数: 0, 高级教师标准: 1523,
  一级教师人数: 0, 一级教师标准: 1309,
  二级教师人数: 0, 二级教师标准: 1241,
  三级教师人数: 0, 三级教师标准: 1128,
  高级技师人数: 0, 高级技师标准: 0,
  技师人数: 0, 技师标准: 1331,
  高级工人数: 0, 高级工标准: 1219,
  中级工人数: 0, 中级工标准: 1185,
  初级工人数: 0, 初级工标准: 1106,
  普工人数: 0, 普工标准: 1106,
  绩效人数合计: 0,
  绩效工资合计: 0,
  在职人数: 0,
  乡镇补贴标准: 350,
  乡镇补贴合计: 0,
  退休干部: 0,
  退休职工: 0,
  离休干部人数: 0,
  遗留问题详情: '',
  遗留问题人数: 0,
  遗留问题金额: 0,
  无补贴人数: 0,
  无补贴名单: '',
  备注: ''
})

const calculateSubtotal = (countKey: string, stdKey: string, defaultStd: number) => {
  return (Number(reportData[countKey] || 0)) * (Number(reportData[stdKey] || defaultStd))
}

const calculateTotalCount = () => {
  const keys = ['副处级人数','正科级人数','副科级人数','科员级人数','办事员级人数','正高级教师人数','高级教师人数','一级教师人数','二级教师人数','三级教师人数','高级技师人数','技师人数','高级工人数','中级工人数','初级工人数','普工人数']
  return keys.reduce((s, k) => s + Number(reportData[k] || 0), 0)
}

const calculateTotalAmount = () => {
  const items = [
    ['副处级人数','副处级标准',0],['正科级人数','正科级标准',0],['副科级人数','副科级标准',0],
    ['科员级人数','科员级标准',1185],['办事员级人数','办事员级标准',0],
    ['正高级教师人数','正高级教师标准',1862],['高级教师人数','高级教师标准',1523],
    ['一级教师人数','一级教师标准',1309],['二级教师人数','二级教师标准',1241],
    ['三级教师人数','三级教师标准',1128],
    ['高级技师人数','高级技师标准',0],['技师人数','技师标准',1331],
    ['高级工人数','高级工标准',1219],['中级工人数','中级工标准',1185],
    ['初级工人数','初级工标准',1106],['普工人数','普工标准',1106]
  ]
  return items.reduce((s, [c, st, d]) => s + calculateSubtotal(c, st, d), 0)
}

const calculateTownshipSubsidy = () => (Number(reportData.在职人数 || 0)) * (Number(reportData.乡镇补贴标准 || 350))

const calculateGrandTotal = () => calculateTotalAmount() + calculateTownshipSubsidy() + (reportData.遗留问题金额 || 0)

const handleLoadData = async () => {
  loadingData.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/load-from-database', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year: reportYear.value, month: reportMonth.value })
    })
    if (!response.ok) throw new Error('加载数据失败')
    const result = await response.json()
    if (result.status === 'success') { Object.assign(reportData, result.data); ElMessage.success('数据加载成功') }
  } catch (error: any) { ElMessage.error(error.message || '加载数据失败') }
  finally { loadingData.value = false }
}

const handleSave = async () => {
  saving.value = true
  try {
    reportData.绩效人数合计 = calculateTotalCount()
    reportData.绩效工资合计 = calculateTotalAmount()
    reportData.乡镇补贴合计 = calculateTownshipSubsidy()
    const response = await fetch('/api/performance-pay-approval/save', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData)
    })
    if (!response.ok) throw new Error('保存失败')
    const result = await response.json()
    if (result.status === 'success') ElMessage.success('保存成功')
  } catch (error: any) { ElMessage.error(error.message || '保存失败') }
  finally { saving.value = false }
}

const handleExport = async (format: string) => {
  if (format === 'print') { window.print(); return }
  exporting.value = true
  try {
    reportData.绩效人数合计 = calculateTotalCount()
    reportData.绩效工资合计 = calculateTotalAmount()
    reportData.乡镇补贴合计 = calculateTownshipSubsidy()
    const response = await fetch(`/api/performance-pay-approval/export?format=${format}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData)
    })
    if (!response.ok) throw new Error('导出失败')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `绩效工资审批表_${reportYear.value}年${reportMonth.value}月.${format === 'excel' ? 'xlsx' : 'pdf'}`
    document.body.appendChild(link); link.click(); document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success(`已导出 ${format.toUpperCase()} 格式`)
  } catch (error: any) { ElMessage.error(error.message || '导出失败') }
  finally { exporting.value = false }
}

onMounted(() => {})
</script>

<style scoped>
.performance-pay-approval-page { padding: 20px; }
.page-card { min-height: calc(100vh - 140px); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h2 { margin: 0; font-size: 20px; }
.header-actions { display: flex; gap: 10px; }
.report-container { margin-top: 20px; overflow-x: auto; }

.a4-page {
  width: 880px;
  margin: 0 auto;
  background: white;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  font-family: '宋体', 'SimSun', serif;
  font-size: 10pt;
}

.salary-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.salary-table td {
  padding: 2px 4px;
  text-align: center;
  vertical-align: middle;
  font-size: 10pt;
}

.cell-input { width: 100%; }
.cell-input :deep(.el-input__inner) { padding: 0 2px; height: 20px; text-align: center; font-size: 9pt; }
.inline-input :deep(.el-input__inner) { border: none; border-bottom: 1px solid #ccc; border-radius: 0; background: transparent; }

@media print {
  .page-card :deep(.el-card__header) { display: none; }
  .a4-page { width: 100%; padding: 0; box-shadow: none; }
  .cell-input :deep(.el-input__inner) { border: none; background: transparent; }
}
</style>
