<template>
  <view class="empty-state" :class="[`size-${size}`]">
    <view class="empty-icon">
      <text v-if="icon">{{ icon }}</text>
      <slot v-else name="icon" />
    </view>
    <text v-if="title" class="empty-title">{{ title }}</text>
    <text v-if="description" class="empty-description">{{ description }}</text>
    <slot />
  </view>
</template>

<script setup lang="ts">
/**
 * 空状态组件
 * 用于页面内容为空或功能开发中的占位展示
 */

type EmptySize = 'small' | 'medium' | 'large'

interface Props {
  /** 图标（可以是emoji或文本） */
  icon?: string
  /** 标题 */
  title?: string
  /** 描述文本 */
  description?: string
  /** 尺寸 */
  size?: EmptySize
}

withDefaults(defineProps<Props>(), {
  icon: '📦',
  title: '',
  description: '',
  size: 'medium'
})
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $uni-md-space-xl;
  text-align: center;

  &.size-small {
    padding: $uni-md-space-md;

    .empty-icon {
      font-size: 48rpx;
      margin-bottom: $uni-md-space-sm;
    }

    .empty-title {
      font-size: $uni-font-size-base;
    }

    .empty-description {
      font-size: $uni-font-size-sm;
    }
  }

  &.size-medium {
    padding: $uni-md-space-xl;

    .empty-icon {
      font-size: 96rpx;
      margin-bottom: $uni-md-space-md;
    }

    .empty-title {
      font-size: $uni-font-size-lg;
    }

    .empty-description {
      font-size: $uni-font-size-base;
    }
  }

  &.size-large {
    padding: $uni-md-space-2xl;

    .empty-icon {
      font-size: 144rpx;
      margin-bottom: $uni-md-space-lg;
    }

    .empty-title {
      font-size: 20px;
    }

    .empty-description {
      font-size: $uni-font-size-lg;
    }
  }
}

.empty-icon {
  opacity: 0.6;
}

.empty-title {
  color: $uni-md-text-primary;
  font-weight: 500;
  margin-bottom: $uni-md-space-sm;
}

.empty-description {
  color: $uni-md-text-secondary;
  line-height: 1.5;
}
</style>
