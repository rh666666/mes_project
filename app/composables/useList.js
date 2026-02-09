/**
 * 列表管理组合式函数
 * @module composables/useList
 * @description 封装列表的搜索、分页、刷新、加载更多等通用逻辑
 */

/**
 * 创建列表管理 mixin
 * @param {Object} options - 配置选项
 * @param {Function} options.fetchApi - 获取数据的API函数
 * @param {number} [options.pageSize=10] - 每页数量
 * @param {number} [options.debounceTime=300] - 搜索防抖时间
 * @returns {Object} mixin 对象
 */
export function createListMixin(options) {
  const { fetchApi, pageSize = 10, debounceTime = 300 } = options

  return {
    data() {
      return {
        /** @type {Array} 列表数据 */
        list: [],
        /** @type {boolean} 是否正在加载 */
        isLoading: false,
        /** @type {boolean} 是否正在刷新 */
        isRefreshing: false,
        /** @type {boolean} 是否正在加载更多 */
        isLoadingMore: false,
        /** @type {number} 当前页码 */
        currentPage: 1,
        /** @type {number} 每页数量 */
        pageSize: pageSize,
        /** @type {number} 总数量 */
        total: 0,
        /** @type {string} 搜索关键词 */
        searchKeyword: '',
        /** @type {number|null} 搜索防抖定时器 */
        searchDebounceTimer: null
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
        if (this.isLoadingMore) return 'loading'
        if (!this.hasMore && this.list.length > 0) return 'finished'
        return 'default'
      }
    },

    beforeUnmount() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
    },

    methods: {
      /**
       * 加载列表数据
       * @async
       * @param {boolean} [isLoadMore=false] - 是否是加载更多
       * @param {Object} [extraParams={}] - 额外请求参数
       */
      async loadList(isLoadMore = false, extraParams = {}) {
        if (isLoadMore) {
          this.isLoadingMore = true
        } else {
          this.isLoading = true
          this.currentPage = 1
        }

        try {
          const params = {
            page: this.currentPage,
            limit: this.pageSize,
            ...extraParams
          }
          if (this.searchKeyword) {
            params.search = this.searchKeyword
          }

          const res = await fetchApi.call(this, params)
          if (res.code === 2000) {
            const newData = res.data || []
            this.total = res.total || 0

            if (isLoadMore) {
              this.list = [...this.list, ...newData]
            } else {
              this.list = newData
            }
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
          this.isLoading = false
          this.isRefreshing = false
          this.isLoadingMore = false
        }
      },

      /**
       * 刷新列表
       * @param {Object} [extraParams={}] - 额外请求参数
       */
      refreshList(extraParams = {}) {
        this.isRefreshing = true
        this.loadList(false, extraParams)
      },

      /**
       * 加载更多数据
       * @param {Object} [extraParams={}] - 额外请求参数
       */
      loadMoreList(extraParams = {}) {
        if (!this.hasMore || this.isLoadingMore || this.isLoading) {
          return
        }
        this.currentPage++
        this.loadList(true, extraParams)
      },

      /**
       * 搜索（防抖）
       * @param {Object} [extraParams={}] - 额外请求参数
       */
      debouncedSearch(extraParams = {}) {
        if (this.searchDebounceTimer) {
          clearTimeout(this.searchDebounceTimer)
        }
        this.searchDebounceTimer = setTimeout(() => {
          this.loadList(false, extraParams)
        }, debounceTime)
      },

      /**
       * 清除搜索
       * @param {Object} [extraParams={}] - 额外请求参数
       */
      clearSearch(extraParams = {}) {
        this.searchKeyword = ''
        this.loadList(false, extraParams)
      }
    }
  }
}
