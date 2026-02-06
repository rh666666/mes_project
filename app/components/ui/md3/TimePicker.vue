<template>
  <view class="md3-timepicker">
    <!-- 触发器 -->
    <view
      class="md3-timepicker__trigger"
      :class="{ 'is-disabled': disabled }"
      @click="openPicker"
    >
      <view class="md3-timepicker__icon">
        <MdIcon type="schedule" :size="20" :color="iconColor" />
      </view>
      <text class="md3-timepicker__value" :class="{ 'is-placeholder': !displayValue }">
        {{ displayValue || placeholder }}
      </text>
    </view>

    <!-- 时间选择对话框 -->
    <view v-if="isOpen" class="md3-timepicker__overlay" @click="closePicker">
      <view class="md3-timepicker__dialog" @click.stop>
        <!-- 头部 -->
        <view class="md3-timepicker__header">
          <text class="md3-timepicker__title">{{ title }}</text>
          <view class="md3-timepicker__display">
            <text class="md3-timepicker__time">{{ displayTime }}</text>
          </view>
        </view>

        <!-- 内容区域 -->
        <view class="md3-timepicker__content">
          <!-- 时钟拨盘模式 -->
          <view v-if="inputMode === 'clock'" class="md3-timepicker__clock">
            <!-- 时钟表盘 -->
            <view class="md3-timepicker__clock-face">
              <view
                v-for="num in clockNumbers"
                :key="num.value"
                class="md3-timepicker__clock-number"
                :class="{ 'is-selected': isClockNumberSelected(num) }"
                :style="getClockNumberStyle(num)"
                @click="selectClockNumber(num)"
              >
                {{ num.display }}
              </view>
              <!-- 时钟指针 -->
              <view
                class="md3-timepicker__clock-hand"
                :style="clockHandStyle"
              />
              <!-- 中心点 -->
              <view class="md3-timepicker__clock-center" />
            </view>
          </view>

          <!-- 键盘输入模式 -->
          <view v-else class="md3-timepicker__keyboard">
            <view class="md3-timepicker__inputs">
              <view class="md3-timepicker__input-group">
                <input
                  v-model="hourInput"
                  type="number"
                  class="md3-timepicker__input"
                  :max="format === '24h' ? 23 : 12"
                  :min="0"
                  @blur="validateHour"
                />
                <text class="md3-timepicker__input-label">时</text>
              </view>
              <text class="md3-timepicker__separator">:</text>
              <view class="md3-timepicker__input-group">
                <input
                  v-model="minuteInput"
                  type="number"
                  class="md3-timepicker__input"
                  max="59"
                  min="0"
                  @blur="validateMinute"
                />
                <text class="md3-timepicker__input-label">分</text>
              </view>
            </view>
            <!-- 12小时制 AM/PM 选择 -->
            <view v-if="format === '12h'" class="md3-timepicker__period">
              <view
                class="md3-timepicker__period-btn"
                :class="{ 'is-selected': period === 'AM' }"
                @click="period = 'AM'"
              >
                AM
              </view>
              <view
                class="md3-timepicker__period-btn"
                :class="{ 'is-selected': period === 'PM' }"
                @click="period = 'PM'"
              >
                PM
              </view>
            </view>
          </view>

          <!-- 输入模式切换按钮 -->
          <view class="md3-timepicker__mode-toggle">
            <view
              class="md3-timepicker__mode-btn"
              :class="{ 'is-active': inputMode === 'clock' }"
              @click="inputMode = 'clock'"
            >
              <MdIcon type="schedule" :size="20" />
            </view>
            <view
              class="md3-timepicker__mode-btn"
              :class="{ 'is-active': inputMode === 'keyboard' }"
              @click="inputMode = 'keyboard'"
            >
              <MdIcon type="keyboard" :size="20" />
            </view>
          </view>
        </view>

        <!-- 操作按钮 -->
        <view class="md3-timepicker__actions">
          <view class="md3-timepicker__action-btn" @click="closePicker">
            <text class="md3-timepicker__action-btn-text">{{ cancelText }}</text>
          </view>
          <view class="md3-timepicker__action-btn md3-timepicker__action-btn--confirm" @click="confirmSelection">
            <text class="md3-timepicker__action-btn-text md3-timepicker__action-btn-text--confirm">{{ confirmText }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 TimePicker 组件
 * @component
 * @description 时间选择器组件，支持时钟拨盘和键盘输入两种模式
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {Object} ClockNumber
 * @property {number} value - 数值
 * @property {string} display - 显示文本
 * @property {number} angle - 角度
 */

export default {
  name: 'TimePicker',

  components: {
    MdIcon
  },

  props: {
    /**
     * 当前时间值 {hour, minute}
     * @type {{hour: number, minute: number}|null}
     */
    modelValue: {
      type: Object,
      default: null
    },

    /**
     * 时间格式
     * @type {'12h'|'24h'}
     */
    format: {
      type: String,
      default: '24h',
      validator: (value) => ['12h', '24h'].includes(value)
    },

    /**
     * 默认输入模式
     * @type {'clock'|'keyboard'}
     */
    defaultInputMode: {
      type: String,
      default: 'clock',
      validator: (value) => ['clock', 'keyboard'].includes(value)
    },

    /**
     * 对话框标题
     * @type {string}
     */
    title: {
      type: String,
      default: '选择时间'
    },

    /**
     * 确认按钮文本
     * @type {string}
     */
    confirmText: {
      type: String,
      default: '确定'
    },

    /**
     * 取消按钮文本
     * @type {string}
     */
    cancelText: {
      type: String,
      default: '取消'
    },

    /**
     * 占位文本
     * @type {string}
     */
    placeholder: {
      type: String,
      default: '选择时间'
    },

    /**
     * 是否禁用
     * @type {boolean}
     */
    disabled: {
      type: Boolean,
      default: false
    }
  },

  emits: ['update:modelValue', 'change'],

  data() {
    return {
      isOpen: false,
      inputMode: 'clock',
      tempHour: 12,
      tempMinute: 0,
      period: 'AM',
      selecting: 'hour', // 'hour' or 'minute'
      hourInput: '12',
      minuteInput: '00'
    }
  },

  computed: {
    /**
     * 图标颜色
     * @returns {string}
     */
    iconColor() {
      return this.disabled ? '#C7C7CC' : '#6E6E73'
    },

    /**
     * 显示值
     * @returns {string}
     */
    displayValue() {
      if (!this.modelValue) return ''
      return this.formatTime(this.modelValue.hour, this.modelValue.minute)
    },

    /**
     * 显示时间
     * @returns {string}
     */
    displayTime() {
      return this.formatTime(this.tempHour, this.tempMinute)
    },

    /**
     * 时钟数字
     * @returns {ClockNumber[]}
     */
    clockNumbers() {
      const numbers = []
      const max = this.selecting === 'hour' ? (this.format === '24h' ? 24 : 12) : 12
      const step = this.selecting === 'hour' ? 1 : 5

      for (let i = 0; i < max; i += step) {
        const value = i === 0 && this.selecting === 'minute' ? 0 : i
        const display = this.selecting === 'hour'
          ? (this.format === '12h' && value === 0 ? 12 : value)
          : (value === 0 ? '00' : value)
        const angle = (value / max) * 360 - 90
        numbers.push({ value, display, angle })
      }
      return numbers
    },

    /**
     * 时钟指针样式
     * @returns {Object}
     */
    clockHandStyle() {
      const value = this.selecting === 'hour' ? this.tempHour : Math.floor(this.tempMinute / 5) * 5
      const max = this.selecting === 'hour' ? (this.format === '24h' ? 24 : 12) : 60
      const angle = (value / max) * 360 - 90
      return {
        transform: `rotate(${angle}deg)`
      }
    }
  },

  watch: {
    modelValue: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.tempHour = newVal.hour
          this.tempMinute = newVal.minute
          this.updatePeriod()
          this.updateInputs()
        } else {
          this.tempHour = 12
          this.tempMinute = 0
          this.period = 'AM'
          this.updateInputs()
        }
      }
    }
  },

  methods: {
    /**
     * 打开选择器
     */
    openPicker() {
      if (this.disabled) return
      this.isOpen = true
      this.inputMode = this.defaultInputMode
      this.selecting = 'hour'
      if (this.modelValue) {
        this.tempHour = this.modelValue.hour
        this.tempMinute = this.modelValue.minute
        this.updatePeriod()
      } else {
        this.tempHour = 12
        this.tempMinute = 0
        this.period = 'AM'
      }
      this.updateInputs()
    },

    /**
     * 关闭选择器
     */
    closePicker() {
      this.isOpen = false
    },

    /**
     * 更新 AM/PM
     */
    updatePeriod() {
      if (this.format === '12h') {
        this.period = this.tempHour >= 12 ? 'PM' : 'AM'
      }
    },

    /**
     * 更新输入框值
     */
    updateInputs() {
      this.hourInput = String(this.tempHour).padStart(2, '0')
      this.minuteInput = String(this.tempMinute).padStart(2, '0')
    },

    /**
     * 验证小时输入
     */
    validateHour() {
      let hour = parseInt(this.hourInput) || 0
      const max = this.format === '24h' ? 23 : 12
      const min = 0
      hour = Math.max(min, Math.min(max, hour))
      this.tempHour = hour
      this.hourInput = String(hour).padStart(2, '0')
    },

    /**
     * 验证分钟输入
     */
    validateMinute() {
      let minute = parseInt(this.minuteInput) || 0
      minute = Math.max(0, Math.min(59, minute))
      this.tempMinute = minute
      this.minuteInput = String(minute).padStart(2, '0')
    },

    /**
     * 获取时钟数字样式
     * @param {ClockNumber} num - 时钟数字
     * @returns {Object}
     */
    getClockNumberStyle(num) {
      const radius = 100
      const angleRad = (num.angle * Math.PI) / 180
      const x = Math.cos(angleRad) * radius
      const y = Math.sin(angleRad) * radius
      return {
        transform: `translate(${x}px, ${y}px)`
      }
    },

    /**
     * 判断时钟数字是否选中
     * @param {ClockNumber} num - 时钟数字
     * @returns {boolean}
     */
    isClockNumberSelected(num) {
      if (this.selecting === 'hour') {
        return num.value === this.tempHour
      } else {
        return num.value === Math.floor(this.tempMinute / 5) * 5
      }
    },

    /**
     * 选择时钟数字
     * @param {ClockNumber} num - 时钟数字
     */
    selectClockNumber(num) {
      if (this.selecting === 'hour') {
        this.tempHour = num.value
        this.selecting = 'minute'
      } else {
        this.tempMinute = num.value
      }
      this.updateInputs()
    },

    /**
     * 格式化时间
     * @param {number} hour - 小时
     * @param {number} minute - 分钟
     * @returns {string}
     */
    formatTime(hour, minute) {
      if (this.format === '12h') {
        const displayHour = hour === 0 ? 12 : (hour > 12 ? hour - 12 : hour)
        const period = hour >= 12 ? 'PM' : 'AM'
        return `${String(displayHour).padStart(2, '0')}:${String(minute).padStart(2, '0')} ${period}`
      } else {
        return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      }
    },

    /**
     * 确认选择
     */
    confirmSelection() {
      let hour = this.tempHour
      if (this.format === '12h') {
        if (this.period === 'PM' && hour !== 12) {
          hour += 12
        } else if (this.period === 'AM' && hour === 12) {
          hour = 0
        }
      }

      const timeValue = {
        hour,
        minute: this.tempMinute
      }

      this.$emit('update:modelValue', timeValue)
      this.$emit('change', timeValue)
      this.closePicker()
    }
  }
}
</script>

<style lang="scss">
.md3-timepicker {
  width: 100%;
}

// 触发器
.md3-timepicker__trigger {
  display: flex;
  align-items: center;
  padding: $uni-md-space-md;
  background-color: $uni-md-surface-variant;
  border-radius: $uni-md-radius-small $uni-md-radius-small 0 0;
  border-bottom: 1px solid $uni-md-border;
  cursor: pointer;
  transition: all $uni-md-animation-fast ease;

  &:hover:not(.is-disabled) {
    background-color: darken($uni-md-surface-variant, 3%);
  }

  &.is-disabled {
    background-color: rgba($uni-md-surface-variant, 0.5);
    cursor: not-allowed;

    .md3-timepicker__value {
      color: $uni-md-text-disabled;
    }
  }
}

.md3-timepicker__icon {
  display: flex;
  align-items: center;
  margin-right: $uni-md-space-md;
  flex-shrink: 0;
}

.md3-timepicker__value {
  flex: 1;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &.is-placeholder {
    color: $uni-md-text-tertiary;
  }
}

// 遮罩层
.md3-timepicker__overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

// 对话框
.md3-timepicker__dialog {
  width: min(320rpx, 90%);
  max-width: 320rpx;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-lg;
  overflow: hidden;
}

// 头部
.md3-timepicker__header {
  padding: $uni-md-space-xl;
  background-color: $uni-md-color-primary;
}

.md3-timepicker__title {
  font-size: $uni-font-size-sm;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: $uni-md-space-sm;
  display: block;
}

.md3-timepicker__display {
  display: flex;
  align-items: center;
  justify-content: center;
}

.md3-timepicker__time {
  font-size: 48px;
  font-weight: 400;
  color: white;
  font-variant-numeric: tabular-nums;
}

// 内容区域
.md3-timepicker__content {
  padding: $uni-md-space-xl;
  display: flex;
  flex-direction: column;
  align-items: center;
}

// 时钟拨盘
.md3-timepicker__clock {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: $uni-md-space-lg;
}

.md3-timepicker__clock-face {
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background-color: $uni-md-surface-variant;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.md3-timepicker__clock-number {
  position: absolute;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  cursor: pointer;
  transition: all $uni-md-animation-fast ease;

  &:hover {
    background-color: rgba($uni-md-color-primary, 0.1);
  }

  &.is-selected {
    background-color: $uni-md-color-primary;
    color: white;
  }
}

.md3-timepicker__clock-hand {
  position: absolute;
  width: 2px;
  height: 80px;
  background-color: $uni-md-color-primary;
  transform-origin: bottom center;
  bottom: 50%;
  left: 50%;
  margin-left: -1px;
  border-radius: 1px;
}

.md3-timepicker__clock-center {
  position: absolute;
  width: 8px;
  height: 8px;
  background-color: $uni-md-color-primary;
  border-radius: 50%;
}

// 键盘输入模式
.md3-timepicker__keyboard {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $uni-md-space-lg;
  margin-bottom: $uni-md-space-lg;
  padding: $uni-md-space-lg 0;
}

.md3-timepicker__inputs {
  display: flex;
  align-items: center;
  gap: $uni-md-space-md;
}

.md3-timepicker__input-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $uni-md-space-xs;
}

.md3-timepicker__input {
  width: 80px;
  height: 56px;
  border: 1px solid $uni-md-border;
  border-radius: $uni-md-radius-small;
  text-align: center;
  font-size: 32px;
  color: $uni-md-text-primary;
  background-color: $uni-md-surface;

  &:focus {
    border-color: $uni-md-color-primary;
    outline: none;
  }
}

.md3-timepicker__input-label {
  font-size: 12px;
  color: $uni-md-text-secondary;
}

.md3-timepicker__separator {
  font-size: 32px;
  color: $uni-md-text-primary;
  margin-top: -20px;
}

.md3-timepicker__period {
  display: flex;
  gap: $uni-md-space-sm;
}

.md3-timepicker__period-btn {
  padding: $uni-md-space-sm $uni-md-space-lg;
  border: 1px solid $uni-md-border;
  border-radius: $uni-md-radius-small;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  cursor: pointer;
  transition: all $uni-md-animation-fast ease;

  &:hover {
    background-color: $uni-md-surface-variant;
  }

  &.is-selected {
    background-color: $uni-md-color-primary;
    border-color: $uni-md-color-primary;
    color: white;
  }
}

// 模式切换
.md3-timepicker__mode-toggle {
  display: flex;
  gap: $uni-md-space-sm;
}

.md3-timepicker__mode-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: $uni-md-text-secondary;
  transition: all $uni-md-animation-fast ease;

  &:hover {
    background-color: $uni-md-surface-variant;
  }

  &.is-active {
    background-color: rgba($uni-md-color-primary, 0.1);
    color: $uni-md-color-primary;
  }
}

// 操作按钮
.md3-timepicker__actions {
  display: flex;
  justify-content: flex-end;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-top: 1px solid $uni-md-divider;
}

.md3-timepicker__action-btn {
  padding: $uni-md-space-sm $uni-md-space-md;
  border-radius: $uni-md-radius-small;
  cursor: pointer;
  transition: background-color $uni-md-animation-fast ease;

  &:hover {
    background-color: rgba($uni-md-color-primary, 0.1);
  }
}

.md3-timepicker__action-btn-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  font-weight: 500;

  &--confirm {
    color: $uni-md-color-primary;
  }
}
</style>
