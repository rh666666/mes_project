<template>
  <view class="md3-searchbar" :class="{ 'is-focused': isFocused, 'is-loading': loading }">
    <!-- 搜索图标 -->
    <view class="md3-searchbar__icon-leading">
      <MdIcon type="search" :size="20" :color="iconColor" />
    </view>

    <!-- 输入框 -->
    <input
      ref="inputRef"
      v-model="inputValue"
      class="md3-searchbar__input"
      type="text"
      :placeholder="placeholder"
      :disabled="disabled"
      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"
      @confirm="onConfirm"
    />

    <!-- 清除按钮 -->
    <view
      v-if="showClear && inputValue"
      class="md3-searchbar__icon-trailing"
      @click="clearInput"
    >
      <MdIcon type="close" :size="18" :color="iconColor" />
    </view>

    <!-- 加载指示器 -->
    <view v-if="loading" class="md3-searchbar__loading">
      <view class="md3-searchbar__spinner"></view>
    </view>

    <!-- 语音搜索按钮 -->
    <view
      v-if="showVoice && !inputValue"
      class="md3-searchbar__icon-trailing"
      @click="onVoiceSearch"
    >
      <MdIcon type="mic" :size="20" :color="iconColor" />
    </view>

    <!-- 搜索建议列表 -->
    <view v-if="showSuggestions && filteredSuggestions.length > 0" class="md3-searchbar__suggestions">
      <scroll-view scroll-y class="md3-searchbar__suggestions-scroll">
        <view
          v-for="(suggestion, index) in filteredSuggestions"
          :key="index"
          class="md3-searchbar__suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          <MdIcon type="search" :size="16" :color="suggestionIconColor" />
          <text class="md3-searchbar__suggestion-text">{{ getSuggestionText(suggestion) }}</text>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 SearchBar 组件
 * @component
 * @description 搜索栏组件，支持搜索建议、清除按钮和语音搜索
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {Object} SearchSuggestion
 * @property {string} text - 建议文本
 * @property {string} [value] - 建议值
 */

export default {
  name: 'SearchBar',

  components: {
    MdIcon
  },

  props: {
    /**
     * 搜索文本
     * @type {string}
     */
    modelValue: {
      type: String,
      default: ''
    },

    /**
     * 占位文本
     * @type {string}
     */
    placeholder: {
      type: String,
      default: '搜索'
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
     * 是否加载中
     * @type {boolean}
     */
    loading: {
      type: Boolean,
      default: false
    },

    /**
     * 搜索建议列表
     * @type {Array<SearchSuggestion|string>}
     */
    suggestions: {
      type: Array,
      default: () => []
    },

    /**
     * 是否显示清除按钮
     * @type {boolean}
     */
    showClear: {
      type: Boolean,
      default: true
    },

    /**
     * 是否显示语音按钮
     * @type {boolean}
     */
    showVoice: {
      type: Boolean,
      default: false
    },

    /**
     * 是否自动聚焦
     * @type {boolean}
     */
    autoFocus: {
      type: Boolean,
      default: false
    },

    /**
     * 最大建议数量
     * @type {number}
     */
    maxSuggestions: {
      type: Number,
      default: 5
    }
  },

  emits: ['update:modelValue', 'search', 'focus', 'blur', 'input', 'clear', 'voice', 'select'],

  data() {
    return {
      isFocused: false,
      showSuggestions: false,
      inputValue: this.modelValue
    }
  },

  computed: {
    /**
     * 图标颜色
     * @returns {string}
     */
    iconColor() {
      return this.isFocused ? '#1976D2' : '#6E6E73'
    },

    /**
     * 建议图标颜色
     * @returns {string}
     */
    suggestionIconColor() {
      return '#6E6E73'
    },

    /**
     * 过滤后的建议列表
     * @returns {Array<SearchSuggestion|string>}
     */
    filteredSuggestions() {
      if (!this.inputValue) {
        return this.suggestions.slice(0, this.maxSuggestions)
      }
      const query = this.inputValue.toLowerCase()
      return this.suggestions
        .filter(s => {
          const text = this.getSuggestionText(s).toLowerCase()
          return text.includes(query)
        })
        .slice(0, this.maxSuggestions)
    }
  },

  watch: {
    modelValue: {
      immediate: true,
      handler(newVal) {
        this.inputValue = newVal
      }
    }
  },

  mounted() {
    if (this.autoFocus) {
      this.focus()
    }
  },

  methods: {
    /**
     * 获取建议文本
     * @param {SearchSuggestion|string} suggestion - 建议项
     * @returns {string}
     */
    getSuggestionText(suggestion) {
      if (typeof suggestion === 'object' && suggestion !== null) {
        return suggestion.text || suggestion.value || ''
      }
      return String(suggestion)
    },

    /**
     * 获取建议值
     * @param {SearchSuggestion|string} suggestion - 建议项
     * @returns {string}
     */
    getSuggestionValue(suggestion) {
      if (typeof suggestion === 'object' && suggestion !== null) {
        return suggestion.value || suggestion.text || ''
      }
      return String(suggestion)
    },

    /**
     * 处理聚焦事件
     */
    onFocus() {
      this.isFocused = true
      this.showSuggestions = true
      this.$emit('focus')
    },

    /**
     * 处理失焦事件
     */
    onBlur() {
      // 延迟隐藏建议列表，以便点击建议项
      setTimeout(() => {
        this.isFocused = false
        this.showSuggestions = false
      }, 200)
      this.$emit('blur')
    },

    /**
     * 处理输入事件
     * @param {Event} event - 输入事件
     */
    onInput(event) {
      const value = event.detail.value
      this.inputValue = value
      this.$emit('update:modelValue', value)
      this.$emit('input', value)
      this.showSuggestions = true
    },

    /**
     * 处理确认事件
     */
    onConfirm() {
      this.$emit('search', this.inputValue)
      this.showSuggestions = false
    },

    /**
     * 清除输入
     */
    clearInput() {
      this.inputValue = ''
      this.$emit('update:modelValue', '')
      this.$emit('clear')
      this.$emit('input', '')
      this.focus()
    },

    /**
     * 选择建议
     * @param {SearchSuggestion|string} suggestion - 建议项
     */
    selectSuggestion(suggestion) {
      const value = this.getSuggestionValue(suggestion)
      this.inputValue = value
      this.$emit('update:modelValue', value)
      this.$emit('select', suggestion)
      this.$emit('search', value)
      this.showSuggestions = false
    },

    /**
     * 语音搜索
     */
    onVoiceSearch() {
      this.$emit('voice')
    },

    /**
     * 聚焦输入框
     */
    focus() {
      // uni-app 中无法直接操作 input ref
      // 需要通过组件方法或条件渲染来处理
      this.isFocused = true
    },

    /**
     * 失焦输入框
     */
    blur() {
      this.isFocused = false
      this.showSuggestions = false
    }
  }
}
</script>

<style lang="scss">
.md3-searchbar {
  position: relative;
  display: flex;
  align-items: center;
  padding: $uni-md-space-sm $uni-md-space-md;
  background-color: $uni-md-surface-variant;
  border-radius: $uni-md-radius-full;
  transition: all $uni-md-animation-fast ease;

  // 聚焦状态
  &.is-focused {
    background-color: $uni-md-surface;
    box-shadow: $uni-md-shadow-md;
  }

  // 禁用状态
  &.is-disabled {
    opacity: 0.5;
    pointer-events: none;
  }
}

// 前置图标
.md3-searchbar__icon-leading {
  display: flex;
  align-items: center;
  margin-right: $uni-md-space-sm;
  flex-shrink: 0;
}

// 输入框
.md3-searchbar__input {
  flex: 1;
  height: 40px;
  border: none;
  background: transparent;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  outline: none;

  &::placeholder {
    color: $uni-md-text-tertiary;
  }
}

// 后置图标
.md3-searchbar__icon-trailing {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin-left: $uni-md-space-xs;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color $uni-md-animation-fast ease;

  &:hover {
    background-color: rgba($uni-md-text-secondary, 0.1);
  }

  &:active {
    background-color: rgba($uni-md-text-secondary, 0.2);
  }
}

// 加载指示器
.md3-searchbar__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin-left: $uni-md-space-xs;
  flex-shrink: 0;
}

.md3-searchbar__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid $uni-md-border;
  border-top-color: $uni-md-color-primary;
  border-radius: 50%;
  animation: md3-searchbar-spin 0.8s linear infinite;
}

@keyframes md3-searchbar-spin {
  to {
    transform: rotate(360deg);
  }
}

// 搜索建议列表
.md3-searchbar__suggestions {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-medium;
  box-shadow: $uni-md-shadow-lg;
  z-index: 1000;
  max-height: 240px;
  overflow: hidden;
}

.md3-searchbar__suggestions-scroll {
  max-height: 240px;
}

.md3-searchbar__suggestion-item {
  display: flex;
  align-items: center;
  gap: $uni-md-space-md;
  padding: $uni-md-space-md $uni-md-space-lg;
  cursor: pointer;
  transition: background-color $uni-md-animation-fast ease;

  &:hover {
    background-color: $uni-md-surface-variant;
  }

  &:active {
    background-color: rgba($uni-md-color-primary, 0.08);
  }
}

.md3-searchbar__suggestion-text {
  flex: 1;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
