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
        <wd-cell
          title="部门"
          is-link
          value-align="left"
          title-width="33%"
          :value="selectedDeptName"
          @click="onShowDeptSelector"
        />
      </wd-cell-group>
    </view>

    <!-- 底部操作区 -->
    <view class="actions">
      <wd-button type="primary" size="large" :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中...' : '保存' }}
      </wd-button>
    </view>

    <!-- 部门选择弹窗 -->
    <wd-popup v-model="showDeptSelector" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">选择部门</text>
          <wd-icon name="close" size="20" @click="showDeptSelector = false" />
        </view>
        <view class="popup-body">
          <SearchableSelector
            v-model="form.dept"
            label=""
            placeholder="搜索部门名称"
            search-key="name"
            :fetch-api="deptApi.getDeptList"
            title-field="name"
            subtitle-field="code"
            @select="onDeptSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" @click="showDeptSelector = false">
            确认
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import authApi from '@/api/auth'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import deptApi from '@/api/dept'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * 用户编辑页面
 * @component
 * @description 提供用户权限和部门的编辑功能
 */
export default {
  name: 'UserEdit',

  components: {
    SearchableSelector
  },

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
      /** @type {string} 已选部门名称 */
      selectedDeptLabel: '',
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {boolean} 是否显示部门选择弹窗 */
      showDeptSelector: false,
      /** @type {Object} deptApi 引用 */
      deptApi: deptApi
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
     * 已选部门显示名称
     * @returns {string}
     */
    selectedDeptName() {
      if (!this.form.dept) return '无部门'
      return this.selectedDeptLabel || '已选择'
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
    async initUserData(user) {
      this.userInfo = {
        username: user.username || '',
        name: user.name || '',
        email: user.email || ''
      }
      this.form = {
        role: user.role || 'user',
        dept: user.dept || ''
      }
      // 根据API定义，UserListItem只有dept字段（部门ID），需要获取部门名称
      if (user.dept) {
        await this.loadDeptName(user.dept)
      } else {
        this.selectedDeptLabel = ''
      }
    },

    /**
     * 加载部门名称
     * @async
     * @param {number} deptId - 部门ID
     */
    async loadDeptName(deptId) {
      try {
        const res = await deptApi.getDeptDetail(deptId)
        if (res.code === 2000 && res.data) {
          this.selectedDeptLabel = res.data.name || ''
        }
      } catch (error) {
        console.error('获取部门名称失败:', error)
        this.selectedDeptLabel = ''
      }
    },

    /**
     * 从用户列表中加载用户信息
     * @async
     */
    async loadUserFromList() {
      showAppLoading({ title: '加载中...' })
      try {
        const res = await authApi.getUserList({ page: 1, limit: 100 })
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
        hideAppLoading()
      }
    },

    /**
     * 显示部门选择弹窗
     */
    onShowDeptSelector() {
      this.showDeptSelector = true
    },

    /**
     * 部门选择回调
     * @param {Object} dept - 选中的部门，为null表示取消选择
     */
    onDeptSelect(dept) {
      if (dept) {
        this.selectedDeptLabel = dept.name || ''
      } else {
        this.selectedDeptLabel = ''
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
</style>
