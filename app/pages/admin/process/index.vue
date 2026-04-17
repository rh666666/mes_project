<template>
  <view class="page">
    <!-- 搜索区域 -->
    <view class="filter-section">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索工序名称或编码"
        @search="onSearch"
        @clear="onClearSearch"
      />

      <!-- 功能入口列表 -->
      <view class="function-section">
        <wd-cell-group>
          <wd-cell title="工序技能绑定" is-link @click="onProcessSkillBind">
            <template #icon>
              <wd-icon name="link" size="20" custom-class="function-icon" />
            </template>
          </wd-cell>
        </wd-cell-group>
      </view>

      <!-- 结果统计 -->
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ processList.length }} 个工序</text>
        <wd-tag v-if="searchKeyword" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <!-- 工序列表 -->
    <scroll-view
      scroll-y
      class="process-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-cell
          v-for="(process, index) in processList"
          :key="process.id"
          :title="process.name"
          :label="process.code"
          clickable
          @click="onProcessClick(process)"
        >
          <template #value>
            <wd-icon name="arrow-right" size="16" color="#969799" />
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="processList.length === 0 && !isLoading" image="search" tip="暂无工序数据" />
    </scroll-view>

    <!-- 加载状态 -->
    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <!-- FAB 按钮 -->
    <view class="fab-container" @click="onCreateProcess">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>
  </view>
</template>

<script>
import processApi from '@/api/process.js'

/**
 * 工序管理页面（管理员专属）
 * @description 提供工序列表查看、创建、编辑和删除功能，点击跳转到独立编辑页面
 */
export default {
  data() {
    return {
      /** @type {Array} 工序列表 */
      processList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 是否正在加载更多 */
      isLoadingMore: false,
      /** @type {string} 搜索关键词 */
      searchKeyword: '',
      /** @type {number|null} 搜索防抖定时器 */
      searchDebounceTimer: null,
      /** @type {number} 当前页码 */
      currentPage: 1,
      /** @type {number} 每页数量 */
      pageSize: 10,
      /** @type {number} 总数量 */
      total: 0,
      /** @type {boolean} 是否还有更多数据 */
      hasMore: true,
      /** @type {number} 滚动位置 */
      scrollTop: 0,
      /** @type {boolean} 是否是首次加载 */
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
      if (!this.hasMore && this.processList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad() {
    this.loadProcessList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadProcessList()
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
     * 加载工序列表
     * @async
     * @param {boolean} [isLoadMore=false] - 是否是加载更多
     */
    async loadProcessList(isLoadMore = false) {
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
        if (this.searchKeyword) {
          params.name = this.searchKeyword
        }

        const res = await processApi.getProcessList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.processList = [...this.processList, ...newData]
          } else {
            this.processList = newData
          }

          this.hasMore = this.processList.length < this.total
        } else {
          uni.showToast({
            title: res.msg || '获取工序列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取工序列表失败:', error)
        uni.showToast({
          title: error.msg || '获取工序列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 刷新工序列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadProcessList(false)
    },

    /**
     * 加载更多数据
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadProcessList(true)
    },

    /**
     * 搜索处理（防抖）
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.loadProcessList()
      }, 300)
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadProcessList()
    },

    /**
     * 点击创建工序按钮 - 跳转到创建页面
     */
    onCreateProcess() {
      uni.navigateTo({
        url: '/pages/admin/process/edit'
      })
    },

    /**
     * 点击工序项 - 跳转到编辑页面
     * @param {Object} process - 工序对象
     */
    onProcessClick(process) {
      uni.navigateTo({
        url: `/pages/admin/process/edit?id=${process.id}`
      })
    },

    /**
     * 跳转到工序技能绑定页面
     */
    onProcessSkillBind() {
      uni.navigateTo({
        url: '/pages/admin/process/process-skill'
      })
    },

    /**
     * 滚动事件处理
     * @param {Object} e - 滚动事件对象
     */
    onScroll(e) {
      this.scrollTop = e.detail.scrollTop
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

.function-section {
  margin-top: 24rpx;
}

.function-icon {
  color: $uni-color-primary;
  margin-right: 16rpx;
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

.process-list {
  flex: 1;
  overflow-y: auto;
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
