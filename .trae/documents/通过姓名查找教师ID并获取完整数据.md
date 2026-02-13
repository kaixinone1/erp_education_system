# 问题分析

## 错误提示
"教师ID无效，请重新选择教师"

## 根本原因
在 `ChecklistDrawer.vue` 的 `handleTaskAction` 函数中：
```javascript
const teacherId = props.todoData?.teacher_id  // ← 这里获取的是 undefined
```

`todoData` 中只有 `teacher_name`，没有 `teacher_id` 字段。

## 解决方案

修改 `ChecklistDrawer.vue` 的 `handleTaskAction` 函数：

```javascript
// 特殊处理退休呈报表填报
if (tableName === 'retirement_report_form') {
  let teacherId = props.todoData?.teacher_id
  const teacherName = props.todoData?.teacher_name
  
  // 如果teacher_id无效，尝试通过姓名查找
  if (!teacherId || teacherId <= 0) {
    if (teacherName) {
      // 通过姓名查找教师ID
      const response = await fetch(`/api/retirement/search-by-name?name=${encodeURIComponent(teacherName)}`)
      if (response.ok) {
        const result = await response.json()
        const teachers = result.data || []
        if (teachers.length > 0) {
          teacherId = teachers[0].id
        }
      }
    }
  }
  
  if (!teacherId || teacherId <= 0) {
    ElMessage.error('教师ID无效，请重新选择教师')
    return
  }
  
  await handleRetirementReportForm(teacherName, teacherId)
  return
}
```

## 实施步骤
1. 修改 `ChecklistDrawer.vue` 的 `handleTaskAction` 函数
2. 确保后端 `/api/retirement/search-by-name` API 可用
3. 测试通过姓名查找教师功能