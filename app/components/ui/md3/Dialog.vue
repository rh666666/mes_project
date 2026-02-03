<template>
  <view
    v-if="visible"
    class="md3-dialog-overlay"
    :class="{ 'is-open': isOpen }"
    @click="onOverlayClick"
  >
    <view
      class="md3-dialog-container"
      role="dialog"
      :aria-label="ariaLabel || title"
      @click.stop
    >
      <!-- headline slot: 标题 -->
      <view v-if="$slots.headline || title" class="md3-dialog__headline">
        <slot name="headline">
          <text class="md3-dialog__headline-text">{{ title }}</text>
        </slot>
      </view>

      <!-- content slot: 内容 -->
      <view class="md3-dialog__content">
        <slot name="content">
          <text v-if="content" class="md3-dialog__supporting-text">{{ content }}</text>
        </slot>
        <slot></slot>
      </view>

      <!-- actions slot: 操作按钮 -->
      <view v-if="$slots.actions || showActions" class="md3-dialog__actions">
        <slot name="actions">
          <view
            v-if="showCancel"
            class="md3-dialog__action-btn md3-dialog__action-btn--cancel"
            @click="onCancel"
          >
            <text class="md3-dialog__action-btn-text">{{ cancelText }}</text>
          </view>
          <view
            class="md3-dialog__action-btn md3-dialog__action-btn--confirm"
            @click="onConfirm"
          >
            <text class="md3-dialog__action-btn-text md3-dialog__action-btn-text--confirm">{{ confirmText }}</text>
          </view>
        </slot>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 Dialog 组件
 * @component
 * @description 遵循 MD3 规范的对话框组件，支持 headline、content、actions slot
 */
export default {
  name: 'Dialog',

  props: {
    /** @type {boolean} 是否可见 */
    visible: {
      type: Boolean,
      default: false
    },
    /** @type {string} 标题 */
    title: {
      type: String,
      default: ''
    },
    /** @type {string} 内容文本 */
    content: {
      type: String,
      default: ''
    },
    /** @type {string} 确认按钮文本 */
    confirmText: {
      type: String,
      default: '确定'
    },
    /** @type {string} 取消按钮文本 */
    cancelText: {
      type: String,
      default: '取消'
    },
    /** @type {boolean} 是否显示取消按钮 */
    showCancel: {
      type: Boolean,
      default: true
    },
    /** @type {boolean} 是否显示操作按钮 */
    showActions: {
      type: Boolean,
      default: true
    },
    /** @type {boolean} 点击遮罩是否关闭 */
    closeOnOverlayClick: {
      type: Boolean,
      default: false
    },
    /** @type {string} aria-label 用于无障碍访问 */
    ariaLabel: {
      type: String,
      default: ''
    },
    /** @type {string} 对话框类型（alert 或默认） */
    type: {
      type: String,
      default: ''
    }
  },

  emits: ['confirm', 'cancel', 'update:visible'],

  data() {
    return {
      isOpen: false
    }
  },

  watch: {
    visible: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            setTimeout(() => {
              this.isOpen = true
            }, 10)
          })
        } else {
          this.isOpen = false
        }
      }
    }
  },

  methods: {
    /**
     * 处理遮罩点击事件
     */
    onOverlayClick() {
      if (this.closeOnOverlayClick) {
        this.onCancel()
      }
    },

    /**
     * 处理确认按钮点击
     */
    onConfirm() {
      this.$emit('confirm')
      this.$emit('update:visible', false)
    },

    /**
     * 处理取消按钮点击
     */
    onCancel() {
      this.$emit('cancel')
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style lang="scss">
// MD3 Dialog Tokens
// --md-dialog-container-color: --md-sys-color-surface-container-high
// --md-dialog-headline-color: --md-sys-color-on-surface
// --md-dialog-headline-font: --md-sys-typescale-headline-small-font
// --md-dialog-supporting-text-color: --md-sys-color-on-surface-variant
// --md-dialog-supporting-text-font: --md-sys-typescale-body-medium-font

.md3-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: background-color $uni-md-animation-normal ease;

  &.is-open {
    background-color: rgba(0, 0, 0, 0.5);
  }
}

.md3-dialog-container {
  width: min(560rpx, 90%);
  max-width: 560rpx;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-lg;
  overflow: hidden;
  opacity: 0;
  transform: scale(0.8);
  transition: opacity $uni-md-animation-normal ease, transform $uni-md-animation-normal ease;

  .md3-dialog-overlay.is-open & {
    opacity: 1;
    transform: scale(1);
  }
}

.md3-dialog__headline {
  padding: $uni-md-space-xl $uni-md-space-xl $uni-md-space-md;
}

.md3-dialog__headline-text {
  font-size: $uni-font-size-lg;
  font-weight: 500;
  color: $uni-md-text-primary;
  line-height: 1.5;
}

.md3-dialog__content {
  padding: 0 $uni-md-space-xl $uni-md-space-xl;
}

.md3-dialog__supporting-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  line-height: 1.5;
}

.md3-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-md $uni-md-space-lg;
}

.md3-dialog__action-btn {
  padding: $uni-md-space-sm $uni-md-space-md;
  border-radius: $uni-md-radius-small;
  transition: background-color $uni-md-animation-fast ease;

  &:active {
    background-color: rgba($uni-md-color-primary, 0.1);
  }
}

.md3-dialog__action-btn--cancel {
  .md3-dialog__action-btn-text {
    color: $uni-md-text-secondary;
  }

  &:active {
    background-color: $uni-md-surface-variant;
  }
}

.md3-dialog__action-btn--confirm {
  .md3-dialog__action-btn-text {
    color: $uni-md-color-primary;
    font-weight: 500;
  }
}

.md3-dialog__action-btn-text {
  font-size: $uni-font-size-base;
}

.md3-dialog__action-btn-text--confirm {
  color: $uni-md-color-primary;
}
</style>
