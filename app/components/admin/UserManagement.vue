<template>
  <view class="user-management">
    <!-- 标题栏 -->
    <view class="header">
      <text class="header-title">用户管理</text>
      <view class="header-actions">
        <view class="refresh-btn" @click="onRefresh">
          <UniIcons type="refreshempty" size="20" color="#1976D2" />
        </view>
      </view>
    </view>

    <!-- 统计信息 -->
    <view class="stats-section">
      <view class="stat-card">
        <text class="stat-value">{{ userList.length }}</text>
        <text class="stat-label">总用户数</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ adminCount }}</text>
        <text class="stat-label">管理员</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ userCount }}</text>
        <text class="stat-label">普通用户</text>
      </view>
    </view>

    <!-- 用户列表 -->
    <scroll-view
      class="user-list"
      scroll-y
      :refresher-enabled="true"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
    >
      <List v-if="userList.length > 0" class="user-md3-list">
        <template v-for="(user, index) in userList" :key="user.id">
          <ListItem
            :clickable="true"
            :has-divider="index < userList.length - 1"
            @click="onUserClick(user)"
          >
            <!-- start slot: 头像 -->
            <template #start>
              <image
                v-if="user.avatar"
                class="user-avatar-img"
                :src="getAvatarUrl(user.avatar)"
                mode="aspectFill"
              />
              <view v-else class="user-avatar">
                <text class="avatar-text">{{ getUserInitial(user) }}</text>
              </view>
            </template>

            <!-- headline slot: 用户名 -->
            <template #headline>
              <text class="user-headline">{{ user.name || user.username }}</text>
            </template>

            <!-- supporting-text slot: 用户邮箱/用户名 -->
            <template #supporting-text>
              <text v-if="user.email" class="user-supporting-text">{{ user.email }}</text>
              <text v-else class="user-supporting-text">@{{ user.username }}</text>
            </template>

            <!-- trailing-supporting-text slot: 角色标签 -->
            <template #trailing-supporting-text>
              <view class="role-tag" :class="getRoleClass(user.role)">
                <text class="role-text">{{ getRoleLabel(user.role) }}</text>
              </view>
            </template>

            <!-- end slot: 箭头 -->
            <template #end>
              <UniIcons type="arrowright" size="18" color="#8E8E93" />
            </template>
          </ListItem>
        </template>
      </List>

      <!-- 空状态 -->
      <view v-if="userList.length === 0 && !isLoading" class="empty-state">
        <UniIcons type="person" size="60" color="#C7C7CC" />
        <text class="empty-text">暂无用户数据</text>
      </view>
    </scroll-view>

    <!-- 编辑用户弹窗 -->
    <Dialog
      :visible="editDialogVisible"
      :title="`编辑用户 - ${editingUser?.name || editingUser?.username}`"
      confirm-text="保存"
      cancel-text="取消"
      @confirm="onSaveUser"
      @cancel="onCancelEdit"
    >
      <template #content>
        <view class="edit-form">
          <view class="form-item">
            <text class="form-label">用户名</text>
            <text class="form-value readonly">{{ editingUser?.username }}</text>
          </view>
          <view class="form-item">
            <text class="form-label">昵称</text>
            <text class="form-value readonly">{{ editingUser?.name || '未设置' }}</text>
          </view>
          <view class="form-item">
            <text class="form-label">角色</text>
            <view class="role-selector">
              <view
                class="role-option"
                :class="{ active: editForm.role === 'admin' }"
                @click="editForm.role = 'admin'"
              >
                <text class="role-option-text">管理员</text>
              </view>
              <view
                class="role-option"
                :class="{ active: editForm.role === 'user' }"
                @click="editForm.role = 'user'"
              >
                <text class="role-option-text">普通用户</text>
              </view>
            </view>
          </view>
          <view class="form-item">
            <text class="form-label">部门ID</text>
            <input
              class="form-input"
              v-model="editForm.dept"
              type="number"
              placeholder="请输入部门ID"
            />
          </view>
        </view>
      </template>
    </Dialog>

    <!-- 加载状态 -->
    <view v-if="isLoading" class="loading-overlay">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'
import UniIcons from '@dcloudio/uni-ui/lib/uni-icons/uni-icons.vue'
import List from '@/components/ui/md3/List.vue'
import ListItem from '@/components/ui/md3/ListItem.vue'
import Divider from '@/components/ui/md3/Divider.vue'
import Dialog from '@/components/ui/md3/Dialog.vue'
import { getApiBaseURL } from '@/config/index.js'

/**
 * 用户管理组件（管理员专属）
 * @component
 * @description 提供用户列表查看、角色和部门管理功能
 */
export default {
  name: 'UserManagement',

  components: {
    UniIcons,
    List,
    ListItem,
    Divider,
    Dialog
  },

  data() {
    return {
      /** @type {Array} 用户列表 */
      userList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 编辑弹窗是否可见 */
      editDialogVisible: false,
      /** @type {Object|null} 当前编辑的用户 */
      editingUser: null,
      /** @type {Object} 编辑表单数据 */
      editForm: {
        role: 'user',
        dept: null
      }
    }
  },

  computed: {
    /**
     * 管理员数量
     * @returns {number}
     */
    adminCount() {
      return this.userList.filter(user => user.role === 'admin').length
    },

    /**
     * 普通用户数量
     * @returns {number}
     */
    userCount() {
      return this.userList.filter(user => user.role === 'user' || !user.role).length
    }
  },

  mounted() {
    this.loadUserList()
  },

  methods: {
    /**
     * 加载用户列表
     * @async
     * @returns {Promise<void>}
     */
    async loadUserList() {
      this.isLoading = true
      try {
        const res = await authApi.getUserList()
        if (res.code === 2000) {
          this.userList = res.data || []
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
      }
    },

    /**
     * 刷新用户列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.loadUserList()
    },

    /**
     * 获取头像URL
     * @param {string} avatar - 头像路径
     * @returns {string}
     */
    getAvatarUrl(avatar) {
      if (!avatar) return ''
      if (avatar.startsWith('http')) return avatar
      return getApiBaseURL() + avatar
    },

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
     * 获取角色标签样式类
     * @param {string|null} role - 角色
     * @returns {string}
     */
    getRoleClass(role) {
      return role === 'admin' ? 'role-admin' : 'role-user'
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
     * 点击用户项
     * @param {Object} user - 用户对象
     */
    onUserClick(user) {
      this.editingUser = user
      this.editForm = {
        role: user.role || 'user',
        dept: user.dept || null
      }
      this.editDialogVisible = true
    },

    /**
     * 保存用户修改
     * @async
     * @returns {Promise<void>}
     */
    async onSaveUser() {
      if (!this.editingUser) return

      uni.showLoading({ title: '保存中...' })

      try {
        const res = await authApi.adminUpdateUser(this.editingUser.id, {
          role: this.editForm.role,
          dept: this.editForm.dept ? parseInt(this.editForm.dept) : null
        })

        if (res.code === 2000) {
          uni.showToast({
            title: '保存成功',
            icon: 'success'
          })
          this.editDialogVisible = false
          // 更新本地数据
          const index = this.userList.findIndex(u => u.id === this.editingUser.id)
          if (index !== -1) {
            this.userList[index] = { ...this.userList[index], ...res.data }
          }
        } else {
          uni.showToast({
            title: res.msg || '保存失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('保存用户失败:', error)
        uni.showToast({
          title: error.msg || '保存失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    /**
     * 取消编辑
     */
    onCancelEdit() {
      this.editDialogVisible = false
      this.editingUser = null
    }
  }
}
</script>

<style lang="scss">
.user-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: $uni-md-background;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $uni-md-space-md $uni-md-space-lg;
  background-color: $uni-md-surface;
  border-bottom: 1px solid $uni-md-divider;
}

.header-title {
  font-size: $uni-font-size-lg;
  font-weight: 600;
  color: $uni-md-text-primary;
}

.header-actions {
  display: flex;
  align-items: center;
}

.refresh-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $uni-md-radius-medium;
  transition: background-color $uni-md-animation-fast ease;

  &:active {
    background-color: $uni-md-surface-variant;
  }
}



.stats-section {
  display: flex;
  padding: $uni-md-space-md;
  gap: $uni-md-space-md;
  background-color: $uni-md-surface;
  margin-bottom: $uni-md-space-md;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $uni-md-space-md;
  background-color: $uni-md-surface-variant;
  border-radius: $uni-md-radius-medium;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 700;
  color: $uni-md-color-primary;
  margin-bottom: $uni-md-space-xs;
}

.stat-label {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.user-list {
  flex: 1;
  padding: 0 $uni-md-space-md;
}

.user-md3-list {
  margin-bottom: $uni-md-space-md;
}

.user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background-color: $uni-md-color-primary;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar-img {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background-color: $uni-md-surface;
}

.avatar-text {
  font-size: $uni-font-size-lg;
  color: white;
  font-weight: 500;
}

.user-headline {
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.user-supporting-text {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.role-tag {
  padding: 4rpx 12rpx;
  border-radius: $uni-md-radius-small;

  &.role-admin {
    background-color: rgba($uni-md-color-primary, 0.1);

    .role-text {
      color: $uni-md-color-primary;
    }
  }

  &.role-user {
    background-color: rgba($uni-md-text-tertiary, 0.1);

    .role-text {
      color: $uni-md-text-tertiary;
    }
  }
}

.role-text {
  font-size: 20rpx;
  font-weight: 500;
}



.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $uni-md-space-2xl;
}



.empty-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
}

.edit-form {
  padding: $uni-md-space-md 0;
}

.form-item {
  display: flex;
  align-items: center;
  margin-bottom: $uni-md-space-md;

  &:last-child {
    margin-bottom: 0;
  }
}

.form-label {
  width: 140rpx;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  font-weight: 500;
}

.form-value {
  flex: 1;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;

  &.readonly {
    color: $uni-md-text-secondary;
  }
}

.form-input {
  flex: 1;
  height: 72rpx;
  padding: 0 $uni-md-space-md;
  background-color: $uni-md-surface-variant;
  border-radius: $uni-md-radius-small;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
}

.role-selector {
  flex: 1;
  display: flex;
  gap: $uni-md-space-md;
}

.role-option {
  flex: 1;
  padding: $uni-md-space-sm $uni-md-space-md;
  background-color: $uni-md-surface-variant;
  border-radius: $uni-md-radius-small;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $uni-md-animation-fast ease;

  &.active {
    background-color: $uni-md-color-primary;

    .role-option-text {
      color: white;
    }
  }
}

.role-option-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid rgba($uni-md-color-primary, 0.2);
  border-top: 4rpx solid $uni-md-color-primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: $uni-md-space-md;
}

.loading-text {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
