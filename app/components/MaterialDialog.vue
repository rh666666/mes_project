<template>
  <view v-if="visible" class="dialog-overlay" @click="onOverlayClick">
    <view class="dialog-container" @click.stop>
      <view class="dialog-content">
        <text v-if="title" class="dialog-title">{{ title }}</text>
        <text v-if="content" class="dialog-message">{{ content }}</text>
        <slot></slot>
      </view>
      <view class="dialog-actions">
        <view
          v-if="showCancel"
          class="dialog-btn dialog-btn-cancel"
          @click="onCancel"
        >
          <text class="dialog-btn-text">{{ cancelText }}</text>
        </view>
        <view
          class="dialog-btn dialog-btn-confirm"
          :class="{ 'dialog-btn-full': !showCancel }"
          @click="onConfirm"
        >
          <text class="dialog-btn-text dialog-btn-text-confirm">{{ confirmText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MaterialDialog',

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    content: {
      type: String,
      default: ''
    },
    confirmText: {
      type: String,
      default: '确定'
    },
    cancelText: {
      type: String,
      default: '取消'
    },
    showCancel: {
      type: Boolean,
      default: true
    },
    closeOnOverlayClick: {
      type: Boolean,
      default: false
    }
  },

  methods: {
    onOverlayClick() {
      if (this.closeOnOverlayClick) {
        this.onCancel();
      }
    },
    onConfirm() {
      this.$emit('confirm');
    },
    onCancel() {
      this.$emit('cancel');
    }
  }
};
</script>

<style lang="scss">
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn $uni-md-animation-fast ease;
}

.dialog-container {
  width: 80%;
  max-width: 320px;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-lg;
  overflow: hidden;
  animation: scaleIn $uni-md-animation-normal ease;
}

.dialog-content {
  padding: $uni-md-space-xl;
}

.dialog-title {
  display: block;
  font-size: $uni-font-size-lg;
  font-weight: 600;
  color: $uni-md-text-primary;
  margin-bottom: $uni-md-space-md;
}

.dialog-message {
  display: block;
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  border-top: 1px solid $uni-md-divider;
}

.dialog-btn {
  flex: 1;
  padding: $uni-md-space-md;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color $uni-md-animation-fast ease;

  &:active {
    background-color: $uni-md-surface-variant;
  }

  & + .dialog-btn {
    border-left: 1px solid $uni-md-divider;
  }
}

.dialog-btn-cancel {
  .dialog-btn-text {
    color: $uni-md-text-secondary;
  }
}

.dialog-btn-confirm {
  .dialog-btn-text {
    color: $uni-md-color-primary;
    font-weight: 600;
  }
}

.dialog-btn-full {
  flex: 1;
}

.dialog-btn-text {
  font-size: $uni-font-size-base;
}

.dialog-btn-text-confirm {
  color: $uni-md-color-primary;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
