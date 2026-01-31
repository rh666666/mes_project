<template>
  <view class="menu-list">
    <view
      v-for="(item, index) in menuItems"
      :key="index"
      class="menu-item"
      :class="[item.className || '', { 'last-item': index === menuItems.length - 1 }]"
      @click="onItemClick(item, index)"
    >
      <text class="menu-text" :class="item.textClass">{{ item.text }}</text>
      <text class="menu-arrow">></text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MenuList',

  props: {
    menuItems: {
      type: Array,
      default: () => []
    }
  },

  methods: {
    onItemClick(item, index) {
      this.$emit('item-click', item, index)
      if (item.onClick) {
        item.onClick()
      }
    }
  }
}
</script>

<style lang="scss">
.menu-list {
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-sm;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-bottom: 1px solid $uni-md-divider;
  transition: background-color $uni-md-animation-fast ease;

  &:last-child,
  &.last-item {
    border-bottom: none;
  }

  &:active {
    background-color: $uni-md-surface-variant;
  }
}

.menu-text {
  flex: 1;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &.danger {
    color: $uni-color-error;
  }
}

.menu-arrow {
  font-size: $uni-font-size-base;
  color: $uni-md-text-tertiary;
}
</style>
