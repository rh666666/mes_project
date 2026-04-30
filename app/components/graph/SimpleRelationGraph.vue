<template>
  <view class="simple-graph">
    <view
      class="simple-graph-viewport"
      :style="viewportStyle"
      @touchstart="onViewportTouchStart"
      @touchmove="onViewportTouchMove"
      @touchend="onViewportTouchEnd"
      @touchcancel="onViewportTouchEnd"
    >
      <view class="simple-graph-stage" :style="stageStyle">
        <view
          v-for="line in renderLines"
          :key="line.id"
        >
          <view
            v-for="segment in line.segments"
            :key="segment.id"
            class="line-hit-area"
            :style="segment.hitStyle"
            @click.stop="handleLineClick(line.raw)"
          >
            <view class="line-core" :style="segment.coreStyle"></view>
          </view>
        </view>
        <view
          v-for="node in renderNodes"
          :key="node.id"
          class="node-wrapper"
          :style="node.style"
          @click.stop="handleNodeClick(node.raw)"
        >
          <slot name="node" :node="node.raw">
            <view class="default-node">{{ node.raw.text || node.id }}</view>
          </slot>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 简易关系图组件（APP 兼容）
 * @component
 * @description 使用绝对定位节点与旋转线段实现基础关系图，避免浏览器 DOM 依赖
 */
export default {
  name: 'SimpleRelationGraph',
  props: {
    /**
     * 关系图数据
     */
    graphData: {
      type: Object,
      default: () => ({ rootId: 'root', nodes: [], lines: [] })
    },
    /**
     * 图配置
     */
    options: {
      type: Object,
      default: () => ({})
    },
    /**
     * 节点点击回调
     */
    onNodeClick: {
      type: Function,
      default: null
    },
    /**
     * 连线点击回调
     */
    onLineClick: {
      type: Function,
      default: null
    }
  },
  data() {
    return {
      localGraphData: { rootId: 'root', nodes: [], lines: [] },
      zoomLevel: 1,
      isPinching: false,
      pinchStartDistance: 0,
      pinchStartZoom: 1,
      pinchEndAt: 0
    }
  },
  computed: {
    /**
     * 画布样式
     * @returns {Object}
     */
    containerStyle() {
      const size = this.options?.canvasSize || {}
      return {
        width: `${size.width || 1200}px`,
        height: `${size.height || 900}px`
      }
    },
    /**
     * 视口样式
     * @returns {Object}
     */
    viewportStyle() {
      return {
        width: '100%',
        height: '100%'
      }
    },
    /**
     * 舞台样式（含缩放）
     * @returns {Object}
     */
    stageStyle() {
      return {
        ...this.containerStyle,
        transform: `scale(${this.zoomLevel})`,
        transformOrigin: '0 0'
      }
    },
    /**
     * 归一化节点
     * @returns {Array}
     */
    renderNodes() {
      const nodeW = this.options?.defaultNodeWidth || 180
      const nodeH = this.options?.defaultNodeHeight || 84
      return (this.localGraphData.nodes || []).map((node, index) => {
        const nx = typeof node.x === 'number' ? node.x : 60 + (index % 4) * 220
        const ny = typeof node.y === 'number' ? node.y : 60 + Math.floor(index / 4) * 140
        return {
          id: node.id,
          raw: node,
          x: nx,
          y: ny,
          width: node.width || nodeW,
          height: node.height || nodeH,
          style: {
            left: `${nx}px`,
            top: `${ny}px`,
            width: `${node.width || nodeW}px`,
            height: `${node.height || nodeH}px`
          }
        }
      })
    },
    /**
     * 节点坐标索引
     * @returns {Object<string, Object>}
     */
    nodeMap() {
      const out = {}
      this.renderNodes.forEach((node) => {
        out[node.id] = node
      })
      return out
    },
    /**
     * 连线渲染数据
     * @returns {Array}
     */
    renderLines() {
      const lines = this.localGraphData.lines || []
      const splitLevelMap = this.buildSourceSplitLevelMap(lines)
      return lines.map((line, index) => {
        const fromNode = this.nodeMap[line.from]
        const toNode = this.nodeMap[line.to]
        if (!fromNode || !toNode) {
          return {
            id: `line-${index}`,
            raw: line,
            segments: []
          }
        }
        const x1 = fromNode.x + fromNode.width / 2
        const y1 = fromNode.y + fromNode.height / 2
        const x2 = toNode.x + toNode.width / 2
        const y2 = toNode.y + toNode.height / 2
        const preferredSplitY = splitLevelMap[line.from]
        return {
          id: `line-${line.from}-${line.to}-${index}`,
          raw: line,
          segments: this.buildOrthogonalSegments(x1, y1, x2, y2, `${line.from}-${line.to}-${index}`, preferredSplitY)
        }
      })
    }
  },
  watch: {
    /**
     * 监听外部图数据变化
     */
    graphData: {
      immediate: true,
      deep: true,
      handler(value) {
        this.localGraphData = this.cloneGraph(value)
      }
    }
  },
  methods: {
    /**
     * 深拷贝图数据
     * @param {Object} value
     * @returns {Object}
     */
    cloneGraph(value) {
      if (!value) return { rootId: 'root', nodes: [], lines: [] }
      return JSON.parse(JSON.stringify(value))
    },
    /**
     * 构建水平线段点击区域与可视线条
     * @param {number} x1 - 起点 x
     * @param {number} x2 - 终点 x
     * @param {number} y - 水平线 y
     * @param {string} id - 线段 ID
     * @returns {Object}
     */
    createHorizontalSegment(x1, x2, y, id) {
      const left = Math.min(x1, x2)
      const width = Math.max(1, Math.abs(x2 - x1))
      return {
        id,
        hitStyle: {
          left: `${left}px`,
          top: `${y - 12}px`,
          width: `${width}px`,
          height: '24px'
        },
        coreStyle: {
          left: '0',
          top: '11px',
          width: `${width}px`,
          height: '2px'
        }
      }
    },
    /**
     * 构建垂直线段点击区域与可视线条
     * @param {number} x - 垂直线 x
     * @param {number} y1 - 起点 y
     * @param {number} y2 - 终点 y
     * @param {string} id - 线段 ID
     * @returns {Object}
     */
    createVerticalSegment(x, y1, y2, id) {
      const top = Math.min(y1, y2)
      const height = Math.max(1, Math.abs(y2 - y1))
      return {
        id,
        hitStyle: {
          left: `${x - 12}px`,
          top: `${top}px`,
          width: '24px',
          height: `${height}px`
        },
        coreStyle: {
          left: '11px',
          top: '0',
          width: '2px',
          height: `${height}px`
        }
      }
    },
    /**
     * 为每个出边数量大于 1 的源节点计算共享分叉层（Y 坐标）
     * @param {Array<{from: string, to: string}>} lines - 连线列表
     * @returns {Object<string, number>}
     */
    buildSourceSplitLevelMap(lines) {
      const groups = {}
      lines.forEach((line) => {
        if (!line?.from || !line?.to) {
          return
        }
        if (!groups[line.from]) {
          groups[line.from] = []
        }
        groups[line.from].push(line)
      })
      const out = {}
      Object.keys(groups).forEach((fromId) => {
        const fromNode = this.nodeMap[fromId]
        const group = groups[fromId]
        if (!fromNode || group.length < 2) {
          return
        }
        const fromCenterY = fromNode.y + fromNode.height / 2
        const targetCenterYs = group
          .map((line) => this.nodeMap[line.to])
          .filter(Boolean)
          .map((node) => node.y + node.height / 2)
        if (!targetCenterYs.length) {
          return
        }
        const deltas = targetCenterYs.map(y => y - fromCenterY)
        const meanDelta = deltas.reduce((sum, value) => sum + value, 0) / deltas.length
        const dir = meanDelta >= 0 ? 1 : -1
        const fromAnchorY = dir > 0 ? fromNode.y + fromNode.height : fromNode.y
        const targetAnchorYs = group
          .map((line) => this.nodeMap[line.to])
          .filter(Boolean)
          .map((node) => (dir > 0 ? node.y : node.y + node.height))
        if (!targetAnchorYs.length) {
          return
        }
        const nearestTargetAnchorY = dir > 0
          ? Math.min(...targetAnchorYs)
          : Math.max(...targetAnchorYs)
        const rawGap = Math.abs(nearestTargetAnchorY - fromAnchorY)
        if (rawGap < 2) {
          out[fromId] = Math.round(fromAnchorY)
          return
        }
        // 分叉层放在父锚点与最近子锚点中点，保证上下间距对等，同时设置最小留白避免贴边
        const halfGap = rawGap / 2
        const minEdgeGap = 18
        const step = Math.max(minEdgeGap, Math.round(halfGap))
        out[fromId] = Math.round(fromAnchorY + dir * step)
      })
      return out
    },
    /**
     * 构建正交连线（仅水平/竖直线段）
     * @param {number} x1 - 起点 x
     * @param {number} y1 - 起点 y
     * @param {number} x2 - 终点 x
     * @param {number} y2 - 终点 y
     * @param {string} baseId - 线段 ID 前缀
     * @param {number} [preferredSplitY] - 可选的共享分叉层 Y 坐标
     * @returns {Array<Object>}
     */
    buildOrthogonalSegments(x1, y1, x2, y2, baseId, preferredSplitY) {
      if (Math.abs(y2 - y1) < 1) {
        return [this.createHorizontalSegment(x1, x2, y1, `${baseId}-h-0`)]
      }
      if (Math.abs(x2 - x1) < 1) {
        return [this.createVerticalSegment(x1, y1, y2, `${baseId}-v-0`)]
      }
      const fallbackMidY = Math.round((y1 + y2) / 2)
      let midY = Number.isFinite(preferredSplitY) ? Math.round(preferredSplitY) : fallbackMidY
      const minY = Math.min(y1, y2) + 4
      const maxY = Math.max(y1, y2) - 4
      if (minY <= maxY) {
        midY = Math.max(minY, Math.min(maxY, midY))
      }
      return [
        this.createVerticalSegment(x1, y1, midY, `${baseId}-v-1`),
        this.createHorizontalSegment(x1, x2, midY, `${baseId}-h-2`),
        this.createVerticalSegment(x2, midY, y2, `${baseId}-v-3`)
      ]
    },
    /**
     * 对外兼容方法：设置图数据
     * @param {Object} value
     * @param {boolean} _animate
     * @param {Function} callback
     */
    setJsonData(value, _animate, callback) {
      this.localGraphData = this.cloneGraph(value)
      this.$nextTick(() => {
        if (typeof callback === 'function') callback()
      })
    },
    /**
     * 对外兼容方法：返回图实例能力
     * @returns {Object}
     */
    getInstance() {
      return {
        options: this.options || {},
        getNodes: () =>
          this.renderNodes.map(node => ({
            id: node.id,
            x: node.x,
            y: node.y,
            width: node.width,
            height: node.height
          })),
        setNodePosition: (targetNode, x, y) => {
          const node = (this.localGraphData.nodes || []).find(item => item.id === targetNode.id)
          if (node) {
            node.x = x
            node.y = y
          }
        },
        updateElementLines: () => {},
        _dataUpdated: () => {},
        resetViewSize: () => {},
        moveToCenter: () => {},
        zoomToFit: () => {
          this.zoomToFit()
        },
        getZoom: () => this.zoomLevel,
        setZoom: (zoom) => {
          this.setZoom(zoom)
        }
      }
    },
    /**
     * 设置缩放比例
     * @param {number} zoom - 缩放值
     */
    setZoom(zoom) {
      const numeric = Number(zoom)
      if (!Number.isFinite(numeric)) {
        return
      }
      this.zoomLevel = Math.max(0.3, Math.min(2.5, Number(numeric.toFixed(3))))
    },
    /**
     * 计算双指距离
     * @param {Array} touches - 触点数组
     * @returns {number}
     */
    getPinchDistance(touches) {
      if (!touches || touches.length < 2) {
        return 0
      }
      const [a, b] = touches
      const dx = (b.clientX || 0) - (a.clientX || 0)
      const dy = (b.clientY || 0) - (a.clientY || 0)
      return Math.sqrt(dx * dx + dy * dy)
    },
    /**
     * 触摸开始：双指时进入捏合模式
     * @param {Object} event - 触摸事件
     */
    onViewportTouchStart(event) {
      const touches = event?.touches || []
      if (touches.length < 2) {
        return
      }
      const distance = this.getPinchDistance(touches)
      if (distance <= 0) {
        return
      }
      this.isPinching = true
      this.pinchStartDistance = distance
      this.pinchStartZoom = this.zoomLevel
    },
    /**
     * 触摸移动：根据双指间距实时缩放
     * @param {Object} event - 触摸事件
     */
    onViewportTouchMove(event) {
      const touches = event?.touches || []
      if (!this.isPinching || touches.length < 2 || this.pinchStartDistance <= 0) {
        return
      }
      const currentDistance = this.getPinchDistance(touches)
      if (currentDistance <= 0) {
        return
      }
      const scale = currentDistance / this.pinchStartDistance
      this.setZoom(this.pinchStartZoom * scale)
    },
    /**
     * 触摸结束：退出捏合模式并记录结束时间
     */
    onViewportTouchEnd() {
      if (!this.isPinching) {
        return
      }
      this.isPinching = false
      this.pinchStartDistance = 0
      this.pinchStartZoom = this.zoomLevel
      this.pinchEndAt = Date.now()
    },
    /**
     * 按视口自适应缩放
     */
    zoomToFit() {
      const canvas = this.options?.canvasSize || {}
      const stageWidth = Number(canvas.width) || 1200
      const stageHeight = Number(canvas.height) || 900
      const viewportWidth = this.$el?.clientWidth || stageWidth
      const viewportHeight = this.$el?.clientHeight || stageHeight
      const fit = Math.min(viewportWidth / stageWidth, viewportHeight / stageHeight)
      this.zoomLevel = Math.max(0.3, Math.min(1.2, Number(fit.toFixed(3))))
    },
    /**
     * 节点点击
     * @param {Object} node
     */
    handleNodeClick(node) {
      if (Date.now() - this.pinchEndAt < 160) {
        return
      }
      if (typeof this.onNodeClick === 'function') {
        this.onNodeClick(node)
      }
    },
    /**
     * 连线点击
     * @param {Object} line
     */
    handleLineClick(line) {
      if (Date.now() - this.pinchEndAt < 160) {
        return
      }
      if (typeof this.onLineClick === 'function') {
        this.onLineClick(line)
      }
    }
  }
}
</script>

<style scoped lang="scss">
.simple-graph {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #fff;
}

.simple-graph-viewport {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.simple-graph-stage {
  position: relative;
}

.line-hit-area {
  position: absolute;
  z-index: 20;
}

.line-core {
  position: absolute;
  background: #c8c9cc;
}

.node-wrapper {
  position: absolute;
  z-index: 30;
}

.default-node {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #1989fa;
  border-radius: 8px;
  background: #fff;
  color: #303133;
  font-size: 12px;
  box-sizing: border-box;
}
</style>
