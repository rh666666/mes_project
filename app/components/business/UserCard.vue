<template>
  <view class="user-card" :class="[{ 'is-clickable': clickable }]" @click="handleClick">
    <Avatar
      :src="avatar"
      :name="name"
      :size="avatarSize"
      :clickable="false"
    />
    <view class="user-info">
      <text class="user-name">{{ name }}</text>
      <text v-if="role" class="user-role">{{ role }}</text>
      <text v-if="description" class="user-description">{{ description }}</text>
    </view>
    <slot name="extra" />
  </view>
</template>

<script setup lang="ts">
/**
 * 用户信息卡片组件
 * 展示用户头像、名称、角色等信息
 */

import Avatar from '@/components/ui/Avatar.vue'

type AvatarSize = 'small' | 'medium' | 'large'

interface Props {
  /** 用户头像地址 */
  avatar?: string
  /** 用户名称 */
  name: string
  /** 用户角色 */
  role?: string
  /** 描述信息 */
  description?: string
  /** 头像尺寸 */
  avatarSize?: AvatarSize
  /** 是否可点击 */
  clickable?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  avatar: '',
  role: '',
  description: '',
  avatarSize: 'large',
  clickable: false
})

const emit = defineEmits<Emits>()

/**
 * 处理点击事件
 * @param event 点击事件
 */
const handleClick = (event: MouseEvent): void => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
.user-card {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-medium;
  box-shadow: $uni-md-shadow-sm;
  transition: all $uni-md-animation-fast ease;

  &.is-clickable {
    cursor: pointer;

    &:active {
      transform: scale(0.98);
      box-shadow: $uni-md-shadow-sm;
    }
  }
}

.user-info {
  flex: 1;
  margin-left: $uni-md-space-md;
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-xs;
}

.user-name {
  font-size: $uni-font-size-lg;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.user-role {
  font-size: $uni-font-size-sm;
  color: $uni-md-color-primary;
  background-color: rgba($uni-md-color-primary, 0.1);
  padding: 2rpx 12rpx;
  border-radius: $uni-md-radius-small;
  align-self: flex-start;
}

.user-description {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}
</style>
