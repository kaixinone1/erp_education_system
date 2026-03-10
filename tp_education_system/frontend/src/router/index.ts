import { createRouter, createWebHistory } from "vue-router"
import Dashboard from "../views/dashboard/index.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
          component: () => import("../views/system/UniversalTemplate.vue"),
          meta: {
            title: "通用模板管理",
            icon: "Document"
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
    // 通用中间表路由（旧框架）- 匹配 /intermediate/:tableName 格式
    {
      path: "/intermediate/:tableName",
      name: "intermediateTableView",
      component: () => import("../views/IntermediateTableView.vue"),
      meta: {
        title: "中间表管理（旧框架）",
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
        title: "推送清单",
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
    {
      path: "/system/intermediate-table",
      name: "intermediateTableManager",
      component: () => import("../views/intermediate-table/IntermediateTableManager.vue"),
      meta: {
        title: "中间表管理",
        icon: "Grid"
      }
    },
    // 报表管理子模块路由
    {
      path: "/report/template-mgt",
      name: "templateManagement",
      component: () => import("../views/template-manager/index.vue"),
      meta: {
        title: "模板管理",
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
    },
    // 模板标记界面
    {
      path: "/template-marker/:id",
      name: "templateMarker",
      component: () => import("../components/TemplateMarker/index.vue"),
      meta: {
        title: "模板字段标记",
        icon: "Edit"
      }
    },
    // 字段映射配置界面
    {
      path: "/template-field-mapping/:id",
      name: "templateFieldMapping",
      component: () => import("../views/template-manager/FieldMapping.vue"),
      meta: {
        title: "字段映射配置",
        icon: "Connection"
      }
    },
    // 可编辑预览界面
    {
      path: "/template-preview/:id",
      name: "templateEditablePreview",
      component: () => import("../views/template-manager/EditablePreview.vue"),
      meta: {
        title: "模板预览编辑",
        icon: "View"
      }
    },
    // 中间表设计器
    {
      path: "/intermediate-table-designer/:tableName?",
      name: "intermediateTableDesigner",
      component: () => import("../views/template-manager/IntermediateTableDesigner.vue"),
      meta: {
        title: "中间表设计器",
        icon: "Grid"
      }
    },
    // Excel模板编辑器
    {
      path: "/excel-template-editor/:id",
      name: "excelTemplateEditor",
      component: () => import("../components/ExcelTemplateEditor/index.vue"),
      meta: {
        title: "Excel模板编辑",
        icon: "Grid"
      }
    },
    // PDF模板编辑器
    {
      path: "/pdf-template-editor/:id",
      name: "pdfTemplateEditor",
      component: () => import("../components/PDFTemplateEditor/index.vue"),
      meta: {
        title: "PDF模板编辑",
        icon: "Document"
      }
    },
    // A3模板编辑器（四区域）
    {
      path: "/a3-template-editor/:id",
      name: "a3TemplateEditor",
      component: () => import("../components/PDFTemplateEditor/A3RegionEditor.vue"),
      meta: {
        title: "A3模板编辑",
        icon: "Document"
      }
    },
    // HTML模板编辑器
    {
      path: "/html-template-editor/:id",
      name: "htmlTemplateEditor",
      component: () => import("../views/html-template-editor/index.vue"),
      meta: {
        title: "HTML模板编辑",
        icon: "Document"
      }
    },
    // 模板填报页面
    {
      path: "/template-fill/:id",
      name: "templateFill",
      component: () => import("../views/template-fill/index.vue"),
      meta: {
        title: "模板填报",
        icon: "Edit"
      }
    },

    // 文件上传测试
    {
      path: "/test-upload",
      name: "testUpload",
      component: () => import("../components/TestFileUpload.vue"),
      meta: {
        title: "文件上传测试",
        icon: "Upload"
      }
    }
  ]
})

// 全局前置守卫，设置页面标题和模块类型检查
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || "页面"} - 太平镇教育人事管理系统`
  
  // 检查是否是模块类型的路由（文件夹类型不应该直接访问）
  if (to.meta.moduleType === 'module') {
    // 如果是模块类型（文件夹），重定向到第一个子节点或提示
    console.warn(`[路由守卫] 尝试直接访问文件夹类型模块: ${to.path}，该模块用于组织子模块，不直接显示内容`)
    // 可以重定向到首页或显示提示页面
    // next({ path: '/', query: { message: '该模块为文件夹类型，请选择子模块访问' }})
  }
  
  next()
})

export default router
