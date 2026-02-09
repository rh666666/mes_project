<template>
  <view class="page">
    <view class="content">
      <wd-form ref="form" :model="form">
        <wd-input
          v-model="form.code"
          label="设备编码"
          placeholder="请输入设备编码"
          :maxlength="100"
          clearable
        />

        <wd-input
          v-model="form.name"
          label="设备名称"
          placeholder="请输入设备名称"
          :maxlength="100"
          clearable
        />

        <wd-cell title="设备状态" :value="getStatusLabel(form.status)" />
      </wd-form>
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
        删除设备
      </wd-button>
    </view>
  </view>
</template>

<script>
import deviceApi, { DeviceStatus, DeviceStatusLabel } from '@/api/device.js'

/**
 * 设备编辑/创建页面
 * @component
 * @description 提供设备信息的编辑和创建功能
 */
export default {
  name: 'DeviceEdit',

  data() {
    return {
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {number|null} 设备ID（编辑模式） */
      deviceId: null,
      /** @type {Object} 表单数据 */
      form: {
        code: '',
        name: '',
        status: ''
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false
    }
  },

  onLoad(options) {
    if (options.id) {
      this.isCreating = false
      this.deviceId = parseInt(options.id)
      this.loadDeviceDetail()
    } else {
      this.isCreating = true
      this.deviceId = null
      this.form.status = DeviceStatus.IDLE
    }
  },

  methods: {
    /**
     * 获取状态标签
     * @param {string} status - 状态值
     * @returns {string} 状态标签
     */
    getStatusLabel(status) {
      return DeviceStatusLabel[status] || status
    },
    /**
     * 加载设备详情
     * @async
     */
    async loadDeviceDetail() {
      uni.showLoading({ title: '加载中...' })
      try {
        const res = await deviceApi.getDeviceDetail(this.deviceId)
        if (res.code === 2000) {
          const device = res.data
          this.form = {
            code: device.code || '',
            name: device.name || '',
            status: device.status || DeviceStatus.IDLE
          }
        } else {
          uni.showToast({
            title: res.msg || '获取设备信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取设备详情失败:', error)
        uni.showToast({
          title: error.msg || '获取设备信息失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    /**
     * 保存设备
     * @async
     */
    async onSave() {
      if (!this.form.code.trim()) {
        uni.showToast({
          title: '请输入设备编码',
          icon: 'none'
        })
        return
      }
      if (!this.form.name.trim()) {
        uni.showToast({
          title: '请输入设备名称',
          icon: 'none'
        })
        return
      }

      this.isSaving = true

      try {
        let res
        const data = {
          code: this.form.code.trim(),
          name: this.form.name.trim()
        }

        if (this.isCreating) {
          res = await deviceApi.createDevice(data)
        } else {
          res = await deviceApi.updateDevice(this.deviceId, data)
        }

        if (res.code === 2000) {
          uni.showToast({
            title: this.isCreating ? '创建成功' : '保存成功',
            icon: 'success'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          uni.showToast({
            title: res.msg || (this.isCreating ? '创建失败' : '保存失败'),
            icon: 'none'
          })
        }
      } catch (error) {
        console.error(this.isCreating ? '创建设备失败:' : '保存设备失败:', error)
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
        content: `确定要删除设备 "${this.form.name}" 吗？此操作不可恢复。`,
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
      if (!this.deviceId) return

      uni.showLoading({ title: '删除中...' })
      try {
        const res = await deviceApi.deleteDevice(this.deviceId)
        if (res.code === 2000) {
          uni.showToast({
            title: '删除成功',
            icon: 'success'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          uni.showToast({
            title: res.msg || '删除失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('删除设备失败:', error)
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

.actions {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-top: 1px solid $uni-border-color;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
</style>
