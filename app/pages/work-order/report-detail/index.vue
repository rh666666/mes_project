<template>
  <view class="page">
    <view v-if="report" class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell title="报工编码" :value="report.code || '-'" />
        <wd-cell
          title="工序派工单"
          :value="report.dispatch_order_code || '-'"
          is-link
          @click="onGoDispatchOrder"
        />
        <wd-cell title="工序" :value="report.process_name || '-'" />
        <wd-cell title="报工数量" :value="report.quantity != null ? String(report.quantity) : '-'" />
        <wd-cell title="工作时间" :value="workTimeDisplay" />
        <wd-cell title="报工日期" :value="report.report_date || '-'" />
        <wd-cell title="创建时间" :value="formatDateTime(report.create_datetime)" />
      </wd-cell-group>
    </view>

    <view v-else-if="!loadError" class="loading-wrap">
      <wd-loading />
    </view>
    <wd-status-tip v-else image="search" :tip="loadError" />
  </view>
</template>

<script>
import productionReportApi from '@/api/production-report'
import { formatDateTime, formatDuration } from '@/utils/format.js'

/**
 * 生产报工详情（员工）
 * @description 只读展示本人报工记录，可跳转关联派工单详情
 */
export default {
  data() {
    return {
      /** @type {number|null} 报工记录 ID */
      reportId: null,
      /** @type {Object|null} 详情数据 */
      report: null,
      /** @type {string} 加载错误 */
      loadError: ''
    }
  },

  computed: {
    /**
     * 工作时间展示
     * @returns {string}
     */
    workTimeDisplay() {
      if (!this.report) {
        return '-'
      }
      return formatDuration(this.report.work_time)
    }
  },

  onLoad(options) {
    if (options.id) {
      const n = Number(options.id)
      if (!Number.isNaN(n)) {
        this.reportId = n
        this.loadDetail()
        return
      }
    }
    this.loadError = '缺少报工记录 ID'
  },

  methods: {
    formatDateTime,

    /**
     * 加载报工详情
     * @returns {Promise<void>}
     */
    async loadDetail() {
      if (this.reportId == null) {
        return
      }
      this.loadError = ''
      try {
        const res = await productionReportApi.getProductionReportDetail(this.reportId)
        if (res.code === 2000 && res.data) {
          this.report = res.data
          return
        }
        this.loadError = res.msg || '加载失败'
      } catch (error) {
        console.error('加载生产报工详情失败:', error)
        this.loadError = error.msg || '加载失败'
      }
    },

    /**
     * 跳转关联工序派工单详情
     */
    onGoDispatchOrder() {
      if (!this.report || !this.report.dispatch_order) {
        uni.showToast({ title: '无关联派工单', icon: 'none' })
        return
      }
      uni.navigateTo({
        url: `/pages/work-order/dispatch-detail/index?id=${this.report.dispatch_order}`
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $uni-bg-color;
}

.content {
  padding: 24rpx;
}

.section-header {
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 26rpx;
  font-weight: 500;
  color: $uni-text-color-grey;
}

.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
</style>
