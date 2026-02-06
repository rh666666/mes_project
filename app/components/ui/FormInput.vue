<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="['form-input', { 'has-error': hasError, 'is-focused': isFocused }]"
    @input="handleInput"
    @focus="handleFocus"
    @blur="handleBlur"
  />
</template>

<script setup lang="ts">
/**
 * 表单输入框组件
 * 提供统一的输入框样式和交互行为
 */

import { ref } from 'vue'

interface Props {
  /** 输入框类型 */
  type?: 'text' | 'number' | 'email' | 'tel' | 'url' | 'password'
  /** 输入值 */
  modelValue?: string
  /** 占位符文本 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否有错误 */
  hasError?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  modelValue: '',
  placeholder: '',
  disabled: false,
  hasError: false
})

const emit = defineEmits<Emits>()

const isFocused = ref(false)

/**
 * 处理输入事件
 * @param event 输入事件
 */
const handleInput = (event: any): void => {
  emit('update:modelValue', event.detail.value)
}

/**
 * 处理聚焦事件
 * @param event 聚焦事件
 */
const handleFocus = (event: FocusEvent): void => {
  isFocused.value = true
  emit('focus', event)
}

/**
 * 处理失焦事件
 * @param event 失焦事件
 */
const handleBlur = (event: FocusEvent): void => {
  isFocused.value = false
  emit('blur', event)
}
</script>

<style lang="scss" scoped>
.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 $uni-md-space-md;
  background-color: $uni-md-surface;
  border: 1px solid $uni-md-border;
  border-radius: $uni-md-radius-medium;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  box-sizing: border-box;
  transition: all $uni-md-animation-fast ease;

  &::placeholder {
    color: $uni-md-text-tertiary;
  }

  &:focus {
    border-color: $uni-md-color-primary;
    outline: none;
  }

  &.is-focused {
    border-color: $uni-md-color-primary;
  }

  &.has-error {
    border-color: $uni-color-error;
  }

  &:disabled {
    background-color: $uni-md-surface-variant;
    color: $uni-md-text-disabled;
    cursor: not-allowed;
  }
}
</style>
