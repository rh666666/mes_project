<template>
  <view class="form-view">
    <view class="form-content">
      <wd-form ref="formRef" :model="formData">
        <slot :form="formData" />
      </wd-form>
    </view>

    <view class="form-actions">
      <wd-button
        type="primary"
        size="large"
        :loading="saving"
        @click="handleSave"
      >
        {{ saving ? '保存中...' : '保存' }}
      </wd-button>

      <wd-button
        v-if="!isCreating && showDelete"
        type="danger"
        size="large"
        plain
        @click="handleDelete"
      >
        {{ deleteText }}
      </wd-button>
    </view>
  </view>
</template>

<script>
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'

/**
 * 通用表单视图组件
 * @component
 * @description 封装表单的保存、删除等通用逻辑
 */

export default {
  name: 'FormView',

  props: {
    /**
     * 是否是创建模式
     * @type {boolean}
     */
    isCreating: {
      type: Boolean,
      default: false
    },
    /**
     * 是否显示删除按钮
     * @type {boolean}
     */
    showDelete: {
      type: Boolean,
      default: true
    },
    /**
     * 删除按钮文本
     * @type {string}
     */
    deleteText: {
      type: String,
      default: '删除'
    },
    /**
     * 创建API函数
     * @type {Function}
     */
    createApi: {
      type: Function,
      default: null
    },
    /**
     * 更新API函数
     * @type {Function}
     */
    updateApi: {
      type: Function,
      default: null
    },
    /**
     * 删除API函数
     * @type {Function}
     */
    deleteApi: {
      type: Function,
      default: null
    },
    /**
     * 表单验证规则
     * @type {Object}
     */
    rules: {
      type: Object,
      default: () => ({})
    },
    /**
     * 初始表单数据
     * @type {Object}
     */
    initialData: {
      type: Object,
      default: () => ({})
    },
    /**
     * 保存成功提示文本
     * @type {string}
     */
    saveSuccessText: {
      type: String,
      default: '保存成功'
    },
    /**
     * 创建成功提示文本
     * @type {string}
     */
    createSuccessText: {
      type: String,
      default: '创建成功'
    },
    /**
     * 删除成功提示文本
     * @type {string}
     */
    deleteSuccessText: {
      type: String,
      default: '删除成功'
    }
  },

  data() {
    return {
      /** @type {Object} 表单数据 */
      formData: {},
      /** @type {boolean} 是否正在保存 */
      saving: false
    }
  },

  watch: {
    initialData: {
      immediate: true,
      handler(val) {
        this.formData = { ...val }
      }
    }
  },

  methods: {
    /**
     * 处理保存
     * @async
     */
    async handleSave() {
      const valid = await this.$refs.formRef.validate()
      if (!valid) return

      this.saving = true
      try {
        const api = this.isCreating ? this.createApi : this.updateApi
        if (!api) {
          uni.showToast({
            title: '未配置API',
            icon: 'none'
          })
          return
        }

        const res = await api(this.formData)

        if (res.code === 2000) {
          uni.showToast({
            title: this.isCreating ? this.createSuccessText : this.saveSuccessText,
            icon: 'success'
          })
          this.$emit('save', res.data)
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
        console.error(this.isCreating ? '创建失败:' : '保存失败:', error)
        uni.showToast({
          title: error.msg || (this.isCreating ? '创建失败' : '保存失败'),
          icon: 'none'
        })
      } finally {
        this.saving = false
      }
    },
    /**
     * 处理删除
     */
    handleDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除吗？此操作不可恢复。',
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: async (res) => {
          if (res.confirm) {
            await this.confirmDelete()
          }
        }
      })
    },
    /**
     * 确认删除
     * @async
     */
    async confirmDelete() {
      if (!this.deleteApi) {
        uni.showToast({
          title: '未配置删除API',
          icon: 'none'
        })
        return
      }

      showAppLoading({ title: '删除中...' })
      try {
        const result = await this.deleteApi()
        if (result.code === 2000) {
          uni.showToast({
            title: this.deleteSuccessText,
            icon: 'success'
          })
          this.$emit('delete')
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          uni.showToast({
            title: result.msg || '删除失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('删除失败:', error)
        uni.showToast({
          title: error.msg || '删除失败',
          icon: 'none'
        })
      } finally {
        hideAppLoading()
      }
    },
    /**
     * 重置表单
     */
    resetForm() {
      this.formData = { ...this.initialData }
      this.$refs.formRef.reset()
    },
    /**
     * 设置表单数据
     * @param {Object} data - 表单数据
     */
    setFormData(data) {
      this.formData = { ...data }
    }
  }
}
</script>

<style lang="scss" scoped>
.form-view {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.form-content {
  flex: 1;
  padding: 24rpx;
}

.form-actions {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-top: 1px solid $uni-border-color;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
</style>
