<template>
  <view class="page">
    <view class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell
          title="选择物料"
          is-link
          value-align="left"
          title-width="33%"
          :value="selectedMaterialName"
          @click="onShowMaterialSelector"
        />

        <wd-input
          v-model="form.version"
          label="版本"
          placeholder="请输入版本"
          :maxlength="10"
          clearable
        />

        <wd-textarea
          v-model="form.description"
          label="描述"
          placeholder="请输入描述（可选）"
          :maxlength="255"
          auto-height
          clearable
        />

        <view class="switch-cell">
          <text class="switch-label">是否启用</text>
          <wd-switch v-model="form.is_active" />
        </view>
      </wd-cell-group>
    </view>

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
          <wd-button type="primary" size="large" @click="showMaterialSelector = false">确认</wd-button>
        </view>
      </view>
    </wd-popup>

    <view class="actions">
      <wd-button type="primary" size="large" :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中...' : '保存' }}
      </wd-button>
      <wd-button v-if="!isCreating" type="danger" size="large" plain @click="onDelete">删除 BOM</wd-button>
    </view>
  </view>
</template>

<script>
import bomApi from '@/api/bom'
import materialApi from '@/api/material'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'

/**
 * BOM 基本信息编辑页面
 * @description 提供 BOM 基本信息的创建、编辑与删除
 */
export default {
  name: 'BomEdit',

  components: {
    SearchableSelector
  },

  data() {
    return {
      /** @type {boolean} 是否创建模式 */
      isCreating: false,
      /** @type {number|null} BOM ID */
      bomId: null,
      /** @type {Object} 表单数据 */
      form: {
        material: null,
        version: '',
        description: '',
        is_active: true
      },
      /** @type {boolean} 是否保存中 */
      isSaving: false,
      /** @type {Object} materialApi 引用 */
      materialApi: materialApi,
      /** @type {boolean} 是否显示物料选择弹窗 */
      showMaterialSelector: false,
      /** @type {string} 物料显示名 */
      selectedMaterialLabel: ''
    }
  },

  computed: {
    /**
     * 物料显示名
     * @returns {string}
     */
    selectedMaterialName() {
      return this.selectedMaterialLabel || '请选择'
    }
  },

  onLoad(options) {
    if (options.id) {
      this.isCreating = false
      this.bomId = Number(options.id)
      this.loadBomDetail()
      return
    }
    this.isCreating = true
    this.bomId = null
  },

  methods: {
    /**
     * 加载 BOM 详情
     * @returns {Promise<void>}
     */
    async loadBomDetail() {
      uni.showLoading({ title: '加载中...' })
      try {
        const res = await bomApi.getBomDetail(this.bomId)
        if (res.code === 2000) {
          const bom = res.data || {}
          this.form = {
            material: bom.material || null,
            version: bom.version || '',
            description: bom.description || '',
            is_active: bom.is_active !== false
          }
          this.selectedMaterialLabel = bom.material_name || ''
          return
        }
        uni.showToast({ title: res.msg || '获取 BOM 详情失败', icon: 'none' })
      } catch (error) {
        console.error('获取 BOM 详情失败:', error)
        uni.showToast({ title: error.msg || '获取 BOM 详情失败', icon: 'none' })
      } finally {
        uni.hideLoading()
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
     * @param {Object|null} material - 选中的物料
     */
    onMaterialSelect(material) {
      this.selectedMaterialLabel = material?.name || ''
    },

    /**
     * 保存 BOM
     * @returns {Promise<void>}
     */
    async onSave() {
      if (!this.form.material) {
        uni.showToast({ title: '请选择物料', icon: 'none' })
        return
      }
      if (!this.form.version.trim()) {
        uni.showToast({ title: '请输入版本', icon: 'none' })
        return
      }

      this.isSaving = true
      try {
        const payload = {
          material: this.form.material,
          version: this.form.version.trim(),
          is_active: this.form.is_active,
          description: this.form.description?.trim() || ''
        }
        const res = this.isCreating
          ? await bomApi.createBom(payload)
          : await bomApi.updateBom(this.bomId, payload)

        if (res.code === 2000) {
          uni.showToast({ title: this.isCreating ? '创建成功' : '保存成功', icon: 'success' })
          uni.navigateBack()
          return
        }
        uni.showToast({ title: res.msg || (this.isCreating ? '创建失败' : '保存失败'), icon: 'none' })
      } catch (error) {
        console.error(this.isCreating ? '创建 BOM 失败:' : '保存 BOM 失败:', error)
        uni.showToast({ title: error.msg || (this.isCreating ? '创建失败' : '保存失败'), icon: 'none' })
      } finally {
        this.isSaving = false
      }
    },

    /**
     * 删除 BOM
     */
    onDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除该 BOM 吗？此操作不可恢复。',
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
     * 确认删除 BOM
     * @returns {Promise<void>}
     */
    async onConfirmDelete() {
      if (!this.bomId) {
        return
      }
      uni.showLoading({ title: '删除中...' })
      try {
        const res = await bomApi.deleteBom(this.bomId)
        if (res.code === 2000) {
          uni.showToast({ title: '删除成功', icon: 'success' })
          uni.navigateBack()
          return
        }
        uni.showToast({ title: res.msg || '删除失败', icon: 'none' })
      } catch (error) {
        console.error('删除 BOM 失败:', error)
        uni.showToast({ title: error.msg || '删除失败', icon: 'none' })
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
