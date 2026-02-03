<template>
  <view class="form-item" :class="{ 'has-error': hasError }">
    <text v-if="label" class="form-label">{{ label }}</text>
    <slot />
    <text v-if="errorMessage" class="form-error">{{ errorMessage }}</text>
  </view>
</template>

<script setup lang="ts">
/**
 * 表单项容器组件
 * 提供统一的表单项布局，包括标签、输入区域和错误提示
 */

interface Props {
  /** 标签文本 */
  label?: string
  /** 是否有错误 */
  hasError?: boolean
  /** 错误提示信息 */
  errorMessage?: string
}

withDefaults(defineProps<Props>(), {
  label: '',
  hasError: false,
  errorMessage: ''
})
</script>

<style lang="scss" scoped>
.form-item {
  margin-bottom: $uni-md-space-lg;
  position: relative;

  &:last-child {
    margin-bottom: 0;
  }

  &.has-error {
    :deep(.form-input) {
      border-color: $uni-color-error;
    }
  }
}

.form-label {
  display: block;
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
  margin-bottom: $uni-md-space-sm;
}

.form-error {
  display: block;
  font-size: $uni-font-size-sm;
  color: $uni-color-error;
  margin-top: $uni-md-space-xs;
}
</style>
