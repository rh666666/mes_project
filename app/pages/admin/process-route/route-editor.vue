<template>
  <view class="page">
    <!-- 工艺路线信息卡片 -->
    <view class="route-info-card">
      <view class="route-info-header">
        <view class="route-info-title">
          <text class="material-name">{{ routeInfo.material_name || '加载中...' }}</text>
          <wd-tag type="primary" size="small">{{ routeInfo.version || '-' }}</wd-tag>
        </view>
        <wd-button type="info" size="small" plain @click="onEditBaseInfo">
          编辑基础信息
        </wd-button>
      </view>
      <text v-if="routeInfo.description" class="route-description">{{ routeInfo.description }}</text>
    </view>

    <!-- 节点图编辑区域 -->
    <scroll-view
      scroll-y
      class="node-editor"
      :scroll-left="editorScrollLeft"
      :scroll-top="editorScrollTop"
      scroll-with-animation="false"
    >
      <view
        class="node-tree-wrapper"
        :style="{ minHeight: `${graphViewportHRpx}rpx` }"
      >
        <view class="gesture-tip">
          <text>{{ gestureTipText }}</text>
        </view>
        <RelationGraph
          ref="relationGraphRef"
          :options="graphOptions"
          :on-node-click="onGraphNodeClick"
          :on-line-click="onGraphLineClick"
          class="relation-graph"
          :style="{ width: '100%', height: `${graphViewportHRpx}rpx` }"
        >
          <template #node="{ node }">
            <view class="rg-node-card" :class="{ 'rg-node-root': node.id === 'root' }">
              <text class="rg-node-title">{{ node.text || '点击选择工序' }}</text>
              <text v-if="node.id !== 'root'" class="rg-node-subtitle">
                {{ (node.data && node.data.processCode) || '未选择工序编码' }}
              </text>
            </view>
          </template>
        </RelationGraph>
      </view>

      <wd-status-tip v-if="graphData.nodes.length <= 1" image="search" tip="暂无工序，请先添加节点" />
    </scroll-view>

    <!-- 悬浮保存按钮 -->
    <view v-if="!showProcessSelector" class="save-fab">
      <wd-button type="primary" round :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中' : '保存' }}
      </wd-button>
    </view>

    <!-- 选择工序弹窗 -->
    <wd-popup v-model="showProcessSelector" position="bottom" :style="{ height: '70%' }">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">选择工序</text>
          <wd-icon name="close" size="20" @click="showProcessSelector = false" />
        </view>
        <view class="popup-body">
          <SearchableSelector
            v-model="selectedProcessId"
            label="工序"
            placeholder="搜索工序名称或编码"
            search-key="name"
            :fetch-api="processApi.getProcessList"
            title-field="name"
            subtitle-field="code"
            :required="true"
            @select="onProcessSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" @click="onConfirmSelectProcess">
            确认
          </wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 加载状态 -->
    <view v-if="isLoading" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import dagre from 'dagre'
import processRouteApi from '@/api/process-route.js'
import processApi from '@/api/process.js'
import RelationGraph from 'relation-graph/vue3'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * 工艺路线节点图编辑页面
 * @component
 * @description 使用纵向节点图编辑工艺路线的工序流程，支持串行和并行，支持拖拽连接；无环拓扑采用 Dagre 分层布局（adoleiiiiii）
 */
export default {
  name: 'ProcessRouteEditor',
  components: {
    RelationGraph,
    SearchableSelector
  },
  data() {
    return {
      routeId: null,
      routeInfo: {},
      isLoading: false,
      isRefreshing: false,
      isSaving: false,
      showProcessSelector: false,
      selectedProcessId: null,
      selectedProcess: null,
      editingNode: null,
      processApi,
      nodeIdCounter: 0,
      selectedNodeId: 'root',
      isConnecting: false,
      pendingFromNodeId: '',
      graphViewportHRpx: 780,
      hasInitializedViewport: false,
      editorScrollLeft: 0,
      editorScrollTop: 0,
      relationGraphRef: null,
      graphData: {
        rootId: 'root',
        nodes: [{ id: 'root', text: '工艺路线起点', data: { processId: null, nodeKey: 'root' } }],
        lines: []
      },
      graphOptions: {
        allowSwitchLineShape: false,
        allowSwitchJunctionPoint: false,
        allowShowMiniToolBar: false,
        allowShowRefreshButton: false,
        defaultNodeBorderColor: '#1989fa',
        defaultNodeColor: '#ffffff',
        defaultNodeFontColor: '#303133',
        defaultNodeShape: 1,
        defaultNodeWidth: 180,
        defaultNodeHeight: 84,
        defaultLineColor: '#c8c9cc',
        defaultLineWidth: 1,
        // 使用直线形态，避免视觉上出现“歪线”
        defaultLineShape: 4,
        defaultShowLineLabel: false,
        defaultJunctionPoint: 'tb',
        disableDragCanvas: false,
        disableDragNode: false,
        disableZoom: false,
        moveToCenterWhenRefresh: false,
        zoomToFitWhenRefresh: false,
        debug: false,
        // 默认可用 Dagre+fixed；存在有向环时 syncGraphLayoutStrategy 会回退为树布局
        layout: {
          layoutName: 'fixed'
        }
      }
    }
  },
  computed: {
    /**
     * 手势提示文案
     * @returns {string}
     */
    gestureTipText() {
      if (this.isConnecting) {
        return '连线模式：点目标节点完成连线'
      }
      return '点击节点可操作'
    }
  },
  onLoad(options) {
    this.updateGraphViewportSize()
    if (options.id) {
      this.routeId = parseInt(options.id)
      this.loadRouteData()
    }
    this.updateContainerSize()
  },
  onShow() {
    this.updateGraphViewportSize()
    this.$nextTick(() => {
      this.applyZoomToFitEntireGraph()
    })
  },
  methods: {
    /**
     * 更新容器尺寸
     */
    updateContainerSize() {
      this.updateGraphViewportSize()
    },
    /**
     * 关系图区域使用屏幕内固定视口（rpx），实际拓扑再宽再高也由 relation-graph 缩放到该区域内完整显示
     */
    updateGraphViewportSize() {
      const sys = uni.getSystemInfoSync()
      const winW = sys.windowWidth || 375
      const winH = sys.windowHeight || 667
      const topReservedPx = uni.upx2px(420)
      const bottomReservedPx = uni.upx2px(320) + (sys.safeAreaInsets?.bottom || 0)
      const availPx = Math.max(240, winH - topReservedPx - bottomReservedPx)
      let heightRpx = Math.round((availPx * 750) / winW)
      heightRpx = Math.min(1200, Math.max(520, heightRpx))
      this.graphViewportHRpx = heightRpx
    },
    /**
     * 加载工艺路线数据
     */
    async loadRouteData() {
      this.isLoading = true
      this.hasInitializedViewport = false
      try {
        const [routeRes, detailsRes] = await Promise.all([
          processRouteApi.getProcessRouteDetail(this.routeId),
          processRouteApi.getProcessRouteGraph(this.routeId)
        ])
        if (routeRes.code === 2000) {
          this.routeInfo = routeRes.data
        }
        if (detailsRes.code === 2000) {
          const graphPayload = detailsRes.data || {}
          this.graphData = this.buildGraphData(graphPayload)
          this.updateCanvasSizeByGraph()
          this.selectedNodeId = 'root'
          this.refreshGraph({ fitToView: true })
        }
      } catch (error) {
        console.error('加载工艺路线数据失败:', error)
        uni.showToast({ title: '加载数据失败', icon: 'none' })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
      }
    },
    /**
     * 构建图谱数据（后端 nodes + edges）
     * @param {Object} payload - 工艺路线图数据
     * @returns {Object}
     */
    buildGraphData(payload) {
      this.nodeIdCounter = 0
      const graph = {
        rootId: 'root',
        nodes: [{ id: 'root', text: '工艺路线起点', data: { processId: null, nodeKey: 'root' } }],
        lines: []
      }
      const nodes = payload.nodes || []
      const edges = payload.edges || []
      if (!nodes.length) return graph

      const keyToIdMap = { root: 'root' }
      nodes.forEach((node) => {
        const nodeId = node.node_key
        keyToIdMap[node.node_key] = nodeId
        graph.nodes.push({
          id: nodeId,
          text: node.process_name || '未命名工序',
          data: {
            processId: node.process,
            processCode: node.process_code,
            nodeKey: node.node_key,
            bomId: node.process_bom || null
          }
        })
      })

      const hasIncoming = new Set(edges.map(edge => edge.to_node_key))
      const startNodeKeys = nodes.filter(node => !hasIncoming.has(node.node_key)).map(node => node.node_key)
      startNodeKeys.forEach((nodeKey) => {
        graph.lines.push({ from: 'root', to: keyToIdMap[nodeKey] })
      })
      edges.forEach((edge) => {
        if (keyToIdMap[edge.from_node_key] && keyToIdMap[edge.to_node_key]) {
          graph.lines.push({ from: keyToIdMap[edge.from_node_key], to: keyToIdMap[edge.to_node_key] })
        }
      })

      return graph
    },
    /**
     * 创建空图节点
     * @returns {Object}
     */
    createNewNode() {
      this.nodeIdCounter++
      return {
        id: `draft-node-${Date.now()}-${this.nodeIdCounter}`,
        text: '点击选择工序',
        data: {
          processId: null,
          processCode: '',
          nodeKey: `node-${Date.now()}-${this.nodeIdCounter}`,
          bomId: null
        }
      }
    },
    /**
     * 按节点宽度同步树布局的横向 min/max_per_width，保证并行时 u 不会被夹得过窄
     * @param {number} maxFanout 单父节点最大子节点数
     * @param {number} maxBreadth 单层最大节点数（BFS）
     */
    syncTreeLayoutGapsFromGraph(maxFanout, maxBreadth) {
      const layout = this.graphOptions.layout || {}
      if (layout.layoutName !== 'tree') {
        return
      }
      const nodeW = this.graphOptions.defaultNodeWidth || 180
      const gap = Math.max(48, Math.round(nodeW * 0.32))
      const minUnit = nodeW + gap
      const spread = Math.max(1, maxBreadth, maxFanout)
      layout.min_per_width = minUnit
      layout.max_per_width = Math.max(Math.round(minUnit * 2.2), minUnit + spread * 24)
    },
    /**
     * 判断当前连线是否存在有向环（Dagre 仅支持 DAG）
     * @returns {boolean}
     */
    graphDataHasDirectedCycle() {
      const lines = this.graphData.lines || []
      const adj = {}
      const ids = new Set()
      lines.forEach((line) => {
        if (!line.from || !line.to) {
          return
        }
        ids.add(line.from)
        ids.add(line.to)
        if (!adj[line.from]) {
          adj[line.from] = []
        }
        adj[line.from].push(line.to)
      })
      const visited = new Set()
      const stack = new Set()
      const dfs = (u) => {
        if (stack.has(u)) {
          return true
        }
        if (visited.has(u)) {
          return false
        }
        visited.add(u)
        stack.add(u)
        for (const v of adj[u] || []) {
          if (dfs(v)) {
            return true
          }
        }
        stack.delete(u)
        return false
      }
      for (const id of ids) {
        if (!visited.has(id) && dfs(id)) {
          return true
        }
      }
      return false
    },
    /**
     * 去掉节点上的布局坐标，便于切换为 relation-graph 内置树布局
     */
    clearNodeLayoutCoords() {
      const nodes = this.graphData.nodes || []
      nodes.forEach((node) => {
        delete node.x
        delete node.y
        delete node.width
        delete node.height
      })
    },
    /**
     * 无环时使用 Dagre 计算节点 x/y（relation-graph 中为左上角），并写入 graphData.nodes
     * Dagre 输出为节点中心坐标，此处换算为与 fixed 布局一致的左上角
     * @returns {boolean} 是否成功写入坐标
     */
    applyDagreLayoutToGraphData() {
      const nodes = this.graphData.nodes || []
      const lines = this.graphData.lines || []
      if (nodes.length <= 1 || lines.length === 0) {
        this.resetRelationGraphCanvasSizeDefault()
        return true
      }
      const nodeW = this.graphOptions.defaultNodeWidth || 180
      const nodeH = this.graphOptions.defaultNodeHeight || 84
      const g = new dagre.graphlib.Graph({ multigraph: false, compound: false })
      g.setGraph({
        rankdir: 'TB',
        nodesep: Math.max(40, Math.round(nodeW * 0.28)),
        ranksep: Math.max(56, Math.round(nodeH * 0.85)),
        marginx: 24,
        marginy: 24,
        edgesep: 20
      })
      g.setDefaultEdgeLabel(() => ({}))
      nodes.forEach((n) => {
        g.setNode(n.id, { width: nodeW, height: nodeH })
      })
      const edgeSeen = new Set()
      lines.forEach((line) => {
        if (!line.from || !line.to || !g.hasNode(line.from) || !g.hasNode(line.to)) {
          return
        }
        const key = `${line.from}->${line.to}`
        if (edgeSeen.has(key)) {
          return
        }
        edgeSeen.add(key)
        g.setEdge(line.from, line.to)
      })
      try {
        dagre.layout(g)
      } catch (error) {
        console.error('Dagre layout failed:', error)
        return false
      }
      nodes.forEach((n) => {
        const pos = g.node(n.id)
        if (!pos) {
          return
        }
        n.x = Math.round(pos.x - nodeW / 2)
        n.y = Math.round(pos.y - nodeH / 2)
        n.width = nodeW
        n.height = nodeH
      })
      this.padDagreLayoutAndSetIntrinsicCanvasSize(nodes, nodeW, nodeH)
      return true
    },
    /**
     * Dagre 结果先整体平移到正象限留白边，并按包围盒设置 canvasSize（与组件真实 viewSize 无关）。
     * 与视口对齐在 resetViewSize 之后由 recenterFixedLayoutToDomViewport 用 $dom 量到的尺寸完成。
     */
    padDagreLayoutAndSetIntrinsicCanvasSize(nodes, nodeW, nodeH) {
      const pad = 64
      let minX = Infinity
      let minY = Infinity
      let maxX = -Infinity
      let maxY = -Infinity
      nodes.forEach((n) => {
        if (typeof n.x !== 'number' || typeof n.y !== 'number') {
          return
        }
        const w = n.width != null ? n.width : nodeW
        const h = n.height != null ? n.height : nodeH
        minX = Math.min(minX, n.x)
        minY = Math.min(minY, n.y)
        maxX = Math.max(maxX, n.x + w)
        maxY = Math.max(maxY, n.y + h)
      })
      if (!Number.isFinite(minX) || !Number.isFinite(minY)) {
        return
      }
      const dx = pad - minX
      const dy = pad - minY
      nodes.forEach((n) => {
        if (typeof n.x === 'number' && typeof n.y === 'number') {
          n.x = Math.round(n.x + dx)
          n.y = Math.round(n.y + dy)
        }
      })
      const bw = Math.ceil(maxX - minX + pad * 2)
      const bh = Math.ceil(maxY - minY + pad * 2)
      this.graphOptions.canvasSize = {
        width: Math.max(320, bw),
        height: Math.max(280, bh)
      }
    },
    /**
     * fixed 布局下用 relation-graph 实例量到的 viewSize 与节点包围盒对齐（移动端/H5 与 windowWidth 常不一致）
     */
    recenterFixedLayoutToDomViewport(graphInstance) {
      const gi = graphInstance
      if (!gi || this.graphOptions.layout?.layoutName !== 'fixed') {
        return
      }
      const opts = gi.options || {}
      const vw = Math.floor(opts.viewSize?.width || 0)
      const vh = Math.floor(opts.viewSize?.height || 0)
      if (vw < 80 || vh < 80) {
        return
      }
      const nodeW = opts.defaultNodeWidth || 180
      const nodeH = opts.defaultNodeHeight || 84
      const rgNodes = typeof gi.getNodes === 'function' ? gi.getNodes() : []
      if (!rgNodes.length) {
        return
      }
      let minX = Infinity
      let minY = Infinity
      let maxX = -Infinity
      let maxY = -Infinity
      rgNodes.forEach((n) => {
        const ew = n.el && n.el.offsetWidth > 0 ? n.el.offsetWidth : null
        const eh = n.el && n.el.offsetHeight > 0 ? n.el.offsetHeight : null
        const w = ew || n.width || nodeW
        const h = eh || n.height || nodeH
        const nx = n.x || 0
        const ny = n.y || 0
        minX = Math.min(minX, nx)
        minY = Math.min(minY, ny)
        maxX = Math.max(maxX, nx + w)
        maxY = Math.max(maxY, ny + h)
      })
      if (!Number.isFinite(minX)) {
        return
      }
      const bw = maxX - minX
      const bh = maxY - minY
      const canvasW = Math.max(vw, Math.ceil(bw + 48))
      const canvasH = Math.max(vh, Math.ceil(bh + 48))
      opts.canvasSize = { width: canvasW, height: canvasH }
      const cx = (minX + maxX) / 2
      const cy = (minY + maxY) / 2
      const dx = canvasW / 2 - cx
      const dy = canvasH / 2 - cy
      if (Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5) {
        return
      }
      rgNodes.forEach((n) => {
        if (typeof gi.setNodePosition === 'function') {
          gi.setNodePosition(n, (n.x || 0) + dx, (n.y || 0) + dy)
        } else {
          n.x = (n.x || 0) + dx
          n.y = (n.y || 0) + dy
        }
      })
      this.syncGraphDataNodeCoordsFromRgNodes(rgNodes)
      if (typeof gi.updateElementLines === 'function') {
        gi.updateElementLines()
      }
      if (typeof gi._dataUpdated === 'function') {
        gi._dataUpdated()
      }
    },
    /**
     * 将 relation-graph 实例中的节点坐标写回 this.graphData（保存与下次刷新一致）
     */
    syncGraphDataNodeCoordsFromRgNodes(rgNodes) {
      const byId = new Map((this.graphData.nodes || []).map((n) => [n.id, n]))
      rgNodes.forEach((rn) => {
        const jn = byId.get(rn.id)
        if (jn) {
          jn.x = rn.x
          jn.y = rn.y
        }
      })
    },
    /**
     * 恢复 relation-graph 默认画布尺寸（树布局依赖内置扩展逻辑）
     */
    resetRelationGraphCanvasSizeDefault() {
      this.graphOptions.canvasSize = { width: 10, height: 10 }
    },
    /**
     * 刷新前同步布局策略：DAG 用 Dagre+fixed；含环则回退树布局并清理坐标
     */
    syncGraphLayoutStrategy() {
      if (this.graphDataHasDirectedCycle()) {
        this.clearNodeLayoutCoords()
        this.resetRelationGraphCanvasSizeDefault()
        this.graphOptions.layout = {
          layoutName: 'tree',
          from: 'top',
          levelDistance: '140',
          fixedRootNode: true,
          min_per_width: 260,
          max_per_width: 560
        }
        this.updateCanvasSizeByGraph()
        return
      }
      this.graphOptions.layout = {
        layoutName: 'fixed'
      }
      if (!this.applyDagreLayoutToGraphData()) {
        this.clearNodeLayoutCoords()
        this.resetRelationGraphCanvasSizeDefault()
        this.graphOptions.layout = {
          layoutName: 'tree',
          from: 'top',
          levelDistance: '140',
          fixedRootNode: true,
          min_per_width: 260,
          max_per_width: 560
        }
        this.updateCanvasSizeByGraph()
      }
    },
    /**
     * 根据图拓扑同步树布局横向间距；图形容器尺寸固定为视口，由 applyZoomToFitEntireGraph 整体缩放适配
     */
    updateCanvasSizeByGraph() {
      const lines = this.graphData.lines || []
      const nodes = this.graphData.nodes || []
      const childrenMap = {}
      lines.forEach((line) => {
        if (!childrenMap[line.from]) {
          childrenMap[line.from] = []
        }
        childrenMap[line.from].push(line.to)
      })
      let maxFanout = 1
      Object.keys(childrenMap).forEach((fromId) => {
        const n = childrenMap[fromId].length
        if (n > maxFanout) {
          maxFanout = n
        }
      })
      const queue = [{ id: 'root', depth: 0 }]
      const visited = new Set()
      const depthCount = {}
      while (queue.length > 0) {
        const current = queue.shift()
        if (visited.has(current.id)) continue
        visited.add(current.id)
        depthCount[current.depth] = (depthCount[current.depth] || 0) + 1
        const children = childrenMap[current.id] || []
        children.forEach((childId) => queue.push({ id: childId, depth: current.depth + 1 }))
      }
      const maxBreadth = Math.max(...Object.values(depthCount), 1)
      const breadthForLayout = visited.size < nodes.length ? Math.max(maxBreadth, 3) : maxBreadth
      const fanoutForLayout = visited.size < nodes.length ? Math.max(maxFanout, 2) : maxFanout
      this.syncTreeLayoutGapsFromGraph(fanoutForLayout, breadthForLayout)
    },
    onRefresh() {
      this.isRefreshing = true
      this.loadRouteData()
    },
    /**
     * 图节点点击事件
     * @param {Object} node - 关系图节点
     */
    onGraphNodeClick(node) {
      if (this.isConnecting) {
        this.onConnectNodeTarget(node)
        return
      }
      this.selectedNodeId = node.id
      this.editingNode = node
      if (node.id !== 'root') {
        this.selectedProcessId = node.data?.processId || null
      }
      this.showNodeActionSheet(node)
    },
    /**
     * 图连线点击事件
     * @param {Object} line - 连线对象
     */
    onGraphLineClick(line) {
      const fromId = line?.from || line?.fromNode || line?.fromNodeId || ''
      const toId = line?.to || line?.toNode || line?.toNodeId || ''
      if (!fromId || !toId) {
        return
      }
      if (fromId === 'root') {
        uni.showToast({ title: '起点连线不可删除', icon: 'none' })
        return
      }
      uni.showActionSheet({
        itemList: ['删除连线'],
        success: ({ tapIndex }) => {
          if (tapIndex === 0) {
            this.deleteLine(fromId, toId)
          }
        }
      })
    },
    /**
     * 删除连线
     * @param {string} fromId - 起点节点ID
     * @param {string} toId - 终点节点ID
     */
    deleteLine(fromId, toId) {
      const beforeCount = this.graphData.lines.length
      this.graphData.lines = this.graphData.lines.filter(line => !(line.from === fromId && line.to === toId))
      if (this.graphData.lines.length === beforeCount) {
        uni.showToast({ title: '未找到连线', icon: 'none' })
        return
      }
      this.updateCanvasSizeByGraph()
      this.refreshGraph()
      uni.showToast({ title: '连线已删除', icon: 'success' })
    },
    /**
     * 节点操作菜单
     * @param {Object} node - 节点对象
     */
    showNodeActionSheet(node) {
      const isRoot = node.id === 'root'
      const itemList = isRoot
        ? ['串行新增']
        : ['选择工序', '串行新增', '并行新增', this.isConnecting ? '取消连线模式' : '从当前节点开始连线', '删除节点']
      uni.showActionSheet({
        itemList,
        success: ({ tapIndex }) => {
          if (isRoot) {
            if (tapIndex === 0) this.onAddSerialNode()
            return
          }
          if (tapIndex === 0) this.onSelectCurrentNodeProcess()
          if (tapIndex === 1) this.onAddSerialNode()
          if (tapIndex === 2) this.onAddParallelNode()
          if (tapIndex === 3) {
            if (this.isConnecting) {
              this.cancelConnectMode()
            } else {
              this.startConnectMode(node.id)
            }
          }
          if (tapIndex === 4) this.onDeleteCurrentNode()
        }
      })
    },
    /**
     * 开始连线模式
     * @param {string} fromNodeId - 起点节点ID
     */
    startConnectMode(fromNodeId) {
      if (!fromNodeId || fromNodeId === 'root') {
        uni.showToast({ title: '请选择有效起点节点', icon: 'none' })
        return
      }
      this.isConnecting = true
      this.pendingFromNodeId = fromNodeId
      this.selectedNodeId = fromNodeId
      uni.showToast({ title: '已进入连线模式', icon: 'none' })
    },
    /**
     * 取消连线模式
     */
    cancelConnectMode() {
      this.isConnecting = false
      this.pendingFromNodeId = ''
      uni.showToast({ title: '已取消连线模式', icon: 'none' })
    },
    /**
     * 连线模式下点击目标节点
     * @param {Object} targetNode - 目标节点
     */
    onConnectNodeTarget(targetNode) {
      const fromNodeId = this.pendingFromNodeId
      if (!fromNodeId) {
        this.cancelConnectMode()
        return
      }
      if (!targetNode || targetNode.id === 'root') {
        uni.showToast({ title: '请选择有效目标节点', icon: 'none' })
        return
      }
      if (fromNodeId === targetNode.id) {
        uni.showToast({ title: '不允许自环连线', icon: 'none' })
        return
      }
      const exists = this.graphData.lines.some(line => line.from === fromNodeId && line.to === targetNode.id)
      if (exists) {
        uni.showToast({ title: '连线已存在', icon: 'none' })
        return
      }
      this.graphData.lines.push({ from: fromNodeId, to: targetNode.id })
      this.updateCanvasSizeByGraph()
      this.refreshGraph()
      this.isConnecting = false
      this.pendingFromNodeId = ''
      uni.showToast({ title: '连线成功', icon: 'success' })
    },
    onSelectProcess(node) {
      this.editingNode = node
      this.selectedProcessId = node.data?.processId || null
      this.selectedProcess = null
      this.showProcessSelector = true
    },
    onProcessSelect(process) {
      if (process) {
        this.selectedProcess = process
        this.selectedProcessId = process.id
      } else {
        this.selectedProcess = null
        this.selectedProcessId = null
      }
    },
    onConfirmSelectProcess() {
      if (!this.selectedProcessId || !this.selectedProcess) {
        uni.showToast({ title: '请选择工序', icon: 'none' })
        return
      }
      const targetId = this.editingNode.id
      this.graphData.nodes = this.graphData.nodes.map((node) => {
        if (node.id !== targetId) return node
        return {
          ...node,
          text: this.selectedProcess.name,
          data: {
            ...node.data,
            processId: this.selectedProcessId,
            processCode: this.selectedProcess.code
          }
        }
      })
      this.refreshGraph()
      this.showProcessSelector = false
      this.selectedProcessId = null
      this.selectedProcess = null
      this.editingNode = null
      uni.showToast({ title: '已选择工序', icon: 'success' })
    },
    /**
     * 串行新增节点
     */
    onAddSerialNode() {
      const parentId = this.selectedNodeId || 'root'
      const newNode = this.createNewNode()
      this.graphData.nodes.push(newNode)
      this.graphData.lines.push({ from: parentId, to: newNode.id })
      this.updateCanvasSizeByGraph()
      this.refreshGraph()
      this.onSelectProcess(newNode)
    },
    /**
     * 并行新增节点
     */
    onAddParallelNode() {
      const currentId = this.selectedNodeId || 'root'
      const parentLine = this.graphData.lines.find(line => line.to === currentId)
      const parentId = parentLine ? parentLine.from : 'root'
      const newNode = this.createNewNode()
      this.graphData.nodes.push(newNode)
      this.graphData.lines.push({ from: parentId, to: newNode.id })
      this.updateCanvasSizeByGraph()
      this.refreshGraph()
      this.onSelectProcess(newNode)
    },
    /**
     * 删除当前选中节点
     */
    onDeleteCurrentNode() {
      const nodeId = this.selectedNodeId
      if (!nodeId || nodeId === 'root') {
        uni.showToast({ title: '请先选择工序节点', icon: 'none' })
        return
      }
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个工序节点吗？',
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: (res) => {
          if (res.confirm) {
            this.deleteNodeWithChildren(nodeId)
          }
        }
      })
    },
    /**
     * 删除节点及其下游节点
     * @param {string} nodeId - 节点ID
     */
    deleteNodeWithChildren(nodeId) {
      const removeSet = new Set([nodeId])
      let changed = true
      while (changed) {
        changed = false
        this.graphData.lines.forEach((line) => {
          if (removeSet.has(line.from) && !removeSet.has(line.to)) {
            removeSet.add(line.to)
            changed = true
          }
        })
      }
      this.graphData.nodes = this.graphData.nodes.filter(node => !removeSet.has(node.id))
      this.graphData.lines = this.graphData.lines.filter(line => !removeSet.has(line.from) && !removeSet.has(line.to))
      this.selectedNodeId = 'root'
      this.updateCanvasSizeByGraph()
      this.refreshGraph()
    },
    /**
     * 打开当前节点工序选择弹窗
     */
    onSelectCurrentNodeProcess() {
      const currentNode = this.graphData.nodes.find(node => node.id === this.selectedNodeId)
      if (!currentNode || currentNode.id === 'root') {
        uni.showToast({ title: '请先选择工序节点', icon: 'none' })
        return
      }
      this.onSelectProcess(currentNode)
    },
    /**
     * 将 scroll-view 水平与垂直滚动复位，避免部分端初始停在非 0 偏移导致图看起来偏到一侧
     */
    resetEditorScrollPosition() {
      const bump = 1
      this.editorScrollLeft = bump
      this.editorScrollTop = bump
      this.$nextTick(() => {
        this.editorScrollLeft = 0
        this.editorScrollTop = 0
      })
    },
    /**
     * 仅复位外层滚动；不在此重复 moveToCenter/zoomToFit，避免与 relation-graph 内置
     * moveToCenterWhenRefresh、zoomToFitWhenRefresh 叠加导致整图偏到一角
     */
    stabilizeGraphScrollAfterLayout() {
      this.resetEditorScrollPosition()
      this.$nextTick(() => {
        this.resetEditorScrollPosition()
      })
    },
    /**
     * 从 graphData.lines 收集某节点沿出边的下游节点 id（含自身）
     * @param {string} rootId - 起点节点 id
     * @param {Array<{from: string, to: string}>} lines - 连线列表
     * @returns {Set<string>}
     */
    collectDownstreamNodeIds(rootId, lines) {
      const out = new Set()
      const stack = [rootId]
      while (stack.length > 0) {
        const id = stack.pop()
        if (out.has(id)) {
          continue
        }
        out.add(id)
        lines.forEach((line) => {
          if (line.from === id && line.to) {
            stack.push(line.to)
          }
        })
      }
      return out
    },
    /**
     * 多条入边汇合时，relation-graph 树布局易把节点贴在某一父节点下；将汇合点水平置于各父节点中心均值处，并平移其整棵下游子树以保持拓扑
     */
    centerMergeNodesHorizontally() {
      const graphRef = this.$refs.relationGraphRef
      const gi = graphRef?.getInstance?.()
      const lines = this.graphData.lines || []
      if (!gi || typeof gi.getNodes !== 'function' || lines.length === 0) {
        return
      }
      const indegree = {}
      lines.forEach((line) => {
        if (!line.to) {
          return
        }
        indegree[line.to] = (indegree[line.to] || 0) + 1
      })
      const mergeIds = Object.keys(indegree).filter((id) => indegree[id] >= 2)
      if (mergeIds.length === 0) {
        return
      }
      const rgNodes = gi.getNodes() || []
      mergeIds.sort((a, b) => {
        const na = rgNodes.find((n) => n.id === a)
        const nb = rgNodes.find((n) => n.id === b)
        return (nb?.y || 0) - (na?.y || 0)
      })
      const defaultW = this.graphOptions.defaultNodeWidth || 180
      const nodeWidth = (n) => {
        if (!n) {
          return defaultW
        }
        const w = n.el?.offsetWidth || n.width
        return w > 0 ? w : defaultW
      }
      const nodeCenterX = (n) => (n.x || 0) + nodeWidth(n) / 2
      mergeIds.forEach((mergeId) => {
        const parentIds = [...new Set(lines.filter((l) => l.to === mergeId).map((l) => l.from))]
        const parents = parentIds.map((pid) => rgNodes.find((n) => n.id === pid)).filter(Boolean)
        const mergeNode = rgNodes.find((n) => n.id === mergeId)
        if (!mergeNode || parents.length < 2) {
          return
        }
        const avgCx = parents.reduce((sum, p) => sum + nodeCenterX(p), 0) / parents.length
        const w = nodeWidth(mergeNode)
        const targetLeft = Math.round(avgCx - w / 2)
        const dx = targetLeft - (mergeNode.x || 0)
        if (Math.abs(dx) < 1) {
          return
        }
        const shiftSet = this.collectDownstreamNodeIds(mergeId, lines)
        shiftSet.forEach((nid) => {
          const n = rgNodes.find((item) => item.id === nid)
          if (!n || typeof gi.setNodePosition !== 'function') {
            return
          }
          gi.setNodePosition(n, (n.x || 0) + dx, n.y || 0)
        })
      })
      if (typeof gi.updateElementLines === 'function') {
        gi.updateElementLines()
      }
      if (typeof gi._dataUpdated === 'function') {
        gi._dataUpdated()
      }
    },
    /**
     * 将当前图整体缩放到关系图组件视口内（含并行、深层树）；视口尺寸由 updateGraphViewportSize 固定为屏幕内区域
     */
    applyZoomToFitEntireGraph() {
      const graphRef = this.$refs.relationGraphRef
      const gi = graphRef?.getInstance?.()
      if (!gi) {
        return
      }
      try {
        if (typeof gi.resetViewSize === 'function') {
          gi.resetViewSize(false)
        }
        if (this.graphOptions.layout && this.graphOptions.layout.layoutName === 'fixed') {
          this.recenterFixedLayoutToDomViewport(gi)
        }
        if (this.graphOptions.layout && this.graphOptions.layout.layoutName === 'tree') {
          this.centerMergeNodesHorizontally()
        }
        if (typeof gi.moveToCenter === 'function') {
          gi.moveToCenter()
        }
        if (typeof gi.zoomToFit === 'function') {
          gi.zoomToFit()
        }
      } catch (error) {
        console.error('关系图缩放到视口失败:', error)
      }
    },
    /**
     * 布局与 DOM 尺寸稳定后多次尝试 zoomToFit，适配 uni-app 异步测量
     */
    scheduleZoomToFitEntireGraph() {
      const run = () => {
        this.applyZoomToFitEntireGraph()
      }
      this.$nextTick(run)
      setTimeout(run, 80)
      setTimeout(run, 220)
      setTimeout(run, 420)
    },
    /**
     * 关系图渲染刷新
     * @param {Object} [options={}]
     * @param {boolean} [options.fitToView=false] 首次进入时额外复位外层 scroll-view
     */
    refreshGraph(options = {}) {
      const { fitToView = false } = options
      this.$nextTick(() => {
        this.updateGraphViewportSize()
        this.syncGraphLayoutStrategy()
        if (this.graphOptions.layout && this.graphOptions.layout.layoutName === 'tree') {
          this.updateCanvasSizeByGraph()
        }
        this.resetEditorScrollPosition()
        const graphRef = this.$refs.relationGraphRef
        if (graphRef && graphRef.setJsonData) {
          graphRef.setJsonData(this.graphData, true, () => {
            this.scheduleZoomToFitEntireGraph()
            if (fitToView && !this.hasInitializedViewport) {
              this.hasInitializedViewport = true
              this.stabilizeGraphScrollAfterLayout()
              setTimeout(() => {
                this.stabilizeGraphScrollAfterLayout()
              }, 120)
            }
          })
        }
      })
    },
    /**
     * 图谱数据转保存载荷
     * @returns {Object}
     */
    graphToPayload() {
      const nodes = this.graphData.nodes
        .filter(node => node.id !== 'root' && node.data?.processId)
        .map(node => ({
          node_key: node.data.nodeKey || node.id,
          process: node.data.processId,
          process_bom: node.data.bomId || null
        }))
      const incomingSet = new Set(
        this.graphData.lines
          .filter(line => line.from !== 'root' && line.to !== 'root')
          .map(line => line.to)
      )
      const rootStartEdges = this.graphData.lines
        .filter(line => line.from === 'root' && line.to !== 'root')
        .map(line => ({
          to: line.to
        }))
      const edges = this.graphData.lines
        .filter(line => line.from !== 'root' && line.to !== 'root')
        .map(line => ({
          from_node_key: this.getNodeKeyById(line.from),
          to_node_key: this.getNodeKeyById(line.to),
          priority: 1
        }))
      rootStartEdges.forEach((edge) => {
        if (!incomingSet.has(edge.to)) {
          edges.push({
            from_node_key: 'root',
            to_node_key: this.getNodeKeyById(edge.to),
            priority: 1
          })
        }
      })
      return {
        process_route: this.routeId,
        nodes,
        edges: edges.filter(edge => edge.from_node_key && edge.to_node_key && edge.from_node_key !== 'root')
      }
    },
    getNodeKeyById(nodeId) {
      const node = this.graphData.nodes.find(item => item.id === nodeId)
      return node?.data?.nodeKey || node?.id || ''
    },
    async onSave() {
      const unselectedNodes = this.findUnselectedNodes()
      if (unselectedNodes.length > 0) {
        uni.showToast({ title: '还有未选择工序的节点', icon: 'none' })
        return
      }
      this.isSaving = true
      try {
        const payload = this.graphToPayload()
        await processRouteApi.saveProcessRouteGraph(payload)
        uni.showToast({ title: '保存成功', icon: 'success' })
        this.loadRouteData()
      } catch (error) {
        console.error('保存工艺路线失败:', error)
        uni.showToast({ title: error.msg || '保存失败', icon: 'none' })
      } finally {
        this.isSaving = false
      }
    },
    /**
     * 查找未选择工序的节点
     * @returns {Array}
     */
    findUnselectedNodes() {
      return this.graphData.nodes.filter(node => node.id !== 'root' && !node.data?.processId)
    },
    onEditBaseInfo() {
      uni.navigateTo({
        url: `/pages/admin/process-route/edit?id=${this.routeId}`
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $uni-bg-color;
}

.route-info-card {
  margin: 24rpx;
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.route-info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.route-info-title {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.material-name {
  font-size: 32rpx;
  font-weight: 600;
  color: $uni-text-color;
}

.route-description {
  font-size: 26rpx;
  color: $uni-text-color-grey;
  line-height: 1.5;
}

.node-editor {
  flex: 1;
  padding: 16rpx 16rpx 320rpx;
}

.node-tree-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  padding: 12rpx;
}

.relation-graph {
  min-width: 100%;
  min-height: 100%;
  background-color: $uni-bg-color-white;
  border: 1px solid $uni-border-color;
  border-radius: 16rpx;
}

.rg-node-card {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  padding: 10rpx 16rpx;
  border-radius: 12rpx;
  border: 1px solid #1989fa;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  margin: 6rpx 0;
}

.rg-node-root {
  border-color: #faad14;
  background-color: #fffaf0;
}

.rg-node-title {
  font-size: 24rpx;
  font-weight: 600;
  color: $uni-text-color;
  text-align: center;
  line-height: 1.4;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rg-node-subtitle {
  font-size: 20rpx;
  color: $uni-text-color-grey;
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gesture-tip {
  position: absolute;
  left: 20rpx;
  top: 20rpx;
  z-index: 100;
  padding: 10rpx 16rpx;
  border-radius: 20rpx;
  background-color: rgba(0, 0, 0, 0.42);
  color: #ffffff;
  font-size: 22rpx;
  pointer-events: none;
}

.save-fab {
  position: fixed;
  right: 24rpx;
  bottom: calc(24rpx + env(safe-area-inset-bottom));
  z-index: 120;
}

.popup-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  border-bottom: 1px solid $uni-border-color;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.popup-body {
  flex: 1;
  padding: 24rpx;
  overflow-y: auto;
}

.popup-footer {
  padding: 24rpx;
  border-top: 1px solid $uni-border-color;

  :deep(.wd-button) {
    width: 100%;
  }
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
}
</style>
