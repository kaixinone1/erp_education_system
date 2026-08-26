import { createRouter, createWebHashHistory } from "vue-router"
import Dashboard from "../views/dashboard/index.vue"

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginPage.vue"),
      meta: {
        title: "登录",
        hideMenu: true
      }
    },
    {
      path: "/",
      name: "home",
      component: Dashboard,
      meta: {
        title: "首页",
        icon: "House"
      }
    },
    // 系统管理 - 元模块，必须保留
    {
      path: "/system",
      name: "system",
      redirect: "/system/module-mgt",
      children: [
        {
          path: "module-mgt",
          name: "moduleMgt",
          component: () => import("../views/system/ModuleManagement.vue"),
          meta: {
            title: "模块管理",
            icon: "Grid"
          }
        },
        {
          path: "table-mgt",
          name: "tableMgt",
          component: () => import("../views/admin/TableManagementView.vue"),
          meta: {
            title: "数据表管理",
            icon: "List"
          }
        },
        {
          path: "data-migration",
          name: "dataMigration",
          component: () => import("../views/system/DataMigration.vue"),
          meta: {
            title: "数据迁移工具",
            icon: "Switch"
          }
        },
        {
          path: "table-export",
          name: "systemTableExport",
          component: () => import("../views/system/SystemTableExport.vue"),
          meta: {
            title: "数据表导出导入",
            icon: "Download"
          }
        },
        {
          path: "tag-relations",
          name: "tagRelations",
          component: () => import("../views/system/TagRelations.vue"),
          meta: {
            title: "标签关系管理",
            icon: "Connection"
          }
        },
        {
          path: "universal-template",
          name: "universalTemplate",
          component: () => import("../views/template/TemplateManager.vue"),
          meta: {
            title: "通用模板系统",
            icon: "Files"
          }
        },
        {
          path: "file-manager",
          name: "fileManager",
          component: () => import("../views/system/FileManager.vue"),
          meta: {
            title: "文件管理",
            icon: "FolderOpened"
          }
        },
        {
          path: "users",
          name: "systemUsers",
          component: () => import("../views/system/UserManagement.vue"),
          meta: {
            title: "用户管理",
            icon: "User"
          }
        },
        {
          path: "backup",
          name: "systemBackup",
          component: () => import("../views/system/SystemBackup.vue"),
          meta: {
            title: "系统自动备份",
            icon: "Upload"
          }
        },
        {
          path: "db-backup",
          name: "dbBackupSettings",
          component: () => import("../views/system/BackupSettings.vue"),
          meta: {
            title: "数据库自动备份",
            icon: "Coin"
          }
        },
        {
          path: "snapshot-history",
          name: "snapshotHistory",
          component: () => import("../views/system/SnapshotHistory.vue"),
          meta: {
            title: "历史快照",
            icon: "Timer"
          }
        },
        ]
    },
    // 预警督办模块
    {
      path: "/todo",
      name: "todoManagement",
      redirect: "/todo/work",
      children: [
        {
          path: "business",
          name: "todoBusinessNew",
          component: () => import("../views/system/TodoBusiness.vue"),
          meta: {
            title: "待办业务管理",
            icon: "List"
          }
        },
        {
          path: "checklist-template",
          name: "checklistTemplateManage",
          component: () => import("../views/checklist/ChecklistTemplateView.vue"),
          meta: {
            title: "清单模板管理",
            icon: "DocumentCopy"
          }
        },
        {
          path: "work",
          name: "todoWorkNew",
          component: () => import("../views/system/TodoWork.vue"),
          meta: {
            title: "待办工作",
            icon: "Bell"
          }
        },
        {
          path: "history",
          name: "todoHistory",
          component: () => import("../views/system/TodoHistory.vue"),
          meta: {
            title: "待办历史",
            icon: "Clock"
          }
        }
      ]
    },
    // 数据导入工作台 - 核心功能
    {
      path: "/import/workbench",
      name: "importWorkbench",
      component: () => import("../views/import/DataImportWorkbench.vue"),
      meta: {
        title: "数据导入工作台",
        icon: "Upload"
      }
    },
    // 通用数据视图 - 动态路由，用于所有数据节点
    {
      path: "/data/:tableName",
      name: "genericDataView",
      component: () => import("../views/data/GenericDataView.vue"),
      meta: {
        title: "数据管理",
        icon: "Document"
      }
    },
    // 绩效管理模块（其他子路由保留，仅绩效工资审批移到薪酬管理）
    {
      path: "/performance",
      name: "performance",
      redirect: "/performance/pay-history",
      children: [
        {
          path: "pay-history",
          name: "performancePayHistory",
          component: () => import("../views/performance/PerformancePayHistory.vue"),
          meta: {
            title: "绩效工资历史",
            icon: "Clock"
          }
        },
        {
          path: "pay-statistics",
          name: "performancePayStatistics",
          component: () => import("../views/performance/PerformancePayStatistics.vue"),
          meta: {
            title: "绩效工资统计",
            icon: "TrendCharts"
          }
        },
        {
          path: "pay-upload",
          name: "performancePayUpload",
          component: () => import("../views/performance/PerformancePayUpload.vue"),
          meta: {
            title: "绩效工资上传",
            icon: "Upload"
          }
        },
        {
          path: "standards",
          name: "performanceStandards",
          component: () => import("../views/performance/PerformanceStandards.vue"),
          meta: {
            title: "绩效标准设置",
            icon: "Setting"
          }
        },
        {
          path: "aggregate-query",
          name: "aggregateQuery",
          component: () => import("../views/AggregateQuery.vue"),
          meta: {
            title: "聚合查询",
            icon: "Search"
          }
        },      ]
    },
    // 模块数据节点路由 - 匹配 /module-id/table-name 格式
    {
      path: "/:moduleId/:tableName",
      name: "moduleDataView",
      component: () => import("../views/data/GenericDataView.vue"),
      meta: {
        title: "数据管理",
        icon: "Document"
      }
    },
    // 子模块路由 - 匹配 /module-id/sub-module/table-name 格式
    {
      path: "/:parentId/:moduleId/:tableName",
      name: "subModuleDataView",
      component: () => import("../views/data/GenericDataView.vue"),
      meta: {
        title: "数据管理",
        icon: "Document"
      }
    },
    // 系统模块路由 - 匹配 /system/module-id/table-name 格式
    {
      path: "/system/:moduleId/:tableName",
      name: "systemModuleDataView",
      component: () => import("../views/data/GenericDataView.vue"),
      meta: {
        title: "数据管理",
        icon: "Document"
      }
    },
    // 自动表管理路由（新框架 - 零配置）- 匹配 /auto-table/:tableName 格式
    {
      path: "/auto-table/:tableName",
      name: "autoTableView",
      component: () => import("../views/AutoTableView.vue"),
      meta: {
        title: "自动表管理（零配置）",
        icon: "Document"
      }
    },
    // 通用数据字典/数据表路由 - 匹配 /data/:tableName 格式（导航动态生成）
    {
      path: "/data/:tableName",
      name: "dynamicDataView",
      component: () => import("../views/AutoTableView.vue"),
      meta: {
        title: "数据管理",
        icon: "Document"
      }
    },
    // 统一报表查看路由 - 三处共用
    {
      path: "/report-view/:templateId/:teacherId?",
      name: "reportView",
      component: () => import("../views/report/ReportView.vue"),
      meta: {
        title: "报表查看",
        icon: "Document"
      }
    },
    // 通用模板报表查看路由
    {
      path: "/universal-report/:templateId/:teacherId?",
      name: "universalReportView",
      component: () => import("../views/report/UniversalReportView.vue"),
      meta: {
        title: "通用模板导出",
        icon: "Document"
      }
    },
    {
      path: "/scheduled-templates",
      name: "scheduledTemplates",
      component: () => import("../views/report/ScheduledTemplateView.vue"),
      meta: {
        title: "固定时段任务",
        icon: "Timer"
      }
    },
    // 清单管理子模块路由
    {
      path: "/system/checklist/pushed",
      name: "checklistPushed",
      component: () => import("../views/checklist/PushedChecklistView.vue"),
      meta: {
        title: "待办工作项",
        icon: "Bell"
      }
    },
    {
      path: "/system/checklist/templates",
      name: "checklistTemplates",
      component: () => import("../views/checklist/ChecklistTemplateView.vue"),
      meta: {
        title: "清单模板",
        icon: "DocumentCopy"
      }
    },
    // 薪酬管理模块
    {
      path: "/salary",
      name: "salary",
      redirect: "/salary/performance",
      children: [
        {
          path: "performance",
          name: "salaryPerformance",
          redirect: "/salary/performance/approval",
          meta: {
            title: "绩效工资管理",
            icon: "Money"
          }
        },
        {
          path: "performance/approval",
          name: "salaryPerformanceApproval",
          component: () => import("../views/salary/SalaryPerformanceApproval.vue"),
          meta: {
            title: "绩效工资审批",
            icon: "Document"
          }
        }
      ]
    },
    // 学校管理模块（含学生管理和考勤管理预留子路由）
    {
      path: "/school",
      name: "school",
      redirect: "/data/school_information_table",
      children: [
        {
          path: "student",
          name: "schoolStudent",
          component: () => import("../views/school/SchoolPlaceholder.vue"),
          meta: {
            title: "学生管理",
            icon: "User"
          }
        },
        {
          path: "attendance",
          name: "schoolAttendance",
          component: () => import("../views/school/SchoolPlaceholder.vue"),
          meta: {
            title: "考勤管理",
            icon: "Calendar"
          }
        }
      ],
      meta: {
        title: "学校管理",
        icon: "School"
      }
    },
    // 党组织管理模块
    {
      path: "/party",
      name: "party",
      redirect: "/data/zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao",
      meta: {
        title: "党组织管理",
        icon: "Flag"
      }
    },
    // 报表管理子模块路由
    {
      path: "/report/retirement/estimate",
      name: "retirementEstimate",
      component: () => import("../views/retirement/RetirementEstimate.vue"),
      meta: {
        title: "退休测算",
        icon: "Calculator"
      }
    },
    // 退休教师管理 - 模板
    {
      path: "/personnel/retired/post-change-report",
      name: "retirementPostChangeReport",
      component: () => import("../views/retirement/RetirementPostChangeReport.vue"),
      meta: {
        title: "职务升降退休人员信息申报表",
        icon: "Document"
      }
    },
    {
      path: "/personnel/retired/retirement-report",
      name: "retirementReportForm",
      component: () => import("../views/retirement/RetirementReportForm.vue"),
      meta: {
        title: "职工退休呈报表",
        icon: "Document"
      }
    },
    // 表结构管理
    {
      path: "/data/table-structure",
      name: "tableStructure",
      component: () => import("../views/data/TableStructure.vue"),
      meta: {
        title: "表结构管理",
        icon: "Setting"
      }
    },
    // 数据清理工具（开发用）
    {
      path: "/admin/data-cleanup",
      name: "dataCleanup",
      component: () => import("../views/admin/DataCleanupView.vue"),
      meta: {
        title: "数据清理工具",
        icon: "Delete"
      }
    }
  ]
})

// 全局前置守卫，设置页面标题和认证检查
router.beforeEach(async (to, from, next) => {
  const saved = localStorage.getItem('user_auth')
  const parsed = saved ? JSON.parse(saved) : {}
  const unitName = parsed.已选单位名称 || ''
  const systemName = unitName ? `${unitName}教育人事管理系统` : '教育人事管理系统'
  document.title = `${to.meta.title || "页面"} - ${systemName}`
  
  // 登录页面不需要认证
  if (to.path === '/login') {
    next()
    return
  }
  
  // 检查是否已登录（localStorage 无数据则跳转登录页）
  if (!saved) {
    next('/login')
    return
  }
  
  // 检查是否已选择单位（已登录但未选单位，引导选择）
  try {
    if (!parsed.已选单位ID && !parsed.已选单位名称) {
      next('/login')
      return
    }
  } catch (e) {
    next('/login')
    return
  }
  
  // === token 有效性验证 ===
  // 每个浏览器会话只验证一次，避免每次路由切换都发请求
  const tokenVerified = sessionStorage.getItem('token_verified')
  if (!tokenVerified) {
    try {
      const token = parsed.token
      if (token) {
        const res = await fetch(`/api/auth/current-unit?token=${encodeURIComponent(token)}`)
        if (res.status === 401) {
          // token 已过期，清除登录状态，跳转登录页
          localStorage.removeItem('user_auth')
          sessionStorage.removeItem('token_verified')
          console.log('[路由守卫] token 已过期，需要重新登录')
          next('/login')
          return
        }
        // token 有效，标记已验证
        sessionStorage.setItem('token_verified', '1')
      } else {
        // 没有 token，跳转登录页
        localStorage.removeItem('user_auth')
        next('/login')
        return
      }
    } catch (e) {
      // 网络错误，允许继续（可能是后端未启动）
      console.warn('[路由守卫] token 验证失败（网络错误）:', e)
    }
  }
  
  // 检查是否是模块类型的路由（文件夹类型不应该直接访问）
  if (to.meta.moduleType === 'module') {
    console.warn(`[路由守卫] 尝试直接访问文件夹类型模块: ${to.path}，该模块用于组织子模块，不直接显示内容`)
  }
  
  next()
})

export default router