<template>
  <view class="page">
    <!-- 搜索区域 -->
    <view class="filter-section">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索物料名称或编码"
        @search="onSearch"
        @clear="onClearSearch"
      />

      <!-- 结果统计 -->
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ materialList.length }} 个物料</text>
        <wd-tag v-if="searchKeyword" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <!-- 物料列表 -->
    <scroll-view
      scroll-y
      class="material-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-cell
          v-for="(material, index) in materialList"
          :key="material.id"
          :title="material.name"
          :label="material.code"
          clickable
          @click="onMaterialClick(material)"
        >
          <template #value>
            <view class="value-container">
              <wd-tag
                :color="getTypeColor(material.is_production)"
                size="small"
                round
              >
                {{ getTypeLabel(material.is_production) }}
              </wd-tag>
              <text v-if="material.unit_name" class="unit-text">{{ material.unit_name }}</text>
            </view>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="materialList.length === 0 && !isLoading" image="search" tip="暂无物料数据" />
    </scroll-view>

    <!-- 加载状态 -->
    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <!-- FAB 按钮 -->
    <view class="fab-container" @click="onCreateMaterial">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>
  </view>
</template>

<script>
import materialApi, { MaterialTypeLabel, MaterialTypeColor } from '@/api/material.js'

/**
 * 物料管理页面（管理员专属）
 * @description 提供物料列表查看、创建、编辑和删除功能，点击跳转到独立编辑页面
 */
export default {
  data() {
    return {
      /** @type {Array} 物料列表 */
      materialList: [],
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
      if (!this.hasMore && this.materialList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad() {
    this.loadMaterialList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadMaterialList()
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
     * 获取类型颜色
     * @param {boolean} isProduction - 是否为产品
     * @returns {string} 颜色值
     */
    getTypeColor(isProduction) {
      return MaterialTypeColor[isProduction] || '#969799'
    },

    /**
     * 获取类型标签
     * @param {boolean} isProduction - 是否为产品
     * @returns {string} 类型标签
     */
    getTypeLabel(isProduction) {
      return MaterialTypeLabel[isProduction] || '原材料'
    },

    /**
     * 加载物料列表
     * @async
     * @param {boolean} [isLoadMore=false] - 是否是加载更多
     */
    async loadMaterialList(isLoadMore = false) {
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

        const res = await materialApi.getMaterialList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.materialList = [...this.materialList, ...newData]
          } else {
            this.materialList = newData
          }

          this.hasMore = this.materialList.length < this.total
        } else {
          uni.showToast({
            title: res.msg || '获取物料列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取物料列表失败:', error)
        uni.showToast({
          title: error.msg || '获取物料列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 刷新物料列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadMaterialList(false)
    },

    /**
     * 加载更多数据
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadMaterialList(true)
    },

    /**
     * 搜索处理（防抖）
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.loadMaterialList()
      }, 300)
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadMaterialList()
    },

    /**
     * 点击创建物料按钮 - 跳转到创建页面
     */
    onCreateMaterial() {
      uni.navigateTo({
        url: '/pages/admin/material/edit'
      })
    },

    /**
     * 点击物料项 - 跳转到编辑页面
     * @param {Object} material - 物料对象
     */
    onMaterialClick(material) {
      uni.navigateTo({
        url: `/pages/admin/material/edit?id=${material.id}`
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

.value-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.unit-text {
  font-size: 22rpx;
  color: $uni-text-color-grey;
}

.material-list {
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
