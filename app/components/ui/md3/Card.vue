<template>
  <view
    class="md3-card"
    :class="[
      `variant-${variant}`,
      {
        'is-clickable': clickable,
        'is-disabled': disabled,
        'is-selected': selected
      }
    ]"
    :style="cardStyle"
    @click="onCardClick"
  >
    <!-- 媒体区域 -->
    <view v-if="$slots.media || image" class="md3-card__media">
      <slot name="media">
        <image
          v-if="image"
          class="md3-card__image"
          :src="image"
          :mode="imageMode"
          @error="onImageError"
        />
      </slot>
      <!-- 媒体内容覆盖层 -->
      <view v-if="$slots['media-content']" class="md3-card__media-content">
        <slot name="media-content" />
      </view>
    </view>

    <!-- 头部区域 -->
    <view v-if="$slots.header || title || subtitle" class="md3-card__header">
      <slot name="header">
        <!-- 头像/图标 -->
        <view v-if="avatar || icon" class="md3-card__avatar">
          <slot name="avatar">
            <image v-if="avatar" class="md3-card__avatar-image" :src="avatar" mode="aspectFill" />
            <MdIcon v-else-if="icon" :type="icon" :size="24" />
          </slot>
        </view>
        <!-- 标题区域 -->
        <view class="md3-card__titles">
          <text v-if="title" class="md3-card__title">{{ title }}</text>
          <text v-if="subtitle" class="md3-card__subtitle">{{ subtitle }}</text>
        </view>
        <!-- 头部操作 -->
        <view v-if="$slots['header-actions']" class="md3-card__header-actions">
          <slot name="header-actions" />
        </view>
      </slot>
    </view>

    <!-- 内容区域 -->
    <view v-if="$slots.default || content" class="md3-card__content">
      <slot>
        <text class="md3-card__text">{{ content }}</text>
      </slot>
    </view>

    <!-- 操作区域 -->
    <view v-if="$slots.actions" class="md3-card__actions">
      <slot name="actions" />
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 Card 组件
 * @component
 * @description 卡片组件，支持多种变体和丰富的内容布局
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {'elevated'|'filled'|'outlined'} CardVariant
 */

export default {
  name: 'Card',

  components: {
    MdIcon
  },

  props: {
    /**
     * 卡片变体
     * @type {CardVariant}
     */
    variant: {
      type: String,
      default: 'elevated',
      validator: (value) => ['elevated', 'filled', 'outlined'].includes(value)
    },

    /**
     * 标题
     * @type {string}
     */
    title: {
      type: String,
      default: ''
    },

    /**
     * 副标题
     * @type {string}
     */
    subtitle: {
      type: String,
      default: ''
    },

    /**
     * 内容文本
     * @type {string}
     */
    content: {
      type: String,
      default: ''
    },

    /**
     * 图片地址
     * @type {string}
     */
    image: {
      type: String,
      default: ''
    },

    /**
     * 图片模式
     * @type {string}
     */
    imageMode: {
      type: String,
      default: 'aspectFill'
    },

    /**
     * 头像地址
     * @type {string}
     */
    avatar: {
      type: String,
      default: ''
    },

    /**
     * 图标类型
     * @type {string}
     */
    icon: {
      type: String,
      default: ''
    },

    /**
     * 是否可点击
     * @type {boolean}
     */
    clickable: {
      type: Boolean,
      default: false
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
     * 是否选中
     * @type {boolean}
     */
    selected: {
      type: Boolean,
      default: false
    },

    /**
     * 圆角大小
     * @type {number}
     */
    borderRadius: {
      type: Number,
      default: 12
    }
  },

  emits: ['click', 'image-error'],

  computed: {
    /**
     * 卡片样式
     * @returns {Object}
     */
    cardStyle() {
      return {
        borderRadius: `${this.borderRadius}px`
      }
    }
  },

  methods: {
    /**
     * 处理卡片点击
     */
    onCardClick() {
      if (this.disabled || !this.clickable) return
      this.$emit('click')
    },

    /**
     * 处理图片加载错误
     */
    onImageError() {
      this.$emit('image-error')
    }
  }
}
</script>

<style lang="scss">
.md3-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 200ms ease;

  // Elevated 变体
  &.variant-elevated {
    background-color: $uni-md-surface;
    box-shadow: $uni-md-shadow-md;

    &:hover {
      box-shadow: $uni-md-shadow-lg;
    }
  }

  // Filled 变体
  &.variant-filled {
    background-color: $uni-md-surface-variant;

    &:hover {
      background-color: darken($uni-md-surface-variant, 3%);
    }
  }

  // Outlined 变体
  &.variant-outlined {
    background-color: $uni-md-surface;
    border: 1px solid $uni-md-border;

    &:hover {
      background-color: $uni-md-surface-variant;
    }
  }

  // 可点击状态
  &.is-clickable {
    cursor: pointer;

    &:active {
      transform: scale(0.98);
    }
  }

  // 禁用状态
  &.is-disabled {
    opacity: 0.38;
    pointer-events: none;
  }

  // 选中状态
  &.is-selected {
    outline: 2px solid $uni-md-color-primary;
    outline-offset: -2px;
  }
}

// 媒体区域
.md3-card__media {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.md3-card__image {
  width: 100%;
  height: 200px;
  display: block;
}

.md3-card__media-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: $uni-md-space-md;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
}

// 头部区域
.md3-card__header {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md;
  gap: $uni-md-space-md;
}

.md3-card__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $uni-md-surface-variant;
  flex-shrink: 0;
}

.md3-card__avatar-image {
  width: 100%;
  height: 100%;
}

.md3-card__titles {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-xs;
  min-width: 0;
}

.md3-card__title {
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.md3-card__subtitle {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.md3-card__header-actions {
  flex-shrink: 0;
}

// 内容区域
.md3-card__content {
  flex: 1;
  padding: 0 $uni-md-space-md $uni-md-space-md;
}

.md3-card__text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  line-height: 1.5;
}

// 操作区域
.md3-card__actions {
  display: flex;
  align-items: center;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-sm $uni-md-space-md $uni-md-space-md;
}
</style>
