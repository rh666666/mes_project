<template>
  <view class="form-input-field">
    <!-- 标签 -->
    <text v-if="label" class="field-label">{{ label }}</text>

    <!-- 输入框包装器 -->
    <view class="input-wrapper">
      <!-- 前缀图标 -->
      <MdIcon
        v-if="icon"
        :type="icon"
        :size="36"
        :color="iconColor"
        class="input-icon"
      />

      <!-- 输入框 -->
      <input
        v-if="type === 'text' || type === 'number' || type === 'password'"
        class="form-input"
        :class="{ 'with-icon': icon }"
        :value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :maxlength="maxlength"
        :disabled="disabled"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
      />

      <!-- 文本域 -->
      <textarea
        v-else-if="type === 'textarea'"
        class="form-input form-textarea"
        :class="{ 'with-icon': icon }"
        :value="modelValue"
        :placeholder="placeholder"
        :maxlength="maxlength"
        :disabled="disabled"
        :auto-height="autoHeight"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
      />

      <!-- Select 选择器 -->
      <Select
        v-else-if="type === 'select'"
        :model-value="modelValue"
        :options="options"
        :placeholder="placeholder"
        :prefix-icon="icon"
        :disabled="disabled"
        @update:model-value="onSelectChange"
      />
    </view>

    <!-- 错误提示 -->
    <text v-if="error" class="error-text">{{ error }}</text>
  </view>
</template>

<script>
/**
 * 表单输入字段组件
 * @component
 * @description 统一的表单输入框组件，支持文本输入、文本域和选择器
 */
import MdIcon from './MdIcon.vue'
import Select from './md3/Select.vue'

export default {
  name: 'FormInputField',

  components: {
    MdIcon,
    Select
  },

  props: {
    /**
     * 输入框类型
     * @type {'text' | 'number' | 'password' | 'textarea' | 'select'}
     * @default 'text'
     */
    type: {
      type: String,
      default: 'text',
      validator: (value) => ['text', 'number', 'password', 'textarea', 'select'].includes(value)
    },

    /**
     * 输入框值（支持 v-model）
     * @type {string | number}
     * @default ''
     */
    modelValue: {
      type: [String, Number],
      default: ''
    },

    /**
     * 标签文本
     * @type {string}
     * @default ''
     */
    label: {
      type: String,
      default: ''
    },

    /**
     * 占位符文本
     * @type {string}
     * @default ''
     */
    placeholder: {
      type: String,
      default: ''
    },

    /**
     * 图标类型
     * @type {string}
     * @default ''
     */
    icon: {
      type: String,
      default: ''
    },

    /**
     * 图标颜色
     * @type {string}
     * @default '#8E8E93'
     */
    iconColor: {
      type: String,
      default: '#8E8E93'
    },

    /**
     * 最大长度
     * @type {number}
     * @default 100
     */
    maxlength: {
      type: Number,
      default: 100
    },

    /**
     * 是否禁用
     * @type {boolean}
     * @default false
     */
    disabled: {
      type: Boolean,
      default: false
    },

    /**
     * 错误提示文本
     * @type {string}
     * @default ''
     */
    error: {
      type: String,
      default: ''
    },

    /**
     * 选择器选项列表（仅 type='select' 时有效）
     * @type {Array<{value: any, label: string}>}
     * @default () => []
     */
    options: {
      type: Array,
      default: () => []
    },

    /**
     * 文本域是否自动高度（仅 type='textarea' 时有效）
     * @type {boolean}
     * @default false
     */
    autoHeight: {
      type: Boolean,
      default: false
    }
  },

  emits: ['update:modelValue', 'input', 'focus', 'blur', 'change'],

  methods: {
    /**
     * 处理输入事件
     * @param {Event} event - 输入事件
     */
    onInput(event) {
      const value = event.detail.value
      this.$emit('update:modelValue', value)
      this.$emit('input', value)
    },

    /**
     * 处理选择器变更事件
     * @param {any} value - 选中的值
     */
    onSelectChange(value) {
      this.$emit('update:modelValue', value)
      this.$emit('change', value)
    },

    /**
     * 处理聚焦事件
     * @param {Event} event - 聚焦事件
     */
    onFocus(event) {
      this.$emit('focus', event)
    },

    /**
     * 处理失焦事件
     * @param {Event} event - 失焦事件
     */
    onBlur(event) {
      this.$emit('blur', event)
    }
  }
}
</script>

<style lang="scss" scoped>
.form-input-field {
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-sm;

  &:last-child {
    margin-bottom: 0;
  }
}

.field-label {
  font-size: $uni-font-size-sm;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: $uni-md-space-md;
  z-index: 1;
}

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
  transition: border-color $uni-md-animation-fast ease;

  &.with-icon {
    padding-left: 80rpx;
  }

  &:focus {
    border-color: $uni-md-color-primary;
    outline: none;
  }

  &:disabled {
    background-color: $uni-md-surface-variant;
    color: $uni-md-text-disabled;
    cursor: not-allowed;
  }
}

.form-textarea {
  height: auto;
  min-height: 176rpx;
  padding: $uni-md-space-md;

  &.with-icon {
    padding-left: 80rpx;
    padding-top: $uni-md-space-md;
  }
}

.error-text {
  font-size: $uni-font-size-sm;
  color: $uni-color-error;
  margin-top: 4rpx;
}
</style>
