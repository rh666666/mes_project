<template>
  <view class="page">
    <view class="content">
      <!-- 用户信息卡片 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-input v-model="userInfo.username" label="用户名" disabled />
        <wd-input v-model="userInfo.name" label="昵称" disabled />
        <wd-input v-model="userInfo.email" label="邮箱" disabled />
      </wd-cell-group>

      <!-- 权限设置卡片 -->
      <view class="section-header">
        <text class="section-title">权限设置</text>
      </view>
      <wd-cell-group>
        <!-- 角色选择 -->
        <wd-picker
          v-model="form.role"
          label="角色"
          placeholder="选择角色"
          :columns="roleColumns"
        />

        <!-- 部门选择 -->
        <wd-picker
          v-model="form.dept"
          label="部门"
          placeholder="选择部门"
          :columns="deptColumns"
        />
      </wd-cell-group>
    </view>

    <!-- 底部操作区 -->
    <view class="actions">
      <wd-button type="primary" size="large" :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中...' : '保存' }}
      </wd-button>
    </view>
  </view>
</template>

<script>
import authApi from '@/api/auth.js'
import deptApi from '@/api/dept.js'

/**
 * 用户编辑页面
 * @component
 * @description 提供用户权限和部门的编辑功能
 */
export default {
  name: 'UserEdit',

  data() {
    return {
      /** @type {number|null} 用户ID */
      userId: null,
      /** @type {Object} 用户信息（只读展示） */
      userInfo: {
        username: '',
        name: '',
        email: ''
      },
      /** @type {Object} 表单数据 */
      form: {
        role: 'user',
        dept: null
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {Array} 部门列表 */
      deptList: []
    }
  },

  computed: {
    /**
     * 角色选项列表
     * @returns {Array}
     */
    roleColumns() {
      return [
        { value: 'admin', label: '管理员' },
        { value: 'user', label: '普通用户' }
      ]
    },

    /**
     * 部门选项列表
     * @returns {Array}
     */
    deptColumns() {
      const columns = [{ value: '', label: '无部门' }]
      this.deptList.forEach(dept => {
        columns.push({ value: dept.id, label: dept.name })
      })
      return columns
    }
  },

  onLoad(options) {
    if (options.id) {
      this.userId = parseInt(options.id)
      const eventChannel = this.getOpenerEventChannel()
      if (eventChannel && eventChannel.on) {
        eventChannel.on('userData', (data) => {
          if (data && data.user) {
            this.initUserData(data.user)
          } else {
            this.loadUserFromList()
          }
        })
      } else {
        this.loadUserFromList()
      }
      this.loadDeptList()
    } else {
      uni.showToast({
        title: '用户ID不能为空',
        icon: 'none'
      })
      setTimeout(() => {
        uni.navigateBack()
      }, 1500)
    }
  },

  methods: {
    /**
     * 初始化用户数据
     * @param {Object} user - 用户数据
     */
    initUserData(user) {
      this.userInfo = {
        username: user.username || '',
        name: user.name || '',
        email: user.email || ''
      }
      this.form = {
        role: user.role || 'user',
        dept: user.dept || ''
      }
    },

    /**
     * 从用户列表中加载用户信息
     * @async
     */
    async loadUserFromList() {
      uni.showLoading({ title: '加载中...' })
      try {
        const res = await authApi.getUserList({ page: 1, limit: 1000 })
        if (res.code === 2000) {
          const user = res.data.find(u => u.id === this.userId)
          if (user) {
            this.initUserData(user)
          } else {
            uni.showToast({
              title: '未找到用户信息',
              icon: 'none'
            })
          }
        } else {
          uni.showToast({
            title: res.msg || '获取用户信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        uni.showToast({
          title: error.msg || '获取用户信息失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
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
     * 保存用户
     * @async
     */
    async onSave() {
      this.isSaving = true

      try {
        const res = await authApi.adminUpdateUser(this.userId, {
          role: this.form.role,
          dept: this.form.dept || null
        })

        if (res.code === 2000) {
          uni.showToast({
            title: '保存成功',
            icon: 'success'
          })
          uni.navigateBack()
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
        this.isSaving = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: $uni-bg-color;
  box-sizing: border-box;
}

.content {
  flex: 1;
  padding: 24rpx;
}

.section-header {
  margin: 32rpx 0 24rpx;
}

.section-title {
  font-size: 26rpx;
  font-weight: 400;
  color: $uni-text-color-grey;
}

.actions {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-top: 1px solid $uni-border-color;

  :deep(.wd-button) {
    width: 100%;
  }
}
</style>
