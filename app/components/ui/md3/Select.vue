<template>
  <view class="md3-select" :class="[`variant-${variant}`, { 'is-open': isOpen, 'is-disabled': disabled, 'is-error': error }]">
    <!-- Filled 变体 -->
    <template v-if="variant === 'filled'">
      <view
        class="md3-select__container md3-select__container--filled"
        @click="toggleDropdown"
      >
        <!-- 前缀图标 -->
        <view v-if="prefixIcon" class="md3-select__prefix">
          <MdIcon :type="prefixIcon" :size="20" :color="iconColor" />
        </view>

        <!-- 文本区域 -->
        <view class="md3-select__text-field">
          <text
            class="md3-select__label"
            :class="{ 'is-floating': isLabelFloating }"
          >{{ label }}</text>
          <text
            class="md3-select__value"
            :class="{ 'is-placeholder': !selectedLabel }"
          >{{ selectedLabel || placeholder }}</text>
        </view>

        <!-- 后缀图标 -->
        <view class="md3-select__suffix">
          <MdIcon
            type="arrow_drop_down"
            :size="24"
            :color="iconColor"
            :class="{ 'is-rotated': isOpen }"
          />
        </view>
      </view>
    </template>

    <!-- Outlined 变体 -->
    <template v-else>
      <view
        class="md3-select__container md3-select__container--outlined"
        @click="toggleDropdown"
      >
        <!-- 前缀图标 -->
        <view v-if="prefixIcon" class="md3-select__prefix">
          <MdIcon :type="prefixIcon" :size="20" :color="iconColor" />
        </view>

        <!-- 文本区域 -->
        <view class="md3-select__text-field">
          <text
            class="md3-select__label"
            :class="{ 'is-floating': isLabelFloating }"
          >{{ label }}</text>
          <text
            class="md3-select__value"
            :class="{ 'is-placeholder': !selectedLabel }"
          >{{ selectedLabel || placeholder }}</text>
        </view>

        <!-- 后缀图标 -->
        <view class="md3-select__suffix">
          <MdIcon
            type="arrow_drop_down"
            :size="24"
            :color="iconColor"
            :class="{ 'is-rotated': isOpen }"
          />
        </view>

        <!-- 边框 -->
        <view class="md3-select__outline">
          <view class="md3-select__outline-leading"></view>
          <view class="md3-select__outline-notch" :class="{ 'is-floating': isLabelFloating }">
            <text v-if="isLabelFloating" class="md3-select__outline-label">{{ label }}</text>
          </view>
          <view class="md3-select__outline-trailing"></view>
        </view>
      </view>
    </template>

    <!-- 下拉菜单 -->
    <view v-if="isOpen" class="md3-select__menu-overlay" @click="closeDropdown">
      <view class="md3-select__menu" :style="menuStyle" @click.stop>
        <scroll-view scroll-y class="md3-select__menu-scroll">
          <view
            v-for="(option, index) in options"
            :key="getOptionKey(option, index)"
            class="md3-select__menu-item"
            :class="{ 'is-selected': isSelected(option) }"
            @click="selectOption(option)"
          >
            <text class="md3-select__menu-item-text">{{ getOptionLabel(option) }}</text>
            <MdIcon
              v-if="isSelected(option)"
              type="check"
              :size="18"
              :color="checkIconColor"
            />
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 支持文本 -->
    <text v-if="supportingText" class="md3-select__supporting-text">{{ supportingText }}</text>
  </view>
</template>

<script>
/**
 * Material Design 3 Select 组件
 * @component
 * @description 下拉选择器组件，支持 Filled 和 Outlined 两种变体
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {Object} SelectOption
 * @property {string|number} value - 选项值
 * @property {string} label - 选项标签
 */

export default {
  name: 'Select',

  components: {
    MdIcon
  },

  props: {
    /**
     * 当前选中值
     * @type {string|number|null}
     */
    modelValue: {
      type: [String, Number, null],
      default: null
    },

    /**
     * 选项列表
     * @type {Array<SelectOption|string>}
     */
    options: {
      type: Array,
      default: () => []
    },

    /**
     * 标签文本
     * @type {string}
     */
    label: {
      type: String,
      default: ''
    },

    /**
     * 样式变体
     * @type {'filled'|'outlined'}
     */
    variant: {
      type: String,
      default: 'filled',
      validator: (value) => ['filled', 'outlined'].includes(value)
    },

    /**
     * 是否禁用
     * @type {boolean}
     */
    disabled: {
      type: Boolean,
      default: false
    },

    /**
     * 是否错误状态
     * @type {boolean}
     */
    error: {
      type: Boolean,
      default: false
    },

    /**
     * 占位文本
     * @type {string}
     */
    placeholder: {
      type: String,
      default: ''
    },

    /**
     * 前缀图标
     * @type {string}
     */
    prefixIcon: {
      type: String,
      default: ''
    },

    /**
     * 支持文本
     * @type {string}
     */
    supportingText: {
      type: String,
      default: ''
    }
  },

  emits: ['update:modelValue', 'change'],

  data() {
    return {
      isOpen: false,
      menuStyle: {}
    }
  },

  computed: {
    /**
     * 标签是否浮动
     * @returns {boolean}
     */
    isLabelFloating() {
      return this.modelValue !== null && this.modelValue !== undefined && this.modelValue !== ''
    },

    /**
     * 当前选中项的标签
     * @returns {string}
     */
    selectedLabel() {
      const selected = this.options.find(opt => this.getOptionValue(opt) === this.modelValue)
      return selected ? this.getOptionLabel(selected) : ''
    },

    /**
     * 图标颜色
     * @returns {string}
     */
    iconColor() {
      if (this.disabled) {
        return '#C7C7CC'
      }
      if (this.error) {
        return '#B3261E'
      }
      return '#6E6E73'
    },

    /**
     * 选中图标颜色
     * @returns {string}
     */
    checkIconColor() {
      return '#1976D2'
    }
  },

  methods: {
    /**
     * 切换下拉菜单
     */
    toggleDropdown() {
      if (this.disabled) return
      this.isOpen = !this.isOpen
    },

    /**
     * 关闭下拉菜单
     */
    closeDropdown() {
      this.isOpen = false
    },

    /**
     * 选择选项
     * @param {SelectOption|string} option - 选中的选项
     */
    selectOption(option) {
      const value = this.getOptionValue(option)
      this.$emit('update:modelValue', value)
      this.$emit('change', value)
      this.closeDropdown()
    },

    /**
     * 获取选项值
     * @param {SelectOption|string} option - 选项
     * @returns {string|number}
     */
    getOptionValue(option) {
      if (typeof option === 'object' && option !== null) {
        return option.value
      }
      return option
    },

    /**
     * 获取选项标签
     * @param {SelectOption|string} option - 选项
     * @returns {string}
     */
    getOptionLabel(option) {
      if (typeof option === 'object' && option !== null) {
        return option.label
      }
      return String(option)
    },

    /**
     * 获取选项键
     * @param {SelectOption|string} option - 选项
     * @param {number} index - 索引
     * @returns {string}
     */
    getOptionKey(option, index) {
      return `${this.getOptionValue(option)}-${index}`
    },

    /**
     * 判断选项是否被选中
     * @param {SelectOption|string} option - 选项
     * @returns {boolean}
     */
    isSelected(option) {
      return this.getOptionValue(option) === this.modelValue
    }
  }
}
</script>

<style lang="scss">
.md3-select {
  position: relative;
  width: 100%;
}

// 容器基础样式
.md3-select__container {
  display: flex;
  align-items: center;
  min-height: 56px;
  padding: 0 $uni-md-space-md;
  cursor: pointer;
  transition: all $uni-md-animation-fast ease;

  &--filled {
    background-color: $uni-md-surface-variant;
    border-radius: $uni-md-radius-small $uni-md-radius-small 0 0;
    border-bottom: 1px solid $uni-md-border;

    &:hover:not(.is-disabled) {
      background-color: darken($uni-md-surface-variant, 3%);
    }

    .md3-select.is-open & {
      border-bottom-color: $uni-md-color-primary;
      border-bottom-width: 2px;
    }

    .md3-select.is-error & {
      border-bottom-color: #B3261E;
    }
  }

  &--outlined {
    background-color: transparent;
    border-radius: $uni-md-radius-small;

    &:hover:not(.is-disabled) {
      .md3-select__outline-leading,
      .md3-select__outline-notch,
      .md3-select__outline-trailing {
        border-color: $uni-md-text-primary;
      }
    }
  }
}

// 禁用状态
.md3-select.is-disabled {
  .md3-select__container {
    background-color: rgba($uni-md-surface-variant, 0.5);
    cursor: not-allowed;
  }

  .md3-select__label,
  .md3-select__value {
    color: $uni-md-text-disabled;
  }
}

// 错误状态
.md3-select.is-error {
  .md3-select__label {
    color: #B3261E;
  }

  .md3-select__supporting-text {
    color: #B3261E;
  }
}

// 前缀图标
.md3-select__prefix {
  display: flex;
  align-items: center;
  margin-right: $uni-md-space-md;
  flex-shrink: 0;
}

// 文本区域
.md3-select__text-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  position: relative;
  height: 48px;
}

// 标签
.md3-select__label {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  transition: all $uni-md-animation-fast ease;
  transform-origin: left top;

  &.is-floating {
    font-size: 12px;
    transform: translateY(-10px);
  }
}

// 值文本
.md3-select__value {
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  line-height: 1.5;

  &.is-placeholder {
    color: $uni-md-text-tertiary;
  }
}

// 后缀图标
.md3-select__suffix {
  display: flex;
  align-items: center;
  margin-left: $uni-md-space-sm;
  flex-shrink: 0;

  .is-rotated {
    transform: rotate(180deg);
    transition: transform $uni-md-animation-fast ease;
  }
}

// Outlined 边框
.md3-select__outline {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  pointer-events: none;
}

.md3-select__outline-leading,
.md3-select__outline-trailing {
  border: 1px solid $uni-md-border;
  transition: border-color $uni-md-animation-fast ease;
}

.md3-select__outline-leading {
  width: 12px;
  border-right: none;
  border-radius: $uni-md-radius-small 0 0 $uni-md-radius-small;
}

.md3-select__outline-trailing {
  flex: 1;
  border-left: none;
  border-radius: 0 $uni-md-radius-small $uni-md-radius-small 0;
}

.md3-select__outline-notch {
  border-top: 1px solid $uni-md-border;
  border-bottom: 1px solid $uni-md-border;
  transition: border-color $uni-md-animation-fast ease;
  padding: 0 4px;

  &.is-floating {
    border-top: none;
  }
}

.md3-select__outline-label {
  font-size: 12px;
  color: $uni-md-text-secondary;
  padding: 0 4px;
  transform: translateY(-50%);
}

// 下拉菜单遮罩
.md3-select__menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

// 下拉菜单
.md3-select__menu {
  position: absolute;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-small;
  box-shadow: $uni-md-shadow-lg;
  max-height: 300px;
  min-width: 200px;
  overflow: hidden;
  margin-top: 4px;
}

.md3-select__menu-scroll {
  max-height: 300px;
}

// 菜单项
.md3-select__menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $uni-md-space-md $uni-md-space-lg;
  cursor: pointer;
  transition: background-color $uni-md-animation-fast ease;

  &:hover {
    background-color: $uni-md-surface-variant;
  }

  &.is-selected {
    background-color: rgba($uni-md-color-primary, 0.08);
  }
}

.md3-select__menu-item-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
}

// 支持文本
.md3-select__supporting-text {
  font-size: 12px;
  color: $uni-md-text-secondary;
  margin-top: 4px;
  padding: 0 $uni-md-space-md;
}
</style>
