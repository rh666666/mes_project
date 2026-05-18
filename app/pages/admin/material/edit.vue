<template>
  <view class="page">
    <view class="content">
      <!-- 物料信息 -->
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-input
          v-model="form.code"
          label="物料编码"
          placeholder="请输入物料编码"
          :maxlength="100"
          clearable
        />
        <wd-input
          v-model="form.name"
          label="物料名称"
          placeholder="请输入物料名称"
          :maxlength="100"
          clearable
        />
        <wd-input
          v-model="form.description"
          label="物料描述"
          placeholder="请输入物料描述（可选）"
          :maxlength="200"
          clearable
        />
        <!-- 单位选择 -->
        <wd-cell
          title="单位"
          is-link
          value-align="left"
          title-width="33%"
          :value="selectedUnitName"
          @click="onShowUnitSelector"
        />
        <view class="switch-cell">
          <text class="switch-label">是否为产成品</text>
          <wd-switch v-model="form.is_production" />
        </view>
      </wd-cell-group>
    </view>

    <!-- 单位选择弹窗 -->
    <wd-popup v-model="showUnitSelector" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">选择单位</text>
          <wd-icon name="close" size="20" @click="showUnitSelector = false" />
        </view>
        <view class="popup-body">
          <SearchableSelector
            v-model="form.unit_id"
            label=""
            placeholder="搜索单位名称"
            search-key="name"
            :fetch-api="unitApi.getUnitList"
            title-field="name"
            subtitle-field="code"
            @select="onUnitSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" @click="showUnitSelector = false">
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
        删除物料
      </wd-button>
    </view>
  </view>
</template>

<script>
import materialApi from '@/api/material'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import unitApi from '@/api/unit'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * 物料编辑/创建页面
 * @component
 * @description 提供物料信息的编辑和创建功能
 */
export default {
  name: 'MaterialEdit',

  components: {
    SearchableSelector
  },

  data() {
    return {
      /** @type {boolean} 是否是创建模式 */
      isCreating: false,
      /** @type {number|null} 物料ID（编辑模式） */
      materialId: null,
      /** @type {Object} 表单数据 */
      form: {
        code: '',
        name: '',
        description: '',
        unit_id: '',
        is_production: false
      },
      /** @type {boolean} 是否正在保存 */
      isSaving: false,
      /** @type {Object} unitApi 引用 */
      unitApi: unitApi,
      /** @type {boolean} 是否显示单位选择弹窗 */
      showUnitSelector: false,
      /** @type {string} 已选单位名称 */
      selectedUnitLabel: ''
    }
  },

  computed: {
    /**
     * 已选单位显示名称
     * @returns {string}
     */
    selectedUnitName() {
      return this.selectedUnitLabel || '请选择'
    }
  },

  async onLoad(options) {
    if (options.id) {
      this.isCreating = false
      this.materialId = parseInt(options.id)
      await this.loadMaterialDetail()
    } else {
      this.isCreating = true
      this.materialId = null
    }
  },

  methods: {
    /**
     * 加载物料详情
     * @async
     */
    async loadMaterialDetail() {
      showAppLoading({ title: '加载中...' })
      try {
        const res = await materialApi.getMaterialDetail(this.materialId)
        if (res.code === 2000) {
          const material = res.data
          this.form = {
            code: material.code || '',
            name: material.name || '',
            description: material.description || '',
            unit_id: material.unit?.id || material.unit_id || '',
            is_production: material.is_production || false
          }
          this.selectedUnitLabel = material.unit?.name || ''
        } else {
          uni.showToast({
            title: res.msg || '获取物料信息失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取物料详情失败:', error)
        uni.showToast({
          title: error.msg || '获取物料信息失败',
          icon: 'none'
        })
      } finally {
        hideAppLoading()
      }
    },

    /**
     * 显示单位选择弹窗
     */
    onShowUnitSelector() {
      this.showUnitSelector = true
    },

    /**
     * 单位选择回调
     * @param {Object|null} unit - 选中的单位，为null表示取消选择
     */
    onUnitSelect(unit) {
      if (unit) {
        this.selectedUnitLabel = unit.name || ''
      } else {
        this.selectedUnitLabel = ''
      }
    },

    /**
     * 保存物料
     * @async
     */
    async onSave() {
      if (!this.form.code.trim()) {
        uni.showToast({
          title: '请输入物料编码',
          icon: 'none'
        })
        return
      }
      if (!this.form.name.trim()) {
        uni.showToast({
          title: '请输入物料名称',
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
          description: this.form.description.trim() || undefined,
          unit_id: this.form.unit_id || null,
          is_production: this.form.is_production
        }

        if (this.isCreating) {
          res = await materialApi.createMaterial(data)
        } else {
          res = await materialApi.updateMaterial(this.materialId, data)
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
        console.error(this.isCreating ? '创建物料失败:' : '保存物料失败:', error)
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
        content: `确定要删除物料 "${this.form.name}" 吗？此操作不可恢复。`,
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
      if (!this.materialId) return

      showAppLoading({ title: '删除中...' })
      try {
        const res = await materialApi.deleteMaterial(this.materialId)
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
        console.error('删除物料失败:', error)
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

.switch-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  background-color: $uni-bg-color-white;
  border-bottom: 1px solid $uni-border-color;
}

.switch-label {
  font-size: 28rpx;
  color: $uni-text-color;
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
