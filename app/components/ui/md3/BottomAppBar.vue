<template>
  <view
    class="md3-bottom-app-bar"
    :class="[
      `fab-align-${fabAlign}`,
      {
        'has-fab': showFab,
        'is-scrolled': isScrolled
      }
    ]"
    :style="barStyle"
  >
    <!-- 导航图标 -->
    <view
      v-if="showNavigation"
      class="md3-bottom-app-bar__navigation"
      @click="onNavigationClick"
    >
      <slot name="navigation">
        <MdIcon :type="navigationIcon" :size="24" :color="iconColor" />
      </slot>
    </view>

    <!-- 操作项容器 -->
    <view class="md3-bottom-app-bar__actions">
      <slot name="actions">
        <view
          v-for="(action, index) in actions"
          :key="index"
          class="md3-bottom-app-bar__action"
          :class="{ 'is-active': action.active }"
          @click="onActionClick(action, index)"
        >
          <MdIcon
            :type="action.icon"
            :size="24"
            :color="action.active ? activeColor : iconColor"
          />
          <text
            v-if="action.label"
            class="md3-bottom-app-bar__action-label"
            :class="{ 'is-active': action.active }"
          >
            {{ action.label }}
          </text>
        </view>
      </slot>
    </view>

    <!-- 溢出菜单 -->
    <view
      v-if="showOverflow"
      class="md3-bottom-app-bar__overflow"
      @click="onOverflowClick"
    >
      <slot name="overflow">
        <MdIcon type="more_vert" :size="24" :color="iconColor" />
      </slot>
    </view>

    <!-- FAB 占位区域 -->
    <view v-if="showFab" class="md3-bottom-app-bar__fab-placeholder" />

    <!-- FAB 容器 -->
    <view
      v-if="showFab"
      class="md3-bottom-app-bar__fab"
      :class="`fab-align-${fabAlign}`"
      @click="onFabClick"
    >
      <slot name="fab">
        <view class="md3-bottom-app-bar__fab-button" :style="fabStyle">
          <MdIcon :type="fabIcon" :size="24" color="#FFFFFF" />
        </view>
      </slot>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 Bottom App Bar 组件
 * @component
 * @description 底部应用栏组件，提供导航和关键操作入口
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {Object} BottomAppBarAction
 * @property {string} icon - 图标类型
 * @property {string} [label] - 标签文本
 * @property {boolean} [active] - 是否激活
 * @property {Function} [onClick] - 点击回调
 */

export default {
  name: 'BottomAppBar',

  components: {
    MdIcon
  },

  props: {
    /**
     * 是否显示导航图标
     * @type {boolean}
     */
    showNavigation: {
      type: Boolean,
      default: false
    },

    /**
     * 导航图标类型
     * @type {string}
     */
    navigationIcon: {
      type: String,
      default: 'menu'
    },

    /**
     * 操作项列表
     * @type {BottomAppBarAction[]}
     */
    actions: {
      type: Array,
      default: () => []
    },

    /**
     * 是否显示溢出菜单
     * @type {boolean}
     */
    showOverflow: {
      type: Boolean,
      default: false
    },

    /**
     * 是否显示 FAB
     * @type {boolean}
     */
    showFab: {
      type: Boolean,
      default: false
    },

    /**
     * FAB 图标类型
     * @type {string}
     */
    fabIcon: {
      type: String,
      default: 'add'
    },

    /**
     * FAB 对齐方式
     * @type {'start'|'center'|'end'}
     */
    fabAlign: {
      type: String,
      default: 'end',
      validator: (value) => ['start', 'center', 'end'].includes(value)
    },

    /**
     * FAB 背景色
     * @type {string}
     */
    fabColor: {
      type: String,
      default: ''
    },

    /**
     * 背景色
     * @type {string}
     */
    backgroundColor: {
      type: String,
      default: ''
    },

    /**
     * 是否滚动状态
     * @type {boolean}
     */
    isScrolled: {
      type: Boolean,
      default: false
    }
  },

  emits: ['navigation-click', 'action-click', 'overflow-click', 'fab-click'],

  computed: {
    /**
     * 图标颜色
     * @returns {string}
     */
    iconColor() {
      return '#49454F'
    },

    /**
     * 激活颜色
     * @returns {string}
     */
    activeColor() {
      return '#1976D2'
    },

    /**
     * 栏样式
     * @returns {Object}
     */
    barStyle() {
      return {
        backgroundColor: this.backgroundColor || '#F3EFF8'
      }
    },

    /**
     * FAB 样式
     * @returns {Object}
     */
    fabStyle() {
      return {
        backgroundColor: this.fabColor || '#1976D2'
      }
    }
  },

  methods: {
    /**
     * 处理导航点击
     */
    onNavigationClick() {
      this.$emit('navigation-click')
    },

    /**
     * 处理操作项点击
     * @param {BottomAppBarAction} action - 操作项
     * @param {number} index - 索引
     */
    onActionClick(action, index) {
      this.$emit('action-click', { action, index })
      if (action.onClick) {
        action.onClick()
      }
    },

    /**
     * 处理溢出菜单点击
     */
    onOverflowClick() {
      this.$emit('overflow-click')
    },

    /**
     * 处理 FAB 点击
     */
    onFabClick() {
      this.$emit('fab-click')
    }
  }
}
</script>

<style lang="scss">
.md3-bottom-app-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  height: 80px;
  padding: 0 $uni-md-space-md;
  background-color: #F3EFF8;
  border-radius: $uni-md-radius-large $uni-md-radius-large 0 0;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.08);
  z-index: 1000;
  transition: all 200ms ease;

  // 滚动状态
  &.is-scrolled {
    box-shadow: 0 -4px 8px rgba(0, 0, 0, 0.12);
  }
}

// 导航图标
.md3-bottom-app-bar__navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 150ms ease;
  flex-shrink: 0;

  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  &:active {
    background-color: rgba(0, 0, 0, 0.08);
  }
}

// 操作项容器
.md3-bottom-app-bar__actions {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: $uni-md-space-xs;
  margin: 0 $uni-md-space-sm;
}

// 操作项
.md3-bottom-app-bar__action {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  height: 56px;
  padding: $uni-md-space-xs $uni-md-space-sm;
  border-radius: $uni-md-radius-small;
  cursor: pointer;
  transition: all 150ms ease;
  gap: 2px;

  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  &:active {
    background-color: rgba(0, 0, 0, 0.08);
  }

  &.is-active {
    background-color: rgba(25, 118, 210, 0.08);
  }
}

.md3-bottom-app-bar__action-label {
  font-size: 12px;
  color: #49454F;
  line-height: 1;

  &.is-active {
    color: #1976D2;
    font-weight: 500;
  }
}

// 溢出菜单
.md3-bottom-app-bar__overflow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 150ms ease;
  flex-shrink: 0;

  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  &:active {
    background-color: rgba(0, 0, 0, 0.08);
  }
}

// FAB 占位区域
.md3-bottom-app-bar__fab-placeholder {
  width: 56px;
  flex-shrink: 0;
}

// FAB 容器
.md3-bottom-app-bar__fab {
  position: absolute;
  bottom: 28px;
  z-index: 1001;

  &.fab-align-start {
    left: 16px;
  }

  &.fab-align-center {
    left: 50%;
    transform: translateX(-50%);
  }

  &.fab-align-end {
    right: 16px;
  }
}

// FAB 按钮
.md3-bottom-app-bar__fab-button {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1976D2;
  border-radius: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 200ms ease;

  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
    transform: translateY(-2px);
  }

  &:active {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    transform: translateY(0);
  }
}

// 安全区域适配（iPhone X 及以上）
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .md3-bottom-app-bar {
    padding-bottom: env(safe-area-inset-bottom);
    height: calc(80px + env(safe-area-inset-bottom));
  }

  .md3-bottom-app-bar__fab {
    bottom: calc(28px + env(safe-area-inset-bottom));
  }
}
</style>
