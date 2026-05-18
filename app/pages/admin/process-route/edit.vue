<template>
  <view class="page">
    <view class="content">
      <!-- 工艺路线信息 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <!-- 物料选择 -->
        <wd-cell
          title="选择物料"
          is-link
          value-align="left"
          title-width="33%"
          :value="selectedMaterialName"
          @click="onShowMaterialSelector"
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

    <!-- 物料选择弹窗 -->
    <wd-popup v-model="showMaterialSelector" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">选择物料</text>
          <wd-icon name="close" size="20" @click="showMaterialSelector = false" />
        </view>
        <view class="popup-body">
          <SearchableSelector
            v-model="form.material"
            label=""
            placeholder="搜索物料名称或编码"
            search-key="name"
            :fetch-api="materialApi.getMaterialList"
            title-field="name"
            subtitle-field="code"
            :required="true"
            @select="onMaterialSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" @click="showMaterialSelector = false">
            确认
          </wd-button>
        </view>
      </view>
    </wd-popup>

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
import processRouteApi from '@/api/process-route'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import materialApi from '@/api/material'
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
      materialApi: materialApi,
      /** @type {boolean} 是否显示物料选择弹窗 */
      showMaterialSelector: false,
      /** @type {string} 已选物料名称 */
      selectedMaterialLabel: ''
    }
  },

  computed: {
    /**
     * 已选物料显示名称
     * @returns {string}
     */
    selectedMaterialName() {
      return this.selectedMaterialLabel || '请选择'
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
      showAppLoading({ title: '加载中...' })
      try {
        const res = await processRouteApi.getProcessRouteDetail(this.processRouteId)
        if (res.code === 2000) {
          const route = res.data
          this.form = {
            material: route.material || null,
            version: route.version || '',
            description: route.description || ''
          }
          this.selectedMaterialLabel = route.material?.name || ''
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
        hideAppLoading()
      }
    },

    /**
     * 显示物料选择弹窗
     */
    onShowMaterialSelector() {
      this.showMaterialSelector = true
    },

    /**
     * 物料选择回调
     * @param {Object|null} material - 选中的物料，为null表示取消选择
     */
    onMaterialSelect(material) {
      if (material) {
        this.selectedMaterialLabel = material.name || ''
      } else {
        this.selectedMaterialLabel = ''
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

      showAppLoading({ title: '删除中...' })
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
        hideAppLoading()
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
