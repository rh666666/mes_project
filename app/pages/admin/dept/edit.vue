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
        <!-- 父级部门选择 -->
        <wd-cell
          title="父级部门"
          is-link
          value-align="left"
          title-width="33%"
          :value="selectedParentName"
          @click="onShowParentSelector"
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

    <!-- 父级部门选择弹窗 -->
    <wd-popup v-model="showParentSelector" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">选择父级部门</text>
          <wd-icon name="close" size="20" @click="showParentSelector = false" />
        </view>
        <view class="popup-body">
          <SearchableSelector
            v-model="form.parent"
            label=""
            placeholder="搜索部门名称"
            search-key="name"
            :fetch-api="fetchParentDepts"
            title-field="name"
            subtitle-field="code"
            :extra-params="parentExtraParams"
            @select="onParentSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" @click="showParentSelector = false">
            确认
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import deptApi from '@/api/dept.js'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * 部门编辑/创建页面
 * @component
 * @description 提供部门信息的编辑和创建功能
 */
export default {
  name: 'DeptEdit',

  components: {
    SearchableSelector
  },

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
      /** @type {string} 已选父级部门名称 */
      selectedParentLabel: '',
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {boolean} 是否显示父级部门选择弹窗 */
      showParentSelector: false
    }
  },

  computed: {
    /**
     * 已选父级部门显示名称
     * @returns {string}
     */
    selectedParentName() {
      if (!this.form.parent) return '无（顶级部门）'
      return this.selectedParentLabel || '已选择'
    },

    /**
     * 父级部门选择器的额外参数
     * @returns {Object}
     */
    parentExtraParams() {
      return {}
    }
  },

  onLoad(options) {
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
     * 获取父级部门列表的API包装函数
     * 排除当前编辑的部门（编辑模式）
     * @async
     * @param {Object} params - 请求参数
     * @returns {Promise}
     */
    async fetchParentDepts(params) {
      const res = await deptApi.getDeptList(params)
      if (res.code === 2000 && res.data && !this.isCreating) {
        // 编辑模式下排除当前部门
        res.data = res.data.filter(dept => dept.id !== this.deptId)
      }
      return res
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
          // 根据API定义，Dept只有parent字段（父级部门ID），需要获取父级部门名称
          if (dept.parent) {
            await this.loadParentDeptName(dept.parent)
          } else {
            this.selectedParentLabel = ''
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
     * 加载父级部门名称
     * @async
     * @param {number} parentId - 父级部门ID
     */
    async loadParentDeptName(parentId) {
      try {
        const res = await deptApi.getDeptDetail(parentId)
        if (res.code === 2000 && res.data) {
          this.selectedParentLabel = res.data.name || ''
        }
      } catch (error) {
        console.error('获取父级部门名称失败:', error)
        this.selectedParentLabel = ''
      }
    },

    /**
     * 显示父级部门选择弹窗
     */
    onShowParentSelector() {
      this.showParentSelector = true
    },

    /**
     * 父级部门选择回调
     * @param {Object} dept - 选中的部门，为null表示取消选择
     */
    onParentSelect(dept) {
      if (dept) {
        this.selectedParentLabel = dept.name || ''
      } else {
        this.selectedParentLabel = ''
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
