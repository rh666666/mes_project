<template>
  <view class="page">
    <view v-if="order" class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell title="派工单编码" :value="order.code || '-'" />
        <wd-cell title="状态" :value="order.status_display || order.status || '-'" />
        <wd-cell title="生产任务单" :value="order.production_order_code || '-'" />
        <wd-cell title="工序" :value="processSummary" />
        <wd-cell title="工序顺序" :value="order.sequence != null ? String(order.sequence) : '-'" />
        <wd-cell title="生产数量" :value="order.quantity != null ? String(order.quantity) : '-'" />
        <wd-cell title="已完成数量" :value="order.completed_quantity != null ? String(order.completed_quantity) : '-'" />
        <wd-cell title="可派发" :value="order.is_reachable ? '是' : '否'" />
        <wd-cell title="接单人" :value="order.operator_name || '-'" />
        <wd-cell title="设备编码" :value="deviceSummary" />
        <wd-cell title="父工单" :value="parentSummary" />
        <wd-cell title="子工单数" :value="order.children_count != null ? String(order.children_count) : '-'" />
        <wd-cell title="创建时间" :value="order.create_datetime || '-'" />
        <wd-cell title="更新时间" :value="order.update_datetime || '-'" />
      </wd-cell-group>

      <view v-if="dispatchHint" class="hint-box section-mt">
        <text class="hint-text">{{ dispatchHint }}</text>
      </view>
    </view>

    <view v-else-if="!loadError" class="loading-wrap">
      <wd-loading />
    </view>
    <wd-status-tip v-else image="search" :tip="loadError" />

    <wd-popup
      v-model="showOperationDrawer"
      position="right"
      :modal="true"
      :safe-area-inset-bottom="true"
      :root-portal="true"
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
          <wd-cell v-if="canDispatch" title="派工" is-link @click="onDrawerDispatch" />
          <wd-cell v-if="canSplit" title="拆分派工单" is-link @click="onDrawerSplit" />
        </wd-cell-group>
      </view>
    </wd-popup>

    <wd-popup v-model="showDispatchPopup" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-sheet">
        <view class="popup-header">
          <text class="popup-title">派工</text>
          <wd-icon name="close" size="20" @click="showDispatchPopup = false" />
        </view>
        <view class="popup-body popup-body--scroll">
          <wd-cell
            title="接单人"
            is-link
            value-align="left"
            title-width="33%"
            :value="dispatchOperatorLabel || '可选'"
            @click="showOperatorSelector = true"
          />
          <wd-cell
            title="生产设备"
            is-link
            value-align="left"
            title-width="33%"
            :value="dispatchDeviceLabel || '可选'"
            @click="showDeviceSelector = true"
          />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" block :loading="actionLoading === 'dispatch'" @click="onConfirmDispatch">
            确认派工
          </wd-button>
        </view>
      </view>
    </wd-popup>

    <wd-popup v-model="showOperatorSelector" position="bottom" :safe-area-inset-bottom="true">
      <SearchableSelector
        v-model="dispatchForm.operator"
        label=""
        placeholder="搜索姓名或用户名"
        search-key="search"
        :fetch-api="authApi.getUserList"
        title-field="name"
        subtitle-field="username"
        :page-size="selectorPageSize"
        :show-avatar="true"
        @select="onOperatorSelect"
      />
    </wd-popup>

    <wd-popup v-model="showDeviceSelector" position="bottom" :safe-area-inset-bottom="true">
      <SearchableSelector
        v-model="dispatchForm.device"
        label=""
        placeholder="搜索设备名称"
        search-key="name"
        :fetch-api="deviceApi.getDeviceList"
        title-field="name"
        subtitle-field="code"
        :page-size="selectorPageSize"
        @select="onDeviceSelect"
      />
    </wd-popup>

    <wd-popup v-model="showSplitPopup" position="bottom" :safe-area-inset-bottom="true">
      <view class="popup-sheet">
        <view class="popup-header">
          <text class="popup-title">拆分派工单</text>
          <wd-icon name="close" size="20" @click="showSplitPopup = false" />
        </view>
        <view class="popup-body">
          <text class="split-hint">拆分数量范围：1 ~ {{ maxSplitQuantity }}（须小于当前工单数量且不超过剩余未生产数量）</text>
          <wd-input v-model="splitQuantityInput" type="number" label="拆分数量" placeholder="请输入正整数" />
        </view>
        <view class="popup-footer">
          <wd-button type="primary" size="large" block :loading="actionLoading === 'split'" @click="onConfirmSplit">
            确认拆分
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import authApi from '@/api/auth'
import deviceApi from '@/api/device'
import dispatchOrderApi from '@/api/dispatch-order'
import SearchableSelector from '@/components/ui/SearchableSelector/SearchableSelector.vue'
import { getStorageKey } from '@/config/index.js'
import { clampApiListLimit } from '@/utils/common.js'

/**
 * 工序派工单详情（管理员）
 * @description 展示详情；待抢单时可派工；满足数量规则时可拆分
 */
export default {
  components: {
    SearchableSelector
  },

  data() {
    return {
      /** @type {number|null} 派工单 ID */
      orderId: null,
      /** @type {Object|null} 详情数据 */
      order: null,
      /** @type {string} 加载错误 */
      loadError: '',
      /** @type {boolean} 刷新中 */
      reloadLoading: false,
      /** @type {string} 进行中的操作 */
      actionLoading: '',
      /** @type {boolean} 派工弹层 */
      showDispatchPopup: false,
      /** @type {boolean} 接单人选择器 */
      showOperatorSelector: false,
      /** @type {boolean} 设备选择器 */
      showDeviceSelector: false,
      /** @type {{operator: number|string, device: number|string}} 派工表单 */
      dispatchForm: {
        operator: '',
        device: ''
      },
      /** @type {string} 接单人展示 */
      dispatchOperatorLabel: '',
      /** @type {string} 设备展示 */
      dispatchDeviceLabel: '',
      /** @type {boolean} 右侧操作抽屉 */
      showOperationDrawer: false,
      /** @type {boolean} 拆分弹层 */
      showSplitPopup: false,
      /** @type {string} 拆分数量输入 */
      splitQuantityInput: '1',
      /** @type {number} 选择器分页大小 */
      selectorPageSize: clampApiListLimit(20),
      authApi,
      deviceApi
    }
  },

  computed: {
    /**
     * 工序展示
     * @returns {string}
     */
    processSummary() {
      if (!this.order) return '-'
      const name = this.order.process_name || ''
      const code = this.order.process_code || ''
      if (name && code) return `${name} (${code})`
      return name || code || '-'
    },

    /**
     * 设备编码展示（详情接口只读字段）
     * @returns {string}
     */
    deviceSummary() {
      if (!this.order) return '-'
      return this.order.device_code ? String(this.order.device_code) : '-'
    },

    /**
     * 父工单展示
     * @returns {string}
     */
    parentSummary() {
      if (!this.order || !this.order.parent) return '-'
      return this.order.parent_code || String(this.order.parent)
    },

    /**
     * 是否可派工（后端仅允许待抢单）
     * @returns {boolean}
     */
    canDispatch() {
      return this.order && this.order.status === 'pending'
    },

    /**
     * 剩余可生产数量
     * @returns {number}
     */
    remainingQuantity() {
      if (!this.order) return 0
      const q = Number(this.order.quantity) || 0
      const c = Number(this.order.completed_quantity) || 0
      return Math.max(0, q - c)
    },

    /**
     * 允许拆分的最大数量（含业务约束）
     * @returns {number}
     */
    maxSplitQuantity() {
      if (!this.order) return 0
      const q = Number(this.order.quantity) || 0
      const rem = this.remainingQuantity
      if (q <= 1 || rem <= 0) return 0
      const capByQty = q - 1
      return Math.min(rem, capByQty)
    },

    /**
     * 是否展示拆分入口
     * @returns {boolean}
     */
    canSplit() {
      return this.maxSplitQuantity >= 1
    },

    /**
     * 派工前置提示
     * @returns {string}
     */
    dispatchHint() {
      if (!this.order || !this.canDispatch) return ''
      if (this.order.sequence > 1 && this.order.is_reachable === false) {
        return '当前工序可能仍受前置工序产出限制，提交派工以后端校验为准。'
      }
      return ''
    }
  },

  onLoad(options) {
    if (!this.assertAdmin()) {
      return
    }
    if (!options.id) {
      this.loadError = '缺少派工单 ID'
      return
    }
    this.orderId = Number(options.id)
    this.loadAll()
  },

  /**
   * App 原生导航栏右侧按钮：buttons 自右向左排列，index 0 为最右侧（纵向三点），index 1 为刷新（三点左侧）
   * @param {Object} e - 事件对象
   */
  onNavigationBarButtonTap(e) {
    if (e.index === 0) {
      this.openOperationDrawer()
      return
    }
    if (e.index === 1) {
      this.reload()
    }
  },

  methods: {
    /**
     * 打开右侧操作抽屉（与导航栏三点按钮一致；wot 无独立 Drawer，使用 wd-popup position=right）
     */
    openOperationDrawer() {
      if (!this.orderId) {
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
     * 抽屉内：派工
     */
    onDrawerDispatch() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onOpenDispatch()
      })
    },

    /**
     * 抽屉内：拆分
     */
    onDrawerSplit() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onOpenSplit()
      })
    },

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
     * 加载详情
     * @returns {Promise<void>}
     */
    async loadAll() {
      this.loadError = ''
      this.reloadLoading = true
      try {
        const res = await dispatchOrderApi.getDispatchOrderDetail(this.orderId)
        if (res.code !== 2000) {
          this.loadError = res.msg || '加载失败'
          return
        }
        this.order = res.data || null
      } catch (error) {
        console.error('加载工序派工单详情失败:', error)
        this.loadError = error.msg || '加载失败'
      } finally {
        this.reloadLoading = false
      }
    },

    /**
     * 刷新
     * @returns {Promise<void>}
     */
    async reload() {
      await this.loadAll()
      if (this.order && !this.loadError) {
        uni.showToast({ title: '已更新', icon: 'success' })
      }
    },

    /**
     * 打开派工弹层并清空临时展示
     */
    onOpenDispatch() {
      this.dispatchForm = { operator: '', device: '' }
      this.dispatchOperatorLabel = ''
      this.dispatchDeviceLabel = ''
      this.showDispatchPopup = true
    },

    /**
     * 接单人选中
     * @param {Object} user - 用户行
     */
    onOperatorSelect(user) {
      this.dispatchOperatorLabel = user.name || user.username || ''
      this.showOperatorSelector = false
    },

    /**
     * 设备选中
     * @param {Object} dev - 设备行
     */
    onDeviceSelect(dev) {
      this.dispatchDeviceLabel = dev.name || dev.code || ''
      this.showDeviceSelector = false
    },

    /**
     * 提交派工
     * @returns {Promise<void>}
     */
    async onConfirmDispatch() {
      if (!this.orderId) return
      this.actionLoading = 'dispatch'
      try {
        const body = {}
        if (this.dispatchForm.operator !== '' && this.dispatchForm.operator != null) {
          body.operator = Number(this.dispatchForm.operator)
        }
        if (this.dispatchForm.device !== '' && this.dispatchForm.device != null) {
          body.device = Number(this.dispatchForm.device)
        }
        const res = await dispatchOrderApi.dispatchDispatchOrder(this.orderId, body)
        if (res.code === 2000) {
          uni.showToast({ title: res.msg || '派工成功', icon: 'success' })
          this.showDispatchPopup = false
          await this.loadAll()
          return
        }
        uni.showToast({ title: res.msg || '派工失败', icon: 'none' })
      } catch (error) {
        console.error('派工失败:', error)
        uni.showToast({ title: error.msg || '派工失败', icon: 'none' })
      } finally {
        this.actionLoading = ''
      }
    },

    /**
     * 打开拆分弹层
     */
    onOpenSplit() {
      this.splitQuantityInput = this.maxSplitQuantity >= 1 ? '1' : '1'
      this.showSplitPopup = true
    },

    /**
     * 提交拆分
     * @returns {Promise<void>}
     */
    async onConfirmSplit() {
      const n = parseInt(String(this.splitQuantityInput).trim(), 10)
      if (Number.isNaN(n) || n < 1) {
        uni.showToast({ title: '请输入有效的拆分数量', icon: 'none' })
        return
      }
      if (n > this.maxSplitQuantity) {
        uni.showToast({ title: '拆分数量超出允许范围', icon: 'none' })
        return
      }
      if (!this.orderId) return
      this.actionLoading = 'split'
      try {
        const res = await dispatchOrderApi.splitDispatchOrder(this.orderId, { split_quantity: n })
        if (res.code === 2000) {
          const child = res.data && res.data.child_order ? res.data.child_order : null
          const code = child && child.code ? child.code : ''
          uni.showToast({
            title: code ? `拆分成功，子工单 ${code}` : res.msg || '拆分成功',
            icon: 'none'
          })
          this.showSplitPopup = false
          await this.loadAll()
          return
        }
        uni.showToast({ title: res.msg || '拆分失败', icon: 'none' })
      } catch (error) {
        console.error('拆分失败:', error)
        uni.showToast({ title: error.msg || '拆分失败', icon: 'none' })
      } finally {
        this.actionLoading = ''
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $uni-bg-color;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.content {
  padding: 24rpx;
}

.section-header {
  margin-bottom: 16rpx;
}

.section-mt {
  margin-top: 32rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 500;
  color: $uni-text-color;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 80rpx;
}

.hint-box {
  padding: 16rpx 24rpx;
  background-color: $uni-bg-color-white;
  border-radius: 12rpx;
}

.hint-text {
  font-size: 24rpx;
  color: $uni-text-color-grey;
  line-height: 1.5;
}

.popup-sheet {
  background-color: $uni-bg-color-white;
  border-radius: 24rpx 24rpx 0 0;
  padding-bottom: env(safe-area-inset-bottom);
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
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

.popup-body--scroll {
  max-height: 60vh;
  overflow-y: auto;
}

.popup-footer {
  padding: 24rpx 32rpx 32rpx;
}

.split-hint {
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
