<template>
  <view class="page">
    <!-- 搜索和筛选区域 -->
    <view class="filter-section">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索用户名称"
        @search="onSearch"
        @clear="onClearSearch"
      />

      <!-- 技能筛选 -->
      <view class="filter-row">
        <wd-picker
          v-model="filterSkill"
          placeholder="选择技能筛选"
          :columns="skillColumns"
          @confirm="onFilterChange"
        />
      </view>

      <!-- 结果统计 -->
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ userSkillList.length }} 条绑定记录</text>
        <wd-tag v-if="hasActiveFilters" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <!-- 用户技能列表 -->
    <scroll-view
      scroll-y
      class="user-skill-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-swipe-action
          v-for="(item, index) in userSkillList"
          :key="item.id"
          v-model="swipeState[item.id]"
          @click="onSwipeClick($event, item)"
        >
          <wd-cell
            :title="item.user_name"
            :label="`${item.skill_code} - ${item.skill_name}`"
            clickable
            @click="onItemClick(item)"
            @longpress="onLongPress(item)"
          />
          <template #right>
            <view class="swipe-action-delete" @click="onDelete(item)">
              <wd-icon name="delete" size="20" color="#fff" />
              <text class="delete-text">删除</text>
            </view>
          </template>
        </wd-swipe-action>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="userSkillList.length === 0 && !isLoading" image="search" tip="暂无绑定记录" />
    </scroll-view>

    <!-- 加载状态 -->
    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>

    <!-- FAB 按钮 -->
    <view class="fab-container" @click="onShowAddDialog">
      <wd-button round type="primary">
        <wd-icon name="add" size="24" color="#fff" />
      </wd-button>
    </view>

    <!-- 添加绑定弹窗 -->
    <wd-popup v-model="showAddDialog" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">添加用户技能绑定</text>
          <wd-icon name="close" size="20" @click="showAddDialog = false" />
        </view>
        <view class="popup-body">
          <!-- 用户选择 - 使用 SearchableSelector 组件 -->
          <SearchableSelector
            v-model="addForm.user"
            label="选择用户"
            placeholder="搜索用户名称"
            search-key="search"
            :fetch-api="authApi.getUserList"
            title-field="name"
            subtitle-field="username"
            :required="true"
            @select="onUserSelect"
          />

          <!-- 技能选择 - 使用 SearchableSelector 组件 -->
          <SearchableSelector
            v-model="addForm.skill"
            label="选择技能"
            placeholder="搜索技能名称"
            search-key="name"
            :fetch-api="fetchUserSkills"
            title-field="name"
            subtitle-field="code"
            :required="true"
            @select="onSkillSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" :loading="isAdding" @click="onAddBind">
            {{ isAdding ? '添加中...' : '确认添加' }}
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import skillApi from '@/api/skill'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import authApi from '@/api/auth'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * 用户技能绑定管理页面
 * @description 提供用户技能绑定列表查看、添加和删除功能
 */
export default {
  components: {
    SearchableSelector
  },

  data() {
    return {
      /** @type {Array} 用户技能列表 */
      userSkillList: [],
      /** @type {Array} 技能列表（用于筛选） */
      skillList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 是否正在加载更多 */
      isLoadingMore: false,
      /** @type {string} 搜索关键词 */
      searchKeyword: '',
      /** @type {number|string} 技能筛选 */
      filterSkill: '',
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
      isFirstLoad: true,
      /** @type {boolean} 是否显示添加弹窗 */
      showAddDialog: false,
      /** @type {boolean} 是否正在添加 */
      isAdding: false,
      /** @type {Object} 添加表单 */
      addForm: {
        user: '',
        skill: ''
      },
      /** @type {Object} authApi 引用 */
      authApi: authApi,
      /** @type {Object} 滑动操作状态 */
      swipeState: {}
    }
  },

  computed: {
    /**
     * 技能筛选选项
     * @returns {Array}
     */
    skillColumns() {
      const columns = [{ value: '', label: '全部技能' }]
      this.skillList.forEach(skill => {
        columns.push({ value: skill.id, label: `${skill.name} (${skill.code})` })
      })
      return columns
    },

    /**
     * 是否有激活的筛选条件
     * @returns {boolean}
     */
    hasActiveFilters() {
      return this.searchKeyword || this.filterSkill !== ''
    },

    /**
     * 加载更多状态
     * @returns {string}
     */
    loadMoreState() {
      if (this.isLoadingMore) return 'loading'
      if (!this.hasMore && this.userSkillList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad() {
    this.loadUserSkillList()
    this.loadSkillList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadUserSkillList()
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
     * 加载用户技能列表
     * @async
     * @param {boolean} [isLoadMore=false] - 是否是加载更多
     */
    async loadUserSkillList(isLoadMore = false) {
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
        if (this.filterSkill !== '') {
          params.skill = this.filterSkill
        }

        const res = await skillApi.getUserSkillList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.userSkillList = [...this.userSkillList, ...newData]
          } else {
            this.userSkillList = newData
          }

          this.hasMore = this.userSkillList.length < this.total
        } else {
          uni.showToast({
            title: res.msg || '获取用户技能列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取用户技能列表失败:', error)
        uni.showToast({
          title: error.msg || '获取用户技能列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 加载技能列表（用于筛选）
     * @async
     */
    async loadSkillList() {
      try {
        const res = await skillApi.getSkillList({ page: 1, limit: 100, type: 'user' })
        if (res.code === 2000) {
          this.skillList = res.data || []
        }
      } catch (error) {
        console.error('获取技能列表失败:', error)
      }
    },

    /**
     * 获取用户类型技能的API包装函数
     * @async
     * @param {Object} params - 请求参数
     * @returns {Promise}
     */
    async fetchUserSkills(params) {
      const res = await skillApi.getSkillList({ ...params, type: 'user' })
      return res
    },

    /**
     * 刷新用户技能列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadUserSkillList(false)
    },

    /**
     * 加载更多数据
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadUserSkillList(true)
    },

    /**
     * 搜索处理（防抖）
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.filterByKeyword()
      }, 300)
    },

    /**
     * 根据关键词筛选
     */
    filterByKeyword() {
      if (!this.searchKeyword) {
        this.loadUserSkillList()
        return
      }
      const keyword = this.searchKeyword.toLowerCase()
      this.userSkillList = this.userSkillList.filter(item =>
        item.user_name.toLowerCase().includes(keyword)
      )
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadUserSkillList()
    },

    /**
     * 筛选条件变化处理
     */
    onFilterChange() {
      this.loadUserSkillList()
    },

    /**
     * 显示添加弹窗
     */
    onShowAddDialog() {
      this.addForm = {
        user: '',
        skill: ''
      }
      this.showAddDialog = true
    },

    /**
     * 用户选择回调
     * @param {Object} user - 选中的用户
     */
    onUserSelect(user) {
      console.log('选中用户:', user)
    },

    /**
     * 技能选择回调
     * @param {Object} skill - 选中的技能
     */
    onSkillSelect(skill) {
      console.log('选中技能:', skill)
    },

    /**
     * 添加绑定
     * @async
     */
    async onAddBind() {
      if (!this.addForm.user) {
        uni.showToast({
          title: '请选择用户',
          icon: 'none'
        })
        return
      }
      if (!this.addForm.skill) {
        uni.showToast({
          title: '请选择技能',
          icon: 'none'
        })
        return
      }

      this.isAdding = true
      try {
        const res = await skillApi.createUserSkill({
          user: this.addForm.user,
          skill: this.addForm.skill
        })
        if (res.code === 2000) {
          uni.showToast({
            title: '添加成功',
            icon: 'success'
          })
          this.showAddDialog = false
          this.loadUserSkillList()
        } else {
          uni.showToast({
            title: res.msg || '添加失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('添加用户技能绑定失败:', error)
        uni.showToast({
          title: error.msg || '添加失败',
          icon: 'none'
        })
      } finally {
        this.isAdding = false
      }
    },

    /**
     * 删除绑定
     * @param {Object} item - 绑定记录
     */
    onDelete(item) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除用户 "${item.user_name}" 的技能 "${item.skill_name}" 绑定吗？`,
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: (res) => {
          if (res.confirm) {
            this.onConfirmDelete(item.id)
          }
        }
      })
    },

    /**
     * 确认删除
     * @async
     * @param {number} id - 绑定记录ID
     */
    async onConfirmDelete(id) {
      showAppLoading({ title: '删除中...' })
      try {
        const res = await skillApi.deleteUserSkill(id)
        if (res.code === 2000) {
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          this.loadUserSkillList()
        } else {
          uni.showToast({
            title: res.msg || '删除失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('删除用户技能绑定失败:', error)
        uni.showToast({
          title: error.msg || '删除失败',
          icon: 'none'
        })
      } finally {
        hideAppLoading()
      }
    },

    /**
     * 点击列表项
     * @param {Object} item - 绑定记录
     */
    onItemClick(item) {
      // 可以扩展为查看详情或编辑
      console.log('点击了:', item)
    },

    /**
     * 长按列表项，显示删除确认
     * @param {Object} item - 绑定记录
     */
    onLongPress(item) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除用户 "${item.user_name}" 的技能 "${item.skill_name}" 绑定吗？`,
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: (res) => {
          if (res.confirm) {
            this.onConfirmDelete(item.id)
          }
        }
      })
    },

    /**
     * 滑动操作点击
     * @param {Object} event - 点击事件
     * @param {Object} item - 绑定记录
     */
    onSwipeClick(event, item) {
      // 点击滑动区域外部时关闭滑动
      if (event.value === 'inside') {
        this.swipeState[item.id] = 'close'
      }
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

.filter-row {
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

.user-skill-list {
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

.popup-content {
  background-color: $uni-bg-color-white;
  border-radius: 24rpx 24rpx 0 0;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1px solid $uni-border-color;
  flex-shrink: 0;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.popup-body {
  padding: 32rpx;
  flex: 1;
  overflow-y: auto;
}

.popup-footer {
  padding: 24rpx 32rpx calc(24rpx + env(safe-area-inset-bottom));
  border-top: 1px solid $uni-border-color;
  flex-shrink: 0;

  :deep(.wd-button) {
    width: 100%;
  }
}

.swipe-action-delete {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 100%;
  background-color: #ee0a24;
  color: #fff;
}

.delete-text {
  font-size: 24rpx;
  margin-top: 8rpx;
}
</style>
