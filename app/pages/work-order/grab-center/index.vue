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
      <wd-cell-group>
        <wd-cell
          v-for="item in orderList"
          :key="item.id"
          :title="item.code || `派工单 ${item.id}`"
          :label="cellLabel(item)"
          clickable
          @click="onRowClick(item)"
        >
          <template #value>
            <view class="cell-right">
              <wd-button
                v-if="canGrab(item)"
                type="primary"
                size="small"
                :loading="grabbingId === item.id"
                @click.stop="onGrab(item)"
              >
                抢单
              </wd-button>
              <wd-tag v-else size="small" type="warning">{{ unreachableTip(item) }}</wd-tag>
              <wd-icon name="arrow-right" size="16" color="#969799" />
            </view>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="orderList.length === 0 && !isLoading" image="search" tip="暂无可抢工单" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import dispatchOrderApi from '@/api/dispatch-order'
import { clampApiListLimit } from '@/utils/common.js'

/**
 * 抢单中心
 * @description 展示待抢单工序派工单，支持一键抢单
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
      isFirstLoad: true
    }
  },

  computed: {
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
     * 列表项副标题
     * @param {Object} item - 派工单行
     * @returns {string}
     */
    cellLabel(item) {
      const po = item.production_order_code || '-'
      const proc = item.process_name || '-'
      const qty = item.quantity != null ? item.quantity : '-'
      return `${po}  ${proc}  数量 ${qty}`
    },

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
     * 抢单
     * @param {Object} item - 派工单行
     * @returns {Promise<void>}
     */
    async onGrab(item) {
      if (!this.canGrab(item) || this.grabbingId != null) {
        return
      }

      this.grabbingId = item.id
      try {
        const res = await dispatchOrderApi.grabDispatchOrder(item.id)
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '抢单成功', icon: 'success' })
          this.loadOrderList(false)
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

.cell-right {
  display: flex;
  align-items: center;
  gap: 12rpx;
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
</style>
