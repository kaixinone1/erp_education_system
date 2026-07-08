// vite.config.ts
import { defineConfig } from "file:///D:/erp_thirteen/tp_education_system/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/erp_thirteen/tp_education_system/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import AutoImport from "file:///D:/erp_thirteen/tp_education_system/frontend/node_modules/unplugin-auto-import/dist/vite.js";
import Components from "file:///D:/erp_thirteen/tp_education_system/frontend/node_modules/unplugin-vue-components/dist/vite.js";
import { ElementPlusResolver } from "file:///D:/erp_thirteen/tp_education_system/frontend/node_modules/unplugin-vue-components/dist/resolvers.js";
import path from "path";
var __vite_injected_original_dirname = "D:\\erp_thirteen\\tp_education_system\\frontend";
var vite_config_default = defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()]
    }),
    Components({
      resolvers: [ElementPlusResolver()]
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src")
    }
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api/universal-template": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      },
      "/api/navigation-admin": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      },
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path2) => path2
      },
      "/template-files": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    },
    // 优化热更新性能
    hmr: {
      overlay: false
      // 禁用错误遮罩层，提高性能
    },
    // 优化预构建
    preTransformRequests: false
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: [
      "vue",
      "vue-router",
      "pinia",
      "element-plus",
      "@element-plus/icons-vue",
      "echarts",
      "vue-echarts",
      "docx",
      "xlsx"
    ],
    // 排除大文件
    exclude: [],
    // 强制预构建
    force: false
  },
  // 构建优化
  build: {
    // 启用代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          "element-plus": ["element-plus"],
          "echarts": ["echarts", "vue-echarts"],
          "vendor": ["vue", "vue-router", "pinia"]
        }
      }
    },
    // 减小 chunk 大小警告阈值
    chunkSizeWarningLimit: 1e3
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxlcnBfdGhpcnRlZW5cXFxcdHBfZWR1Y2F0aW9uX3N5c3RlbVxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiRDpcXFxcZXJwX3RoaXJ0ZWVuXFxcXHRwX2VkdWNhdGlvbl9zeXN0ZW1cXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcudHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0Q6L2VycF90aGlydGVlbi90cF9lZHVjYXRpb25fc3lzdGVtL2Zyb250ZW5kL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSBcInZpdGVcIlxyXG5pbXBvcnQgdnVlIGZyb20gXCJAdml0ZWpzL3BsdWdpbi12dWVcIlxyXG5pbXBvcnQgQXV0b0ltcG9ydCBmcm9tIFwidW5wbHVnaW4tYXV0by1pbXBvcnQvdml0ZVwiXHJcbmltcG9ydCBDb21wb25lbnRzIGZyb20gXCJ1bnBsdWdpbi12dWUtY29tcG9uZW50cy92aXRlXCJcclxuaW1wb3J0IHsgRWxlbWVudFBsdXNSZXNvbHZlciB9IGZyb20gXCJ1bnBsdWdpbi12dWUtY29tcG9uZW50cy9yZXNvbHZlcnNcIlxyXG5pbXBvcnQgcGF0aCBmcm9tIFwicGF0aFwiXHJcblxyXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xyXG4gIHBsdWdpbnM6IFtcclxuICAgIHZ1ZSgpLFxyXG4gICAgQXV0b0ltcG9ydCh7XHJcbiAgICAgIHJlc29sdmVyczogW0VsZW1lbnRQbHVzUmVzb2x2ZXIoKV0sXHJcbiAgICB9KSxcclxuICAgIENvbXBvbmVudHMoe1xyXG4gICAgICByZXNvbHZlcnM6IFtFbGVtZW50UGx1c1Jlc29sdmVyKCldLFxyXG4gICAgfSksXHJcbiAgXSxcclxuICByZXNvbHZlOiB7XHJcbiAgICBhbGlhczoge1xyXG4gICAgICBcIkBcIjogcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgXCIuL3NyY1wiKSxcclxuICAgIH0sXHJcbiAgfSxcclxuICBzZXJ2ZXI6IHtcclxuICAgIHBvcnQ6IDUxNzMsXHJcbiAgICBob3N0OiAnMC4wLjAuMCcsXHJcbiAgICBwcm94eToge1xyXG4gICAgICAnL2FwaS91bml2ZXJzYWwtdGVtcGxhdGUnOiB7XHJcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovLzEyNy4wLjAuMTo4MDAwJyxcclxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWVcclxuICAgICAgfSxcclxuICAgICAgJy9hcGkvbmF2aWdhdGlvbi1hZG1pbic6IHtcclxuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vMTI3LjAuMC4xOjgwMDAnLFxyXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZVxyXG4gICAgICB9LFxyXG4gICAgICAnL2FwaSc6IHtcclxuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vMTI3LjAuMC4xOjgwMDAnLFxyXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcclxuICAgICAgICByZXdyaXRlOiAocGF0aCkgPT4gcGF0aFxyXG4gICAgICB9LFxyXG4gICAgICAnL3RlbXBsYXRlLWZpbGVzJzoge1xyXG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6ODAwMCcsXHJcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlXHJcbiAgICAgIH1cclxuICAgIH0sXHJcbiAgICAvLyBcdTRGMThcdTUzMTZcdTcwRURcdTY2RjRcdTY1QjBcdTYwMjdcdTgwRkRcclxuICAgIGhtcjoge1xyXG4gICAgICBvdmVybGF5OiBmYWxzZSwgLy8gXHU3OTgxXHU3NTI4XHU5NTE5XHU4QkVGXHU5MDZFXHU3RjY5XHU1QzQyXHVGRjBDXHU2M0QwXHU5QUQ4XHU2MDI3XHU4MEZEXHJcbiAgICB9LFxyXG4gICAgLy8gXHU0RjE4XHU1MzE2XHU5ODg0XHU2Nzg0XHU1RUZBXHJcbiAgICBwcmVUcmFuc2Zvcm1SZXF1ZXN0czogZmFsc2UsXHJcbiAgfSxcclxuICAvLyBcdTRGMThcdTUzMTZcdTRGOURcdThENTZcdTk4ODRcdTY3ODRcdTVFRkFcclxuICBvcHRpbWl6ZURlcHM6IHtcclxuICAgIGluY2x1ZGU6IFtcclxuICAgICAgJ3Z1ZScsXHJcbiAgICAgICd2dWUtcm91dGVyJyxcclxuICAgICAgJ3BpbmlhJyxcclxuICAgICAgJ2VsZW1lbnQtcGx1cycsXHJcbiAgICAgICdAZWxlbWVudC1wbHVzL2ljb25zLXZ1ZScsXHJcbiAgICAgICdlY2hhcnRzJyxcclxuICAgICAgJ3Z1ZS1lY2hhcnRzJyxcclxuICAgICAgJ2RvY3gnLFxyXG4gICAgICAneGxzeCcsXHJcbiAgICBdLFxyXG4gICAgLy8gXHU2MzkyXHU5NjY0XHU1OTI3XHU2NTg3XHU0RUY2XHJcbiAgICBleGNsdWRlOiBbXSxcclxuICAgIC8vIFx1NUYzQVx1NTIzNlx1OTg4NFx1Njc4NFx1NUVGQVxyXG4gICAgZm9yY2U6IGZhbHNlLFxyXG4gIH0sXHJcbiAgLy8gXHU2Nzg0XHU1RUZBXHU0RjE4XHU1MzE2XHJcbiAgYnVpbGQ6IHtcclxuICAgIC8vIFx1NTQyRlx1NzUyOFx1NEVFM1x1NzgwMVx1NTIwNlx1NTI3MlxyXG4gICAgcm9sbHVwT3B0aW9uczoge1xyXG4gICAgICBvdXRwdXQ6IHtcclxuICAgICAgICBtYW51YWxDaHVua3M6IHtcclxuICAgICAgICAgICdlbGVtZW50LXBsdXMnOiBbJ2VsZW1lbnQtcGx1cyddLFxyXG4gICAgICAgICAgJ2VjaGFydHMnOiBbJ2VjaGFydHMnLCAndnVlLWVjaGFydHMnXSxcclxuICAgICAgICAgICd2ZW5kb3InOiBbJ3Z1ZScsICd2dWUtcm91dGVyJywgJ3BpbmlhJ10sXHJcbiAgICAgICAgfSxcclxuICAgICAgfSxcclxuICAgIH0sXHJcbiAgICAvLyBcdTUxQ0ZcdTVDMEYgY2h1bmsgXHU1OTI3XHU1QzBGXHU4QjY2XHU1NDRBXHU5NjA4XHU1MDNDXHJcbiAgICBjaHVua1NpemVXYXJuaW5nTGltaXQ6IDEwMDAsXHJcbiAgfSxcclxufSlcclxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUE4VCxTQUFTLG9CQUFvQjtBQUMzVixPQUFPLFNBQVM7QUFDaEIsT0FBTyxnQkFBZ0I7QUFDdkIsT0FBTyxnQkFBZ0I7QUFDdkIsU0FBUywyQkFBMkI7QUFDcEMsT0FBTyxVQUFVO0FBTGpCLElBQU0sbUNBQW1DO0FBT3pDLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVM7QUFBQSxJQUNQLElBQUk7QUFBQSxJQUNKLFdBQVc7QUFBQSxNQUNULFdBQVcsQ0FBQyxvQkFBb0IsQ0FBQztBQUFBLElBQ25DLENBQUM7QUFBQSxJQUNELFdBQVc7QUFBQSxNQUNULFdBQVcsQ0FBQyxvQkFBb0IsQ0FBQztBQUFBLElBQ25DLENBQUM7QUFBQSxFQUNIO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLEtBQUssUUFBUSxrQ0FBVyxPQUFPO0FBQUEsSUFDdEM7QUFBQSxFQUNGO0FBQUEsRUFDQSxRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCwyQkFBMkI7QUFBQSxRQUN6QixRQUFRO0FBQUEsUUFDUixjQUFjO0FBQUEsTUFDaEI7QUFBQSxNQUNBLHlCQUF5QjtBQUFBLFFBQ3ZCLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxNQUNoQjtBQUFBLE1BQ0EsUUFBUTtBQUFBLFFBQ04sUUFBUTtBQUFBLFFBQ1IsY0FBYztBQUFBLFFBQ2QsU0FBUyxDQUFDQSxVQUFTQTtBQUFBLE1BQ3JCO0FBQUEsTUFDQSxtQkFBbUI7QUFBQSxRQUNqQixRQUFRO0FBQUEsUUFDUixjQUFjO0FBQUEsTUFDaEI7QUFBQSxJQUNGO0FBQUE7QUFBQSxJQUVBLEtBQUs7QUFBQSxNQUNILFNBQVM7QUFBQTtBQUFBLElBQ1g7QUFBQTtBQUFBLElBRUEsc0JBQXNCO0FBQUEsRUFDeEI7QUFBQTtBQUFBLEVBRUEsY0FBYztBQUFBLElBQ1osU0FBUztBQUFBLE1BQ1A7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLElBQ0Y7QUFBQTtBQUFBLElBRUEsU0FBUyxDQUFDO0FBQUE7QUFBQSxJQUVWLE9BQU87QUFBQSxFQUNUO0FBQUE7QUFBQSxFQUVBLE9BQU87QUFBQTtBQUFBLElBRUwsZUFBZTtBQUFBLE1BQ2IsUUFBUTtBQUFBLFFBQ04sY0FBYztBQUFBLFVBQ1osZ0JBQWdCLENBQUMsY0FBYztBQUFBLFVBQy9CLFdBQVcsQ0FBQyxXQUFXLGFBQWE7QUFBQSxVQUNwQyxVQUFVLENBQUMsT0FBTyxjQUFjLE9BQU87QUFBQSxRQUN6QztBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUE7QUFBQSxJQUVBLHVCQUF1QjtBQUFBLEVBQ3pCO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFsicGF0aCJdCn0K
