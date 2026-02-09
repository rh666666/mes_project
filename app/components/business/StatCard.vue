<template>
  <wd-card :class="[`stat-card variant-${variant}`]">
    <view class="stat-content">
      <wd-icon v-if="icon" :name="icon" size="32" class="stat-icon" />
      <view class="stat-info">
        <text class="stat-value">{{ formattedValue }}</text>
        <text class="stat-label">{{ label }}</text>
      </view>
      <wd-tag
        v-if="trend !== undefined"
        :type="trend >= 0 ? 'success' : 'danger'"
        size="small"
      >
        {{ trend >= 0 ? '+' : '' }}{{ trend }}%
      </wd-tag>
    </view>
  </wd-card>
</template>

<script>
/**
 * 统计卡片组件
 * 用于展示统计数据，如用户数量、订单数量等
 * 基于 wd-card 组件封装
 */

export default {
  name: 'StatCard',

  props: {
    /** 数值 */
    value: {
      type: Number,
      required: true
    },
    /** 标签 */
    label: {
      type: String,
      required: true
    },
    /** 图标名称 */
    icon: {
      type: String,
      default: ''
    },
    /** 趋势百分比 */
    trend: {
      type: Number,
      default: undefined
    },
    /** 变体样式 */
    variant: {
      type: String,
      default: 'default'
    }
  },

  computed: {
    /**
     * 格式化数值显示
     * @returns {string}
     */
    formattedValue() {
      if (this.value >= 10000) {
        return (this.value / 10000).toFixed(1) + 'w'
      }
      if (this.value >= 1000) {
        return (this.value / 1000).toFixed(1) + 'k'
      }
      return this.value.toString()
    }
  }
}
</script>

<style lang="scss" scoped>
.stat-card {
  margin-bottom: 0;

  &.variant-primary .stat-value {
    color: $uni-color-primary;
  }

  &.variant-success .stat-value {
    color: $uni-color-success;
  }

  &.variant-warning .stat-value {
    color: $uni-color-warning;
  }

  &.variant-error .stat-value {
    color: $uni-color-error;
  }
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx;
}

.stat-icon {
  color: $uni-text-color-grey;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 600;
  color: $uni-text-color;
}

.stat-label {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}
</style>
