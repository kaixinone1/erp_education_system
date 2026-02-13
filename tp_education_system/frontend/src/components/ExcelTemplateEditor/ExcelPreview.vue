<template>
  <div class="excel-preview-wrapper">
    <!-- 工具栏 -->
    <div class="preview-toolbar">
      <div class="zoom-controls">
        <el-button size="small" @click="zoomOut">
          <el-icon><ZoomOut /></el-icon>
        </el-button>
        <span class="zoom-value">{{ Math.round(zoom * 100) }}%</span>
        <el-button size="small" @click="zoomIn">
          <el-icon><ZoomIn /></el-icon>
        </el-button>
        <el-button size="small" @click="fitToWidth">
          适应宽度
        </el-button>
        <el-button size="small" @click="resetZoom">
          100%
        </el-button>
      </div>
      <div class="info">
        <span v-if="sheetInfo">{{ sheetInfo }}</span>
      </div>
    </div>

    <!-- 预览区域 -->
    <div class="preview-scroll-area" ref="scrollAreaRef">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div 
        v-else 
        class="excel-sheet-container"
        :style="containerStyle"
      >
        <table 
          class="excel-table" 
          :style="tableStyle"
          ref="tableRef"
        >
          <colgroup>
            <col 
              v-for="(width, index) in columnWidths" 
              :key="index" 
              :style="{ width: (width * zoom) + 'px' }"
            />
          </colgroup>
          <tbody>
            <tr 
              v-for="(row, rowIndex) in displayData" 
              :key="rowIndex"
              :style="{ height: (rowHeights[rowIndex] * zoom) + 'px' }"
            >
              <td
                v-for="(cell, colIndex) in row"
                :key="colIndex"
                class="excel-cell"
                :class="{
                  'merged': isMergedCell(rowIndex, colIndex),
                  'marked': isMarkedCell(rowIndex, colIndex),
                  'selected': isSelectedCell(rowIndex, colIndex)
                }"
                :style="getCellStyle(rowIndex, colIndex)"
                :colspan="getColSpan(rowIndex, colIndex)"
                :rowspan="getRowSpan(rowIndex, colIndex)"
                @click="handleCellClick(rowIndex