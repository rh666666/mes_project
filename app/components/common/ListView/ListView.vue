<template>
  <view class="list-view">
    <!-- 搜索区域 -->
    <view v-if="showSearch" class="search-section">
      <wd-search
        v-model="searchKeyword"
        :placeholder="searchPlaceholder"
        @search="debouncedSearch"
        @clear="clearSearch"
      />
    </view>

    <!-- 自定义筛选区域 -->
    <slot name="filter" />

    <!-- 统计信息 -->
    <view v-if="showStats && !loading" class="results-stats">
      <text class="stats-text">共 {{ list.length }} 条记录</text>
      <slot name="statsExtra" />
    </view>

    <!-- 列表内容 -->
    <scroll-view
      scroll-y
      class="list-container"
      :refresher-enabled="enableRefresh"
      :refresher-triggered="refreshing"
      @refresherrefresh="refresh"
      @scrolltolower="loadMore"
    >
      <slot :list="list" :loading="loading" />

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip
        v-if="list.length === 0 && !loading"
        image="search"
        :tip="emptyTip"
      />
    </scroll-view>

    <!-- 加载状态 -->
    <wd-loading v-if="loading && list.length === 0" class="loading-overlay" />

    <!-- FAB按钮 -->
    <slot name="fab" />
  </view>
</template>

<script>
/**
 * 通用列表视图组件
 * @component
 * @description 封装列表的搜索、分页、刷新、加载更多等通用逻辑
 */

export default {
  name: 'ListView',

  props: {
    /**
     * 获取数据的API函数
     * @type {Function}
     */
    fetchApi: {
      type: Function,
      required: true
    },
    /**
     * 是否显示搜索框
     * @type {boolean}
     */
    showSearch: {
      type: Boolean,
      default: true
    },
    /**
     * 搜索框占位符
     * @type {string}
     */
    searchPlaceholder: {
      type: String,
      default: '搜索'
    },
    /**
     * 是否显示统计信息
     * @type {boolean}
     */
    showStats: {
      type: Boolean,
      default: true
    },
    /**
     * 是否启用下拉刷新
     * @type {boolean}
     */
    enableRefresh: {
      type: Boolean,
      default: true
    },
    /**
     * 空数据提示文本
     * @type {string}
     */
    emptyTip: {
      type: String,
      default: '暂无数据'
    },
    /**
     * 每页数量
     * @type {number}
     */
    pageSize: {
      type: Number,
      default: 10
    },
    /**
     * 搜索防抖时间（毫秒）
     * @type {number}
     */
    debounceTime: {
      type: Number,
      default: 300
    },
    /**
     * 额外的请求参数
     * @type {Object}
     */
    extraParams: {
      type: Object,
      default: () => ({})
    }
  },

  data() {
    return {
      /** @type {Array} 列表数据 */
      list: [],
      /** @type {boolean} 是否正在加载 */
      loading: false,
      /** @type {boolean} 是否正在刷新 */
      refreshing: false,
      /** @type {boolean} 是否正在加载更多 */
      loadingMore: false,
      /** @type {number} 当前页码 */
      currentPage: 1,
      /** @type {number} 总数量 */
      total: 0,
      /** @type {string} 搜索关键词 */
      searchKeyword: '',
      /** @type {number|null} 搜索防抖定时器 */
      searchTimer: null
    }
  },

  computed: {
    /**
     * 是否还有更多数据
     * @returns {boolean}
     */
    hasMore() {
      return this.list.length < this.total
    },
    /**
     * 加载更多状态
     * @returns {string}
     */
    loadMoreState() {
      if (this.loadingMore) return 'loading'
      if (!this.hasMore && this.list.length > 0) return 'finished'
      return 'default'
    }
  },

  mounted() {
    this.fetchData()
  },

  beforeUnmount() {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer)
    }
  },

  methods: {
    /**
     * 获取数据
     * @async
     * @param {boolean} isLoadMore - 是否是加载更多
     */
    async fetchData(isLoadMore = false) {
      if (isLoadMore) {
        this.loadingMore = true
      } else {
        this.loading = true
        this.currentPage = 1
      }

      try {
        const params = {
          page: this.currentPage,
          limit: this.pageSize,
          ...this.extraParams
        }
        if (this.searchKeyword) {
          params.search = this.searchKeyword
        }

        const res = await this.fetchApi(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.list = [...this.list, ...newData]
          } else {
            this.list = newData
          }

          this.$emit('load', this.list)
        } else {
          uni.showToast({
            title: res.msg || '获取数据失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取数据失败:', error)
        uni.showToast({
          title: error.msg || '获取数据失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
        this.refreshing = false
        this.loadingMore = false
      }
    },
    /**
     * 刷新数据
     */
    refresh() {
      this.refreshing = true
      this.fetchData(false)
    },
    /**
     * 加载更多数据
     */
    loadMore() {
      if (!this.hasMore || this.loadingMore || this.loading) {
        return
      }
      this.currentPage++
      this.fetchData(true)
    },
    /**
     * 搜索（防抖）
     */
    debouncedSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer)
      }
      this.searchTimer = setTimeout(() => {
        this.fetchData(false)
      }, this.debounceTime)
    },
    /**
     * 清除搜索
     */
    clearSearch() {
      this.searchKeyword = ''
      this.fetchData(false)
    },
    /**
     * 重新加载数据
     */
    reload() {
      this.fetchData(false)
    }
  }
}
</script>

<style lang="scss" scoped>
.list-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: $uni-bg-color;
}

.search-section {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-bottom: 1px solid $uni-border-color;
}

.results-stats {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-bottom: 1px solid $uni-border-color;
}

.stats-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.list-container {
  flex: 1;
  padding: 24rpx;
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
