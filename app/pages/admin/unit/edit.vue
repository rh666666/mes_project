<template>
  <view class="page">
    <view class="content">
      <!-- 单位信息 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-input
          v-model="form.code"
          label="单位编码"
          placeholder="请输入单位编码"
          :maxlength="100"
          clearable
        />
        <wd-input
          v-model="form.name"
          label="单位名称"
          placeholder="请输入单位名称"
          :maxlength="100"
          clearable
        />
        <wd-input
          v-model="form.description"
          label="单位描述"
          placeholder="请输入单位描述（可选）"
          :maxlength="200"
          clearable
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
        删除单位
      </wd-button>
    </view>
  </view>
</template>

<script>
import unitApi from '@/api/unit'

/**
 * 单位编辑/创建页面
 * @component
 * @description 提供单位信息的编辑和创建功能
 */
export default {
  name: 'UnitEdit',

  data() {
    return {
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {number|null} 单位ID（编辑模式） */
      unitId: null,
      /** @type {Object} 表单数据 */
      form: {
        code: '',
        name: '',
        description: ''
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false
    }
  },

  onLoad(options) {
    if (options.id) {
      this.isCreating = false
      this.unitId = parseInt(options.id)
      this.loadUnitDetail()
    } else {
      this.isCreating = true
      this.unitId = null
    }
  },

  methods: {
    /**
     * 加载单位详情
     * @async
     */
    async loadUnitDetail() {
      uni.showLoading({ title: '加载中...' })
      try {
        const res = await unitApi.getUnitDetail(this.unitId)
        if (res.code === 2000) {
          const unit = res.data
          this.form = {
            code: unit.code || '',
            name: unit.name || '',
            description: unit.description || ''
          }
        } else {
          uni.showToast({
            title: res.msg || '获取单位信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取单位详情失败:', error)
        uni.showToast({
          title: error.msg || '获取单位信息失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    /**
     * 保存单位
     * @async
     */
    async onSave() {
      if (!this.form.code.trim()) {
        uni.showToast({
          title: '请输入单位编码',
          icon: 'none'
        })
        return
      }
      if (!this.form.name.trim()) {
        uni.showToast({
          title: '请输入单位名称',
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
          description: this.form.description.trim() || undefined
        }

        if (this.isCreating) {
          res = await unitApi.createUnit(data)
        } else {
          res = await unitApi.updateUnit(this.unitId, data)
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
        console.error(this.isCreating ? '创建单位失败:' : '保存单位失败:', error)
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
        content: `确定要删除单位 "${this.form.name}" 吗？此操作不可恢复。`,
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
      if (!this.unitId) return

      uni.showLoading({ title: '删除中...' })
      try {
        const res = await unitApi.deleteUnit(this.unitId)
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
        console.error('删除单位失败:', error)
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
