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
    // 表结构管理
    {
      path: "/data/table-structure",
      name: "tableStructure",
      component: () => import("../views/data/TableStructure.vue"),
      meta: {
        title: "表结构管理",
        icon: "Setting"
      }
    }
  ]
})

// 全局前置守卫，设置页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || "页面"} - 太平镇教育人事管理系统`
  next()
})

export default router
