<template>
  <view class="page">
    <view class="filter-section">
      <view class="filter-row">
        <wd-picker
          v-model="filterType"
          placeholder="类型"
          :columns="typeColumns"
          @confirm="onFilterChange"
        />
      </view>
      <view v-if="filterProductionOrder != null" class="task-filter-hint">
        <text class="hint-text">当前筛选生产任务单 ID：{{ filterProductionOrder }}</text>
      </view>
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">已加载 {{ orderList.length }} / 共 {{ total }} 条</text>
        <wd-tag v-if="hasActiveFilters" type="primary" size="small">已筛选</wd-tag>
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
          :title="item.code || `质检 ${item.id}`"
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
            <view class="cell-right">
              <wd-tag size="small" type="primary">{{ item.status_display || item.status }}</wd-tag>
              <wd-icon name="arrow-right" size="16" color="#969799" />
            </view>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="orderList.length === 0 && !isLoading" image="search" tip="暂无质检任务单" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import qualityCheckOrderApi from '@/api/quality-check-order'
import { getStorageKey } from '@/config/index.js'
import { clampApiListLimit } from '@/utils/common.js'

/**
 * 质检任务单列表（管理员）
 * @description 分页列表、按类型筛选；支持从任务单详情传入 production_order 过滤
 */
export default {
  data() {
    return {
      /** @type {Array} 质检任务单列表 */
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
      /** @type {string} 类型筛选 */
      filterType: '',
      /** @type {number|null} 生产任务单 ID 筛选（来自 URL） */
      filterProductionOrder: null,
      /** @type {boolean} 是否首次加载 */
      isFirstLoad: true
    }
  },

  computed: {
    /**
     * 类型筛选项（与后端 QualityCheckOrder.Type 对齐）
     * @returns {Array<{value:string,label:string}>}
     */
    typeColumns() {
      return [
        { value: '', label: '全部类型' },
        { value: 'first', label: '首检' },
        { value: 'process', label: '过程检' },
        { value: 'completion', label: '完工检' }
      ]
    },

    /**
     * 是否有筛选条件
     * @returns {boolean}
     */
    hasActiveFilters() {
      return this.filterType !== '' || this.filterProductionOrder != null
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

  onLoad(options) {
    if (!this.assertAdmin()) {
      return
    }
    if (options.production_order) {
      const n = Number(options.production_order)
      if (!Number.isNaN(n)) {
        this.filterProductionOrder = n
      }
    }
    this.loadOrderList()
  },

  onShow() {
    if (!this.assertAdmin()) {
      return
    }
    if (!this.isFirstLoad) {
      this.loadOrderList()
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
     * 副标题第一行：类型、生产任务单号
     * @param {Object} item - 质检任务单行
     * @returns {string}
     */
    cellLabelLine1(item) {
      const typeLabel = item.type_display || item.type || '-'
      const po = item.production_order_code || '-'
      return `${typeLabel}  ${po}`
    },

    /**
     * 副标题第二行：物料、顺序（质检数量）、合格率
     * @param {Object} item - 质检任务单行
     * @returns {string}
     */
    cellLabelLine2(item) {
      const product = item.product_name || '-'
      const sequence = item.quantity != null ? item.quantity : '-'
      const passRate = this.formatPassRate(item)
      return `${product}  顺序 ${sequence}  合格率 ${passRate}`
    },

    /**
     * 格式化合格率
     * @param {Object} item - 质检任务单行
     * @returns {string}
     */
    formatPassRate(item) {
      const qty = Number(item.quantity)
      if (!qty || qty <= 0) {
        return '-'
      }
      if (item.status === 'pending') {
        return '-'
      }
      const qualified = Number(item.qualified_quantity) || 0
      return `${((qualified / qty) * 100).toFixed(1)}%`
    },

    /**
     * 拉取质检任务单列表
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
          limit: clampApiListLimit(this.pageSize)
        }
        if (this.filterType !== '') {
          params.type = this.filterType
        }
        if (this.filterProductionOrder != null) {
          params.production_order = this.filterProductionOrder
        }

        const res = await qualityCheckOrderApi.getQualityCheckOrderList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0
          this.orderList = isLoadMore ? [...this.orderList, ...newData] : newData
          this.hasMore = this.orderList.length < this.total
          return
        }
        uni.showToast({ title: res.msg || '获取列表失败', icon: 'none' })
      } catch (error) {
        console.error('获取质检任务单列表失败:', error)
        uni.showToast({ title: error.msg || '获取列表失败', icon: 'none' })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 筛选变更后重新加载
     */
    onFilterChange() {
      this.loadOrderList(false)
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
     * @param {Object} item - 质检任务单行
     */
    onRowClick(item) {
      uni.navigateTo({
        url: `/pages/admin/work-order/quality-check-order/detail?id=${item.id}`
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

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.task-filter-hint {
  margin-top: 16rpx;
}

.hint-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
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

.cell-right {
  display: flex;
  align-items: center;
  gap: 12rpx;
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
