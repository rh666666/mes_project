<template>
  <view class="checkbox-wrapper" @click="toggle">
    <view
      class="checkbox"
      :class="{ 'is-checked': modelValue, 'is-disabled': disabled }"
    >
      <text v-if="modelValue" class="check-icon">✓</text>
    </view>
    <text v-if="label" class="checkbox-label" :class="{ 'is-disabled': disabled }">
      {{ label }}
    </text>
    <slot />
  </view>
</template>

<script setup lang="ts">
/**
 * 复选框组件
 * 提供统一的复选框样式和交互
 */

interface Props {
  /** 是否选中 */
  modelValue: boolean
  /** 标签文本 */
  label?: string
  /** 是否禁用 */
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'change', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  disabled: false
})

const emit = defineEmits<Emits>()

/**
 * 切换选中状态
 */
const toggle = (): void => {
  if (props.disabled) return
  const newValue = !props.modelValue
  emit('update:modelValue', newValue)
  emit('change', newValue)
}
</script>

<style lang="scss" scoped>
.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid $uni-md-border;
  border-radius: $uni-md-radius-small;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $uni-md-animation-fast ease;
  background-color: $uni-md-surface;
  flex-shrink: 0;

  &.is-checked {
    background-color: $uni-md-color-primary;
    border-color: $uni-md-color-primary;
  }

  &.is-disabled {
    background-color: $uni-md-surface-variant;
    border-color: $uni-md-border;
    cursor: not-allowed;

    &.is-checked {
      background-color: $uni-md-text-disabled;
      border-color: $uni-md-text-disabled;
    }
  }
}

.check-icon {
  color: white;
  font-size: 24rpx;
  font-weight: bold;
}

.checkbox-label {
  margin-left: $uni-md-space-sm;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &.is-disabled {
    color: $uni-md-text-disabled;
  }
}
</style>
