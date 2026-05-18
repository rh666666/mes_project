<template>
  <view class="page">
    <view v-if="order" class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell title="派工单编码" :value="order.code || '-'" />
        <wd-cell title="状态" :value="order.status_display || order.status || '-'" />
        <wd-cell title="生产任务单" :value="order.production_order_code || '-'" />
        <wd-cell title="工序" :value="processSummary" />
        <wd-cell title="生产数量" :value="order.quantity != null ? String(order.quantity) : '-'" />
        <wd-cell title="已完成数量" :value="order.completed_quantity != null ? String(order.completed_quantity) : '-'" />
        <wd-cell title="接单人" :value="order.operator_name || '-'" />
        <wd-cell title="创建时间" :value="formatDateTime(order.create_datetime)" />
        <wd-cell title="更新时间" :value="formatDateTime(order.update_datetime)" />
      </wd-cell-group>

      <view class="action-section">
        <wd-button
          v-if="canGrab"
          type="primary"
          size="large"
          block
          :loading="actionLoading === 'grab'"
          @click="onGrab"
        >
          抢单
        </wd-button>
        <wd-button
          v-if="canStart"
          type="primary"
          size="large"
          block
          :loading="actionLoading === 'start'"
          @click="onStart"
        >
          开始生产
        </wd-button>
        <wd-button
          v-if="canPause"
          plain
          size="large"
          block
          :loading="actionLoading === 'pause'"
          @click="onPause"
        >
          暂停生产
        </wd-button>
        <wd-button
          v-if="canReport"
          type="primary"
          size="large"
          block
          @click="onOpenReport"
        >
          生产报工
        </wd-button>
        <wd-button plain size="large" block :loading="reportNavLoading" @click="onGoReportDetail">
          查看报工记录
        </wd-button>
      </view>
    </view>

    <view v-else-if="!loadError" class="loading-wrap">
      <wd-loading />
    </view>
    <wd-status-tip v-else image="search" :tip="loadError" />

    <wd-popup v-model="showReportPopup" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-sheet">
        <view class="popup-header">
          <text class="popup-title">生产报工</text>
          <wd-icon name="close" size="20" @click="showReportPopup = false" />
        </view>
        <view class="popup-body">
          <wd-input v-model="reportForm.quantity" type="number" label="报工数量" placeholder="请输入正整数" />
          <wd-input v-model="reportForm.work_time" label="工时" placeholder="格式 HH:MM:SS，如 01:30:00" />
        </view>
        <view class="popup-footer">
          <wd-button
            type="primary"
            size="large"
            block
            :loading="actionLoading === 'report'"
            @click="onConfirmReport"
          >
            提交报工
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import dispatchOrderApi from '@/api/dispatch-order'
import productionReportApi from '@/api/production-report'
import { clampApiListLimit } from '@/utils/common.js'
import { formatDateTime } from '@/utils/format.js'

/**
 * 工序派工单详情（员工）
 * @description 展示派工单详情，支持抢单、开工、暂停、报工
 */
export default {
  data() {
    return {
      /** @type {number|null} 派工单 ID */
      orderId: null,
      /** @type {Object|null} 详情数据 */
      order: null,
      /** @type {string} 加载错误 */
      loadError: '',
      /** @type {string} 进行中的操作 */
      actionLoading: '',
      /** @type {boolean} 报工弹层 */
      showReportPopup: false,
      /** @type {{quantity: string, work_time: string}} 报工表单 */
      reportForm: {
        quantity: '',
        work_time: '01:00:00'
      },
      /** @type {boolean} 跳转报工详情加载中 */
      reportNavLoading: false
    }
  },

  computed: {
    /**
     * 工序展示
     * @returns {string}
     */
    processSummary() {
      if (!this.order) return '-'
      const name = this.order.process_name || ''
      const code = this.order.process_code || ''
      if (name && code) return `${name} (${code})`
      return name || code || '-'
    },

    /**
     * 是否可抢单
     * @returns {boolean}
     */
    canGrab() {
      if (!this.order || this.order.status !== 'pending') {
        return false
      }
      if (this.order.is_parent) {
        return false
      }
      return this.order.is_reachable !== false
    },

    /**
     * 是否可开始生产
     * @returns {boolean}
     */
    canStart() {
      if (!this.order) return false
      return ['dispatched', 'grabbed', 'paused'].includes(this.order.status)
    },

    /**
     * 是否可暂停
     * @returns {boolean}
     */
    canPause() {
      return this.order && this.order.status === 'in_progress'
    },

    /**
     * 是否可报工
     * @returns {boolean}
     */
    canReport() {
      if (!this.order) return false
      return ['in_progress', 'grabbed'].includes(this.order.status)
    }
  },

  onLoad(options) {
    if (!options.id) {
      this.loadError = '缺少派工单 ID'
      return
    }
    this.orderId = Number(options.id)
    this.loadAll()
  },

  methods: {
    formatDateTime,

    /**
     * 加载详情
     * @returns {Promise<void>}
     */
    async loadAll() {
      this.loadError = ''
      try {
        const res = await dispatchOrderApi.getDispatchOrderDetail(this.orderId)
        if (res.code !== 2000) {
          this.loadError = res.msg || '加载失败'
          return
        }
        this.order = res.data || null
      } catch (error) {
        console.error('加载派工单详情失败:', error)
        this.loadError = error.msg || '加载失败'
      }
    },

    /**
     * 抢单
     * @returns {Promise<void>}
     */
    async onGrab() {
      if (!this.orderId || !this.canGrab) return
      this.actionLoading = 'grab'
      try {
        const res = await dispatchOrderApi.grabDispatchOrder(this.orderId)
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '抢单成功', icon: 'success' })
          await this.loadAll()
          return
        }
        uni.showToast({ title: res.msg || '抢单失败', icon: 'none' })
      } catch (error) {
        console.error('抢单失败:', error)
        uni.showToast({ title: error.msg || '抢单失败', icon: 'none' })
      } finally {
        this.actionLoading = ''
      }
    },

    /**
     * 开始生产
     * @returns {Promise<void>}
     */
    async onStart() {
      if (!this.orderId || !this.canStart) return
      this.actionLoading = 'start'
      try {
        const res = await dispatchOrderApi.startDispatchOrder(this.orderId)
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '已开始生产', icon: 'success' })
          await this.loadAll()
          return
        }
        uni.showToast({ title: res.msg || '操作失败', icon: 'none' })
      } catch (error) {
        console.error('开始生产失败:', error)
        uni.showToast({ title: error.msg || '操作失败', icon: 'none' })
      } finally {
        this.actionLoading = ''
      }
    },

    /**
     * 暂停生产
     * @returns {Promise<void>}
     */
    async onPause() {
      if (!this.orderId || !this.canPause) return
      this.actionLoading = 'pause'
      try {
        const res = await dispatchOrderApi.pauseDispatchOrder(this.orderId)
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '已暂停', icon: 'success' })
          await this.loadAll()
          return
        }
        uni.showToast({ title: res.msg || '操作失败', icon: 'none' })
      } catch (error) {
        console.error('暂停生产失败:', error)
        uni.showToast({ title: error.msg || '操作失败', icon: 'none' })
      } finally {
        this.actionLoading = ''
      }
    },

    /**
     * 打开报工弹层
     */
    onOpenReport() {
      this.reportForm = { quantity: '', work_time: '01:00:00' }
      this.showReportPopup = true
    },

    /**
     * 提交报工
     * @returns {Promise<void>}
     */
    async onConfirmReport() {
      const quantity = parseInt(String(this.reportForm.quantity).trim(), 10)
      if (Number.isNaN(quantity) || quantity < 1) {
        uni.showToast({ title: '请输入有效的报工数量', icon: 'none' })
        return
      }
      const workTime = String(this.reportForm.work_time || '').trim()
      if (!workTime) {
        uni.showToast({ title: '请输入工时', icon: 'none' })
        return
      }
      if (!this.orderId) return

      this.actionLoading = 'report'
      try {
        const res = await dispatchOrderApi.reportDispatchOrder(this.orderId, {
          dispatch_order_id: this.orderId,
          quantity,
          work_time: workTime
        })
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '报工成功', icon: 'success' })
          this.showReportPopup = false
          await this.loadAll()
          return
        }
        uni.showToast({ title: res.msg || '报工失败', icon: 'none' })
      } catch (error) {
        console.error('报工失败:', error)
        uni.showToast({ title: error.msg || '报工失败', icon: 'none' })
      } finally {
        this.actionLoading = ''
      }
    },

    /**
     * 跳转该派工单最新一条报工记录详情
     * @returns {Promise<void>}
     */
    async onGoReportDetail() {
      if (this.orderId == null || this.reportNavLoading) {
        return
      }

      this.reportNavLoading = true
      try {
        const res = await productionReportApi.getProductionReportList({
          dispatch_order: this.orderId,
          page: 1,
          limit: clampApiListLimit(1)
        })
        const latest = res.code === 2000 && res.data && res.data.length > 0 ? res.data[0] : null
        if (latest && latest.id != null) {
          uni.navigateTo({
            url: `/pages/work-order/report-detail/index?id=${latest.id}`
          })
          return
        }
        uni.showToast({ title: res.msg || '暂无报工记录', icon: 'none' })
      } catch (error) {
        console.error('获取报工记录失败:', error)
        uni.showToast({ title: error.msg || '获取报工记录失败', icon: 'none' })
      } finally {
        this.reportNavLoading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $uni-bg-color;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.content {
  padding: 24rpx;
}

.section-header {
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 80rpx;
}

.action-section {
  margin-top: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.popup-sheet {
  background-color: $uni-bg-color-white;
  border-radius: 24rpx 24rpx 0 0;
  padding-bottom: env(safe-area-inset-bottom);
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  border-bottom: 1px solid $uni-border-color;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.popup-body {
  padding: 24rpx 32rpx;
}

.popup-footer {
  padding: 24rpx 32rpx 32rpx;
}
</style>
