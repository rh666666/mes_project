<template>
  <view class="tab-bar">
    <view
      v-for="(item, index) in list"
      :key="index"
      class="tab-bar-item"
      :class="{ active: selected === index }"
      @click="switchTab(index, item)"
    >
      <view class="tab-icon-wrapper">
        <uni-icons
          class="tab-icon"
          :type="selected === index ? item.iconActive : item.icon"
          size="24"
          :color="selected === index ? '#1976D2' : '#6E6E73'"
        />
      </view>
      <text class="tab-text">{{ item.text }}</text>
      <view v-if="selected === index" class="tab-indicator" />
    </view>
  </view>
</template>

<script>
/**
 * 自定义底部导航栏组件
 * @description 使用 uni-icons 图标库替代纯文本图标
 */
export default {
  data() {
    return {
      /** @type {number} 当前选中的索引 */
      selected: 0,
      /** @type {Array} 导航项列表 */
      list: [
        {
          pagePath: '/pages/index/index',
          text: '首页',
          icon: 'home',
          iconActive: 'home-filled'
        },
        {
          pagePath: '/pages/production/index',
          text: '生产',
          icon: 'list',
          iconActive: 'list-filled'
        },
        {
          pagePath: '/pages/equipment/index',
          text: '设备',
          icon: 'settings',
          iconActive: 'settings-filled'
        },
        {
          pagePath: '/pages/profile/index',
          text: '我的',
          icon: 'person',
          iconActive: 'personadd-filled'
        }
      ]
    };
  },

  methods: {
    /**
     * 切换标签页
     * @param {number} index - 索引
     * @param {Object} item - 导航项
     */
    switchTab(index, item) {
      if (this.selected === index) {
        return;
      }
      this.selected = index;
      uni.switchTab({
        url: item.pagePath
      });
    }
  }
};
</script>

<style lang="scss">
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 100rpx;
  background-color: $uni-md-surface;
  border-top: 1rpx solid $uni-md-divider;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
  z-index: 999;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rpx 0;
  position: relative;
  cursor: pointer;
  transition: all $uni-md-animation-fast ease;

  &:active {
    transform: scale(0.98);
  }

  &.active {
    .tab-icon {
      transform: translateY(-4rpx);
    }

    .tab-text {
      color: $uni-md-color-primary;
      font-weight: 500;
    }
  }
}

.tab-icon-wrapper {
  margin-bottom: 4rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-icon {
  line-height: 1;
  opacity: 0.6;
  transition: all $uni-md-animation-normal ease;
}

.tab-text {
  font-size: 22rpx;
  color: $uni-md-text-secondary;
  transition: all $uni-md-animation-normal ease;
}

.tab-indicator {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 4rpx;
  height: 4rpx;
  border-radius: 50%;
  background-color: $uni-md-color-primary;
  box-shadow: 0 0 8rpx $uni-md-color-primary;
  animation: pulse $uni-md-animation-normal ease-in-out;
}

@keyframes pulse {
  0% {
    transform: translateX(-50%) scale(0.8);
    opacity: 0.8;
  }
  50% {
    transform: translateX(-50%) scale(1.2);
    opacity: 1;
  }
  100% {
    transform: translateX(-50%) scale(1);
    opacity: 1;
  }
}
</style>
