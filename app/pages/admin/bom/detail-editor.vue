<template>
  <view class="page">
    <view class="content">
      <view class="summary-card">
        <view class="summary-row">
          <text class="summary-label">物料</text>
          <text class="summary-value">{{ bomInfo.material_name || '-' }}</text>
        </view>
        <view class="summary-row">
          <text class="summary-label">版本</text>
          <text class="summary-value">{{ bomInfo.version || '-' }}</text>
        </view>
        <view class="summary-row">
          <text class="summary-label">是否启用</text>
          <text class="summary-value">{{ bomInfo.is_active ? '是' : '否' }}</text>
        </view>
        <wd-button size="small" type="primary" plain @click="onEditBaseInfo">编辑基本信息</wd-button>
      </view>

      <view class="section-header">
        <text class="section-title">详情项</text>
        <wd-button size="small" type="primary" @click="showCreatePopup = true">新增详情</wd-button>
      </view>

      <BomDetailTreeList :detail-list="detailList" @delete="onDeleteDetail" />
    </view>

    <wd-popup v-model="showCreatePopup" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">新增详情</text>
          <wd-icon name="close" size="20" @click="showCreatePopup = false" />
        </view>
        <view class="popup-body">
          <wd-cell-group>
            <wd-cell
              title="子物料"
              is-link
              value-align="left"
              title-width="33%"
              :value="selectedMaterialName"
              @click="showMaterialSelector = true"
            />
            <wd-cell
              title="子物料 BOM"
              is-link
              value-align="left"
              title-width="33%"
              :value="selectedSubBomName"
              @click="onShowSubBomSelector"
            />
            <wd-input
              v-model="createForm.quantity"
              label="数量"
              placeholder="请输入数量"
              type="digit"
              clearable
            />
          </wd-cell-group>
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" :loading="isCreatingDetail" @click="onCreateDetail">
            {{ isCreatingDetail ? '保存中...' : '保存' }}
          </wd-button>
        </view>
      </view>
    </wd-popup>

    <wd-popup v-model="showMaterialSelector" position="bottom" :safe-area-inset-bottom="true">
      <SearchableSelector
        v-model="createForm.material"
        label=""
        placeholder="搜索物料名称或编码"
        search-key="name"
        :fetch-api="materialApi.getMaterialList"
        title-field="name"
        subtitle-field="code"
        :required="true"
        @select="onMaterialSelect"
      />
    </wd-popup>

    <wd-popup v-model="showSubBomSelector" position="bottom" :safe-area-inset-bottom="true">
      <SearchableSelector
        v-model="createForm.sub_bom"
        label=""
        placeholder="搜索该子物料的 BOM 版本"
        search-key="search"
        :fetch-api="fetchSubBomListForMaterial"
        title-field="version"
        subtitle-field="material_code"
        @select="onSubBomSelect"
      />
    </wd-popup>
  </view>
</template>

<script>
import bomApi from '@/api/bom'
import materialApi from '@/api/material'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'
import BomDetailTreeList from '@/components/business/BomDetailTreeList.vue'

/**
 * BOM 详情编辑页面
 * @description 展示 BOM 基本信息，并支持详情项新增、删除和跳转基础信息编辑
 */
export default {
  name: 'BomDetailEditor',

  components: {
    SearchableSelector,
    BomDetailTreeList
  },

  data() {
    return {
      /** @type {number|null} BOM ID */
      bomId: null,
      /** @type {Object} BOM 基本信息 */
      bomInfo: {},
      /** @type {Array} BOM 详情列表 */
      detailList: [],
      /** @type {boolean} 是否显示新增弹窗 */
      showCreatePopup: false,
      /** @type {boolean} 是否显示物料选择弹窗 */
      showMaterialSelector: false,
      /** @type {boolean} 是否显示子 BOM 选择弹窗 */
      showSubBomSelector: false,
      /** @type {boolean} 是否新增中 */
      isCreatingDetail: false,
      /** @type {Object} 新增详情表单 */
      createForm: {
        material: null,
        sub_bom: null,
        quantity: ''
      },
      /** @type {string} 已选物料名称 */
      selectedMaterialLabel: '',
      /** @type {string} 已选子 BOM 名称 */
      selectedSubBomLabel: '',
      /** @type {Object} materialApi 引用 */
      materialApi: materialApi,
      /** @type {Object} bomApi 引用 */
      bomApi: bomApi
    }
  },

  computed: {
    /**
     * 已选物料显示名
     * @returns {string}
     */
    selectedMaterialName() {
      return this.selectedMaterialLabel || '请选择'
    },

    /**
     * 已选子 BOM 显示名
     * @returns {string}
     */
    selectedSubBomName() {
      return this.selectedSubBomLabel || '请选择'
    }
  },

  onLoad(options) {
    this.bomId = Number(options.id)
    this.loadPageData()
  },

  onShow() {
    this.loadPageData()
  },

  methods: {
    /**
     * 加载页面数据
     * @returns {Promise<void>}
     */
    async loadPageData() {
      if (!this.bomId) {
        return
      }
      showAppLoading({ title: '加载中...' })
      try {
        const [bomRes, detailRes] = await Promise.all([
          bomApi.getBomDetail(this.bomId),
          bomApi.getBomDetailList({ bom: this.bomId, page: 1, limit: 100 })
        ])

        if (bomRes.code === 2000) {
          this.bomInfo = bomRes.data || {}
        } else {
          uni.showToast({ title: bomRes.msg || '获取 BOM 信息失败', icon: 'none' })
        }

        if (detailRes.code === 2000) {
          this.detailList = detailRes.data || []
        } else {
          this.detailList = []
          uni.showToast({ title: detailRes.msg || '获取详情列表失败', icon: 'none' })
        }
      } catch (error) {
        console.error('加载 BOM 详情页失败:', error)
        uni.showToast({ title: error.msg || '加载失败', icon: 'none' })
      } finally {
        hideAppLoading()
      }
    },

    /**
     * 跳转基础信息编辑页
     */
    onEditBaseInfo() {
      uni.navigateTo({
        url: `/pages/admin/bom/edit?id=${this.bomId}`
      })
    },

    /**
     * 物料选择回调
     * @param {Object|null} material - 已选物料
     */
    async onMaterialSelect(material) {
      this.selectedMaterialLabel = material?.name || ''
      this.createForm.sub_bom = null
      this.selectedSubBomLabel = ''
      this.showMaterialSelector = false
      await this.syncDefaultSubBom(material)
    },

    /**
     * 打开子物料 BOM 选择器
     */
    onShowSubBomSelector() {
      if (!this.createForm.material) {
        uni.showToast({ title: '请先选择子物料', icon: 'none' })
        return
      }
      this.showSubBomSelector = true
    },

    /**
     * 拉取当前子物料名下的 BOM 列表
     * @param {Object} params - 分页与搜索参数
     * @returns {Promise<Object>}
     */
    fetchSubBomListForMaterial(params = {}) {
      if (!this.createForm.material) {
        return Promise.resolve({
          code: 400,
          msg: '请先选择子物料',
          data: [],
          total: 0
        })
      }
      return bomApi.getBomList({
        ...params,
        material: this.createForm.material
      })
    },

    /**
     * 根据子物料同步默认子 BOM（优先启用版本）
     * @param {Object|null} material - 已选子物料
     * @returns {Promise<void>}
     */
    async syncDefaultSubBom(material) {
      if (!material?.id) {
        this.createForm.sub_bom = null
        this.selectedSubBomLabel = '无 BOM（叶子物料）'
        return
      }
      try {
        const res = await bomApi.getBomList({ material: material.id, page: 1, limit: 20 })
        if (res.code !== 2000 || !res.data?.length) {
          this.createForm.sub_bom = null
          this.selectedSubBomLabel = '无 BOM（叶子物料）'
          return
        }
        const preferred = res.data.find((item) => item.is_active) || res.data[0]
        this.createForm.sub_bom = preferred.id
        this.selectedSubBomLabel = this.formatSubBomLabel(preferred)
      } catch (error) {
        console.error('加载子物料 BOM 失败:', error)
        this.createForm.sub_bom = null
        this.selectedSubBomLabel = ''
      }
    },

    /**
     * 格式化子 BOM 展示文案
     * @param {Object|null} bom - BOM 记录
     * @returns {string}
     */
    formatSubBomLabel(bom) {
      if (!bom) {
        return '无 BOM（叶子物料）'
      }
      const version = bom.version || '-'
      const code = bom.material_code || bom.material_name || '-'
      return `${version} (${code})`
    },

    /**
     * 子 BOM 选择回调
     * @param {Object|null} bom - 已选子 BOM
     */
    onSubBomSelect(bom) {
      if (bom && bom.material != null && bom.material !== this.createForm.material) {
        uni.showToast({ title: '只能选择该子物料名下的 BOM', icon: 'none' })
        return
      }
      this.selectedSubBomLabel = bom ? this.formatSubBomLabel(bom) : '无 BOM（叶子物料）'
      this.createForm.sub_bom = bom?.id ?? null
      this.showSubBomSelector = false
    },

    /**
     * 创建详情项
     * @returns {Promise<void>}
     */
    async onCreateDetail() {
      if (!this.createForm.material) {
        uni.showToast({ title: '请选择子物料', icon: 'none' })
        return
      }
      if (this.bomInfo.material && this.createForm.material === this.bomInfo.material) {
        uni.showToast({ title: '子物料不能与当前 BOM 所属物料相同', icon: 'none' })
        return
      }
      const quantity = Number(this.createForm.quantity)
      if (!Number.isInteger(quantity) || quantity <= 0) {
        uni.showToast({ title: '请输入大于 0 的整数数量', icon: 'none' })
        return
      }

      this.isCreatingDetail = true
      try {
        const payload = {
          bom: this.bomId,
          material: this.createForm.material,
          quantity: quantity
        }
        if (this.createForm.sub_bom) {
          payload.sub_bom = this.createForm.sub_bom
        }

        const res = await bomApi.createBomDetail(payload)
        if (res.code === 2000) {
          this.resetCreateForm()
          this.showCreatePopup = false
          await this.loadPageData()
          uni.showToast({ title: '新增成功', icon: 'success' })
          return
        }
        uni.showToast({ title: res.msg || '新增失败', icon: 'none' })
      } catch (error) {
        console.error('新增 BOM 详情失败:', error)
        uni.showToast({ title: error.msg || '新增失败', icon: 'none' })
      } finally {
        this.isCreatingDetail = false
      }
    },

    /**
     * 删除详情项
     * @param {Object} detail - 详情项
     */
    onDeleteDetail(detail) {
      uni.showModal({
        title: '确认删除',
        content: `确定删除详情项 "${detail.material_name || detail.material_code || detail.id}" 吗？`,
        confirmText: '删除',
        confirmColor: '#ee0a24',
        success: async (res) => {
          if (!res.confirm) {
            return
          }
          showAppLoading({ title: '删除中...' })
          try {
            const result = await bomApi.deleteBomDetail(detail.id)
            if (result.code === 2000) {
              await this.loadPageData()
              uni.showToast({ title: '删除成功', icon: 'success' })
            } else {
              uni.showToast({ title: result.msg || '删除失败', icon: 'none' })
            }
          } catch (error) {
            console.error('删除 BOM 详情失败:', error)
            uni.showToast({ title: error.msg || '删除失败', icon: 'none' })
          } finally {
            hideAppLoading()
          }
        }
      })
    },

    /**
     * 重置新增表单
     */
    resetCreateForm() {
      this.createForm = {
        material: null,
        sub_bom: null,
        quantity: ''
      }
      this.selectedMaterialLabel = ''
      this.selectedSubBomLabel = ''
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $uni-bg-color;
}

.content {
  padding: 24rpx;
}

.summary-card {
  background-color: $uni-bg-color-white;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.summary-row {
  display: flex;
  justify-content: space-between;
}

.summary-label {
  font-size: 24rpx;
  color: $uni-text-color-grey;
}

.summary-value {
  font-size: 26rpx;
  color: $uni-text-color;
}

.section-header {
  margin: 24rpx 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 28rpx;
  color: $uni-text-color;
  font-weight: 500;
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

  :deep(.wd-button) {
    width: 100%;
  }
}
</style>
