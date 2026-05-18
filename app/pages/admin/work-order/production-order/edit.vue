<template>
  <view class="page">
    <view class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell
          title="产品（产成品）"
          is-link
          value-align="left"
          title-width="33%"
          :value="selectedProductName"
          @click="onShowProductSelector"
        />

        <wd-picker
          v-model="form.process_route"
          label="工艺路线"
          placeholder="请选择工艺路线"
          :columns="routeColumns"
          :disabled="!form.product"
          @confirm="onRoutePickerConfirm"
        />

        <wd-input
          v-model="quantityInput"
          label="生产数量"
          type="number"
          placeholder="请输入正整数"
          clearable
        />

        <wd-textarea
          v-model="form.description"
          label="描述"
          placeholder="选填"
          :maxlength="255"
          auto-height
          clearable
        />
      </wd-cell-group>
    </view>

    <wd-popup v-model="showProductSelector" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">选择产成品</text>
          <wd-icon name="close" size="20" @click="showProductSelector = false" />
        </view>
        <view class="popup-body">
          <SearchableSelector
            v-model="form.product"
            label=""
            placeholder="搜索产品名称或编码"
            search-key="name"
            :fetch-api="fetchFinishedProductList"
            title-field="name"
            subtitle-field="code"
            :required="true"
            @select="onProductSelect"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" @click="showProductSelector = false">确认</wd-button>
        </view>
      </view>
    </wd-popup>

    <view class="actions">
      <wd-button type="primary" size="large" :loading="isSaving" @click="onSave">
        {{ isSaving ? '保存中...' : '保存' }}
      </wd-button>
    </view>
  </view>
</template>

<script>
import materialApi from '@/api/material'
import processRouteApi from '@/api/process-route'
import productionOrderApi from '@/api/production-order'
import { hideAppLoading, showAppLoading } from '@/utils/loading.js'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'
import { getStorageKey } from '@/config/index.js'
import { clampApiListLimit, fetchAllPagesWithPagedApi } from '@/utils/common.js'

/**
 * 生产任务单创建/编辑页（管理员）
 * @description 选择产成品与工艺路线、数量与描述；未下发状态可编辑
 */
export default {
  name: 'ProductionOrderEdit',

  components: {
    SearchableSelector
  },

  data() {
    return {
      /** @type {boolean} 是否新建 */
      isCreating: true,
      /** @type {number|null} 任务单 ID */
      orderId: null,
      /** @type {{product:number|null,process_route:number|string,description:string}} */
      form: {
        product: null,
        /** 工艺路线 ID；wd-picker 不接受 null，未选时使用空字符串 */
        process_route: '',
        description: ''
      },
      /** @type {string} 数量输入框（与 wd-input 绑定） */
      quantityInput: '',
      /** @type {string} 产品展示名 */
      selectedProductLabel: '',
      /** @type {Array<Object>} 工艺路线原始列表 */
      routeList: [],
      /** @type {boolean} 是否保存中 */
      isSaving: false,
      /** @type {boolean} 是否显示产品选择弹层 */
      showProductSelector: false
    }
  },

  computed: {
    /**
     * 产品单元格展示文本
     * @returns {string}
     */
    selectedProductName() {
      return this.selectedProductLabel || '请选择'
    },

    /**
     * 工艺路线下拉列
     * @returns {Array<{value:number,label:string}>}
     */
    routeColumns() {
      return this.routeList.map((r) => ({
        value: r.id,
        label: `${r.version || '-'} (${r.material_code || ''})`
      }))
    }
  },

  onLoad(options) {
    if (!this.assertAdmin()) {
      return
    }
    if (options.id) {
      this.isCreating = false
      this.orderId = Number(options.id)
      this.loadDetail()
      uni.setNavigationBarTitle({ title: '编辑任务单' })
      return
    }
    this.isCreating = true
    this.orderId = null
    uni.setNavigationBarTitle({ title: '新建任务单' })
  },

  methods: {
    /**
     * 校验管理员角色
     * @returns {boolean}
     */
    assertAdmin() {
      const userInfo = uni.getStorageSync(getStorageKey('user_info')) || {}
      if (userInfo.role !== 'admin') {
        uni.showToast({ title: '无权限访问', icon: 'none' })
        setTimeout(() => {
          uni.navigateBack({ fail: () => {} })
        }, 400)
        return false
      }
      return true
    },

    /**
     * 拉取产成品列表（全量分页加载后在前端按类型筛选并内存分页）
     * @param {Object} params - 分页与搜索参数（与 SearchableSelector 传入一致）
     * @returns {Promise<Object>}
     */
    async fetchFinishedProductList(params = {}) {
      const page = params.page || 1
      const limit = clampApiListLimit(params.limit || 20)
      const nameKw = (params.name || '').trim().toLowerCase()
      const base = {}
      if (params.name && String(params.name).trim()) {
        base.name = String(params.name).trim()
      }
      try {
        const allRows = await fetchAllPagesWithPagedApi((p) => materialApi.getMaterialList(p), base)
        let rows = allRows.filter((m) => m.is_production)
        if (nameKw) {
          rows = rows.filter(
            (m) =>
              (m.name && m.name.toLowerCase().includes(nameKw)) ||
              (m.code && m.code.toLowerCase().includes(nameKw))
          )
        }
        const start = (page - 1) * limit
        const slice = rows.slice(start, start + limit)
        return {
          code: 2000,
          data: slice,
          total: rows.length,
          page,
          limit
        }
      } catch (error) {
        console.error('获取产成品列表失败:', error)
        return {
          code: 400,
          msg: error.message || '加载失败',
          data: [],
          total: 0
        }
      }
    },

    /**
     * 加载任务单详情（编辑模式）
     * @returns {Promise<void>}
     */
    async loadDetail() {
      showAppLoading({ title: '加载中...' })
      try {
        const res = await productionOrderApi.getProductionOrderDetail(this.orderId)
        if (res.code === 2000) {
          const row = res.data || {}
          if (row.status && row.status !== 'pending') {
            uni.showToast({ title: '仅未下发任务单可编辑', icon: 'none' })
            setTimeout(() => uni.navigateBack(), 600)
            return
          }
          this.form.product = row.product != null ? row.product : null
          this.form.process_route = row.process_route != null ? row.process_route : ''
          this.form.description = row.description || ''
          this.quantityInput = row.quantity != null ? String(row.quantity) : ''
          this.selectedProductLabel = row.product_name || ''
          await this.loadProcessRoutes(this.form.product)
          return
        }
        uni.showToast({ title: res.msg || '加载失败', icon: 'none' })
      } catch (error) {
        console.error('加载任务单详情失败:', error)
        uni.showToast({ title: error.msg || '加载失败', icon: 'none' })
      } finally {
        hideAppLoading()
      }
    },

    /**
     * 根据产品加载工艺路线列表
     * @param {number|null} materialId - 产品物料 ID
     * @returns {Promise<void>}
     */
    async loadProcessRoutes(materialId) {
      if (!materialId) {
        this.routeList = []
        this.form.process_route = ''
        return
      }
      try {
        this.routeList = await fetchAllPagesWithPagedApi(
          (p) => processRouteApi.getProcessRouteList(p),
          { material: materialId }
        )
      } catch (error) {
        console.error('获取工艺路线失败:', error)
        this.routeList = []
        uni.showToast({
          title: (error.raw && error.raw.msg) || error.message || '获取工艺路线失败',
          icon: 'none'
        })
      }
    },

    /**
     * 打开产品选择弹层
     */
    onShowProductSelector() {
      this.showProductSelector = true
    },

    /**
     * 选中产品回调
     * @param {Object|null} material - 物料对象
     */
    async onProductSelect(material) {
      this.selectedProductLabel = material?.name || ''
      this.form.process_route = ''
      await this.loadProcessRoutes(material?.id || null)
    },

    /**
     * 工艺路线列变更时同步内部值（兼容 wd-picker）
     */
    onRoutePickerConfirm() {
      /* value 已由 v-model 同步 */
    },

    /**
     * 校验并提交
     * @returns {Promise<void>}
     */
    async onSave() {
      if (!this.form.product) {
        uni.showToast({ title: '请选择产品', icon: 'none' })
        return
      }
      if (this.form.process_route === '' || this.form.process_route === undefined) {
        uni.showToast({ title: '请选择工艺路线', icon: 'none' })
        return
      }
      const qty = parseInt(this.quantityInput, 10)
      if (!Number.isFinite(qty) || qty < 1) {
        uni.showToast({ title: '请输入有效的生产数量', icon: 'none' })
        return
      }

      this.isSaving = true
      try {
        const payload = {
          product: this.form.product,
          quantity: qty,
          process_route: Number(this.form.process_route),
          description: (this.form.description || '').trim()
        }
        let res
        if (this.isCreating) {
          res = await productionOrderApi.createProductionOrder(payload)
        } else {
          res = await productionOrderApi.updateProductionOrder(this.orderId, payload)
        }
        if (res.code === 2000) {
          uni.showToast({ title: '保存成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateBack()
          }, 500)
          return
        }
        uni.showToast({ title: res.msg || '保存失败', icon: 'none' })
      } catch (error) {
        console.error('保存任务单失败:', error)
        uni.showToast({ title: error.msg || '保存失败', icon: 'none' })
      } finally {
        this.isSaving = false
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
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.popup-content {
  padding: 24rpx;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 500;
}

.popup-body {
  flex: 1;
  min-height: 400rpx;
}

.popup-footer {
  margin-top: 24rpx;
}

.actions {
  padding: 32rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
}
</style>
