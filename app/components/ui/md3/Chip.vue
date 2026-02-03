<template>
  <view
    class="md3-chip"
    :class="[
      `type-${type}`,
      {
        'is-selected': selected,
        'is-elevated': elevated,
        'is-disabled': disabled
      }
    ]"
    @click="handleClick"
  >
    <!-- 图标插槽 -->
    <view v-if="$slots.icon || icon" class="md3-chip__icon">
      <slot name="icon">
        <MdIcon :type="icon" :size="18" />
      </slot>
    </view>

    <!-- 标签文本 -->
    <text class="md3-chip__label">{{ label }}</text>

    <!-- 移除按钮（仅 input 和 removable filter 类型） -->
    <view
      v-if="removable"
      class="md3-chip__remove"
      @click.stop="handleRemove"
    >
      <MdIcon type="close" :size="18" />
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 Chip 组件
 * @component
 * @description 支持 Assist、Filter、Input、Suggestion 四种类型的芯片组件
 */

import MdIcon from '@/components/ui/MdIcon.vue'

export default {
  name: 'Chip',

  components: {
    MdIcon
  },

  props: {
    /** @type {string} 芯片类型: assist | filter | input | suggestion */
    type: {
      type: String,
      default: 'assist'
    },
    /** @type {string} 显示标签 */
    label: {
      type: String,
      required: true
    },
    /** @type {string} 图标类型 */
    icon: {
      type: String,
      default: ''
    },
    /** @type {boolean} 是否选中（filter 类型） */
    selected: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 是否提升（elevated 样式） */
    elevated: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 是否可移除 */
    removable: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 是否禁用 */
    disabled: {
      type: Boolean,
      default: false
    }
  },

  emits: ['click', 'remove'],

  methods: {
    /**
     * 处理点击事件
     */
    handleClick() {
      if (!this.disabled) {
        this.$emit('click')
      }
    },

    /**
     * 处理移除事件
     */
    handleRemove() {
      if (!this.disabled) {
        this.$emit('remove')
      }
    }
  }
}
</script>

<style lang="scss">
.md3-chip {
  display: inline-flex;
  align-items: center;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-sm $uni-md-space-md;
  border-radius: $uni-md-radius-small;
  background-color: transparent;
  border: 1px solid $uni-md-divider;
  transition: all $uni-md-animation-fast ease;

  &:active:not(.is-disabled) {
    background-color: rgba($uni-md-color-primary, 0.1);
  }

  // 提升样式
  &.is-elevated {
    background-color: $uni-md-surface;
    box-shadow: $uni-md-shadow-sm;
    border: none;
  }

  // 禁用状态
  &.is-disabled {
    opacity: 0.5;
    pointer-events: none;
  }

  // Assist Chip - 辅助芯片
  &.type-assist {
    &:active:not(.is-disabled) {
      background-color: rgba($uni-md-color-primary, 0.1);
    }
  }

  // Filter Chip - 筛选芯片
  &.type-filter {
    &.is-selected {
      background-color: rgba($uni-md-color-primary, 0.1);
      border-color: $uni-md-color-primary;

      .md3-chip__label {
        color: $uni-md-color-primary;
        font-weight: 500;
      }
    }
  }

  // Input Chip - 输入芯片
  &.type-input {
    background-color: $uni-md-surface-variant;
    border: none;

    .md3-chip__icon {
      width: 24rpx;
      height: 24rpx;
      border-radius: 50%;
      overflow: hidden;
    }
  }

  // Suggestion Chip - 建议芯片
  &.type-suggestion {
    &:active:not(.is-disabled) {
      background-color: rgba($uni-md-color-primary, 0.1);
    }
  }
}

.md3-chip__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $uni-md-text-secondary;
}

.md3-chip__label {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-primary;
  line-height: 1;
}

.md3-chip__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  margin-right: -$uni-md-space-xs;
  color: $uni-md-text-secondary;

  &:active {
    background-color: rgba($uni-md-text-secondary, 0.1);
  }
}
</style>
