<template>
  <view
    v-if="visible"
    class="md3-snackbar"
    :class="[
      `position-${position}`,
      {
        'is-visible': isVisible,
        'has-action': showAction,
        'has-close': showClose
      }
    ]"
    :style="snackbarStyle"
    @click="onSnackbarClick"
  >
    <!-- 文本内容 -->
    <text class="md3-snackbar__text">{{ message }}</text>

    <!-- 操作按钮 -->
    <view v-if="showAction" class="md3-snackbar__actions">
      <view
        class="md3-snackbar__action-btn"
        @click.stop="onActionClick"
      >
        <text class="md3-snackbar__action-text">{{ actionText }}</text>
      </view>

      <!-- 关闭按钮 -->
      <view
        v-if="showClose"
        class="md3-snackbar__close-btn"
        @click.stop="onCloseClick"
      >
        <MdIcon type="close" :size="18" color="#FFFFFF" />
      </view>
    </view>

    <!-- 仅关闭按钮（无操作按钮时） -->
    <view
      v-else-if="showClose"
      class="md3-snackbar__close-btn"
      @click.stop="onCloseClick"
    >
      <MdIcon type="close" :size="18" color="#FFFFFF" />
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 Snackbar 组件
 * @component
 * @description 底部提示条组件，用于显示简短的操作反馈信息
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {'short'|'long'|'indefinite'} SnackbarDuration
 */

export default {
  name: 'Snackbar',

  components: {
    MdIcon
  },

  props: {
    /**
     * 是否显示
     * @type {boolean}
     */
    visible: {
      type: Boolean,
      default: false
    },

    /**
     * 显示文本
     * @type {string}
     */
    message: {
      type: String,
      default: ''
    },

    /**
     * 显示时长
     * @type {SnackbarDuration}
     */
    duration: {
      type: String,
      default: 'short',
      validator: (value) => ['short', 'long', 'indefinite'].includes(value)
    },

    /**
     * 位置
     * @type {'bottom'|'top'}
     */
    position: {
      type: String,
      default: 'bottom',
      validator: (value) => ['bottom', 'top'].includes(value)
    },

    /**
     * 是否显示操作按钮
     * @type {boolean}
     */
    showAction: {
      type: Boolean,
      default: false
    },

    /**
     * 操作按钮文本
     * @type {string}
     */
    actionText: {
      type: String,
      default: '操作'
    },

    /**
     * 是否显示关闭按钮
     * @type {boolean}
     */
    showClose: {
      type: Boolean,
      default: false
    },

    /**
     * 点击外部是否关闭
     * @type {boolean}
     */
    closeOnClickOutside: {
      type: Boolean,
      default: true
    }
  },

  emits: ['update:visible', 'action', 'close', 'dismiss'],

  data() {
    return {
      isVisible: false,
      timer: null
    }
  },

  computed: {
    /**
     * Snackbar 样式
     * @returns {Object}
     */
    snackbarStyle() {
      return {
        transform: this.isVisible ? 'translateY(0)' : (this.position === 'bottom' ? 'translateY(100%)' : 'translateY(-100%)'),
        opacity: this.isVisible ? 1 : 0
      }
    },

    /**
     * 持续时间（毫秒）
     * @returns {number|null}
     */
    durationMs() {
      switch (this.duration) {
        case 'short':
          return 4000
        case 'long':
          return 10000
        case 'indefinite':
          return null
        default:
          return 4000
      }
    }
  },

  watch: {
    visible: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.showSnackbar()
        } else {
          this.hideSnackbar()
        }
      }
    }
  },

  beforeDestroy() {
    this.clearTimer()
  },

  methods: {
    /**
     * 显示 Snackbar
     */
    showSnackbar() {
      this.$nextTick(() => {
        setTimeout(() => {
          this.isVisible = true
        }, 10)

        // 设置自动关闭定时器
        if (this.durationMs) {
          this.clearTimer()
          this.timer = setTimeout(() => {
            this.dismiss()
          }, this.durationMs)
        }
      })
    },

    /**
     * 隐藏 Snackbar
     */
    hideSnackbar() {
      this.isVisible = false
      this.clearTimer()
    },

    /**
     * 清除定时器
     */
    clearTimer() {
      if (this.timer) {
        clearTimeout(this.timer)
        this.timer = null
      }
    },

    /**
     * 关闭 Snackbar
     */
    dismiss() {
      this.hideSnackbar()
      setTimeout(() => {
        this.$emit('update:visible', false)
        this.$emit('dismiss')
      }, 300)
    },

    /**
     * 处理操作按钮点击
     */
    onActionClick() {
      this.$emit('action')
      this.dismiss()
    },

    /**
     * 处理关闭按钮点击
     */
    onCloseClick() {
      this.$emit('close')
      this.dismiss()
    },

    /**
     * 处理 Snackbar 点击
     */
    onSnackbarClick() {
      // 点击 Snackbar 本身不关闭，除非点击操作按钮或关闭按钮
    }
  }
}
</script>

<style lang="scss">
.md3-snackbar {
  position: fixed;
  left: $uni-md-space-md;
  right: $uni-md-space-md;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $uni-md-space-md;
  background-color: #323232;
  border-radius: $uni-md-radius-small;
  box-shadow: $uni-md-shadow-lg;
  z-index: 9999;
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);

  // 底部位置
  &.position-bottom {
    bottom: $uni-md-space-lg;
  }

  // 顶部位置
  &.position-top {
    top: $uni-md-space-lg;
  }

  // 可见状态
  &.is-visible {
    transform: translateY(0);
    opacity: 1;
  }
}

// 文本
.md3-snackbar__text {
  flex: 1;
  font-size: $uni-font-size-base;
  color: #FFFFFF;
  line-height: 1.5;
  margin-right: $uni-md-space-md;
}

// 操作区域
.md3-snackbar__actions {
  display: flex;
  align-items: center;
  gap: $uni-md-space-sm;
  flex-shrink: 0;
}

// 操作按钮
.md3-snackbar__action-btn {
  padding: $uni-md-space-sm $uni-md-space-md;
  border-radius: $uni-md-radius-small;
  cursor: pointer;
  transition: background-color 150ms ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  &:active {
    background-color: rgba(255, 255, 255, 0.2);
  }
}

.md3-snackbar__action-text {
  font-size: $uni-font-size-base;
  color: #90CAF9;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

// 关闭按钮
.md3-snackbar__close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color 150ms ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  &:active {
    background-color: rgba(255, 255, 255, 0.2);
  }
}
</style>
