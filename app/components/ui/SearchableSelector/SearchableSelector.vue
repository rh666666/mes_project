<template>
  <view class="searchable-selector">
    <text v-if="label" class="selector-label">
      {{ label }}
      <text v-if="required" class="required">*</text>
    </text>
    <wd-search
      v-model="searchKeyword"
      :placeholder="placeholder"
      size="small"
      @search="onSearch"
      @clear="onClearSearch"
    />
    <scroll-view
      scroll-y
      class="selector-list"
      @scrolltolower="onLoadMore"
    >
      <wd-cell-group>
        <wd-cell
          v-for="item in list"
          :key="item.id"
          :title="getTitle(item)"
          :label="getSubtitle(item)"
          clickable
          value-align="left"
          :custom-class="isSelected(item) ? 'selected-cell' : ''"
          @click="onSelect(item)"
        >
          <template #value>
            <wd-icon v-if="isSelected(item)" name="check" color="#1989fa" />
          </template>
        </wd-cell>
      </wd-cell-group>
      <wd-loadmore :state="loadMoreState" />
    </scroll-view>
  </view>
</template>

<script>
/**
 * 可搜索分页选择器组件
 * @component
 * @description 支持搜索、分页加载的选择器组件
 */
export default {
  name: 'SearchableSelector',

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
     * 当前选中的值
     * @type {Number|String}
     */
    modelValue: {
      type: [Number, String],
      default: null
    },
    /**
     * 选择器标签文本
     * @type {String}
     */
    label: {
      type: String,
      default: ''
    },
    /**
     * 搜索框占位符
     * @type {String}
     */
    placeholder: {
      type: String,
      default: '搜索'
    },
    /**
     * 搜索参数名
     * @type {String}
     */
    searchKey: {
      type: String,
      default: 'search'
    },
    /**
     * 每页数量
     * @type {Number}
     */
    pageSize: {
      type: Number,
      default: 20
    },
    /**
     * 列表项标题字段
     * @type {String}
     */
    titleField: {
      type: String,
      default: 'name'
    },
    /**
     * 列表项副标题字段
     * @type {String}
     */
    subtitleField: {
      type: String,
      default: ''
    },
    /**
     * 额外的请求参数
     * @type {Object}
     */
    extraParams: {
      type: Object,
      default: () => ({})
    },
    /**
     * 是否必填
     * @type {Boolean}
     */
    required: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      /** @type {Array} 列表数据 */
      list: [],
      /** @type {String} 搜索关键词 */
      searchKeyword: '',
      /** @type {Number} 当前页码 */
      currentPage: 1,
      /** @type {Number} 总数量 */
      total: 0,
      /** @type {Boolean} 是否正在加载 */
      loading: false,
      /** @type {Boolean} 是否还有更多数据 */
      hasMore: true
    }
  },

  computed: {
    /**
     * 加载更多状态
     * @returns {String}
     */
    loadMoreState() {
      if (this.loading) return 'loading'
      if (!this.hasMore && this.list.length > 0) return 'finished'
      return 'default'
    }
  },

  mounted() {
    this.loadData()
  },

  methods: {
    /**
     * 加载数据
     * @async
     * @param {Boolean} isLoadMore - 是否是加载更多
     */
    async loadData(isLoadMore = false) {
      if (this.loading) return

      if (isLoadMore) {
        if (!this.hasMore) return
        this.currentPage++
      } else {
        this.currentPage = 1
        this.hasMore = true
        this.list = []
      }

      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          limit: this.pageSize,
          ...this.extraParams
        }
        if (this.searchKeyword) {
          params[this.searchKey] = this.searchKeyword
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

          this.hasMore = this.list.length < this.total
        }
      } catch (error) {
        console.error('获取数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * 搜索
     */
    onSearch() {
      this.loadData(false)
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadData(false)
    },

    /**
     * 加载更多
     */
    onLoadMore() {
      this.loadData(true)
    },

    /**
     * 选择项，再次点击已选中项则取消选择
     * @param {Object} item - 选中的项
     */
    onSelect(item) {
      if (this.modelValue === item.id) {
        // 再次点击已选中项，取消选择
        this.$emit('update:modelValue', null)
        this.$emit('select', null)
        this.$emit('change', null)
      } else {
        this.$emit('update:modelValue', item.id)
        this.$emit('select', item)
        this.$emit('change', item.id)
      }
    },

    /**
     * 判断是否选中
     * @param {Object} item - 列表项
     * @returns {Boolean}
     */
    isSelected(item) {
      return this.modelValue === item.id
    },

    /**
     * 获取标题
     * @param {Object} item - 列表项
     * @returns {String}
     */
    getTitle(item) {
      return item[this.titleField] || ''
    },

    /**
     * 获取副标题
     * @param {Object} item - 列表项
     * @returns {String}
     */
    getSubtitle(item) {
      if (!this.subtitleField) return ''
      return item[this.subtitleField] || ''
    },

    /**
     * 重新加载数据
     */
    reload() {
      this.loadData(false)
    }
  }
}
</script>

<style lang="scss" scoped>
.searchable-selector {
  margin-bottom: 32rpx;
}

.selector-label {
  display: block;
  font-size: 28rpx;
  color: $uni-text-color;
  margin-bottom: 16rpx;

  .required {
    color: #ee0a24;
  }
}

.selector-list {
  max-height: 300rpx;
  margin-top: 16rpx;
  border: 1px solid $uni-border-color;
  border-radius: 8rpx;
}

:deep(.selected-cell) {
  background-color: rgba(25, 137, 250, 0.08);

  .wd-cell__title {
    color: #1989fa;
    font-weight: 500;
  }
}
</style>
