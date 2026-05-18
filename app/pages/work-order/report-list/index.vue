<template>
  <view class="page">
    <view class="filter-section">
      <view v-if="filterDispatchOrder != null" class="task-filter-hint">
        <text class="hint-text">当前筛选工序派工单 ID：{{ filterDispatchOrder }}</text>
      </view>
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">已加载 {{ reportList.length }} / 共 {{ total }} 条</text>
      </view>
    </view>

    <scroll-view
      scroll-y
      class="report-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <view class="report-cards">
        <view
          v-for="item in reportList"
          :key="item.id"
          class="report-card"
          @click="onRowClick(item)"
        >
          <view class="report-card__header">
            <text class="report-card__code">{{ item.code || `报工 ${item.id}` }}</text>
            <wd-icon name="arrow-right" size="16" color="#969799" />
          </view>
          <view class="report-card__table">
            <view v-if="filterDispatchOrder == null" class="report-card__row">
              <text class="report-card__label">派工单</text>
              <text class="report-card__value">{{ item.dispatch_order_code || '-' }}</text>
            </view>
            <view class="report-card__row">
              <text class="report-card__label">工序</text>
              <text class="report-card__value">{{ item.process_name || '-' }}</text>
            </view>
            <view class="report-card__row">
              <text class="report-card__label">报工数量</text>
              <text class="report-card__value report-card__value--emphasis">
                {{ item.quantity != null ? item.quantity : '-' }}
              </text>
            </view>
            <view class="report-card__row">
              <text class="report-card__label">报工日期</text>
              <text class="report-card__value">{{ item.report_date || '-' }}</text>
            </view>
            <view class="report-card__row">
              <text class="report-card__label">创建时间</text>
              <text class="report-card__value">{{ formatDateTime(item.create_datetime) }}</text>
            </view>
          </view>
        </view>
      </view>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="reportList.length === 0 && !isLoading" image="search" tip="暂无报工记录" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import productionReportApi from '@/api/production-report'
import { clampApiListLimit } from '@/utils/common.js'
import { formatDateTime } from '@/utils/format.js'

/**
 * 报工记录
 * @description 分页展示生产报工记录（卡片表格化布局）
 */
export default {
  data() {
    return {
      /** @type {Array} 报工列表 */
      reportList: [],
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
      /** @type {number|null} 工序派工单 ID 筛选 */
      filterDispatchOrder: null,
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
      if (!this.hasMore && this.reportList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad(options) {
    if (options.dispatch_order) {
      const n = Number(options.dispatch_order)
      if (!Number.isNaN(n)) {
        this.filterDispatchOrder = n
      }
    }
    this.loadReportList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadReportList()
    }
    this.isFirstLoad = false
  },

  methods: {
    formatDateTime,

    /**
     * 拉取报工列表
     * @param {boolean} [isLoadMore=false] - 是否追加分页
     * @returns {Promise<void>}
     */
    async loadReportList(isLoadMore = false) {
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
          limit: clampApiListLimit(this.pageSize)
        }
        if (this.filterDispatchOrder != null) {
          params.dispatch_order = this.filterDispatchOrder
        }

        const res = await productionReportApi.getProductionReportList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0
          this.reportList = isLoadMore ? [...this.reportList, ...newData] : newData
          this.hasMore = this.reportList.length < this.total
          return
        }
        uni.showToast({ title: res.msg || '获取列表失败', icon: 'none' })
      } catch (error) {
        console.error('获取报工记录失败:', error)
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
      this.loadReportList(false)
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
      await this.loadReportList(true)
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
     * @param {Object} item - 报工行
     */
    onRowClick(item) {
      uni.navigateTo({
        url: `/pages/work-order/report-detail/index?id=${item.id}`
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

.task-filter-hint {
  margin-bottom: 16rpx;
}

.hint-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.results-stats {
  display: flex;
  align-items: center;
}

.stats-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.report-list {
  flex: 1;
  overflow-y: auto;
}

.report-cards {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.report-card {
  padding: 24rpx;
  border-radius: 16rpx;
  background-color: $uni-bg-color-white;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.report-card__header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1px solid $uni-border-color;
}

.report-card__code {
  font-size: 30rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.report-card__table {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.report-card__row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  line-height: 1.5;
}

.report-card__label {
  flex-shrink: 0;
  width: 152rpx;
  font-size: 26rpx;
  color: $uni-text-color-grey;
}

.report-card__value {
  flex: 1;
  min-width: 0;
  font-size: 26rpx;
  color: $uni-text-color;
  word-break: break-all;
}

.report-card__value--emphasis {
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
