<template>
  <view class="stat-card" :class="[`variant-${variant}`]">
    <view class="stat-icon" v-if="icon">
      <text>{{ icon }}</text>
    </view>
    <view class="stat-content">
      <text class="stat-value">{{ formattedValue }}</text>
      <text class="stat-label">{{ label }}</text>
    </view>
    <view v-if="trend !== undefined" class="stat-trend" :class="{ 'is-positive': trend >= 0, 'is-negative': trend < 0 }">
      <text>{{ trend >= 0 ? '+' : '' }}{{ trend }}%</text>
    </view>
  </view>
</template>

<script setup lang="ts">
/**
 * 统计卡片组件
 * 用于展示统计数据，如用户数量、订单数量等
 */

import { computed } from 'vue'

type CardVariant = 'default' | 'primary' | 'success' | 'warning' | 'error'

interface Props {
  /** 数值 */
  value: number
  /** 标签 */
  label: string
  /** 图标（emoji） */
  icon?: string
  /** 趋势百分比 */
  trend?: number
  /** 变体样式 */
  variant?: CardVariant
}

const props = withDefaults(defineProps<Props>(), {
  icon: '',
  trend: undefined,
  variant: 'default'
})

/**
 * 格式化数值显示
 */
const formattedValue = computed(() => {
  if (props.value >= 10000) {
    return (props.value / 10000).toFixed(1) + 'w'
  }
  if (props.value >= 1000) {
    return (props.value / 1000).toFixed(1) + 'k'
  }
  return props.value.toString()
})
</script>

<style lang="scss" scoped>
.stat-card {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-medium;
  box-shadow: $uni-md-shadow-sm;
  gap: $uni-md-space-md;

  &.variant-primary {
    background-color: rgba($uni-md-color-primary, 0.1);

    .stat-icon {
      background-color: $uni-md-color-primary;
    }

    .stat-value {
      color: $uni-md-color-primary;
    }
  }

  &.variant-success {
    background-color: rgba($uni-color-success, 0.1);

    .stat-icon {
      background-color: $uni-color-success;
    }

    .stat-value {
      color: $uni-color-success;
    }
  }

  &.variant-warning {
    background-color: rgba($uni-color-warning, 0.1);

    .stat-icon {
      background-color: $uni-color-warning;
    }

    .stat-value {
      color: $uni-color-warning;
    }
  }

  &.variant-error {
    background-color: rgba($uni-color-error, 0.1);

    .stat-icon {
      background-color: $uni-color-error;
    }

    .stat-value {
      color: $uni-color-error;
    }
  }
}

.stat-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: $uni-md-radius-medium;
  background-color: $uni-md-surface-variant;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-xs;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 600;
  color: $uni-md-text-primary;
}

.stat-label {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.stat-trend {
  font-size: $uni-font-size-sm;
  font-weight: 500;
  padding: 4rpx 12rpx;
  border-radius: $uni-md-radius-small;

  &.is-positive {
    color: $uni-color-success;
    background-color: rgba($uni-color-success, 0.1);
  }

  &.is-negative {
    color: $uni-color-error;
    background-color: rgba($uni-color-error, 0.1);
  }
}
</style>
