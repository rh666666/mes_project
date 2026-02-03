<template>
  <view
    class="md3-checkbox-wrapper"
    :class="{ 'is-disabled': disabled, 'is-checked': modelValue }"
    @click="toggle"
  >
    <!-- Checkbox 容器 -->
    <view
      class="md3-checkbox"
      :class="{
        'is-checked': modelValue,
        'is-indeterminate': indeterminate,
        'is-disabled': disabled
      }"
      :aria-checked="modelValue"
      :aria-label="ariaLabel || label"
      role="checkbox"
    >
      <!-- 选中图标 -->
      <view v-if="modelValue && !indeterminate" class="md3-checkbox__icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"
            fill="currentColor"
          />
        </svg>
      </view>
      <!-- 不确定状态图标 -->
      <view v-if="indeterminate" class="md3-checkbox__icon md3-checkbox__icon--indeterminate">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="5" y="11" width="14" height="2" fill="currentColor" />
        </svg>
      </view>
    </view>

    <!-- 标签文本 -->
    <text
      v-if="label"
      class="md3-checkbox__label"
      :class="{ 'is-disabled': disabled }"
    >
      {{ label }}
    </text>

    <!-- 默认插槽 -->
    <slot />
  </view>
</template>

<script>
/**
 * Material Design 3 Checkbox 组件
 * @component
 * @description 遵循 MD3 规范的复选框组件
 */
export default {
  name: 'Checkbox',

  props: {
    /** @type {boolean} 是否选中 */
    modelValue: {
      type: Boolean,
      default: false
    },
    /** @type {string} 标签文本 */
    label: {
      type: String,
      default: ''
    },
    /** @type {boolean} 是否禁用 */
    disabled: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 不确定状态 */
    indeterminate: {
      type: Boolean,
      default: false
    },
    /** @type {string} aria-label 用于无障碍访问 */
    ariaLabel: {
      type: String,
      default: ''
    }
  },

  emits: ['update:modelValue', 'change'],

  methods: {
    /**
     * 切换选中状态
     */
    toggle() {
      if (this.disabled) return
      const newValue = !this.modelValue
      this.$emit('update:modelValue', newValue)
      this.$emit('change', newValue)
    }
  }
}
</script>

<style lang="scss">
// MD3 Checkbox Tokens
// --md-checkbox-outline-color: --md-sys-color-on-surface-variant
// --md-checkbox-selected-container-color: --md-sys-color-primary
// --md-checkbox-selected-icon-color: --md-sys-color-on-primary
// --md-checkbox-container-shape: 2px

.md3-checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  padding: $uni-md-space-xs;
  margin: -$uni-md-space-xs;

  &.is-disabled {
    cursor: not-allowed;
    opacity: 0.38;
  }
}

.md3-checkbox {
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid $uni-md-text-secondary;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $uni-md-animation-fast ease;
  background-color: transparent;
  flex-shrink: 0;
  position: relative;

  // 选中状态
  &.is-checked {
    background-color: $uni-md-color-primary;
    border-color: $uni-md-color-primary;

    .md3-checkbox__icon {
      color: white;
    }
  }

  // 不确定状态
  &.is-indeterminate {
    background-color: $uni-md-color-primary;
    border-color: $uni-md-color-primary;

    .md3-checkbox__icon {
      color: white;
    }
  }

  // 禁用状态
  &.is-disabled {
    border-color: $uni-md-text-disabled;
    background-color: transparent;

    &.is-checked,
    &.is-indeterminate {
      background-color: $uni-md-text-disabled;
      border-color: $uni-md-text-disabled;
    }
  }

  // 激活效果
  &:active:not(.is-disabled) {
    background-color: rgba($uni-md-color-primary, 0.1);

    &.is-checked,
    &.is-indeterminate {
      background-color: $uni-md-color-primary;
    }
  }
}

.md3-checkbox__icon {
  width: 24rpx;
  height: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 100%;
    height: 100%;
  }
}

.md3-checkbox__label {
  margin-left: $uni-md-space-md;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  line-height: 1.5;

  &.is-disabled {
    color: $uni-md-text-disabled;
  }
}
</style>
