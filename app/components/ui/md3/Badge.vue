<template>
  <view class="badge-wrapper">
    <slot />
    <view
      v-if="visible"
      class="badge"
      :class="[`badge--${variant}`, { 'badge--dot': variant === 'small' }]"
    >
      <text v-if="variant === 'large' && displayContent" class="badge-text">
        {{ displayContent }}
      </text>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 Badge 组件
 * @component
 * @description 用于显示通知、计数或状态信息的徽章组件
 */
export default {
  name: 'Badge',

  props: {
    /**
     * 徽章变体类型
     * @type {'small' | 'large'}
     * @default 'small'
     */
    variant: {
      type: String,
      default: 'small',
      validator(value) {
        return ['small', 'large'].includes(value);
      }
    },

    /**
     * 徽章内容（仅 large 类型有效）
     * @type {string | number}
     * @default ''
     */
    content: {
      type: [String, Number],
      default: ''
    },

    /**
     * 是否显示徽章
     * @type {boolean}
     * @default true
     */
    visible: {
      type: Boolean,
      default: true
    },

    /**
     * 数字最大值，超过显示为 {max}+
     * @type {number}
     * @default 99
     */
    max: {
      type: Number,
      default: 99
    }
  },

  computed: {
    /**
     * 处理后的显示内容
     * @returns {string}
     */
    displayContent() {
      if (typeof this.content === 'number') {
        return this.content > this.max ? `${this.max}+` : String(this.content);
      }
      return this.content;
    }
  }
};
</script>

<style lang="scss">
.badge-wrapper {
  position: relative;
  display: inline-flex;
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(50%, -50%);
  background-color: $uni-color-error;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;

  &--small {
    width: 16rpx;
    height: 16rpx;
    border-radius: 50%;
    min-width: 16rpx;
    min-height: 16rpx;
  }

  &--large {
    height: 32rpx;
    min-width: 32rpx;
    padding: 0 12rpx;
    border-radius: $uni-md-radius-full;
  }
}

.badge-text {
  font-size: 20rpx;
  font-weight: 600;
  color: #ffffff;
  line-height: 1;
}
</style>
