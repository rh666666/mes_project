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
          v-model="filterProcess"
          placeholder="工序"
          :columns="processColumns"
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
          :title="item.code || `派工单 ${item.id}`"
          :label="cellLabel(item)"
          clickable
          @click="onRowClick(item)"
        >
          <template #value>
            <view class="cell-right">
              <wd-tag size="small" type="primary">{{ item.status_display || item.status }}</wd-tag>
              <wd-icon name="arrow-right" size="16" color="#969799" />
            </view>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="orderList.length === 0 && !isLoading" image="search" tip="暂无工序派工单" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import dispatchOrderApi from '@/api/dispatch-order'
import processApi from '@/api/process'
import { getStorageKey } from '@/config/index.js'
import { clampApiListLimit, fetchAllPagesWithPagedApi } from '@/utils/common.js'

/**
 * 工序派工单列表（管理员）
 * @description 分页列表、按状态与工序筛选；支持从任务单详情传入 production_order 过滤
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
      /** @type {string} 状态筛选 */
      filterStatus: '',
      /** @type {number|string} 工序筛选 */
      filterProcess: '',
      /** @type {Array<Object>} 工序选项源 */
      processPickerSource: [],
      /** @type {number|null} 生产任务单 ID 筛选（来自 URL 或逻辑） */
      filterProductionOrder: null,
      /** @type {boolean} 是否首次加载 */
      isFirstLoad: true
    }
  },

  computed: {
    /**
     * 状态筛选项（与后端 DispatchOrder.Status 对齐）
     * @returns {Array<{value:string,label:string}>}
     */
    statusColumns() {
      return [
        { value: '', label: '全部状态' },
        { value: 'pending', label: '待抢单' },
        { value: 'dispatched', label: '已派工' },
        { value: 'grabbed', label: '已抢单' },
        { value: 'in_progress', label: '生产中' },
        { value: 'paused', label: '已暂停' },
        { value: 'waiting_previous', label: '等待前置工序' },
        { value: 'cancelled', label: '已取消' },
        { value: 'completed', label: '已完成' },
        { value: 'obsolete', label: '已废弃' }
      ]
    },

    /**
     * 工序筛选项（含全部）
     * @returns {Array<{value:number|string,label:string}>}
     */
    processColumns() {
      const columns = [{ value: '', label: '全部工序' }]
      this.processPickerSource.forEach((p) => {
        columns.push({
          value: p.id,
          label: p.name ? `${p.name} (${p.code || ''})` : String(p.id)
        })
      })
      return columns
    },

    /**
     * 是否有筛选条件
     * @returns {boolean}
     */
    hasActiveFilters() {
      return (
        this.filterStatus !== '' ||
        this.filterProcess !== '' ||
        this.filterProductionOrder != null
      )
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
    this.loadProcessOptions()
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
     * 加载全部工序供筛选（分页拼接）
     * @returns {Promise<void>}
     */
    async loadProcessOptions() {
      try {
        const rows = await fetchAllPagesWithPagedApi((p) => processApi.getProcessList(p), {})
        this.processPickerSource = rows || []
      } catch (e) {
        console.error('加载工序筛选列表失败:', e)
      }
    },

    /**
     * 列表项副标题
     * @param {Object} item - 派工单行
     * @returns {string}
     */
    cellLabel(item) {
      const po = item.production_order_code || '-'
      const proc = item.process_name || '-'
      const seq = item.sequence != null ? item.sequence : '-'
      const done = item.completed_quantity != null ? item.completed_quantity : 0
      const qty = item.quantity != null ? item.quantity : '-'
      return `${po}  ${proc}  序${seq}  进度 ${done}/${qty}`
    },

    /**
     * 拉取派工单列表
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
        if (this.filterProcess !== '') {
          params.process = Number(this.filterProcess)
        }
        if (this.filterProductionOrder != null) {
          params.production_order = this.filterProductionOrder
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
        console.error('获取工序派工单列表失败:', error)
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
     * @param {Object} item - 派工单行
     */
    onRowClick(item) {
      uni.navigateTo({
        url: `/pages/admin/work-order/dispatch-order/detail?id=${item.id}`
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
