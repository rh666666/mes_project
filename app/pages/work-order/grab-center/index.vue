<template>
  <view class="page">
    <view class="filter-section">
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">已加载 {{ orderList.length }} / 共 {{ total }} 条待抢单</text>
      </view>
    </view>

    <scroll-view
      scroll-y
      class="order-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <view class="order-cards">
        <view
          v-for="item in orderList"
          :key="item.id"
          class="order-card"
          @click="onRowClick(item)"
        >
          <view class="order-card__header">
            <text class="order-card__code">{{ item.code || `派工单 ${item.id}` }}</text>
            <wd-icon name="arrow-right" size="16" color="#969799" />
          </view>
          <view class="order-card__table">
            <view class="order-card__row">
              <text class="order-card__label">生产任务单</text>
              <text class="order-card__value">{{ item.production_order_code || '-' }}</text>
            </view>
            <view class="order-card__row">
              <text class="order-card__label">工序</text>
              <text class="order-card__value">{{ item.process_name || '-' }}</text>
            </view>
            <view class="order-card__row">
              <text class="order-card__label">生产数量</text>
              <text class="order-card__value order-card__value--emphasis">
                {{ item.quantity != null ? item.quantity : '-' }}
              </text>
            </view>
          </view>
          <view class="order-card__footer" @click.stop>
            <wd-button
              v-if="canGrab(item)"
              type="primary"
              size="small"
              :loading="grabbingId === item.id"
              @click="onOpenGrab(item)"
            >
              抢单
            </wd-button>
            <wd-tag v-else size="small" type="warning">{{ unreachableTip(item) }}</wd-tag>
          </view>
        </view>
      </view>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="orderList.length === 0 && !isLoading" image="search" tip="暂无可抢工单" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <wd-popup
      v-if="grabTarget"
      v-model="showGrabPopup"
      position="bottom"
      :safe-area-inset-bottom="true"
      :root-portal="false"
    >
      <view class="popup-sheet">
        <view class="popup-header">
          <text class="popup-title">抢单</text>
          <wd-icon name="close" size="20" @click="showGrabPopup = false" />
        </view>
        <view class="popup-body">
          <text class="popup-hint">派工单：{{ grabTarget.code || grabTarget.id }}</text>
          <text class="popup-hint">剩余可抢数量：{{ grabRemaining }}</text>
          <wd-input
            v-model="grabForm.quantity"
            type="number"
            label="抢单数量"
            :placeholder="`1 ~ ${grabRemaining}`"
          />
        </view>
        <view class="popup-footer">
          <wd-button
            type="primary"
            size="large"
            block
            :loading="grabbingId === grabTarget.id"
            @click="onConfirmGrab"
          >
            确认抢单
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import dispatchOrderApi from '@/api/dispatch-order'
import { clampApiListLimit, getDispatchRemainingQuantity } from '@/utils/common.js'
import { showToastDeferred, waitAnimationFrames } from '@/utils/loading.js'

/**
 * 抢单中心
 * @description 展示待抢单工序派工单，支持一键抢单（卡片表格化布局）
 */
export default {
  data() {
    return {
      /** @type {Array} 派工单列表 */
      orderList: [],
      /** @type {boolean} 是否加载中 */
      isLoading: false,
      /** @type {boolean} 是否刷新中 */
      isRefreshing: false,
      /** @type {boolean} 是否加载更多中 */
      isLoadingMore: false,
      /** @type {number} 当前页码 */
      currentPage: 1,
      /** @type {number} 每页数量 */
      pageSize: 10,
      /** @type {number} 总数量 */
      total: 0,
      /** @type {boolean} 是否还有更多 */
      hasMore: true,
      /** @type {number} 滚动位置 */
      scrollTop: 0,
      /** @type {number|null} 正在抢单的派工单 ID */
      grabbingId: null,
      /** @type {boolean} 是否首次加载 */
      isFirstLoad: true,
      /** @type {boolean} 抢单弹层 */
      showGrabPopup: false,
      /** @type {Object|null} 当前抢单目标 */
      grabTarget: null,
      /** @type {{quantity: string}} 抢单表单 */
      grabForm: {
        quantity: ''
      }
    }
  },

  computed: {
    /**
     * 当前抢单目标剩余可抢数量
     * @returns {number}
     */
    grabRemaining() {
      return getDispatchRemainingQuantity(this.grabTarget)
    },
    /**
     * 加载更多状态
     * @returns {string}
     */
    loadMoreState() {
      if (this.isLoadingMore) return 'loading'
      if (!this.hasMore && this.orderList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad() {
    this.loadOrderList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadOrderList()
    }
    this.isFirstLoad = false
  },

  methods: {
    /**
     * 是否可抢单
     * @param {Object} item - 派工单行
     * @returns {boolean}
     */
    canGrab(item) {
      if (!item || item.status !== 'pending') {
        return false
      }
      if (item.is_parent) {
        return false
      }
      return item.is_reachable !== false
    },

    /**
     * 不可抢单时的提示
     * @param {Object} item - 派工单行
     * @returns {string}
     */
    unreachableTip(item) {
      if (item && item.is_parent) {
        return '父工单'
      }
      return '暂不可抢'
    },

    /**
     * 拉取待抢单列表
     * @param {boolean} [isLoadMore=false] - 是否追加分页
     * @returns {Promise<void>}
     */
    async loadOrderList(isLoadMore = false) {
      if (isLoadMore) {
        this.isLoadingMore = true
      } else {
        this.isLoading = true
        this.currentPage = 1
        this.hasMore = true
      }

      try {
        const params = {
          page: this.currentPage,
          limit: clampApiListLimit(this.pageSize),
          status: 'pending'
        }

        const res = await dispatchOrderApi.getDispatchOrderList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0
          this.orderList = isLoadMore ? [...this.orderList, ...newData] : newData
          this.hasMore = this.orderList.length < this.total
          return
        }
        uni.showToast({ title: res.msg || '获取列表失败', icon: 'none' })
      } catch (error) {
        console.error('获取抢单列表失败:', error)
        uni.showToast({ title: error.msg || '获取列表失败', icon: 'none' })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 打开抢单弹层（剩余为 1 时直接抢单）
     * @param {Object} item - 派工单行
     */
    onOpenGrab(item) {
      if (!this.canGrab(item) || this.grabbingId != null) {
        return
      }
      const remaining = getDispatchRemainingQuantity(item)
      if (remaining < 1) {
        uni.showToast({ title: '该工单无可抢数量', icon: 'none' })
        return
      }
      if (remaining === 1) {
        this.submitGrab(item, 1, false)
        return
      }
      this.grabTarget = item
      this.grabForm = { quantity: String(remaining) }
      this.showGrabPopup = true
    },

    /**
     * 确认抢单
     * @returns {Promise<void>}
     */
    async onConfirmGrab() {
      if (!this.grabTarget) {
        return
      }
      const remaining = this.grabRemaining
      const quantity = parseInt(String(this.grabForm.quantity).trim(), 10)
      if (Number.isNaN(quantity) || quantity < 1) {
        uni.showToast({ title: '请输入有效的抢单数量', icon: 'none' })
        return
      }
      if (quantity > remaining) {
        uni.showToast({ title: `抢单数量不能超过 ${remaining}`, icon: 'none' })
        return
      }
      await this.submitGrab(this.grabTarget, quantity, true)
    },

    /**
     * 提交抢单
     * @param {Object} item - 派工单行
     * @param {number} quantity - 抢单数量
     * @param {boolean} fromPopup - 是否来自弹层
     * @returns {Promise<void>}
     */
    async submitGrab(item, quantity, fromPopup) {
      if (!this.canGrab(item) || this.grabbingId != null) {
        return
      }
      const remaining = getDispatchRemainingQuantity(item)
      const payload = quantity < remaining ? { quantity } : {}

      this.grabbingId = item.id
      try {
        const res = await dispatchOrderApi.grabDispatchOrder(item.id, payload)
        if (res.code === 2000) {
          if (fromPopup) {
            this.showGrabPopup = false
            this.grabTarget = null
          }
          this.grabbingId = null
          await this.$nextTick()
          await this.loadOrderList(false)
          await this.$nextTick()
          await waitAnimationFrames(2)
          showToastDeferred({ title: res.msg || '抢单成功', icon: 'success' }, 250)
          return
        }
        uni.showToast({ title: res.msg || '抢单失败', icon: 'none' })
      } catch (error) {
        console.error('抢单失败:', error)
        uni.showToast({ title: error.msg || '抢单失败', icon: 'none' })
      } finally {
        this.grabbingId = null
      }
    },

    /**
     * 下拉刷新
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadOrderList(false)
    },

    /**
     * 触底加载更多
     * @returns {Promise<void>}
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadOrderList(true)
    },

    /**
     * 滚动事件
     * @param {Object} e - 事件对象
     */
    onScroll(e) {
      this.scrollTop = e.detail.scrollTop
    },

    /**
     * 进入详情
     * @param {Object} item - 派工单行
     */
    onRowClick(item) {
      uni.navigateTo({
        url: `/pages/work-order/dispatch-detail/index?id=${item.id}&from=grab`
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $uni-bg-color;
}

.filter-section {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-bottom: 1px solid $uni-border-color;
}

.results-stats {
  display: flex;
  align-items: center;
}

.stats-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.order-list {
  flex: 1;
  overflow-y: auto;
}

.order-cards {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.order-card {
  padding: 24rpx;
  border-radius: 16rpx;
  background-color: $uni-bg-color-white;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.order-card__header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1px solid $uni-border-color;
}

.order-card__code {
  font-size: 30rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.order-card__table {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.order-card__row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  line-height: 1.5;
}

.order-card__label {
  flex-shrink: 0;
  width: 152rpx;
  font-size: 26rpx;
  color: $uni-text-color-grey;
}

.order-card__value {
  flex: 1;
  min-width: 0;
  font-size: 26rpx;
  color: $uni-text-color;
  word-break: break-all;
}

.order-card__value--emphasis {
  font-weight: 500;
  color: $uni-color-primary;
}

.order-card__footer {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 20rpx;
  padding-top: 16rpx;
  border-top: 1px solid $uni-border-color;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
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

.popup-hint {
  display: block;
  margin-bottom: 12rpx;
  font-size: 26rpx;
  color: $uni-text-color-grey;
}

.popup-footer {
  padding: 24rpx 32rpx 32rpx;
}
</style>
