<template>
  <view class="connection-lines-container">
    <!-- SVG连接线层 -->
    <svg class="svg-layer" :style="svgStyle">
      <!-- 定义箭头标记 -->
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#c8c9cc" />
        </marker>
        <marker
          id="arrowhead-active"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#1989fa" />
        </marker>
      </defs>

      <!-- 静态连接线 -->
      <g v-for="(line, index) in lines" :key="`line-${index}`">
        <!-- 串行连接线 -->
        <path
          v-if="line.type === 'serial'"
          :d="generateSerialPath(line.from, line.to)"
          class="connection-path serial-path"
          marker-end="url(#arrowhead)"
        />
        <!-- 并行分叉线 -->
        <path
          v-else-if="line.type === 'fork'"
          :d="generateForkPath(line.from, line.toList)"
          class="connection-path fork-path"
        />
      </g>

      <!-- 拖拽中的动态连接线 -->
      <path
        v-if="draggingLine"
        :d="generateDraggingPath(draggingLine.from, draggingLine.to)"
        class="connection-path dragging-path"
        marker-end="url(#arrowhead-active)"
      />
    </svg>
  </view>
</template>

<script>
/**
 * 连接线组件
 * @component
 * @description 使用SVG绘制工艺路线节点之间的连接线
 */
export default {
  name: 'ConnectionLines',

  props: {
    /**
     * 已存在的连接线列表
     * @type {Array}
     */
    lines: {
      type: Array,
      default: () => []
    },
    /**
     * 正在拖拽的连接线
     * @type {Object|null}
     */
    draggingLine: {
      type: Object,
      default: null
    },
    /**
     * 容器尺寸
     * @type {Object}
     */
    containerSize: {
      type: Object,
      default: () => ({ width: 0, height: 0 })
    }
  },

  computed: {
    /**
     * SVG样式
     * @returns {Object}
     */
    svgStyle() {
      return {
        width: `${this.containerSize.width}px`,
        height: `${this.containerSize.height}px`
      }
    }
  },

  methods: {
    /**
     * 生成串行连接线路径（垂直直线）
     * @param {Object} from - 起始点 {x, y}
     * @param {Object} to - 终点 {x, y}
     * @returns {string} SVG路径
     */
    generateSerialPath(from, to) {
      if (!from || !to) return ''
      // 垂直直线连接，带箭头
      return `M ${from.x} ${from.y} L ${to.x} ${to.y}`
    },

    /**
     * 生成分叉线路径（并行连接）
     * @param {Object} from - 起始点 {x, y}
     * @param {Array} toList - 终点列表 [{x, y}, ...]
     * @returns {string} SVG路径
     */
    generateForkPath(from, toList) {
      if (!from || !toList || toList.length === 0) return ''

      // 从起点垂直向下一段距离
      const forkY = from.y + 30
      let path = `M ${from.x} ${from.y} L ${from.x} ${forkY}`

      if (toList.length === 1) {
        // 只有一个子节点，直接连接
        path += ` L ${toList[0].x} ${toList[0].y}`
      } else {
        // 多个子节点，绘制分叉
        const minX = Math.min(...toList.map(t => t.x))
        const maxX = Math.max(...toList.map(t => t.x))

        // 水平分叉线
        path += ` M ${minX} ${forkY} L ${maxX} ${forkY}`

        // 从分叉线到各子节点的垂直线
        toList.forEach(to => {
          path += ` M ${to.x} ${forkY} L ${to.x} ${to.y}`
        })
      }

      return path
    },

    /**
     * 生成拖拽中的动态路径
     * @param {Object} from - 起始点 {x, y}
     * @param {Object} to - 终点 {x, y}
     * @returns {string} SVG路径
     */
    generateDraggingPath(from, to) {
      if (!from || !to) return ''

      // 计算控制点，创建平滑的贝塞尔曲线
      const deltaY = to.y - from.y
      const controlY1 = from.y + deltaY * 0.5
      const controlY2 = to.y - deltaY * 0.5

      // 使用三次贝塞尔曲线
      return `M ${from.x} ${from.y} C ${from.x} ${controlY1}, ${to.x} ${controlY2}, ${to.x} ${to.y}`
    }
  }
}
</script>

<style lang="scss" scoped>
.connection-lines-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.svg-layer {
  position: absolute;
  top: 0;
  left: 0;
  overflow: visible;
}

.connection-path {
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;

  &.serial-path {
    stroke: #c8c9cc;
  }

  &.fork-path {
    stroke: #07c160;
  }

  &.dragging-path {
    stroke: #1989fa;
    stroke-width: 3;
    stroke-dasharray: 8, 4;
    animation: dash 1s linear infinite;
  }
}

@keyframes dash {
  to {
    stroke-dashoffset: -12;
  }
}
</style>
