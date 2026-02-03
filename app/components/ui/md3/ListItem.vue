<template>
  <view
    class="md3-list-item"
    :class="{ 'is-clickable': clickable, 'has-divider': hasDivider }"
    role="listitem"
    @click="handleClick"
  >
    <!-- start slot: 左侧内容（头像、图标等） -->
    <view v-if="$slots.start" class="md3-list-item__start">
      <slot name="start" />
    </view>

    <!-- 内容区域 -->
    <view class="md3-list-item__content">
      <!-- headline slot: 主标题 -->
      <view v-if="$slots.headline" class="md3-list-item__headline">
        <slot name="headline" />
      </view>

      <!-- supporting-text slot: 辅助文本 -->
      <view v-if="$slots['supporting-text']" class="md3-list-item__supporting-text">
        <slot name="supporting-text" />
      </view>
    </view>

    <!-- trailing-supporting-text slot: 尾部辅助文本 -->
    <view v-if="$slots['trailing-supporting-text']" class="md3-list-item__trailing-supporting-text">
      <slot name="trailing-supporting-text" />
    </view>

    <!-- end slot: 右侧内容（箭头、图标等） -->
    <view v-if="$slots.end" class="md3-list-item__end">
      <slot name="end" />
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 List Item 组件
 * @component
 * @description 列表项组件，支持 headline、supporting-text、trailing-supporting-text、start、end 等 slot
 */
export default {
  name: 'ListItem',

  props: {
    /** @type {boolean} 是否可点击 */
    clickable: {
      type: Boolean,
      default: false
    },
    /** @type {boolean} 是否显示底部分割线 */
    hasDivider: {
      type: Boolean,
      default: false
    }
  },

  emits: ['click'],

  methods: {
    /**
     * 处理点击事件
     * @param {Event} event - 点击事件
     */
    handleClick(event) {
      if (this.clickable) {
        this.$emit('click', event)
      }
    }
  }
}
</script>

<style lang="scss">
.md3-list-item {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md $uni-md-space-lg;
  background-color: $uni-md-surface;
  transition: background-color $uni-md-animation-fast ease;

  &.is-clickable {
    cursor: pointer;

    &:active {
      background-color: $uni-md-surface-variant;
    }
  }

  &.has-divider {
    border-bottom: 1px solid $uni-md-divider;
  }
}

.md3-list-item__start {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $uni-md-space-md;
  flex-shrink: 0;
}

.md3-list-item__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-xs;
  min-width: 0;
}

.md3-list-item__headline {
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
  line-height: 1.5;
}

.md3-list-item__supporting-text {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
  line-height: 1.4;
}

.md3-list-item__trailing-supporting-text {
  margin-left: $uni-md-space-md;
  flex-shrink: 0;
}

.md3-list-item__end {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: $uni-md-space-sm;
  flex-shrink: 0;
}
</style>
