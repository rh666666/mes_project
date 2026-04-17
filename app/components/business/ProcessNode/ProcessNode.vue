<template>
  <view class="node-container" :class="{ 'root-node': isRoot, 'parallel-container': isParallelContainer }">
    <!-- 根节点 - 简化图标样式 -->
    <template v-if="isRoot">
      <view class="root-header">
        <view class="root-icon-wrapper">
          <wd-icon name="play-circle" size="48" color="#1989fa" />
        </view>
        <view class="root-title">工艺路线起点</view>
      </view>

      <!-- 根节点添加按钮 -->
      <view v-if="!hasChildren" class="root-add-button">
        <wd-button type="primary" size="small" @click="onAddSerial">
          <wd-icon name="add" size="16" color="#fff" />
          添加第一个工序
        </wd-button>
      </view>
    </template>

    <!-- 普通节点 - 卡片样式 -->
    <template v-else>
      <!-- 顶部连接点（用于接收连接） -->
      <view
        v-if="node.processId"
        class="connection-point connection-point-top"
        @touchstart.stop="onConnectPointStart('top', $event)"
        @touchmove.stop="onConnectPointMove($event)"
        @touchend.stop="onConnectPointEnd($event)"
      >
        <view class="connection-point-inner"></view>
      </view>

      <!-- 节点卡片 -->
      <view
        class="node-card"
        :class="{
          'node-empty': !node.processId,
          'node-selected': node.processId,
          'is-dragging': isDragging
        }"
        @click="onCardClick"
      >
        <!-- 序号徽章 -->
        <view v-if="node.sequence" class="sequence-badge">
          {{ node.sequence }}
        </view>

        <!-- 节点内容 -->
        <view class="node-content">
          <template v-if="node.processId">
            <view class="node-name">{{ node.processName || '未命名工序' }}</view>
            <view class="node-code">{{ node.processCode || '-' }}</view>
          </template>
          <template v-else>
            <wd-icon name="add" size="32" color="#1989fa" />
            <view class="node-placeholder">点击选择工序</view>
          </template>
        </view>

        <!-- 删除按钮 -->
        <view v-if="node.processId" class="node-actions">
          <wd-icon name="delete" size="18" color="#ee0a24" @click.stop="onDeleteClick" />
        </view>
      </view>

      <!-- 底部连接点（用于拖拽出连接） -->
      <view
        v-if="node.processId"
        class="connection-point connection-point-bottom"
        @touchstart.stop="onConnectPointStart('bottom', $event)"
        @touchmove.stop="onConnectPointMove($event)"
        @touchend.stop="onConnectPointEnd($event)"
      >
        <view class="connection-point-inner"></view>
      </view>
    </template>

    <!-- 子节点区域 -->
    <view v-if="hasChildren" class="children-wrapper">
      <!-- 垂直连接线（从当前节点到子节点区域） -->
      <view class="vertical-line-down"></view>

      <!-- 子节点容器 -->
      <view class="children-container" :class="{ 'parallel-layout': isParallelLayout }">
        <!-- 并行布局的水平连接线 -->
        <view v-if="isParallelLayout" class="horizontal-connector">
          <view class="horizontal-line"></view>
        </view>

        <!-- 子节点列表 -->
        <view
          v-for="(child, index) in node.children"
          :key="child.id"
          class="child-wrapper"
          :class="{ 'with-vertical-line': isParallelLayout }"
        >
          <!-- 并行节点的垂直连接线 -->
          <view v-if="isParallelLayout" class="vertical-line-to-child"></view>

          <ProcessNode
            :node="child"
            :is-root="false"
            :parent-type="node.type"
            @select-process="handleSelectProcess"
            @add-child="handleAddChild"
            @delete="handleDelete"
            @connect-start="handleConnectStart"
            @connect-move="handleConnectMove"
            @connect-end="handleConnectEnd"
          />
        </view>
      </view>
    </view>

    <!-- 添加按钮区域（仅在无子节点时显示） -->
    <view v-if="!isRoot && !hasChildren" class="add-buttons">
      <wd-button type="primary" size="small" plain @click="onAddSerial">
        <wd-icon name="add" size="14" color="#1989fa" />
        串行
      </wd-button>
      <wd-button type="success" size="small" plain @click="onAddParallel">
        <wd-icon name="add" size="14" color="#07c160" />
        并行
      </wd-button>
    </view>
  </view>
</template>

<script>
/**
 * 工艺路线节点组件
 * @component
 * @description 递归渲染工艺路线节点，支持串行和并行布局，支持拖拽连接
 */
export default {
  name: 'ProcessNode',

  props: {
    /**
     * 节点数据
     * @type {Object}
     */
    node: {
      type: Object,
      required: true
    },
    /**
     * 是否为根节点
     * @type {boolean}
     */
    isRoot: {
      type: Boolean,
      default: false
    },
    /**
     * 父节点类型
     * @type {string}
     */
    parentType: {
      type: String,
      default: 'serial'
    }
  },

  emits: ['select-process', 'add-child', 'delete', 'connect-start', 'connect-move', 'connect-end'],

  data() {
    return {
      /** @type {boolean} 是否正在拖拽 */
      isDragging: false
    }
  },

  computed: {
    /**
     * 是否有子节点
     * @returns {boolean}
     */
    hasChildren() {
      return this.node.children && this.node.children.length > 0
    },

    /**
     * 是否为并行布局容器
     * @returns {boolean}
     */
    isParallelLayout() {
      return this.node.type === 'parallel' || (this.node.children && this.node.children.length > 1)
    },

    /**
     * 是否为并行容器
     * @returns {boolean}
     */
    isParallelContainer() {
      return this.node.type === 'parallel-container'
    }
  },

  methods: {
    /**
     * 处理子节点选择工序事件
     * @param {Object} node - 节点
     */
    handleSelectProcess(node) {
      this.$emit('select-process', node)
    },

    /**
     * 处理子节点添加事件
     * @param {Object} params - 参数
     */
    handleAddChild(params) {
      this.$emit('add-child', params)
    },

    /**
     * 处理子节点删除事件
     * @param {Object} node - 节点
     */
    handleDelete(node) {
      this.$emit('delete', node)
    },

    /**
     * 处理连接开始事件
     * @param {Object} params - 参数
     */
    handleConnectStart(params) {
      this.$emit('connect-start', params)
    },

    /**
     * 处理连接移动事件
     * @param {Object} params - 参数
     */
    handleConnectMove(params) {
      this.$emit('connect-move', params)
    },

    /**
     * 处理连接结束事件
     * @param {Object} params - 参数
     */
    handleConnectEnd(params) {
      this.$emit('connect-end', params)
    },

    /**
     * 卡片点击事件
     */
    onCardClick() {
      this.$emit('select-process', this.node)
    },

    /**
     * 删除按钮点击
     */
    onDeleteClick() {
      this.$emit('delete', this.node)
    },

    /**
     * 添加串行子节点
     */
    onAddSerial() {
      this.$emit('add-child', {
        parentNode: this.node,
        type: 'serial'
      })
    },

    /**
     * 添加并行子节点
     */
    onAddParallel() {
      this.$emit('add-child', {
        parentNode: this.node,
        type: 'parallel'
      })
    },

    /**
     * 连接点开始拖拽
     * @param {string} position - 'top' | 'bottom'
     * @param {Object} event - 触摸事件
     */
    onConnectPointStart(position, event) {
      this.isDragging = true
      this.$emit('connect-start', {
        node: this.node,
        position: position,
        touch: event.touches[0]
      })
    },

    /**
     * 连接点拖拽中
     * @param {Object} event - 触摸事件
     */
    onConnectPointMove(event) {
      event.preventDefault()
      this.$emit('connect-move', {
        node: this.node,
        touch: event.touches[0]
      })
    },

    /**
     * 连接点拖拽结束
     * @param {Object} event - 触摸事件
     */
    onConnectPointEnd(event) {
      this.isDragging = false
      this.$emit('connect-end', {
        node: this.node,
        touch: event.changedTouches[0]
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.node-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

/* 根节点样式 */
.root-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 32rpx;
}

.root-icon-wrapper {
  width: 96rpx;
  height: 96rpx;
  border-radius: 48rpx;
  background: linear-gradient(135deg, rgba(25, 137, 250, 0.1), rgba(25, 137, 250, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(25, 137, 250, 0.2);
}

.root-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #1989fa;
}

.root-add-button {
  margin-top: 24rpx;
}

/* 连接点样式 */
.connection-point {
  position: absolute;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  transition: all 0.2s ease;

  &-top {
    top: -24rpx;
    left: 50%;
    transform: translateX(-50%);
  }

  &-bottom {
    bottom: -24rpx;
    left: 50%;
    transform: translateX(-50%);
  }

  &-inner {
    width: 24rpx;
    height: 24rpx;
    border-radius: 12rpx;
    background: linear-gradient(135deg, #1989fa, #36a1ff);
    border: 4rpx solid #fff;
    box-shadow: 0 2rpx 8rpx rgba(25, 137, 250, 0.4);
    transition: all 0.2s ease;
  }

  &:active &-inner {
    transform: scale(1.3);
    box-shadow: 0 4rpx 16rpx rgba(25, 137, 250, 0.6);
  }
}

/* 节点卡片 */
.node-card {
  position: relative;
  min-width: 280rpx;
  max-width: 400rpx;
  padding: 32rpx 40rpx;
  background-color: $uni-bg-color-white;
  border: 2rpx solid #ebedf0;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  z-index: 2;
  margin: 24rpx 0;

  &.node-empty {
    border-style: dashed;
    border-color: #1989fa;
    background-color: rgba(25, 137, 250, 0.02);
  }

  &.node-selected {
    border-color: #1989fa;
    box-shadow: 0 4rpx 16rpx rgba(25, 137, 250, 0.15);
  }

  &.is-dragging {
    transform: scale(1.02);
    box-shadow: 0 8rpx 24rpx rgba(25, 137, 250, 0.2);
  }

  &:active {
    transform: scale(0.98);
  }
}

/* 序号徽章 */
.sequence-badge {
  position: absolute;
  top: -12rpx;
  left: -12rpx;
  min-width: 40rpx;
  height: 40rpx;
  padding: 0 10rpx;
  background: linear-gradient(135deg, #1989fa, #36a1ff);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 2rpx 8rpx rgba(25, 137, 250, 0.3);
  z-index: 10;
}

/* 节点内容 */
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  width: 100%;
  min-height: 60rpx;
}

.node-name {
  font-size: 30rpx;
  font-weight: 600;
  color: $uni-text-color;
  text-align: center;
  width: 100%;
  line-height: 1.4;
}

.node-code {
  font-size: 22rpx;
  color: $uni-text-color-grey;
  text-align: center;
  width: 100%;
  background-color: $uni-bg-color;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}

.node-placeholder {
  font-size: 26rpx;
  color: #1989fa;
  font-weight: 500;
}

/* 删除按钮 */
.node-actions {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 22rpx;
  transition: all 0.2s ease;
  z-index: 10;

  &:active {
    background-color: rgba(238, 10, 36, 0.1);
  }
}

/* 子节点包装器 */
.children-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

/* 垂直向下连接线 */
.vertical-line-down {
  width: 2rpx;
  height: 40rpx;
  background-color: #c8c9cc;
}

/* 子节点容器 */
.children-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 100%;

  /* 串行布局 */
  &:not(.parallel-layout) {
    > .child-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;

      /* 串行节点之间的连接线 */
      &::before {
        content: '';
        width: 2rpx;
        height: 40rpx;
        background-color: #c8c9cc;
      }

      &:first-child::before {
        display: none;
      }
    }
  }

  /* 并行布局 */
  &.parallel-layout {
    flex-direction: row;
    justify-content: center;
    gap: 32rpx;
    padding: 0 24rpx 24rpx;
    margin-top: 0;
  }
}

/* 水平连接线（并行） */
.horizontal-connector {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  height: 2rpx;
  background-color: #c8c9cc;
}

.horizontal-line {
  width: 100%;
  height: 100%;
}

/* 子节点包装 */
.child-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;

  &.with-vertical-line {
    position: relative;
    padding-top: 40rpx;

    /* 从水平线到子节点的垂直线 */
    .vertical-line-to-child {
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 2rpx;
      height: 40rpx;
      background-color: #c8c9cc;
    }
  }
}

/* 添加按钮 */
.add-buttons {
  display: flex;
  gap: 24rpx;
  margin-top: 24rpx;
}

/* 并行容器 */
.parallel-container {
  .children-container {
    flex-direction: row;
    gap: 32rpx;
  }
}
</style>
