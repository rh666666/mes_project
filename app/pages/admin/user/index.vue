<template>
  <view class="page">
    <!-- 搜索和筛选区域 -->
    <view class="filter-section">
      <wd-search
        v-model="searchKeyword"
        placeholder="搜索用户名或昵称"
        @search="onSearch"
        @clear="onClearSearch"
      />

      <!-- 筛选器行 -->
      <view class="filter-row">
        <wd-picker
          v-model="filterRole"
          placeholder="选择角色"
          :columns="roleColumns"
          @confirm="onFilterChange"
        />
        <wd-picker
          v-model="filterDept"
          placeholder="选择部门"
          :columns="deptColumns"
          @confirm="onFilterChange"
        />
      </view>

      <!-- 结果统计 -->
      <view v-if="!isLoading" class="results-stats">
        <text class="stats-text">共 {{ userList.length }} 位用户</text>
        <wd-tag v-if="hasActiveFilters" type="primary" size="small">已筛选</wd-tag>
      </view>
    </view>

    <!-- 用户列表 -->
    <scroll-view
      scroll-y
      class="user-list"
      :refresher-enabled="scrollTop <= 10"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
      @scroll="onScroll"
    >
      <wd-cell-group>
        <wd-cell
          v-for="(user, index) in userList"
          :key="user.id"
          :title="user.name || user.username"
          :label="user.email || '@' + user.username"
          clickable
          @click="onUserClick(user)"
        >
          <template #icon>
            <wd-avatar
              v-if="user.avatar"
              :src="getFullAvatarUrl(user.avatar)"
              size="small"
              custom-class="user-avatar"
            />
            <wd-avatar v-else :text="getUserInitial(user)" size="small" custom-class="user-avatar" />
          </template>
          <template #value>
            <wd-tag :type="user.role === 'admin' ? 'primary' : 'default'" size="small">
              {{ getRoleLabel(user.role) }}
            </wd-tag>
          </template>
        </wd-cell>
      </wd-cell-group>

      <wd-loadmore :state="loadMoreState" />

      <wd-status-tip v-if="userList.length === 0 && !isLoading" image="search" tip="暂无用户数据" />
    </scroll-view>

    <!-- 加载状态 -->
    <view v-if="isLoading || isRefreshing" class="loading-overlay">
      <wd-loading />
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth'
import deptApi from '@/api/dept'
import { getFullAvatarUrl } from '@/utils/format.js'

/**
 * 用户管理页面（管理员专属）
 * @description 提供用户列表查看、角色和部门管理功能，点击跳转到独立编辑页面
 */
export default {
  data() {
    return {
      /** @type {Array} 用户列表 */
      userList: [],
      /** @type {Array} 部门列表 */
      deptList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 是否正在加载更多 */
      isLoadingMore: false,
      /** @type {string} 搜索关键词 */
      searchKeyword: '',
      /** @type {string} 角色筛选 */
      filterRole: '',
      /** @type {number|string} 部门筛选 */
      filterDept: '',
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
     * 角色筛选选项
     * @returns {Array}
     */
    roleColumns() {
      return [
        { value: '', label: '全部角色' },
        { value: 'admin', label: '管理员' },
        { value: 'user', label: '普通用户' }
      ]
    },

    /**
     * 部门筛选选项
     * @returns {Array}
     */
    deptColumns() {
      const columns = [{ value: '', label: '全部部门' }]
      this.deptList.forEach(dept => {
        columns.push({ value: dept.id, label: dept.name })
      })
      return columns
    },

    /**
     * 是否有激活的筛选条件
     * @returns {boolean}
     */
    hasActiveFilters() {
      return this.searchKeyword || this.filterRole !== '' || this.filterDept !== ''
    },

    /**
     * 加载更多状态
     * @returns {string}
     */
    loadMoreState() {
      if (this.isLoadingMore) return 'loading'
      if (!this.hasMore && this.userList.length > 0) return 'finished'
      return 'default'
    }
  },

  onLoad() {
    this.loadUserList()
    this.loadDeptList()
  },

  onShow() {
    if (!this.isFirstLoad) {
      this.loadUserList()
      this.loadDeptList()
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
     * 加载用户列表
     * @async
     * @param {boolean} [isLoadMore=false] - 是否是加载更多
     */
    async loadUserList(isLoadMore = false) {
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
          params.search = this.searchKeyword
        }
        if (this.filterRole !== '') {
          params.role = this.filterRole
        }
        if (this.filterDept !== '') {
          params.dept = this.filterDept
        }

        const res = await authApi.getUserList(params)
        if (res.code === 2000) {
          const newData = res.data || []
          this.total = res.total || 0

          if (isLoadMore) {
            this.userList = [...this.userList, ...newData]
          } else {
            this.userList = newData
          }

          this.hasMore = this.userList.length < this.total
        } else {
          uni.showToast({
            title: res.msg || '获取用户列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        uni.showToast({
          title: error.msg || '获取用户列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
        this.isLoadingMore = false
      }
    },

    /**
     * 刷新用户列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadUserList(false)
    },

    /**
     * 加载更多数据
     */
    async onLoadMore() {
      if (!this.hasMore || this.isLoadingMore || this.isLoading) {
        return
      }
      this.currentPage++
      await this.loadUserList(true)
    },

    /**
     * 搜索处理（防抖）
     */
    onSearch() {
      if (this.searchDebounceTimer) {
        clearTimeout(this.searchDebounceTimer)
      }
      this.searchDebounceTimer = setTimeout(() => {
        this.loadUserList()
      }, 300)
    },

    /**
     * 清除搜索
     */
    onClearSearch() {
      this.searchKeyword = ''
      this.loadUserList()
    },

    /**
     * 筛选条件变化处理
     */
    onFilterChange() {
      this.loadUserList()
    },

    /**
     * 加载部门列表
     * @async
     */
    async loadDeptList() {
      try {
        const res = await deptApi.getDeptList({ page: 1, limit: 100 })
        if (res.code === 2000) {
          this.deptList = res.data || []
        }
      } catch (error) {
        console.error('获取部门列表失败:', error)
      }
    },

    /**
     * 获取完整头像URL
     * @param {string} avatar - 头像路径
     * @returns {string}
     */
    getFullAvatarUrl,

    /**
     * 获取用户名字首字母
     * @param {Object} user - 用户对象
     * @returns {string}
     */
    getUserInitial(user) {
      const name = user.name || user.username || 'U'
      return name.charAt(0).toUpperCase()
    },

    /**
     * 获取角色显示标签
     * @param {string|null} role - 角色
     * @returns {string}
     */
    getRoleLabel(role) {
      return role === 'admin' ? '管理员' : '用户'
    },

    /**
     * 点击用户项 - 跳转到编辑页面
     * @param {Object} user - 用户对象
     */
    onUserClick(user) {
      uni.navigateTo({
        url: `/pages/admin/user/edit?id=${user.id}`,
        success: (res) => {
          res.eventChannel.emit('userData', { user })
        }
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

.filter-row {
  display: flex;
  gap: 24rpx;
  margin-top: 24rpx;

  /* 让 wd-picker 在一行显示，居左对齐 */
  :deep(.wd-picker) {
    flex: none;
    width: auto;
    min-width: 200rpx;
  }

  :deep(.wd-picker__label) {
    white-space: nowrap;
    flex-shrink: 0;
  }

  :deep(.wd-picker__value) {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
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

.user-list {
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

/* 用户头像样式 - 添加内边距让图片不要铺太满 */
:deep(.user-avatar) {
  padding: 4rpx;
  box-sizing: border-box;
  margin-right: 16rpx;
}

:deep(.user-avatar .wd-avatar__image) {
  object-fit: contain;
  border-radius: 50%;
}

/* 调整 cell 图标区域的间距 */
:deep(.wd-cell__icon) {
  margin-right: 8rpx;
}
</style>
