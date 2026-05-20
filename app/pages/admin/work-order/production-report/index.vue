<template>
  <view class="page">
    <view class="filter-section">
      <view v-if="filterDispatchOrder != null" class="task-filter-hint">
        <text class="hint-text">当前筛选工序派工单 ID：{{ filterDispatchOrder }}</text>
      </view>
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">已加载 {{ reportList.length }} / 共 {{ total }} 条</text>
        <wd-tag v-if="hasActiveFilters" type="primary" size="small">已筛选</wd-tag>
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
      <wd-cell-group>
        <wd-cell
          v-for="item in reportList"
          :key="item.id"
          :title="item.code || `报工 ${item.id}`"
          clickable
          @click="onRowClick(item)"
        >
          <template #label>
            <view class="cell-multiline-label">
              <text class="cell-label-line">{{ cellLabelLine1(item) }}</text>
              <text class="cell-label-line cell-label-line--sub">{{ cellLabelLine2(item) }}</text>
            </view>
          </template>
          <template #value>
            <wd-icon name="arrow-right" size="16" color="#969799" />
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="reportList.length === 0 && !isLoading" image="search" tip="暂无生产报工记录" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import productionReportApi from '@/api/production-report'
import { getStorageKey } from '@/config/index.js'
import { clampApiListLimit } from '@/utils/common.js'

/**
 * 生产报工单列表（管理员）
 * @description 分页列表；支持从派工单详情传入 dispatch_order 过滤
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
      /** @type {number|null} 工序派工单 ID 筛选（来自 URL） */
      filterDispatchOrder: null,
      /** @type {boolean} 是否首次加载 */
      isFirstLoad: true
    }
  },

  computed: {
    /**
     * 是否有筛选条件
     * @returns {boolean}
     */
    hasActiveFilters() {
      return this.filterDispatchOrder != null
    },

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
    if (!this.assertAdmin()) {
      return
    }
    if (options.dispatch_order) {
      const n = Number(options.dispatch_order)
      if (!Number.isNaN(n)) {
        this.filterDispatchOrder = n
      }
    }
    this.loadReportList()
  },

  onShow() {
    if (!this.assertAdmin()) {
      return
    }
    if (!this.isFirstLoad) {
      this.loadReportList()
    }
    this.isFirstLoad = false
  },

  methods: {
    /**
     * 校验管理员角色，非法则提示并返回上一页
     * @returns {boolean}
     */
    assertAdmin() {
      const userInfo = uni.getStorageSync(getStorageKey('user_info')) || {}
      if (userInfo.role !== 'admin') {
        uni.showToast({ title: '无权限访问', icon: 'none' })
        setTimeout(() => {
          uni.navigateBack({ fail: () => {} })
        }, 400)
        return false
      }
      return true
    },

    /**
     * 副标题第一行：派工单号、工序名称
     * @param {Object} item - 报工行
     * @returns {string}
     */
    cellLabelLine1(item) {
      const dispatch = item.dispatch_order_code || '-'
      const proc = item.process_name || '-'
      return `${dispatch}  ${proc}`
    },

    /**
     * 副标题第二行：数量、日期
     * @param {Object} item - 报工行
     * @returns {string}
     */
    cellLabelLine2(item) {
      const qty = item.quantity != null ? item.quantity : '-'
      const date = item.report_date || '-'
      return `数量 ${qty}  日期 ${date}`
    },

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
        console.error('获取生产报工列表失败:', error)
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
        url: `/pages/admin/work-order/production-report/detail?id=${item.id}`
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
  position: sticky;
  top: var(--window-top, 0);
  z-index: 100;
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
  gap: 16rpx;
}

.stats-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.report-list {
  flex: 1;
  overflow-y: auto;
}

.cell-multiline-label {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.cell-label-line {
  font-size: 24rpx;
  color: $uni-text-color-grey;
  line-height: 1.5;
  word-break: break-all;
}

.cell-label-line--sub {
  font-size: 22rpx;
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
