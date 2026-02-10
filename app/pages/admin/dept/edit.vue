<template>
  <view class="page">
    <view class="content">
      <!-- 部门信息 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-input
          v-model="form.code"
          label="部门编码"
          placeholder="请输入部门编码"
          :maxlength="100"
          clearable
        />
        <wd-input
          v-model="form.name"
          label="部门名称"
          placeholder="请输入部门名称"
          :maxlength="100"
          clearable
        />
        <wd-picker
          v-model="form.parent"
          label="父级部门"
          placeholder="选择父级部门"
          :columns="parentDeptColumns"
        />
      </wd-cell-group>
    </view>

    <!-- 底部操作区 -->
    <view class="actions">
      <wd-button type="primary" size="large" :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中...' : '保存' }}
      </wd-button>
      <wd-button
        v-if="!isCreating"
        type="danger"
        size="large"
        plain
        @click="onDelete"
      >
        删除部门
      </wd-button>
    </view>
  </view>
</template>

<script>
import deptApi from '@/api/dept.js'

/**
 * 部门编辑/创建页面
 * @component
 * @description 提供部门信息的编辑和创建功能
 */
export default {
  name: 'DeptEdit',

  data() {
    return {
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {number|null} 部门ID（编辑模式） */
      deptId: null,
      /** @type {Object} 表单数据 */
      form: {
        code: '',
        name: '',
        parent: ''
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {Array} 部门列表（用于选择父级部门） */
      deptList: [],
      /** @type {number} 部门当前页码 */
      deptCurrentPage: 1,
      /** @type {number} 部门每页数量 */
      deptPageSize: 100
    }
  },

  computed: {
    /**
     * 父级部门选项列表（排除当前编辑的部门）
     * @returns {Array}
     */
    parentDeptColumns() {
      const columns = [{ value: '', label: '无（顶级部门）' }]
      const availableDepts = this.isCreating
        ? this.deptList
        : this.deptList.filter(dept => dept.id !== this.deptId)
      availableDepts.forEach(dept => {
        columns.push({ value: dept.id, label: dept.name })
      })
      return columns
    }
  },

  onLoad(options) {
    this.loadDeptList()

    if (options.id) {
      this.isCreating = false
      this.deptId = parseInt(options.id)
      this.loadDeptDetail()
    } else {
      this.isCreating = true
      this.deptId = null
    }
  },

  methods: {
    /**
     * 加载部门列表
     * @async
     */
    async loadDeptList() {
      try {
        const params = {
          page: this.deptCurrentPage,
          limit: this.deptPageSize
        }
        const res = await deptApi.getDeptList(params)
        if (res.code === 2000) {
          this.deptList = res.data || []
        }
      } catch (error) {
        console.error('获取部门列表失败:', error)
      }
    },

    /**
     * 加载部门详情
     * @async
     */
    async loadDeptDetail() {
      uni.showLoading({ title: '加载中...' })
      try {
        const res = await deptApi.getDeptDetail(this.deptId)
        if (res.code === 2000) {
          const dept = res.data
          this.form = {
            code: dept.code || '',
            name: dept.name || '',
            parent: dept.parent || ''
          }
        } else {
          uni.showToast({
            title: res.msg || '获取部门信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取部门详情失败:', error)
        uni.showToast({
          title: error.msg || '获取部门信息失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    /**
     * 保存部门
     * @async
     */
    async onSave() {
      if (!this.form.code.trim()) {
        uni.showToast({
          title: '请输入部门编码',
          icon: 'none'
        })
        return
      }
      if (!this.form.name.trim()) {
        uni.showToast({
          title: '请输入部门名称',
          icon: 'none'
        })
        return
      }

      this.isSaving = true

      try {
        let res
        const data = {
          code: this.form.code.trim(),
          name: this.form.name.trim(),
          parent: this.form.parent || null
        }

        if (this.isCreating) {
          res = await deptApi.createDept(data)
        } else {
          res = await deptApi.updateDept(this.deptId, data)
        }

        if (res.code === 2000) {
          uni.showToast({
            title: this.isCreating ? '创建成功' : '保存成功',
            icon: 'success'
          })
          uni.navigateBack()
        } else {
          uni.showToast({
            title: res.msg || (this.isCreating ? '创建失败' : '保存失败'),
            icon: 'none'
          })
        }
      } catch (error) {
        console.error(this.isCreating ? '创建部门失败:' : '保存部门失败:', error)
        uni.showToast({
          title: error.msg || (this.isCreating ? '创建失败' : '保存失败'),
          icon: 'none'
        })
      } finally {
        this.isSaving = false
      }
    },

    /**
     * 显示删除确认弹窗
     */
    onDelete() {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除部门 "${this.form.name}" 吗？此操作不可恢复。`,
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: (res) => {
          if (res.confirm) {
            this.onConfirmDelete()
          }
        }
      })
    },

    /**
     * 确认删除
     * @async
     */
    async onConfirmDelete() {
      if (!this.deptId) return

      uni.showLoading({ title: '删除中...' })
      try {
        const res = await deptApi.deleteDept(this.deptId)
        if (res.code === 2000) {
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          uni.navigateBack()
        } else {
          uni.showToast({
            title: res.msg || '删除失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('删除部门失败:', error)
        uni.showToast({
          title: error.msg || '删除失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
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
  display: flex;
  flex-direction: column;
  gap: 24rpx;

  :deep(.wd-button) {
    width: 100%;
  }
}
</style>
