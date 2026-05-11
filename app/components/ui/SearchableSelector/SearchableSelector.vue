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
          <template #icon>
            <view v-if="showAvatar" class="selector-cell-icon">
              <wd-img
                v-if="getAvatarSrc(item)"
                :src="getAvatarSrc(item)"
                :width="avatarImgSize"
                :height="avatarImgSize"
                round
                mode="aspectFill"
                :lazy-load="avatarLazyLoad"
              />
              <wd-avatar
                v-else
                :text="getAvatarLetter(item)"
                :size="avatarWdSize"
              />
            </view>
          </template>
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
import { getFullAvatarUrl, getUserInitial } from '@/utils/format.js'

/**
 * 可搜索分页选择器组件
 * @component
 * @description 支持搜索、分页加载的选择器组件；可选列表头像（wd-img 懒加载）
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
    },
    /**
     * 是否在左侧展示头像（适用于用户等含 avatar 字段的数据）
     * @type {Boolean}
     */
    showAvatar: {
      type: Boolean,
      default: false
    },
    /**
     * 头像地址字段名（相对路径时会拼接 API 根地址）
     * @type {String}
     */
    avatarField: {
      type: String,
      default: 'avatar'
    },
    /**
     * 头像图片是否懒加载（scroll-view 内建议使用）
     * @type {Boolean}
     */
    avatarLazyLoad: {
      type: Boolean,
      default: true
    },
    /**
     * 头像 wd-img 宽高（px，与 wd-avatar small 接近）
     * @type {Number}
     */
    avatarImgSize: {
      type: Number,
      default: 48
    },
    /**
     * 无头像占位时 wd-avatar 尺寸预设
     * @type {String}
     */
    avatarWdSize: {
      type: String,
      default: 'small'
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
     * 头像完整 URL（无头像时返回空字符串，用于展示文字占位）
     * @param {Object} item - 列表项
     * @returns {string}
     */
    getAvatarSrc(item) {
      if (!this.showAvatar || !item) return ''
      const raw = item[this.avatarField]
      return raw ? getFullAvatarUrl(raw) : ''
    },

    /**
     * 无头像时的占位字母
     * @param {Object} item - 列表项
     * @returns {string}
     */
    getAvatarLetter(item) {
      const name =
        this.getTitle(item) ||
        (this.subtitleField ? item[this.subtitleField] : '') ||
        ''
      return getUserInitial(String(name))
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

.selector-cell-icon {
  display: flex;
  align-items: center;
  margin-right: 8rpx;
}
</style>
