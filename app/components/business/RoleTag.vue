<template>
  <Tag :text="displayText" :variant="variant" :size="size" />
</template>

<script setup lang="ts">
/**
 * 角色标签组件
 * 用于展示用户角色，如管理员、普通用户等
 * 基于 Tag 组件封装
 */

import { computed } from 'vue'
import Tag from '@/components/ui/Tag.vue'

type UserRole = 'admin' | 'user' | 'vip' | 'guest' | string
type TagSize = 'small' | 'medium' | 'large'

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

/**
 * 角色对应的标签变体
 */
const variant = computed(() => {
  const variantMap: Record<string, string> = {
    admin: 'error',
    user: 'primary',
    vip: 'warning',
    guest: 'default'
  }
  return variantMap[props.role] || 'default'
})
</script>
