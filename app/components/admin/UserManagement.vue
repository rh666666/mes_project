<template>
  <view class="user-management">
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
              <MdIcon type="arrowright" :size="36" color="#8E8E93" />
            </template>
          </ListItem>
        </template>
      </List>

      <!-- 空状态 -->
      <view v-if="userList.length === 0 && !isLoading" class="empty-state">
        <MdIcon type="person" :size="120" color="#C7C7CC" />
        <text class="empty-text">暂无用户数据</text>
      </view>
    </scroll-view>

    <!-- 编辑用户弹窗 -->
    <Dialog
      :visible="editDialogVisible"
      type="alert"
      @confirm="onSaveUser"
      @cancel="onCancelEdit"
    >
      <!-- headline slot: 标题 -->
      <template #headline>
        <text class="dialog-headline">编辑用户</text>
      </template>

      <!-- content slot: 表单内容 -->
      <template #content>
        <form id="edit-user-form" method="dialog" class="edit-form">
          <!-- 用户信息展示（只读） -->
          <view class="readonly-section">
            <view class="readonly-row">
              <text class="readonly-label">用户名</text>
              <text class="readonly-value">{{ editingUser?.username }}</text>
            </view>
            <view class="readonly-row">
              <text class="readonly-label">昵称</text>
              <text class="readonly-value">{{ editingUser?.name || '未设置' }}</text>
            </view>
          </view>

          <!-- 角色选择 -->
          <view class="form-field">
            <text class="field-label">角色</text>
            <view class="chip-set" role="group" aria-label="选择用户角色">
              <Chip
                type="filter"
                label="管理员"
                icon="admin_panel_settings"
                :selected="editForm.role === 'admin'"
                @click="editForm.role = 'admin'"
              />
              <Chip
                type="filter"
                label="普通用户"
                icon="person_outline"
                :selected="editForm.role === 'user'"
                @click="editForm.role = 'user'"
              />
            </view>
          </view>

          <!-- 部门ID输入 -->
          <view class="form-field">
            <text class="field-label">部门ID</text>
            <view class="input-wrapper">
              <MdIcon type="apartment" :size="36" color="#8E8E93" class="input-icon" />
              <input
                class="form-input with-icon"
                v-model="editForm.dept"
                type="number"
                placeholder="请输入部门ID"
              />
            </view>
          </view>
        </form>
      </template>

      <!-- actions slot: 操作按钮 -->
      <template #actions>
        <view class="dialog-action-btn" @click="onCancelEdit">
          <text class="dialog-action-btn-text">取消</text>
        </view>
        <view class="dialog-action-btn dialog-action-btn--confirm" @click="onSaveUser">
          <text class="dialog-action-btn-text dialog-action-btn-text--confirm">保存</text>
        </view>
      </template>
    </Dialog>

    <!-- 加载状态 -->
    <view v-if="isLoading" class="loading-overlay">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- FAB 刷新按钮 -->
    <view class="fab-container" @click="onRefresh">
      <view class="fab" :class="{ 'fab-rotating': isRefreshing }">
        <MdIcon type="refreshempty" :size="48" color="#FFFFFF" />
      </view>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'
import MdIcon from '@/components/ui/MdIcon.vue'
import List from '@/components/ui/md3/List.vue'
import ListItem from '@/components/ui/md3/ListItem.vue'
import Dialog from '@/components/ui/md3/Dialog.vue'
import Chip from '@/components/ui/md3/Chip.vue'
import { getApiBaseURL } from '@/config/index.js'

/**
 * 用户管理组件（管理员专属）
 * @component
 * @description 提供用户列表查看、角色和部门管理功能
 */
export default {
  name: 'UserManagement',

  components: {
    MdIcon,
    List,
    ListItem,
    Dialog,
    Chip
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

.dialog-headline {
  font-size: $uni-font-size-lg;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-lg;
}

/* 只读区域样式 - 简洁行内展示 */
.readonly-section {
  display: flex;
  flex-direction: column;
  padding-bottom: $uni-md-space-md;
  border-bottom: 1px solid $uni-md-divider;
  margin-bottom: $uni-md-space-md;
}

.readonly-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $uni-md-space-xs 0;
}

.readonly-label {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.readonly-value {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-primary;
  font-weight: 500;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-sm;
  margin-bottom: $uni-md-space-md;

  &:last-child {
    margin-bottom: 0;
  }
}

.field-label {
  font-size: $uni-font-size-sm;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: $uni-md-space-md;
  z-index: 1;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 $uni-md-space-md;
  background-color: $uni-md-surface;
  border: 1px solid $uni-md-border;
  border-radius: $uni-md-radius-medium;
  font-size: $uni-font-size-base;
  color: $uni-md-text-primary;
  box-sizing: border-box;
  transition: border-color $uni-md-animation-fast ease;

  &.with-icon {
    padding-left: 80rpx;
  }

  &:focus {
    border-color: $uni-md-color-primary;
    outline: none;
  }
}

.chip-set {
  display: flex;
  flex-wrap: wrap;
  gap: $uni-md-space-sm;
}

.dialog-action-btn {
  padding: $uni-md-space-sm $uni-md-space-md;
  border-radius: $uni-md-radius-small;
  transition: background-color $uni-md-animation-fast ease;

  &:active {
    background-color: rgba($uni-md-color-primary, 0.1);
  }
}

.dialog-action-btn--confirm {
  .dialog-action-btn-text--confirm {
    color: $uni-md-color-primary;
    font-weight: 500;
  }
}

.dialog-action-btn-text {
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

.fab-container {
  position: fixed;
  right: $uni-md-space-lg;
  bottom: calc($uni-md-space-lg + env(safe-area-inset-bottom));
  z-index: 100;
}

.fab {
  width: 112rpx;
  height: 112rpx;
  border-radius: $uni-md-radius-full;
  background-color: $uni-md-color-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $uni-md-shadow-md;
  transition: all $uni-md-animation-fast ease;

  &:active {
    transform: scale(0.92);
    box-shadow: $uni-md-shadow-sm;
  }

  &.fab-rotating {
    animation: fab-spin 1s linear infinite;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes fab-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
