<template>
  <view class="page">
    <view class="filter-section">
      <wd-search
        v-model="versionKeyword"
        placeholder="按版本筛选"
        @search="onSearch"
        @clear="onClearSearch"
      />
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ bomList.length }} 条 BOM</text>
        <wd-tag v-if="versionKeyword" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <scroll-view
      scroll-y
      class="bom-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-cell
          v-for="item in bomList"
          :key="item.id"
          :title="item.material_name || item.material_code || `BOM ${item.id}`"
          :label="`版本: ${item.version || '-'}  明细数: ${item.details_count || 0}`"
          clickable
          @click="onBomClick(item)"
        >
          <template #value>
            <view class="cell-actions">
              <wd-button size="small" type="danger" plain @click.stop="onDelete(item)">删除</wd-button>
              <wd-icon name="arrow-right" size="16" color="#969799" />
            </view>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="bomList.length === 0 && !isLoading" image="search" tip="暂无 BOM 数据" />
    </scroll-view>

    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <view class="fab-container" @click="onCreateBom">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>
  </view>
</template>

<script>
import bomApi from '@/api/bom'

/**
 * BOM 管理列表页面
 * @description 提供 BOM 的列表展示、分页刷新、创建入口、删除和详情编辑入口
 */
export default {
  data() {
    return {
      /** @type {Array} BOM 列表 */
      bomList: [],
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
      /** @type {string} 版本筛选关键词 */
      versionKeyword: '',
      /** @type {number|null} 搜索防抖定时器 */
      searchDebounceTimer: null,
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
      if (!this.hasMore && this.bomList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad() {
    this.loadBomList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadBomList()
    }
    this.isFirstLoad = false
  },

  onUnload() {
    if (this.searchDebounceTimer) {
      clearTimeout(this.searchDebounceTimer)
    }
  },

  methods: {
    /**
     * 加载 BOM 列表
     * @param {boolean} [isLoadMore=false] - 是否加载更多
     * @returns {Promise<void>}
     */
    async loadBomList(isLoadMore = false) {
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
          limit: this.pageSize
        }
        if (this.versionKeyword.trim()) {
          params.version = this.versionKeyword.trim()
        }

        const res = await bomApi.getBomList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0
          this.bomList = isLoadMore ? [...this.bomList, ...newData] : newData
          this.hasMore = this.bomList.length < this.total
          return
        }

        uni.showToast({ title: res.msg || '获取 BOM 列表失败', icon: 'none' })
      } catch (error) {
        console.error('获取 BOM 列表失败:', error)
        uni.showToast({ title: error.msg || '获取 BOM 列表失败', icon: 'none' })
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
      this.loadBomList(false)
    },

    /**
     * 加载更多
     * @returns {Promise<void>}
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadBomList(true)
    },

    /**
     * 搜索
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.loadBomList()
      }, 300)
    },

    /**
     * 清空搜索
     */
    onClearSearch() {
      this.versionKeyword = ''
      this.loadBomList()
    },

    /**
     * 滚动事件
     * @param {Object} e - 滚动事件
     */
    onScroll(e) {
      this.scrollTop = e.detail.scrollTop
    },

    /**
     * 跳转创建页面
     */
    onCreateBom() {
      uni.navigateTo({ url: '/pages/admin/bom/edit' })
    },

    /**
     * 点击 BOM 项
     * @param {Object} item - BOM 项
     */
    onBomClick(item) {
      uni.navigateTo({
        url: `/pages/admin/bom/detail-editor?id=${item.id}`
      })
    },

    /**
     * 删除 BOM
     * @param {Object} item - BOM 项
     */
    onDelete(item) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除 BOM "${item.material_name || item.material_code || item.id}" 吗？`,
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: async (res) => {
          if (!res.confirm) {
            return
          }
          uni.showLoading({ title: '删除中...' })
          try {
            const result = await bomApi.deleteBom(item.id)
            if (result.code === 2000) {
              uni.showToast({ title: '删除成功', icon: 'success' })
              this.loadBomList()
            } else {
              uni.showToast({ title: result.msg || '删除失败', icon: 'none' })
            }
          } catch (error) {
            console.error('删除 BOM 失败:', error)
            uni.showToast({ title: error.msg || '删除失败', icon: 'none' })
          } finally {
            uni.hideLoading()
          }
        }
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

.bom-list {
  flex: 1;
  overflow-y: auto;
}

.cell-actions {
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
