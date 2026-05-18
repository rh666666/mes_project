<template>
  <view class="page">
    <view v-if="order" class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell title="质检编码" :value="order.code || '-'" />
        <wd-cell title="类型" :value="order.type_display || order.type || '-'" />
        <wd-cell title="状态" :value="order.status_display || order.status || '-'" />
        <wd-cell
          title="生产任务单"
          :value="order.production_order_code || '-'"
          is-link
          @click="onGoProductionOrder"
        />
        <wd-cell title="产品" :value="productSummary" />
        <wd-cell title="质检数量" :value="order.quantity != null ? String(order.quantity) : '-'" />
        <wd-cell title="合格品数量" :value="order.qualified_quantity != null ? String(order.qualified_quantity) : '-'" />
        <wd-cell title="不合格品数量" :value="order.unqualified_quantity != null ? String(order.unqualified_quantity) : '-'" />
        <wd-cell title="创建时间" :value="formatDateTime(order.create_datetime)" />
        <wd-cell title="更新时间" :value="formatDateTime(order.update_datetime)" />
      </wd-cell-group>
    </view>

    <view v-else-if="!loadError" class="loading-wrap">
      <wd-loading />
    </view>
    <wd-status-tip v-else image="search" :tip="loadError" />

    <wd-popup
      v-if="order"
      v-model="showOperationDrawer"
      position="right"
      :modal="true"
      :safe-area-inset-bottom="true"
      :root-portal="false"
      custom-class="operation-drawer-popup"
      custom-style="width: 520rpx; height: 100%; max-width: 85vw; box-sizing: border-box;"
      @close="onOperationDrawerClose"
    >
      <view class="operation-drawer">
        <view class="operation-drawer-header">
          <text class="operation-drawer-title">操作</text>
          <wd-icon name="close" size="20" @click="closeOperationDrawer" />
        </view>
        <wd-cell-group border class="operation-drawer-body">
          <wd-cell v-if="canSubmit" title="提交质检结果" is-link @click="onDrawerSubmit" />
        </wd-cell-group>
      </view>
    </wd-popup>

    <wd-popup
      v-if="order"
      v-model="showSubmitPopup"
      position="bottom"
      :safe-area-inset-bottom="true"
      :root-portal="false"
    >
      <view class="popup-sheet">
        <view class="popup-header">
          <text class="popup-title">提交质检结果</text>
          <wd-icon name="close" size="20" @click="showSubmitPopup = false" />
        </view>
        <view class="popup-body">
          <text class="submit-hint">合格品与不合格品数量之和须等于质检数量 {{ order.quantity }}</text>
          <wd-input v-model="qualifiedInput" type="number" label="合格品数量" placeholder="请输入" />
          <wd-input v-model="unqualifiedInput" type="number" label="不合格品数量" placeholder="请输入" />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" block :loading="submitLoading" @click="onConfirmSubmit">
            确认提交
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import qualityCheckOrderApi from '@/api/quality-check-order'
import { getStorageKey } from '@/config/index.js'
import { formatDateTime } from '@/utils/format.js'

/**
 * 质检任务单详情（管理员）
 * @description 展示详情；导航栏操作抽屉内可提交质检结果（待质检）
 */
export default {
  data() {
    return {
      /** @type {number|null} 质检任务单 ID */
      orderId: null,
      /** @type {Object|null} 详情数据 */
      order: null,
      /** @type {string} 加载错误 */
      loadError: '',
      /** @type {boolean} 右侧操作抽屉 */
      showOperationDrawer: false,
      /** @type {boolean} 提交弹层 */
      showSubmitPopup: false,
      /** @type {string} 合格品数量输入 */
      qualifiedInput: '',
      /** @type {string} 不合格品数量输入 */
      unqualifiedInput: '',
      /** @type {boolean} 提交中 */
      submitLoading: false
    }
  },

  computed: {
    /**
     * 产品展示
     * @returns {string}
     */
    productSummary() {
      if (!this.order) {
        return '-'
      }
      const name = this.order.product_name || ''
      const code = this.order.product_code || ''
      if (name && code) {
        return `${name} (${code})`
      }
      return name || code || '-'
    },

    /**
     * 是否可提交质检结果
     * @returns {boolean}
     */
    canSubmit() {
      return this.order && this.order.status === 'pending'
    }
  },

  onLoad(options) {
    const userInfo = uni.getStorageSync(getStorageKey('user_info')) || {}
    if (userInfo.role !== 'admin') {
      uni.showToast({ title: '无权限访问', icon: 'none' })
      setTimeout(() => {
        uni.navigateBack({ fail: () => {} })
      }, 400)
      return
    }

    if (options.id) {
      const n = Number(options.id)
      if (!Number.isNaN(n)) {
        this.orderId = n
        this.loadDetail()
        return
      }
    }
    this.loadError = '缺少质检任务单 ID'
  },

  /**
   * 导航栏右侧按钮：index 0 打开操作抽屉，index 1 刷新详情
   * @param {Object} e - 事件对象
   */
  onNavigationBarButtonTap(e) {
    if (e.index === 0) {
      this.openOperationDrawer()
      return
    }
    if (e.index === 1) {
      this.loadDetail()
    }
  },

  methods: {
    formatDateTime,

    /**
     * 打开右侧操作抽屉
     */
    openOperationDrawer() {
      if (this.orderId == null) {
        uni.showToast({ title: '页面未就绪', icon: 'none' })
        return
      }
      this.showOperationDrawer = true
    },

    /**
     * 关闭操作抽屉
     */
    closeOperationDrawer() {
      this.showOperationDrawer = false
    },

    /**
     * 抽屉关闭回调（含点击遮罩）
     */
    onOperationDrawerClose() {
      this.showOperationDrawer = false
    },

    /**
     * 抽屉内：提交质检结果
     */
    onDrawerSubmit() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onOpenSubmit()
      })
    },

    /**
     * 加载质检任务单详情
     * @returns {Promise<void>}
     */
    async loadDetail() {
      if (this.orderId == null) {
        return
      }
      this.loadError = ''
      try {
        const res = await qualityCheckOrderApi.getQualityCheckOrderDetail(this.orderId)
        if (res.code === 2000 && res.data) {
          this.order = res.data
          return
        }
        this.loadError = res.msg || '加载失败'
      } catch (error) {
        console.error('加载质检任务单详情失败:', error)
        this.loadError = error.msg || '加载失败'
      }
    },

    /**
     * 跳转关联生产任务单详情
     */
    onGoProductionOrder() {
      if (!this.order || !this.order.production_order) {
        uni.showToast({ title: '无关联生产任务单', icon: 'none' })
        return
      }
      uni.navigateTo({
        url: `/pages/admin/work-order/production-order/detail?id=${this.order.production_order}`
      })
    },

    /**
     * 打开提交质检结果弹层
     */
    onOpenSubmit() {
      if (!this.canSubmit) {
        return
      }
      this.qualifiedInput = ''
      this.unqualifiedInput = ''
      this.showSubmitPopup = true
    },

    /**
     * 确认提交质检结果
     * @returns {Promise<void>}
     */
    async onConfirmSubmit() {
      if (!this.order) {
        return
      }

      const qualified = parseInt(this.qualifiedInput, 10)
      const unqualified = parseInt(this.unqualifiedInput, 10)
      const qty = this.order.quantity

      if (Number.isNaN(qualified) || qualified < 0) {
        uni.showToast({ title: '请输入有效的合格品数量', icon: 'none' })
        return
      }
      if (Number.isNaN(unqualified) || unqualified < 0) {
        uni.showToast({ title: '请输入有效的不合格品数量', icon: 'none' })
        return
      }
      if (qualified + unqualified !== qty) {
        uni.showToast({
          title: `合格与不合格数量之和须等于质检数量 ${qty}`,
          icon: 'none'
        })
        return
      }

      this.submitLoading = true
      try {
        const res = await qualityCheckOrderApi.submitQualityCheckResult(this.orderId, {
          qualified_quantity: qualified,
          unqualified_quantity: unqualified
        })
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '提交成功', icon: 'success' })
          this.showSubmitPopup = false
          await this.loadDetail()
          return
        }
        uni.showToast({ title: res.msg || '提交失败', icon: 'none' })
      } catch (error) {
        console.error('提交质检结果失败:', error)
        uni.showToast({ title: error.msg || '提交失败', icon: 'none' })
      } finally {
        this.submitLoading = false
      }
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

.section-header {
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 26rpx;
  font-weight: 500;
  color: $uni-text-color-grey;
}

.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.popup-sheet {
  background-color: $uni-bg-color-white;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx;
  border-bottom: 1px solid $uni-border-color;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.popup-body {
  padding: 24rpx 32rpx;
}

.popup-footer {
  padding: 24rpx 32rpx 32rpx;
}

.submit-hint {
  display: block;
  font-size: 24rpx;
  color: $uni-text-color-grey;
  margin-bottom: 24rpx;
  line-height: 1.5;
}

.operation-drawer {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background-color: $uni-bg-color-white;
}

.operation-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 24rpx;
  border-bottom: 1px solid $uni-border-color;
}

.operation-drawer-title {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.operation-drawer-body {
  flex: 1;
}
</style>
