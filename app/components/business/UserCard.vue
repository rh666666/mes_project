<template>
  <view
    class="user-card"
    :class="[{ 'is-clickable': clickable }]"
    @click="handleClick"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <view
      v-if="clickable"
      class="ripple-container"
      :class="{ 'is-animating': isRippling }"
      :style="rippleStyle"
    />
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

import { ref, computed } from 'vue'
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

/** 是否正在显示 Ripple 动画 */
const isRippling = ref(false)
/** Ripple 位置 */
const rippleX = ref(0)
const rippleY = ref(0)

/** Ripple 样式 */
const rippleStyle = computed(() => ({
  left: `${rippleX.value}px`,
  top: `${rippleY.value}px`
}))

/**
 * 处理点击事件
 * @param event 点击事件
 */
const handleClick = (event: MouseEvent): void => {
  if (props.clickable) {
    emit('click', event)
  }
}

/**
 * 处理触摸开始事件
 * @param event 触摸事件
 */
const handleTouchStart = (event: TouchEvent): void => {
  if (!props.clickable) return
  const touch = event.touches[0]
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  rippleX.value = touch.clientX - rect.left
  rippleY.value = touch.clientY - rect.top
  isRippling.value = true
}

/**
 * 处理触摸结束事件
 */
const handleTouchEnd = (): void => {
  setTimeout(() => {
    isRippling.value = false
  }, 300)
}
</script>

<style lang="scss" scoped>
.user-card {
  position: relative;
  display: flex;
  align-items: center;
  padding: $uni-md-space-md;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-medium;
  box-shadow: $uni-md-shadow-sm;
  transition: all $uni-md-animation-fast ease;
  overflow: hidden;

  &.is-clickable {
    cursor: pointer;

    &:active {
      transform: scale(0.98);
      box-shadow: $uni-md-shadow-sm;
    }
  }
}

.ripple-container {
  position: absolute;
  border-radius: 50%;
  background-color: rgba($uni-md-text-primary, 0.1);
  transform: scale(0);
  pointer-events: none;
  width: 200px;
  height: 200px;
  margin-left: -100px;
  margin-top: -100px;

  &.is-animating {
    animation: ripple-effect 300ms ease-out;
  }
}

@keyframes ripple-effect {
  0% {
    transform: scale(0);
    opacity: 0.5;
  }
  100% {
    transform: scale(2);
    opacity: 0;
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
