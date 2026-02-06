<template>
  <view class="dept-management">
    <!-- 部门列表 -->
    <scroll-view
      class="dept-list"
      scroll-y
      :refresher-enabled="true"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
    >
      <List v-if="deptList.length > 0" class="dept-md3-list">
        <template v-for="(dept, index) in deptList" :key="dept.id">
          <ListItem
            :clickable="true"
            :has-divider="index < deptList.length - 1"
            @click="onDeptClick(dept)"
          >
            <!-- headline slot: 部门名称 -->
            <template #headline>
              <text class="dept-headline">{{ dept.name }}</text>
            </template>

            <!-- supporting-text slot: 部门编码 -->
            <template #supporting-text>
              <text class="dept-supporting-text">{{ dept.code }}</text>
            </template>

            <!-- trailing-supporting-text slot: 父级部门 -->
            <template #trailing-supporting-text>
              <view v-if="dept.parent" class="parent-tag">
                <text class="parent-text">子部门</text>
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
      <view v-if="deptList.length === 0 && !isLoading" class="empty-state">
        <MdIcon type="apartment" :size="120" color="#C7C7CC" />
        <text class="empty-text">暂无部门数据</text>
      </view>
    </scroll-view>

    <!-- 编辑/创建部门弹窗 -->
    <Dialog
      :visible="editDialogVisible"
      type="alert"
      @confirm="onSaveDept"
      @cancel="onCancelEdit"
    >
      <!-- headline slot: 标题 -->
      <template #headline>
        <text class="dialog-headline">{{ isCreating ? '创建部门' : '编辑部门' }}</text>
      </template>

      <!-- content slot: 表单内容 -->
      <template #content>
        <form id="edit-dept-form" method="dialog" class="edit-form">
          <!-- 部门编码 -->
          <FormInputField
            v-model="editForm.code"
            label="部门编码"
            placeholder="请输入部门编码"
            icon="badge"
            :maxlength="100"
          />

          <!-- 部门名称 -->
          <FormInputField
            v-model="editForm.name"
            label="部门名称"
            placeholder="请输入部门名称"
            icon="apartment"
            :maxlength="100"
          />

          <!-- 父级部门选择 -->
          <FormInputField
            v-model="editForm.parent"
            type="select"
            label="父级部门"
            placeholder="请选择父级部门"
            icon="account_tree"
            :options="parentDeptOptions"
          />
        </form>
      </template>

      <!-- actions slot: 操作按钮 -->
      <template #actions>
        <view v-if="!isCreating" class="dialog-action-btn dialog-action-btn--delete" @click="onDeleteDept">
          <text class="dialog-action-btn-text dialog-action-btn-text--delete">删除</text>
        </view>
        <view class="dialog-action-btn" @click="onCancelEdit">
          <text class="dialog-action-btn-text">取消</text>
        </view>
        <view class="dialog-action-btn dialog-action-btn--confirm" @click="onSaveDept">
          <text class="dialog-action-btn-text dialog-action-btn-text--confirm">保存</text>
        </view>
      </template>
    </Dialog>

    <!-- 删除确认弹窗 -->
    <Dialog
      :visible="deleteDialogVisible"
      type="alert"
      @confirm="onConfirmDelete"
      @cancel="onCancelDelete"
    >
      <!-- headline slot: 标题 -->
      <template #headline>
        <text class="dialog-headline">确认删除</text>
      </template>

      <!-- content slot: 提示内容 -->
      <template #content>
        <text class="delete-content">
          确定要删除部门 "{{ editingDept?.name }}" 吗？此操作不可恢复。
        </text>
      </template>

      <!-- actions slot: 操作按钮 -->
      <template #actions>
        <view class="dialog-action-btn" @click="onCancelDelete">
          <text class="dialog-action-btn-text">取消</text>
        </view>
        <view class="dialog-action-btn dialog-action-btn--delete" @click="onConfirmDelete">
          <text class="dialog-action-btn-text dialog-action-btn-text--delete">删除</text>
        </view>
      </template>
    </Dialog>

    <!-- 加载状态 -->
    <view v-if="isLoading" class="loading-overlay">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- FAB 按钮组 -->
    <view class="fab-container">
      <view class="fab fab--primary" @click="onCreateDept">
        <MdIcon type="add" :size="48" color="#FFFFFF" />
      </view>
      <view class="fab fab--secondary" :class="{ 'fab-rotating': isRefreshing }" @click="onRefresh">
        <MdIcon type="refreshempty" :size="40" color="#FFFFFF" />
      </view>
    </view>
  </view>
</template>

<script>
import deptApi from '@/api/dept.js'
import MdIcon from '@/components/ui/MdIcon.vue'
import List from '@/components/ui/md3/List.vue'
import ListItem from '@/components/ui/md3/ListItem.vue'
import Dialog from '@/components/ui/md3/Dialog.vue'
import FormInputField from '@/components/ui/FormInputField.vue'

/**
 * 部门管理组件（管理员专属）
 * @component
 * @description 提供部门列表查看、创建、编辑和删除功能
 */
export default {
  name: 'DeptManagement',

  components: {
    MdIcon,
    List,
    ListItem,
    Dialog,
    FormInputField
  },

  data() {
    return {
      /** @type {Array} 部门列表 */
      deptList: [],
      /** @type {boolean} 是否正在加载 */
      isLoading: false,
      /** @type {boolean} 是否正在刷新 */
      isRefreshing: false,
      /** @type {boolean} 编辑弹窗是否可见 */
      editDialogVisible: false,
      /** @type {boolean} 删除确认弹窗是否可见 */
      deleteDialogVisible: false,
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {Object|null} 当前编辑的部门 */
      editingDept: null,
      /** @type {Object} 编辑表单数据 */
      editForm: {
        code: '',
        name: '',
        parent: null
      }
    }
  },

  computed: {
    /**
     * 父级部门选项列表（包含"无"选项，排除当前编辑的部门）
     * @returns {Array<{value: number|null, label: string}>}
     */
    parentDeptOptions() {
      const options = [{ value: null, label: '无（顶级部门）' }]
      const availableDepts = this.editingDept
        ? this.deptList.filter(dept => dept.id !== this.editingDept.id)
        : this.deptList
      availableDepts.forEach(dept => {
        options.push({ value: dept.id, label: dept.name })
      })
      return options
    }
  },

  mounted() {
    this.loadDeptList()
  },

  methods: {
    /**
     * 加载部门列表
     * @async
     * @returns {Promise<void>}
     */
    async loadDeptList() {
      this.isLoading = true
      try {
        const res = await deptApi.getDeptList()
        if (res.code === 2000) {
          this.deptList = res.data || []
        } else {
          uni.showToast({
            title: res.msg || '获取部门列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取部门列表失败:', error)
        uni.showToast({
          title: error.msg || '获取部门列表失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        this.isRefreshing = false
      }
    },

    /**
     * 刷新部门列表
     */
    onRefresh() {
      this.isRefreshing = true
      this.loadDeptList()
    },

    /**
     * 点击创建部门按钮
     */
    onCreateDept() {
      this.isCreating = true
      this.editingDept = null
      this.editForm = {
        code: '',
        name: '',
        parent: null
      }
      this.editDialogVisible = true
    },

    /**
     * 点击部门项（编辑）
     * @param {Object} dept - 部门对象
     */
    onDeptClick(dept) {
      this.isCreating = false
      this.editingDept = dept
      this.editForm = {
        code: dept.code || '',
        name: dept.name || '',
        parent: dept.parent || null
      }
      this.editDialogVisible = true
    },

    /**
     * 保存部门（创建或更新）
     * @async
     * @returns {Promise<void>}
     */
    async onSaveDept() {
      // 表单验证
      if (!this.editForm.code.trim()) {
        uni.showToast({
          title: '请输入部门编码',
          icon: 'none'
        })
        return
      }
      if (!this.editForm.name.trim()) {
        uni.showToast({
          title: '请输入部门名称',
          icon: 'none'
        })
        return
      }

      uni.showLoading({ title: '保存中...' })

      try {
        let res
        if (this.isCreating) {
          // 创建部门
          res = await deptApi.createDept({
            code: this.editForm.code.trim(),
            name: this.editForm.name.trim(),
            parent: this.editForm.parent
          })
        } else {
          // 更新部门
          res = await deptApi.updateDept(this.editingDept.id, {
            code: this.editForm.code.trim(),
            name: this.editForm.name.trim(),
            parent: this.editForm.parent
          })
        }

        if (res.code === 2000) {
          uni.showToast({
            title: this.isCreating ? '创建成功' : '保存成功',
            icon: 'success'
          })
          this.editDialogVisible = false
          // 刷新列表
          this.loadDeptList()
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
        uni.hideLoading()
      }
    },

    /**
     * 显示删除确认弹窗
     */
    onDeleteDept() {
      this.deleteDialogVisible = true
    },

    /**
     * 确认删除部门
     * @async
     * @returns {Promise<void>}
     */
    async onConfirmDelete() {
      if (!this.editingDept) return

      uni.showLoading({ title: '删除中...' })
      try {
        const result = await deptApi.deleteDept(this.editingDept.id)
        if (result.code === 2000) {
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          this.deleteDialogVisible = false
          this.editDialogVisible = false
          this.editingDept = null
          // 刷新列表
          this.loadDeptList()
        } else {
          uni.showToast({
            title: result.msg || '删除失败',
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
    },

    /**
     * 取消删除
     */
    onCancelDelete() {
      this.deleteDialogVisible = false
    },

    /**
     * 取消编辑
     */
    onCancelEdit() {
      this.editDialogVisible = false
      this.editingDept = null
    }
  }
}
</script>

<style lang="scss">
.dept-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: $uni-md-background;
}

.dept-list {
  flex: 1;
  padding: 0 $uni-md-space-md;
}

.dept-md3-list {
  margin-bottom: $uni-md-space-md;
}

.dept-headline {
  font-size: $uni-font-size-base;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.dept-supporting-text {
  font-size: $uni-font-size-sm;
  color: $uni-md-text-secondary;
}

.parent-tag {
  padding: 4rpx 12rpx;
  border-radius: $uni-md-radius-small;
  background-color: rgba($uni-md-color-primary, 0.1);
}

.parent-text {
  font-size: 20rpx;
  font-weight: 500;
  color: $uni-md-color-primary;
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
  margin-top: $uni-md-space-md;
}

.dialog-headline {
  font-size: $uni-font-size-lg;
  font-weight: 500;
  color: $uni-md-text-primary;
}

.delete-content {
  font-size: $uni-font-size-base;
  color: $uni-md-text-secondary;
  line-height: 1.5;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-lg;
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

.dialog-action-btn--delete {
  &:active {
    background-color: rgba($uni-color-error, 0.1);
  }

  .dialog-action-btn-text--delete {
    color: $uni-color-error;
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
  display: flex;
  flex-direction: column;
  gap: $uni-md-space-md;
}

.fab {
  width: 112rpx;
  height: 112rpx;
  border-radius: $uni-md-radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $uni-md-shadow-md;
  transition: all $uni-md-animation-fast ease;

  &:active {
    transform: scale(0.92);
    box-shadow: $uni-md-shadow-sm;
  }

  &--primary {
    background-color: $uni-md-color-primary;
  }

  &--secondary {
    background-color: $uni-md-color-secondary;
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