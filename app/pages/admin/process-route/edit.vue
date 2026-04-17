<template>
  <view class="page">
    <view class="content">
      <!-- 工艺路线信息 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <!-- 物料选择 -->
        <SearchableSelector
          v-model="form.material"
          label="选择物料"
          placeholder="搜索物料名称或编码"
          search-key="name"
          :fetch-api="materialApi.getMaterialList"
          title-field="name"
          subtitle-field="code"
          :required="true"
        />

        <!-- 版本 -->
        <wd-input
          v-model="form.version"
          label="版本"
          placeholder="请输入版本"
          :maxlength="50"
          clearable
        />

        <!-- 描述 -->
        <wd-textarea
          v-model="form.description"
          label="描述"
          placeholder="请输入描述"
          :maxlength="255"
          auto-height
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
        删除工艺路线
      </wd-button>
    </view>
  </view>
</template>

<script>
import processRouteApi from '@/api/process-route.js'
import materialApi from '@/api/material.js'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * 工艺路线编辑/创建页面
 * @component
 * @description 提供工艺路线信息的编辑和创建功能
 *
 * API文档参考：
 * - 详情接口：/paths/_api_mes_process-routes_%7Bid%7D_.json
 * - 创建接口：/paths/_api_mes_process-routes_.json
 * - 更新接口：/paths/_api_mes_process-routes_%7Bid%7D_.json
 * - 删除接口：/paths/_api_mes_process-routes_%7Bid%7D_.json
 * - 模型定义：/components/schemas/ProcessRoute.json
 */
export default {
  name: 'ProcessRouteEdit',

  components: {
    SearchableSelector
  },

  data() {
    return {
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {number|null} 工艺路线ID（编辑模式） */
      processRouteId: null,
      /** @type {Object} 表单数据 */
      form: {
        material: null,
        version: '',
        description: ''
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {Object} materialApi 引用 */
      materialApi: materialApi
    }
  },

  onLoad(options) {
    if (options.id) {
      this.isCreating = false
      this.processRouteId = parseInt(options.id)
      this.loadProcessRouteDetail()
    } else {
      this.isCreating = true
      this.processRouteId = null
    }
  },

  methods: {
    /**
     * 加载工艺路线详情
     * @async
     *
     * API调用：processRouteApi.getProcessRouteDetail
     */
    async loadProcessRouteDetail() {
      uni.showLoading({ title: '加载中...' })
      try {
        const res = await processRouteApi.getProcessRouteDetail(this.processRouteId)
        if (res.code === 2000) {
          const route = res.data
          this.form = {
            material: route.material || null,
            version: route.version || '',
            description: route.description || ''
          }
        } else {
          uni.showToast({
            title: res.msg || '获取工艺路线信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取工艺路线详情失败:', error)
        uni.showToast({
          title: error.msg || '获取工艺路线信息失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },

    /**
     * 保存工艺路线
     * @async
     *
     * API调用：
     * - 创建：processRouteApi.createProcessRoute
     * - 更新：processRouteApi.updateProcessRoute
     */
    async onSave() {
      // 表单验证
      if (!this.form.material) {
        uni.showToast({
          title: '请选择物料',
          icon: 'none'
        })
        return
      }
      if (!this.form.version.trim()) {
        uni.showToast({
          title: '请输入版本',
          icon: 'none'
        })
        return
      }

      this.isSaving = true

      try {
        let res
        const data = {
          version: this.form.version.trim(),
          description: this.form.description?.trim() || ''
        }

        if (this.isCreating) {
          data.material = this.form.material
          res = await processRouteApi.createProcessRoute(data)
        } else {
          res = await processRouteApi.updateProcessRoute(this.processRouteId, data)
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
        console.error(this.isCreating ? '创建工艺路线失败:' : '保存工艺路线失败:', error)
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
        content: `确定要删除该工艺路线吗？此操作不可恢复。`,
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
     *
     * API调用：processRouteApi.deleteProcessRoute
     */
    async onConfirmDelete() {
      if (!this.processRouteId) return

      uni.showLoading({ title: '删除中...' })
      try {
        const res = await processRouteApi.deleteProcessRoute(this.processRouteId)
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
        console.error('删除工艺路线失败:', error)
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
