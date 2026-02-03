<template>
  <view class="password-input-wrapper">
    <FormInput
      :type="showPassword ? 'text' : 'password'"
      :model-value="modelValue"
      :placeholder="placeholder"
      :has-error="hasError"
      @update:model-value="$emit('update:modelValue', $event)"
    />
    <view class="password-toggle" @click="togglePassword">
      <UniIcons
        :type="showPassword ? 'eye-slash' : 'eye'"
        size="20"
        color="#999"
      />
    </view>
  </view>
</template>

<script setup lang="ts">
/**
 * 密码输入框组件
 * 带显示/隐藏密码切换功能
 */

import { ref } from 'vue'
import FormInput from './FormInput.vue'
// @ts-ignore
import UniIcons from '@dcloudio/uni-ui/lib/uni-icons/uni-icons.vue'

interface Props {
  /** 输入值 */
  modelValue?: string
  /** 占位符文本 */
  placeholder?: string
  /** 是否有错误 */
  hasError?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '请输入密码',
  hasError: false
})

defineEmits<Emits>()

const showPassword = ref(false)

/**
 * 切换密码显示状态
 */
const togglePassword = (): void => {
  showPassword.value = !showPassword.value
}
</script>

<style lang="scss" scoped>
.password-input-wrapper {
  position: relative;
  width: 100%;
}

.password-toggle {
  position: absolute;
  right: $uni-md-space-md;
  top: 50%;
  transform: translateY(-50%);
  padding: $uni-md-space-xs;
  cursor: pointer;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
