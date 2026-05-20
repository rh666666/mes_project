<template>
  <view class="page">
    <view class="filter-section">
      <view class="status-filter">
        <wd-tabs v-model="selectedStatus">
          <wd-tab title="全部" name="all" />
          <wd-tab
            v-for="status in statusOptions"
            :key="status.value"
            :title="status.label"
            :name="status.value"
          />
        </wd-tabs>
      </view>
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">已加载 {{ orderList.length }} / 共 {{ total }} 条</text>
        <wd-tag v-if="selectedStatus && selectedStatus !== 'all'" type="primary" size="small">已筛选</wd-tag>
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
            <view class="order-card__header-right">
              <wd-tag size="small" type="primary">{{ item.status_display || item.status }}</wd-tag>
              <wd-icon name="arrow-right" size="16" color="#969799" />
            </view>
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
              <text class="order-card__label">完成进度</text>
              <text class="order-card__value order-card__value--emphasis">{{ formatProgress(item) }}</text>
            </view>
          </view>
        </view>
      </view>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="orderList.length === 0 && !isLoading" image="search" tip="暂无我的工单" />
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
 * 我的工单
 * @description 展示当前用户接取的工序派工单，支持按状态筛选（卡片表格化布局）
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
      /** @type {string} 选中的状态筛选 */
      selectedStatus: 'all',
      /** @type {Array<{value:string,label:string}>} 状态选项（不含待抢单） */
      statusOptions: [
        { value: 'dispatched', label: '已派工' },
        { value: 'grabbed', label: '已抢单' },
        { value: 'in_progress', label: '生产中' },
        { value: 'paused', label: '已暂停' },
        { value: 'waiting_previous', label: '等待前置工序' },
        { value: 'completed', label: '已完成' }
      ],
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

  watch: {
    /**
     * 监听状态 Tab 切换并重新加载列表
     * @param {string} newVal - 新状态
     * @param {string} oldVal - 旧状态
     */
    selectedStatus(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.loadOrderList(false)
      }
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
     * 格式化完成进度
     * @param {Object} item - 派工单行
     * @returns {string}
     */
    formatProgress(item) {
      const done = item.completed_quantity != null ? item.completed_quantity : 0
      const qty = item.quantity != null ? item.quantity : '-'
      return `${done}/${qty}`
    },

    /**
     * 拉取我的派工单列表
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
          mine: true
        }
        if (this.selectedStatus && this.selectedStatus !== 'all') {
          params.status = this.selectedStatus
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
        console.error('获取我的工单列表失败:', error)
        uni.showToast({ title: error.msg || '获取列表失败', icon: 'none' })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
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
        url: `/pages/work-order/dispatch-detail/index?id=${item.id}&from=my`
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

.status-filter {
  margin-top: 0;
}

.results-stats {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1px solid $uni-border-color;
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

.order-card__header-right {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12rpx;
}

.order-card__code {
  flex: 1;
  min-width: 0;
  font-size: 30rpx;
  font-weight: 500;
  color: $uni-text-color;
  word-break: break-all;
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
