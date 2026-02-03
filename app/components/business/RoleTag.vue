<template>
  <view class="role-tag" :class="[`role-${role}`, `size-${size}`]">
    <text class="role-text">{{ displayText }}</text>
  </view>
</template>

<script setup lang="ts">
/**
 * 角色标签组件
 * 用于展示用户角色，如管理员、普通用户等
 */

import { computed } from 'vue'

type UserRole = 'admin' | 'user' | 'vip' | 'guest' | string
type TagSize = 'small' | 'medium'

interface Props {
  /** 角色类型 */
  role: UserRole
  /** 尺寸 */
  size?: TagSize
  /** 自定义显示文本 */
  customText?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  customText: ''
})

/**
 * 角色显示文本映射
 */
const roleTextMap: Record<string, string> = {
  admin: '管理员',
  user: '普通用户',
  vip: 'VIP用户',
  guest: '访客'
}

/**
 * 计算显示文本
 */
const displayText = computed(() => {
  if (props.customText) {
    return props.customText
  }
  return roleTextMap[props.role] || props.role
})
</script>

<style lang="scss" scoped>
.role-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: $uni-md-radius-small;
  font-weight: 500;

  &.size-small {
    padding: 2rpx 10rpx;
    font-size: 20rpx;
  }

  &.size-medium {
    padding: 4rpx 16rpx;
    font-size: $uni-font-size-sm;
  }

  &.role-admin {
    background-color: rgba($uni-color-error, 0.1);
    color: $uni-color-error;
  }

  &.role-user {
    background-color: rgba($uni-md-color-primary, 0.1);
    color: $uni-md-color-primary;
  }

  &.role-vip {
    background-color: rgba($uni-color-warning, 0.1);
    color: $uni-color-warning;
  }

  &.role-guest {
    background-color: $uni-md-surface-variant;
    color: $uni-md-text-secondary;
  }
}

.role-text {
  line-height: 1;
}
</style>
