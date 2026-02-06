<template>
  <view
    v-if="visible"
    class="md3-bottom-sheet"
    :class="[
      `variant-${variant}`,
      {
        'is-open': isOpen,
        'is-dragging': isDragging,
        'has-drag-handle': showDragHandle
      }
    ]"
    @click="onOverlayClick"
  >
    <!-- 遮罩层 -->
    <view
      v-if="variant === 'modal'"
      class="md3-bottom-sheet__scrim"
      :class="{ 'is-visible': isOpen }"
      :style="scrimStyle"
    />

    <!-- 底部面板 -->
    <view
      ref="sheetRef"
      class="md3-bottom-sheet__sheet"
      :class="{ 'is-visible': isOpen }"
      :style="sheetStyle"
      @click.stop
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      <!-- 拖拽把手 -->
      <view
        v-if="showDragHandle"
        class="md3-bottom-sheet__drag-handle"
        @touchstart="onDragHandleTouchStart"
      >
        <view class="md3-bottom-sheet__drag-handle-bar" />
      </view>

      <!-- 头部区域 -->
      <view v-if="$slots.header || title" class="md3-bottom-sheet__header">
        <slot name="header">
          <view class="md3-bottom-sheet__header-content">
            <text v-if="title" class="md3-bottom-sheet__title">{{ title }}</text>
            <text v-if="subtitle" class="md3-bottom-sheet__subtitle">{{ subtitle }}</text>
          </view>
          <view
            v-if="showClose"
            class="md3-bottom-sheet__close"
            @click="close"
          >
            <MdIcon type="close" :size="24" :color="iconColor" />
          </view>
        </slot>
      </view>

      <!-- 内容区域 -->
      <scroll-view
        scroll-y
        class="md3-bottom-sheet__content"
        :style="contentStyle"
      >
        <slot />
      </scroll-view>

      <!-- 操作区域 -->
      <view v-if="$slots.actions" class="md3-bottom-sheet__actions">
        <slot name="actions" />
      </view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 BottomSheet 组件
 * @component
 * @description 底部面板组件，支持标准和模态两种变体
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {'standard'|'modal'} BottomSheetVariant
 * @typedef {'collapsed'|'half'|'expanded'} BottomSheetState
 */

export default {
  name: 'BottomSheet',

  components: {
    MdIcon
  },

  props: {
    /**
     * 是否可见
     * @type {boolean}
     */
    visible: {
      type: Boolean,
      default: false
    },

    /**
     * 面板变体
     * @type {BottomSheetVariant}
     */
    variant: {
      type: String,
      default: 'modal',
      validator: (value) => ['standard', 'modal'].includes(value)
    },

    /**
     * 标题
     * @type {string}
     */
    title: {
      type: String,
      default: ''
    },

    /**
     * 副标题
     * @type {string}
     */
    subtitle: {
      type: String,
      default: ''
    },

    /**
     * 是否显示关闭按钮
     * @type {boolean}
     */
    showClose: {
      type: Boolean,
      default: true
    },

    /**
     * 是否显示拖拽把手
     * @type {boolean}
     */
    showDragHandle: {
      type: Boolean,
      default: true
    },

    /**
     * 是否可拖拽
     * @type {boolean}
     */
    draggable: {
      type: Boolean,
      default: true
    },

    /**
     * 是否点击遮罩关闭
     * @type {boolean}
     */
    closeOnOverlayClick: {
      type: Boolean,
      default: true
    },

    /**
     * 是否可隐藏
     * @type {boolean}
     */
    hideable: {
      type: Boolean,
      default: true
    },

    /**
     * 面板高度
     * @type {string}
     */
    height: {
      type: String,
      default: 'auto'
    },

    /**
     * 最大高度
     * @type {string}
     */
    maxHeight: {
      type: String,
      default: '80vh'
    },

    /**
     * 背景色
     * @type {string}
     */
    backgroundColor: {
      type: String,
      default: ''
    }
  },

  emits: ['update:visible', 'open', 'close', 'state-change'],

  data() {
    return {
      isOpen: false,
      isDragging: false,
      sheetHeight: 0,
      startY: 0,
      currentY: 0,
      translateY: 0
    }
  },

  computed: {
    /**
     * 图标颜色
     * @returns {string}
     */
    iconColor() {
      return '#49454F'
    },

    /**
     * 遮罩层样式
     * @returns {Object}
     */
    scrimStyle() {
      return {
        opacity: this.isOpen ? 1 : 0
      }
    },

    /**
     * 面板样式
     * @returns {Object}
     */
    sheetStyle() {
      const styles = {
        backgroundColor: this.backgroundColor || '#FEF7FF',
        transform: `translateY(${this.translateY}px)`,
        maxHeight: this.maxHeight
      }

      if (this.height !== 'auto') {
        styles.height = this.height
      }

      return styles
    },

    /**
     * 内容区域样式
     * @returns {Object}
     */
    contentStyle() {
      return {
        maxHeight: this.maxHeight
      }
    }
  },

  watch: {
    visible: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.open()
        } else {
          this.close()
        }
      }
    }
  },

  methods: {
    /**
     * 打开面板
     */
    open() {
      this.$nextTick(() => {
        setTimeout(() => {
          this.isOpen = true
          this.translateY = 0
          this.$emit('open')
        }, 10)
      })
    },

    /**
     * 关闭面板
     */
    close() {
      this.isOpen = false
      this.translateY = 100
      setTimeout(() => {
        this.$emit('update:visible', false)
        this.$emit('close')
      }, 300)
    },

    /**
     * 处理遮罩点击
     */
    onOverlayClick() {
      if (this.closeOnOverlayClick && this.variant === 'modal') {
        this.close()
      }
    },

    /**
     * 处理触摸开始
     * @param {TouchEvent} event
     */
    onTouchStart(event) {
      if (!this.draggable) return
      this.isDragging = true
      this.startY = event.touches[0].clientY
      this.currentY = this.startY
    },

    /**
     * 处理拖拽把手触摸开始
     * @param {TouchEvent} event
     */
    onDragHandleTouchStart(event) {
      event.stopPropagation()
      this.onTouchStart(event)
    },

    /**
     * 处理触摸移动
     * @param {TouchEvent} event
     */
    onTouchMove(event) {
      if (!this.isDragging) return
      this.currentY = event.touches[0].clientY
      const deltaY = this.currentY - this.startY

      if (deltaY > 0) {
        this.translateY = deltaY
      }
    },

    /**
     * 处理触摸结束
     */
    onTouchEnd() {
      if (!this.isDragging) return
      this.isDragging = false

      const deltaY = this.currentY - this.startY
      const threshold = 100

      if (deltaY > threshold && this.hideable) {
        this.close()
      } else {
        this.translateY = 0
      }
    }
  }
}
</script>

<style lang="scss">
.md3-bottom-sheet {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  pointer-events: none;

  &.is-open {
    pointer-events: auto;
  }
}

// 遮罩层
.md3-bottom-sheet__scrim {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 300ms ease;
  pointer-events: auto;

  &.is-visible {
    opacity: 1;
  }
}

// 面板
.md3-bottom-sheet__sheet {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: #FEF7FF;
  border-radius: $uni-md-radius-large $uni-md-radius-large 0 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: auto;
  max-height: 80vh;

  &.is-visible {
    transform: translateY(0);
  }
}

// 拖拽把手
.md3-bottom-sheet__drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $uni-md-space-md 0 $uni-md-space-sm;
  cursor: grab;

  &:active {
    cursor: grabbing;
  }
}

.md3-bottom-sheet__drag-handle-bar {
  width: 32px;
  height: 4px;
  background-color: #CAC4D0;
  border-radius: 2px;
}

// 头部区域
.md3-bottom-sheet__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-bottom: 1px solid transparent;
}

.md3-bottom-sheet__header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-xs;
}

.md3-bottom-sheet__title {
  font-size: $uni-font-size-lg;
  font-weight: 500;
  color: $uni-md-text-primary;
  line-height: 1.5;
}

.md3-bottom-sheet__subtitle {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
  line-height: 1.4;
}

.md3-bottom-sheet__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-left: $uni-md-space-sm;
  cursor: pointer;
  transition: background-color 150ms ease;
  flex-shrink: 0;

  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  &:active {
    background-color: rgba(0, 0, 0, 0.08);
  }
}

// 内容区域
.md3-bottom-sheet__content {
  flex: 1;
  padding: $uni-md-space-md $uni-md-space-lg;
  overflow-y: auto;
}

// 操作区域
.md3-bottom-sheet__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-top: 1px solid $uni-md-divider;
}

// 安全区域适配
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .md3-bottom-sheet__sheet {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>
