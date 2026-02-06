<template>
  <view
    v-if="visible"
    class="md3-side-sheet"
    :class="[
      `position-${position}`,
      `variant-${variant}`,
      {
        'is-open': isOpen,
        'is-dragging': isDragging
      }
    ]"
    @click="onOverlayClick"
  >
    <!-- 遮罩层 -->
    <view
      v-if="variant === 'modal'"
      class="md3-side-sheet__scrim"
      :class="{ 'is-visible': isOpen }"
      :style="scrimStyle"
    />

    <!-- 侧面面板 -->
    <view
      ref="sheetRef"
      class="md3-side-sheet__sheet"
      :class="{ 'is-visible': isOpen }"
      :style="sheetStyle"
      @click.stop
    >
      <!-- 头部区域 -->
      <view v-if="$slots.header || title" class="md3-side-sheet__header">
        <slot name="header">
          <!-- 返回按钮 -->
          <view
            v-if="showBack"
            class="md3-side-sheet__back"
            @click="onBackClick"
          >
            <MdIcon type="arrow_back" :size="24" :color="iconColor" />
          </view>

          <view class="md3-side-sheet__header-content">
            <text v-if="title" class="md3-side-sheet__title">{{ title }}</text>
            <text v-if="subtitle" class="md3-side-sheet__subtitle">{{ subtitle }}</text>
          </view>

          <!-- 关闭按钮 -->
          <view
            v-if="showClose"
            class="md3-side-sheet__close"
            @click="close"
          >
            <MdIcon type="close" :size="24" :color="iconColor" />
          </view>
        </slot>
      </view>

      <!-- 分割线 -->
      <view v-if="showDivider && ($slots.header || title)" class="md3-side-sheet__divider" />

      <!-- 内容区域 -->
      <scroll-view
        scroll-y
        class="md3-side-sheet__content"
        :style="contentStyle"
      >
        <slot />
      </scroll-view>

      <!-- 操作区域 -->
      <view v-if="$slots.actions" class="md3-side-sheet__actions">
        <slot name="actions" />
      </view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 SideSheet 组件
 * @component
 * @description 侧面面板组件，支持标准和模态两种变体
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {'standard'|'modal'} SideSheetVariant
 * @typedef {'start'|'end'} SideSheetPosition
 */

export default {
  name: 'SideSheet',

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
     * @type {SideSheetVariant}
     */
    variant: {
      type: String,
      default: 'modal',
      validator: (value) => ['standard', 'modal'].includes(value)
    },

    /**
     * 面板位置
     * @type {SideSheetPosition}
     */
    position: {
      type: String,
      default: 'end',
      validator: (value) => ['start', 'end'].includes(value)
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
     * 是否显示返回按钮
     * @type {boolean}
     */
    showBack: {
      type: Boolean,
      default: false
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
     * 是否显示分割线
     * @type {boolean}
     */
    showDivider: {
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
     * 面板宽度
     * @type {string}
     */
    width: {
      type: String,
      default: '320px'
    },

    /**
     * 最大宽度
     * @type {string}
     */
    maxWidth: {
      type: String,
      default: '80vw'
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

  emits: ['update:visible', 'open', 'close', 'back'],

  data() {
    return {
      isOpen: false,
      isDragging: false
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
        width: this.width,
        maxWidth: this.maxWidth
      }

      if (this.position === 'start') {
        styles.left = 0
        styles.transform = this.isOpen ? 'translateX(0)' : 'translateX(-100%)'
      } else {
        styles.right = 0
        styles.transform = this.isOpen ? 'translateX(0)' : 'translateX(100%)'
      }

      return styles
    },

    /**
     * 内容区域样式
     * @returns {Object}
     */
    contentStyle() {
      return {}
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
          this.$emit('open')
        }, 10)
      })
    },

    /**
     * 关闭面板
     */
    close() {
      this.isOpen = false
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
     * 处理返回按钮点击
     */
    onBackClick() {
      this.$emit('back')
    }
  }
}
</script>

<style lang="scss">
.md3-side-sheet {
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
.md3-side-sheet__scrim {
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
.md3-side-sheet__sheet {
  position: absolute;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background-color: #FEF7FF;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: auto;

  &.is-visible {
    transform: translateX(0);
  }
}

// 头部区域
.md3-side-sheet__header {
  display: flex;
  align-items: flex-start;
  padding: $uni-md-space-md $uni-md-space-lg;
  gap: $uni-md-space-md;
}

.md3-side-sheet__back,
.md3-side-sheet__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
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

.md3-side-sheet__header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-xs;
  min-width: 0;
}

.md3-side-sheet__title {
  font-size: $uni-font-size-lg;
  font-weight: 500;
  color: $uni-md-text-primary;
  line-height: 1.5;
}

.md3-side-sheet__subtitle {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
  line-height: 1.4;
}

// 分割线
.md3-side-sheet__divider {
  height: 1px;
  background-color: $uni-md-divider;
  margin: 0 $uni-md-space-lg;
}

// 内容区域
.md3-side-sheet__content {
  flex: 1;
  padding: $uni-md-space-md $uni-md-space-lg;
  overflow-y: auto;
}

// 操作区域
.md3-side-sheet__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-top: 1px solid $uni-md-divider;
}

// 安全区域适配
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .md3-side-sheet__sheet {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>
