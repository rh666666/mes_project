<template>
  <view class="md3-datepicker">
    <!-- 触发器 -->
    <view
      class="md3-datepicker__trigger"
      :class="{ 'is-disabled': disabled }"
      @click="openPicker"
    >
      <view class="md3-datepicker__icon">
        <MdIcon type="calendar_today" :size="20" :color="iconColor" />
      </view>
      <text class="md3-datepicker__value" :class="{ 'is-placeholder': !displayValue }">
        {{ displayValue || placeholder }}
      </text>
    </view>

    <!-- 日期选择对话框 -->
    <view v-if="isOpen" class="md3-datepicker__overlay" @click="closePicker">
      <view class="md3-datepicker__dialog" @click.stop>
        <!-- 头部 -->
        <view class="md3-datepicker__header">
          <text class="md3-datepicker__title">{{ title }}</text>
          <text v-if="selectedDate" class="md3-datepicker__selected-date">
            {{ formatSelectedDate }}
          </text>
        </view>

        <!-- 内容区域 -->
        <view class="md3-datepicker__content">
          <!-- 年月选择器 -->
          <view class="md3-datepicker__navigation">
            <view class="md3-datepicker__month-year" @click="toggleYearSelector">
              <text class="md3-datepicker__month-year-text">{{ currentMonthYear }}</text>
              <MdIcon
                type="arrow_drop_down"
                :size="24"
                :class="{ 'is-rotated': showYearSelector }"
              />
            </view>
            <view class="md3-datepicker__nav-buttons">
              <view class="md3-datepicker__nav-btn" @click="prevMonth">
                <MdIcon type="chevron_left" :size="24" />
              </view>
              <view class="md3-datepicker__nav-btn" @click="nextMonth">
                <MdIcon type="chevron_right" :size="24" />
              </view>
            </view>
          </view>

          <!-- 年份选择器 -->
          <scroll-view
            v-if="showYearSelector"
            scroll-y
            class="md3-datepicker__year-list"
          >
            <view
              v-for="year in yearRange"
              :key="year"
              class="md3-datepicker__year-item"
              :class="{ 'is-selected': year === currentYear }"
              @click="selectYear(year)"
            >
              {{ year }}
            </view>
          </scroll-view>

          <!-- 日历网格 -->
          <view v-else class="md3-datepicker__calendar">
            <!-- 星期标题 -->
            <view class="md3-datepicker__weekdays">
              <text
                v-for="day in weekdays"
                :key="day"
                class="md3-datepicker__weekday"
              >{{ day }}</text>
            </view>

            <!-- 日期网格 -->
            <view class="md3-datepicker__days">
              <view
                v-for="(day, index) in calendarDays"
                :key="index"
                class="md3-datepicker__day"
                :class="{
                  'is-other-month': !day.isCurrentMonth,
                  'is-today': day.isToday,
                  'is-selected': day.isSelected,
                  'is-disabled': day.isDisabled
                }"
                @click="selectDay(day)"
              >
                <text class="md3-datepicker__day-text">{{ day.date }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 操作按钮 -->
        <view class="md3-datepicker__actions">
          <view class="md3-datepicker__action-btn" @click="closePicker">
            <text class="md3-datepicker__action-btn-text">{{ cancelText }}</text>
          </view>
          <view class="md3-datepicker__action-btn md3-datepicker__action-btn--confirm" @click="confirmSelection">
            <text class="md3-datepicker__action-btn-text md3-datepicker__action-btn-text--confirm">{{ confirmText }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * Material Design 3 DatePicker 组件
 * @component
 * @description 日期选择器组件，支持年月选择和日历视图
 */

import MdIcon from '@/components/ui/MdIcon.vue'

/**
 * @typedef {Object} CalendarDay
 * @property {number} date - 日期数字
 * @property {Date} fullDate - 完整日期对象
 * @property {boolean} isCurrentMonth - 是否当前月份
 * @property {boolean} isToday - 是否今天
 * @property {boolean} isSelected - 是否选中
 * @property {boolean} isDisabled - 是否禁用
 */

export default {
  name: 'DatePicker',

  components: {
    MdIcon
  },

  props: {
    /**
     * 当前日期值 (YYYY-MM-DD 格式)
     * @type {string|null}
     */
    modelValue: {
      type: String,
      default: null
    },

    /**
     * 最小日期 (YYYY-MM-DD 格式)
     * @type {string|null}
     */
    min: {
      type: String,
      default: null
    },

    /**
     * 最大日期 (YYYY-MM-DD 格式)
     * @type {string|null}
     */
    max: {
      type: String,
      default: null
    },

    /**
     * 对话框标题
     * @type {string}
     */
    title: {
      type: String,
      default: '选择日期'
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
      default: '选择日期'
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
     * 日期格式
     * @type {string}
     */
    format: {
      type: String,
      default: 'YYYY-MM-DD'
    }
  },

  emits: ['update:modelValue', 'change'],

  data() {
    return {
      isOpen: false,
      showYearSelector: false,
      currentDate: new Date(),
      selectedDate: null,
      tempSelectedDate: null
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
      return this.formatDate(this.parseDate(this.modelValue))
    },

    /**
     * 格式化的选中日期
     * @returns {string}
     */
    formatSelectedDate() {
      if (!this.tempSelectedDate) return ''
      return this.formatDateFull(this.tempSelectedDate)
    },

    /**
     * 当前年月显示文本
     * @returns {string}
     */
    currentMonthYear() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth() + 1
      return `${year}年${month}月`
    },

    /**
     * 当前年份
     * @returns {number}
     */
    currentYear() {
      return this.currentDate.getFullYear()
    },

    /**
     * 年份范围
     * @returns {number[]}
     */
    yearRange() {
      const currentYear = new Date().getFullYear()
      const start = currentYear - 50
      const end = currentYear + 50
      const years = []
      for (let i = start; i <= end; i++) {
        years.push(i)
      }
      return years
    },

    /**
     * 星期标题
     * @returns {string[]}
     */
    weekdays() {
      return ['日', '一', '二', '三', '四', '五', '六']
    },

    /**
     * 日历天数
     * @returns {CalendarDay[]}
     */
    calendarDays() {
      const days = []
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()

      // 当月第一天
      const firstDay = new Date(year, month, 1)
      // 当月最后一天
      const lastDay = new Date(year, month + 1, 0)

      // 上月天数
      const prevMonthLastDay = new Date(year, month, 0)
      const startDayOfWeek = firstDay.getDay()

      // 添加上月日期
      for (let i = startDayOfWeek - 1; i >= 0; i--) {
        const date = prevMonthLastDay.getDate() - i
        const fullDate = new Date(year, month - 1, date)
        days.push(this.createDayObject(date, fullDate, false))
      }

      // 添加当月日期
      for (let i = 1; i <= lastDay.getDate(); i++) {
        const fullDate = new Date(year, month, i)
        days.push(this.createDayObject(i, fullDate, true))
      }

      // 添加下月日期
      const remainingDays = 42 - days.length
      for (let i = 1; i <= remainingDays; i++) {
        const fullDate = new Date(year, month + 1, i)
        days.push(this.createDayObject(i, fullDate, false))
      }

      return days
    }
  },

  watch: {
    modelValue: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.selectedDate = this.parseDate(newVal)
          this.tempSelectedDate = new Date(this.selectedDate)
          this.currentDate = new Date(this.selectedDate)
        } else {
          this.selectedDate = null
          this.tempSelectedDate = null
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
      this.showYearSelector = false
      if (this.modelValue) {
        this.tempSelectedDate = new Date(this.selectedDate)
        this.currentDate = new Date(this.selectedDate)
      } else {
        this.tempSelectedDate = new Date()
        this.currentDate = new Date()
      }
    },

    /**
     * 关闭选择器
     */
    closePicker() {
      this.isOpen = false
      this.showYearSelector = false
    },

    /**
     * 切换年份选择器
     */
    toggleYearSelector() {
      this.showYearSelector = !this.showYearSelector
    },

    /**
     * 选择年份
     * @param {number} year - 年份
     */
    selectYear(year) {
      this.currentDate = new Date(year, this.currentDate.getMonth(), 1)
      this.showYearSelector = false
    },

    /**
     * 上一月
     */
    prevMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
    },

    /**
     * 下一月
     */
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
    },

    /**
     * 选择日期
     * @param {CalendarDay} day - 日期对象
     */
    selectDay(day) {
      if (day.isDisabled) return
      this.tempSelectedDate = new Date(day.fullDate)
    },

    /**
     * 确认选择
     */
    confirmSelection() {
      if (this.tempSelectedDate) {
        const dateStr = this.formatDateISO(this.tempSelectedDate)
        this.$emit('update:modelValue', dateStr)
        this.$emit('change', dateStr)
      }
      this.closePicker()
    },

    /**
     * 创建日期对象
     * @param {number} date - 日期数字
     * @param {Date} fullDate - 完整日期
     * @param {boolean} isCurrentMonth - 是否当前月
     * @returns {CalendarDay}
     */
    createDayObject(date, fullDate, isCurrentMonth) {
      const today = new Date()
      const isToday = fullDate.toDateString() === today.toDateString()
      const isSelected = this.tempSelectedDate &&
        fullDate.toDateString() === this.tempSelectedDate.toDateString()
      const isDisabled = this.isDateDisabled(fullDate)

      return {
        date,
        fullDate,
        isCurrentMonth,
        isToday,
        isSelected,
        isDisabled
      }
    },

    /**
     * 判断日期是否禁用
     * @param {Date} date - 日期
     * @returns {boolean}
     */
    isDateDisabled(date) {
      if (this.min) {
        const minDate = this.parseDate(this.min)
        if (date < minDate) return true
      }
      if (this.max) {
        const maxDate = this.parseDate(this.max)
        if (date > maxDate) return true
      }
      return false
    },

    /**
     * 解析日期字符串
     * @param {string} dateStr - 日期字符串
     * @returns {Date}
     */
    parseDate(dateStr) {
      const parts = dateStr.split('-')
      return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
    },

    /**
     * 格式化日期
     * @param {Date} date - 日期对象
     * @returns {string}
     */
    formatDate(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },

    /**
     * 格式化日期完整显示
     * @param {Date} date - 日期对象
     * @returns {string}
     */
    formatDateFull(date) {
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const day = date.getDate()
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      const weekday = weekdays[date.getDay()]
      return `${year}年${month}月${day}日 ${weekday}`
    },

    /**
     * 格式化日期为 ISO 格式
     * @param {Date} date - 日期对象
     * @returns {string}
     */
    formatDateISO(date) {
      return this.formatDate(date)
    }
  }
}
</script>

<style lang="scss">
.md3-datepicker {
  width: 100%;
}

// 触发器
.md3-datepicker__trigger {
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

    .md3-datepicker__value {
      color: $uni-md-text-disabled;
    }
  }
}

.md3-datepicker__icon {
  display: flex;
  align-items: center;
  margin-right: $uni-md-space-md;
  flex-shrink: 0;
}

.md3-datepicker__value {
  flex: 1;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &.is-placeholder {
    color: $uni-md-text-tertiary;
  }
}

// 遮罩层
.md3-datepicker__overlay {
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
.md3-datepicker__dialog {
  width: min(360rpx, 90%);
  max-width: 360rpx;
  background-color: $uni-md-surface;
  border-radius: $uni-md-radius-large;
  box-shadow: $uni-md-shadow-lg;
  overflow: hidden;
}

// 头部
.md3-datepicker__header {
  padding: $uni-md-space-xl;
  background-color: $uni-md-color-primary;
}

.md3-datepicker__title {
  font-size: $uni-font-size-sm;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: $uni-md-space-sm;
  display: block;
}

.md3-datepicker__selected-date {
  font-size: 24px;
  font-weight: 500;
  color: white;
}

// 内容区域
.md3-datepicker__content {
  padding: $uni-md-space-md;
}

// 导航
.md3-datepicker__navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $uni-md-space-md;
}

.md3-datepicker__month-year {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: $uni-md-space-sm;
  border-radius: $uni-md-radius-small;

  &:hover {
    background-color: $uni-md-surface-variant;
  }
}

.md3-datepicker__month-year-text {
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
  margin-right: $uni-md-space-xs;
}

.md3-datepicker__nav-buttons {
  display: flex;
  gap: $uni-md-space-xs;
}

.md3-datepicker__nav-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color $uni-md-animation-fast ease;

  &:hover {
    background-color: $uni-md-surface-variant;
  }
}

// 年份列表
.md3-datepicker__year-list {
  max-height: 240px;
}

.md3-datepicker__year-item {
  padding: $uni-md-space-md;
  text-align: center;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  cursor: pointer;
  border-radius: $uni-md-radius-full;
  margin: $uni-md-space-xs $uni-md-space-md;
  transition: all $uni-md-animation-fast ease;

  &:hover {
    background-color: $uni-md-surface-variant;
  }

  &.is-selected {
    background-color: $uni-md-color-primary;
    color: white;
  }
}

// 日历
.md3-datepicker__calendar {
  padding: $uni-md-space-sm 0;
}

.md3-datepicker__weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: $uni-md-space-sm;
}

.md3-datepicker__weekday {
  text-align: center;
  font-size: 12px;
  color: $uni-md-text-secondary;
  padding: $uni-md-space-sm 0;
}

.md3-datepicker__days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.md3-datepicker__day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: all $uni-md-animation-fast ease;

  &:hover:not(.is-disabled):not(.is-selected) {
    background-color: $uni-md-surface-variant;
  }

  &.is-other-month {
    .md3-datepicker__day-text {
      color: $uni-md-text-disabled;
    }
  }

  &.is-today {
    border: 1px solid $uni-md-color-primary;
  }

  &.is-selected {
    background-color: $uni-md-color-primary;

    .md3-datepicker__day-text {
      color: white;
    }
  }

  &.is-disabled {
    cursor: not-allowed;

    .md3-datepicker__day-text {
      color: $uni-md-text-disabled;
    }
  }
}

.md3-datepicker__day-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
}

// 操作按钮
.md3-datepicker__actions {
  display: flex;
  justify-content: flex-end;
  gap: $uni-md-space-sm;
  padding: $uni-md-space-md $uni-md-space-lg;
  border-top: 1px solid $uni-md-divider;
}

.md3-datepicker__action-btn {
  padding: $uni-md-space-sm $uni-md-space-md;
  border-radius: $uni-md-radius-small;
  cursor: pointer;
  transition: background-color $uni-md-animation-fast ease;

  &:hover {
    background-color: rgba($uni-md-color-primary, 0.1);
  }
}

.md3-datepicker__action-btn-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  font-weight: 500;

  &--confirm {
    color: $uni-md-color-primary;
  }
}

// 旋转动画
.is-rotated {
  transform: rotate(180deg);
  transition: transform $uni-md-animation-fast ease;
}
</style>
