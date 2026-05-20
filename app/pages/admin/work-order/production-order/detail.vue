<template>
  <view class="page">
    <view v-if="order" class="content">
      <view class="section-header">
        <text class="section-title">基本信息</text>
      </view>
      <wd-cell-group>
        <wd-cell title="任务单编码" :value="order.code || '-'" />
        <wd-cell title="状态" :value="order.status_display || order.status || '-'" />
        <wd-cell title="产品" :value="order.product_name || '-'" />
        <wd-cell title="生产数量" :value="order.quantity != null ? String(order.quantity) : '-'" />
        <wd-cell title="工艺路线" :value="routeSummary" />
        <wd-cell v-if="order.description" title="描述" :value="order.description" />
      </wd-cell-group>

      <view class="section-header section-mt">
        <text class="section-title">派工进度</text>
      </view>
      <wd-cell-group>
        <wd-cell title="完成情况" :value="completedDispatchSummary" />
      </wd-cell-group>

      <view class="section-header section-mt">
        <text class="section-title">原材料需求</text>
      </view>
      <wd-cell-group v-if="materialRows.length">
        <wd-cell
          v-for="row in materialRows"
          :key="row.key"
          :title="row.name"
          :label="row.code"
          :value="String(row.qty)"
        />
      </wd-cell-group>
      <view v-else class="empty-hint">
        <text class="hint-text">暂无原材料需求数据（末序未配置成品 BOM 或路线不完整时为空）</text>
      </view>
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
          <wd-cell v-if="order" title="查看工序派工单" is-link @click="onDrawerDispatchList" />
          <wd-cell v-if="order" title="查看质检任务单" is-link @click="onDrawerQualityCheckList" />
          <wd-cell
            v-if="order && order.status === 'pending'"
            title="下发"
            is-link
            @click="onDrawerPublish"
          />
          <wd-cell
            v-if="order && order.status === 'pending'"
            title="编辑"
            is-link
            @click="onDrawerEdit"
          />
          <wd-cell
            v-if="order && order.status === 'pending'"
            title="删除"
            is-link
            @click="onDrawerDelete"
          />
          <wd-cell
            v-if="order && order.status === 'published'"
            title="取消任务单"
            is-link
            @click="onDrawerCancel"
          />
        </wd-cell-group>
      </view>
    </wd-popup>
  </view>
</template>

<script>
import productionOrderApi from '@/api/production-order'
import processRouteApi from '@/api/process-route'
import { getStorageKey } from '@/config/index.js'

/**
 * 生产任务单详情（管理员）
 * @description 展示详情、原材料与派工进度；导航栏更多 + 刷新、右侧操作抽屉（与工序派工单详情一致）
 */
export default {
  data() {
    return {
      /** @type {number|null} 任务单 ID */
      orderId: null,
      /** @type {Object|null} 任务单详情 */
      order: null,
      /** @type {string} 工艺路线展示摘要 */
      routeSummary: '-',
      /** @type {string} 加载错误提示 */
      loadError: '',
      /** @type {boolean} 刷新中 */
      reloadLoading: false,
      /** @type {string} 进行中的操作类型 */
      actionLoading: '',
      /** @type {boolean} 右侧操作抽屉 */
      showOperationDrawer: false
    }
  },

  computed: {
    /**
     * 派工完成情况展示文案（模板内不使用 ??，以兼容 App 端运行时）
     * @returns {string}
     */
    completedDispatchSummary() {
      if (!this.order) {
        return '0 / 0'
      }
      const done =
        this.order.completed_dispatch_count != null ? Number(this.order.completed_dispatch_count) : 0
      const total =
        this.order.dispatch_order_count != null ? Number(this.order.dispatch_order_count) : 0
      return `${done} / ${total}`
    },

    /**
     * 原材料需求表格行
     * @returns {Array<{key:string,name:string,code:string,qty:number}>}
     */
    materialRows() {
      const req = this.order?.material_requirements
      if (!req || typeof req !== 'object') {
        return []
      }
      return Object.keys(req).map((k) => {
        const item = req[k] || {}
        return {
          key: k,
          name: item.material_name || k,
          code: item.material_code || '',
          qty: item.quantity != null ? item.quantity : 0
        }
      })
    }
  },

  onLoad(options) {
    if (!this.assertAdmin()) {
      return
    }
    if (!options.id) {
      this.loadError = '缺少任务单 ID'
      return
    }
    this.orderId = Number(options.id)
    this.loadAll()
  },

  /**
   * App 原生导航栏右侧按钮：index 0 打开操作抽屉，index 1 刷新详情（与工序派工单详情一致）
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
     * 打开右侧操作抽屉（与导航栏纵向三点一致；使用 wd-popup position=right）
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
     * 抽屉内：下发
     */
    onDrawerPublish() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onPublish()
      })
    },

    /**
     * 抽屉内：编辑
     */
    onDrawerEdit() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onGoEdit()
      })
    },

    /**
     * 抽屉内：删除
     */
    onDrawerDelete() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onDelete()
      })
    },

    /**
     * 抽屉内：取消任务单
     */
    onDrawerCancel() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onCancel()
      })
    },

    /**
     * 抽屉内：查看工序派工单
     */
    onDrawerDispatchList() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onGoDispatchList()
      })
    },

    /**
     * 抽屉内：查看质检任务单
     */
    onDrawerQualityCheckList() {
      this.closeOperationDrawer()
      this.$nextTick(() => {
        this.onGoQualityCheckList()
      })
    },

    /**
     * 加载详情与工艺路线摘要
     * @returns {Promise<void>}
     */
    async loadAll() {
      this.loadError = ''
      this.reloadLoading = true
      try {
        const res = await productionOrderApi.getProductionOrderDetail(this.orderId)
        if (res.code !== 2000) {
          this.loadError = res.msg || '加载失败'
          return
        }
        this.order = res.data || null
        await this.loadRouteSummary()
      } catch (error) {
        console.error('加载任务单详情失败:', error)
        this.loadError = error.msg || '加载失败'
      } finally {
        this.reloadLoading = false
      }
    },

    /**
     * 加载工艺路线版本信息用于展示
     * @returns {Promise<void>}
     */
    async loadRouteSummary() {
      const rid = this.order?.process_route
      if (!rid) {
        this.routeSummary = '-'
        return
      }
      try {
        const res = await processRouteApi.getProcessRouteDetail(rid)
        if (res.code === 2000) {
          const r = res.data || {}
          this.routeSummary = `${r.version || '-'} (${r.material_code || ''})`
          return
        }
        this.routeSummary = `ID ${rid}`
      } catch (e) {
        console.error('加载工艺路线失败:', e)
        this.routeSummary = `ID ${rid}`
      }
    },

    /**
     * 手动刷新
     * @returns {Promise<void>}
     */
    async reload() {
      await this.loadAll()
      if (this.order && !this.loadError) {
        uni.showToast({ title: '已更新', icon: 'success' })
      }
    },

    /**
     * 下发生产任务单
     */
    onPublish() {
      uni.showModal({
        title: '确认下发',
        content: '下发后将生成工序派工单，是否继续？',
        success: async (res) => {
          if (!res.confirm) {
            return
          }
          this.actionLoading = 'publish'
          try {
            const result = await productionOrderApi.publishProductionOrder(this.orderId)
            if (result.code === 2000) {
              uni.showToast({ title: result.msg || '下发成功', icon: 'success' })
              await this.loadAll()
              return
            }
            uni.showToast({ title: result.msg || '下发失败', icon: 'none' })
          } catch (error) {
            console.error('下发失败:', error)
            uni.showToast({ title: error.msg || '下发失败', icon: 'none' })
          } finally {
            this.actionLoading = ''
          }
        }
      })
    },

    /**
     * 跳转编辑页
     */
    onGoEdit() {
      uni.navigateTo({
        url: `/pages/admin/work-order/production-order/edit?id=${this.orderId}`
      })
    },

    /**
     * 删除任务单
     */
    onDelete() {
      uni.showModal({
        title: '确认删除',
        content: '仅未下发的任务单可删除，是否继续？',
        confirmColor: '#ee0a24',
        success: async (res) => {
          if (!res.confirm) {
            return
          }
          this.actionLoading = 'delete'
          try {
            const result = await productionOrderApi.deleteProductionOrder(this.orderId)
            if (result.code === 2000) {
              uni.showToast({ title: '已删除', icon: 'success' })
              setTimeout(() => {
                uni.navigateBack()
              }, 400)
              return
            }
            uni.showToast({ title: result.msg || '删除失败', icon: 'none' })
          } catch (error) {
            console.error('删除失败:', error)
            uni.showToast({ title: error.msg || '删除失败', icon: 'none' })
          } finally {
            this.actionLoading = ''
          }
        }
      })
    },

    /**
     * 取消任务单
     */
    onCancel() {
      uni.showModal({
        title: '确认取消',
        content: '将取消本任务单及关联派工单，是否继续？',
        confirmColor: '#ee0a24',
        success: async (res) => {
          if (!res.confirm) {
            return
          }
          this.actionLoading = 'cancel'
          try {
            const result = await productionOrderApi.cancelProductionOrder(this.orderId)
            if (result.code === 2000) {
              uni.showToast({ title: result.msg || '已取消', icon: 'success' })
              await this.loadAll()
              return
            }
            uni.showToast({ title: result.msg || '取消失败', icon: 'none' })
          } catch (error) {
            console.error('取消失败:', error)
            uni.showToast({ title: error.msg || '取消失败', icon: 'none' })
          } finally {
            this.actionLoading = ''
          }
        }
      })
    },

    /**
     * 跳转工序派工单列表（带生产任务单过滤参数）
     */
    onGoDispatchList() {
      uni.navigateTo({
        url: `/pages/admin/work-order/dispatch-order/index?production_order=${this.orderId}`
      })
    },

    /**
     * 跳转质检任务单列表（带生产任务单过滤参数）
     */
    onGoQualityCheckList() {
      uni.navigateTo({
        url: `/pages/admin/work-order/quality-check-order/index?production_order=${this.orderId}`
      })
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

.empty-hint {
  padding: 24rpx;
  background-color: $uni-bg-color-white;
  border-radius: 12rpx;
}

.hint-text {
  font-size: 26rpx;
  color: $uni-text-color-grey;
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
