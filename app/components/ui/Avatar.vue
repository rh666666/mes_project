<template>
  <view
    class="avatar"
    :class="[`size-${size}`, { 'is-clickable': clickable }]"
    :style="avatarStyle"
    @click="handleClick"
  >
    <image
      v-if="src"
      class="avatar-image"
      :src="src"
      :mode="mode"
      @error="handleImageError"
    />
    <text v-else class="avatar-text">{{ displayText }}</text>
  </view>
</template>

<script setup lang="ts">
/**
 * 头像组件
 * 支持图片显示和文字回退，统一的头像样式
 */

import { computed } from 'vue'

type AvatarSize = 'small' | 'medium' | 'large' | 'xlarge'
type ImageMode = 'scaleToFill' | 'aspectFit' | 'aspectFill' | 'widthFix' | 'heightFix' | 'top' | 'bottom' | 'center' | 'left' | 'right' | 'top left' | 'top right' | 'bottom left' | 'bottom right'

interface Props {
  /** 图片地址 */
  src?: string
  /** 名称（用于生成文字头像） */
  name?: string
  /** 尺寸 */
  size?: AvatarSize
  /** 图片裁剪模式 */
  mode?: ImageMode
  /** 是否可点击 */
  clickable?: boolean
  /** 背景色 */
  backgroundColor?: string
}

interface Emits {
  (e: 'click', event: MouseEvent): void
  (e: 'error'): void
}

const props = withDefaults(defineProps<Props>(), {
  src: '',
  name: '',
  size: 'medium',
  mode: 'aspectFill',
  clickable: false,
  backgroundColor: ''
})

const emit = defineEmits<Emits>()

/**
 * 计算头像尺寸
 */
const sizeMap = {
  small: { width: '64rpx', height: '64rpx', fontSize: '28rpx' },
  medium: { width: '96rpx', height: '96rpx', fontSize: '40rpx' },
  large: { width: '128rpx', height: '128rpx', fontSize: '56rpx' },
  xlarge: { width: '160rpx', height: '160rpx', fontSize: '72rpx' }
}

/**
 * 计算显示的文字（取名称首字）
 */
const displayText = computed(() => {
  if (!props.name) return '?'
  return props.name.charAt(0).toUpperCase()
})

/**
 * 计算头像样式
 */
const avatarStyle = computed(() => {
  const size = sizeMap[props.size]
  const bgColor = props.backgroundColor || getDefaultBackgroundColor()

  return {
    width: size.width,
    height: size.height,
    backgroundColor: bgColor,
    fontSize: size.fontSize
  }
})

/**
 * 获取默认背景色（根据名称生成固定颜色）
 * @returns 背景色
 */
const getDefaultBackgroundColor = (): string => {
  const colors = [
    '#1976D2', '#388E3C', '#F57C00', '#7B1FA2',
    '#5D4037', '#00796B', '#C62828', '#303F9F'
  ]
  if (!props.name) return colors[0]
  const index = props.name.charCodeAt(0) % colors.length
  return colors[index]
}

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
 * 处理图片加载错误
 */
const handleImageError = (): void => {
  emit('error')
}
</script>

<style lang="scss" scoped>
.avatar {
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  transition: transform $uni-md-animation-fast ease;

  &.is-clickable {
    cursor: pointer;

    &:active {
      transform: scale(0.95);
    }
  }

}

.avatar-image {
  width: 100%;
  height: 100%;
}

.avatar-text {
  color: white;
  font-weight: 500;
}
</style>
