<template>
  <view
    class="md3-progress-indicator"
    :class="[
      `type-${type}`,
      `variant-${variant}`,
      {
        'is-indeterminate': indeterminate,
        'is-disabled': disabled
      }
    ]"
    :style="containerStyle"
  >
    <!-- 线性进度指示器 -->
    <view v-if="type === 'linear'" class="md3-progress-indicator__linear">
      <!-- 轨道 -->
      <view class="md3-progress-indicator__track" :style="trackStyle">
        <!-- 活动指示器 -->
        <view
          class="md3-progress-indicator__active-indicator"
          :class="{ 'is-animated': indeterminate }"
          :style="activeIndicatorStyle"
        />
      </view>
    </view>

    <!-- 圆形进度指示器 -->
    <view v-else class="md3-progress-indicator__circular">
      <view class="md3-progress-indicator__circular-container" :style="circularContainerStyle">
        <!-- 轨道圆环 -->
        <view class="md3-progress-indicator__circular-track" :style="circularTrackStyle" />
        <!-- 活动指示器圆环 -->
        <view
          class="md3-progress-indicator__circular-indicator"
          :class="{ 'is-animated': indeterminate }"
          :style="circularIndicatorStyle"
        />
      </view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 ProgressIndicator 组件
 * @component
 * @description 进度指示器组件，支持线性和圆形两种类型，确定性和不确定性两种模式
 */

export default {
  name: 'ProgressIndicator',

  props: {
    /**
     * 进度指示器类型
     * @type {'linear'|'circular'}
     */
    type: {
      type: String,
      default: 'linear',
      validator: (value) => ['linear', 'circular'].includes(value)
    },

    /**
     * 进度指示器变体
     * @type {'determinate'|'indeterminate'}
     */
    variant: {
      type: String,
      default: 'determinate',
      validator: (value) => ['determinate', 'indeterminate'].includes(value)
    },

    /**
     * 当前进度值 (0-100)
     * @type {number}
     */
    value: {
      type: Number,
      default: 0,
      validator: (value) => value >= 0 && value <= 100
    },

    /**
     * 轨道厚度 (px)
     * @type {number}
     */
    trackThickness: {
      type: Number,
      default: 4
    },

    /**
     * 圆形指示器大小 (px)
     * @type {number}
     */
    size: {
      type: Number,
      default: 48
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
     * 活动指示器颜色
     * @type {string}
     */
    activeColor: {
      type: String,
      default: ''
    },

    /**
     * 轨道颜色
     * @type {string}
     */
    trackColor: {
      type: String,
      default: ''
    }
  },

  computed: {
    /**
     * 是否不确定性模式
     * @returns {boolean}
     */
    indeterminate() {
      return this.variant === 'indeterminate'
    },

    /**
     * 容器样式
     * @returns {Object}
     */
    containerStyle() {
      return {
        opacity: this.disabled ? 0.38 : 1
      }
    },

    /**
     * 轨道样式
     * @returns {Object}
     */
    trackStyle() {
      return {
        height: `${this.trackThickness}px`,
        backgroundColor: this.trackColor || '#E0E0E0',
        borderRadius: `${this.trackThickness / 2}px`
      }
    },

    /**
     * 活动指示器样式
     * @returns {Object}
     */
    activeIndicatorStyle() {
      if (this.indeterminate) {
        return {
          backgroundColor: this.activeColor || '#1976D2'
        }
      }
      return {
        width: `${this.value}%`,
        backgroundColor: this.activeColor || '#1976D2'
      }
    },

    /**
     * 圆形容器样式
     * @returns {Object}
     */
    circularContainerStyle() {
      return {
        width: `${this.size}px`,
        height: `${this.size}px`
      }
    },

    /**
     * 圆形轨道样式
     * @returns {Object}
     */
    circularTrackStyle() {
      return {
        borderWidth: `${this.trackThickness}px`,
        borderColor: this.trackColor || '#E0E0E0'
      }
    },

    /**
     * 圆形指示器样式
     * @returns {Object}
     */
    circularIndicatorStyle() {
      const styles = {
        borderWidth: `${this.trackThickness}px`,
        borderColor: this.activeColor || '#1976D2'
      }

      if (!this.indeterminate) {
        const circumference = 2 * Math.PI * ((this.size - this.trackThickness) / 2)
        const offset = circumference - (this.value / 100) * circumference
        styles.strokeDasharray = `${circumference}`
        styles.strokeDashoffset = `${offset}`
      }

      return styles
    }
  }
}
</script>

<style lang="scss">
.md3-progress-indicator {
  width: 100%;
}

// 线性进度指示器
.md3-progress-indicator__linear {
  width: 100%;
  padding: $uni-md-space-sm 0;
}

.md3-progress-indicator__track {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.md3-progress-indicator__active-indicator {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: inherit;
  transition: width 0.3s ease;

  &.is-animated {
    width: 50%;
    animation: md3-progress-linear-indeterminate 1.5s ease-in-out infinite;
  }
}

@keyframes md3-progress-linear-indeterminate {
  0% {
    left: -50%;
    width: 50%;
  }
  50% {
    width: 50%;
  }
  100% {
    left: 100%;
    width: 50%;
  }
}

// 圆形进度指示器
.md3-progress-indicator__circular {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $uni-md-space-sm;
}

.md3-progress-indicator__circular-container {
  position: relative;
}

.md3-progress-indicator__circular-track,
.md3-progress-indicator__circular-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border-style: solid;
  border-color: transparent;
}

.md3-progress-indicator__circular-track {
  border-color: #E0E0E0;
}

.md3-progress-indicator__circular-indicator {
  border-top-color: currentColor;
  border-right-color: transparent;
  border-bottom-color: transparent;
  border-left-color: transparent;
  transform: rotate(-90deg);
  transition: stroke-dashoffset 0.3s ease;

  &.is-animated {
    animation: md3-progress-circular-indeterminate 1s linear infinite;
  }
}

@keyframes md3-progress-circular-indeterminate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
