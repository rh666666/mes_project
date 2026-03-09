<template>
  <view class="page">
    <!-- 搜索和筛选区域 -->
    <view class="filter-section">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索技能名称或编码"
        @search="onSearch"
        @clear="onClearSearch"
      />

      <!-- 功能入口列表 -->
      <view class="function-section">
        <wd-cell-group>
          <wd-cell title="用户技能绑定" is-link @click="onUserSkillBind">
            <template #icon>
              <wd-icon name="user" size="20" custom-class="function-icon" />
            </template>
          </wd-cell>
          <wd-cell title="设备技能绑定" is-link @click="onDeviceSkillBind">
            <template #icon>
              <wd-icon name="setting" size="20" custom-class="function-icon" />
            </template>
          </wd-cell>
        </wd-cell-group>
      </view>

      <!-- 类型筛选 -->
      <view class="type-filter">
        <wd-tabs v-model="selectedType">
          <wd-tab title="全部" name="all" />
          <wd-tab
            v-for="type in typeOptions"
            :key="type.value"
            :title="type.label"
            :name="type.value"
          />
        </wd-tabs>
      </view>

      <!-- 结果统计 -->
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ skillList.length }} 个技能</text>
        <wd-tag v-if="searchKeyword || (selectedType && selectedType !== 'all')" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <!-- 技能列表 -->
    <scroll-view
      scroll-y
      class="skill-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-cell
          v-for="(skill, index) in skillList"
          :key="skill.id"
          :title="skill.name"
          :label="skill.code"
          clickable
          @click="onSkillClick(skill)"
        >
          <template #value>
            <wd-tag
              :color="getTypeColor(skill.type)"
              size="small"
              round
            >
              {{ getTypeLabel(skill.type) }}
            </wd-tag>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="skillList.length === 0 && !isLoading" image="search" tip="暂无技能数据" />
    </scroll-view>

    <!-- 加载状态 -->
    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <!-- FAB 按钮 -->
    <view class="fab-container" @click="onCreateSkill">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>
  </view>
</template>

<script>
import skillApi, { SkillType, SkillTypeLabel, SkillTypeColor } from '@/api/skill.js'

/**
 * 技能管理页面（管理员专属）
 * @description 提供技能列表查看、创建、编辑和删除功能，点击跳转到独立编辑页面
 */
export default {
  data() {
    return {
      /** @type {Array} 技能列表 */
      skillList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 是否正在加载更多 */
      isLoadingMore: false,
      /** @type {string} 搜索关键词 */
      searchKeyword: '',
      /** @type {string} 选中的类型筛选 */
      selectedType: 'all',
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
      /** @type {Array} 类型选项列表 */
      typeOptions: [
        { value: SkillType.USER, label: SkillTypeLabel[SkillType.USER] },
        { value: SkillType.DEVICE, label: SkillTypeLabel[SkillType.DEVICE] }
      ],
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
      if (!this.hasMore && this.skillList.length > 0) return 'finished'
      return 'default'
    }
  },

  watch: {
    /**
     * 监听类型筛选变化
     */
    selectedType(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.loadSkillList()
      }
    }
  },

  onLoad() {
    this.loadSkillList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadSkillList()
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
     * @param {string} type - 类型值
     * @returns {string} 颜色值
     */
    getTypeColor(type) {
      return SkillTypeColor[type] || '#969799'
    },

    /**
     * 获取类型标签
     * @param {string} type - 类型值
     * @returns {string} 类型标签
     */
    getTypeLabel(type) {
      return SkillTypeLabel[type] || type
    },

    /**
     * 加载技能列表
     * @async
     * @param {boolean} [isLoadMore=false] - 是否是加载更多
     */
    async loadSkillList(isLoadMore = false) {
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
        if (this.selectedType && this.selectedType !== 'all') {
          params.type = this.selectedType
        }

        const res = await skillApi.getSkillList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.skillList = [...this.skillList, ...newData]
          } else {
            this.skillList = newData
          }

          this.hasMore = this.skillList.length < this.total
        } else {
          uni.showToast({
            title: res.msg || '获取技能列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取技能列表失败:', error)
        uni.showToast({
          title: error.msg || '获取技能列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 刷新技能列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadSkillList(false)
    },

    /**
     * 加载更多数据
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadSkillList(true)
    },

    /**
     * 搜索处理（防抖）
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.loadSkillList()
      }, 300)
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadSkillList()
    },

    /**
     * 点击创建技能按钮 - 跳转到创建页面
     */
    onCreateSkill() {
      uni.navigateTo({
        url: '/pages/admin/skill/edit'
      })
    },

    /**
     * 点击技能项 - 跳转到编辑页面
     * @param {Object} skill - 技能对象
     */
    onSkillClick(skill) {
      uni.navigateTo({
        url: `/pages/admin/skill/edit?id=${skill.id}`
      })
    },

    /**
     * 跳转到用户技能绑定页面
     */
    onUserSkillBind() {
      uni.navigateTo({
        url: '/pages/admin/skill/user-skill'
      })
    },

    /**
     * 跳转到设备技能绑定页面
     */
    onDeviceSkillBind() {
      uni.navigateTo({
        url: '/pages/admin/skill/device-skill'
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

.type-filter {
  margin-top: 24rpx;
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

.skill-list {
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
