<template>
  <view class="page">
    <view class="filter-section">
      <view class="filter-row">
        <wd-picker
          v-model="filterStatus"
          placeholder="状态"
          :columns="statusColumns"
          @confirm="onFilterChange"
        />
        <wd-picker
          v-model="filterProduct"
          placeholder="产品"
          :columns="productColumns"
          @confirm="onFilterChange"
        />
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
          :title="item.code || `任务单 ${item.id}`"
          clickable
          @click="onOrderClick(item)"
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

      <wd-status-tip v-if="orderList.length === 0 && !isLoading" image="search" tip="暂无生产任务单" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <view class="fab-container" @click="onCreate">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>
  </view>
</template>

<script>
import productionOrderApi from '@/api/production-order'
import materialApi from '@/api/material'
import { getStorageKey } from '@/config/index.js'
import { clampApiListLimit, fetchAllPagesWithPagedApi } from '@/utils/common.js'

/**
 * 生产任务单列表（管理员）
 * @description 分页列表、按状态与产品筛选、进入详情与新建（两行副标题）
 */
export default {
  data() {
    return {
      /** @type {Array} 任务单列表 */
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
      /** @type {string} 状态筛选 */
      filterStatus: '',
      /** @type {number|string} 产品筛选 */
      filterProduct: '',
      /** @type {Array} 产成品选项（筛选用） */
      productPickerSource: [],
      /** @type {boolean} 是否首次加载 */
      isFirstLoad: true
    }
  },

  computed: {
    /**
     * 状态筛选项
     * @returns {Array<{value:string,label:string}>}
     */
    statusColumns() {
      return [
        { value: '', label: '全部状态' },
        { value: 'pending', label: '已创建' },
        { value: 'published', label: '已下发' },
        { value: 'cancelled', label: '已取消' },
        { value: 'completed', label: '已完成' },
        { value: 'obsolete', label: '已废弃' }
      ]
    },

    /**
     * 产品筛选项（含全部）
     * @returns {Array<{value:number|string,label:string}>}
     */
    productColumns() {
      const columns = [{ value: '', label: '全部产品' }]
      this.productPickerSource.forEach((m) => {
        columns.push({
          value: m.id,
          label: m.name ? `${m.name} (${m.code || ''})` : String(m.id)
        })
      })
      return columns
    },

    /**
     * 是否有筛选条件
     * @returns {boolean}
     */
    hasActiveFilters() {
      return this.filterStatus !== '' || this.filterProduct !== ''
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
    if (!this.assertAdmin()) {
      return
    }
    this.loadProductOptions()
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
     * 加载产成品列表供筛选（单次拉取后在内存中过滤）
     * @returns {Promise<void>}
     */
    async loadProductOptions() {
      try {
        const rows = await fetchAllPagesWithPagedApi((p) => materialApi.getMaterialList(p), {})
        this.productPickerSource = rows.filter((m) => m.is_production)
      } catch (e) {
        console.error('加载产品筛选列表失败:', e)
      }
    },

    /**
     * 副标题第一行：产品名称、产品编码
     * @param {Object} item - 任务单行
     * @returns {string}
     */
    cellLabelLine1(item) {
      const name = item.product_name || '-'
      const code = item.product_code || '-'
      return `${name}  ${code}`
    },

    /**
     * 副标题第二行：生产数量、派工进度
     * @param {Object} item - 任务单行
     * @returns {string}
     */
    cellLabelLine2(item) {
      const qty = item.quantity != null ? item.quantity : '-'
      const done = item.completed_dispatch_count != null ? item.completed_dispatch_count : 0
      const all = item.dispatch_order_count != null ? item.dispatch_order_count : 0
      return `数量 ${qty}  派工进度 ${done}/${all}`
    },

    /**
     * 拉取任务单列表
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
        if (this.filterStatus !== '') {
          params.status = this.filterStatus
        }
        if (this.filterProduct !== '') {
          params.product = Number(this.filterProduct)
        }

        const res = await productionOrderApi.getProductionOrderList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0
          this.orderList = isLoadMore ? [...this.orderList, ...newData] : newData
          this.hasMore = this.orderList.length < this.total
          return
        }
        uni.showToast({ title: res.msg || '获取列表失败', icon: 'none' })
      } catch (error) {
        console.error('获取生产任务单列表失败:', error)
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
     * @param {Object} item - 任务单行
     */
    onOrderClick(item) {
      uni.navigateTo({
        url: `/pages/admin/work-order/production-order/detail?id=${item.id}`
      })
    },

    /**
     * 新建任务单
     */
    onCreate() {
      uni.navigateTo({
        url: '/pages/admin/work-order/production-order/edit'
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

.fab-container {
  position: fixed;
  right: 32rpx;
  bottom: calc(32rpx + env(safe-area-inset-bottom));
  z-index: 100;

  :deep(.wd-button) {
    min-width: 96rpx !important;
    max-width: 96rpx !important;
    width: 96rpx !important;
    height: 96rpx !important;
    padding: 0 !important;
    border-radius: 50% !important;
  }
}
</style>
